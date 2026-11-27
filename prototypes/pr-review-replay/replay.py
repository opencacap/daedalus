#!/usr/bin/env python3
"""PROTOTYPE, throwaway, never merged.

Replays the review rounds of one PR or MR with the round scope of "What a review
round reviews" (#24) and the finding identity of "What a finding's identity is"
(#25), and compares them with full rounds. Client data never enters this repo:
every input and output lives in a data directory outside it.

Core has no --diff, --json, or --recheck yet (#28), so this script stands in:
- delta: a synthetic base commit that is HEAD with the delta hunks reverted, so
  `code-review <synthetic base>` reviews exactly the delta hunks;
- findings: parsed from the Markdown report;
- recheck: one `claude -p` verifier per open finding in a delta file.

Usage (data dir holds config.json; see README.md):
  replay.py prepare DATA       build synthetic commits and worktrees
  replay.py review DATA [-j N] [--arm delta|full] [--rounds 1,2]
  replay.py replay DATA        identity matching, recheck, tier-2 judge
  replay.py metrics DATA       aggregate numbers (needs labels.json for merges/splits)
"""
import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def sh(args, cwd=None, env=None, input=None, check=True):
    r = subprocess.run(args, cwd=cwd, env=env, input=input, capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"failed: {' '.join(map(str, args))}\n{r.stderr}")
    return r.stdout


def git(repo, *args, **kw):
    return sh(["git", "-C", str(repo), *args], **kw)


def load(data):
    data = Path(data).expanduser()
    cfg = json.loads((data / "config.json").read_text())
    return data, cfg


# ---------- interdiff (#24 item 2) ----------

def pr_diff(repo, base, head):
    """{path: [hunk]} of the -U0 PR diff; a hunk is {header, lines}; plus file headers."""
    out = git(repo, "diff", "--no-renames", "--binary", "-U0", base, head)
    files, cur = {}, None
    for line in out.splitlines(keepends=True):
        if line.startswith("diff --git "):
            path = line.split(" b/", 1)[1].rstrip("\n")
            cur = files[path] = {"head": [line], "hunks": [], "binary": False}
        elif cur is None:
            continue
        elif line.startswith("@@"):
            cur["hunks"].append({"header": line, "lines": []})
        elif cur["hunks"]:
            cur["hunks"][-1]["lines"].append(line)
        else:
            cur["head"].append(line)
            if line.startswith("GIT binary patch") or line.startswith("Binary files"):
                cur["binary"] = True
    return files


def exists(repo, rev, path):
    return subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{rev}:{path}"],
                          capture_output=True).returncode == 0


def delta_patch(repo, base, old, new):
    """The patch of the hunks of base..new that hold a delta line, and the delta file list."""
    cur, prev = pr_diff(repo, base, new), pr_diff(repo, base, old)
    parts, delta_files = [], []
    for path, f in cur.items():
        if not subprocess.run(["git", "-C", str(repo), "diff", "--quiet", old, new, "--", path]).returncode:
            continue  # same blob at both heads: a base move or nothing
        whole = f["binary"] or exists(repo, old, path) != exists(repo, new, path)
        old_lines = {l for h in prev.get(path, {"hunks": []})["hunks"] for l in h["lines"]}
        hunks = f["hunks"] if whole else [h for h in f["hunks"] if any(
            l[:1] in "+-" and l not in old_lines for l in h["lines"])]
        if not hunks and not whole:
            continue
        delta_files.append(path)
        parts.append("".join(f["head"]))
        for h in hunks:
            parts.append(h["header"] + "".join(h["lines"]))
    return "".join(parts), delta_files


