# Research: a rigorous code-review skill for daedalus-core

Status: research complete, decisions taken, spec not yet written. Input for `/mattpocock-skills:to-spec`.
Date: 2026-11-23. Claude Code docs read at changelog head 2.1.330 (installed: 2.1.311).

## Goal

Replace project-local ECC review flows (`/review-pr` and its agents) with one review capability in
`daedalus-core` that is at least as rigorous as the ECC flow: high recall on real defects, few false
positives. Out of scope: posting to a PR, re-review rounds, merging.

`mattpocock-skills:code-review` alone is not enough. It runs two axes (Standards, Spec), caps each
sub-agent at 400 words, does not verify findings, has no severity, and its own docs send bug hunting
elsewhere. Its Standards and Spec briefs and the Fowler smell baseline are worth reusing (MIT).

## Decisions taken

1. Ship a skill, `daedalus-core:code-review`, that orchestrates fresh sub-agents.
2. Review lenses live as reference files inside the skill (`references/`), not as plugin agents.
   No ECC agents move into daedalus.
3. Support Codex where possible. If a Workflow-script orchestration (Claude Code only) measures
   clearly better than skill-driven orchestration, use the Workflow.
4. Severity scale is C/H/M/L. Pre-existing findings are graded on the same scale and marked
   pre-existing.
5. Measure with evals before choosing the orchestration layer.

## Evidence (from a web research pass; sources not all re-read by hand)

Ranked by strength:

