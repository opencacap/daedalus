export const meta = {
  name: 'code-review-workflow',
  description: 'Find-then-verify code review: finders, normalize, verifiers, report. Run it through /daedalus-core:code-review --workflow.',
  whenToUse: 'Only when the daedalus-core:code-review skill calls it with --workflow. It needs the scope and context that skill gathers, passed as args.',
  phases: [
    { title: 'Find', detail: 'one finder per lens' },
    { title: 'Normalize', detail: 'drop suppressed findings and merge duplicates' },
    { title: 'Verify', detail: 'one verifier per finding' },
  ],
}

// Runs steps 4 to 7 of the code-review skill (find, normalize, verify, report) over the
// same reference files. The skill resolves the scope and gathers the context inline,
// because a workflow cannot ask the developer for a spec, then passes them as `args`.
// See skills/code-review/references/workflow.md for the args contract.

const SEVERITIES = ['C', 'H', 'M', 'L']
const RULE_REQUIRED = ['standards', 'spec', 'stack']
const BRIEFS = {
  'correctness-a': ['correctness.md', 'A'],
  'correctness-b': ['correctness.md', 'B'],
  security: ['security.md'],
  'error-handling': ['error-handling.md'],
  standards: ['standards.md'],
  spec: ['spec.md'],
  tests: ['tests.md'],
  types: ['types.md'],
  comments: ['comments.md'],
  stack: ['stack.md'],
}
const SHELL =
  'Read files with your file-reading tool, not the shell. Shell access may be limited to git: run each git command on its own, with no cd, pipes, &&, ;, or redirection.'

const FINDING = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    file: { type: 'string' },
    line: { type: 'string', description: 'A line number, or start-end.' },
    severity: { type: 'string', enum: SEVERITIES },
    origin: { type: 'string', enum: ['introduced', 'pre-existing'] },
    title: { type: 'string' },
    code: { type: 'string' },
    claim: { type: 'string' },
    failure: { type: 'string' },
    rule: { type: 'string', description: 'The cited rule, or none.' },
    fix: { type: 'string' },
  },
  required: ['lens', 'file', 'line', 'severity', 'origin', 'title', 'code', 'claim', 'failure', 'rule', 'fix'],
}
const FINDER_RESULT = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['findings', 'no issues', 'no result'] },
    reason: { type: 'string' },
    coverage: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          requirement: { type: 'string' },
          status: { type: 'string', enum: ['done', 'partial', 'missing'] },
          evidence: { type: 'string' },
        },
        required: ['requirement', 'status', 'evidence'],
      },
    },
    findings: { type: 'array', items: FINDING },
  },
  required: ['status', 'findings'],
}
const NORMALIZE_RESULT = {
  type: 'object',
  properties: {
    suppressed: { type: 'array', items: { type: 'integer' } },
    groups: {
      type: 'array',
      items: {
        type: 'object',
        properties: { ids: { type: 'array', items: { type: 'integer' } }, primary: { type: 'integer' } },
        required: ['ids', 'primary'],
      },
    },
  },
  required: ['suppressed', 'groups'],
}
const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['CONFIRMED', 'REFUTED', 'UNCERTAIN'] },
    origin: { type: 'string', enum: ['introduced', 'pre-existing'] },
    citation: { type: 'string' },
  },
  required: ['verdict', 'origin', 'citation'],
}

if (!args || typeof args !== 'object' || !args.refs || !Array.isArray(args.lenses)) {
  return 'Review stopped: this workflow needs the scope and context that the daedalus-core:code-review skill gathers. Run `/daedalus-core:code-review --workflow` instead.'
}

const none = (value) =>
  Array.isArray(value) ? (value.length ? value.join('; ') : 'none') : value === undefined || value === null || value === '' ? 'none' : value
const listOrNone = (items) => (items && items.length ? items.join(', ') : 'none')
const oneLine = (text) => String(text ?? '').replace(/\s*\n\s*/g, ' ').trim()
const rank = (severity) => SEVERITIES.indexOf(severity)
const isNone = (rule) => !rule || rule.trim().toLowerCase() === 'none'

const refs = args.refs
const spec = args.spec && args.spec.source ? args.spec : null
const checks = args.checks || []
const checkResults = checks.length
  ? checks
      .map((c) =>
        c.status === 'FAIL'
          ? `\`${c.command}\`: FAIL\n${c.output || ''}`
          : c.status === 'NOT RUN'
            ? `\`${c.command}\`: NOT RUN (${c.reason || 'not run'})`
            : `\`${c.command}\`: PASS`,
      )
      .join('\n') + (args.checksOnDirtyTree ? '\nThe checks ran on a working tree with uncommitted changes.' : '')
  : 'none'
