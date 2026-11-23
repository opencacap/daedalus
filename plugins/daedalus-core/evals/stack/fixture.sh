#!/usr/bin/env bash
# The feature branch adds add_tag() with a mutable default argument (src/tags.py:4),
# an anti-pattern that daedalus-python:python-patterns names.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir src
cat > src/tags.py <<'PY'
"""Tag helpers."""
PY
git add -A
git commit -qm "Add tags module"
git switch -qc feature
cat >> src/tags.py <<'PY'


def add_tag(tag, tags=[]):
    """Return tags with tag appended. Without tags, start a new list."""
    tags.append(tag)
    return tags
PY
git commit -qam "Add add_tag"
