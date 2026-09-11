#!/usr/bin/env node
/**
 * CPA competency benchmark runner.
 *
 * Usage:
 *   node run.mjs list [--set reg-core] [--area QBI]   # exam mode: questions, no answers
 *   node run.mjs template [--set ...] > answers.json  # blank answer file
 *   node run.mjs score answers.json                   # grade and report
 *   node run.mjs key [--set ...]                      # answer key with citations
 *   node run.mjs stats                                # coverage summary
 *   node run.mjs sources                              # where questions are loaded from
 *
 * Answer file format:  { "REG-001": "B", "REG-008": 14129.55, ... }
 *
 * Local question overlays
 * -----------------------
 * The bundled sets are portable: doctrine and law, no client facts. A consuming
 * project adds its own applied sets — real entities, real figures — without
 * copying them into this shared library, by any of:
 *
 *   .claude/tax-benchmark/questions/   auto-discovered under the working directory
 *   CPA_BENCHMARK_QUESTIONS=dir1:dir2  colon-separated, absolute or relative
 *   --questions <dir>                  repeatable flag, wins over both
 *
 * Overlay files use the same schema as questions/*.json. An overlay question
 * whose id collides with a bundled one replaces it, so a project can correct a
 * bundled question locally. `sources` prints what actually loaded.
 */

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const QDIR = join(HERE, 'questions');
const PASS_MARK = 75; // CPA exam scaled passing score

function arg(name) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 ? process.argv[i + 1] : undefined;
}

/** Every --questions flag, in order. */
function argAll(name) {
  const out = [];
  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i] === `--${name}` && process.argv[i + 1]) out.push(process.argv[i + 1]);
  }
  return out;
}

/**
 * Question directories, lowest precedence first: the bundled portable sets,
 * then an auto-discovered project overlay, then the environment, then flags.
 * Later directories override earlier ones on question id.
 */
let _dirs = null;
function questionDirs() {
  if (_dirs) return _dirs;
  const dirs = [QDIR];
  const auto = join(process.cwd(), '.claude', 'tax-benchmark', 'questions');
  if (auto !== QDIR && existsSync(auto)) dirs.push(auto);
  for (const d of (process.env.CPA_BENCHMARK_QUESTIONS || '').split(':')) {
    if (d.trim()) dirs.push(resolve(d.trim()));
  }
  for (const d of argAll('questions')) dirs.push(resolve(d));

  const seen = new Set();
  _dirs = dirs.filter((d) => {
    if (seen.has(d)) return false;
    seen.add(d);
    if (existsSync(d)) return true;
    console.error(`warning: question directory not found, skipping: ${d}`);
    return false;
  });
  return _dirs;
}

function loadSets(filterSet) {
  const sets = [];
  for (const dir of questionDirs()) {
    for (const f of readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
      const s = JSON.parse(readFileSync(join(dir, f), 'utf8'));
      if (filterSet && s.set !== filterSet) continue;
      sets.push({ ...s, source: dir === QDIR ? 'bundled' : dir });
    }
  }
  return sets;
}

function allQuestions(opts = {}) {
  const byId = new Map();
  for (const s of loadSets(opts.set)) {
    for (const q of s.questions) {
      if (opts.area && !q.area.toLowerCase().includes(opts.area.toLowerCase())) continue;
      // later sources win, so a project overlay can correct a bundled question
      byId.set(q.id, { ...q, set: s.set, setTitle: s.title, taxYear: s.taxYear, source: s.source });
    }
  }
  return [...byId.values()];
}

/** Grade one answer. Returns { correct, note }. */
function grade(q, given) {
  if (given === undefined || given === null || given === '') {
    return { correct: false, note: 'no answer' };
  }
  if (q.type === 'numeric') {
    const n = typeof given === 'number' ? given : Number(String(given).replace(/[$,\s]/g, ''));
    if (Number.isNaN(n)) return { correct: false, note: `not numeric: ${given}` };
    const tol = q.tolerance ?? 0.01;
    const ok = Math.abs(n - q.answer) <= tol;
    return { correct: ok, note: ok ? '' : `got ${n}, expected ${q.answer} (±${tol})` };
  }
  if (q.type === 'mcq') {
    const ok = String(given).trim().toUpperCase() === String(q.answer).toUpperCase();
    return { correct: ok, note: ok ? '' : `got ${given}, expected ${q.answer}` };
  }
  return { correct: null, note: 'short answer — requires manual grading' };
}

function pct(n, d) {
  return d === 0 ? 0 : Math.round((n / d) * 1000) / 10;
}

function bar(p) {
  const filled = Math.round(p / 5);
  return '█'.repeat(filled) + '░'.repeat(20 - filled);
}

const cmd = process.argv[2] || 'help';