def synthetic(repo, base, old, new, workdir):
    """Commit S = new with the delta reverted, and H' = new's tree on top of S."""
    patch, files = delta_patch(repo, base, old, new)
    pfile = workdir / "delta.patch"
    pfile.write_text(patch)
    index = workdir / "index"
    env = {"GIT_INDEX_FILE": str(index), "PATH": "/usr/bin:/bin:/opt/homebrew/bin",
           "HOME": str(Path.home())}
    git(repo, "read-tree", new, env=env)
    if patch:
        git(repo, "apply", "-R", "--cached", "--unidiff-zero", "--binary", str(pfile), env=env)
    tree = git(repo, "write-tree", env=env).strip()
    s = git(repo, "commit-tree", tree, "-p", base, "-m", "replay: synthetic base", env=env).strip()
    ntree = git(repo, "rev-parse", f"{new}^{{tree}}").strip()
    h = git(repo, "commit-tree", ntree, "-p", s, "-m", f"replay: head {new[:9]}", env=env).strip()
    # Check: S..H' holds exactly the delta's changed lines.
    got = sorted(l for p in pr_diff(repo, s, h).values() for hk in p["hunks"] for l in hk["lines"]
                 if l[:1] in "+-")
    want = sorted(l for line in [patch] for l in line.splitlines(keepends=True)
                  if l[:1] in "+-" and not l.startswith(("+++", "---")))
    # git diff may realign reverted hunks and cancel a line pair; more lines than the delta is a bug.
    from collections import Counter
    extra, missing = Counter(got) - Counter(want), Counter(want) - Counter(got)
    if extra or len(missing) > 4:
        raise SystemExit(f"synthetic diff mismatch for {new[:9]}: extra {dict(extra)} missing {dict(missing)}")
    if missing:
        print(f"note {new[:9]}: diff realigned {sum(missing.values())} lines: {list(missing)}")
    return s, h, files


def cmd_prepare(a):
    data, cfg = load(a.data)
    repo = data / "repo"
    if not repo.exists():
        sh(["git", "clone", "-q", "--no-checkout", cfg["source_repo"], str(repo)])
        git(repo, "remote", "set-url", "origin", cfg["remote_url"])
    heads, base = cfg["heads"], cfg["base"]
    plan = [{"round": 1, "arm": "delta", "base": base, "head": heads[0], "spec": cfg["spec"],
             "delta_files": None}]
    for n in range(1, len(heads)):
        w = data / "work" / f"r{n + 1}"
        w.mkdir(parents=True, exist_ok=True)
        s, h, files = synthetic(repo, base, heads[n - 1], heads[n], w)
        git(repo, "update-ref", f"refs/replay/r{n + 1}-base", s)
        git(repo, "update-ref", f"refs/replay/r{n + 1}-head", h)
        plan.append({"round": n + 1, "arm": "delta", "base": s, "head": h, "real_head": heads[n],
                     "spec": "none", "delta_files": files})
        plan.append({"round": n + 1, "arm": "full", "base": base, "head": heads[n],
                     "spec": cfg["spec"], "delta_files": None})
    for p in plan:
        wt = data / "wt" / f"{p['arm']}-r{p['round']}"
        if not wt.exists():
            git(repo, "worktree", "add", "-q", "--detach", str(wt), p["head"])
        p["worktree"] = str(wt)
    (data / "plan.json").write_text(json.dumps(plan, indent=2))
    for p in plan:
        print(p["arm"], p["round"], p["head"][:9], "delta files:",
              len(p["delta_files"]) if p["delta_files"] is not None else "full")


# ---------- running core ----------

def claude(prompt, cwd, model, budget, tools, plugin=None, timeout=3600):
    args = ["claude", "-p", prompt, "--output-format", "json", "--model", model,
            "--setting-sources", "project,local", "--max-budget-usd", str(budget)]
    args += ["--allowedTools", *tools] if tools else ["--tools", ""]
    if plugin:
        args += ["--plugin-dir", plugin]
    t = time.time()
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        out = {"result": r.stdout, "is_error": True, "stderr": r.stderr[-2000:]}
    out["wall_s"] = round(time.time() - t)
    return out


def cmd_review(a):
    data, cfg = load(a.data)
    plan = json.loads((data / "plan.json").read_text())
    todo = [p for p in plan if (not a.arm or p["arm"] == a.arm)
            and (not a.rounds or p["round"] in a.rounds)]
    (data / "reviews").mkdir(exist_ok=True)

    def run(p):
        out_path = data / "reviews" / f"{p['arm']}-r{p['round']}.json"
        if out_path.exists() and not a.force:
            return
        budget = cfg["budget_full"] if p["spec"] != "none" else cfg["budget_delta"]
        flags = " --workflow" if cfg.get("workflow", True) else ""
        out = claude(f"/daedalus-core:code-review {p['base']} --spec {p['spec']}{flags}",
                     p["worktree"], cfg["review_model"], budget,
                     ["Read", "Glob", "Grep", "Skill", "Agent", "Bash", "Workflow"], cfg["core_plugin"])
        out_path.write_text(json.dumps(out, indent=2))
        print(p["arm"], p["round"], "cost", out.get("total_cost_usd"), "wall", out["wall_s"],
              "error" if out.get("is_error") else "ok", flush=True)

    with ThreadPoolExecutor(a.j) as ex:
        list(ex.map(run, todo))


