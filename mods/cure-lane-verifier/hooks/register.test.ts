import { expect, test } from 'claude-code/testing'

import { countDirty, extractClaims, formatVerdict, isEmptyCompletion, type Evidence } from './claims'

// ── claims, as pure functions ──────────────────────────────────────────────

test('extractClaims reads worktree paths, lane branches and a completion claim', async () => {
  const c = extractClaims(
    'STATUS: complete. Worktree /private/tmp/run/wt/bw-tests, branch `lane/bw-tests`. All 42 tests pass. GAPS: none',
  )
  expect(c.paths).toEqual(['/private/tmp/run/wt/bw-tests'])
  expect(c.branches).toEqual(['lane/bw-tests'])
  expect(c.claimsDone).toBe(true)
})

test('a file path is checked at its directory, trailing punctuation dropped', async () => {
  expect(extractClaims('Wrote /Users/r/repo/src/app.ts, and /Users/r/repo/README.md.').paths).toEqual(['/Users/r/repo/src', '/Users/r/repo'])
})

test('main is never a claimed branch; a report with no completion word claims nothing done', async () => {
  const c = extractClaims('Compared against branch `main`. Still investigating the failure on branch `fix/x`.')
  expect(c.branches).toEqual(['fix/x'])
  expect(c.claimsDone).toBe(false)
  expect(extractClaims('the task is incomplete').claimsDone).toBe(false)
})

const ev = (over: Partial<Evidence>): Evidence => ({ target: 't', ahead: 0, shortstat: '', dirty: 0, base: 'origin/main', ...over })

test('an empty completion is flagged only when every answered target is empty', async () => {
  expect(isEmptyCompletion(true, [ev({})])).toBe(true)
  expect(isEmptyCompletion(true, [ev({}), ev({ ahead: 1, shortstat: '1 file changed' })])).toBe(false)
  expect(isEmptyCompletion(true, [ev({ dirty: 3 })])).toBe(false)
  expect(isEmptyCompletion(false, [ev({})])).toBe(false)
  expect(isEmptyCompletion(true, [ev({ error: 'no branch' })])).toBe(false)
})

test('an empty named branch is a contradiction even when a named checkout is dirty', async () => {
  // Found live: the report named the main checkout (dirty with unrelated work) and an empty lane branch.
  expect(isEmptyCompletion(true, [ev({ kind: 'path', dirty: 1 }), ev({ kind: 'branch', target: 'lane/x' })])).toBe(true)
  expect(isEmptyCompletion(true, [ev({ kind: 'path', dirty: 1 }), ev({ kind: 'branch', ahead: 2, shortstat: '1 file changed' })])).toBe(false)
})

test('formatVerdict leads with EMPTY COMPLETION when the claim has nothing behind it', async () => {
  const c = extractClaims('complete; branch `lane/x`')
  expect(formatVerdict(c, [ev({ target: 'lane/x' })])).toMatch(/^cure-lane-verifier: EMPTY COMPLETION/)
  expect(formatVerdict(c, [ev({ target: 'lane/x', ahead: 2, shortstat: '3 files changed, 40 insertions(+)' })])).toMatch(
    /lane\/x: 2 commit\(s\) ahead of origin\/main; 3 files changed/,
  )
  expect(formatVerdict(c, [])).toBe('')
})

test('countDirty counts porcelain lines', async () => {
  expect(countDirty(' M a.ts\n?? b.ts\n')).toBe(2)
  expect(countDirty('')).toBe(0)
})

// ── the hook, end to end ───────────────────────────────────────────────────

/** A fake git: `git -C <dir> <args...>` answered from a table keyed by args. */
const fakeGit = (on: any, answers: Record<string, string>) => {
  on('process.run', (_$: any, e: any) => {
    const argv: string[] = e.argv ?? e.args ?? e
    const key = argv.slice(3).join(' ')
    const stdout = answers[key]
    return { value: stdout === undefined ? { exitCode: 1, stdout: '', stderr: `unstubbed: ${key}` } : { exitCode: 0, stdout, stderr: '' } }
  })
  on('fs.exists', () => ({ value: true }))
  on('session.root', () => ({ value: '/Users/r/repo' }))
}

