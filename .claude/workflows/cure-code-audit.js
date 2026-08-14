export const meta = {
  name: 'cure-code-audit',
  description: 'Multi-dimension code audit (security, architecture, performance, accessibility) with adversarial verification of every finding',
  whenToUse: 'Deep audit of a repo or subsystem against Cure standards. Pass args: {scope: "src/payments"} to narrow; defaults to the working tree.',
  phases: [
    { title: 'Audit', detail: 'one reviewer per dimension' },
    { title: 'Verify', detail: 'adversarial check per finding' },
    { title: 'Synthesize', detail: 'ranked report' },
  ],
}

const FINDINGS = {
  type: 'object', required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object', required: ['file', 'line', 'severity', 'title', 'detail'],
        properties: {
          file: { type: 'string' }, line: { type: 'integer' },
          severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
          title: { type: 'string' }, detail: { type: 'string' },
        },
      },
    },
  },
}
const VERDICT = {
  type: 'object', required: ['real', 'reason'],
  properties: { real: { type: 'boolean' }, reason: { type: 'string' } },
}

const scope = (args && args.scope) || 'the repository working tree'
const MAX_FINDINGS_PER_DIMENSION = 12

const DIMENSIONS = [
  { key: 'security', prompt: `Audit ${scope} for security defects against Cure standards: unvalidated inputs, injection (SQL/command/prompt), hardcoded secrets, missing authz checks, unsafe deserialization, permissive CORS/security rules. Report only defects you can anchor to a specific file and line.` },
  { key: 'architecture', prompt: `Audit ${scope} for architecture violations against Cure Clean Architecture standards: framework imports in domain layers, business logic in presentation, missing repository pattern, circular dependencies, god modules. Report only violations anchored to a specific file and line.` },
  { key: 'performance', prompt: `Audit ${scope} for performance defects: N+1 queries, unbounded queries or loops over unbounded data, missing indexes implied by query patterns, sync I/O on hot paths, unnecessary re-renders or recomputation. Report only defects anchored to a specific file and line.` },
  { key: 'accessibility', prompt: `Audit UI code in ${scope} for WCAG 2.2 violations: missing labels/alt text, keyboard traps, contrast-hostile hardcoded colors, missing focus management, touch targets under 44px. If there is no UI code in scope, return an empty findings list. Anchor every finding to a file and line.` },
]

const results = await pipeline(
  DIMENSIONS,
  d => agent(d.prompt, { label: `audit:${d.key}`, phase: 'Audit', schema: FINDINGS }),
  (review, d) => {
    const found = (review && review.findings) || []
    if (found.length > MAX_FINDINGS_PER_DIMENSION) {
      log(`${d.key}: ${found.length} findings, verifying top ${MAX_FINDINGS_PER_DIMENSION} by severity (${found.length - MAX_FINDINGS_PER_DIMENSION} dropped — re-run scoped if this dimension is hot)`)
    }
    const order = { critical: 0, high: 1, medium: 2, low: 3 }
    const kept = found.slice().sort((a, b) => order[a.severity] - order[b.severity]).slice(0, MAX_FINDINGS_PER_DIMENSION)
    return parallel(kept.map(f => () =>
      agent(
        `Adversarially verify this ${d.key} finding — try to REFUTE it by reading the actual code at ${f.file}:${f.line} and its callers. Finding: "${f.title}" — ${f.detail}. If the code already handles it, it is unreachable, or the claim misreads the code, it is not real. Default to real=false when uncertain.`,
        { label: `verify:${f.file}:${f.line}`, phase: 'Verify', schema: VERDICT, effort: 'high' },
      ).then(v => ({ ...f, dimension: d.key, verdict: v }))
    ))
  },
)

const confirmed = results.filter(Boolean).flat().filter(Boolean).filter(f => f.verdict && f.verdict.real)
log(`${confirmed.length} findings confirmed across ${DIMENSIONS.length} dimensions`)

if (confirmed.length === 0) {
  return { confirmed: [], report: `Audit of ${scope}: no findings survived adversarial verification.` }
}

const report = await agent(
  `Write a Cure audit report (severity-ranked, remediation with effort estimates per finding) from these verified findings:\n${JSON.stringify(confirmed, null, 2)}`,
  { label: 'report', phase: 'Synthesize' },
)

return { confirmed, report }
