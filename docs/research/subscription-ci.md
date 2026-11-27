# Research: Claude Code on a subscription (OAuth) in CI on a self-hosted runner

Status: research complete. Input for map #19 (`daedalus-land`), resolves #33, feeds #30.
Date: 2026-11-27. Sources read on that date: code.claude.com/docs (authentication, legal-and-compliance,
headless, costs, errors, cli-reference, env-vars, settings-reference, interactive-mode, llm-gateway,
github-actions, gitlab-ci-cd, Agent SDK TypeScript reference, agent loop, cost tracking), anthropic.com
legal pages (Consumer Terms effective Oct 8, 2025; Commercial Terms effective Jun 17, 2025; Service
Specific Terms effective Aug 31, 2026; Usage Policy), support.claude.com (articles 11845131, 11145838,
12429409, 11049741, 9797557), `anthropics/claude-code-action` at `main` commit `4411a9e9b028`
(`action.yml`, `docs/setup.md`, `docs/security.md`, `docs/usage.md`), docs.github.com, and
docs.gitlab.com.

Claims marked **UNVERIFIED** were not found on a primary page and need a sandbox test, or a written
answer from Anthropic, before the spec relies on them.

## Question

Can `daedalus-land`'s CI review job run `claude -p` on a Claude subscription (Pro, Max, Ultra, Team, or
Enterprise) through OAuth, either `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` or a logged-in
self-hosted runner, instead of an organization API key or a cloud provider?

## Verdict at a glance

| Question | Answer |
|---|---|
| Allowed: one person's Pro/Max/Ultra plan reviewing that person's own repositories | Yes. The docs offer `claude setup-token` "for CI pipelines, scripts, or other environments where interactive browser login isn't available". Limits assume "ordinary, individual usage". |
| Allowed: one person's Pro/Max/Ultra plan reviewing an organization's PRs for a team | No in practice. The Consumer Terms forbid sharing credentials and making the account "available to anyone else". Every teammate's push would spend that one person's plan. |
| Allowed: a Team or Enterprise seat | The Commercial Terms apply and have no credential-sharing clause. Seats are per member, and the docs say to use an API key for a secret shared across repositories. A seat used as a team bot is **UNVERIFIED**. Ask Anthropic sales. |
| Usage limits | Seat or plan allowance with a rolling five-hour window and a weekly window, shared with Claude chat, Cowork, and the member's own Claude Code use. No dollar or token size is published, so how many $8 to $20 rounds fit is **UNVERIFIED**. |
| On hitting a limit in `-p` | The run fails. `-p` never waits for the reset. The stream carries `rate_limit_event` with `status: "rejected"` and `resetsAt`, and the assistant message carries `error: "rate_limit"`. The exact `result` subtype is **UNVERIFIED**. |
| `total_cost_usd`, `--max-budget-usd` | Both are client-side estimates at list price, computed the same way for every credential. On a subscription they measure API-equivalent spend, not money billed. The cap still stops the run. That it fires on a subscription is **UNVERIFIED** by test. |
| Token lifetime and scope | `setup-token` gives a one-year token with only the `user:inference` scope. It is not saved, not refreshed, and is revoked by signing out everywhere or by an admin. No per-token revoke UI is documented (**UNVERIFIED**). |
| `--bare` | Bare mode never reads `CLAUDE_CODE_OAUTH_TOKEN`, OAuth credentials, or the keychain. A subscription driver cannot use `--bare`. |
| Self-hosted runner | Possible on both forges. Use ephemeral, single-job runners, keep the token in a protected secret, and never run fork PRs on them. One runner per job. One login refresh lock per machine. |
| For `daedalus-land` | Keep rejecting subscription OAuth as the default. At most, allow it as a documented personal mode for a solo maintainer on their own repositories, with no `--bare`, serialized jobs, and limit errors mapped to "retry later". |

## Terms: what is allowed

