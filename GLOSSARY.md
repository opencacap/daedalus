# Daedalus

Daedalus is a plugin marketplace that gives every team the same engineering rules and skills in Claude Code and Codex.

## Language

**Shared rules**:
The always-loaded engineering rules that `daedalus-core` puts into every session of every project that installs it.
_Avoid_: core rules, daedalus rules, baseline

**Repo standards**:
A project's own documented conventions, such as its `CLAUDE.md`, `AGENTS.md`, coding standards, contributing guide, and ADRs. They win over the shared rules.
_Avoid_: project standards, project docs, documented standards

**Review config**:
A project's optional settings for code review: where specs live, which checks to run, which lenses are off, and which findings not to report.
_Avoid_: review policy, review settings
