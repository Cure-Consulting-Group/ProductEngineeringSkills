export const meta = {
  name: 'cure-release-check',
  description: 'Pre-release gate: migration safety, deployment config, dependency vulnerabilities, and API contract checks in parallel — all must pass',
  whenToUse: 'Run before tagging a release or merging a release branch. Pass args: {base: "v1.2.0"} to diff against a ref; defaults to the last tag.',
  phases: [{ title: 'Check', detail: 'four validators in parallel' }, { title: 'Gate' }],
}

const CHECK = {
  type: 'object', required: ['pass', 'blockers', 'warnings'],
  properties: {
    pass: { type: 'boolean' },
    blockers: { type: 'array', items: { type: 'string' } },
    warnings: { type: 'array', items: { type: 'string' } },
  },
}

const base = (args && args.base) || 'the most recent git tag (find it with `git describe --tags --abbrev=0`; if none, use the full tree)'

const CHECKS = [
  { key: 'migrations', prompt: `Validate database migrations changed since ${base} for release safety: reversibility, table locks on large tables, column drops or renames without a two-step deploy, missing indexes for new query patterns. pass=false only for defects that could break the release; style issues are warnings.` },
  { key: 'deployment', prompt: `Validate deployment readiness for changes since ${base}: config/env vars referenced in code but missing from deployment config or examples, breaking infra changes, health checks for new services, Dockerfile/CI changes that could fail the pipeline. pass=false only for release-breaking defects.` },
  { key: 'dependencies', prompt: `Audit dependency changes since ${base}: run the ecosystem's audit command (npm audit / pip-audit / cargo audit) if available and read lockfile diffs. pass=false for known critical/high CVEs in shipped dependencies; outdated-but-safe packages are warnings.` },
  { key: 'api', prompt: `Check API surface changes since ${base} for breaking changes: removed/renamed endpoints or fields, narrowed types, changed status codes or error shapes, OpenAPI spec drift from implementation. pass=false for unversioned breaking changes; additive changes are warnings.` },
]

const results = await parallel(CHECKS.map(c => () =>
  agent(c.prompt, { label: `check:${c.key}`, phase: 'Check', schema: CHECK })
    .then(r => ({ key: c.key, ...(r || { pass: false, blockers: [`${c.key} check did not complete`], warnings: [] }) }))
))

const checks = results.filter(Boolean)
const blockers = checks.flatMap(c => c.blockers.map(b => `[${c.key}] ${b}`))
const warnings = checks.flatMap(c => c.warnings.map(w => `[${c.key}] ${w}`))
const ready = checks.length === CHECKS.length && checks.every(c => c.pass)

log(ready ? 'Release gate: PASS' : `Release gate: BLOCKED — ${blockers.length} blocker(s)`)

return { ready, blockers, warnings, checks }