# ---------- parsing a report ----------

BLOCK = re.compile(r"^\*\*([CHML]\d+) — (.+?)\*\*\s*$")


def parse_report(md):
    """Findings of a core Markdown report, by section."""
    findings, section, cur = [], None, None
    sections = {"### Introduced by this diff": "introduced", "### Needs a human": "needs-human",
                "### Pre-existing": "pre-existing"}
    for line in md.splitlines():
        if line.startswith("### "):
            section = sections.get(line.strip())
            cur = None
            continue
        m = BLOCK.match(line)
        if m and section:
            cur = {"tag": m[1], "severity": m[1][0], "title": m[2], "section": section,
                   "file": "", "line": "", "lenses": [], "code": "", "claim": "", "rule": ""}
            findings.append(cur)
            continue
        if cur is None or not line.startswith("- "):
            continue
        key, _, val = line[2:].partition(": ")
        if key == "Location":
            loc = val.strip().strip("`")
            cur["file"], _, cur["line"] = loc.rpartition(":")
        elif key == "Lenses":
            cur["lenses"] = [x.strip() for x in val.split(",")]
        elif key == "Code":
            cur["code"] = val.strip().strip("`")
        elif key == "Failure":  # the report has no claim field; title + failure stand in
            cur["claim"] = f"{cur['title']}. {val.strip()}"
        elif key == "Rule":
            cur["rule"] = val.strip()
    return findings


def report_text(review):
    return review.get("result") or ""


# ---------- identity (#25) ----------

def norm(code):
    return re.sub(r"\s+", " ", code.replace("`", "")).strip()


def families(lenses):
    return {re.sub(r"-[a-z]$", "", l) for l in lenses}


def rules(rule):
    return {r.split(" — ")[0].strip() for r in rule.split(";") if r.strip() and r.strip() != "none"}


def tier1(new, known):
    a, b = norm(new["code"]), norm(known["code"])
    if not a or not b or not (a == b or a in b or b in a):
        return False
    return bool(rules(new["rule"]) & rules(known["rule"])) or bool(
        families(new["lenses"]) & families(known["lenses"]))


JUDGE = """You match code review findings across review rounds of one pull request.
For each NEW finding, say which KNOWN finding (in the same file) reports the same defect, or "new".
Two findings are the same only when they describe the same defect in the same code, even if worded
differently or the line moved. A different defect on the same line or in the same function is new.
Each KNOWN finding matches at most one NEW finding.

{groups}

Reply with only a JSON object mapping each NEW id to a KNOWN id or "new", for example {{"N1": "F3", "N2": "new"}}."""


def describe(fid, f):
    return f"- {fid} [{f['severity']}] {f['title']}\n  code: {f['code'][:300]}\n  claim: {f['claim'][:500]}"


def judge(pairs, cfg, cwd):
    """pairs: {file: (new {nid: f}, known {fid: f})} -> ({nid: fid|'new'}, cost)."""
    groups = []
    for file, (new, known) in pairs.items():
        groups.append(f"File: {file}\nNEW:\n" + "\n".join(describe(k, v) for k, v in new.items())
                      + "\nKNOWN:\n" + "\n".join(describe(k, v) for k, v in known.items()))
    out = claude(JUDGE.format(groups="\n\n".join(groups)), cwd, cfg["judge_model"], 2, [])
    m = re.search(r"\{.*\}", out.get("result") or "", re.S)
    if out.get("is_error") or not m:
        raise SystemExit(f"judge failed: round incomplete\n{out.get('result')}\n{out.get('stderr')}")
    return json.loads(m[0]), out.get("total_cost_usd", 0)


RECHECK = """You recheck one finding from an earlier review round of this pull request. The code may have
changed since. Re-derive from the code at HEAD whether the defect is still there. Do not trust the claim.
Read-only: do not edit files, do not run commands that change the repository, do not start agents or skills.

Finding {id} [{severity}] {title}
Location then: {file}:{line}
Code then: {code}
Claim: {claim}
Rule: {rule}

Reply with exactly these lines and nothing else:
RESULT: <fixed | open | cannot tell>
LOCATION: <file>:<line> where the defect is now, or none
CITATION: <file>:<line> — <one sentence of evidence>"""


