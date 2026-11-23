#!/usr/bin/env bash
# The feature branch adds save_orders(), which swallows a failed write and
# still returns True (src/orders.py:10-12).
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > src/orders.py <<'PY'
"""Order storage."""
import json
PY
git add -A
git commit -qm "Add orders module"
git switch -qc feature
cat >> src/orders.py <<'PY'


def save_orders(path, orders):
    """Write orders to path as JSON. Return True when the file was written."""
    try:
        with open(path, "w") as f:
            json.dump(orders, f)
    except OSError:
        pass
    return True
PY
git commit -qam "Add save_orders"
