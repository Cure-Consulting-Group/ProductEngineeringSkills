import { expect, mock, test } from 'claude-code/testing'

import {
  candidates,
  capped,
  checkCitations,
  discoverRoots,
  extractCitations,
  formatVerificationNotice,
  pathsInCommand,
  verifyCitation,
} from './cite'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('extractCitations: extracts bare and backtick citations', () => {
  const cites = extractCitations('See `src/index.ts:45` and also helpers/utils.py:120 for details.')
  expect(cites.map(c => `${c.path}:${c.line}`)).toEqual(['src/index.ts:45', 'helpers/utils.py:120'])
})

test('extractCitations: extracts ranges and markdown links', () => {
  const [range] = extractCitations('Look at `src/service.ts:10-25`.')
  expect(range.endLine).toBe(25)
  const [link] = extractCitations('Defined in [User](src/components/User.tsx#L88).')
  expect(link.path).toBe('src/components/User.tsx')
  expect(link.line).toBe(88)
})

test('extractCitations: never matches host.tld:port, URLs, versions or ssh remotes', () => {
  const text = [
    'Running on http://localhost:8080 and https://api.service.com:443/x.',
    'Point it at example.com:8080 or redis.internal.io:6379, db.prod.net:5432.',
    'Pages 1.88:1, clause C.18A:22, git@github.com:org/repo.git, https://h.dev/a/b.ts:3',
  ].join('\n')
  expect(extractCitations(text)).toEqual([])
})

test('extractCitations: a citation that ends a sentence', () => {
  expect(extractCitations('See lib/x.ts:3. Then a.md:1, b.py:2; c.go:4!').map(c => c.line)).toEqual([3, 1, 2, 4])
})

test('extractCitations: absolute, home and ./ paths', () => {
  const paths = extractCitations('/Users/x/a.ts:3, ~/notes/b.md:4 and ./c.py:5').map(c => c.path)
  expect(paths).toEqual(['/Users/x/a.ts', '~/notes/b.md', './c.py'])
})

test('candidates: roots first, then touched files by suffix, then the tracked index', () => {
  const ctx = { roots: ['/repo/sub', '/repo'], recent: ['/other/lib/x.ts'], index: ['/repo/pkg/lib/x.ts'] }
  expect(candidates('lib/x.ts', ctx)).toEqual(['/repo/sub/lib/x.ts', '/repo/lib/x.ts', '/other/lib/x.ts', '/repo/pkg/lib/x.ts'])
  expect(candidates('~/a.md', { ...ctx, home: '/h' })).toEqual(['/h/a.md'])
})

test('verifyCitation: range checks', () => {
  const c = { raw: 'a.ts:120', path: 'a.ts', line: 120 }
  expect(verifyCitation({ ...c, line: 25 }, true, 50)).toBeUndefined()
  expect(verifyCitation(c, false, 0)?.reason).toBe('file not found')
  expect(verifyCitation(c, true, 80)?.reason).toContain('exceeds file length (80 lines)')
})

const disk = (files: Record<string, number>, dirs: string[] = []) => ({
  lines: async (p: string) => files[p],
  exists: async (p: string) => p in files || dirs.includes(p),
})

test('checkCitations: a bare name found nowhere is unverified, not stale', async () => {
  const res = await checkCitations(extractCitations('`budget.ts:60`'), { roots: ['/r'], recent: [] }, disk({}))
  expect(res.stale.length).toBe(0)
  expect(res.unverified).toBe(1)
})

test('checkCitations: a path whose folder exists here but file does not is stale', async () => {
  const res = await checkCitations(extractCitations('`src/gone.ts:3`'), { roots: ['/r'], recent: [] }, disk({}, ['/r/src']))
  expect(res.stale[0]?.reason).toBe('file not found')
})

test('checkCitations: a path from another repository the session never touched is unverified', async () => {
  const res = await checkCitations(extractCitations('`apps/web/x.ts:3`'), { roots: ['/r'], recent: [] }, disk({}, ['/r/src']))
  expect(res.unverified).toBe(1)
})

