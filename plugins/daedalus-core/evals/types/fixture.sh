#!/usr/bin/env bash
# The feature branch adds Cell, documented as hashable, with a plain @dataclass
# (src/grid.py:5-6). A non-frozen dataclass with eq=True sets __hash__ to None,
# so visited_cells() raises TypeError.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > src/grid.py <<'PY'
"""Grid helpers."""
from dataclasses import dataclass
PY
git add -A
git commit -qm "Add grid module"
git switch -qc feature
cat >> src/grid.py <<'PY'


@dataclass
class Cell:
    """A grid cell. Cells are immutable and hashable, so they work as set members and dict keys."""

    row: int
    col: int


def visited_cells(path):
    """Return the set of distinct cells on path, a list of Cell."""
    return set(path)
PY
git commit -qam "Add Cell and visited_cells"
