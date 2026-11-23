<!-- Partly adapted from mattpocock/skills 1.3.1, skills/engineering/code-review/SKILL.md (MIT). Changed: the Spec brief reworded for a defect-only finder, with a requirement coverage table and severity guidance. See THIRD_PARTY_NOTICES.md. -->

# Spec lens

Check the diff against the spec it implements: find requirements that are missing, partly done, or implemented wrongly.

## Requirements

Read the spec you were given in full. List the requirements this change must meet:

- Take them from the acceptance criteria when the spec has them, otherwise from its statements of required behavior.
- Leave out what the spec puts out of scope, assigns to another ticket, or marks as a note or an open question.
- Quote each requirement in the spec's own words, shortened only by cutting whole clauses.

Then check each requirement against the diff and the code it changes. Read the code; do not trust names, comments, or commit messages.

- `done`: the code meets the requirement.
- `partial`: the code meets part of it, or meets it wrongly.
- `missing`: no code meets it.

## Look for

- A requirement with no implementation.
- A requirement implemented only in part, for example one case of several.
- A requirement implemented wrongly: wrong value, wrong condition, wrong error, wrong place.
- Behavior the spec explicitly excludes or puts out of scope, added anyway.

Every finding quotes the requirement in its `rule` field: `<spec source> — "<requirement>"`, and its origin is `introduced`. For a missing requirement, point `file` and `line` at the code where the requirement belongs, such as the function or module the spec names; if there is none, use the spec file and the requirement's line.

## Severity

- **H:** a requirement implemented wrongly, or implemented in part so that a normal path behaves wrongly.
- **M:** a requirement missing, a part missing that only an edge case needs, or excluded behavior added. A change may cover only part of a spec on purpose; the coverage table shows what is missing.
- **C:** a requirement implemented wrongly in a way that also meets the C grade in `severity.md`.

## Output

Before your findings, or before `NO ISSUES`, give one coverage block with one row per requirement:

```text
COVERAGE
- <requirement, quoted> | <done | partial | missing> | <file:line that implements it, or none>
END
```

Every `partial` or `missing` row has a finding that quotes the same requirement.
