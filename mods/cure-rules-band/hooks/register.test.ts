import { expect, mock, test } from 'claude-code/testing'


import {
  formatBannerText,
  formatRulesReport,
  parseRulesJson,
  resolveRepoRules,
} from './banner'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('parseRulesJson: parses valid JSON object and array', () => {
  expect(parseRulesJson('{"rules": ["Rule A", "Rule B"]}')).toEqual(['Rule A', 'Rule B'])
  expect(parseRulesJson('["Rule 1", "Rule 2"]')).toEqual(['Rule 1', 'Rule 2'])
  expect(parseRulesJson('bad json')).toBeUndefined()
  expect(parseRulesJson('')).toBeUndefined()
})

test('resolveRepoRules: selects built-in repo rules', () => {
  const level5 = resolveRepoRules('Level5')
  expect(level5?.rules).toContain('PHI Data (GCP BAA)')
  expect(level5?.rules).toContain('Vertex AI Only')

  const tir = resolveRepoRules('initiated-recruiting')
  expect(tir?.rules).toContain('Minors Data')
  expect(tir?.rules).toContain('No New AI Vendors')

  const dz = resolveRepoRules('DistrictZero')
  expect(dz?.rules).toContain('No Cron')
})

test('resolveRepoRules: prioritizes custom config over defaults', () => {
  const custom = resolveRepoRules('Level5', '{"rules": ["Custom Rule 1", "Custom Rule 2"]}')
  expect(custom?.rules).toEqual(['Custom Rule 1', 'Custom Rule 2'])
})

test('resolveRepoRules: a repo with no rules gets nothing, not filler', () => {
  expect(resolveRepoRules('some-other-repo')).toBeNull()
  expect(resolveRepoRules(undefined)).toBeNull()
})

test('formatBannerText and formatRulesReport: format output cleanly', () => {
  const banner = formatBannerText('Level5', ['PHI', 'Vertex'])
  expect(banner).toBe('rules ● Level5 · PHI · Vertex')

  const report = formatRulesReport('Level5', ['PHI', 'Vertex'])
  expect(report).toContain('Active house rules for \'Level5\'')
  expect(report).toContain('• PHI')
  expect(report).toContain('• Vertex')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

const bandProps = { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 100, scroll: { offset: 0, bodyRows: 10 }, view: {} }

/** The engine beneath: the session rooted at `root`, git answering for `repo`. */
function world(on: any, root: { value: string }, repoOf: (dir: string) => string | undefined, config?: string) {
  const runs: string[][] = []
  on('session.root', () => ({ value: root.value }))
  on('session.start', (_$: any, e: any) => ({ cwd: e.cwd }))
  on('command.register', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('turn.complete', () => ({ text: '' }))
  on('fs.exists', (_$: any, e: any) => ({ value: config !== undefined && e.path.endsWith('/.cure/rules.json') }))
  on('fs.read', () => ({ value: config }))
  on('process.run', (_$: any, e: any) => {
    runs.push([...e.argv])
    const repo = repoOf(e.argv[2])
    return repo
      ? { value: { exitCode: 0, stdout: `/code/${repo}/.git\n${e.argv[2]}\n`, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
      : { value: { exitCode: 128, stdout: '', stderr: 'not a git repository', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('ui.render', ($$: any, e: any) => h($$.ui.resolve(e).Box, null) as never)
  return runs
}

const turn = { answer: 'ok', durationMs: 1, isAborted: false, turnId: 't', reason: 'answer' } as any

async function band($: any) {
  const ui = await $.ui.mount({ plugin: 'cure-rules-band', surface: 'terminal', component: 'AbovePrompt', props: bandProps as never })
  const text = (await ui.findAll({ type: 'Text' })).map((t: any) => t.text).join('')
  await ui.unmount()
  return text
}

test('/rules names the repo the session root is in, from a worktree too', async ($, on) => {
  world(on, { value: '/code/wt/level5-feature' }, () => 'Level5')
  await $.session.start({ cwd: '/code/wt/level5-feature', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'rules' })
  expect(r.text).toContain("Active house rules for 'Level5'")
  expect(r.text).toContain('PHI Data (GCP BAA)')
})

test('/rules reads .cure/rules.json from the repo root', async ($, on) => {
  world(on, { value: '/code/MyRepo' }, () => 'MyRepo', '{"rules": ["Custom Enforced Rule"]}')
  await $.session.start({ cwd: '/code/MyRepo', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'rules' })
  expect(r.text).toContain('Custom Enforced Rule')
})

test('a repo with no rules draws nothing', async ($, on) => {
  world(on, { value: '/code/plain' }, () => 'plain')
  await $.session.start({ cwd: '/code/plain', surface: 'terminal', isInteractive: true })
  expect(await band($)).toBe('')
  expect((await $.command.run({ command: 'rules' })).text).toMatch(/no house rules/)
})

test('drawing spawns no git; git runs once per root folder', async ($, on) => {
  const root = { value: '/code/Level5' }
  const runs = world(on, root, dir => (dir.includes('Level5') ? 'Level5' : 'DistrictZero'))
  await $.session.start({ cwd: root.value, surface: 'terminal', isInteractive: true })
  for (let i = 0; i < 5; i++) expect(await band($)).toContain('rules ● Level5')
  await $.turn.complete(turn)
  await $.turn.complete(turn)
  expect(runs.length).toBe(1)
  root.value = '/code/DistrictZero'
  await $.turn.complete(turn)
  expect(await band($)).toContain('rules ● DistrictZero')
  expect(runs.length).toBe(2)
})

test('/rules hide dismisses the band', async ($, on) => {
  world(on, { value: '/code/Level5' }, () => 'Level5')
  await $.session.start({ cwd: '/code/Level5', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'rules', args: 'hide' } as any)
  expect(await band($)).toBe('')
})
