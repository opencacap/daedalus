#!/usr/bin/env bash
# The feature branch adds find_user(), whose docstring promises a KeyError
# (src/directory.py:5), but the function returns None, and its caller relies on None.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > src/directory.py <<'PY'
"""User directory helpers."""
PY
git add -A
git commit -qm "Add directory module"
git switch -qc feature
cat >> src/directory.py <<'PY'


def find_user(users, user_id):
    """Return the user whose id is user_id. Raise KeyError when no user has that id."""
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def display_name(users, user_id):
    """Return the user's name, or "unknown" when there is no such user."""
    user = find_user(users, user_id)
    if user is None:
        return "unknown"
    return user["name"]
PY
git commit -qam "Add find_user and display_name"