test('checkCitations: a bare name is range-checked only against a copy the session touched', async () => {
  const res = await checkCitations(extractCitations('`STATE.md:321`'), { roots: ['/r'], recent: [] }, disk({ '/r/STATE.md': 54 }))
  expect(res.stale.length).toBe(0)
  const touched = await checkCitations(extractCitations('`STATE.md:321`'), { roots: ['/r'], recent: ['/r/STATE.md'] }, disk({ '/r/STATE.md': 54 }))
  expect(touched.stale[0]?.reason).toContain('exceeds')
})

test('discoverRoots: the nearest .git above each touched path', async () => {
  const roots = await discoverRoots(['/a/b/repo1/src/x.ts', '/a/b/repo2/lib'], disk({}, ['/a/b/repo1/.git', '/a/b/repo2/.git']))
  expect(roots).toEqual(['/a/b/repo2', '/a/b/repo1'])
})

test('pathsInCommand: absolute paths a shell command names', () => {
  expect(pathsInCommand('cd /Users/me/repo && git -C /Users/me/other log; cat "/Users/me/x.ts"')).toEqual([
    '/Users/me/repo',
    '/Users/me/other',
    '/Users/me/x.ts',
  ])
})

test('capped keeps the newest 200', () => {
  const out = capped(Array.from({ length: 190 }, (_, i) => i), Array.from({ length: 30 }, (_, i) => 190 + i))
  expect(out.length).toBe(200)
  expect(out[199]).toBe(219)
})

