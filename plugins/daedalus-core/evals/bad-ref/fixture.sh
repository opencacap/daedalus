#!/usr/bin/env bash
# A feature branch with one commit on top of main.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
printf 'def greet(name):\n    return "Hello, " + name\n' > app.py
git add -A
git commit -qm "Add greet"
git switch -qc feature
printf 'def greet(name):\n    return "Hello, " + name + "!"\n' > app.py
git commit -qam "Add exclamation mark"
