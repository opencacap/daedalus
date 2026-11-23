# daedalus

A Claude Code and Codex plugin marketplace for shared engineering rules and workflow plugins.

## Plugins

| Plugin | What it does |
|---|---|
| `daedalus-core` | Loads the shared engineering rules in [`plugins/daedalus-core/rules/`](plugins/daedalus-core/rules/) at every session start, and provides the `code-review` and `security-review` skills (see [Code review](#code-review)). Depends on [`mattpocock-skills`](https://github.com/mattpocock/skills) (engineering workflow) and the pinned `ponytail` and `caveman` entries below. |
| `daedalus-writing` | Opt-in editorial skills for Vietnamese (`vietnamizer`), English (`clarity`), Japanese documents (`natural-japanese`), and Japanese correspondence (`slop-nuki`). Depends on `daedalus-core`. |
| `daedalus-java` | Skill `java-coding-standards`: framework-agnostic Java standards. Depends on `daedalus-core`. |
| `daedalus-springboot` | Skills `spring-coding-standards`, `springboot-patterns`, `springboot-security`, `springboot-verification`, `hexagonal-architecture`, `jpa-patterns`, and the `java-build-resolver` agent. Depends on `daedalus-java`. |
| `daedalus-infra` | Skill `docker-patterns`. Depends on `daedalus-core` and the official [`aws-core`](https://github.com/aws/agent-toolkit-for-aws) and `terraform` (HashiCorp) plugins from `claude-plugins-official`. Their MCP servers need `uvx` plus AWS credentials (`aws-mcp`) and a running Docker daemon (`terraform`); without them the server fails to connect but the skills still work. |
| `daedalus-postgres` | Skill `postgres-patterns`. Depends on `daedalus-core`. Opt-in: no stack plugin depends on it, so enable it in projects that use PostgreSQL. |
| `daedalus-python` | Skills `python-patterns` and `python-testing`. Depends on `daedalus-core`. |
| `daedalus-fastapi` | Skill `fastapi-patterns`. Depends on `daedalus-python`. |
| `daedalus-typescript` | Skill `typescript-patterns`. Depends on `daedalus-core`. |
| `daedalus-frontend` | Skills `accessibility`, `make-interfaces-feel-better`, `vite-patterns`, and `e2e-testing` (Playwright). Depends on `daedalus-typescript`. |
| `daedalus-react` | Skills `react-patterns`, `react-performance`, `react-testing`, `frontend-patterns`, `frontend-a11y`, and the `react-build-resolver` agent. Depends on `daedalus-frontend`. |
| `daedalus-nextjs` | Skill `nextjs-turbopack`. Depends on `daedalus-react`. |
| `ponytail` | Third-party [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), pinned to a reviewed commit (5.3.3): simplest working solution. |
| `caveman` | Third-party [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman), pinned to a reviewed commit (4.1.0): terse replies. |

Plugins extend each other through dependencies: enabling `daedalus-springboot` also installs `daedalus-java` and `daedalus-core`. A Spring Boot project only needs `"daedalus-springboot@daedalus": true` in `enabledPlugins`. Likewise, `daedalus-nextjs` pulls `daedalus-react`, `daedalus-frontend`, `daedalus-typescript`, and `daedalus-core`, and `daedalus-fastapi` pulls `daedalus-python`.

Every plugin is named `daedalus-<name>`, so its skills and agents stay recognizable next to other plugins: `/daedalus-<name>:<skill>`.

## Install

Claude Code installs a dependency only from a marketplace you have already added. If a dependency's marketplace is missing, `daedalus-core` installs but fails to load. Add both marketplaces.

### For a project team

Commit this to the project's `.claude/settings.json`. Teammates are offered the plugins when they trust the repository.

```json
{
  "extraKnownMarketplaces": {
    "daedalus": { "source": { "source": "github", "repo": "opencacap/daedalus" } },
    "claude-plugins-official": { "source": { "source": "github", "repo": "anthropics/claude-plugins-official" } }
  },
  "enabledPlugins": {
    "daedalus-core@daedalus": true
  }
}
```

### For yourself

```text
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add opencacap/daedalus
/plugin install daedalus-core@daedalus
```

### Codex

Codex reads this marketplace's `.claude-plugin/` manifests, skills, and hooks as they are, but it ignores `dependencies`. Install every plugin yourself:

```text
codex plugin marketplace add anthropics/claude-plugins-official
codex plugin marketplace add opencacap/daedalus
codex plugin add daedalus-core@daedalus
codex plugin add caveman@daedalus
codex plugin add ponytail@daedalus
codex plugin add mattpocock-skills@claude-plugins-official
```

A stack plugin needs its whole chain: `daedalus-springboot` also needs `daedalus-java@daedalus`; `daedalus-fastapi` needs `daedalus-python@daedalus`; `daedalus-nextjs` needs `daedalus-react@daedalus`, `daedalus-frontend@daedalus`, and `daedalus-typescript@daedalus`; and `daedalus-infra` also needs `aws-core@claude-plugins-official` and `terraform@claude-plugins-official`.

Then run `/hooks` in Codex and trust the `daedalus-core`, `caveman`, and `ponytail` hooks. Codex skips untrusted plugin hooks, so the rules do not load until you do, and it asks again after every plugin update.

Codex plugins cannot ship agents, so `java-build-resolver` and `react-build-resolver` are Claude Code only.

If you installed caveman with its own installer (an entry in `~/.codex/hooks.json`) or `ponytail@ponytail`, remove them; otherwise their hooks run twice.

### Turning caveman off

A dependency cannot be disabled while `daedalus-core` is enabled. To keep normal replies, set caveman's default mode instead: `{"defaultMode": "off"}` in `~/.config/caveman/config.json`, or `CAVEMAN_DEFAULT_MODE=off`.

If you installed `caveman@caveman` or `ponytail@ponytail` from their own marketplaces before, uninstall them; otherwise their hooks run twice.

## Code review

`/daedalus-core:code-review` reviews a branch and reports; it never edits files, posts comments, or merges. Read-only sub-agents look for defects through separate lenses: correctness (two passes), security, error handling, standards, spec, tests, types, comments, and stack (the `*-patterns` and `*-coding-standards` skills of the installed `daedalus-*` stack plugins). A fresh sub-agent re-derives each finding from the code. The report ranks confirmed findings C/H/M/L, gives a blocking verdict, and lists the lenses that ran, the lenses that were skipped and why, and any gap in scope.

```text
/daedalus-core:code-review                  # the merge-base with the default branch to HEAD
/daedalus-core:code-review develop          # the merge-base with develop to HEAD
/daedalus-core:code-review --uncommitted    # also staged, unstaged, and untracked changes
/daedalus-core:code-review --spec #12       # the spec: a file path, an issue, or none
```

Without `--spec`, the review takes the spec from issue references in the commit messages, then from the review config, then from a file in `docs/`, `specs/`, `spec/`, or `.scratch/` named after the branch. If it finds none, it asks you.

### Review config

A project can tune the review with an optional Markdown file, usually `docs/agents/code-review.md`, which the agent-skills section of its `AGENTS.md` or `CLAUDE.md` points to. It lists spec sources and how to read their latest version, check commands (lint, type check, tests) whose results the finders and verifiers use as evidence, lenses to turn off, and findings not to report. The review reads the config from the base branch, so a branch cannot turn off its own review. Allow the check commands in the project's permissions, or the report marks them as not run. See [the config format](plugins/daedalus-core/skills/code-review/references/review-config.md).

### Codex

The skill is plain Markdown plus sub-agents, so Codex can run it the same way with its `multi_agent` feature, which is on by default. The eval suite runs in Claude Code only, so Codex support is untested.

The eval suite and how to run it are in [`plugins/daedalus-core/evals/`](plugins/daedalus-core/evals/README.md).

## Writing

Updating core gives every project the shared editing rule. Install the writing plugin once for the four on-demand skills. In Claude Code, run `/plugin install daedalus-writing@daedalus` or add `"daedalus-writing@daedalus": true` to the project's `enabledPlugins`. In Codex, install core as described above and run `codex plugin add daedalus-writing@daedalus`. The writing plugin has no hooks. Use existing project instructions for a client glossary, required language, or preferred register.

Choose the skill by the language of the deliverable. For example, use `/daedalus-writing:clarity review proposal.md` in Claude Code for feedback on an English proposal. For Japanese, use `natural-japanese` for the proposal and `slop-nuki` for the email that accompanies it. Both `vietnamizer` and `slop-nuki` use Markdown alone. Clarity's lint mode uses Python 3. Japanese document lint uses `uv` with SudachiPy and its dictionary, with a bundled manual checklist when `uv` is unavailable.

## Third-party plugins

`caveman` and `ponytail` run hook scripts on every session, so teammates must never receive an unreviewed upstream change. This marketplace lists them with a `url` source pinned to a commit `sha`, and `daedalus-core` depends on these pinned entries instead of the upstream marketplaces.

To update one:

1. Read the upstream diff from the pinned `sha`, focusing on `hooks/`, the hook manifests, and any network, process, or file-write calls.
2. Set the new `sha` in `.claude-plugin/marketplace.json`.
3. Installs pick it up with `claude plugin marketplace update daedalus` followed by `claude plugin update <plugin>@daedalus`. Codex upgrades Git marketplaces when it starts (or run `codex plugin marketplace upgrade daedalus`), then asks to trust the changed hooks in `/hooks`.

## Names

| Where | Form | Example |
|---|---|---|
| Add the marketplace | `<owner>/<repo>` | `opencacap/daedalus` |
| Install or enable a plugin | `<plugin>@<marketplace>` | `daedalus-core@daedalus` |
| Invoke a skill | `/<plugin>:<skill>` | `/mattpocock-skills:to-spec` |

## Rules

`daedalus-core` prints every `rules/*.md` file from a `SessionStart` hook, so the rules reach the model as session context. Claude Code plugins cannot ship `CLAUDE.md` or `.claude/rules/` files, so a hook is the only way to load always-on instructions.

- A project's own `CLAUDE.md`, `AGENTS.md`, and documented standards override these rules.
- Keep rules technology-agnostic. Stack-specific rules belong in a separate `daedalus-<stack>` plugin, so each project enables only what it uses.
- Every line is loaded into every session, so keep the files short.
- Codex truncates hook output above about 2,500 tokens, so keep all `rules/*.md` files together under that.
- The hook uses `cat`, so it requires a POSIX shell (macOS, Linux, or WSL).

## Adding a plugin

1. Create `plugins/daedalus-<name>/.claude-plugin/plugin.json`.
2. Add an entry to `.claude-plugin/marketplace.json`.
3. Run `claude plugin validate --strict .` and `claude plugin validate --strict plugins/daedalus-<name>`.

## License

MIT. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
