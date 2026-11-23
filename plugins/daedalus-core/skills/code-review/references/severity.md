# Severity

Grade the consequence of the defect, not the size of the fix.

- **C (critical):** data loss or corruption, a security breach, or a crash or outage on a core path.
- **H (high):** wrong behavior on a normal path, or a spec requirement implemented wrongly.
- **M (medium):** wrong behavior on an edge case, or a breach of a documented standard with real maintenance cost.
- **L (low):** a judgement call. Every code smell is L at most.

Pre-existing defects use the same scale and are marked `pre-existing`.

A review is **blocking** when at least one CONFIRMED C or H finding was introduced by the diff. Pre-existing findings never block.

Do not add a confidence score. The verifier decides whether a finding is real.