1. **Find, then verify each finding independently.** BitsAI-CR (ByteDance) offline precision
   57.03% to 65.59% with a filter stage (https://arxiv.org/abs/2501.15134). Uber uReview chains
   generate, filter, validate, dedup (https://www.uber.com/us/en/blog/ureview/). Anthropic's
   `code-review` plugin keeps only issues a separate validation sub-agent confirms
   (claude-plugins-official `plugins/code-review/commands/code-review.md`). Cost: verifiers lose
   recall (Kuaishou key-bug inclusion 31.11 to 20.00, https://arxiv.org/abs/2505.17928), so do not
   silently drop uncertain high-severity findings.
2. **Hard category suppression, defects only.** Google AutoCommenter useful rate 54% to 66% after
   suppressing 22 low-value rule types (https://arxiv.org/abs/2405.13565). Do not flag style,
   linter territory, lint-ignored code, input-dependent speculation, or mix pre-existing with new.
3. **Several independent passes, union, then verify.** Cursor Bugbot ran 8 passes with shuffled diff
   order (https://cursor.com/blog/building-bugbot). SWR-Bench: aggregating 10 runs raised recall
   118.83% (https://arxiv.org/abs/2509.01494). Majority voting drops bugs only one pass found.
4. **Agentic, targeted context beats bulk context.** Cursor calls the agentic loop its largest gain.
   Bulk or cross-repo context added noise (Atlassian, SWE-PRBench https://arxiv.org/abs/2603.26130).
5. **Repo rules go to finders and verifiers.** Removing guidelines was the largest ablation drop in
   RovoDev. Anthropic passes REVIEW.md to both finders and verifiers
   (https://code.claude.com/docs/en/code-review-customize.md).
6. **Evidence-carrying findings; verifier re-derives from code, not from the finder's reasoning.**
   A critic that reads the finder's reasoning tends to agree ("false consensus");
   evidence-forced verdicts raised F1 0.457 to 0.533 (https://arxiv.org/abs/2608.18167). Running
   code beats judging it (https://arxiv.org/abs/2603.00539).
7. **Severity tiers, caps, dedup.** Anthropic: Important / Nit / Pre-existing, nits capped.
8. **Feedback-trained filters** work at volume; a small team's substitute is a hand-kept
   "do not report" list grown from dismissed findings.
9. **Specialised lenses vs one generalist: weak evidence.** Lenses buy recall; the verifier pays.
10. **Self-rated confidence scores: weak or harmful** (Greptile: "nearly random").

Anti-patterns: "find more" loops (CR-Bench, https://arxiv.org/abs/2603.11078); prompts that demand
an explanation plus a fix without a "no issue" option; trusting a single run; adding finders without
a filter; few-shot good/bad comment examples (Greptile).

## Platform constraints

Claude Code (https://code.claude.com/docs/en/skills.md, sub-agents.md, plugins/components.md):

- Skill frontmatter: `disable-model-invocation`, `allowed-tools`, `disallowed-tools`, `model`,
  `effort`, `context: fork` + `agent`, `background`, `arguments`. Supporting files load on demand;
  `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}`. Keep SKILL.md under 500 lines.
- A forked skill cannot ask the user (AskUserQuestion is removed from sub-agents); run the
  orchestrator inline so it can ask for a missing spec location.
- Sub-agents nest up to 3 levels. Non-fork sub-agents inherit CLAUDE.md and `.claude/rules`.
  SessionStart hook output inside sub-agents is not documented: pass daedalus-core rules by path.
- Plugin agents: project `.claude/agents/<same name>` outranks them; no on-demand-only flag;
  `permissionMode`, `hooks`, `mcpServers` ignored. Codex cannot ship agents. Hence lenses as files.
- Plugins can ship `workflows/*.js` (Dynamic workflows), namespaced `/<plugin>:<name>`. Limits: 16
  concurrent agents by default, schema-validated agent output, resumable. Each run asks permission
  interactively; Pro must enable it in `/config`; orgs can disable; sub-agents cannot start one;
  no Codex equivalent.
- Bundled `/code-review` (2.1.329+): bugs and CLAUDE.md violations only, tagged Important /
  Pre-existing / Nit. A project or personal skill named `code-review` replaces it; `/review` keeps
  the bundled one. Plugin skills are namespaced and never take the bare name.
- `ReportFindings` field names and custom-skill use are undocumented: render findings ourselves.
- `claude plugin eval` (2.1.269+): cases under `evals/<case>/`, graders `regex`, `tool_used`,
  `file_exists`, `llm`, `baseline`; `scaffold_script` builds fixtures with `--scaffold`; sandbox
  is read-only unless `--allow-tools "Bash(git *)"`. No built-in precision/recall: compute from the
  JSON results.

Codex (https://learn.chatgpt.com/docs/agent-configuration/subagents): spawns sub-agents when a skill
instruction asks; custom agents are TOML under `.codex/agents/`; plugin-shipped agents and max
depth are undocumented.

## Proposed design

Pipeline, one thin orchestration layer over shared reference files:

1. **Scope.** Default `merge-base(default branch)...HEAD`; flag to include uncommitted work.
   Fail on a bad ref or empty diff before spawning anything.
2. **Gather context (inline).** Standards sources: CLAUDE.md, AGENTS.md, `.claude/rules/**`,
   CODING_STANDARDS / CONTRIBUTING, ADRs, daedalus-core `rules/*.md` by path. Spec sources: tracker
   doc, plus an optional per-repo review config. Stack detection selects stack skills. Optional
   deterministic checks (lint, type, tests) from the config; their failures are evidence.
3. **Finders in parallel.** Fresh read-only sub-agents; each brief says "do not invoke
   `/code-review` and do not spawn agents".
   - correctness, two independent passes (different diff order / context strategy)
   - security (daedalus-core `security-review` + an exclusion list)
   - error handling / silent failures
   - standards (Matt's Standards brief + smell baseline; smells cap at L)
   - spec (Matt's Spec brief; requirement coverage table; skipped with "no spec available")
   - tests (only when code changed and the repo has a suite)
   - types, comments (only when the diff touches them)
   - stack (the stack plugin's `*-patterns` skill is the rubric; replaces per-stack reviewer agents)
4. **Normalize and dedupe.** Finding schema: id, lens, file, line, quoted code, claim, concrete
   failure scenario, cited rule (standards/spec), suggested fix, introduced-by-diff vs
   pre-existing. Merge same location + same root cause. Drop suppressed categories.
5. **Verify each finding.** Fresh sub-agent per finding, sees the claim and location only, must
   re-derive from code, may grep or run a targeted test. Verdict CONFIRMED (cite file:line),
   REFUTED (cite), UNCERTAIN. UNCERTAIN at H or C goes to a "needs a human" section.
6. **Report.** `**{TAG}{N} — title**` with C/H/M/L. Blocking = open C/H introduced by the diff.
   Pre-existing findings in their own section, same scale. Spec coverage table. Summary line with
   lenses run and skipped.

Per-repo config (optional), located through the repo's agent-skills section: spec sources and how
to read their latest version, deterministic check commands, lens toggles, a "do not report" list.

Rules update: daedalus-core §5/§6 point code review at `daedalus-core:code-review`;
`mattpocock-skills:code-review` stays only inside `implement`.

Attribution: THIRD_PARTY_NOTICES rows for adapted text from mattpocock-skills (MIT),
everything-claude-code (MIT), and claude-plugins-official (Apache-2.0: keep the license and state
changes).

## Orchestration choice: skill vs Workflow

Both are thin layers over the same `references/`. Build the skill path first (works in Claude and
Codex). Build the Workflow path over the same references and run both on the same eval set.
Pick the Workflow only if it is clearly better, defined before measuring, e.g. higher C/H recall
at equal or better precision, or materially lower run-to-run variance or wall time. Also record
orchestration compliance of the skill path (every lens ran, every finding verified).

## Evaluation

Two tiers, because client code must never enter this public repository:

1. **Public, in daedalus:** `plugins/daedalus-core/evals/` with synthetic fixtures built by
   `scaffold_script`: seeded-bug cases per lens (regex on file and line), clean cases
   (`count:0` blocking findings) for false positives, a pre-existing case that must be labelled.
   Run with `--scaffold --allow-tools "Bash(git *)" --runs 3`, pinned model and judge model.
2. **Private, outside daedalus:** replay historical PRs of a real project. Labels: findings the
   old ECC review raised that authors fixed (true positives with location), bugs traced from later
   fix commits back to the introducing PR (misses of the old flow), and clean PRs for false
   positives. A hit needs matching location and description. 3 to 5 runs per configuration. Use an
   LLM judge only for hit matching, from a different model family, checked on ~50 hand labels.
   Bias: labels from the old reviewer measure "does the new one catch what the old one caught";
   the fix-commit set measures what both missed.

## Open items

- Exact lens briefs and the suppression list.
- Verifier batching to bound cost (per finding vs per file).
- Whether to provide a personal `code-review` skill so the bare `/code-review` maps to this one.
- Cost per review, measured during eval.
