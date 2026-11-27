# PROTOTYPE: PR review replay (throwaway, never merged)

Answers [Replay a private client MR with delta rounds and stable identity](https://github.com/opencacap/daedalus/issues/31). It replays the reviewed rounds of one PR or MR three ways:

- **delta**: round 1 full, later rounds review only the interdiff hunks ([What a review round reviews](https://github.com/opencacap/daedalus/issues/24)), recheck open findings in delta files, and match findings to PR-scoped ids ([What a finding's identity is](https://github.com/opencacap/daedalus/issues/25)).
- **full**: the control. Every round is a full code review of the whole PR, with the same matcher.
- **real**: the matcher run over the real rounds' reports, to measure identity alone.

Client data never enters this repository. The data directory lives outside it and holds the clone, the real reports, every review, the labels, and the metrics.

## Stand-ins for core options that do not exist yet

Core has no `--diff`, `--json`, or `--recheck` yet ([Which generic additions code review gets for daedalus-land](https://github.com/opencacap/daedalus/issues/28)).

- **Delta.** `prepare` builds commit S, which is the round's head with the delta's `-U0` hunks reverted, and H', which is the head's tree on top of S. `code-review S` in a worktree at H' then reviews exactly the delta hunks. The review config is read at S. That matches the merge base only when the PR does not change the config.
- **Findings.** Parsed from the Markdown report. The report has no `claim` field, so the title plus `Failure` stand in for it.
- **Recheck.** One `claude -p` verifier per open finding in a delta file. Its results are `fixed`, `open`, or `cannot tell`. It has no `refuted`.

## Run

`DATA/config.json`:

```json
{
  "source_repo": "<local clone>", "remote_url": "<forge remote>",
  "base": "<MR base sha>", "heads": ["<round 1 head>", "..."], "spec": "<spec arg>",
  "core_plugin": "<copy of plugins/daedalus-core without the dependencies field>",
  "workflow": true, "review_model": "claude-sonnet-5-5", "judge_model": "claude-haiku-5-5",
  "budget_full": 35, "budget_delta": 15, "budget_recheck": 1.5
}
```

`DATA/real/notes.json` holds the MR's notes from the forge API. The real round reports are the notes that start with `## Code review`.

```sh
python3 -I replay.py prepare DATA
python3 -I replay.py review DATA --arm delta -j 3
python3 -I replay.py review DATA --arm full -j 3
python3 -I replay.py replay DATA            # matching, recheck, tier-2 judge
python3 -I replay.py metrics DATA           # reads DATA/labels.json for merges and splits
```

`labels.json` maps `<arm>-r<round>-<index>` to the truth for that finding: a finding id, `new`, or `outside-repeat:<ref>`, for a repeat of an earlier finding that never got an id.

Each review runs `claude -p` with `--setting-sources project,local` and `--plugin-dir`. User-level plugins and hooks therefore do not load.
