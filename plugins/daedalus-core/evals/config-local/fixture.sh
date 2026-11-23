#!/usr/bin/env bash
# The review config is a local file: .claude/ is git-ignored, the agent-skills
# section in .claude/rules/ points to the config, and the config turns the
# error-handling lens off. The feature branch adds a correct mean().
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir -p src .claude/rules .claude/agent-config
printf '.claude/\n' > .gitignore
cat > .claude/rules/agent-skills.md <<'MD'
# Agent skills

## Code review

Review config for `daedalus-core:code-review`. See `.claude/agent-config/code-review.md`.
MD
cat > .claude/agent-config/code-review.md <<'MD'
# Code review

## Lenses

- `error-handling`: off. The platform team reviews error handling.
MD
cat > src/stats.py <<'PY'
"""Small statistics helpers."""


def total(values):
    """Return the sum of values."""
    return sum(values)
PY
git add -A
git commit -qm "Add total"
git switch -qc feature
cat >> src/stats.py <<'PY'


def mean(values):
    """Return the arithmetic mean of values, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return total(values) / len(values)
PY
git commit -qam "Add mean"
