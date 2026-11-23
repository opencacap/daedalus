#!/usr/bin/env bash
# Run the daedalus-core eval suite. Arguments go to `claude plugin eval`.
#
# `claude plugin eval` loads the plugin into an isolated home where its marketplace
# dependencies are not installed, so daedalus-core itself would not load. This script
# evaluates a temporary copy without the `dependencies` field and keeps the results here.
#
# The `stack` case also loads daedalus-python. A case can load only plugins under the
# plugin being evaluated, so this script copies daedalus-python into that case directory.
#
# With `--workflow` as the first argument, every case runs the review with `--workflow`.
# Each run's trace is copied next to the results, so `score.py` can read the reports later.
set -euo pipefail

workflow=false
if [ "${1:-}" = --workflow ]; then
  workflow=true
  shift
fi

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

if $workflow; then
  # The prompt gains --workflow and the Workflow tool. Workflow agents are not Agent tool
  # calls, so a grader that requires Agent calls requires one Workflow call instead.
  python3 - "$tmp/daedalus-core/evals" <<'PY'
import re, sys
from pathlib import Path

for case in Path(sys.argv[1]).glob("*/case.yaml"):
    text = case.read_text()
    text = re.sub(r"^(\s+prompt: /daedalus-core:code-review)\b", r"\1 --workflow", text, flags=re.M)
    text = re.sub(r"^(\s+allowed_tools: \[.*)\]$", r"\1, Workflow]", text, flags=re.M)
    text = re.sub(r"tool: Agent\n(\s+)min: [1-9]\d*", r"tool: Workflow\n\1min: 1", text)
    case.write_text(text)
PY
fi

out="$evals_dir/results/$(date -u +%Y-%m-%dT%H-%M-%SZ)"
status=0
claude plugin eval "$tmp/daedalus-core" --keep-temp --output-dir "$out" "$@" || status=$?

# --keep-temp keeps each run's trace in a temporary directory; copy them next to the results.
python3 - "$out" <<'PY'
import json, shutil, sys
from pathlib import Path

out = Path(sys.argv[1])
result = out / "aggregate-result.json"
if result.is_file():
    data = json.loads(result.read_text())
    (out / "traces").mkdir(exist_ok=True)
    for case in data["cases"]:
        for arm, runs in case["arms"].items():
            for index, run in enumerate(runs):
                trace = Path(run.get("tracePath") or "")
                if trace.is_file():
                    copy = f"traces/{case['name']}-{arm}-{index}.jsonl"
                    shutil.copyfile(trace, out / copy)
                    run["tracePath"] = copy
    result.write_text(json.dumps(data, indent=2))
PY
exit "$status"