const context = [
  `Scope: base ${args.base} (merge-base ${args.mergeBase}).`,
  `Diff: run \`${args.diff}\`.`,
]
const shared = [
  `Read file contents from: ${args.read}.`,
  `Repo standards: ${listOrNone(args.standards)}.`,
  `Shared rules: every file in ${args.rules}.`,
  `Check results (evidence): ${checkResults}.`,
]
const gaps = [...(args.scopeGaps || [])]
const addGap = (gap) => {
  if (!gaps.includes(gap)) gaps.push(gap)
}

// 4. Find: one finder per lens, all at once. Normalizing needs every finder's result.
function finderPrompt(id) {
  const [brief, strategy] = BRIEFS[id]
  const input = {
    security: `Checklist: ${args.checklist}`,
    spec: spec && `Spec (${spec.source}): ${spec.text}`,
    stack: `Rubric skills: ${none(args.stack)}`,
  }[id]
  return [
    `You are the ${id} finder in a code review. ${SHELL}`,
    '',
    'Read these files and follow them exactly:',
    `- ${refs}/finder.md`,
    `- ${refs}/lenses/${brief}${strategy ? ` (use strategy ${strategy})` : ''}`,
    `- ${refs}/finding-schema.md`,
    `- ${refs}/severity.md`,
    `- ${refs}/suppression.md`,
    '',
    ...context,
    `Untracked files under review (read them in full): ${none(args.untracked)}.`,
    ...shared,
    `Do not report anything on the repo's list: ${none(args.doNotReport)}.`,
    ...(input ? [input] : []),
    '',
    'Return your reply with the StructuredOutput tool instead of text. Set `status` to `findings`, `no issues`, or `no result`, with the reason in `reason`. Put each FINDING block in `findings`, one object per block with the same fields. Put the rows of a COVERAGE block, when your brief asks for one, in `coverage`.',
  ].join('\n')
}

phase('Find')
const lenses = args.lenses.filter((id) => BRIEFS[id])
const results = await parallel(
  lenses.map((id) => () => agent(finderPrompt(id), { label: `finder:${id}`, phase: 'Find', schema: FINDER_RESULT })),
)

let coverage = null
const raw = []
results.forEach((result, i) => {
  const id = lenses[i]
  if (!result || result.status === 'no result') {
    addGap(`${id} returned no result${result && result.reason ? ` (${oneLine(result.reason)})` : ''}`)
    return
  }
  if (id === 'spec' && result.coverage && result.coverage.length) coverage = result.coverage.map((row) => ({ ...row }))
  for (const f of result.findings || []) {
    if (!f.file || !f.line || !f.claim || !f.failure || (RULE_REQUIRED.includes(id) && isNone(f.rule))) {
      addGap(`${id} returned a malformed finding`)
      continue
    }
    raw.push({
      ...f,
      line: String(f.line).replace(/[–—]/g, '-').replace(/\s+/g, ''),
      lenses: [id],
      rules: isNone(f.rule) ? [] : [f.rule],
      severity: /^smell:/i.test(f.rule || '') ? 'L' : f.severity,
    })
  }
})
if (lenses.includes('spec') && !coverage) addGap('spec returned no coverage table')

