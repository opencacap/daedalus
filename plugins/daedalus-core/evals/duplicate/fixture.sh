#!/usr/bin/env bash
# The feature branch adds is_expired() with an inverted comparison (src/tokens.py:9).
# The bug is plain enough that both correctness passes find it.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > src/tokens.py <<'PY'
"""Access token helpers."""
import time
PY
git add -A
git commit -qm "Add tokens module"
git switch -qc feature
cat >> src/tokens.py <<'PY'


def is_expired(expires_at, current=None):
    """Return True when a token that expires at `expires_at` (Unix seconds) has expired."""
    if current is None:
        current = time.time()
    return current < expires_at
PY
git commit -qam "Add is_expired"
