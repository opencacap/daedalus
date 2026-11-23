<!-- Partly adapted from affaan-m/everything-claude-code, agents/type-design-analyzer.md (MIT). Changed: rewritten as a defect-only finder brief over the type definitions in the diff, with a failure-scenario requirement and severity guidance. See THIRD_PARTY_NOTICES.md. -->

# Types lens

Find type definitions in the diff that let wrong values through or break the code that uses them. A type definition is a class, interface, type alias, struct, enum, record, data class, schema, or model, and the fields and annotations inside it.

## Look for

- **Broken promises.** A type whose declaration does not give the property its docs, name, or users rely on: a type documented as immutable that can be mutated, one used as a dict key or set member that the language makes unhashable, a value object without the equality its users need.
- **Illegal states.** A type that lets the code build a state the rest of the code cannot handle, such as two flags that must never both be true, an optional field that every user reads as present, or a status with no field for the data that status requires.
- **Unenforced invariants.** An invariant the type documents (`low <= high`, `non-empty`, `cents are integers`) that a constructor, setter, or public field lets callers break, where the diff's own code can break it.
- **Types that lie about data.** A declared field type, optional flag, or variant list that does not match what the code actually stores or receives.
- **Breaking changes.** A field, variant, or signature change that existing users still handle the old way, such as a new enum member that an exhaustive switch does not cover.
- **Escape hatches.** A cast, `any`, or non-null assertion in the diff that hides a mismatch the code shows can happen.

Point `file` and `line` at the type definition, or at the field, when the defect is in the type. Show in the failure the code path that builds or receives the wrong value.

## Do not report

- Type design preferences with no wrong result, such as "this could be a union" or "prefer an interface".
- Missing annotations the type checker would report.
- Invariants no code in the diff or its callers can break.

## Severity

- **C:** the wrong value corrupts stored data or breaks a security check.
- **H:** a normal path builds or receives a value the type allows but the code cannot handle, so it crashes or returns a wrong result.
- **M:** the same on an edge case.
- **L:** an invariant the type documents but does not enforce, with no breaking path shown.
