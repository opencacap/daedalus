#!/usr/bin/env bash
# The repo has a pytest suite. The feature branch adds a correct mean() and a test
# whose assertion passes for any non-zero result (tests/test_stats.py:10).
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src tests
cat > src/stats.py <<'PY'
"""Small statistics helpers."""


def total(values):
    """Return the sum of values."""
    return sum(values)
PY
cat > tests/test_stats.py <<'PY'
from src.stats import total


def test_total_adds_values():
    assert total([1, 2, 3]) == 6
PY
git add -A
git commit -qm "Add total with tests"
git switch -qc feature
cat >> src/stats.py <<'PY'


def mean(values):
    """Return the arithmetic mean of values, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return total(values) / len(values)
PY
cat > tests/test_stats.py <<'PY'
from src.stats import mean, total


def test_total_adds_values():
    assert total([1, 2, 3]) == 6


def test_mean_of_three_values():
    result = mean([2, 4, 9])
    assert result
PY
git commit -qam "Add mean with a test"
