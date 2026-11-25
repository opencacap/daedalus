---
status: accepted
---

# Repo standards own the testing policy

`daedalus-core` used to load `rules/testing.md` into every session of every project that installs it. That file required 80% coverage, unit, integration, and E2E tests, and test-driven development for every change. It said these were explicit requirements, which defeated the README's promise that repo standards override the shared rules. It also contradicted the shared rules' own section 5, which gives TDD to `mattpocock-skills:tdd` and says not to run every workflow step for every task. The floor makes no sense for a Terraform repo or a repo of Markdown skills, and ADR 0001 measured its cost in review: code-review precision was 0.67 and 0.76 for one shared reason, "no unit test" findings that cited `testing.md`. As decided in #8, the shared rules now keep a short testing floor with no numbers. Each project sets its own coverage target and required test types in its repo standards.

## Decision

- Delete `rules/testing.md`. Section 3 of `rules/engineering.md` gains three lines. A changed behavior or a bug fix comes with a test that would fail if the change were reverted; a project with no test suite says so and verifies another way. The project sets its coverage target and required test types, and the shared rules set none. Fix the implementation, not the test, unless the test is wrong.
- TDD lives in `mattpocock-skills:tdd`, which the workflow picks per task.
- Precedence: repo standards, then the shared rules, then style plugins such as `ponytail` and `caveman`. A style plugin never reduces the tests that the repo standards or the shared rules require. A repo may raise or lower them.
- A project states its target in its repo standards. To enforce it, the project puts a coverage gate in the `## Checks` section of its review config or in CI.
- The code-review `tests` and `standards` lenses report a missing test only when a repo standard requires one, never on the shared rules alone.

## Considered options

- **Keep the floor and add an opt-out.** It was rejected because a project would have to turn off a rule that does not fit it, and a hook that loads `rules/*.md` cannot turn off one file.
- **Remove all testing guidance from the shared rules.** It was rejected because an agent that changes behavior without a test is still the failure most worth preventing.
- **Let code review cite the shared floor and cap those findings at L.** It was rejected because the floor guides the agent that writes the code. A reviewer that reports against it reproduces the false positives that ADR 0001 measured.

## Consequences

- A team with no test rule in its repo standards gets no missing-test findings from code review. The `tests` lens still reports tests that cannot fail, tests that check the wrong thing, and tests the diff breaks. Such a team adds one line to `AGENTS.md` to get missing-test findings.
- Installed projects change behavior on upgrade, so `daedalus-core` moves to 0.7.0. The README section on rules says where to state a target.
- The `THIRD_PARTY_NOTICES.md` row for `rules/testing.md` goes away with the file.
- The change is done when both paths of `plugins/daedalus-core/evals` (`--runs 3`) keep C/H recall, raise precision, and no finding cites `testing.md`. A new eval case must show that the `tests` lens reports a missing test, at M, when the fixture's `AGENTS.md` requires one.
