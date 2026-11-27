# Research: how AI PR reviewers run later review rounds

Status: research complete. Input for the `daedalus-land` map (issue #19), answering issue #20.
Date: 2026-11-27. All web sources were read on that date. Open-source code was read at the commits named below.
Builds on `.scratch/code-review/research.md`, which covers one-shot review quality (find, then verify;
suppression; multiple passes). This file does not repeat that material.

## Question

How do top-tier AI PR reviewers run later review rounds on the same PR? For each tool: what a new push
re-reviews, how the tool avoids repeating itself, what it does with resolved, dismissed, or replied-to
threads, whether it caps findings or drops low severities in later rounds, and how it decides the PR is
done. Also: what sources say separates reviewing a PR from reviewing a diff once.

## Answer in one paragraph

The mature tools treat a later round as **a delta review plus a check on the open findings**, not a fresh
review of the whole PR. A push reviews only the commits since the last reviewed head (Anthropic Code Review,
Cursor Bugbot, CodeRabbit, PR-Agent `-i`). Findings on code that has not changed since the last review are
held back, and later rounds post fewer nits and pre-existing findings (Anthropic). A whole-PR review runs
only on explicit request. Earlier findings carry a persistent identity, and the next review resolves a
thread only when it judges the issue fixed (Anthropic, CodeRabbit, Copilot, Bugbot, PR-Agent). A thread a
human resolved without a fix counts as dismissed, and the tool does not raise it again unless the code makes
it worse (PR-Agent, Bugbot, Copilot resolution reasons). "Done" is a gate on the latest reviewed head: no
open blocking finding there. It is usually published as a neutral or failing status, and any approval is
withdrawn on the next push. Several tools also cap the loop itself: CodeRabbit pauses after 5 reviewed
commits, Bugbot Autofix stops after 3 attempts, and Greptile's `greploop` stops after 5 iterations. Where
tools did not do this, users reported the same failure seen in #19: every push re-scans the diff, new
findings appear on old code, and the loop does not converge (GitHub Community #189767, Cursor forum
#151367 and #147748). MCR-Bench measures it: F1 falls as rounds increase, and the largest false-positive
class is "already resolved defects ... repeatedly flagged as new".

## Per tool

### Anthropic Code Review (managed service) and `/code-review`

Sources: [Code Review](https://code.claude.com/docs/en/code-review.md),
[Read and request reviews](https://code.claude.com/docs/en/code-review-pull-requests.md),
[Set up](https://code.claude.com/docs/en/code-review-setup.md),
[Customize](https://code.claude.com/docs/en/code-review-customize.md).

- **Triggers.** Per repository: "Once after PR creation", "After every push", or "Manual (@claude review)".
  `@claude review always` subscribes one PR to push reviews and `@claude review stop` ends the subscription.
- **What a later round covers.** "A later review that starts on its own, such as after a push, focuses on
  what changed since the last review and posts fewer nits and pre-existing findings." The review body counts
  what it left out: findings on unchanged code end "outside the scope of this re-review and not posted", and
  nits and pre-existing findings end "found and not posted". A manual `@claude review` "covers the whole pull
  request again".
- **Skipping a round.** After a push that "still adds and removes the same lines" (empty commit, clean merge
  of the base, clean rebase), with no Important thread resolved since, the check run keeps the earlier
  result: "Code review skipped — no new changes" (no Important finding open) or "Code review not repeated —
  earlier findings still open".
- **Threads.** A review "resolves its own earlier comment threads". On a pushed fix: "The next review ...
  resolves its earlier thread when it judges the issue fixed." On a reply: "a reply doesn't start a review.
  The next review ... reads the replies on its earlier findings, and can resolve the thread or post one
  follow-up reply." A human resolving the thread dismisses the finding; "Replying alone doesn't dismiss a
  finding." A finding class that keeps coming back should become a `REVIEW.md` rule.
- **Severity and caps.** Important / Nit / Pre-existing. `REVIEW.md` can redefine Important and cap nits; the
  docs' example is "Report at most five Nits per review."
- **Done.** The check run "never concludes as a failure". For gating, the Details text ends with
  `<!-- bughunter-severity: {"nit":1,"normal":2,"pre_existing":0} -->`, and CI fails when `normal`
  (Important) is above zero. The counts "include findings from earlier reviews of the pull request whose
  threads are still open". A missing line means "no verdict rather than ... zero findings".
- **The plugin version** (`claude-plugins-official` `plugins/code-review/commands/code-review.md`) is
  simpler: it stops if "Claude has already commented on this PR". It has no later-round logic.

### `anthropics/claude-code-action`

Source: repository at commit `4411a9e` (2026-11-25): `action.yml`, `docs/solutions.md`,
`examples/pr-review-comprehensive.yml`, `src/github/data/formatter.ts`.

- It has no built-in round model. The documented auto-review examples trigger on `pull_request` `opened` and
  `synchronize`, and every run is a fresh review driven by the user's `prompt`.
- Earlier reviews and their inline comments (with `diffHunk`) reach the model through `formatReviewComments`.
  Minimized comments are filtered out. **Not found in code:** the thread resolution state (`isResolved`)
  is not passed. So avoiding repeats depends on the prompt.
- `use_sticky_comment` keeps one top-level comment. `classify_inline_comments` buffers inline comments to
  filter probes. Neither one gives findings an identity across runs.

### Cursor Bugbot

Sources: [Bugbot docs](https://cursor.com/docs/bugbot), [Building Bugbot](https://cursor.com/blog/building-bugbot),
[Bugbot learning](https://cursor.com/blog/bugbot-learning), Cursor forum threads
[#151367](https://forum.cursor.com/t/bugbot-doesnt-catch-all-issues-on-first-pass-multiple-review-cycles-needed/151367),
[#147748](https://forum.cursor.com/t/bugbot-should-filter-out-previously-resolved-dismissed-issues/147748),
[#154935](https://forum.cursor.com/t/bugbot-summary-comment-not-updated-after-fixes-are-pushed/154935).

- **What a later round covers.** "By default, Bugbot reviews only the changes since the previous Bugbot
  review." Turning **Incremental Review** off makes it "review the full pull request diff on every push".
  There is also a "Run only once per PR" setting.
- **Repeats.** It reads top-level and inline comments to "avoid duplicate suggestions and build on prior
  feedback". The pipeline includes "Dedupe against bugs posted from previous runs" (blog). Staff, 2026-06-27:
  "dedupe looks at the thread's resolved or dismissed state, and a plain reply might not count as a signal."
- **Threads.** Staff, 2026-03-17: "Inline comments go through a resolution check during re-review." The
  summary comment did not update at that time.
- **Learning.** Reactions, replies, and human reviewer comments on merged PRs become candidate rules. A rule
  is promoted on accumulated signal and disabled on "consistent negative signal".
- **Done.** The check succeeds when "Bugbot found no issues, and there are no unresolved Bugbot comments
  from earlier runs". The default conclusion with findings is neutral, and failure is opt-in. Autofix that
  commits to the branch is limited to "max 3 attempts per PR to prevent loops".
- **Known failure.** Forum #151367 (2026-02 to 2026-04): later pushes surface issues that were already in
  the original code, and one user reports "28 iterations on a single PR". Staff: "This is a known issue".

### CodeRabbit

Sources: [Commands](https://docs.coderabbit.ai/guides/commands),
[Auto review](https://docs.coderabbit.ai/configuration/auto-review.md),
[Automatic approvals](https://docs.coderabbit.ai/pr-reviews/automatic-approvals.md),
[Request changes workflow](https://docs.coderabbit.ai/pr-reviews/request-changes-workflow.md),
[Configuration reference](https://docs.coderabbit.ai/reference/configuration), the "reduce noise" guide,
[Change stack findings](https://docs.coderabbit.ai/change-stack/findings),
[Dashboard metrics](https://docs.coderabbit.ai/guides/dashboard-metrics),
[Learnings](https://docs.coderabbit.ai/knowledge-base/learnings) (all in `docs.coderabbit.ai/llms-full.txt`).

- **What a later round covers.** "By default, CodeRabbit reviews each push to a reviewed pull request,
  looking at the commits added since the last review." `@coderabbitai review` is incremental.
  `@coderabbitai full review` "disregards any comments that CodeRabbit has already made".
- **Loop cap.** `auto_pause_after_reviewed_commits`, default 5: automatic reviews pause after that many
  reviewed commits. The noise guide suggests 1 or 2 for busy PRs and then manual `@coderabbitai review`.
- **Threads.** "During the next review, CodeRabbit checks its open threads and resolves those that the
  changes addressed." `@coderabbitai resolve` clears all its threads. Learnings come from chat replies and
  apply to later reviews.
- **Severity floor.** Critical / Major / Minor / Trivial / Info. `reviews.profile`: `quiet` posts only critical
  and major inline. `chill` (default) posts "Critical, major and minor comments, up to 20, then it collapses
  minor comments and then major ones". `min_blocking_severity` (`major` or `critical`) sets what blocks
  approval. "Findings below the threshold stay visible ... and their discussions can stay open."
- **Done.** It approves only when "The latest commit has a completed CodeRabbit review", "All required review
  threads are resolved", no pre-merge check fails, and the PR is within risk limits. It "checks that the pull
  request HEAD has not changed" just before approving.
- **Across snapshots.** CodeRabbit Explain shows each finding as remains, addressed, or skipped. A finding
  "marked skipped is visible as skipped, rather than silently missing from the newer run and mistaken for one
  that got fixed". A run that is skipped, errored, rate-limited, or cancelled "has not told you the push
  cleared anything".
- **Metrics.** A comment counts as accepted only when CodeRabbit verifies that the feedback was addressed (on
  the next incremental review, or by the developer confirming in the thread). A manual resolve or
  `@coderabbitai resolve` does not count.

### GitHub Copilot code review

Sources: [Concepts](https://docs.github.com/en/copilot/concepts/agents/code-review),
[Use code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review),
changelogs [2026-08-27](https://github.blog/changelog/2026-08-27-copilot-code-review-resolution-reasons-and-expanded-capabilities),
[2026-09-11](https://github.blog/changelog/2026-09-11-auto-resolution-and-analysis-updates-in-copilot-code-review),
[2026-09-18](https://github.blog/changelog/2026-09-18-copilot-code-review-an-improved-review-experience),
[Community discussion #189767](https://github.com/orgs/community/discussions/189767).

- **Triggers.** "Unless Copilot has been configured to review each push ... it will only review a pull
  request once." The "Review new pushes" ruleset option enables push reviews, and you can re-request by hand.
- **What a later round covers.** **Not documented.** The community report (2026-03-16) says "every push to a
  PR triggers a full re-scan of the diff": 5 rounds, about 24 comments, "~3 were genuinely useful", and "If
  Copilot can find an issue on round 3, it should find it on round 1." The thread shows no staff answer.
- **Repeats.** The docs warn: "Copilot may repeat the same comments again, even if they have been dismissed"
  with "Resolve conversation" or thumbs-down.
- **Threads (2026-09).** "Comments are automatically resolved when a later commit addresses the underlying
  feedback." It honors a reply that keeps an issue open. It resolves with a reason (`Won't Fix` or
  `Incorrect`), and the overview has a "Resolved since last review" group. Humans can pick a resolution
  reason (Addressed / Won't fix / Incorrect). The changelog only says those reasons go to the product team.
- **Done.** By default it leaves a Comment review. Approvals can be enabled, and "If new commits are pushed
  after Copilot approves, the approval is dismissed".

### Graphite (Diamond, now Graphite Agent)

Sources: [AI reviews](https://graphite.com/docs/ai-reviews), [Review comments](https://graphite.com/docs/ai-review-comments.md),
`graphite.com/docs/llms-full.txt`.

- Reviews run "on new and updated pull requests". The PR size cap is 200,000 characters. Upvote and downvote
  feedback, acceptance rates, and per-rule "Issues caught" exclusion metrics are tracked.
- **Not documented:** what a later run covers, how repeats are avoided, and what happens to resolved threads.
  The human-review UI offers "hide reviewed changes" when a PR is updated after you reviewed it, which is a
  delta view for people, but nothing says the agent uses it.

### Greptile

Sources: `greptile.com/docs/llms-full.txt` (greptile.json reference, auto-approve, Fix with AI, greploop).

- **Triggers.** `autoReview` defaults to `["open"]`. Adding `push` (adds commits) or `rebase` (rewrites
  history) reviews later pushes. The docs advise: "Push multiple commits at once to avoid triggering reviews
  on every push."
- **What a later round covers.** **Not documented** (delta or whole PR).
- **Threads.** "When you push a commit that touches the flagged files, Greptile marks the corresponding review
  comments as addressed." That is a coarse file-level heuristic. **Unverified:** whether a model checks the fix.
- **Severity.** `strictness` 1-3 and `commentTypes` (logic, syntax, style).
- **Done.** A 0-5 Confidence Score. Auto-approve needs 5/5 within a risk cap and is withheld if "New commits
  landed after the review started". "When new commits are pushed to an approved PR, Greptile dismisses its
  earlier approval." The `greploop` skill loops review, fix, and push until "5/5 confidence with zero
  unresolved comments, or after the max iterations" (5).

### Qodo / PR-Agent (open source)

Source: `qodo-ai/pr-agent` at commit `4d993c2` (2026-11-26; the README now brands it The-PR-Agent):
`pr_agent/settings/configuration.toml`, `pr_agent/settings/pr_reviewer_prompts.toml`,
`pr_agent/algo/review_finding_state.py`, `pr_agent/algo/inline_comment_dedup.py`,
`pr_agent/git_providers/github_provider.py`, `docs/docs/commands/review.md`,
`docs/docs/usage-guide/automations_and_usage.md`. Qodo Merge (the hosted product) was not checked.

This is the most detailed public implementation of finding identity across rounds.

- **What a push re-reviews.** `handle_push_trigger` runs `push_commands` (default `/describe`, `/review`).
  `/review -i` is incremental: it uses the commits after the last PR-Agent review comment and diffs against
  the last seen commit. With no baseline (full rebase) it "Fall[s] back to a full review". Thresholds:
  `minimal_commits_for_incremental_review` and `minimal_minutes_for_incremental_review`.
  `per_commit_review` reviews each commit once, keyed by a fingerprint of its own patch "without line
  numbers", so a rebase that keeps a commit's patch is not reviewed again.
- **Skipping.** `skip_unchanged_diff` skips when the diff is unchanged (hunk line numbers ignored), and
  `push_trigger_ignore_merge_commits` skips "Update branch" merges.
- **Finding identity.** `persistent_finding_state` (default true) stores findings in a hidden
  `<!-- pr-agent-review-state:v1 ... -->` marker in the persistent comment. The id is
  `sha256(path | normalized body)[:12]`. To keep ids stable, earlier findings go back into the prompt
  (`max_previous_findings_chars` 8000) with states and rules:
  - "active": "report it again with the same issue_header and issue_content, word for word ... Leave it out
    if the code no longer has the issue".
  - "resolved": "Report it again only if the current code reintroduces it".
  - "dismissed" (a human resolved the thread; the prompt includes the last reply): "Do not report it again
    unless the current code makes it worse".
  - "Do not report a finding that restates an earlier one in different words."
  - "Earlier findings count toward the limit of {{ num_max_findings }} issues".
- **Resolution rule.** A finding absent from a run becomes RESOLVED only if the run was "a successful, complete
  full review" and the head SHA changed. "Incremental and partial reviews do not resolve absent findings."
  A run that dropped findings for low confidence does not resolve either. A finding that returns is
  "reopened", with a `reopened_count`. `show_previous_findings_summary` renders "Since the last review":
  addressed, reappeared, still-open, new.
- **Caps.** `num_max_findings` = 6. `min_finding_confidence` is optional.
- **Done.** `require_merge_recommendation` builds a verdict from deterministic checks (CI on the reviewed
  head, head current with base, human authors, no sensitive paths, changed lines within cap), with the model
  as "veto only". `needs_review` publishes as neutral and `changes_required` as failure. Auto-approval needs
  `no_concerns_found` and that "the review covered the whole pull request: not an incremental review". Every
  run first withdraws PR-Agent's earlier approval, and a push dismisses it.

### Google Critique, Tricorder, AutoCommenter

Sources: Sadowski et al., [Modern Code Review: A Case Study at Google](https://sback.it/publications/icse2018seip.pdf)
(ICSE-SEIP 2018); [AutoCommenter](https://arxiv.org/abs/2405.13565) (2024);
[Software Engineering at Google, ch. 20](https://abseil.io/resources/swe-book/html/ch20.html);
[Google eng-practices: The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html);
[Resolving code review comments with ML](https://research.google/blog/resolving-code-review-comments-with-ml/).

- **Process.** "When a change has been updated, the author uploads a new snapshot. The author and reviewers
  can look at diffs between any pairs of snapshots". "Unresolved comments represent action items for the
  change author to definitely address. Resolved comments include optional or informational comments". LGTM
  comes "Once all comments have been addressed". "over 80% of all changes involve at most one iteration of
  resolving comments."
- **Analysis in review.** Tricorder and Critique "typically show analysis results only for edited files or
  lines" and "focus on newly introduced warnings". A "Not useful" button feeds analyzer tuning, with a target
  of "less than 10% effective false positives".
- **AutoCommenter** "runs after each update (i.e., on each new code-review snapshot)" and "filters generated
  comments on unchanged lines of code". **Not described:** dedup against comments on earlier snapshots.
- **Done (human standard).** "reviewers should favor approving a CL once it is in a state where it
  definitely improves the overall code health". "there is no such thing as perfect code". Minor points are
  prefixed "Nit:", which the author "could choose to ignore".

### Research: MCR-Bench

Source: Zheng et al., [From Static to Dynamic: Benchmarking Real-World Code Review with MCR-Bench](https://arxiv.org/abs/2608.27442)
(ISSTA 2026).

- It has 2,269 multi-round tasks in five languages. Defect states are **New**, **Open**, **Resolved**, and
  **Reopened**. Each round's input is "the complete code diff for the current round" plus "the accumulated
  review discussions".
- F1 drops with rounds. Examples: Claude Haiku 4.5 0.6495 (R2) to 0.2857 (R10), Gemini 3 Flash 0.5983 to 0.3333.
  GPT-5.2 was more stable (0.5995 to 0.5000). Per-round sample sizes were not checked.
- The largest false-positive class (32.5%) is "State–Temporal Misalignment", which leaves "already resolved
  defects ... repeatedly flagged as new". The largest false-negative class (25.1%) is "Cross-round Defect
  Forgetting", where the model stops mentioning unresolved defects too early.

## Comparison

| Tool | Push re-reviews | Repeat control | Human-resolved thread | Later-round floor / caps | Done signal |
| :- | :- | :- | :- | :- | :- |
| Anthropic Code Review | Delta since last review; holds back unchanged-code findings | Resolves own threads when fixed; reads replies | Dismissed | Fewer nits and pre-existing; nit cap via `REVIEW.md` | Neutral check + severity JSON; gate on `normal > 0` |
| claude-code-action | Whatever the prompt says | Earlier comments in prompt only | Not passed | None built in | None built in |
| Cursor Bugbot | Delta since last Bugbot review (default) | Dedupe on prior runs and thread state | Dismissed (plain reply may not count) | Autofix max 3 attempts | Success = no findings and no unresolved earlier comments |
| CodeRabbit | Commits since last review | Resolves addressed threads; learnings | Stays resolved | Profile (quiet/chill 20); `min_blocking_severity`; pause after 5 commits | Approval when latest commit reviewed and required threads resolved |
| Copilot | Not documented (users report full re-scan) | Auto-resolves addressed comments (2026-09) | May repeat (docs warning) | None documented | Comment review; approval dismissed on push |
| Graphite Agent | Not documented | Not documented | Not documented | Not documented | Not documented |
| Greptile | Not documented | Marks addressed when flagged files change | Not documented | `strictness` 1-3 | 5/5 score, zero unresolved; approval dismissed on push |
| PR-Agent | `-i` delta or full; per-commit option | Persistent ids; verbatim restatement | Dismissed unless worse | `num_max_findings` 6, earlier findings included | Deterministic verdict; approval only after a full review |
| Google | Diff between snapshots; analysis on changed lines | Thread state | Resolved = optional/informational | <10% effective FP per analyzer | LGTM when comments addressed |

## What separates a PR review from a one-shot diff review

1. **State across rounds.** A PR review remembers earlier findings, their states, and the last reviewed head.
   MCR-Bench names the lifecycle (New, Open, Resolved, Reopened) and shows that models fail at exactly this
   tracking. PR-Agent stores the state explicitly. Critique keeps snapshots and comment resolution.
2. **Scope shrinks.** Later rounds review the delta and hold back findings on unchanged code (Anthropic,
   Bugbot, CodeRabbit, PR-Agent `-i`, AutoCommenter, Tricorder). A full re-review is a deliberate,
   on-request act.
3. **The severity floor rises.** Anthropic posts fewer nits and pre-existing findings in later rounds.
   CodeRabbit keeps sub-threshold findings advisory. Google marks nits optional.
4. **Absence is not resolution.** A finding missing from a new run is not proof of a fix (CodeRabbit Explain
   "skipped" vs "addressed"; PR-Agent resolves by absence only on a complete full review; Anthropic and
   Copilot resolve when they "judge"/"validate" the fix).
5. **Human decisions persist.** Resolved threads, resolution reasons, and replies are inputs to the next round
   (PR-Agent "dismissed", Copilot reasons, Bugbot thread state, Anthropic replies).
6. **The output is a gate on a head SHA.** It is not a list of comments. It goes stale on push (approvals
   dismissed: Copilot, Greptile, PR-Agent, CodeRabbit's HEAD check).
7. **CodeRabbit says it directly:** "PR reviews and CLI reviews will differ, even if run on the same code."

## Not verified

- Copilot: what a push review covers (delta or whole diff). Whether resolution reasons change later reviews.
- Graphite Agent: all later-round behavior.
- Greptile: what a push review covers, and whether "addressed" involves more than a file-touch heuristic.
- Bugbot: the exact dedupe algorithm. The resolution-check behavior comes from staff forum replies, not docs.
- Anthropic Code Review: how "outside the scope of this re-review" is computed (line, hunk, or file level).
- AutoCommenter: dedup against comments posted on earlier snapshots.
- Qodo Merge (hosted): whether it matches open-source PR-Agent.
- MCR-Bench: per-round sample sizes behind the R10 numbers. The last 19k characters of the HTML paper were
  not read.

## Implications for daedalus-land

1. **A round's scope is `last_reviewed_sha..HEAD`, plus a check of the open findings.** Run the lenses on the
   delta only. Re-run the whole PR only on an explicit command. (Anthropic "focuses on what changed since the
   last review"; Bugbot and CodeRabbit incremental defaults; PR-Agent `-i`.) This needs the generic
   `--base <sha>` option on `daedalus-core:code-review` that #19 already allows.
2. **Do not post later-round findings on code the round did not change.** Count them in one line instead
   ("N findings outside the scope of this round, not posted"). This targets the ~40% unchanged-code findings
   in #19. (Anthropic's two "not posted" sentences; AutoCommenter and Tricorder show results only on changed lines.)
3. **Raise the floor in later rounds.** After round 1, post only C/H, plus M in code the round changed.
   Count suppressed L and pre-existing findings. Never block on findings below the floor. (Anthropic "fewer
   nits and pre-existing findings"; CodeRabbit `min_blocking_severity`; Google "Nit:" is optional.)
4. **Give findings a persistent id and state, stored on the PR.** Keep the state (id, fingerprint, state,
   first/last seen SHA, ruling) in a hidden marker in one sticky comment, so CI and local runs share it
   without a database. Keep tags stable across rounds. (PR-Agent `pr-agent-review-state` marker and
   `sha256(path|body)` id; MCR-Bench states.) Match on path plus root cause, not exact text alone. PR-Agent
   needs verbatim restatement to make its text hash work, which is fragile.
5. **Resolve a finding only on positive verification, never by absence.** Send each open finding on changed
   code to a verifier, which returns fixed, still open, or cannot tell. A finding missing from a run stays
   open (or "not re-checked"). (CodeRabbit "skipped ... rather than ... mistaken for one that got fixed";
   Anthropic "when it judges the issue fixed"; PR-Agent resolves by absence only after a complete full review.)
   With the run-to-run variance seen in #19, absence-based resolution would close real findings at random.
6. **Rulings come from forge thread state plus an explicit reply vocabulary.** A thread a human resolved
   without a fix is `dismissed` and is not raised again unless the code makes it worse. Pass the last reply as
   the reason. Parse `won't fix` / `incorrect` / `defer` replies as rulings, because a plain reply is
   ambiguous. (PR-Agent "dismissed" prompt rule; Bugbot "a plain reply might not count"; Copilot reasons
   Addressed / Won't fix / Incorrect; Anthropic "Replying alone doesn't dismiss a finding".)
7. **Skip the round when the diff is unchanged.** After an empty commit, a clean base merge, or a rebase that
   keeps the same patch, reuse the last result and say so. (Anthropic "Code review skipped — no new
   changes"; PR-Agent `skip_unchanged_diff`, `push_trigger_ignore_merge_commits`, per-commit patch fingerprint
   "without line numbers".)
8. **The gate is "no open, verified C/H introduced by the PR, on the latest reviewed head".** Publish it as a
   status plus machine-readable counts. Treat a missing or failed round as "no verdict", never as pass. Any
   pass goes stale on the next push. (Anthropic `bughunter-severity` line and "no verdict rather than ... zero
   findings"; PR-Agent fail-closed verdict; Copilot, Greptile, and PR-Agent dismiss approval on push.) Once the
   gate passes, stop starting automatic rounds. That fixes "the loop went on after `NOT BLOCKING`" in #19.
9. **Cap the loop and the volume.** Stop automatic rounds after N reviewed pushes. Cap posted findings per
   round, and let open earlier findings count toward the cap. (CodeRabbit pause after 5; Bugbot Autofix max 3;
   `greploop` max 5; PR-Agent `num_max_findings` 6 "Earlier findings count toward the limit"; Anthropic nit cap.)
10. **Measure convergence the way the vendors measure value.** Per round: new findings, findings on
    unchanged code, verified resolutions, reopens. Count a finding as accepted only when it is verified fixed,
    never when someone resolves the thread by hand. (Bugbot resolution rate "at PR merge time"; CodeRabbit
    acceptance excludes manual resolves; MCR-Bench New/Open/Resolved/Reopened.) This feeds the #19 open item
    on PR-review evals.
11. **Show a "since the last round" section.** List addressed, reappeared, still open, and new findings, so the
    author reads the change in the review, not the whole review again. (PR-Agent
    `show_previous_findings_summary`; Copilot "Resolved since last review"; CodeRabbit Explain.)
