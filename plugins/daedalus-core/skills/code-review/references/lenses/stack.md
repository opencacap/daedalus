# Stack lens

Check the diff against the patterns skills of the stacks it uses, such as Python, Spring Boot, React, or FastAPI. The rubric is those skills, not your own taste.

## Rubric

Load every rubric skill your lens input names, with your skill tool, by its full name (for example `daedalus-python:python-patterns`). These skills are references, not review skills. If a skill does not load, reply exactly `NO RESULT: cannot load <skill>` and stop.

Use only the rules a skill states as rules: its anti-patterns, its "Bad" or "Never" examples, and its explicit requirements. Its general advice and "prefer" items are judgement calls; report them only when breaking them causes a defect the code shows.

## Look for

- Code in the diff that matches an anti-pattern or "Bad" example of a rubric skill.
- Code that breaks an explicit requirement of a rubric skill, such as a required annotation, lifecycle rule, transaction boundary, or resource rule.
- A framework or library API used in a way the rubric says fails, leaks, or is unsafe.

Every finding cites the rule in its `rule` field: `<plugin>:<skill> — "<the rule or example heading, quoted>"`. A documented repo standard overrides a rubric rule; do not report what the repo endorses.

## Severity

Grade the consequence with `severity.md`. A breach that causes wrong behavior on a normal path is H. A breach with a real maintenance cost but no wrong result shown is M at most. A breach of general advice is L.