def recheck(fid, f, cwd, cfg):
    out = claude(RECHECK.format(id=fid, **f), cwd, cfg["review_model"], cfg["budget_recheck"],
                 ["Read", "Glob", "Grep", "Bash(git show:*)", "Bash(git log:*)", "Bash(git diff:*)"])
    text = out.get("result") or ""
    m = re.search(r"RESULT:\s*(fixed|open|cannot tell)", text)
    loc = re.search(r"LOCATION:\s*(\S+)", text)
    return {"id": fid, "result": m[1] if m else "cannot tell", "raw": text.strip()[:600],
            "location": loc[1] if loc else "", "cost": out.get("total_cost_usd", 0)}


def match_round(new_findings, known, cfg, cwd, use_judge=True):
    """One-to-one match of a round's findings to known ids. Returns per-finding match info and cost."""
    taken, result, cost = set(), [], 0.0
    for f in new_findings:
        f = dict(f)
        cand = [k for k, v in known.items() if v["file"] == f["file"] and k not in taken and tier1(f, v)]
        if cand:
            f["match"], f["tier"] = cand[0], 1
            taken.add(cand[0])
        result.append(f)
    if use_judge:
        pairs, ids = {}, {}
        for i, f in enumerate(result):
            if f.get("match"):
                continue
            kn = {k: v for k, v in known.items() if v["file"] == f["file"] and k not in taken}
            if not kn:
                continue
            nid = f"N{i + 1}"
            ids[nid] = f
            pairs.setdefault(f["file"], ({}, kn))[0][nid] = f
        if pairs:
            answers, cost = judge(pairs, cfg, cwd)
            for nid, fid in answers.items():
                f = ids.get(nid)
                if f is None or fid == "new" or fid not in known or fid in taken or \
                        known[fid]["file"] != f["file"]:
                    continue
                f["match"], f["tier"] = fid, 2
                taken.add(fid)
    return result, cost


def cmd_replay(a):
    data, cfg = load(a.data)
    plan = json.loads((data / "plan.json").read_text())
    real = cfg_real_reports(data)
    for arm in a.arms or ("delta", "full", "real"):
        src = "full" if arm == "real" else arm
        rounds = sorted([p for p in plan if p["arm"] == src or (src == "full" and p["round"] == 1)],
                        key=lambda p: p["round"])
        state = {"next": 1, "findings": {}, "rounds": []}
        for p in rounds:
            path = data / "reviews" / f"{p['arm']}-r{p['round']}.json"
            if arm == "real":
                rev = {"result": real[p["round"] - 1]}
            elif not path.exists():
                print(f"{arm} round {p['round']}: no review yet, stop")
                break
            else:
                rev = json.loads(path.read_text())
            found = parse_report(report_text(rev))
            known = {k: v for k, v in state["findings"].items() if v["state"] == "open"}
            rec, rec_cost = [], 0.0
            if arm == "delta" and p["delta_files"] is not None:
                todo = [(k, v) for k, v in known.items() if v["file"] in p["delta_files"]]
                with ThreadPoolExecutor(4) as ex:
                    rec = list(ex.map(lambda kv: recheck(kv[0], kv[1], p["worktree"], cfg), todo))
                rec_cost = sum(r["cost"] or 0 for r in rec)
            matched, judge_cost = match_round(found, known, cfg, p["worktree"])
            matched_ids = {f["match"] for f in matched if f.get("match")}
            for r in rec:
                f = state["findings"][r["id"]]
                if r["result"] == "fixed" and r["id"] not in matched_ids:
                    f["state"], f["closed_round"] = "fixed", p["round"]
            for fid, f in known.items():
                if f["state"] == "open" and not exists(data / "repo", p["head"], f["file"]):
                    f["state"], f["closed_round"] = "code removed", p["round"]
            posted = []
            for f in matched:
                if f.get("match"):
                    k = state["findings"][f["match"]]
                    k.update(file=f["file"], line=f["line"], code=f["code"], severity=f["severity"])
                    k["seen"].append(p["round"])
                elif f["section"] in ("introduced", "needs-human"):
                    fid = f"F{state['next']}"
                    state["next"] += 1
                    state["findings"][fid] = {**{k: f[k] for k in (
                        "file", "line", "code", "claim", "rule", "lenses", "severity", "title")},
                        "state": "open", "first_round": p["round"], "seen": [p["round"]]}
                    f["assigned"] = fid
                    posted.append(fid)
            state["rounds"].append({
                "round": p["round"], "head": p.get("real_head", p["head"]),
                "cost_review": rev.get("total_cost_usd"), "wall_s": rev.get("wall_s"),
                "cost_recheck": rec_cost, "cost_judge": judge_cost, "error": rev.get("is_error"),
                "delta_files": p["delta_files"], "findings": matched, "posted": posted, "recheck": rec})
            print(arm, p["round"], "found", len(found), "posted", len(posted),
                  "matched", len(matched_ids), "rechecked", len(rec), flush=True)
        (data / f"state-{arm}.json").write_text(json.dumps(state, indent=2))


