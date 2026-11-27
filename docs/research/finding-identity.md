# Research: how analysis tools keep a finding's identity across runs

Status: research complete. Input for map issue #19 (`daedalus-land`), ticket #21.
Date: 2026-11-27. Source code read at the commits named in each section.

## Question

How do static-analysis and review tools keep a finding's identity stable across runs and code
changes, and gate on new findings only? What inputs make up the fingerprint, and how often do
matches break? Is there public work on matching LLM-generated review findings across runs?

## Short answer

- No tool uses the line number as identity. They hash content near the finding (one line, a
  100-character window, the matched code, or the rule pattern with its bound values), plus the
  rule id and the file path.
- Matching is staged: exact keys first, then looser keys, with a one-to-one constraint. Each
  looser stage catches fewer pairs and is more likely to pair the wrong findings.
- Matches break when the finding's own line is edited, when files are renamed or refactored, and
  when identical code repeats in a file. One labelled study measured 64.4% tracking precision for
  the classic staged matcher, and 90.3% after adding refactoring detection and optimal assignment.
- Gates count only "new" findings, and tools are moving to define new by the lines a change
  touched, not by whether matching failed.
- Public work on LLM review findings matches by meaning: a cheap deterministic filter (file, line
  overlap), then embeddings or an LLM judge. Nobody publishes a cross-run identity scheme for LLM
  review findings with measured accuracy. The closest data is benchmark scoring and within-run
  dedup.

## 1. SARIF 2.1.0

Source: OASIS SARIF 2.1.0 Errata 01, complete HTML
(https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html).

Terms. Two results are **logically identical** when they report the same condition, even if the
`result` objects differ (§3.27.2). "Result matching" is the "process of determining whether two
results are reporting the same condition in the code" (§1.2).

SARIF allows three designs (§3.27.2):

1. Compute a fingerprint from the result; same fingerprint means logically identical.
2. Group results into equivalence classes and name each class with an opaque, arbitrary id. The id
   holds no information from the result.
3. Compute a fingerprint, then map it to an opaque id and use the id.

The properties:

| Property | Who sets it | Meaning |
| --- | --- | --- |
| `guid` (§3.27.3) | Result management system (RMS) should, on ingest | Unique id of this one result object. Results with identical fingerprints still get distinct `guid`s. |
| `correlationGuid` (§3.27.4) | RMS may; "Direct SARIF producers ... SHOULD NOT" | Shared by all logically identical results, distinct across logically distinct ones. This is design 2 or 3. |
| `fingerprints` (§3.27.16) | RMS may; "A direct SARIF producer SHOULD NOT populate this property" | Map of versioned names (`stableResultHash/v2`) to stable ids. Must resist changes "such as ... the line number where a result appears". Compare with "the latest version of the fingerprint available in both results". |
| `partialFingerprints` (§3.27.17) | The producer (the analysis tool) | Map of versioned names to strings that each "contributes to" the fingerprint. The RMS "MAY use any algorithm to combine" them: any one matches, a majority, or all. |
| `baselineState` (§3.27.24) | Whoever compared against a baseline run | One of `new`, `unchanged`, `updated`, `absent`. If one result has it, every result in the run has it. |

`baselineState` values, quoted:

- `new`: "detected in the current run but was not detected in the baseline run."
- `unchanged`: detected in both, and "did not change between those two runs in any way that the
  tool considers significant."
- `updated`: detected in both, "but it changed between those two runs in a way that the tool
  considers significant."
- `absent`: "detected in the baseline run but was not detected in the current run."

Note 2 of §3.27.24 maps these to issue-tracker actions: `new` files an issue, `updated` edits it,
`absent` resolves it, `unchanged` does nothing.

Appendix B (normative) gives the fingerprint inputs:

- The RMS "SHOULD construct a fingerprint by using information contained in the SARIF file such
  as the name of the tool that produced the result, the rule id, the file system path to the
  analysis target."
