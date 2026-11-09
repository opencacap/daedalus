# daedalus

A Claude Code plugin marketplace for shared engineering rules and workflow plugins.

## Plugins

| Plugin | What it does |
|---|---|
| `daedalus-core` | Loads the shared engineering rules in [`plugins/daedalus-core/rules/`](plugins/daedalus-core/rules/) at every session start. Depends on [`mattpocock-skills`](https://github.com/mattpocock/skills) (engineering workflow), [`ponytail`](https://github.com/DietrichGebert/ponytail) (simplicity), and [`caveman`](https://github.com/JuliusBrussee/caveman) (terse replies). |
| `daedalus-java` | Skill `java-coding-standards`: framework-agnostic Java standards. Depends on `daedalus-core`. |
| `daedalus-springboot` | Skills `spring-coding-standards`, `springboot-patterns`, `springboot-security`, `springboot-verification`, `jpa-patterns`, `postgres-patterns`, and the `java-build-resolver` agent. Depends on `daedalus-java`. |

Plugins extend each other through dependencies: enabling `daedalus-springboot` also installs `daedalus-java` and `daedalus-core`. A Spring Boot project only needs `"daedalus-springboot@daedalus": true` in `enabledPlugins`.

Every plugin is named `daedalus-<name>`, so its skills and agents stay recognizable next to other plugins: `/daedalus-<name>:<skill>`.

## Install

Claude Code installs a dependency only from a marketplace you have already added. If a dependency's marketplace is missing, `daedalus-core` installs but fails to load. Add all four marketplaces.

### For a project team

Commit this to the project's `.claude/settings.json`. Teammates are offered the plugins when they trust the repository.

```json
{
  "extraKnownMarketplaces": {
    "daedalus": { "source": { "source": "github", "repo": "opencacap/daedalus" } },
    "claude-plugins-official": { "source": { "source": "github", "repo": "anthropics/claude-plugins-official" } },
    "caveman": { "source": { "source": "github", "repo": "JuliusBrussee/caveman" } },
    "ponytail": { "source": { "source": "github", "repo": "DietrichGebert/ponytail" } }
  },
  "enabledPlugins": {
    "daedalus-core@daedalus": true
  }
}
```

### For yourself

```text
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add JuliusBrussee/caveman
/plugin marketplace add DietrichGebert/ponytail
/plugin marketplace add opencacap/daedalus
/plugin install daedalus-core@daedalus
```

### Turning caveman off

A dependency cannot be disabled while `daedalus-core` is enabled. To keep normal replies, set caveman's default mode instead: `{"defaultMode": "off"}` in `~/.config/caveman/config.json`, or `CAVEMAN_DEFAULT_MODE=off`.

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
