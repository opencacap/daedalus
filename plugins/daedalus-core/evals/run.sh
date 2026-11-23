#!/usr/bin/env bash
# Run the daedalus-core eval suite. Arguments go to `claude plugin eval`.
#
# `claude plugin eval` loads the plugin into an isolated home where its marketplace
# dependencies are not installed, so daedalus-core itself would not load. This script
# evaluates a temporary copy without the `dependencies` field and keeps the results here.
#
# The `stack` case also loads daedalus-python. A case can load only plugins under the
# plugin being evaluated, so this script copies daedalus-python into that case directory.
set -euo pipefail

evals_dir=$(cd "$(dirname "$0")" && pwd)
plugin_dir=$(dirname "$evals_dir")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

cp -R "$plugin_dir" "$tmp/daedalus-core"
rm -rf "$tmp/daedalus-core/evals/results"
cp -R "$plugin_dir/../daedalus-python" "$tmp/daedalus-core/evals/stack/daedalus-python"
python3 - "$tmp/daedalus-core/.claude-plugin/plugin.json" \
  "$tmp/daedalus-core/evals/stack/daedalus-python/.claude-plugin/plugin.json" <<'PY'
import json, sys

for path in sys.argv[1:]:
    with open(path) as f:
        manifest = json.load(f)
    manifest.pop("dependencies", None)
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
PY

claude plugin eval "$tmp/daedalus-core" \
  --output-dir "$evals_dir/results/$(date -u +%Y-%m-%dT%H-%M-%SZ)" "$@"
