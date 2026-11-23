# Finding schema

Every finder reports each defect as one block. Keep every field on one line, except `code`, which may span up to three lines.

```text
FINDING
lens: <lens id, for example correctness-a>
file: <path relative to the repository root>
line: <line number, or start-end>
severity: <C | H | M | L, see severity.md>
origin: <introduced | pre-existing>
title: <what is wrong, under 80 characters>
code: <the code at that location, quoted exactly>
claim: <what is wrong and why, in one or two sentences>
failure: <a concrete failure: the input or state, then the wrong result>
rule: <the rule and its source, see below; several rules separated by "; "; otherwise none>
fix: <the suggested fix, in one or two sentences or one short code line>
END
```

The `rule` field is required for the `standards`, `spec`, and `stack` lenses; the orchestrator drops their findings without one. Cite a documented rule as `<source> — "<the rule, quoted>"`, where the source is a file path or a skill name such as `daedalus-python:python-patterns`; a spec requirement as `<spec source> — "<the requirement, quoted>"`; and a code smell as `smell: <name> (smell baseline)`.

The orchestrator adds the rest:

- `lenses`: every lens that reported the finding, after duplicates merge.
- `verdict`: `CONFIRMED`, `REFUTED`, or `UNCERTAIN`, from the verifier.
- `citation`: the verifier's `file:line` and evidence.
- `id`: the report tag, the severity letter plus a number, for example `H2`.