if (cmd === 'list') {
  const qs = allQuestions({ set: arg('set'), area: arg('area') });
  console.log(`# CPA Benchmark — ${qs.length} questions\n`);
  for (const q of qs) {
    console.log(`## ${q.id}  [${q.area} · ${q.type} · ${q.difficulty}]`);
    console.log(q.q);
    if (q.choices) {
      for (const [k, v] of Object.entries(q.choices)) console.log(`   ${k}. ${v}`);
    }
    console.log('');
  }
  console.log(`Answer with a JSON object mapping id -> answer. Template: node run.mjs template`);
}

else if (cmd === 'template') {
  const qs = allQuestions({ set: arg('set'), area: arg('area') });
  console.log(JSON.stringify(Object.fromEntries(qs.map((q) => [q.id, ''])), null, 2));
}

else if (cmd === 'key') {
  const qs = allQuestions({ set: arg('set'), area: arg('area') });
  for (const q of qs) {
    console.log(`${q.id}  →  ${q.answer}${q.tolerance ? ` (±${q.tolerance})` : ''}`);
    console.log(`    cite: ${q.cite}`);
    console.log(`    why:  ${q.why}\n`);
  }
}

else if (cmd === 'stats') {
  const qs = allQuestions();
  const by = (fn) => qs.reduce((a, q) => ((a[fn(q)] = (a[fn(q)] || 0) + 1), a), {});
  console.log(`Total questions: ${qs.length}\n`);
  for (const [label, counts] of [
    ['By set', by((q) => q.set)],
    ['By area', by((q) => q.area)],
    ['By type', by((q) => q.type)],
    ['By difficulty', by((q) => q.difficulty)],
  ]) {
    console.log(label);
    for (const [k, v] of Object.entries(counts).sort((a, b) => b[1] - a[1])) {
      console.log(`  ${String(v).padStart(3)}  ${k}`);
    }
    console.log('');
  }
}

else if (cmd === 'sources') {
  const sets = loadSets();
  console.log('Question directories (later overrides earlier on question id)\n');
  for (const d of questionDirs()) console.log(`  ${d === QDIR ? `${d}   [bundled]` : d}`);
  console.log('\nSets loaded\n');
  for (const s of sets) {
    console.log(`  ${String(s.questions.length).padStart(3)}  ${s.set.padEnd(26)} ${s.source === 'bundled' ? 'bundled' : s.source}`);
  }
  console.log(`\n  ${String(allQuestions().length).padStart(3)}  total after id resolution`);
}

else if (cmd === 'score') {
  const file = process.argv[3];
  if (!file) {
    console.error('usage: node run.mjs score <answers.json>');
    process.exit(2);
  }
  const given = JSON.parse(readFileSync(file, 'utf8'));
  const qs = allQuestions();
  const results = qs.map((q) => ({ q, ...grade(q, given[q.id]) }));

  const auto = results.filter((r) => r.correct !== null);
  const manual = results.filter((r) => r.correct === null);
  const right = auto.filter((r) => r.correct).length;
  const score = pct(right, auto.length);

  console.log('═'.repeat(64));
  console.log(`  CPA BENCHMARK RESULT     ${right}/${auto.length}   ${score}%   ${score >= PASS_MARK ? 'PASS' : 'FAIL'} (mark ${PASS_MARK})`);
  console.log('═'.repeat(64));

  const groups = {};
  for (const r of auto) (groups[r.q.area] ||= []).push(r);
  console.log('\nBy area');
  for (const [area, rs] of Object.entries(groups).sort()) {
    const n = rs.filter((r) => r.correct).length;
    const p = pct(n, rs.length);
    console.log(`  ${bar(p)} ${String(p).padStart(5)}%  ${String(n)}/${rs.length}  ${area}`);
  }

  const byDiff = {};
  for (const r of auto) (byDiff[r.q.difficulty] ||= []).push(r);
  console.log('\nBy difficulty');
  for (const d of ['remember', 'application', 'analysis']) {
    const rs = byDiff[d] || [];
    if (!rs.length) continue;
    const n = rs.filter((r) => r.correct).length;
    console.log(`  ${String(pct(n, rs.length)).padStart(5)}%  ${n}/${rs.length}  ${d}`);
  }

  const missed = auto.filter((r) => !r.correct);
  if (missed.length) {
    console.log(`\nMissed (${missed.length}) — remediation targets`);
    for (const r of missed) {
      console.log(`\n  ✗ ${r.q.id}  [${r.q.area}]  ${r.note}`);
      console.log(`    ${r.q.q.slice(0, 100)}${r.q.q.length > 100 ? '…' : ''}`);
      console.log(`    cite: ${r.q.cite}`);
      console.log(`    why:  ${r.q.why}`);
    }
  }

  if (manual.length) {
    console.log(`\nRequires manual grading: ${manual.map((r) => r.q.id).join(', ')}`);
  }

  process.exit(score >= PASS_MARK ? 0 : 1);
}

else {
  console.log(readFileSync(new URL(import.meta.url), 'utf8').split('*/')[0].split('/**')[1].trim());
}
