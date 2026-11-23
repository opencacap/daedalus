#!/usr/bin/env bash
# docs/specs/discount-codes.md matches the branch feature/discount-codes. The diff
# returns the full total for an unknown code instead of raising ValueError
# (src/discounts.py:8) and never adds describe_discount().
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir -p src docs/specs
cat > docs/specs/discount-codes.md <<'MD'
# Discount codes

Checkout accepts discount codes.

## Requirements

1. `apply_discount(total_cents, code)` in `src/discounts.py` returns `total_cents` after the discount for `code`, in integer cents.
2. The code `SAVE10` takes 10% off the total.
3. An unknown code raises `ValueError`.
4. `describe_discount(code)` returns a label for the code, such as `10% off` for `SAVE10`.
MD
cat > src/discounts.py <<'PY'
"""Discount codes."""
PY
git add -A
git commit -qm "Add discount codes spec"
git switch -qc feature/discount-codes
cat >> src/discounts.py <<'PY'

DISCOUNTS = {"SAVE10": 10}


def apply_discount(total_cents, code):
    """Return total_cents after the discount for code."""
    percent = DISCOUNTS.get(code, 0)
    return total_cents - total_cents * percent // 100
PY
git commit -qam "Add apply_discount"