// 5. Normalize: drop suppressed findings and merge duplicates.
let suppressed = 0
let findings = raw
if (raw.length) {
  phase('Normalize')
  const listed = raw.map((f, id) => ({ id, lens: f.lenses[0], file: f.file, line: f.line, title: f.title, claim: f.claim, rule: f.rules.join('; ') || 'none' }))
  const normalized = await agent(
    [
      'You normalize the findings of a code review. Judge from the findings below; do not read code, run commands, or spawn agents.',
      '',
      `1. Read ${refs}/suppression.md. Suppress a finding in a category that it tells the orchestrator to drop, and a finding that matches an entry of the repo's do-not-report list: the place the entry names and the issue it describes. Do-not-report list: ${none(args.doNotReport)}.`,
      '2. Group duplicates: findings in the same file, at overlapping or adjacent lines, with the same root cause. For each group of two or more, name as `primary` the member with the clearest title, claim, failure, and fix.',
      '',
      'Findings, as JSON:',
      JSON.stringify(listed, null, 1),
      '',
      'Return with the StructuredOutput tool: `suppressed`, the ids to suppress; `groups`, one entry per group of duplicates with all its ids and its primary id. Leave out findings that have no duplicate.',
    ].join('\n'),
    { label: 'normalize', phase: 'Normalize', schema: NORMALIZE_RESULT },
  )
  if (normalized) {
    const valid = (id) => Number.isInteger(id) && id >= 0 && id < raw.length
    const dropped = new Set(normalized.suppressed.filter(valid))
    suppressed = dropped.size
    const merged = new Set()
    const kept = []
    for (const group of normalized.groups) {
      const ids = [...new Set(group.ids.filter((id) => valid(id) && !dropped.has(id) && !merged.has(id)))]
      if (ids.length < 2) continue
      ids.forEach((id) => merged.add(id))
      const members = ids.map((id) => raw[id])
      const primary = raw[ids.includes(group.primary) ? group.primary : ids[0]]
      kept.push({
        index: Math.min(...ids),
        finding: {
          ...primary,
          severity: SEVERITIES[Math.min(...members.map((f) => rank(f.severity)))],
          lenses: [...new Set(members.flatMap((f) => f.lenses))],
          rules: [...new Set(members.flatMap((f) => f.rules))],
        },
      })
    }
    raw.forEach((f, id) => {
      if (!dropped.has(id) && !merged.has(id)) kept.push({ index: id, finding: f })
    })
    findings = kept.sort((a, b) => a.index - b.index).map((k) => k.finding)
  } else {
    addGap('normalize returned no result; findings were not merged')
  }
}

// 6. Verify: one fresh verifier per finding, with the claim and location only.
function verifierPrompt(f) {
  return [
    SHELL,
    '',
    `Read ${refs}/verifier.md and follow it exactly.`,
    '',
    `Claim: ${f.claim}`,
    `Location: ${f.file}:${f.line}`,
    `Code at that location: ${f.code}`,
    `Cited rule: ${f.rules.join('; ') || 'none'}`,
    ...(spec && f.lenses.includes('spec') ? [`Spec (${spec.source}): ${spec.text}`] : []),
    '',
    `${context.join(' ')}`,
    `Untracked files under review: ${none(args.untracked)}.`,
    ...shared,
    '',
    'Return your verdict with the StructuredOutput tool instead of the three text lines: `verdict` and `origin` as in those lines, and `citation` as the text of the CITATION line.',
  ].join('\n')
}

let verdicts = []
if (findings.length) {
  phase('Verify')
  verdicts = await parallel(
    findings.map((f) => () => agent(verifierPrompt(f), { label: `verify:${f.file}:${f.line}`, phase: 'Verify', schema: VERDICT })),
  )
}

const introduced = []
const needsHuman = []
const preExisting = []
let refuted = 0
let uncertainLow = 0
findings.forEach((f, i) => {
  const v = verdicts[i] || { verdict: 'UNCERTAIN', origin: f.origin, citation: 'the verifier returned no verdict' }
  f.verdict = v.verdict
  f.citation = oneLine(v.citation)
  if (v.verdict === 'CONFIRMED') {
    ;(v.origin === 'pre-existing' ? preExisting : introduced).push(f)
  } else if (v.verdict === 'REFUTED') {
    refuted += 1
  } else if (rank(f.severity) <= rank('H')) {
    needsHuman.push(f)
  } else {
    uncertainLow += 1
  }
})

// 7. Report, in the form of references/report-template.md.
const counters = { C: 0, H: 0, M: 0, L: 0 }
for (const section of [introduced, needsHuman, preExisting]) {
  section.sort((a, b) => rank(a.severity) - rank(b.severity))
  for (const f of section) {
    counters[f.severity] += 1
    f.tag = `${f.severity}${counters[f.severity]}`
  }
}

function block(f) {
  const code = oneLine(f.code)
  return [
    `**${f.tag} — ${oneLine(f.title)}**`,
    `- Location: \`${f.file}:${f.line}\``,
    `- Lenses: ${f.lenses.join(', ')}`,
    `- Code: ${code.includes('`') ? `\`\` ${code} \`\`` : `\`${code}\``}`,
    `- Failure: ${oneLine(f.failure)}`,
    ...(f.rules.length ? [`- Rule: ${oneLine(f.rules.join('; '))}`] : []),
    `- Fix: ${oneLine(f.fix)}`,
    `- Verifier: ${f.verdict} — ${f.citation}`,
  ].join('\n')
}
const section = (items) => (items.length ? items.map(block).join('\n\n') : 'None.')

