---
name: code-review
description: Find-then-verify review of a branch's changes. Independent read-only sub-agents look for defects, a fresh sub-agent re-derives each finding from the code, and the report ranks confirmed findings C/H/M/L with a blocking verdict. Use when asked to review a branch, a diff, or work in progress, or before merging.
argument-hint: "[base-ref] [--uncommitted]"
---

# Code review

You are the orchestrator. Run inline: resolve the scope, gather context, start finder and verifier sub-agents, and write the report. Never edit files.

`REFS` below is `${CLAUDE_SKILL_DIR}/references`. If your host does not expand `${CLAUDE_SKILL_DIR}`, use the `references/` directory next to this file. `RULES` is the plugin's `rules/` directory, two levels above this skill's directory. Give sub-agents absolute paths.

## 1. Arguments

Arguments: `$ARGUMENTS`

- `--uncommitted`: also review staged, unstaged, and untracked changes.
- Any other argument is the base ref: a commit, branch, or tag.

## 2. Scope

Use only `git` commands, one per call, with no pipes, `&&`, or redirection: the review must work where only `git` is allowed. Start no sub-agent until the scope is valid. A stop message is the whole reply.

1. **Base.**
   - Named base: `git rev-parse --verify --quiet "<base>^{commit}"`. If it fails, stop with `Review stopped: base ref '<base>' does not resolve to a commit.`
   - No base: try `git symbolic-ref --quiet --short refs/remotes/origin/HEAD`, then the first of `main`, `master`, `origin/main`, `origin/master` that `git rev-parse --verify --quiet "<name>^{commit}"` resolves. If none resolves, stop with `Review stopped: no default branch found. Name a base ref.`
2. **Merge-base.** `git merge-base <base> HEAD`. If it fails, stop with `Review stopped: '<base>' and HEAD share no history.`
3. **Changed files.**
   - Default: `git diff --name-status <merge-base> HEAD`.
   - With `--uncommitted`: `git diff --name-status <merge-base>` (index and working tree against the merge-base), plus `git ls-files --others --exclude-standard` for untracked files.
   - If nothing is listed, stop with `Review stopped: no changes between '<base>' and HEAD.` With `--uncommitted`, end it with `HEAD or in the working tree.` instead.
4. **Working tree.** Run `git status --porcelain`. If it lists anything and `--uncommitted` is off, record the scope gap `uncommitted changes not reviewed (<n> paths; rerun with --uncommitted)`.

Record for the sub-agent prompts:

- `DIFF`: `git diff <merge-base> HEAD`, or `git diff <merge-base>` with `--uncommitted`.
- `UNTRACKED`: the untracked files under review, or `none`.
- `READ`: `working tree` when the tree is clean or `--uncommitted` is on. Otherwise `HEAD`: sub-agents read file contents with `git show HEAD:<path>`, because the working tree holds changes outside this review, and they give line numbers from HEAD.

## 3. Context

Collect the paths that exist (use file search; do not read them yourself):

- `CLAUDE.md` and `AGENTS.md` at the repo root and in every directory that holds a changed file.
- `.claude/rules/**/*.md`, `CODING_STANDARDS.md`, `CONTRIBUTING.md`.
- ADRs: `**/adr/**/*.md` and `**/decisions/**/*.md`.

Call this list `STANDARDS`. Sub-agents get the paths, not the contents, and so do the shared rules in `RULES`.

## 4. Find

Lenses in this version:

| Lens id | Brief | Strategy |
| --- | --- | --- |
| `correctness-a` | `REFS/lenses/correctness.md` | A |
| `correctness-b` | `REFS/lenses/correctness.md` | B |

Not available in this version, so always skipped with the reason `not available in this version`: `security`, `error-handling`, `standards`, `spec`, `tests`, `types`, `comments`, `stack`.

Start every finder in **one message** so they run in parallel. Each is a fresh general-purpose sub-agent (in Codex, a fresh sub-agent). Use this prompt, filled in:

```text
You are the <lens id> finder in a code review. Read files with your file-reading tool, not the shell. Shell access may be limited to git: run each git command on its own, with no cd, pipes, &&, ;, or redirection.

Read these files and follow them exactly:
- REFS/finder.md
- REFS/lenses/<lens>.md (use strategy <A|B>)
- REFS/finding-schema.md
- REFS/severity.md
- REFS/suppression.md

Scope: base <base> (merge-base <sha>).
Diff: run `<DIFF>`.
Untracked files under review (read them in full): <UNTRACKED>.
Read file contents from: <READ>.
Repo standards: <STANDARDS, or none>.
Shared rules: every file in RULES.
```

A finder that fails or returns neither findings nor `NO ISSUES` is a scope gap: record `<lens id> returned no result`.

## 5. Normalize

1. Parse every `FINDING` block. Drop a block that lacks `file`, `line`, `claim`, or `failure`, and count it as suppressed.
2. Drop findings in a suppressed category (`REFS/suppression.md`), and count them.
3. Merge duplicates: same file, overlapping or adjacent lines, and the same root cause. The merged finding keeps the highest severity, lists every lens that reported it, and keeps the clearest title, claim, failure, and fix.

## 6. Verify

Skip this step when no finding is left. Otherwise start one fresh general-purpose verifier per finding, all in **one message**. The verifier gets the claim and the location, never the finder's failure scenario, fix, severity, or reasoning:

```text
Read files with your file-reading tool, not the shell. Shell access may be limited to git: run each git command on its own, with no cd, pipes, &&, ;, or redirection.

Read REFS/verifier.md and follow it exactly.

Claim: <claim>
Location: <file>:<line>
Code at that location: <code>

Scope: base <base> (merge-base <sha>). Diff: run `<DIFF>`.
Untracked files under review: <UNTRACKED>.
Read file contents from: <READ>.
Repo standards: <STANDARDS, or none>.
Shared rules: every file in RULES.
```

Apply each verdict:

- `CONFIRMED`: report it. Take its origin from the verifier's `ORIGIN` line.
- `REFUTED`: drop it and count it.
- `UNCERTAIN` at C or H: report it under "Needs a human".
- `UNCERTAIN` at M or L: drop it and count it.
- No verdict line, or the verifier failed: treat it as `UNCERTAIN`.

## 7. Report

Read `REFS/report-template.md` and write the report exactly in that form. It is the whole reply: no preamble, and no offer to fix.