test('formatVerificationNotice: clean vs stale', () => {
  expect(formatVerificationNotice({ total: 2, valid: 2, unverified: 0, stale: [] })).toContain('none stale')
  const cite = { raw: 'a.ts:99', path: 'a.ts', line: 99 }
  const text = formatVerificationNotice({ total: 2, valid: 1, unverified: 0, stale: [{ citation: cite, reason: 'x' }] })
  expect(text).toContain('1 of 2')
  expect(text).toContain('a.ts:99')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

/** The engine beneath: a repo at /repo, the session rooted at /repo/sub. */
function world(on: any, files: Record<string, string>, dirs: string[] = []) {
  const toasts: string[] = []
  const reads: string[] = []
  const runs: string[][] = []
  mock.clock(on)
  mock.env(on, { HOME: '/home/me' })
  on('store.delete', () => ({ value: undefined }))
  on('command.register', (_$: any, e: any) => ({ value: { command: e.name } }))
  on('session.start', (_$: any, e: any) => ({ cwd: e.cwd }))
  on('session.root', () => ({ value: '/repo/sub' }))
  on('process.run', (_$: any, e: any) => {
    runs.push([...e.argv])
    const stdout = e.argv.includes('rev-parse') ? '/repo\n' : Object.keys(files).filter(f => f.startsWith('/repo/')).map(f => f.slice(6)).join('\0')
    return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('fs.exists', (_$: any, e: any) => ({ value: e.path in files || dirs.includes(e.path) }))
  on('fs.stat', (_$: any, e: any) => {
    if (!(e.path in files)) throw new Error('ENOENT')
    return { value: { kind: 'file', size: files[e.path].length, mtimeMs: 1, isLink: false } }
  })
  on('fs.read', (_$: any, e: any) => {
    reads.push(e.path)
    return { value: files[e.path] }
  })
  on('ui.toast', (_$: any, e: any) => (toasts.push(e.text), { value: undefined }))
  on('turn.complete', () => ({ text: '' }))
  on('tool.call', () => ({ result: { stdout: '', stderr: '', interrupted: false } }))
  return { toasts, reads, runs }
}

const answer = (text: string) =>
  ({ answer: text, durationMs: 1, isAborted: false, turnId: 't', reason: 'answer' }) as any

test('resolves against the git toplevel, not the session cwd, and toasts nothing when valid', async ($, on) => {
  const w = world(on, { '/repo/src/a.ts': 'one\ntwo\nthree' })
  await $.session.start({ cwd: '/repo/sub', surface: 'terminal', isInteractive: true })
  await $.turn.complete(answer('The handler is at `src/a.ts:2`.'))
  const r = await $.command.run({ command: 'cite-check' })
  expect(r.text).toContain('1 citation(s) checked · 1 valid · 0 stale')
  expect(w.toasts).toEqual([])
})

test('resolves a file the session read in another repository', async ($, on) => {
  world(on, { '/elsewhere/lib/x.ts': 'a\nb\nc' })
  await $.session.start({ cwd: '/repo/sub', surface: 'terminal', isInteractive: true })
  await $.tool.call({ tool: 'Read', file_path: '/elsewhere/lib/x.ts' } as any)
  await $.turn.complete(answer('See lib/x.ts:3.'))
  expect((await $.command.run({ command: 'cite-check' })).text).toContain('1 valid')
})

test('a stale citation is toasted and the answer text is left alone', async ($, on) => {
  const w = world(on, { '/repo/src/a.ts': 'one' })
  await $.session.start({ cwd: '/repo/sub', surface: 'terminal', isInteractive: true })
  const text = 'Broken at `src/a.ts:50`.'
  const r: any = await $.turn.complete(answer(text))
  expect(r.text).toBe('')
  expect(w.toasts[0]).toContain('src/a.ts:50')
  expect(w.toasts[0]).toContain('exceeds file length (1 lines)')
})

test('a model step is passed through untouched', async ($, on) => {
  world(on, { '/repo/src/a.ts': 'one' })
  on('turn.step', async function* (_$: any, e: any) {
    return { turnId: e.turnId, answer: 'Broken at `src/a.ts:50`.', toolUses: [] }
  })
  const stream: any = $.turn.step({ turnId: 't1', model: 'opus' } as any)
  let result: any
  while (true) {
    const step = await stream.next()
    if (step.done) {
      result = step.value
      break
    }
  }
  expect(result.answer).toBe('Broken at `src/a.ts:50`.')
})

test('an unchanged file is read once across answers, and git spawns at most twice', async ($, on) => {
  const w = world(on, { '/repo/src/a.ts': 'one\ntwo' })
  await $.session.start({ cwd: '/repo/sub', surface: 'terminal', isInteractive: true })
  await $.turn.complete(answer('`src/a.ts:1`'))
  await $.turn.complete(answer('`src/a.ts:2`'))
  await $.turn.complete(answer('`src/a.ts:1-2`'))
  expect(w.reads.filter(p => p === '/repo/src/a.ts').length).toBe(1)
  expect(w.runs.length).toBeLessThanOrEqual(2)
})

test('the stale list is session state, capped at 200', async ($, on) => {
  world(on, { '/repo/src/a.ts': 'one' })
  await $.session.start({ cwd: '/repo/sub', surface: 'terminal', isInteractive: true })
  for (let i = 0; i < 5; i++) {
    const cites = Array.from({ length: 50 }, (_, j) => `src/a.ts:${i * 100 + j + 2}`).join(' ')
    await $.turn.complete(answer(cites))
  }
  const text = (await $.command.run({ command: 'cite-check' })).text
  expect(text).toContain('250 stale')
  expect(text).toContain('last 5 of 200 kept')
})

test('a subagent answer is not checked', async ($, on) => {
  const w = world(on, { '/repo/src/a.ts': 'one' })
  await $.session.start({ cwd: '/repo/sub', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ ...answer('`src/a.ts:50`'), agentId: 'a1' })
  expect(w.toasts).toEqual([])
})

test('a Bash call spawns no process here (T72: at most 1 per Bash call across all mods)', async ($, on) => {
  const w = world(on, {})
  await $.session.start({ cwd: '/repo/sub', surface: 'terminal', isInteractive: true })
  for (const command of ['ls', 'cd /repo && git status', 'npm test']) await $.tool.call({ tool: 'Bash', command } as any)
  expect(w.runs.length).toBe(0)
})
