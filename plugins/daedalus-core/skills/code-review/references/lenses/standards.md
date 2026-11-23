<!-- Partly adapted from mattpocock/skills 1.3.1, skills/engineering/code-review/SKILL.md (MIT). Changed: the Standards brief and the smell baseline reworded for a defect-only finder, with rule citations and a severity cap. See THIRD_PARTY_NOTICES.md. -->

# Standards lens

Find places where the diff breaks a documented standard of this repository, and code smells from the baseline below.

## Sources

- **Documented standards.** The repo standards and shared rules you were given: `CLAUDE.md`, `AGENTS.md`, `.claude/rules`, `CODING_STANDARDS.md`, `CONTRIBUTING.md`, ADRs, and the daedalus-core rules. Read each one, and check the changed code against every rule that applies to it.
- **Smell baseline.** The smells below apply even when the repo documents nothing.

Two rules bind them:

- **The repo overrides.** A documented repo standard always wins over the baseline and over the shared rules. Where the repo endorses something a smell would flag, do not report the smell.
- **Tooling owns its territory.** Skip anything a linter, formatter, or type checker enforces.

## Cite the rule

Every finding cites the rule it applies, in its `rule` field:

- A documented standard: `<file> — "<the rule, quoted>"`, for example `CODING_STANDARDS.md — "Domain code under src/ never reads the clock."`
- A smell: `smell: <name> (smell baseline)`, for example `smell: Feature Envy (smell baseline)`.

A finding without a rule is not a standards finding. Leave it out.

## Smell baseline

Each smell is a judgement call, never a hard violation. Name the smell, quote the code, and give the fix.

- **Mysterious Name:** a function, variable, or type whose name does not say what it does or holds. Fix: rename it.
- **Duplicated Code:** the same logic appears in more than one hunk or file of the change. Fix: extract the shared logic and call it from both places.
- **Feature Envy:** a function that uses another object's data more than its own. Fix: move it next to the data.
- **Data Clumps:** the same few fields or parameters travel together again and again. Fix: bundle them into one type.
- **Primitive Obsession:** a primitive or string stands in for a domain concept that deserves its own type. Fix: give the concept a small type.
- **Repeated Switches:** the same `switch` or `if` cascade on the same value appears in several places of the change. Fix: one shared map, or polymorphism.
- **Shotgun Surgery:** one logical change forces scattered edits across many files. Fix: gather what changes together into one module.
- **Divergent Change:** one file or module is edited for several unrelated reasons. Fix: split it so each part changes for one reason.
- **Speculative Generality:** abstractions, parameters, or hooks for needs the change does not have. Fix: delete them.
- **Message Chains:** long `a.b().c().d()` navigation the caller should not depend on. Fix: hide the walk behind one method.
- **Middle Man:** a class or function that mostly delegates to another. Fix: call the real target directly.
- **Refused Bequest:** a subclass or implementer that ignores or overrides most of what it inherits. Fix: use composition.

Report a smell only in code the diff adds or changes.

## Severity

- **M:** a breach of a documented standard with a real maintenance or correctness cost that the rule itself names or the code shows.
- **L:** every smell, and a breach of a documented standard with no cost beyond the breach.
- Report a breach at C or H only when it also causes the wrong behavior that grade describes, and say so in the failure.
