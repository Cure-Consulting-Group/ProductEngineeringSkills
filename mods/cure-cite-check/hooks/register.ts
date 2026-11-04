import type { $ as Engine, Register } from 'claude-code'

import type { CiteStats } from '../types'
import {
  capped,
  checkCitations,
  discoverRoots,
  extractCitations,
  formatVerificationNotice,
  pathsInCommand,
  type Probe,
} from './cite'

type $ = Engine

/** 0.1.0 kept its counters here, machine-global and unbounded. */
const LEGACY_STORE_KEY = 'cure-cite-check-stats'
const STATS = { plugin: 'cure-cite-check', key: 'stats' } as const
const RECENT_STALE = { plugin: 'cure-cite-check', key: 'recentStale' } as const
const RECENT_PATHS = { plugin: 'cure-cite-check', key: 'recentPaths' } as const
const NO_STATS: CiteStats = { checked: 0, valid: 0, stale: 0, unverified: 0 }
const CAP = 200
const INDEX_TTL_MS = 5 * 60_000
/** `$.fs.read` refuses past 4 MiB; a larger file is taken as long enough. */
const READ_LIMIT = 4 * 1024 * 1024

const TRACKED_TOOLS = new Set(['Read', 'Edit', 'Write', 'MultiEdit', 'NotebookEdit', 'Grep', 'Glob', 'Bash'])

/** Paths a tool call names, absolute only: what the resolver may search later. */
function pathsOf(e: Record<string, unknown>): string[] {
  const out: string[] = []
  for (const key of ['file_path', 'notebook_path', 'path']) {
    const v = e[key]
    if (typeof v === 'string' && v.startsWith('/')) out.push(v)
  }
  if (typeof e.command === 'string') out.push(...pathsInCommand(e.command))
  return out
}

// Module caches: rebuilt after a reload, never a subprocess per tool call.
const lineCache = new Map<string, { mtimeMs: number; size: number; lines: number }>()
const topCache = new Map<string, string | undefined>()
const gitDirs = new Map<string, boolean>()
let index: { top: string; at: number; files: string[] } | undefined

function probe($: $): Probe {
  return {
  exists: path => $.fs.exists(path).catch(() => false),
  lines: async path => {
    const stat = await $.fs.stat(path).catch(() => undefined)
    if (!stat || stat.kind !== 'file') return undefined
    if (stat.size > READ_LIMIT) return Number.MAX_SAFE_INTEGER
    const hit = lineCache.get(path)
    if (hit && hit.mtimeMs === stat.mtimeMs && hit.size === stat.size) return hit.lines
    const text = await $.fs.read(path).catch(() => undefined)
    if (typeof text !== 'string') return undefined
    const lines = text.split('\n').length
    lineCache.set(path, { mtimeMs: stat.mtimeMs, size: stat.size, lines })
    if (lineCache.size > 500) lineCache.delete(lineCache.keys().next().value as string)
    return lines
  },
  }
}

async function toplevel($: $, dir: string): Promise<string | undefined> {
  if (!topCache.has(dir)) {
    const r = await $.process.run(['git', '-C', dir, 'rev-parse', '--show-toplevel'], { timeoutMs: 5000 }).catch(() => undefined)
    topCache.set(dir, r && r.exitCode === 0 ? r.stdout.trim() : undefined)
  }
  return topCache.get(dir)
}

async function trackedFiles($: $, top: string): Promise<string[]> {
  const now = await $.clock.now()
  if (index && index.top === top && now - index.at < INDEX_TTL_MS) return index.files
  const r = await $.process.run(['git', '-C', top, 'ls-files', '-z'], { timeoutMs: 5000 }).catch(() => undefined)
  const files = r && r.exitCode === 0 ? r.stdout.split('\0').filter(Boolean).map(f => `${top}/${f}`) : []
  index = { top, at: now, files }
  return files
}

export const register: Register = (on, options) => {
  lineCache.clear()
  topCache.clear()
  gitDirs.clear()
  index = undefined

  on('session.start', async ($, e, next) => {
    await $.store.delete(LEGACY_STORE_KEY).catch(() => undefined)
    await $.command.register({
      name: 'cite-check',
      description: 'Show how many file:line citations this session checked and which were stale',
    })
    return next(e)
  })

  on('command.run', { command: 'cite-check' }, async $ => {
    const { value: s = NO_STATS } = await $.state.get(STATS)
    const { value: stale = [] } = await $.state.get(RECENT_STALE)
    if (s.checked === 0) return { text: 'cure-cite-check: No code citations checked in this session yet.' }
    const lines = [
      `cure-cite-check: ${s.checked} citation(s) checked · ${s.valid} valid · ${s.stale} stale · ${s.unverified} not found in this session's repos (not flagged)`,
    ]
    if (stale.length > 0) {
      lines.push(`Stale citations (last 5 of ${stale.length} kept):`)
      for (const x of stale.slice(-5)) lines.push(`  • ${x.path}:${x.line} — ${x.reason}`)
    }
    return { text: lines.join('\n') }
  })

  // Remember what the session touched; no git, no read, no await on the tool itself.
  on('tool.call', async ($, e, next) => {
    if (TRACKED_TOOLS.has(String(e.tool))) {
      const add = pathsOf(e as unknown as Record<string, unknown>)
      if (add.length > 0) {
        const { value = [] } = await $.state.get(RECENT_PATHS)
        await $.state.set(RECENT_PATHS, capped(value.filter(p => !add.includes(p)), add, CAP))
      }
    }
    return next(e)
  })

  // Once per main-loop answer, never per model step, and the answer is never rewritten.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined || !e.answer) return result
    const citations = extractCitations(e.answer)
    if (citations.length === 0) return result

    const p = probe($)
    const root = await $.session.root()
    const top = await toplevel($, root)
    const { value: recent = [] } = await $.state.get(RECENT_PATHS)
    const touched = await discoverRoots(recent, p, gitDirs)
    const roots = [...new Set([root, top, ...touched].filter((r): r is string => !!r))]
    const home = await $.env.get('HOME').catch(() => undefined)
    const files = top ? await trackedFiles($, top) : []
    const res = await checkCitations(citations, { roots, recent, home, index: files }, p)

    const { value: s = NO_STATS } = await $.state.get(STATS)
    await $.state.set(STATS, {
      checked: s.checked + res.total,
      valid: s.valid + res.valid,
      stale: s.stale + res.stale.length,
      unverified: s.unverified + res.unverified,
    })
    if (res.stale.length > 0) {
      const { value: prior = [] } = await $.state.get(RECENT_STALE)
      const add = res.stale.map(x => ({ path: x.citation.path, line: x.citation.line, reason: x.reason }))
      await $.state.set(RECENT_STALE, capped(prior, add, CAP))
      const notice = formatVerificationNotice(res)
      $.ui.toast(notice)
      if (options.noteToClaude === true) {
        await $.session
          .append({ message: { type: 'user', content: [{ type: 'text', text: `[${notice}. Re-check these before relying on them.]` }] } })
          .catch(() => undefined)
      }
    }
    return result
  })
}