# ---------- metrics ----------

def cmd_metrics(a):
    data, cfg = load(a.data)
    repo = data / "repo"
    heads = cfg["heads"]
    labels = json.loads((data / "labels.json").read_text()) if (data / "labels.json").exists() else {}

    def untouched(file, n):  # file not changed by the fix commits before round n (1-based)
        if n == 1:
            return False
        return subprocess.run(["git", "-C", str(repo), "diff", "--quiet", heads[n - 2], heads[n - 1],
                               "--", file]).returncode == 0

    out = {"real": [], "arms": {}}
    for n, body in enumerate(cfg_real_reports(data), 1):
        fs = parse_report(body)
        intro = [f for f in fs if f["section"] != "pre-existing"]
        out["real"].append({"round": n, "introduced": len(intro),
                            "pre_existing": len(fs) - len(intro),
                            "untouched_files": sum(untouched(f["file"], n) for f in intro)})
    for arm in ("delta", "full", "real"):
        sp = data / f"state-{arm}.json"
        if not sp.exists():
            continue
        st = json.loads(sp.read_text())
        rows, t1, t2, fm, fsplit, lab, orep = [], 0, 0, 0, 0, 0, 0
        for r in st["rounds"]:
            n, fs = r["round"], r["findings"]
            posted_side = [f for f in fs if f["section"] != "pre-existing"]
            outside = [f for f in fs if f["section"] == "pre-existing"]
            rows.append({
                "round": n, "posted_new": len(r["posted"]),
                "reported_again": sum(1 for f in posted_side if f.get("match")),
                "outside_known": sum(1 for f in outside if f.get("match")),
                "outside_new": sum(1 for f in outside if not f.get("match")),
                "posted_new_untouched_files": sum(untouched(st["findings"][fid]["file"], n)
                                                  for fid in r["posted"]),
                "recheck": {k: sum(1 for x in r["recheck"] if x["result"] == k)
                            for k in ("fixed", "open", "cannot tell")},
                "cost": round(sum(x or 0 for x in (r["cost_review"], r["cost_recheck"], r["cost_judge"])), 2),
                "wall_s": r["wall_s"]})
            for i, f in enumerate(fs):
                key = f"{arm}-r{n}-{i}"
                t1 += f.get("tier") == 1
                t2 += f.get("tier") == 2
                if key in labels:
                    lab += 1
                    truth = labels[key]  # id of the known finding it is, or "new"
                    if f.get("match") and truth != f["match"]:
                        fm += 1
                    if not f.get("match") and truth.startswith("F"):
                        fsplit += 1
                    orep += truth.startswith("outside-repeat")
        out["arms"][arm] = {"rounds": rows, "tier1": t1, "tier2": t2, "labelled": lab,
                            "false_merges": fm, "false_splits": fsplit, "outside_repeats_without_id": orep,
                            "open_at_end": sum(1 for f in st["findings"].values() if f["state"] == "open"),
                            "ids": len(st["findings"])}
    print(json.dumps(out, indent=2))
    (data / "metrics.json").write_text(json.dumps(out, indent=2))


def cfg_real_reports(data):
    notes = json.loads((data / "real" / "notes.json").read_text())
    return [x["body"] for x in sorted(notes, key=lambda x: x["created_at"])
            if not x["system"] and x["body"].startswith("## Code review")]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prepare", "review", "replay", "metrics"):
        s = sub.add_parser(name)
        s.add_argument("data")
        if name == "review":
            s.add_argument("-j", type=int, default=3)
            s.add_argument("--arm", choices=["delta", "full"])
            s.add_argument("--rounds", type=lambda v: [int(x) for x in v.split(",")])
            s.add_argument("--force", action="store_true")
        if name == "replay":
            s.add_argument("--arms", type=lambda v: v.split(","))
    a = ap.parse_args()
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
