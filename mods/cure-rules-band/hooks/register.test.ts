import { expect, mock, test } from 'claude-code/testing'

const h = (type: any, props: any, ...children: any[]) => ({ type, props, children })

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
  expect(level5.rules).toContain('PHI Data (GCP BAA)')
  expect(level5.rules).toContain('Vertex AI Only')

  const tir = resolveRepoRules('initiated-recruiting')
  expect(tir.rules).toContain('Minors Data')
  expect(tir.rules).toContain('No New AI Vendors')

  const dz = resolveRepoRules('DistrictZero')
  expect(dz.rules).toContain('No Cron')
})

test('resolveRepoRules: prioritizes custom config over defaults', () => {
  const custom = resolveRepoRules('Level5', '{"rules": ["Custom Rule 1", "Custom Rule 2"]}')
  expect(custom.rules).toEqual(['Custom Rule 1', 'Custom Rule 2'])
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

test('command: /rules returns active rules for repository', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: false }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/path/Level5\n', stderr: '' } }))

  const r = await $.command.run({ command: 'rules' })
  expect(r.text).toContain('Active house rules for \'Level5\'')
  expect(r.text).toContain('PHI Data (GCP BAA)')
})

test('command: /rules reads .cure/rules.json when present', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: '{"rules": ["Custom Enforced Rule"]}' }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/path/MyRepo\n', stderr: '' } }))

  const r = await $.command.run({ command: 'rules' })
  expect(r.text).toContain('Active house rules for \'MyRepo\'')
  expect(r.text).toContain('Custom Enforced Rule')
})

test('ui.render: mounts AbovePrompt banner', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: false }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/path/Level5\n', stderr: '' } }))
  on('ui.render', ($$, e) => h($$.ui.resolve(e).Box, null) as never)

  const ui = await $.ui.mount({
    plugin: 'cure-rules-band',
    surface: 'terminal',
    component: 'AbovePrompt',
    props: bandProps as never,
  })

  expect(ui).toBeDefined()
  await ui.unmount()
})
