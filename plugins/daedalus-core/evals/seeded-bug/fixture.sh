#!/usr/bin/env bash
# The feature branch adds mean(), which divides by len(values) - 1 (src/stats.py:13).
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
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
    return total(values) / (len(values) - 1)
PY
git commit -qam "Add mean"
