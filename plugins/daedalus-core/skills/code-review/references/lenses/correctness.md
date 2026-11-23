<!-- Partly adapted from anthropics/claude-plugins-official, plugins/code-review/commands/code-review.md (Apache-2.0). Changed: reworded, split into two read strategies, and extended for this skill. See THIRD_PARTY_NOTICES.md. -->

# Correctness lens

Find code that does the wrong thing: code that will fail, crash, or produce a wrong result.

## Look for

- Logic errors: inverted or wrong conditions, wrong operators, off-by-one errors, wrong boundaries, wrong order of operations.
- Wrong results on a normal path: a function that does not do what its name, docstring, callers, or tests say it does.
- Code that will not compile, parse, or load: syntax errors, type errors, missing imports, unresolved names, wrong argument counts or orders.
- Broken contracts: a changed signature, return value, or side effect that a caller still relies on.
- State and data errors: mutation of shared state, values lost or overwritten, a resource that is never released, a race on a path that runs concurrently.
- Null, empty, and missing values the code itself shows can occur.

Leave security, error handling, standards, tests, and types to their own lenses, unless the defect is a plain wrong result.

## Strategy

Both passes use the same brief. They read the diff differently, so each can find what the other misses. Use the strategy you were given.

- **Strategy A: diff first.** Read the diff in file order, hunk by hunk. For each hunk, read the whole changed function, then the code it calls.
- **Strategy B: context first.** Take the changed files in reverse order. For each changed function, read its callers and its tests first and write down what they expect. Then read the change and check it against those expectations.