if (coverage) {
  const unquote = (text) => oneLine(text).toLowerCase().replace(/[“”"'`]/g, '')
  for (const row of coverage) {
    if (row.status === 'done') continue
    const requirement = unquote(row.requirement)
    const owner = findings.find((f) => f.rules.some((rule) => unquote(rule).includes(requirement)))
    if (!owner) continue
    if (owner.tag) row.evidence = owner.tag
    else if (owner.verdict === 'REFUTED') {
      row.status = 'done'
      row.evidence = owner.citation
    } else {
      row.status = `${row.status} (unverified)`
      row.evidence = 'none'
    }
  }
}
const cell = (text) => oneLine(text).replace(/\|/g, '\\|')
let specSection = 'No spec available.'
if (spec && lenses.includes('spec')) {
  specSection = coverage
    ? [
        `Spec: ${spec.source}`,
        '',
        '| Requirement | Status | Evidence |',
        '| --- | --- | --- |',
        ...coverage.map((row) => `| "${cell(row.requirement).replace(/^"|"$/g, '')}" | ${cell(row.status)} | ${cell(none(row.evidence))} |`),
      ].join('\n')
    : `Spec: ${spec.source}\n\nThe spec lens returned no coverage table.`
}

const checksSection = checks.length
  ? checks
      .map((c) => {
        if (c.status === 'FAIL') {
          const output = String(c.output || '').split('\n').map((line) => `  ${line}`).join('\n')
          return `- \`${c.command}\`: FAIL\n  \`\`\`text\n${output}\n  \`\`\``
        }
        return c.status === 'NOT RUN' ? `- \`${c.command}\`: NOT RUN (${c.reason || 'not run'})` : `- \`${c.command}\`: PASS`
      })
      .join('\n') + (args.checksOnDirtyTree ? '\n\nChecks ran on the working tree, which holds uncommitted changes.' : '')
  : 'No checks configured.'

const blocking = introduced.filter((f) => rank(f.severity) <= rank('H')).map((f) => f.tag)
const tagList =
  blocking.length < 3 ? blocking.join(' and ') : `${blocking.slice(0, -1).join(', ')}, and ${blocking[blocking.length - 1]}`
const verdict = blocking.length
  ? `**Verdict: BLOCKING** — ${tagList} ${blocking.length === 1 ? 'is' : 'are'} confirmed and introduced by this diff.`
  : '**Verdict: NOT BLOCKING** — no confirmed C or H finding introduced by this diff.'
const count = (items) => SEVERITIES.map((s) => `${s}${items.filter((f) => f.severity === s).length}`).join(' ')
const files = Number(args.files) || 0
const summary = [
  `Lenses run: ${listOrNone(lenses)}.`,
  `Lenses skipped: ${listOrNone((args.skipped || []).map((s) => `${s.id} (${s.reason})`))}.`,
  `Findings: ${count(introduced)} introduced, ${count(preExisting)} pre-existing, ${needsHuman.length} need a human.`,
  `Dropped: ${suppressed} suppressed, ${refuted} refuted, ${uncertainLow} uncertain M/L.`,
  `Config: ${args.config && args.config !== 'none' ? `\`${args.config}\`` : 'none'}.`,
  `Checks: ${listOrNone(checks.map((c) => `\`${c.command}\` ${c.status}`))}.`,
  `Scope: ${files} ${files === 1 ? 'file' : 'files'}, \`${args.base}\`...${args.uncommitted ? 'HEAD plus uncommitted changes' : 'HEAD'}.`,
  `Scope gaps: ${gaps.length ? gaps.join('; ') : 'none'}.`,
].join(' ')

return [
  `## Code review: \`${args.base}\`...HEAD`,
  '',
  verdict,
  '',
  '### Introduced by this diff',
  '',
  section(introduced),
  '',
  '### Needs a human',
  '',
  section(needsHuman),
  '',
  '### Pre-existing',
  '',
  section(preExisting),
  '',
  '### Spec coverage',
  '',
  specSection,
  '',
  '### Checks',
  '',
  checksSection,
  '',
  '### Summary',
  '',
  summary,
].join('\n')
