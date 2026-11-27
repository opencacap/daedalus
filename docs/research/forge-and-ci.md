# Research: what GitHub, GitLab, and their CI offer an AI review bot

Status: research complete. Input for map #19 (`daedalus-land`), resolves #23.
Date: 2026-11-27. Sources read on that date: docs.github.com, docs.gitlab.com, code.claude.com/docs,
`anthropics/claude-code-action` at tag `v1.0.290`, `openai/codex-action` at tag `v1.14`, `openai/codex`
at tag `rust-v0.172.0`, and the Codex docs (developers.openai.com/codex now redirects to
learn.chatgpt.com/docs).

Claims marked **UNVERIFIED** were not found on a primary page and need a sandbox test before the spec
relies on them.

## Question

What does each forge offer a bot that posts AI review rounds (one summary with a hidden marker plus
inline comments, then later rounds that edit or add, as in #7), and how does an AI reviewer run
headless in each CI?

## GitHub vs GitLab at a glance

| Concern | GitHub | GitLab |
|---|---|---|
| Unit of a round | Pull request review: `POST /pulls/{n}/reviews` with `event` `COMMENT`, `APPROVE`, or `REQUEST_CHANGES`, a `body`, and `comments[]`. Omit `event` for a pending review. | No review object in the API. A round is draft notes (`/merge_requests/:iid/draft_notes`) then `POST .../draft_notes/bulk_publish`, or separate notes and discussions. Free tier. |
| Summary body | Review body, or an issue comment (`POST /issues/{n}/comments`) | MR note (`POST /merge_requests/:iid/notes`), body up to 1,000,000 characters |
| Inline comment | `path` + `line` + `side` (`LEFT`/`RIGHT`), `start_line`/`start_side` for ranges, `subject_type: file` for file level. `position` is being phased out. | Diff discussion with `position[base_sha, start_sha, head_sha, position_type, old_path, new_path, old_line, new_line]`, `line_range` for ranges. SHAs come from the MR `diff_refs` or the versions API. |
| After new commits or force-push | Comment keeps `original_line` and `original_commit_id`. GraphQL `PullRequestReviewThread.isOutdated` marks it outdated. | Each push creates a new diff version. Threads survive force-push. A thread whose lines changed becomes outdated, and can auto-resolve if the project sets `resolve_outdated_diff_discussions`. |
| Edit own body | `PUT /pulls/{n}/reviews/{id}` (body only), `PATCH /pulls/comments/{id}`, `PATCH /issues/comments/{id}` | `PUT .../notes/:note_id` or `PUT .../discussions/:d/notes/:note_id` |
| Delete | Only pending reviews. Submitted reviews cannot be deleted, only dismissed. | Notes and draft notes can be deleted |
| Resolve threads | GraphQL only: `resolveReviewThread`, `unresolveReviewThread`, `isResolved`, `viewerCanResolve`. People who can resolve: the PR author or anyone with write access. | `PUT .../discussions/:d` with `resolved=true`. People who can resolve: Developer role or higher, or the MR author. |
| "All threads resolved" gate | Ruleset rule: require conversation resolution | `only_allow_merge_if_all_discussions_are_resolved` (project, Free) |
| Replies | `POST /pulls/{n}/comments/{id}/replies` (top-level comment only) | `POST .../discussions/:d/notes` |
| Reactions | `GET /pulls/comments/{id}/reactions`, `GET /issues/comments/{id}/reactions`. Each entry has `user`. | `GET .../notes/:note_id/award_emoji`. Each entry has `user`. |
| Approve | Review with `event: APPROVE` | `POST .../merge_requests/:iid/approve` (Free, does not block). Required approvals and approval rules need Premium. |
| Status gate | Checks API (check runs: GitHub Apps only, 50 annotations per request, `neutral` passes) or commit statuses. Either can be a required status check. | Commit status `POST /projects/:id/statuses/:sha`. "Pipelines must succeed" gates on CI. External status checks need Ultimate. |
| Bot identity | GitHub App installation token (1 hour) posts as `<app-slug>[bot]`. `GITHUB_TOKEN` in Actions is also an installation token. | Project or group access token: a bot user, up to 365 days, Premium on GitLab.com, any license on self-managed. Service account: the only option on GitLab.com Free. `CI_JOB_TOKEN` cannot post notes. |
| Rate limits | Installation token: 5,000 requests/h, up to 12,500. `GITHUB_TOKEN`: 1,000/h per repo. Content creation: about 80/min and 500/h. Send mutations one at a time, about 1 s apart. | GitLab.com: 2,000 authenticated requests/min per user, and 60 notes/min on issues and MRs. On self-managed, admins set the limits (`notes_create_limit` defaults to 300/min). |

## Forge side: GitHub

Sources: [reviews](https://docs.github.com/en/rest/pulls/reviews),
[review comments](https://docs.github.com/en/rest/pulls/comments),
[GraphQL pulls](https://docs.github.com/en/graphql/reference/pulls),
[issue comments](https://docs.github.com/en/rest/issues/comments),
[reactions](https://docs.github.com/en/rest/reactions/reactions),
[check runs](https://docs.github.com/en/rest/checks/runs),
[commit statuses](https://docs.github.com/en/rest/commits/statuses),
[protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches),
[rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets),
[installation tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app),
[GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token),
[REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api),
[GraphQL rate limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api),
[REST best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api).

- **Review.** One API call posts the summary and all inline comments with a single notification, so it
  matches #7's "one review per round". `body` is required for `COMMENT` and `REQUEST_CHANGES`.
  `commit_id` defaults to the head. The docs warn that an old SHA "may render your review comment
  outdated". GraphQL `addPullRequestReview` takes `threads: [DraftPullRequestReviewThread]`.
- **Inline position.** Use `line` + `side`, plus `start_line`/`start_side` for a range. `position`
  (diff-relative) "is closing down". The line must be in the PR diff. **UNVERIFIED:** the exact 422
  behaviour for a line outside a hunk, and whether one invalid comment fails the whole review.
- **Outdated.** REST comments keep `original_line`, `original_start_line`, `original_commit_id`.
  GraphQL threads expose `isOutdated`, `line`, `originalLine`, `subjectType`. **UNVERIFIED:** when
  `line` becomes null after a push. Plan to read `isOutdated` and not to compute a remap ourselves.
- **Edit by marker.** List `GET /pulls/{n}/reviews`, `GET /pulls/{n}/comments`, or
  `GET /issues/{n}/comments` (100 per page, ascending ID). Filter on `user.login == "<app-slug>[bot]"`
  and the marker in `body`. Then edit with `PUT .../reviews/{id}` (body only; GraphQL
  `updatePullRequestReview` also exists). **UNVERIFIED:** that REST `PUT` works on a submitted review.
  #7's helper does it today, which suggests it does.
- **Threads.** Resolve and unresolve exist only in GraphQL. The UI docs say the PR author or anyone with
  write access can resolve. **UNVERIFIED:** that an App with `pull_requests: write` can resolve. Read
  `viewerCanResolve` at runtime.
- **Author signals.** Replies to a top-level review comment
  (`POST /pulls/{n}/comments/{id}/replies`; replies to replies are not supported). Reactions use eight
  fixed values (`+1`, `-1`, `laugh`, `confused`, `heart`, `hooray`, `rocket`, `eyes`), and the list
  response names the user.
- **Gate.** Required status checks accept check runs or commit statuses, and count `success`,
  `skipped`, and `neutral` as passing. Check runs need a GitHub App, allow 50 annotations per request
  (more through PATCH), and take the conclusions `action_required`, `cancelled`, `failure`, `neutral`,
  `success`, `skipped`, `stale`, `timed_out`. Commit statuses allow up to 1,000 per SHA and context.
  Required approvals count reviews "from people with write permissions … or from a designated code
  owner". **UNVERIFIED:** that a custom App's `APPROVE` counts toward required approvals.
  `GITHUB_TOKEN` can approve only when the repository or organization turns on "Allow GitHub Actions
  to create and approve pull requests".
- **Identity.** The installation token expires after 1 hour. It can be narrowed to some repositories
  and permissions. The App JWT that mints it lives at most 10 minutes. App bots do not use seats.
  Permissions a review bot needs: Pull requests (write), plus Checks or Commit statuses (write) for a
  gate, and Issues (write) for issue comments. Events caused by `GITHUB_TOKEN` do not trigger new
  workflow runs.
- **Rate limits.** See the table. GraphQL mutations cost 5 secondary points each. A 304 conditional
  request does not count against the primary limit. **UNVERIFIED:** a documented cap on comments per
  review. Large reviews can hit secondary limits or spam detection (422).

## Forge side: GitLab

Sources: [discussions](https://docs.gitlab.com/api/discussions/),
[notes](https://docs.gitlab.com/api/notes/), [draft notes](https://docs.gitlab.com/api/draft_notes/),
[MR reviews (user docs)](https://docs.gitlab.com/user/project/merge_requests/reviews/),
[MR versions](https://docs.gitlab.com/user/project/merge_requests/versions/),
[discussions (user docs)](https://docs.gitlab.com/user/discussions/),
[MR settings](https://docs.gitlab.com/user/project/merge_requests/),
[emoji reactions](https://docs.gitlab.com/api/emoji_reactions/),
[MR approvals API](https://docs.gitlab.com/api/merge_request_approvals/),
[approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/),
[status checks](https://docs.gitlab.com/user/project/merge_requests/status_checks/),
[commits API](https://docs.gitlab.com/api/commits/),
[auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/),
[project access tokens](https://docs.gitlab.com/user/project/settings/project_access_tokens/),
[group access tokens](https://docs.gitlab.com/user/group/settings/group_access_tokens/),
[service accounts](https://docs.gitlab.com/user/profile/service_accounts/),
[CI job token](https://docs.gitlab.com/ci/jobs/ci_job_token/),
[GitLab.com rate limits](https://docs.gitlab.com/user/gitlab_com/rate_limits/),
[self-managed rate limits](https://docs.gitlab.com/administration/settings/user_and_ip_rate_limits/).

- **Round as a review.** The UI has reviews: pending comments published on submit with the outcome
  Approve, Comment, or Request changes. In the API that is draft notes. Create each draft with `note`,
  optional `position` (same fields as discussions, including `line_range`), and optional
  `in_reply_to_discussion_id` or `resolve_discussion`. Then `POST .../draft_notes/bulk_publish` with
  optional `note` (a summary) and `reviewer_state` (`requested_changes` or `reviewed`; this is not an
  approval). The UI docs say a submitted review sends one email. **UNVERIFIED:** that `bulk_publish`
  through the API sends a single notification. The GitLab 19 upgrade notes (seen in search results
  only) say the notes rate limit counts each published draft.
- **Inline position.** Discussions need the three SHAs and both paths. Set `new_line` alone for an added
  line, `old_line` alone for a removed line, and both for an unchanged line. A range uses
  `line_range.start` and `line_range.end`, each with a `line_code` (`<sha>_<old>_<new>`). This is more
  work than GitHub's `line` + `side`, and an error is easy to make.
- **Outdated.** Every push adds a diff version and a system note. Threads persist through rebase and
  amend. A thread is outdated when a push changes its lines. The project setting
  `resolve_outdated_diff_discussions` resolves outdated threads automatically. Internally GitLab
  stores `position` and `original_position`. **UNVERIFIED:** whether REST returns `original_position`,
  and how positions get remapped to new versions.
- **Edit by marker.** `GET .../merge_requests/:iid/notes`, filter by bot user and marker, then
  `PUT .../notes/:note_id`. A note update takes exactly one of `body` or `resolved`.
- **Threads.** Threads created through `/discussions` can be resolved. Developer role or higher, or the
  MR author, can resolve them. A bot token with Developer role can therefore resolve (an inference
  from the role rule; no page says it about bots).
- **Author signals.** Replies go to `.../discussions/:d/notes`. Award emoji on notes can be read with
  `user` by any token that can read the note.
- **Gate.** On Free, `approve` and `unapprove` exist but approvals do not block. Required approvals and
  rules need Premium. `reset_approvals` is "available only to bot users with a valid project or group
  token". **UNVERIFIED:** that a token bot or service account counts as an eligible approver. Commit
  statuses take `pending|running|success|failed|canceled|skipped`, with `name` defaulting to
  `default`. **UNVERIFIED:** that a commit status set from outside CI blocks merge through
  "Pipelines must succeed". External status checks (Ultimate) are an HTTP service that GitLab calls.
  They fail if pending for more than 2 minutes, so they do not fit a review that runs for minutes.
  `detailed_merge_status` reports `discussions_not_resolved`, `not_approved`, `requested_changes`,
  `ci_must_pass`, and `status_checks_must_pass`.
- **Identity.** A project access token creates `project_{id}_bot_{random}` with a chosen role
  (Developer = 30) and scope `api`. It lasts up to 365 days by default, and a Maintainer or Owner
  creates it. On GitLab.com it needs Premium; on self-managed or Dedicated any license works. Group
  tokens (`group_{id}_bot_*`) need an Owner and the same tiers. Service accounts are available on every
  tier, and on Free they are capped at 100 per top-level group (GitLab.com) or per instance. A service
  account can join several projects. `CI_JOB_TOKEN` can only read MRs and notes. It cannot post, approve,
  or set statuses, so CI always needs a stored bot token.
- **Rate limits.** On GitLab.com, note creation is limited to 60 per minute. A round with more than
  about 60 inline findings must be throttled or batched.

## CI side: Claude Code

Sources: [claude-code-action](https://github.com/anthropics/claude-code-action) (`action.yml`,
`docs/usage.md`, `docs/configuration.md`, `docs/setup.md`, `docs/faq.md`,
`base-action/src/install-plugins.ts` at `v1.0.290`),
[GitHub Actions](https://code.claude.com/docs/en/github-actions),
[GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd),
[headless](https://code.claude.com/docs/en/headless),
[CLI reference](https://code.claude.com/docs/en/cli-reference),
[plugins CLI](https://code.claude.com/docs/en/plugins/cli-reference),
[settings reference](https://code.claude.com/docs/en/settings-reference),
[authentication](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token).

- **`anthropics/claude-code-action@v1`** (latest `v1.0.290`, composite action). It runs in automation
  mode when `prompt` is set, and in tag mode (`@claude`) otherwise.
  - Main inputs: `prompt`, `claude_args`, `settings`, `anthropic_api_key`, `claude_code_oauth_token`,
    `github_token`, `use_bedrock`, `use_vertex`, `use_foundry`, `plugins`, `plugin_marketplaces`,
    `allowed_bots`, `track_progress`, `use_sticky_comment`, and `classify_inline_comments`.
  - Outputs: `conclusion`, `execution_file`, `structured_output` (when `claude_args` has
    `--json-schema`), and `session_id`.
  - `allowed_tools`, `max_turns`, `model`, and `mcp_config` are deprecated. Pass them in `claude_args`
    as `--allowedTools`, `--max-turns`, `--model`, and `--mcp-config` instead.
- **Plugins in the action.** `plugin_marketplaces` and `plugins` are newline-separated lists, and
  plugins use the form `name@marketplace`. The action runs `claude plugin marketplace add` and
  `claude plugin install` before Claude starts. The validator accepts `https://….git` URLs and local
  paths only.
- **Permissions in the action.** The default permission mode is `auto`, a classifier review. In that
  mode a broad `--allowedTools` such as `Bash(*)` is ignored. For a strict allowlist set
  `--permission-mode acceptEdits` or `default` in `claude_args`. Classifier requests count toward token
  usage.
- **GitHub auth in the action.** By default the action uses the Claude GitHub App through OIDC, so the
  job needs `id-token: write`. With a custom App, mint a token (for example with
  `actions/create-github-app-token`) and pass it as `github_token`. For a review bot that posts as
  its own App, that is the path. The action has no GitLab support: its docs never mention GitLab.
- **Headless `claude -p`** (works in any CI).
  - Output: `--output-format json|stream-json` and `--json-schema` (the result goes to
    `structured_output`, absent on failure). The JSON output includes `total_cost_usd`, a client-side
    estimate.
  - Limits: `--max-turns` and `--max-budget-usd`.
  - Tools and permissions: `--allowedTools`, `--disallowedTools`, `--tools`, and `--permission-mode`
    (`default|acceptEdits|plan|auto|dontAsk|bypassPermissions`). The docs suggest `dontAsk` for
    locked-down CI. Since v2.1.302, `-p` defaults to Manual mode.
  - MCP: `--mcp-config` and `--strict-mcp-config`.
  - `--bare`, recommended for CI, skips installed plugins, skills, hooks, MCP, and `CLAUDE.md`. It still
    loads plugins passed with `--plugin-dir` or `--plugin-url`.
  - The init message reports `plugin_errors` and `mcp_server_errors`, so CI can fail fast.
- **Plugin install without the action.** Run
  `claude plugin marketplace add <owner/repo[@ref] | git URL | path>`, then
  `claude plugin install <plugin>@<marketplace>`, or skip installation with
  `--plugin-dir <path|.zip>`. The settings keys are `extraKnownMarketplaces` and `enabledPlugins`.
  **UNVERIFIED:** how the trust prompt for `extraKnownMarketplaces` behaves in `-p`. `--plugin-dir`
  avoids the question.
- **GitLab CI.** The code.claude.com page is in beta and "maintained by GitLab". Its example installs
  Claude with `curl -fsSL https://claude.ai/install.sh | bash` on `node:24-alpine`, then runs
  `claude -p … --permission-mode acceptEdits --allowedTools "Bash Read Edit Write mcp__gitlab"`. It
  posts through a `gitlab-mcp-server` "if your setup provides one", and the page does not say where that
  server comes from. Its variables are `ANTHROPIC_API_KEY` and `GITLAB_ACCESS_TOKEN` (`api` scope),
  with `CI_JOB_TOKEN` named as the default. That default cannot post notes (see the GitLab section).
  Bedrock and Vertex use `id_tokens` OIDC.
- **Secrets.** Use `ANTHROPIC_API_KEY`, or `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`. That
  token lasts 1 year, needs a subscription, and is tied to one person, so the docs prefer an API key
  for an organization. The action also supports workload identity federation to Anthropic, and Bedrock,
  Vertex, or Foundry through OIDC.
- **Cost.** The docs name runner minutes plus tokens and advise `--max-turns`, job timeouts, and
  `concurrency`. They give no per-run dollar figure. The only project figure is #7's measurement of
  about $17 for one 10-lens review of a real PR. `total_cost_usd` and `--max-budget-usd` let
  `daedalus-land` report and cap each round.

## CI side: OpenAI Codex

Sources: [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode),
[auth](https://learn.chatgpt.com/docs/auth), [CI auth](https://learn.chatgpt.com/docs/auth/ci-cd-auth),
[GitHub integration](https://learn.chatgpt.com/docs/third-party/github),
[GitLab integration](https://learn.chatgpt.com/codex/third-party/gitlab),
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[skills](https://learn.chatgpt.com/docs/build-skills),
[MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli),
[plugins](https://learn.chatgpt.com/docs/plugins),
[Claude plugin submission](https://developers.openai.com/plugins/guides/submit-claude-plugin),
[pricing](https://learn.chatgpt.com/docs/pricing),
[codex-action](https://github.com/openai/codex-action) (`README.md`, `action.yml` at `v1.14`),
`openai/codex` source at `rust-v0.172.0` (`codex-rs/exec/src/cli.rs`, `codex-rs/cli/src/main.rs`).

- **`codex exec`.**
  - Output: `--json` (JSONL events), `-o/--output-last-message`, and `--output-schema <file>`.
  - Sandbox: `-s/--sandbox read-only|workspace-write|danger-full-access`. Exec defaults to read-only.
  - Other flags: `-m/--model`, `--skip-git-repo-check`, `--ephemeral`, and `-c key=value`.
  - `--full-auto` is no longer supported.
  - `codex exec review --base <branch>` (also `codex review`) is a built-in review.
- **Codex auth in CI.** `CODEX_API_KEY` can be set inline for one run, or run
  `printenv OPENAI_API_KEY | codex login --with-api-key`. The docs warn against job-level key env vars
  when the job runs repository-controlled code. ChatGPT `auth.json` on runners is only for trusted
  private runners.
- **`openai/codex-action@v1`** (latest `v1.14`).
  - Inputs: `prompt`, `prompt-file`, `openai-api-key`, `permission-profile` (`:read-only`,
    `:workspace`), `sandbox` (legacy), `codex-args`, `output-schema(-file)`, `model`, `effort`,
    `safety-strategy` (`drop-sudo` by default), and `allow-users` / `allow-bots`.
  - Output: `final-message`.
  - The README's PR bot example splits the work into two jobs. A read-only Codex job produces the text,
    and a second job with `pull-requests: write` posts it with `actions/github-script`. The model never
    holds the write token.
- **Built-in Codex review.** Codex cloud reviews GitHub PRs on `@codex review` or automatically, and
  posts as `chatgpt-codex-connector`. It posts only P0 and P1 findings, with rules from `AGENTS.md`. A
  GitLab MR integration is in beta: reviews start on a mention and come from a workspace service
  account. Neither integration can host our own rounds, rulings, or gate.
- **Codex in GitLab CI.** No official doc or `.gitlab-ci.yml` example. Running `codex exec` in a GitLab
  job is our own setup (**UNVERIFIED** in practice).
- **Reuse of daedalus content.** Codex reads `AGENTS.md`, and reads `CLAUDE.md` only through
  `project_doc_fallback_filenames`. Skills live in `.agents/skills` from the working directory up to the
  repository root, and in `$HOME/.agents/skills`. Each skill needs `SKILL.md` with `name` and
  `description`. MCP servers go under `[mcp_servers.<name>]` in `config.toml`. Codex plugins use
  `.codex-plugin/plugin.json`. The submission guide converts a skills-only Claude plugin. It says to
  turn commands and agents into skills, removes hooks, and leaves out `.mcp.json`. A Claude Workflow
  script has no Codex equivalent.
- **Cost.** The pricing page lists per-model credit rates and usage-based rates, and gives no per-review
  figure. GitHub reviews by Codex cloud draw from a separate Code Review usage bucket. API-key use is
  billed at standard API rates. The model names and prices came through a fetch summary; check them on
  the page before quoting them in a decision.

## Implications for daedalus-land

**What a forge-neutral posting layer must abstract**

1. **Publish a round atomically.** On GitHub that is one review call with the body and `comments[]`. On
   GitLab it is N draft notes, then `bulk_publish` with the summary as `note`. The port is
   `publishRound(summary, findings[], headSha)`, and it returns IDs for the summary and each thread.
2. **Anchor a finding.** Store a neutral anchor: `path`, `side` (old/new), `startLine`, `endLine`,
   `headSha`. The GitHub adapter maps it to `line`/`side`/`start_line`. The GitLab adapter builds
   `position` from `diff_refs` and the line codes. A file-level fallback covers lines outside the diff
   (GitHub `subject_type: file`; on GitLab, a `position_type: file` or a plain note).
3. **Find and edit own posts.** List the posts, filter by bot identity and hidden marker, and edit the
   body. The marker carries the round number and the finding fingerprints, so the next round can match
   findings and does not need forge-side state.
4. **Read the thread state** as one model: `resolved`, `outdated`, replies, and reactions with their
   authors. Rulings come from replies or reactions and are normalized before the matching logic sees
   them.
5. **Report the gate** through one port (`setGate(state, summaryUrl)`). On GitHub use a check run, or a
   commit status when the token is not an App token. On GitLab use a commit status. Map
   `NOT BLOCKING` to a passing state (GitHub `neutral` or `success`, GitLab `success`).
6. **Mint credentials.** On GitHub, the App JWT gives a 1-hour installation token. On GitLab, read a
   project or group access token or a service account PAT from a secret. The CI job token is never
   enough on GitLab.
7. **Throttle.** Send mutations serially, about 1 s apart on GitHub, under 60 notes/min on GitLab.com.
   Honour `Retry-After`.
8. **Dry run.** The adapter's input payload is the artifact that evals grade (#7 acceptance criteria).

**Gaps between forges**

- GitLab has no review object in the API. Draft notes come close, but single notification and rate
  limit behaviour on `bulk_publish` are unverified.
- GitHub resolves threads only through GraphQL, and an App's right to resolve is unverified. GitLab
  resolves through REST for Developer role or higher. Keep "never resolve threads in CI" (#7) as the
  policy on both forges.
- Approval as a gate: an App's approval may not count on GitHub, and on GitLab approvals block only on
  Premium. A status check or commit status is the portable gate.
- Bot identity costs differ. A GitHub App is available on every GitHub plan, and its bot uses no seat. On GitLab.com Free the only bot is a
  service account. Project and group tokens need Premium there.
- Outdated handling differs. GitHub flags threads with `isOutdated`. GitLab may auto-resolve outdated
  threads when a project setting is on, so a finding can look resolved without any author ruling. The
  matching logic must treat auto-resolved as "code changed", not as a ruling.
- GitLab position objects are more fragile: three SHAs and line codes. Test that adapter first.

**CI runner notes for the spec**

- GitHub: `claude-code-action` with a custom App token. Load the plugin with `plugin_marketplaces` and
  `plugins`, and set `--permission-mode` explicitly. Or use plain `claude -p` with `--plugin-dir`. The
  action adds nothing for GitLab.
- GitLab: plain `claude -p` in a job, posting through the daedalus adapter with a bot token, not the
  beta MCP flow.
- Codex: `codex exec --output-schema` in a read-only sandbox produces the findings, and a separate step
  posts them. A Codex path can reuse the skills but not the Workflow script.
- Keep the model run apart from the write token. This is codex-action's two-job pattern, and it is
  worth copying for Claude too.

## Open items to test on a sandbox repository

- GitHub: `PUT` on a submitted review body, an App resolving a thread, an App's `APPROVE` counting
  toward required approvals, and a comment cap per review or a 422 on a line outside the diff.
- GitLab: notification count and rate-limit accounting for `bulk_publish`, whether a token bot counts
  as an eligible approver, whether an external commit status blocks merge, and whether REST returns
  `original_position`.
- Claude: trust handling of `extraKnownMarketplaces` in `-p`.
- Codex: a working `codex exec` job in GitLab CI.
