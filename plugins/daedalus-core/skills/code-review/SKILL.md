---
name: code-review
description: Find-then-verify review of a branch's changes. Independent read-only sub-agents look for defects, a fresh sub-agent re-derives each finding from the code, and the report ranks confirmed findings C/H/M/L with a blocking verdict. Use when asked to review a branch, a diff, or work in progress, or before merging.
argument-hint: "[base-ref] [--uncommitted] [--spec <path | issue | none>]"
---

# Code review

You are the orchestrator. Run inline: resolve the scope, gather context, start finder and verifier sub-agents, and write the report. Never edit files.

`REFS` below is `${CLAUDE_SKILL_DIR}/references`. If your host does not expand `${CLAUDE_SKILL_DIR}`, use the `references/` directory next to this file. `RULES` is the plugin's `rules/` directory, two levels above this skill's directory. `CHECKLIST` is `security-review/SKILL.md`, a sibling of this skill's directory. Give sub-agents absolute paths.

## 1. Arguments

Arguments: `$ARGUMENTS`

- `--uncommitted`: also review staged, unstaged, and untracked changes.
- `--spec <value>`: the spec for this change: a file path, an issue reference such as `#12`, or `none` when there is no spec.
- Any other argument is the base ref: a commit, branch, or tag.

## 2. Scope

Use only `git` commands, one per call, with no pipes, `&&`, or redirection: the review must work where only `git` is allowed. Start no sub-agent until the scope is valid. A stop message is the whole reply.

1. **Base.**
   - Named base: `git rev-parse --verify --quiet "<base>^{commit}"`. If it fails, stop with `Review stopped: base ref '<base>' does not resolve to a commit.`
   - No base: try `git symbolic-ref --quiet --short refs/remotes/origin/HEAD`, then the first of `main`, `master`, `origin/main`, `origin/master` that `git rev-parse --verify --quiet "<name>^{commit}"` resolves. If none resolves, stop with `Review stopped: no default branch found. Name a base ref.`
2. **Merge-base.** `git merge-base <base> HEAD`. If it fails, stop with `Review stopped: '<base>' and HEAD share no history.`
3. **Working tree.** Run `git status --porcelain`. If it lists anything and `--uncommitted` is off, record the scope gap `uncommitted changes not reviewed (<n> paths; rerun with --uncommitted)`.
4. **Changed files.**
   - Default: `git diff --name-status <merge-base> HEAD`.
   - With `--uncommitted`: `git diff --name-status <merge-base>` (index and working tree against the merge-base), plus `git ls-files --others --exclude-standard` for untracked files.
   - If nothing is listed, stop with `Review stopped: no changes between '<base>' and HEAD.` With `--uncommitted`, end it with `HEAD or in the working tree.` instead. If step 3 recorded a scope gap, add `Uncommitted changes were not reviewed; rerun with --uncommitted.`

Record for the sub-agent prompts:

- `DIFF`: `git diff <merge-base> HEAD`, or `git diff <merge-base>` with `--uncommitted`.
- `UNTRACKED`: the untracked files under review, or `none`.
- `READ`: `working tree` when the tree is clean or `--uncommitted` is on. Otherwise `HEAD`: sub-agents read file contents with `git show HEAD:<path>`, because the working tree holds changes outside this review, and they give line numbers from HEAD.

## 3. Context

Collect the paths that exist (use file search; do not read them yourself):

- `CLAUDE.md` and `AGENTS.md` at the repo root and in every directory that holds a changed file.
- `.claude/rules/**/*.md`: list them with `git ls-files --cached --others -- .claude/rules`, which also lists git-ignored files that file search may skip.
- `CODING_STANDARDS.md`, `CONTRIBUTING.md`.
- ADRs: `**/adr/**/*.md` and `**/decisions/**/*.md`.

Call this list `STANDARDS`. Sub-agents get the paths, not the contents, and so do the shared rules in `RULES`.

### Review config

Find the review config: the Markdown file that the repo's agent-skills section names for code review, usually `docs/agents/code-review.md`. That section is in the root `AGENTS.md` or `CLAUDE.md`, a file one of them imports with `@<path>`, or a file under `.claude/rules/`; list the candidates with `git ls-files --cached --others -- AGENTS.md CLAUDE.md .claude/rules`, which includes git-ignored files. Read the files that hold the section, and the config, at the merge-base with `git show <merge-base>:<path>` when git tracks them, never from the working tree: the change under review must not tune its own review. A file that git does not track (`git ls-files -- <path>` lists nothing) is the reviewer's local file: read it from the working tree. Its format is in `REFS/review-config.md`.

- No config: every default below applies.
- Git tracks the config but it is not at the merge-base: use no config, and record the scope gap `review config <path> is not on the base branch; defaults used`.
- The diff changes the config: use the merge-base version, and record the scope gap `this diff changes the review config; the base version was used`.

Record `CONFIG`: its path, or `none`. From its sections, record `CONFIG SPECS`, `CHECK COMMANDS`, `LENSES OFF`, and `DO NOT REPORT`, each `none` when absent.

### Spec

When `LENSES OFF` holds `spec`, skip this step: `SPEC` is `none`. Otherwise find the spec in this order and stop at the first source that gives one:

1. **Argument.** `--spec none` means there is no spec. A path: use that file; if it does not exist, ask as in source 5. An issue reference: read it as in source 2.
2. **Commit messages.** Run `git log --format=%B <merge-base>..HEAD` and collect issue and merge request references (`#12`, `Closes #12`, GitLab `!12`, tracker keys such as `ABC-123`). Find the repo's issue tracker doc: the root `AGENTS.md` or `CLAUDE.md` points to it. Read each referenced issue the way that doc says. Without a tracker doc, skip this source.
3. **Review config.** Follow `CONFIG SPECS` to the spec for this change, and read its latest version the way they say.
4. **Spec file.** Search `docs/`, `specs/`, `spec/`, and `.scratch/` for a Markdown file whose path matches the branch name (`git branch --show-current`, without a prefix such as `feat/`) or the feature the commit messages name.
5. **Ask.** Ask the developer exactly `Where is the spec for this change? Reply with a file path or an issue reference, or "none" if there is no spec.` Use your question tool if you have one; otherwise make the question your whole reply and wait for the answer. Start no sub-agent before the answer.

If the developer answers `none`, there is no spec. Record `SPEC`: the spec's path when the working-tree file is the version to review, otherwise the text you read (an issue, or a file from another ref); `SPEC SOURCE`: the path or the issue reference; or `none`.

### Stack

Read the list of skills available in this session, which your host gives you; do not search the file system for skills. From it, take those of an installed `daedalus-*` plugin other than `daedalus-core` and `daedalus-writing` whose name ends in `-patterns` or `-coding-standards`. Keep the ones whose description matches a language or framework of the changed files. Record their full names (`<plugin>:<skill>`) as `STACK`, or `none`.

### Lens conditions

`RANGE` is `<merge-base> HEAD`, or `<merge-base>` with `--uncommitted`. Run each condition's git command on its own, exactly as written: hosts that allow only `git` refuse a command that contains `$` or a backtick, so the patterns avoid both. With `--uncommitted`, also apply each pattern to the untracked files under review with your file search tool.

- **Code changed:** at least one changed file is source code, not only documentation, prose, data, or images.
- **Test suite:** `git ls-files -- ':(glob)**/test_*' ':(glob)**/*_test.*' ':(glob)**/*.test.*' ':(glob)**/*.spec.*' ':(glob)**/*_spec.*' ':(glob)**/*Test.*' ':(glob)**/*Tests.*' ':(glob)**/*Spec.*' ':(glob)**/__tests__/**' ':(glob)**/tests/**' ':(glob)**/test/**' ':(glob)**/spec/**'` lists at least one file.
- **Type definitions:** this command lists at least one file. It matches added or removed lines that declare a type, a typed field, a member with an access modifier, an enum member, or a Go struct field. It is a cheap filter, so it also matches some lines that are not type definitions.

  ```text
  git diff --name-only -G '^[[:space:]]*((export|public|private|protected|internal|abstract|sealed|final|static|data|declare|default|pub)[[:space:]]+)*(class|interface|type|struct|enum|record|trait|protocol|typedef|union)[[:space:]]+[[:alpha:]_]|^[[:space:]]+(readonly[[:space:]]+)?[[:alpha:]_][[:alnum:]_]*[?]?:[[:space:]]*[[:alpha:]_]|^[[:space:]]+((public|private|protected|internal|readonly|override)[[:space:]]+)+[[:alpha:]_]|^[[:space:]]+[[:upper:]][[:alnum:]_]*[[:space:]]*(,|;|[(]|=[[:space:]]*[^[:space:][:alpha:]_])|^[[:space:]]+[[:upper:]][[:alnum:]_]*[[:space:]]+[][*]*[[:alpha:]][[:alnum:]_.]*' <RANGE> -- . ':(exclude)*.md' ':(exclude)*.mdx' ':(exclude)*.rst' ':(exclude)*.txt' ':(exclude)*.yml' ':(exclude)*.yaml'
  ```

- **Comments:** this command lists at least one file. It matches added or removed lines with a comment marker or a docstring quote.

  ```text
  git diff --name-only -G '(^|[[:space:]])(#|//|--[[:space:]])|/[*]|<!--|^[[:space:]]*[*]|["]{3}' <RANGE> -- . ':(exclude)*.md' ':(exclude)*.mdx' ':(exclude)*.rst' ':(exclude)*.txt'
  ```

### Checks

Run each command in `CHECK COMMANDS` from the repository root, exactly as written, one per call, with your shell tool's longest timeout up to 10 minutes. Apart from these, you run only `git`. Record `CHECK RESULTS`, one entry per command: `PASS`; `FAIL`, followed by the output lines that show the failure (at most 20, quoted); or `NOT RUN (<reason>)` when the host refuses it or it times out, which is also the scope gap `check <command> not run: <reason>`. When `READ` is `HEAD`, add that the checks ran on a working tree with uncommitted changes. With no check commands, `CHECK RESULTS` is `none`.

## 4. Find

