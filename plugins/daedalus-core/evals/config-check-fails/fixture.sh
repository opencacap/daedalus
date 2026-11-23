#!/usr/bin/env bash
# The review config lists a unittest check. The feature branch adds mean(), which
# divides by len(values) - 1 (src/stats.py:13), and a test that fails on it.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir -p src tests docs/agents
cat > AGENTS.md <<'MD'
# Agent instructions

## Agent skills

### Code review

Review config for `daedalus-core:code-review`. See `docs/agents/code-review.md`.
MD
cat > docs/agents/code-review.md <<'MD'
# Code review

## Checks

- `python3 -B -m unittest discover -s tests -t .`
MD
cat > src/__init__.py <<'PY'
PY
cat > src/stats.py <<'PY'
"""Small statistics helpers."""


def total(values):
    """Return the sum of values."""
    return sum(values)
PY
cat > tests/__init__.py <<'PY'
PY
cat > tests/test_stats.py <<'PY'
import unittest

from src.stats import total


class TotalTest(unittest.TestCase):
    def test_adds_values(self):
        self.assertEqual(total([1, 2, 3]), 6)
PY
git add -A
git commit -qm "Add total with tests and the review config"
git switch -qc feature
cat >> src/stats.py <<'PY'


def mean(values):
    """Return the arithmetic mean of values, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return total(values) / (len(values) - 1)
PY
cat >> tests/test_stats.py <<'PY'


class MeanTest(unittest.TestCase):
    def test_mean_of_two_values(self):
        self.assertEqual(mean([2, 4]), 3)
PY
sed -i.bak 's/^from src.stats import total$/from src.stats import mean, total/' tests/test_stats.py
rm tests/test_stats.py.bak
git commit -qam "Add mean with a test"
