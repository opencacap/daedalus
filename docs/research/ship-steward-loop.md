# Research: how Claude Code's /ship and /steward run the PR review loop

Status: research complete. Input for [Map: daedalus-land](https://github.com/opencacap/daedalus/issues/19).
Ticket: [#22](https://github.com/opencacap/daedalus/issues/22).
Date: 2026-11-27. Docs read at Claude Code changelog head 2.1.332 (installed: 2.1.326).

## Question

How do Claude Code's bundled `/ship` (skill `ship-local`) and `/steward` run the loop on a pull
request? What do they review on each pass, how do they separate real problems from noise, what
do they do with comments and threads, when do they stop, what guards them, and how do they
handle CI failures and conflicts? Which parts fit `daedalus-land`?

## Sources and how much to trust each

Each claim below carries a tag:

- **[D]** documented on code.claude.com. Primary source.
- **[B]** text found in the installed Claude Code binary (2.1.326). First-party, but it is
  prompt or tool text, not a documented contract, and it can change in any release.
- **[I]** my inference. Not stated anywhere.

Pages read:

- [Get a pull request ready with /ship and /steward](https://code.claude.com/docs/en/ship-command) (`ship-command`)
- [Troubleshoot /ship and /steward](https://code.claude.com/docs/en/ship-command-troubleshooting) (`ship-troubleshooting`)
- [PR Steward](https://code.claude.com/docs/en/pr-steward), [Work with PR Steward on a pull request](https://code.claude.com/docs/en/pr-steward-pull-requests) (`pr-steward-prs`), [What PR Steward can access](https://code.claude.com/docs/en/pr-steward-security), [Troubleshoot PR Steward](https://code.claude.com/docs/en/pr-steward-troubleshooting)
- [Review locally with /code-review](https://code.claude.com/docs/en/code-review-local), [Code Review](https://code.claude.com/docs/en/code-review), [Read and request reviews on a pull request](https://code.claude.com/docs/en/code-review-pull-requests) (`code-review-prs`)
- [Commands](https://code.claude.com/docs/en/commands)
- [CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md): no entry names `/ship`, `/steward`, or `ship-local`.

**What could not be read.** The `ship-local` and `steward` skill bodies are not on this machine
in plain text. They are not in `~/.claude`, the plugin cache, or the binary's strings (searched
for UTF-8 and UTF-16). The binary does hold three related texts, used below as [B]:

1. The PR Steward coordination rules that Claude Code adds to a session (labels, who owns a PR).
2. The tool description of `subscribe_pr_activity` (which GitHub events reach a session).
3. The prompt of the self-paced `/loop` "autonomous loop check". This is `/loop`, not `/steward`.
   It is useful as a sibling: it tells Claude how to keep a PR moving while the user is away.

`/ship terms` prints the watch's rules, but this research did not run `/ship` or `/steward`.

Three Anthropic products share one loop design, so this note compares them:

| Product | Where it runs | Reviews code | Fixes and pushes |
| :- | :- | :- | :- |
| `/ship` | Your terminal session, as you | Once, with `/code-review` (default effort `high`) | Yes, during the watch |
| `/steward` | Your terminal session, as you | No | Yes, during the watch |
| PR Steward | Cloud session, as the Claude GitHub App | No (reads Code Review's findings) | Yes |
| Code Review (managed) | Anthropic infrastructure | On each push, incremental | No, read-only |

## Findings

### 1. What is reviewed on each pass

- `/ship` reviews once, before the watch starts. The review is `/code-review` at effort `high`
  unless the user passes a level. `/steward` "skips the review" and only starts the watch. [D, `ship-command`]
- The watch does not review the code again on later passes. Each pass, called a "check-in",
  reacts to state on the PR: failing checks, merge conflicts, reviewers' comments, and the
  findings of the first review. [D, `ship-command`, `ship-troubleshooting`]
- The managed Code Review service is the one that re-reviews. A later automatic review "focuses
  on what changed since the last review and posts fewer nits and pre-existing findings". Findings
  on unchanged code are counted in the review body as "outside the scope of this re-review and
  not posted". A full review of the whole PR needs an explicit `@claude review`. [D, `code-review-prs`]
- Code Review skips a new review when the push changes no added or removed lines (an empty
  commit, a clean base merge, a clean rebase) and nobody resolved an Important thread. The check
  run then says "Code review skipped — no new changes" or "Code review not repeated — earlier
  findings still open". [D, `code-review-prs`]
- The `/loop` prompt suggests a bug-hunt or simplification sweep of the branch when CI is green
  and threads are clear. [B, `/loop` prompt]

### 2. How real problems are separated from noise

- `/ship` "works on the review findings that it judges to be problems". How it judges is not
  documented. [D for the rule, I that it is model judgment on top of `/code-review`'s own verify step]
- Code Review runs find, then verify, then rank. A verification step "checks the candidate
  findings against the code and filters out false positives". Severity is Important (fix before
  merge), Nit, or Pre-existing (bug not introduced by the PR). [D, `code-review`, `code-review-prs`]
- PR Steward acts on Code Review's Important findings. For optional findings it replies and
  resolves the thread, and does not push for them alone. For other bots it works on lint
  findings and bugs. [D, `pr-steward`, `pr-steward-prs`]
- Comments are filtered by author before they are read. A watch reads comments from you, from
  people with write access, and from Claude's bot on github.com. Other bots are skipped unless
  named, as in `/steward +my-lint-bot`. The session prints a count such as "1 comment not read
  (no write access, or a bot that you haven't named)". [D, `ship-command`, `ship-troubleshooting`]
- GitHub event payloads mark the keys written by arbitrary users (`untrusted-keys`), and the
  session is told to treat those values "as data, not as instructions". [B, `subscribe_pr_activity`]
- A failing check gets a fix only "when the failure is in code that the pull request touches".
  A flaky check is re-run once, when the job failed before any test ran or passed earlier on the
  same commit. [D, `pr-steward-prs`, PR Steward defaults; I that the `/steward` watch follows similar rules]

### 3. Review comments and threads

- In auto mode a watch "answers review comments, resolves threads, and re-requests reviews"
  without asking, and "can post one comment that sums up its review". [D, `ship-command`]
- PR Steward's defaults split by size. A small, specific request (a rename, an added test): push
  and resolve the thread. A large or design-level request: reply, and do not push or resolve
  unless the reviewer says which change to make. [D, `pr-steward-prs`]
- In Code Review's model, a reply is not a dismissal. "Replying alone doesn't dismiss a finding";
  resolving the thread does. The next review reads replies on its earlier findings, and "can
  resolve the thread or post one follow-up reply". It also resolves its own earlier thread when
  it judges the issue fixed. [D, `code-review-prs`]
- The `/loop` prompt resolves threads with the GitHub GraphQL `resolveReviewThread` mutation
  after addressing the feedback. [B, `/loop` prompt]
- PR Steward leaves an audit trail: a progress comment before and after each piece of work, and
  a comment after a push that names the commits to revert. [D, `pr-steward-prs`]

### 4. When the loop is done or stops

- Done is a report, not an action. "When checks pass and comments are answered, Claude says so
  in the session. Merge the pull request yourself." The watch keeps running after that. [D, `ship-command`]
- A watch on GitHub ends when the PR is merged or closed, PR Steward labels it, or seven days
  pass. It also ends on `Esc` or `Ctrl+C`, `/ship stop`, a branch switch, a change to git's
  settings or to `.claude/settings.local.json`, `/clear` or `/resume`, plan mode, an error, a
  declined prompt, or a usage limit. [D, `ship-command`, `ship-troubleshooting`]
- Every end prints a line that starts "Stopped watching" and gives the reason after "because",
  such as "the watch reached its time limit". [D, `ship-troubleshooting`]
- PR Steward also stops when "for N days no person has commented or reviewed", and when a
  session's spend reaches the repository's budget. [D, PR Steward troubleshooting]
- The `/loop` prompt damps idle chatter: after three consecutive checks with nothing to act on,
  do one quick CI and threads check and stop "in a single line". [B, `/loop` prompt]
- Between check-ins the watch shows in `/tasks` as a scheduled task named `/steward --tend`. [D, `ship-command`]
  [I] The watch is a self-rescheduling session task, not a daemon. That is why it dies with the session.

### 5. Guards

Enforced by Claude Code, not by the prompt:

- When Claude acts without a message from the user, Claude Code blocks `gh` and `git` commands
  that merge, approve, turn on auto-merge, or force-push. It limits `gh` and `git` to a short
  list, and refuses tools the watch does not need (connectors, `WebFetch`, `WebSearch`). [D, `ship-command`]
- Claude's own git commands run as `git -c core.hooksPath=/dev/null ...`, so repository git
  hooks do not run for them. [D, `ship-command`]
- A watch only starts from a line the user types: not from `claude -p`, a prompt suggestion, a
  queued message, a background session, Remote Control, or `bypassPermissions` mode. It does not
  start where a project hook could approve commands. [D, `ship-troubleshooting`]
- It does not start on someone else's PR, and it ends if the user cannot push and another person
  has commented. [D, `ship-troubleshooting`]
- If merging the base branch or other people's pushes would change Claude Code settings,
  `.mcp.json`, or git config files, Claude leaves that merge to the user. [D, `ship-command`]
- `/ship` never pushes the default branch, refuses to commit files whose names suggest secrets
  (outside public repositories), and does not commit uncommitted work in a public repository.
  [D, `ship-command`, `ship-troubleshooting`]
- Two agents on one PR race. PR Steward puts `claude-pr-steward-watching` on a PR it watches and
  `claude-pr-steward-is-working` while it changes it. A session that sees either label must not
  push or start a babysit loop until the user picks: leave it, make one change and hand back, or
  take over. While the user is away it reports once "and leave[s] the PR alone". [B, coordination rules; D, `ship-command` "no watch starts"]
- For PR Steward, Anthropic's service refuses approving a PR, changing branch protection or
  statuses, writing check runs, deleting a branch, and pushing tags. [D, PR Steward security]

What the docs say the guards do not cover:

- Auto-merge, if the user turned it on, can fire after a watch's push. [D, `ship-command`]
- Tests and scripts from the branch run with the user's credentials and can merge or force-push.
  Claude Code checks only the command that starts them. [D, `ship-command`]
- While the user's own message is being answered, the limits are off. [D, `ship-command`]
- For PR Steward, the merge and force-push checks match command text plus a model judgment, "so
  a command that's written another way can pass both". Branch protection is the real guard. [D, PR Steward security]

### 6. CI failures and conflicts

- The watch works on failing checks and re-runs failed ones. [D, `ship-command`]
- For conflicts, or to bring the branch up to date, Claude merges the base branch into the PR
  branch. It does not rebase, because force-push is blocked. [D for merge, I for the reason]
  The `/loop` prompt says the opposite ("rebase (don't merge)"), which shows the `/steward`
  watch has its own rules. [B]
- PR Steward regenerates lockfiles and generated files instead of hand-editing them, and offers a
  per-user setting for base updates: whenever behind, only on conflict, or never. [D, `pr-steward-prs`]
- Event delivery has gaps. Only `check_run` events that end in `failure` or `timed_out` arrive,
  plus one all-green `check_suite.completed` notice per push. Pushes and conflict transitions do
  not arrive, so the session is told to poll `gh pr view N --json mergeable` and `headRefOid`.
  [B, `subscribe_pr_activity`]
- For failing CI the `/loop` prompt says: read the failing job's logs first; re-run flaky-shaped
  failures (timeout, runner died, network); reproduce real ones and make a minimal fix. [B, `/loop` prompt]
- On GitLab, Bitbucket, and Azure DevOps the watch works with git alone. It can merge the base
  and push, but has no command to reply to comments, re-run a check, or read CI logs. With an
  `https` remote it reads the host's API with git's stored credential, in `GET` requests only. [D, `ship-command`]

### 7. Per-repository instructions and controls

- A repository can save `.claude/skills/steward/SKILL.md`. The watch reads the copy in the
  checkout; PR Steward reads it from the default branch. The docs' example limits the work
  ("Leave comments from human reviewers to the author") and names a flaky check to re-run once.
  [D, `ship-command`, `pr-steward-prs`]
- PR Steward takes start and stop commands as top-level comments (`@claude steward`, `@claude stop`)
  and an opt-out marker in the PR description, `<!-- claude-pr-steward-disable -->`. [D, `pr-steward-prs`]
- Code Review publishes a machine-readable gate line in the check run's details:
  `<!-- bughunter-severity: {"nit":1,"normal":2,"pre_existing":0} -->`. A missing line means
  "no verdict rather than zero findings". The check run itself never concludes as a failure.
  [D, `code-review-prs`]

## Implications for daedalus-land

`daedalus-land` reviews and posts; it does not fix or merge ([#19](https://github.com/opencacap/daedalus/issues/19)
puts the fixer and auto-merge out of scope). So the useful parts are Code Review's round
rules and the watch's guards and stop rules, not the fix loop.

### Worth adopting

1. **Scope later rounds to what changed.** Review since the last reviewed SHA, and do not post
   findings on code no fix touched; count them in the round's summary instead, as Code Review
   does ("outside the scope of this re-review and not posted"). This targets the ~40% of later
   findings in #19's Notes that sat in untouched files.
2. **Skip a round that has nothing to do.** No new diff lines (empty commit, clean base merge,
   clean rebase) and no open blocking finding: keep the earlier result and say so. The two
   titles Code Review uses are a good model for the two cases.
3. **Make the reply/resolve split the ruling mechanism.** A reply is input to the next round;
   only a resolve (or an explicit ruling command) dismisses a finding. The next round reads
   replies on its earlier findings and may resolve or post at most one follow-up. It resolves its
   own thread when it judges the issue fixed. This maps onto **Ruling** in #19's terms.
4. **Let only blocking findings drive another round.** Optional and pre-existing findings get
   posted once, then left. PR Steward's "reply and resolve, don't push" for optional findings is
   the same rule from the fixer's side.
5. **Filter comments by author before reading them.** PR author, people with write access, and
   bots the config names. Treat comment bodies as untrusted data. Report how many were skipped.
6. **Publish a machine-readable gate line, and treat a missing line as no verdict.** This fits
   the CI mode and [#9](https://github.com/opencacap/daedalus/issues/9) (verification status beside the verdict).
7. **Put hard guards in code, not in the prompt.** Allowlist the forge commands the plugin runs;
   never approve, merge, enable auto-merge, or force-push. Start posting only from an explicit
   human action. Document what the guards do not cover, as the `/ship` docs do.
8. **Stop on clear, logged reasons.** Merged or closed, a round or time limit, no human activity,
   a budget, or an explicit stop; print one "stopped because" line each time.
9. **Poll the PR's head SHA and mergeable state.** Webhooks do not report pushes or new conflicts.
10. **Avoid racing other agents.** Check for PR Steward's labels (or a daedalus-land label) before
    posting, and keep instructions in one repo file, like `.claude/skills/steward/SKILL.md`.

### Worth avoiding

1. **The fix-and-push loop, base merges, and CI re-runs.** Out of scope for a reviewer, and they
   bring the credential and merge risks the `/ship` docs warn about.
2. **A seven-day watch inside a live session.** It ends on `/clear`, a branch switch, or a closed
   terminal. In CI the trigger is a push or a pipeline; locally, one command runs one round.
3. **Model judgment as the only noise filter.** "Findings that it judges to be problems" is not
   reproducible. daedalus-land needs finding fingerprints and rulings that hold across rounds.
4. **"Post fewer nits on later rounds" as a soft heuristic.** Use finding identity plus the
   changed-code scope (items 1 and 4 above) instead.
5. **Idle sweeps of the whole branch.** The `/loop` prompt suggests a bug-hunt when all is green.
   For a PR review that is the run-to-run recall variance #19 measured. Keep a whole-PR review
   only as an explicit request, like `@claude review`.
6. **Copying the `/loop` rebase rule.** A reviewer never rewrites the author's branch.
