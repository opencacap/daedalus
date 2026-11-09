# daedalus

A Claude Code plugin marketplace for shared engineering rules and workflow plugins.

## Plugins

| Plugin | What it does |
|---|---|
| `daedalus-core` | Loads the shared engineering rules in [`plugins/daedalus-core/rules/`](plugins/daedalus-core/rules/) at every session start, and provides the `security-review` skill. Depends on [`mattpocock-skills`](https://github.com/mattpocock/skills) (engineering workflow) and the pinned `ponytail` and `caveman` entries below. |
| `daedalus-java` | Skill `java-coding-standards`: framework-agnostic Java standards. Depends on `daedalus-core`. |
| `daedalus-springboot` | Skills `spring-coding-standards`, `springboot-patterns`, `springboot-security`, `springboot-verification`, `hexagonal-architecture`, `jpa-patterns`, `postgres-patterns`, and the `java-build-resolver` agent. Depends on `daedalus-java`. |
| `daedalus-infra` | Skill `docker-patterns`. Depends on `daedalus-core` and the official [`aws-core`](https://github.com/aws/agent-toolkit-for-aws) and `terraform` (HashiCorp) plugins from `claude-plugins-official`. Their MCP servers need `uvx` plus AWS credentials (`aws-mcp`) and a running Docker daemon (`terraform`); without them the server fails to connect but the skills still work. |
| `ponytail` | Third-party [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), pinned to a reviewed commit (5.3.3): simplest working solution. |
| `caveman` | Third-party [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman), pinned to a reviewed commit: terse replies. |

Plugins extend each other through dependencies: enabling `daedalus-springboot` also installs `daedalus-java` and `daedalus-core`. A Spring Boot project only needs `"daedalus-springboot@daedalus": true` in `enabledPlugins`.

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

### Turning caveman off

A dependency cannot be disabled while `daedalus-core` is enabled. To keep normal replies, set caveman's default mode instead: `{"defaultMode": "off"}` in `~/.config/caveman/config.json`, or `CAVEMAN_DEFAULT_MODE=off`.

If you installed `caveman@caveman` or `ponytail@ponytail` from their own marketplaces before, uninstall them; otherwise their hooks run twice.

## Third-party plugins

`caveman` and `ponytail` run hook scripts on every session, so teammates must never receive an unreviewed upstream change. This marketplace lists them with a `url` source pinned to a commit `sha`, and `daedalus-core` depends on these pinned entries instead of the upstream marketplaces.

To update one:

1. Read the upstream diff from the pinned `sha`, focusing on `hooks/`, the hook manifests, and any network, process, or file-write calls.
2. Set the new `sha` in `.claude-plugin/marketplace.json`.
3. Installs pick it up with `claude plugin marketplace update daedalus` followed by `claude plugin update <plugin>@daedalus`.

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
- The hook uses `cat`, so it requires a POSIX shell (macOS, Linux, or WSL).

## Adding a plugin

1. Create `plugins/daedalus-<name>/.claude-plugin/plugin.json`.
2. Add an entry to `.claude-plugin/marketplace.json`.
3. Run `claude plugin validate --strict .` and `claude plugin validate --strict plugins/daedalus-<name>`.

## License

MIT. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
