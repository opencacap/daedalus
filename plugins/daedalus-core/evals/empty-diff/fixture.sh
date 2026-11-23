#!/usr/bin/env bash
# A clean checkout of main: HEAD is the default branch, so the diff is empty.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
printf 'def greet(name):\n    return "Hello, " + name\n' > app.py
git add -A
git commit -qm "Add greet"
