---
status: accepted
---

# Workflow orchestration for code review in Claude Code

`daedalus-core:code-review` has two orchestrations over the same reference files. In the skill path, the model that runs the skill starts the finders and verifiers itself and writes the report. In the Workflow path (`--workflow`), the skill still resolves the scope and gathers the context, then the `code-review-workflow` Workflow script starts the agents, merges and verifies the findings, and renders the report in code. On the same eval set, the Workflow path ran about 28% faster and about 22% cheaper per review. Its C/H recall was slightly lower, and it was a little less stable from run to run. Under the selection rule fixed in #2 before measuring, lower wall time alone qualifies, so Claude Code users are pointed to `--workflow`. The skill path stays the default, because Codex and hosts without workflows can only run that.

## Selection rule

The rule was fixed in #2: the Workflow replaces the skill-driven orchestration only if it has higher C/H recall at equal or better precision, or materially lower run-to-run variance or wall time. #2 gave no number for "materially". These readings were written down at 2026-11-23T10:06:56Z, before any result of the decision runs was read:

- Higher C/H recall: a strictly higher pooled C/H recall over the 3 runs.
- Equal or better precision: precision no more than 0.02 lower.
- Materially lower variance: C/H recall stdev at least 0.05 lower, and fewer flaky cases.
- Materially lower wall time: mean wall time per scored review at least 25% lower.

## Measurement

Both paths ran the 22 cases of `plugins/daedalus-core/evals`, `--runs 3`, on Claude Code 2.1.323. Every case pins `claude-sonnet-5-5`, and the judge model was pinned to `claude-haiku-5-5`, although no case has an `llm` grader. Both suites ran on 2026-11-23, at the same time on one machine with `-j 4` each, so both had the same load. `evals/score.py` scored the 19 cases that end in a report against `evals/labels.json`:

| Path | C/H recall | Recall stdev | Precision | Clean FP rate | Pass rate | Compliance | Cost/review (USD) | Wall time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skill | 1.00 | 0.00 | 0.67 | 0.00 | 1.00 | 1.00 | 0.75 | 95 |
| workflow | 0.97 | 0.05 | 0.76 | 0.00 | 0.97 | 1.00 | 0.58 | 68 |

- The skill suite cost $43.46 and passed 66 of 66 runs. The workflow suite cost $34.15 and passed 64 of 66.
- The Workflow path was faster on all 19 scored cases. Its median time was 0.71 of the skill path's.
- Both runs that the Workflow path failed found the defect, but at the wrong location. In the `security` case it cited `src/users.py:6` instead of line 7. In the `spec` case it cited `src/discounts.py:7-9` where the grader expects line 8. The first run is the only C/H recall miss. The Workflow renders the location a finder gives without changing it. In the skill path, the orchestrating model writes the report and can correct the location as it does.
- Precision is low on both paths for one shared reason. The standards lens reports "no unit test" findings that cite the `testing.md` shared rule, and the labels count them as false positives.

## Decision

- Recall: not met (0.97 against 1.00).
- Variance: not met (stdev 0.05 against 0.00, and 2 flaky cases against none).
- Wall time: met (68 s against 95 s, 28% lower).

The Workflow path wins under the rule. The shared rules and the README point Claude Code users to `--workflow`. The skill path is not removed. It is the Codex path, and the fallback wherever the Workflow tool is missing or refused.

## Consequences

- The Workflow path runs in Claude Code only. Each run needs permission for the Workflow tool, and Pro users must turn on dynamic workflows. An organization can turn workflows off, and a sub-agent cannot start one. If the call fails, the review stops and says to rerun without `--workflow`.
- Both paths read the same lens, finder, verifier, and report reference files. A change to a brief applies to both. A change to the orchestration steps in `SKILL.md` must be mirrored in `workflows/code-review-workflow.js`.
- Before a later decision is revisited, rerun both paths through `evals/run.sh` and `evals/score.py`. The private replay tier can use the same scorer.
