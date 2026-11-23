# Report template

Write the report in this exact form. Replace every `<...>`. Keep the headings, the field labels, and their order.

## Tags

Each reported finding gets a tag: its severity letter and a number, for example `H2`. Number each severity from 1 in report order across all sections, so no tag repeats. Within a section, put the most severe first.

## Finding block

```markdown
**<tag> — <title>**
- Location: `<file>:<line>`
- Lenses: <lens ids, comma-separated>
- Code: `<quoted code>`
- Failure: <failure scenario>
- Rule: <cited rule; omit this line when the finding has none>
- Fix: <suggested fix>
- Verifier: <CONFIRMED | UNCERTAIN> — <citation>
```

## Report

```markdown
## Code review: `<base>`...HEAD

**Verdict: <BLOCKING | NOT BLOCKING>** — <reason>

### Introduced by this diff

<CONFIRMED findings with origin introduced, or "None.">

### Needs a human

<UNCERTAIN C and H findings, or "None.">

### Pre-existing

<CONFIRMED findings with origin pre-existing, or "None.">

### Spec coverage

<the coverage table below, or "No spec available.">

### Summary

Lenses run: <ids>. Lenses skipped: <id (reason), ...>. Findings: C<n> H<n> M<n> L<n> introduced, C<n> H<n> M<n> L<n> pre-existing, <n> need a human. Dropped: <n> suppressed, <n> refuted, <n> uncertain M/L. Scope: <n> files, `<base>`...<HEAD, or HEAD plus uncommitted changes>. Scope gaps: <gaps, or none>.
```

## Coverage table

```markdown
Spec: <SPEC SOURCE>

| Requirement | Status | Evidence |
| --- | --- | --- |
| <requirement, quoted> | <done | partial | missing, plus "(unverified)" when its finding is uncertain> | <file:line, or the tag of its finding> |
```

When the spec lens ran but returned no coverage block, write `Spec: <SPEC SOURCE>` and `The spec lens returned no coverage table.`, and record that as a scope gap.

## Rules

- The verdict is `BLOCKING` only when "Introduced by this diff" holds a C or H finding. Its reason names those tags, for example `H1 and H2 are confirmed and introduced by this diff.` Otherwise the verdict is `NOT BLOCKING` and its reason is `no confirmed C or H finding introduced by this diff.`
- The summary is one paragraph. Name every scope gap in it, such as uncommitted changes that were not reviewed or a finder that returned no result.
