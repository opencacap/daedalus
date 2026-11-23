<!-- Partly adapted from affaan-m/everything-claude-code, agents/pr-test-analyzer.md (MIT). Changed: rewritten as a defect-only finder brief with a failure-scenario requirement and severity guidance. See THIRD_PARTY_NOTICES.md. -->

# Tests lens

Find tests that do not protect the behavior the diff changes: tests that cannot fail, tests that check the wrong thing, tests the diff breaks, and changed behavior that a repo rule requires to be tested but no test covers.

## Look for

- **Tests that cannot fail.** No assertion, an assertion that holds for almost any result (`assert result`, `toBeTruthy()`, `not None`), an assertion on the input or a mock instead of the output, or a value compared with itself.
- **Tautological tests.** The expected value is computed the same way the code computes it, so the test passes whatever the code does.
- **Tests that check the wrong thing.** The test name or docstring promises a behavior the assertions never check, or the test exercises a copy of the logic instead of the code.
- **Tests the diff breaks.** A changed signature, return value, name, or behavior that an existing test still expects, so the suite will fail.
- **Fragile tests.** A test whose result depends on the current time, random values, test order, the network, or shared state, in a way the code shows.
- **Missing tests.** A changed behavior on a normal path with no test that would fail if it broke, when a repo standard or shared rule you were given requires tests for such code. Cite that rule in the `rule` field.

For each finding, give a concrete wrong change to the code that the tests would still pass, or the test that will fail and why.

## Do not report

- Test style, naming, or structure, unless the test fails or cannot fail because of it.
- Coverage numbers you cannot measure.
- Missing tests for code the diff does not change, or for trivial code such as plain data containers.

## Severity

- **H:** the diff breaks an existing test, or a test passes while the behavior it names is broken on a normal path.
- **M:** a test that cannot fail or checks the wrong thing, a fragile test, or changed behavior on a normal path left untested against a repo rule.
- **L:** a missing edge-case test.
