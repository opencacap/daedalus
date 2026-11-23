<!-- Partly adapted from affaan-m/everything-claude-code, agents/comment-analyzer.md (MIT). Changed: rewritten as a defect-only finder brief limited to comments that state something false, with severity guidance. See THIRD_PARTY_NOTICES.md. -->

# Comments lens

Find comments and docstrings in the diff that state something false about the code: a reader who trusts them will use the code wrongly.

## Look for

- **Contradictions.** A comment or docstring that says the code does something it does not: a different return value, an exception it never raises, a side effect it does not have, a unit or range the code does not use.
- **Wrong contracts.** Parameter, return, or error descriptions that do not match the signature or the implementation.
- **Stale comments.** A comment the diff left behind when it changed the code it describes, or a reference to a function, field, flag, or behavior that no longer exists.
- **False guarantees.** A comment that promises thread safety, ordering, idempotency, or validation that the code does not provide.

Check every claim against the code, its callers, and its tests. When the comment and the code disagree, decide which one the callers and tests follow; the defect is in the other one. Point `file` and `line` at the comment when the comment is wrong.

## Do not report

- Wording, grammar, tone, or length of a comment that is true.
- Missing comments or docstrings.
- Comments that restate the code but are true.
- `TODO`, `FIXME`, and `HACK` markers, unless the comment says the work is done.

## Severity

- **M:** a false docstring or comment on a public function, API, or type that callers rely on.
- **L:** a false comment inside a function, or on private code with few users.
- Report a contradiction at H only when the code, not the comment, is wrong and that wrong behavior meets the H grade.