- The RMS "SHOULD include the information in partialFingerprints in its fingerprint computation."
- The tool "SHOULD NOT include in partialFingerprints information that a result management
  system could deduce from other information in the SARIF file, for example, file hashes."
- The RMS "SHOULD NOT include an absolute line number ... in its fingerprint computation."
- Stability goal: the fingerprint "only needs to be stable enough to reduce the number of results
  that are erroneously reported as new to a low enough level that the development team can manage
  the erroneously reported results without too much effort."

§3.29 adds that logical locations (for example `fullyQualifiedName`) are "typically more resilient
to changes in source code than are the line numbers", which makes them good fingerprint input.

The split matters for `daedalus-land`: the producer emits partial fingerprints; the RMS owns
matching, the final fingerprint, and the opaque class id. In #19 terms, `daedalus-core` is the
producer and `daedalus-land` is the RMS.

### Reference matcher: Microsoft SARIF SDK

Source: `microsoft/sarif-sdk`, `src/Sarif/Baseline/V2/` (last change 03b4ef4, 2024-07-24). The
Multitool's baseliner pairs results by **where** (file URI or fully qualified name, sorted) and
**what**. `WhatComparer.cs` checks, in order:

1. Equal `guid` matches. A different `guid` does not reject, "as GUIDs are often re-generated by
   tools."
2. Any one equal `fingerprints` entry matches. If both have the same fingerprint names but no
   value is equal, the pair is rejected.
3. `partialFingerprints`: match if the matching entries carry at least half of the trust weight.
4. Otherwise: the message, with line and column numbers replaced by markers, and the first
   snippet must both be equal.

`TrustMap.cs` learns each attribute's trust from the two runs: "Trust is the product of how often
values match and how unique the values were." An attribute with one constant value, or one that
never matches, gets low trust. After exact links, the matcher tries nearby unlinked results before
and after each linked pair.

## 2. CodeQL and GitHub code scanning

Sources: GitHub docs "SARIF support for code scanning"
(https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning);
`github/codeql-action` `src/fingerprints.ts` (last change 048d0ea, 2026-03-10); issue
github/codeql-action#986.

Inputs. GitHub matches on the `ruleId`, the file path, and `partialFingerprints`. The docs say
"Code scanning only uses the `primaryLocationLineHash`", the `ruleId` "has to be the same across
analysis", and the file path "has to be consistent across the runs". If the SARIF has no
fingerprint, the CodeQL Action computes one; a raw API upload without one may show duplicate
alerts.

`primaryLocationLineHash`, from `fingerprints.ts`:

- A rolling hash (modulus base 37) over the first 100 characters starting at the start line of
  the primary location (`locations[0]`), skipping spaces and tabs, with CR and CRLF normalized to
  LF. The window runs past the end of a short line into the next lines.
- A `:N` suffix counts earlier lines in the same file with the same hash, so identical code gets
  `hash:1`, `hash:2`, and so on.
- A result with no region uses line 1. A result with no start line, a non-file URI, or a path
  outside the source root gets no fingerprint.

Failure modes:

- Editing the alert's line, or the next characters inside the 100-character window, changes the
  hash. A GitHub staff reply on #986 says the old alert is then "closed" and a fresh one is
  created, and "The fresh alert won't be connected to the closed one so things like 'won't fix'
  status are lost." The reported case was a Dependabot bump of a pinned action hash.
- Adding an identical copy of the code above the alert shifts the `:N` index.
- A renamed or moved file changes the path, so the alert closes and reopens as new.

PR gate. Since March 2023 code scanning "reports only alerts inside the lines of code that the
pull request has changed" (GitHub changelog 2023-03-17). The PR check fails on results with
severity error, critical, or high, and repository settings can change that threshold.

Not verified: the server-side matching beyond `primaryLocationLineHash` (closed source), whether
GitHub reads `baselineState`, `correlationGuid`, or `guid` (the docs do not mention them), and
whether the CodeQL CLI computes the hash the same way as the Action.

