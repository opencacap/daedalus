# Workflow orchestration

Claude Code only. With `--workflow`, the plugin's `code-review-workflow` Workflow runs steps 4 to 7: it starts one finder per lens, normalizes the findings, starts one verifier per finding, and writes the report, over the same reference files. You still run steps 1 to 3 inline, so a scope failure or a question about the spec happens before any agent starts.

## Run it

1. Decide which lenses run and which are skipped, with their skip reasons, from the lens table in step 4. Start no finder yourself.
2. Call your Workflow tool with the name `daedalus-core:code-review-workflow` and the args below, passed as a JSON object, not as a string. If you have no Workflow tool, or the call is refused, stop with `Review stopped: the code-review workflow cannot run here. Rerun without --workflow.`
3. The workflow may run in the background. Wait for it to finish; never run `sleep` or any other command to wait.
4. Its result is the report. Reply with it exactly as returned, as your whole reply and last message: no preamble, no edits, and no offer to fix. Copy it character for character, even where it differs from your own writing style. Tools parse the report, so keep every heading, bold marker, em dash (`—`), and line break, and keep the summary as one paragraph.

## Args

| Field | Value |
| --- | --- |
| `refs` | the absolute path of `REFS` |
| `rules` | the absolute path of `RULES` |
| `checklist` | the absolute path of `CHECKLIST` |
| `base` | the named base ref, or the default branch you found |
| `mergeBase` | the merge-base SHA |
| `diff` | `DIFF` |
| `untracked` | `UNTRACKED` |
| `read` | `READ` |
| `uncommitted` | `true` with `--uncommitted`, otherwise `false` |
| `files` | the number of changed files under review |
| `standards` | `STANDARDS`, as an array of paths |
| `config` | `CONFIG`, as a path relative to the repository root |
| `doNotReport` | `DO NOT REPORT` |
| `checks` | one object per command in `CHECK COMMANDS`: `command`; `status`, which is `PASS`, `FAIL`, or `NOT RUN`; `output`, the quoted failure lines of a `FAIL`; `reason`, why a check did not run. An empty array without check commands. |
| `checksOnDirtyTree` | `true` when checks ran and `READ` is `HEAD`, otherwise `false` |
| `spec` | `{"source": "<SPEC SOURCE>", "text": "<SPEC>"}`, or `null` when `SPEC` is `none` |
| `stack` | `STACK`, or `null` when it is `none` |
| `lenses` | the ids of the lenses that run, in the order of the lens table |
| `skipped` | one `{"id": "<lens id>", "reason": "<skip reason>"}` object per skipped lens, in the order of the lens table |
| `scopeGaps` | the scope gaps recorded so far, as an array of strings |