test('a foreground Agent report with an empty branch gets an EMPTY COMPLETION note', async ($, on) => {
  fakeGit(on, {
    'rev-parse --verify --quiet lane/bw-tests': 'abc\n',
    'rev-parse --abbrev-ref origin/HEAD': 'origin/main\n',
    'rev-list --count origin/main..lane/bw-tests': '0\n',
    'diff --shortstat origin/main...lane/bw-tests': '',
  })
  on('tool.call', () => ({ result: 'ok', text: 'STATUS: complete on branch `lane/bw-tests`. 42 tests pass. GAPS: none' }))
  const r = await $.tool.call({ tool: 'Agent', prompt: 'do it', description: 'lane' })
  expect(r.context?.join('\n')).toMatch(/EMPTY COMPLETION/)
  expect(r.context?.join('\n')).toMatch(/lane\/bw-tests: 0 commit/)
})

test('a report whose branch has commits gets the evidence, not an alarm', async ($, on) => {
  fakeGit(on, {
    'rev-parse --verify --quiet lane/ok': 'abc\n',
    'rev-parse --abbrev-ref origin/HEAD': 'origin/main\n',
    'rev-list --count origin/main..lane/ok': '3\n',
    'diff --shortstat origin/main...lane/ok': ' 4 files changed, 120 insertions(+), 3 deletions(-)\n',
  })
  on('tool.call', () => ({ result: 'ok', text: 'Done. Branch `lane/ok`.' }))
  const r = await $.tool.call({ tool: 'Agent', prompt: 'do it', description: 'lane' })
  const note = r.context?.join('\n') ?? ''
  expect(note).not.toMatch(/EMPTY COMPLETION/)
  expect(note).toMatch(/lane\/ok: 3 commit\(s\) ahead of origin\/main; 4 files changed/)
})

test('a report naming nothing checkable passes through unchanged', async ($, on) => {
  fakeGit(on, {})
  on('tool.call', () => ({ result: 'ok', text: 'Here is a summary of the docs.' }))
  const r = await $.tool.call({ tool: 'Agent', prompt: 'summarise', description: 'read' })
  expect(r.context).toBeUndefined()
})

test('other tools are not touched', async ($, on) => {
  fakeGit(on, {})
  on('tool.call', () => ({ result: 'ok', text: 'complete on branch `lane/x`' }))
  const r = await $.tool.call({ tool: 'Bash', command: 'echo hi' })
  expect(r.context).toBeUndefined()
})

test('a branch git does not know is reported as unverifiable, not as empty', async ($, on) => {
  fakeGit(on, { 'rev-parse --abbrev-ref origin/HEAD': 'origin/main\n' })
  on('tool.call', () => ({ result: 'ok', text: 'complete on branch `lane/ghost`' }))
  const r = await $.tool.call({ tool: 'Agent', prompt: 'x', description: 'x' })
  const note = r.context?.join('\n') ?? ''
  expect(note).toMatch(/lane\/ghost: could not verify/)
  expect(note).not.toMatch(/EMPTY COMPLETION/)
})

test('a background hand-back delivered as an engine attachment gets the note appended', async ($, on) => {
  fakeGit(on, {
    'rev-parse --verify --quiet lane/bg': 'abc\n',
    'rev-parse --abbrev-ref origin/HEAD': 'origin/main\n',
    'rev-list --count origin/main..lane/bg': '0\n',
    'diff --shortstat origin/main...lane/bg': '',
  })
  on('prompt.attachment', (_$: any, e: any) => ({ text: e.text }))
  const r = await $.prompt.attachment({
    type: 'queued_command',
    text: '[Subagent hand-back] The report follows: STATUS complete, branch `lane/bg`.',
    origin: { kind: 'engine' },
  })
  expect(r.text).toMatch(/EMPTY COMPLETION/)
  expect(r.text).toMatch(/^\[Subagent hand-back\]/)
})

test('an ordinary engine attachment is left alone', async ($, on) => {
  fakeGit(on, {})
  on('prompt.attachment', (_$: any, e: any) => ({ text: e.text }))
  const r = await $.prompt.attachment({ type: 'todo_reminder', text: 'You are on branch `lane/x`; complete the todo list.', origin: { kind: 'engine' } })
  expect(r.text).toBe('You are on branch `lane/x`; complete the todo list.')
})
