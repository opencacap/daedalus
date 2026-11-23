#!/usr/bin/env python3
"""Score `claude plugin eval` results of the code-review skill against case labels.

Usage: score.py --labels <labels.json> <name>=<results dir or aggregate-result.json> ... [--json]
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

VERDICT = re.compile(r"\*\*Verdict: (BLOCKING|NOT BLOCKING)\*\*")
VERIFIED = re.compile(r"^- Verifier: (CONFIRMED|UNCERTAIN)\b", re.M)
LENSES_RUN = re.compile(r"Lenses run: ([^.\n]*)")
FINDING = re.compile(r"^\*\*([CHML])\d+ — .*\*\*\n- Location: `([^`]+?):(\d+)(?:-(\d+))?`", re.M)


def read_run(trace):
    """Return the run's last result text (the report) and its sub-agent count.

    Agent tool sub-agents are counted in `subagent_stats`; Workflow agents are not, so
    they are counted by their distinct ids in the workflow progress events.
    """
    if not trace.is_file():
        print(f"score.py: trace not found: {trace}", file=sys.stderr)
        sys.exit(2)
    report, spawned, workflow_agents = "", 0, set()
    for line in trace.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event.get("type") == "result" and isinstance(event.get("result"), str):
            report = event["result"]
            spawned = event.get("subagent_stats", {}).get("spawned", 0)
        for item in event.get("workflow_progress", []):
            if item.get("type") == "workflow_agent" and item.get("agentId"):
                workflow_agents.add(item["agentId"])
    return report, spawned + len(workflow_agents)


def findings(report):
    heads = list(FINDING.finditer(report))
    found = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(report)
        block = report[m.start() : end].split("\n### ")[0]
        found.append(
            {
                "severity": m[1],
                "file": m[2],
                "lines": (int(m[3]), int(m[4] or m[3])),
                "verified": bool(VERIFIED.search(block)),
            }
        )
    return found


def matches(found, defect):
    start, end = defect.get("lines", (1, float("inf")))  # no lines: anywhere in the file
    return found["file"] == defect["file"] and found["lines"][0] <= end and start <= found["lines"][1]


def ratio(part, whole):
    return part / whole if whole else None


def score(labels, path):
    ch_total = ch_hits = reported = true = clean_runs = clean_blocking = 0
    compliant = scored_runs = 0
    noncompliant = []
    costs, seconds = [], []
    by_run = {}  # run index -> [C/H hits, C/H defects]
    passed = []
    flaky = []
    for case in json.loads(path.read_text(encoding="utf-8"))["cases"]:
        runs = case["arms"]["with"]
        outcomes = {run["passed"] for run in runs}
        passed += [run["passed"] for run in runs]
        if len(outcomes) > 1:
            flaky.append(case["name"])
        label = labels.get(case["name"])
        if label is None:
            continue
        defects = label.get("defects", [])
        for index, run in enumerate(runs):
            report, spawned = read_run(path.parent / run["tracePath"])
            found = findings(report)
            ran = LENSES_RUN.search(report)
            ran = [lens.strip() for lens in ran[1].split(",")] if ran else []
            ok = (
                bool(report)
                and set(label.get("lenses", [])) <= set(ran)
                and all(f["verified"] for f in found)
                and spawned >= len(ran) + len(found)
            )
            scored_runs += 1
            compliant += ok
            if "costUsd" in run:
                costs.append(run["costUsd"])
            if "durationSeconds" in run:
                seconds.append(run["durationSeconds"])
            if not ok and case["name"] not in noncompliant:
                noncompliant.append(case["name"])
            tally = by_run.setdefault(index, [0, 0])
            for defect in defects:
                if set(defect.get("severity", "CHML")) <= set("CH"):
                    hit = any(f["severity"] in "CH" and matches(f, defect) for f in found)
                    ch_total += 1
                    ch_hits += hit
                    tally[0] += hit
                    tally[1] += 1
            reported += len(found)
            true += sum(any(matches(f, d) for d in defects) for f in found)
            if label.get("clean"):
                verdict = VERDICT.search(report)
                clean_runs += 1
                clean_blocking += bool(verdict) and verdict[1] == "BLOCKING"
    recalls = [hits / total for hits, total in by_run.values() if total]
    return {
        "ch_recall": ratio(ch_hits, ch_total),
        "ch_recall_stdev": statistics.pstdev(recalls) if len(recalls) > 1 else None,
        "precision": ratio(true, reported),
        "clean_fp_rate": ratio(clean_blocking, clean_runs),
        "pass_rate": ratio(sum(passed), len(passed)),
        "flaky_cases": flaky,
        "compliance": ratio(compliant, scored_runs),
        "noncompliant_cases": noncompliant,
        "cost_per_review": statistics.fmean(costs) if costs else None,
        "wall_seconds": statistics.fmean(seconds) if seconds else None,
    }


def rounded(value):
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    return value


COLUMNS = [
    ("C/H recall", "ch_recall", "{:.2f}"),
    ("Recall stdev", "ch_recall_stdev", "{:.2f}"),
    ("Precision", "precision", "{:.2f}"),
    ("Clean FP rate", "clean_fp_rate", "{:.2f}"),
    ("Pass rate", "pass_rate", "{:.2f}"),
    ("Compliance", "compliance", "{:.2f}"),
    ("Cost/review (USD)", "cost_per_review", "{:.2f}"),
    ("Wall time (s)", "wall_seconds", "{:.0f}"),
]


def table(scores):
    lines = [
        "| Config | " + " | ".join(title for title, _, _ in COLUMNS) + " |",
        "| --- |" + " --- |" * len(COLUMNS),
    ]
    for name, row in scores.items():
        cells = ["n/a" if row[key] is None else form.format(row[key]) for _, key, form in COLUMNS]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines.append("")
    for name, row in scores.items():
        flaky = ", ".join(row["flaky_cases"]) or "none"
        noncompliant = ", ".join(row["noncompliant_cases"]) or "none"
        lines.append(f"- {name}: flaky cases: {flaky}; non-compliant cases: {noncompliant}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("configs", nargs="+", metavar="NAME=RESULTS")
    args = parser.parse_args(argv)
    labels = json.loads(args.labels.read_text(encoding="utf-8"))["cases"]
    configs = {}
    for item in args.configs:
        name, _, path = item.partition("=")
        if not name or not path:
            parser.error(f"expected NAME=RESULTS, got {item!r}")
        if name in configs:
            parser.error(f"configuration {name} given twice")
        path = Path(path)
        configs[name] = path / "aggregate-result.json" if path.is_dir() else path
    scores = {name: score(labels, path) for name, path in configs.items()}
    print(json.dumps(rounded(scores), indent=2) if args.json else table(scores))


if __name__ == "__main__":
    sys.exit(main())
