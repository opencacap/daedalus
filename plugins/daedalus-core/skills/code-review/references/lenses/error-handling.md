<!-- Partly adapted from affaan-m/everything-claude-code, agents/silent-failure-hunter.md (MIT). Changed: rewritten as a defect-only finder brief with a failure-scenario requirement and severity guidance. See THIRD_PARTY_NOTICES.md. -->

# Error-handling lens

Find failures that the code hides, loses, or reports as success.

## Look for

- **Swallowed errors.** An empty `catch` or `except`, a handler that only logs and continues where the caller needs to know, or an error turned into `null`, an empty list, `false`, or a default with no signal to the caller.
- **Failure reported as success.** A function that returns success, `true`, `200`, or a normal result after the operation failed or was skipped.
- **Dangerous fallbacks.** A default value or `.catch(() => ...)` that hides a real failure, so that later code works on wrong data.
- **Lost errors.** A rethrow that drops the cause or stack trace, an unawaited promise or ignored future whose failure nobody sees, an error callback that is never called, or an error return value that is ignored.
- **Missing failure paths.** A network, file, database, or subprocess call whose failure the surrounding code must handle but does not: no timeout where a hung call blocks a core path, no rollback when a multi-step write fails halfway, no cleanup of a resource on the error path.
- **Too-broad handlers.** A handler for every exception that also catches the programming errors and interrupts it was not written for.

For each candidate, name the failure that can happen (the exception, the error value, the timeout) and show from the code that it can happen and what the caller then sees.

## Do not report

- A handler that deliberately ignores an error the code or a comment shows is expected and harmless, such as a missing optional file.
- Logging wording or log levels, unless the failure is otherwise invisible.
- Missing handling around calls that cannot fail in the way you describe.

## Severity

- **C:** the hidden failure loses or corrupts data, or hides a failed security check.
- **H:** a caller is told an operation succeeded when it failed, or works on wrong data, on a normal path.
- **M:** the same on an edge case, or a lost cause that makes a real failure hard to diagnose.
- **L:** a handler broader than it needs to be, with no wrong result shown.
