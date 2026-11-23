#!/usr/bin/env bash
# main already has percent_of() with inverted operands (src/money.py:11).
# The feature branch adds a correct to_dollars() to the same file.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > src/money.py <<'PY'
"""Money helpers. Amounts are integer cents."""


def to_cents(dollars):
    """Convert a dollar amount to integer cents."""
    return round(dollars * 100)


def percent_of(part, whole):
    """Return part as a percentage of whole."""
    return whole / part * 100
PY
git add -A
git commit -qm "Add money helpers"
git switch -qc feature
cat >> src/money.py <<'PY'


def to_dollars(cents):
    """Convert integer cents to a dollar amount."""
    return cents / 100
PY
git commit -qam "Add to_dollars"
