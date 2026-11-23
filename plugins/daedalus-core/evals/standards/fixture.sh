#!/usr/bin/env bash
# CODING_STANDARDS.md forbids reading the clock in domain code. The feature branch
# calls datetime.now() in is_overdue() (src/invoices.py:7) and adds a Middle Man
# (overdue_invoices delegates to _select_overdue).
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > CODING_STANDARDS.md <<'MD'
# Coding standards

## Time

Domain code under `src/` never reads the clock. A function that needs the current time takes it as a `now` parameter, and the caller at the edge of the program passes `datetime.now(timezone.utc)`. Tests pass a fixed `now`; a clock call inside domain code makes their result depend on the day they run.
MD
cat > src/invoices.py <<'PY'
"""Invoice helpers."""
from datetime import datetime
PY
git add -A
git commit -qm "Add invoices module and coding standards"
git switch -qc feature
cat >> src/invoices.py <<'PY'


def is_overdue(invoice):
    """Return True when the invoice is past its due date."""
    return datetime.now() > invoice.due_at


def overdue_invoices(invoices):
    """Return the overdue invoices."""
    return _select_overdue(invoices)


def _select_overdue(invoices):
    """Return the invoices that are past their due date."""
    return [invoice for invoice in invoices if is_overdue(invoice)]
PY
git commit -qam "Add overdue invoice helpers"
