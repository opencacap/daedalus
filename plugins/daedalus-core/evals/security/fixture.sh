#!/usr/bin/env bash
# The feature branch builds an SQL query from a request parameter (src/users.py:7).
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > src/users.py <<'PY'
"""User lookups."""
import sqlite3
PY
git add -A
git commit -qm "Add users module"
git switch -qc feature
cat >> src/users.py <<'PY'


def find_user_by_name(conn: sqlite3.Connection, name):
    """Return the (id, name, email) row of the user called name, or None."""
    cursor = conn.execute(f"SELECT id, name, email FROM users WHERE name = '{name}'")
    return cursor.fetchone()


def lookup_handler(conn, query_params):
    """Handle GET /users?name=<name>; query_params holds the parsed URL query of the request."""
    return find_user_by_name(conn, query_params["name"])
PY
git commit -qam "Add user lookup by name"