## 3. SonarQube

Sources: `SonarSource/sonarqube` `sonar-core/src/main/java/org/sonar/core/issue/tracking/`
(`Tracker.java`, `AbstractTracker.java`, `BlockRecognizer.java`, `BlockHashSequence.java`) and
`sonar-core/src/main/java/org/sonar/core/hash/SourceLineHashesComputer.java`, read from the
default branch on 2026-11-27; docs on issues, new code, and quality gates (links below).

Inputs. An issue carries the rule key, the line, the message, and a **line hash**: MD5 of the
issue's line with spaces and tabs removed (an empty line hashes to `""`). There is no global
fingerprint. `Tracker.trackNonClosed` pairs raw (this analysis) and base (previous) issues in six
passes, each only over issues still unmatched:

1. rule, line, line hash, message
2. rule, line, line hash
3. code-move detection by block hashes (below)
4. rule, message, line hash
5. rule, line, message
6. rule, line hash (SONAR-2812)

When several base issues fit, the most recently updated one wins. Unmatched raw issues are new;
unmatched base issues are closed. A second pass (`trackClosed`) matches remaining raw issues
against closed issues on rule, line, line hash, and message, so a fixed issue that comes back is
reopened with its history.

Code moves. `BlockHashSequence` hashes a block of the line hashes five lines on each side of each
line. A block hash that occurs exactly once in base and once in raw maps all issues on the base
line to the raw line. Otherwise the matcher pairs lines by the longest shared run of line hashes,
and gives up when the remaining line pairs reach 250,000.

Failure modes, from the passes: an issue whose line and message both change, and that is not
inside a recognized moved block, is closed and reopened as new. A message that embeds a variable
name changes when the variable is renamed.

### New-code gate (Clean as You Code)

