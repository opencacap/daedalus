<!-- Partly adapted from anthropics/claude-plugins-official, plugins/code-review/commands/code-review.md (Apache-2.0). Changed: reworded, grouped by category, and extended for this skill. See THIRD_PARTY_NOTICES.md. -->

# Suppression list

Finders do not report anything below.

The orchestrator also drops any finding that reaches it in one of these categories:

- **Style.** Naming, formatting, layout, ordering, comment wording, and personal preference.
- **Linter and compiler territory.** Unused imports or variables, formatting, and anything else the repo's linter, formatter, or type checker reports. Do not run the linter to check.
- **Silenced code.** Code under a lint-ignore or suppression directive (`# noqa`, `// eslint-disable-next-line`, `@SuppressWarnings`, `# type: ignore`, and similar) for the rule that directive names.
- **Input-dependent speculation.** "If this ever receives null", "this could be slow at scale", and other claims that depend on input or state the code does not show can happen.

These guide finders only. The orchestrator leaves them to the verifier:

- **Code that only looks wrong.** Check the surrounding code before you report. Code that is correct in context is not a finding.
- **Nitpicks.** Anything a senior engineer would not raise in review.
- **General quality wishes outside your lens.** "Consider adding tests", "consider adding validation", or "add documentation", unless a repo rule requires it.
