# Review config

An optional Markdown file that tunes `daedalus-core:code-review` for one repository. Without it, the review runs on its defaults.

## Where it lives

Put it next to the issue tracker doc, usually at `docs/agents/code-review.md`, and point to it from the agent-skills section of the root `AGENTS.md` or `CLAUDE.md`:

```markdown
### Code review

Review config for `daedalus-core:code-review`. See `docs/agents/code-review.md`.
```

The review reads the config as it is at the merge-base, so a branch cannot turn off its own review or hide its own findings. Merge a config change before a review uses it.

## Sections

Every section is optional. A missing section keeps its default.

- **`## Spec sources`**: where this repo's specs live and how to read their latest version, one bullet per source. The review uses them after a `--spec` argument and issue references in commit messages, and before it searches `docs/`, `specs/`, `spec/`, and `.scratch/`.
- **`## Checks`**: deterministic commands such as lint, type check, and tests, one per bullet, in backticks. The review runs each from the repository root, exactly as written, and gives the results to finders and verifiers as evidence. The host must allow each command: in Claude Code, add a permission rule such as `Bash(npm test)`. A refused or timed-out check is reported as not run.
- **`## Lenses`**: lenses to turn off, one per bullet: `` `<lens id>`: off``, with the reason. Lens ids: `correctness-a`, `correctness-b`, `security`, `error-handling`, `standards`, `spec`, `tests`, `types`, `comments`, `stack`. The summary names each one with `disabled by config`.
- **`## Do not report`**: findings the team has dismissed, one per bullet: where it is and what it says, and why. The review drops a finding that matches an entry and counts it as suppressed.

## Example

```markdown
# Code review

## Spec sources

- Feature specs live in `product/requirements/<feature>.md`, named after the branch without its `feature/` prefix. Read the latest version from `main`: `git show main:product/requirements/<feature>.md`.

## Checks

- `npm run lint`
- `npm test`

## Lenses

- `comments`: off. Generated API docs carry most comments.

## Do not report

- `fetchOrders()` in `src/api/orders.ts` does not retry. The gateway retries; see ADR-0004.
```