Sources: [legal and compliance](https://code.claude.com/docs/en/legal-and-compliance),
[Consumer Terms](https://www.anthropic.com/legal/consumer-terms),
[Commercial Terms](https://www.anthropic.com/legal/commercial-terms),
[Service Specific Terms](https://www.anthropic.com/legal/service-specific-terms),
[Usage Policy](https://www.anthropic.com/legal/aup),
[authentication](https://code.claude.com/docs/en/authentication),
[GitHub Actions](https://code.claude.com/docs/en/github-actions).

- **Which terms apply.** The legal page lists the Commercial Terms "for Team, Enterprise, and Claude API
  users" and the Consumer Terms "for Free, Pro, Max, and Ultra users".
- **Consumer Terms, account sharing (section 2).** Exact wording: "You may not share your Account login
  information, Anthropic API key, or Account credentials with anyone else. You also may not make your
  Account available to anyone else. You are responsible for all activity occurring under your Account".
- **Consumer Terms, automation (section 3).** Exact wording of the forbidden use: "Except when you are
  accessing our Services via an Anthropic API Key or where we otherwise explicitly permit it, to access
  the Services through automated or non-human means, whether through a bot, script, or otherwise."
- **The explicit permission for scripts.** The authentication page says about `CLAUDE_CODE_OAUTH_TOKEN`:
  "Use this for CI pipelines and scripts where browser login isn't available." And about
  `claude setup-token`: "For CI pipelines, scripts, or other environments where interactive browser
  login isn't available, generate a one-year OAuth token". Our reading: this is the "where we otherwise
  explicitly permit it" exception for the account owner's own scripts. That reading is ours, not a
  quoted Anthropic statement.
- **Ordinary, individual use.** The legal page: "Advertised usage limits for Pro, Max, and Ultra plans
  assume ordinary, individual usage of Claude Code and the Agent SDK." And: "OAuth authentication is
  intended exclusively for purchasers of Claude Free, Pro, Max, Ultra, Team, and Enterprise subscription
  plans and is designed to support ordinary use of Claude Code and other native Anthropic applications."
- **No routing on behalf of others.** The legal page: "Anthropic does not permit third-party developers
  to offer Claude.ai login into their own applications, or to route requests through Free, Pro, Max, or
  Ultra plan credentials on behalf of their users. Moreover, developers may not collect, store, or
  intermediate Claude.ai credentials or session tokens — sign-in to a Claude account must complete
  through Anthropic's own flow." It also says the rule does not "prevent an end user from signing in to
  the unmodified Claude Code binary with their own Claude subscription". Enforcement: "Anthropic
  reserves the right to take measures to enforce these restrictions and may do so without prior notice."
- **Products that run Claude Code.** "Customers may not pay for, resell, or intermediate Claude usage on
  their end users' behalf. Each end user must authenticate with their own Anthropic API key, Claude
  subscription plan credentials, or 3P inference provider credential". This matters only if
  `daedalus-land` were ever hosted for other people. Each installer bringing their own credential is
  fine.
- **Commercial Terms (Team, Enterprise).** D.4 restricts competing products, reverse engineering, and
  resale. D.5: "Customer is responsible for all activity under its account." No clause on sharing a
  member's credential was found. The Service Specific Terms section A (Claude for Work) covers user
  notices and data only. Whether one member's seat may serve as a shared team bot is **UNVERIFIED**.
- **Docs guidance for shared secrets.** The GitHub Actions page: "For a secret shared across
  repositories, authenticate with an API key from the Claude Console rather than an OAuth token, since
  an OAuth token is tied to the subscription of the person who ran `claude setup-token`."
- **Usage Policy.** Nothing on CI. It forbids "Coordinate malicious activity across multiple accounts,
  or create multiple accounts, to avoid detection, circumvent product guardrails", which rules out
  rotating several personal plans to dodge limits.

**Per case**

1. Solo maintainer, own plan, own repositories: allowed by the setup-token wording. Heavy automated
   use is outside "ordinary, individual usage", so expect limits, and possibly enforcement, if it runs
   all day.
2. One person's Pro/Max/Ultra plan reviewing an organization's PRs that teammates push: conflicts with
   "may not make your Account available to anyone else". Not acceptable for a public tool's default.
3. A Team or Enterprise member's seat: not forbidden by any clause found. It is still one member's
   allowance and identity, and the docs steer shared use to API keys. Treat it as **UNVERIFIED** and
   ask Anthropic.
4. One token shared across a team or many repositories: no. This is case 2 or 3 with a wider blast
   radius.

## Usage limits and what `-p` does when they run out

Sources: [costs](https://code.claude.com/docs/en/costs),
[errors](https://code.claude.com/docs/en/errors),
[interactive mode](https://code.claude.com/docs/en/interactive-mode),
[headless](https://code.claude.com/docs/en/headless),
[Agent SDK TypeScript reference](https://code.claude.com/docs/en/agent-sdk/typescript),
support articles [11845131](https://support.claude.com/en/articles/11845131),
[11145838](https://support.claude.com/en/articles/11145838),
[12429409](https://support.claude.com/en/articles/12429409),
[11049741](https://support.claude.com/en/articles/11049741).

- **Windows.** Pro and Max have "a five-hour session limit and a weekly limit". Ultra has a weekly
  limit, and verified Ultra accounts have no five-hour limit. Max and Ultra have a separate weekly
  limit for Fable. Max is "five times the Pro plan's usage every five hours and every week". The limits
  "are shared across Claude and Claude Code".
- **Team and Enterprise.** "each member's Claude Code usage draws from a per-seat allowance that resets
  on a rolling five-hour window and a weekly window. The allowance is shared with Claude chat and
  Cowork". Usage-based Enterprise plans have "no per-seat usage limits" and bill at API rates.
- **No published size.** No page gives the allowance in tokens or dollars. The Max article adds:
  "Additional usage limits may apply ... We don't guarantee uninterrupted service." How many $20 full
  rounds or $8 delta rounds fit in a window is **UNVERIFIED**. Measure it with `/usage` before and
  after a real round.
- **Fan-out.** The errors page: "Usage counts against the session and weekly allowances at the same
  time. A single burst of heavy activity, such as a large workflow fanout, can exhaust the weekly
  allowance before the session window resets." Many PRs reviewed at once all drain one account.
- **Messages.** `You've hit your session limit · resets 3:45pm`, `You've hit your weekly limit · resets
  Mon 12:00am`, and model-family variants for Opus and Sonnet. "Claude Code blocks further requests
  until the reset time shown in the message."
- **No waiting in `-p`.** Interactive sessions can wait and continue after the reset, but "Claude Code
  doesn't offer the wait at all in these cases: Background sessions and `-p` runs". So a `-p` round
  that hits the limit stops.
- **Not retried.** Automatic retries cover 429 throttles that "don't carry your plan's quota headers".
  A real plan limit carries those headers, so Claude Code does not retry it.
- **What the stream carries.**
  - `rate_limit_event` with `rate_limit_info.status` of `allowed`, `allowed_warning`, or `rejected`,
    plus `resetsAt` and `utilization`. `errorCode: "credits_required"` means "a claude.ai subscription
    whose included usage is exhausted".
  - The assistant message's `error` field: "A 429 against your quota is `'rate_limit'`".
  - The `result` message has `api_error_status` (the HTTP status) and `terminal_reason` (values include
    `api_error` and `budget_exhausted`).
  - **UNVERIFIED:** whether the `result` subtype is `success` with `is_error: true` or
    `error_during_execution`, and which `terminal_reason` a quota rejection sets. Test it, and key the
    driver on `rate_limit_event.status == "rejected"` and `error == "rate_limit"`, not on the subtype.
- **Partial work.** The Pro/Max article describes a small "wrap-up allowance" at the five-hour limit
  that lets "a response that's already in progress" finish. It is rolling out gradually. A review
  round is many requests, so most of the round still fails and any findings so far are lost unless the
  driver saved them.
- **Usage credits.** With usage credits on, requests past the limit "switch to pay-as-you-go pricing on
  usage credits" at "standard API rates". A Team or Enterprise member without billing access cannot
  ask for credits from `-p`: "in non-interactive mode with the `-p` flag ... the command sends no
  request".

## `total_cost_usd` and `--max-budget-usd` on a subscription

Sources: [headless](https://code.claude.com/docs/en/headless),
[CLI reference](https://code.claude.com/docs/en/cli-reference),
[cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking),
[costs](https://code.claude.com/docs/en/costs).

- `total_cost_usd` is a "cumulative estimated cost in USD". The SDK "computes them locally from a price
  table bundled at build time". No page makes it depend on the credential type, so on a subscription it
  is the API-price equivalent of the round.
- The costs page says the session dollar figure "is intended for API users" and that for Pro, Max, and
  Ultra subscribers "the session cost figure isn't relevant for billing purposes".
- `--max-budget-usd`: "Stop the run once estimated spend on API calls reaches this amount (print mode
  only). Claude Code checks the cap against its client-side cost estimate". Spend from subagents
  counts, and "Spend can pass the cap, so leave headroom".
- **Meaning for daedalus-land.** Both fields keep working as a size measure and a runaway brake. They no
  longer say what the round cost anyone. The real constraint is the share of a five-hour and weekly
  window, which no field in the result reports. `rate_limit_event.utilization` is the closest signal.
- **UNVERIFIED:** that `--max-budget-usd` fires the same way when the credential is
  `CLAUDE_CODE_OAUTH_TOKEN`. The docs imply it, but no page says so for subscriptions.

## Token lifetime, scopes, rotation, revocation

Sources: [authentication](https://code.claude.com/docs/en/authentication),
[env vars](https://code.claude.com/docs/en/env-vars),
[errors](https://code.claude.com/docs/en/errors),
[Agent SDK TypeScript reference](https://code.claude.com/docs/en/agent-sdk/typescript),
[GitHub Actions](https://code.claude.com/docs/en/github-actions),
`claude-code-action` `docs/setup.md`.

- **Lifetime.** `claude setup-token` generates "a one-year OAuth token". It "does not save the token
  anywhere". It "requires a Pro, Max, Ultra, Team, or Enterprise plan". (`claude-code-action`'s
  `setup.md` still says "Pro and Max users", which is out of date.)
- **Scope.** The token "can only make model requests, so it can't establish Remote Control sessions or
  fetch claude.ai connectors". The SDK reference says it "carries only the `user:inference` scope".
  Because it lacks `user:profile`, plan usage data in `rate_limits` can be `null`.
- **Precedence.** `CLAUDE_CODE_OAUTH_TOKEN` is fifth, after cloud provider variables,
  `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY`, and `apiKeyHelper`. "In non-interactive mode (`-p`), the
  key is always used when present", so a stray `ANTHROPIC_API_KEY` silently moves the run to API
  billing.
- **No refresh.** "Unless you run `/login`, Claude Code uses the token you set for the whole session. To
  replace an expired token, generate a new one and restart". After a 401 "Claude Code keeps sending the
  value you set".
- **Expiry and revocation errors in `-p`.** `Failed to authenticate: OAuth token revoked. Please log in
  again or contact your administrator.` and `Failed to authenticate. API Error: 401 OAuth token has
  expired ...`, with the structured error code `authentication_failed`. "A revoked token means you
  signed out everywhere or an admin removed access".
- **Rotation.** Manual: the person runs `claude setup-token` again and replaces the CI secret. Deleting
  the CI secret does not revoke anything: "If you delete a secret, the credential it held stays valid."
  `claude-code-action` advises "Regularly rotate your API keys and tokens".
- **Revoking one token.** No page documents how to revoke one setup-token without signing out
  everywhere. **UNVERIFIED.**
- **Organization pinning.** `claude setup-token` and `/install-github-app` "enforce only
  `forceLoginMethod`, so they can mint a token in a different organization". An admin cannot pin these
  tokens with `forceLoginOrgUUID`.
- **Logged-in runner instead of a token.** A `/login` session stores credentials in
  `~/.claude/.credentials.json` (mode `0600`) on Linux, or the macOS Keychain. That login has an end
  date ("Using Claude Code doesn't extend the login"), visible with `claude auth status --text`. A `-p`
  run within 10 days of the end prints `Warning: this sign-in` on stderr. Concurrent processes share one
  refresh lock, and a stuck lock fails the request with `Failed to refresh OAuth token: another Claude
  Code process is refreshing it ...` (error code `server_error`).
- **Bare mode.** "Bare mode does not read `CLAUDE_CODE_OAUTH_TOKEN`." And: "In bare mode, Claude Code
  never reads OAuth credentials or the system keychain." The docs recommend `--bare` for CI and say it
  "will become the default for `-p` in a future release". Once that ships, a subscription run will need
  an explicit opt-out flag. **UNVERIFIED:** which flag that will be.

## Self-hosted runners

Sources: [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use),
[GitHub self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners),
[GitHub events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows),
[GitHub secrets](https://docs.github.com/en/actions/concepts/security/secrets),
[GitHub fork approvals](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks),
[GitLab runner security](https://docs.gitlab.com/runner/security/),
[GitLab runner advanced config](https://docs.gitlab.com/runner/configuration/advanced-configuration/),
[GitLab configure runners](https://docs.gitlab.com/ci/runners/configure_runners/),
[GitLab CI/CD variables](https://docs.gitlab.com/ci/variables/),
[GitLab MR pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/).

A self-hosted runner is not needed for subscription auth. `CLAUDE_CODE_OAUTH_TOKEN` works on hosted
runners too, and the docs' quick setup stores it as a repository secret. A self-hosted runner only
matters for the "logged-in machine" variant, or to keep the token off shared infrastructure.

**GitHub Actions**

- **Public repositories.** "self-hosted runners should almost never be used for public repositories on
  GitHub" "because any user can open pull requests against the repository and compromise the
  environment."
- **Persistence.** A runner "can be persistently compromised by untrusted code in a workflow", and
  "there is no way to guarantee that a self-hosted runner only runs one job" unless it is ephemeral:
  "With ephemeral runners, this can be guaranteed because GitHub only assigns one job to a runner."
  Register with `--ephemeral`, or create just-in-time runners through the REST API, which "perform at
  most one job before being automatically removed". GitHub "recommends implementing autoscaling with
  ephemeral self-hosted runners".
- **Secrets between jobs.** "Some jobs will use secrets as command-line arguments which can be seen by
  another job running on the same runner". A logged-in persistent runner hands its
  `~/.claude/.credentials.json` to every later job on that machine.
- **Boundaries.** Runner groups limit which repositories use which runners. Organization secrets take a
  repository access policy, and environment secrets can require reviewers: "A workflow job cannot access
  environment secrets until approval is granted by required approvers."
- **Fork PRs.** On `pull_request`, "secrets are not passed to the runner when a workflow is triggered
  from a forked repository" and "The `GITHUB_TOKEN` has read-only permissions". `pull_request_target`
  runs with secrets, and GitHub warns: "Running untrusted code on the `pull_request_target` trigger may
  lead to security vulnerabilities." Outside contributors' runs "may require manual approval from a
  maintainer with write access".
- **Concurrency.** One ephemeral runner takes one job. Parallel PRs need parallel runners. On one
  persistent machine they also share one login and its refresh lock.

**GitLab**

- **Executor.** "High-security risks exist to your runner host and network when running builds with the
  shell executor". "Docker can be considered safe when running in non-privileged mode". Privileged mode
  lets a job "gain full root access to the runner's host system".
- **Sharing and persistence.** "A job from a repository embedded with malicious code can compromise the
  security of other repositories", and "This risk is even more acute if your self-managed runners are
  non-ephemeral and used for multiple projects." With Docker Machine, use `MaxBuilds = 1`. "Secret
  variables exposed to jobs running in a compromised environment can be stolen".
- **Protected runners and variables.** Runners can be set to "only run jobs on protected branches, or
  jobs that have protected tags", and variables can be "available only to pipelines that run on
  protected branches or protected tags". Masking helps, but "Masking a CI/CD variable is not a guaranteed
  way to prevent malicious users from accessing variable values."
- **Fork MRs.** By default the pipeline "runs in the fork (source) project" with the fork's variables,
  and "Merge request pipelines from forked repositories cannot access these protected resources." A
  parent project member can run it in the parent with the parent's variables, behind the warning "Fork
  merge requests can contain malicious code that tries to steal secrets in the parent project".
- **Concurrency.** `concurrent` "Limits how many jobs can run concurrently, across all registered
  runners". The per-runner `limit` caps one registration (`0` means no limit). Set `limit = 1` on a
  runner that holds a login.

**Runner recipe if a subscription is used anyway**

1. Store `CLAUDE_CODE_OAUTH_TOKEN` as a protected or environment secret, scoped to the review job only.
   Do not keep a `/login` session on a long-lived machine.
2. Use ephemeral, single-job runners (GitHub `--ephemeral` or JIT; GitLab Docker executor,
   non-privileged, `MaxBuilds = 1`), in a runner group or as protected runners for one project.
3. Never run the review job for fork PRs or MRs with the secret. Do not use `pull_request_target` to
   work around this.
4. Unset `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` in that job, so the run does not fall back to
   API billing without notice.
5. Serialize review jobs across all PRs that share the token (GitHub `concurrency` group; GitLab
   `resource_group` or runner `limit = 1`), because they share one allowance.

## Implications for daedalus-land

- **Keep the current rejection as the default.** The three reasons in the proposal hold, and the
  primary sources add two more. The Consumer Terms forbid making the account available to others, and
  limit exhaustion fails a `-p` round with no wait and no retry.
- **A subscription mode would break `--bare`.** The forge-and-ci notes recommend `--bare` with
  `--plugin-dir`. Bare mode ignores `CLAUDE_CODE_OAUTH_TOKEN`, so a subscription mode needs non-bare
  runs. Those runs load the runner's hooks, plugins, `CLAUDE.md`, and the repository's
  `.claude/settings.json` hooks and `.mcp.json` servers "even in a folder you've never trusted". That
  widens what PR content can do inside the review job.
- **Budget semantics change.** `--max-budget-usd` 20 and 8 still cap runaway rounds, and
  `total_cost_usd` still sizes them, but the stored value is API-equivalent, not billed. Label it as an
  estimate. The real limit is the window, which the driver sees only through `rate_limit_event`.
- **New failure state.** The driver needs a "quota exhausted, retry after `resetsAt`" outcome distinct
  from a review failure. It must not post a partial round, and it must not burn retries before the
  reset.
- **Concurrency conflicts with "many PRs at once".** All rounds on one token drain one window. A
  subscription mode must serialize globally, not only per PR.
- **Credential expiry.** A one-year token fails with `authentication_failed`. The driver should report
  that as a configuration error and name `claude setup-token`.
- **If supported at all**, document it as a personal mode for a solo maintainer reviewing their own
  repositories: their own token, no fork PRs, no `--bare`, global serialization, and a warning that
  Anthropic can enforce "ordinary, individual usage" without notice. Do not offer it for organization
  repositories. Point Team and Enterprise users at an API key, workload identity federation, or a cloud
  provider.

## Open items

- Ask Anthropic: may a Team or Enterprise seat's `setup-token` run an organization's automated PR
  review, and is unattended CI on a personal plan within "ordinary, individual usage"?
- Sandbox: the `result` subtype, `is_error`, `terminal_reason`, `api_error_status`, and exit code when
  a subscription limit hits mid-round in `-p` with `--output-format stream-json`.
- Sandbox: `--max-budget-usd` with `CLAUDE_CODE_OAUTH_TOKEN`, and the share of a Max five-hour window
  that one full round and one delta round use.
- Docs: how to revoke one setup-token without signing out everywhere, and which flag keeps OAuth
  working once `--bare` becomes the default for `-p`.