A lens in `LENSES OFF` is skipped with the reason `disabled by config`. Every other lens runs when its condition holds. Otherwise it is skipped, and the summary names it with the skip reason from the table.

| Lens id | Brief (in `REFS/lenses/`) | Runs when | Skip reason | Lens input |
| --- | --- | --- | --- | --- |
| `correctness-a` | `correctness.md`, strategy A | always | | none |
| `correctness-b` | `correctness.md`, strategy B | always | | none |
| `security` | `security.md` | always | | `Checklist: <CHECKLIST>` |
| `error-handling` | `error-handling.md` | always | | none |
| `standards` | `standards.md` | always | | none |
| `spec` | `spec.md` | `SPEC` is not `none` | `no spec available` | `Spec (<SPEC SOURCE>): <SPEC>` |
| `tests` | `tests.md` | code changed and the repo has a test suite | `no code changed` or `no test suite` | none |
| `types` | `types.md` | the diff touches type definitions | `no type definitions changed` | none |
| `comments` | `comments.md` | the diff touches comments or docstrings | `no comments changed` | none |
| `stack` | `stack.md` | `STACK` is not `none` | `no matching stack plugin installed` | `Rubric skills: <STACK>` |

Start every lens that runs as its own finder sub-agent, however small the diff or clear the check results; never review the diff yourself. Start every finder in **one message** so they run in parallel. Each is a fresh general-purpose sub-agent (in Codex, a fresh sub-agent). Use this prompt, filled in:

```text
You are the <lens id> finder in a code review. Read files with your file-reading tool, not the shell. Shell access may be limited to git: run each git command on its own, with no cd, pipes, &&, ;, or redirection.

Read these files and follow them exactly:
- REFS/finder.md
- REFS/lenses/<brief> (use strategy <A|B> when the brief has strategies)
- REFS/finding-schema.md
- REFS/severity.md
- REFS/suppression.md

Scope: base <base> (merge-base <sha>).
Diff: run `<DIFF>`.
Untracked files under review (read them in full): <UNTRACKED>.
Read file contents from: <READ>.
Repo standards: <STANDARDS, or none>.
Shared rules: every file in RULES.
Check results (evidence): <CHECK RESULTS, or none>.
Do not report anything on the repo's list: <DO NOT REPORT, or none>.
<lens input, omitted when none>
```

A finder that fails, replies `NO RESULT: <reason>`, or returns neither findings nor `NO ISSUES` is a scope gap: record `<lens id> returned no result`, with the reason when it gave one.

Sub-agents may run in the background. Wait for every result to arrive; never run `sleep` or any other command to wait, and start no background command.

## 5. Normalize

1. Keep the spec lens's `COVERAGE` block for the report. Parse every `FINDING` block. Drop a block that lacks `file`, `line`, `claim`, or `failure`, or whose lens requires a `rule` (see `REFS/finding-schema.md`) and gives `none`, and record the scope gap `<lens id> returned a malformed finding`.
2. Set the severity of every finding whose `rule` starts with `smell:` to L.
3. Drop findings in a category that `REFS/suppression.md` marks for the orchestrator to drop, and findings that match a `DO NOT REPORT` entry (the place it names and the issue it describes). Count them as suppressed. Leave every other finding to the verifier.
4. Merge duplicates: same file, overlapping or adjacent lines, and the same root cause. The merged finding keeps the highest severity, lists every lens that reported it, keeps every cited rule, and keeps the clearest title, claim, failure, and fix.

## 6. Verify

Skip this step when no finding is left. Otherwise start one fresh general-purpose verifier per finding, all in **one message**. The verifier gets the claim, the location, and the cited rule, never the finder's failure scenario, fix, severity, or reasoning:

```text
Read files with your file-reading tool, not the shell. Shell access may be limited to git: run each git command on its own, with no cd, pipes, &&, ;, or redirection.

Read REFS/verifier.md and follow it exactly.

Claim: <claim>
Location: <file>:<line>
Code at that location: <code>
Cited rule: <rule, or none>
Spec (<SPEC SOURCE>): <SPEC; include this line for spec findings only>

Scope: base <base> (merge-base <sha>). Diff: run `<DIFF>`.
Untracked files under review: <UNTRACKED>.
Read file contents from: <READ>.
Repo standards: <STANDARDS, or none>.
Shared rules: every file in RULES.
Check results (evidence): <CHECK RESULTS, or none>.
```

Apply each verdict:

- `CONFIRMED`: report it. Take its origin from the verifier's `ORIGIN` line.
- `REFUTED`: drop it and count it.
- `UNCERTAIN` at C or H: report it under "Needs a human".
- `UNCERTAIN` at M or L: drop it and count it.
- No verdict line, or the verifier failed: treat it as `UNCERTAIN`.

Then update each `partial` or `missing` coverage row from its finding, the one that quotes the same requirement: a reported finding puts its tag in the row's evidence; a refuted one turns the row to `done`, with the verifier's citation as evidence; an uncertain one that was dropped keeps the status, adds `(unverified)`, and keeps the evidence `none`.

## 7. Report

Read `REFS/report-template.md` and write the report exactly in that form, once every finder and verifier has returned. It is the whole reply and your last message: no preamble, and no offer to fix.