- New code is "code that you've recently added or modified". The new code definition is one of:
  previous version, number of days, specific analysis, or reference branch. In a pull request, new
  code is "the code that has changed in the pull request branch compared to the target branch"
  (https://docs.sonarsource.com/sonarqube-server/latest/user-guide/about-new-code/).
- Built-in Sonar way gate, SonarQube Server 2025.4: "No new issues are introduced", "All new
  Security Hotspots are reviewed", new-code coverage at least 80.0%, new-code duplication at most
  3.0%. The fudge factor ignores the coverage and duplication conditions "until the number of new
  lines is at least 20"
  (https://docs.sonarsource.com/sonarqube-server/2025.4/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates).
- Whether an issue counts as new code depends on its **issue date**. Per the Server issue docs
  (https://docs.sonarsource.com/sonarqube-server/2025.5/user-guide/issues/solution-overview,
  paraphrased), a new issue gets the analysis date, but is backdated to the line's last commit
  date in some cases: first analysis, a newly activated or changed rule, an upgrade, external
  rules, and previously excluded files.
- Change, announced 2026-09-23
  (https://community.sonarsource.com/t/issues-on-unchanged-code-no-longer-fail-your-quality-gate/188724):
  "SonarQube always sets the issue date to that line's last commit date instead of the analysis
  date." So issues on lines nobody touched no longer count as new code. Live in SonarQube Cloud and
  Community Build 26.9; Server 2026.5 was announced as "Coming soon". The post accepts the cost:
  some real new issues on unchanged lines are now left out of the gate.
- PR analysis reports only issues on new code. After the merge, the PR's issue status, assignee,
  and comments move to the target branch.

Not verified: whether Server 2026.5 shipped the change.

## 4. Semgrep

Sources: `semgrep/semgrep` `cli/src/semgrep/rule_match.py`, `cli/src/semgrep/run_scan.py`, and
`src/osemgrep/reporting/Sarif_output.ml`, read from the default branch on 2026-11-27; docs
https://docs.semgrep.dev/semgrep-code/remove-duplicates.

Semgrep computes two ids:

- `syntactic_id`: a hash of `(rule id, path, syntactic_context, index)`. The syntactic context is
  the matched code with `nosemgrep` comments removed, dedented, and stripped. Changes to the
  matched code, the path, or the occurrence index change it. The docs call it mainly "for internal
  debugging".
- `match_based_id`: BLAKE2b (SHA-256 in FIPS mode) of `(pattern formula with metavariable values
  substituted, path, rule id)`, plus `_<index>` among same-key matches in the file. The source
  comment: "we no longer count formatting + line number changs + other things as new findings".
  The docs: code changes that give "the same rule pattern when abstracted to the level of the rule
  pattern match" keep the id. SARIF output writes it as `fingerprints["matchBasedId/v1"]`, only
  for a logged-in user.

Semgrep also sends `code_hash`, `pattern_hash`, `start_line_hash`, and `end_line_hash` so the
platform can tell a file move from a move within a file.

Diff-aware scans (`--baseline-commit`): `remove_matches_in_baseline` drops each head finding whose
`(rule id, path after renames, syntactic_context, index)` also occurs in the baseline scan. If the
baseline scan failed on a file, or on a rule in that file, it suppresses those head findings
instead of reporting them as new: it "cannot prove new".

Failure modes: a changed metavariable value (for example a renamed variable) changes
`match_based_id`, and a renamed file changes both ids outside diff-aware scans. The docs warn that
the calculations "are subject to change at any time".

## 5. GitLab (both forges matter to `daedalus-land`)

- Code Quality reports carry a required `fingerprint`: "A unique fingerprint to identify this
  specific code quality violation, such as a hash of its contents." The merge request compares
  findings "with the findings from a baseline pipeline on the target branch", and "Multiple code
  quality findings with identical fingerprints display as a single entry"
  (https://docs.gitlab.com/ci/testing/code_quality/).
- SAST in GitLab Ultimate has "advanced vulnerability tracking" to find "when the same
  vulnerability has moved in the same file due to refactoring or unrelated changes"
  (https://docs.gitlab.com/user/application_security/sast/).

Not verified: the advanced tracking algorithm (the user docs do not describe it).

## 6. Posting tools: reviewdog

Source: `reviewdog/reviewdog` `service/serviceutil/comment.go` and `service/github/github.go`
(master 89d3fff, 2026-11-25). Fingerprint: FNV-64a of the whole serialized diagnostic, including
message and location. reviewdog writes it into each posted comment as
`<!-- __reviewdog__:<base64> -->`, reads it back on the next run to skip already-posted comments,
and deletes its own comments that were not reproduced, unless they have replies. The state lives
on the forge; any change to the message or the line makes a new comment.

## 7. Measured failure rates for warning tracking

- Avgustinov et al., "Tracking Static Analysis Violations over Time to Capture Developer
  Characteristics", ICSE 2015 (Semmle; https://codeql.github.com/publications/tracking-analysis-violations.pdf).
  Staged matching: location-based through the diff (exact, or "fuzzy" within three lines in a
  diff region), then same-file snippet equality, then a hash of the 100 tokens before or after the
  violation for renamed or moved files. Duplicate hashes are excluded, and matching is one-to-one.
  Over 5,000 snapshots per project, exact matches were 99.53% to 99.95% of all matchings, fuzzy
  0.04% to 0.27%, snippet up to 0.01%, and hash 0.01% to 0.19%. The small stages still mattered: on
  MongoDB, hash matching gave 21,239 matchings, ten times the number of fixed violations found.
  Each missed match counts as one false new and one false fixed. A manual check of 400 hash-based
  matchings found none "obviously wrong".
- Li and Yang, "Tracking the Evolution of Static Code Warnings: the State-of-the-Art and a Better
  Approach", arXiv 2210.02651v2, 2024-01-23. On 3,451 manually labelled SpotBugs and PMD warnings
  from JClouds, Kafka, Spring Boot, and Guava, the state-of-the-art staged matcher reached 64.4%
  precision on the removed and newly-introduced statuses. Causes: refactoring, code shifts, and
  volatile metadata (anonymous classes or methods). StaticTracker adds refactoring detection
  (RefactoringMiner), optimal one-to-one assignment (Hungarian algorithm), and metadata handling,
  and reaches 90.3%. It also splits removed warnings into fixed and non-fix removal (for example
  code deletion), with 69.9% precision on removed-by-fix.

Not verified: the published venue of the Li and Yang paper.

## 8. Matching LLM-generated review findings

No published cross-run identity scheme for LLM review findings was found. Related work:

- **SWR-Bench** (arXiv 2509.01494, 2025-09-01). An LLM extracts change-points from a review and
  does "a fact-based matching task" against ground-truth change-points. On 100 reports with three
  human experts and two LLM judges, pairwise agreement on the binary hit label was 89.2% to 94.9%;
  severity agreement was much lower. Run-to-run variance: "for the same LLM over five independent
  runs, only 27 successfully identified change-points overlapped" (the denominator is in a figure
  and was not verified). Aggregating 10 runs with one more LLM call (Self-Agg) raised recall
  118.83% and F1 43.67% over a single run. This matches #19's note that later rounds report
  defects that were in the code all along.
- **Kumar, Bararia, and Raj**, "Bigger Isn't Always Better" (arXiv 2606.15689, 2026-04-09).
  Two-pass matching of model findings to ground truth. Pass 1 is deterministic and requires all of:
  a normalized file path match, line-range overlap with ±5-line tolerance, and a compatible comment
  type. Pass 2 sends the uncertain findings to an LLM judge at temperature 0 with a rubric; a
  partial match scores 0.5. Pass 1 "handles ∼70% of cases at zero LLM cost."
- **Kodus** (`kodustech/kodus-ai`, `libs/code-review/infrastructure/agents/engine/finding-dedup.ts`,
  last change d027ea9, 2026-11-20). Within-run dedup of LLM review suggestions: an LLM proposes
  groups per file, then a tiered guard decides each merge. High lexical overlap merges. Otherwise
  the embedding cosine decides: above a high threshold merges, below a low one keeps both, and in
  between an LLM "same bug?" tiebreak decides. A failed tiebreak keeps both. Issue
  kodustech/kodus-ai#2170 (2026-10-17) measured 10 PRs, 103 suggestions, and 73 gold duplicate
  pairs. With embeddings, 68 of 73 pairs were found (93.2%) and no wrong pair was merged. Without
  embeddings, 40 of 73 were found (54.8%), and an extra LLM pairwise arm recovered 59 of 73. Small
  sample, one vendor, within one run.

Not verified: Kodus threshold values (defined in another file), and how any commercial PR bot
(for example CodeRabbit or Copilot code review) tracks findings across pushes. Their docs and code
were not read.

## Implications for daedalus-land

What the sources mean for LLM findings:

- The finding schema has `file`, `line`, `code` (quoted exactly), `lens`, `title`, `claim`,
  `failure`, `rule`, and `severity`. For an LLM, `title`, `claim`, `failure`, and `fix` are like a
  SARIF message that is reworded every run, so they cannot go into an exact fingerprint. The
  SARIF SDK trust map would give them low trust for the same reason. `line` shifts, and Appendix B
  bans absolute lines. `code` is the most stable field, but the model may quote a different span
  each run.
- An LLM finding can be `absent` because the code was fixed or because the reviewer missed it this
  time (SWR-Bench: little overlap across five runs). Static tools treat absent as fixed; Li and
  Yang show that even for static tools, removed is not always fixed. `daedalus-land` should not
  resolve a finding only because it is absent; it should check whether the code at its anchor
  changed.
- A ruling must not hang on a hash. GitHub loses "won't fix" when the hash changes (#986). A ruling
  should attach to a stable class id that the matcher carries forward.

Candidate designs, which can be combined:

**A. Content-anchored partial fingerprints from `daedalus-core`.** Core emits, per finding, a
versioned partial fingerprint such as `codeHash/v1` = hash of (`file`, the `code` text with
whitespace removed) plus an occurrence index, and maybe `symbol/v1` = the enclosing function or
class. This is the SARIF producer role (§3.27.17) and fits the "finding fingerprint" option that
#19 allows in core. Sources: SARIF Appendix B, CodeQL `primaryLocationLineHash`, SonarQube line
hash, Semgrep `syntactic_context`. Tradeoffs: deterministic, cheap, and survives line shifts.
It breaks when the model quotes one line in one run and three in the next, and when a fix edits
the quoted code; then a stage-B or stage-C match must catch it. Leave the lens id out, because the
lens set and duplicate merging vary per run; the `rule` source path may be used for the
`standards`, `spec`, and `stack` lenses. Also leave severity out: a severity change is `updated`,
not `new`.

**B. A staged one-to-one matcher in `daedalus-land`.** Run in order, each stage only on findings
still unmatched: (1) equal partial fingerprint; (2) the earlier line mapped through
`git diff <last reviewed SHA>..HEAD`, then same file and line-range overlap within a small
tolerance; (3) the quoted code contains or is contained in the other quote; (4) stage C for the
rest. Resolve conflicts with one-to-one assignment (Hungarian, or greedy by score). Sources:
SonarQube `Tracker` passes, Avgustinov et al. stages, StaticTracker. Tradeoffs: the most accurate
deterministic design and easy to explain. It needs the diff between reviewed SHAs and more code.
Each loose stage adds wrong pairs, so only stage 1 or 2 should carry a ruling forward without
review.

**C. Semantic match for what remains.** For leftover pairs in the same file (or same symbol), ask
an LLM judge "same defect?" over the two claims, failures, and quoted code, optionally gated by
embedding similarity with high and low thresholds. Sources: SWR-Bench judge, Kumar et al. two-pass,
Kodus tiered guard. Tradeoffs: catches rewording and quote drift that hashes miss. It costs model
calls, is not deterministic, and has to be measured: the published numbers are about 89% to 95%
judge agreement and 93% pair recall on small samples. If the judge fails, keep both findings as
distinct, as Kodus does. Never merge silently.

**D. Opaque stable ids owned by `daedalus-land`.** At first sight a finding gets a PR-scoped id
that never changes (for example `F7`), stored with the PR review state. Matching only decides which
earlier id a new finding inherits. The per-round `H1`/`M2` tags become display labels, or give way
to the stable id. Sources: SARIF `correlationGuid` (§3.27.2, §3.27.4); reviewdog's metadata
comment for keeping state on the forge itself. Tradeoffs: fixes the restarting tags and gives
rulings a home. It needs persistent state (a forge comment or a state file), and a wrong match
carries a ruling onto the wrong defect, so the id should record which stage matched it.

**E. Gate on changed lines, not on matching.** A finding counts toward round N's gate only if its
anchor lies in lines changed since the last reviewed SHA. A finding that is unmatched but sits on
untouched code is a late find of an old defect: report it, but do not let it block or reopen the
loop on its own. Sources: SonarQube's 2026-09 issue-date change and new-code gate, GitHub "only
alerts inside the lines of code that the pull request has changed", Semgrep `--baseline-commit`
(which suppresses findings it "cannot prove new"). Tradeoffs: this targets the #19 evidence (19 of
48 later findings sat in files no fix touched) and does not depend on matching being perfect. Like
SonarQube, it accepts that a real defect on untouched code found late will not gate. It needs a
clear rule for the first round, where the whole PR diff is new.

A plausible combination is A plus B plus D, with E as the gate and C only for leftovers, each
behind an eval with multi-round fixtures, as #19's "Not yet specified" list expects.
