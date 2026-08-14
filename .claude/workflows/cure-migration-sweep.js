export const meta = {
  name: 'cure-migration-sweep',
  description: 'Codebase-wide mechanical migration: discover every call site, transform each, verify the suite still passes',
  whenToUse: 'Repo-wide mechanical changes: API renames, import migrations, deprecated-pattern replacement. REQUIRES args: {pattern: "what to find", instruction: "how to transform each site"}. Refuses without them.',
  phases: [
    { title: 'Discover', detail: 'find every affected file' },
    { title: 'Transform', detail: 'one agent per file' },
    { title: 'Verify', detail: 'tests + spot review' },
  ],
}

if (!args || !args.pattern || !args.instruction) {
  return { error: 'cure-migration-sweep requires args: {pattern, instruction}. Example: {pattern: "imports from lib/legacy-http", instruction: "replace with lib/http; the new client throws instead of returning null"}' }
}

const MAX_FILES = 40

const FILE_LIST = {
  type: 'object', required: ['files'],
  properties: { files: { type: 'array', items: { type: 'string' } } },
}
const TRANSFORM = {
  type: 'object', required: ['changed', 'summary'],
  properties: { changed: { type: 'boolean' }, summary: { type: 'string' } },
}
const VERIFY = {
  type: 'object', required: ['pass', 'detail'],
  properties: { pass: { type: 'boolean' }, detail: { type: 'string' } },
}

const found = await agent(
  `Find every file in this repository matching: ${args.pattern}. Search exhaustively (grep by content, glob by naming conventions). Return repo-relative paths only — no explanations.`,
  { label: 'discover', phase: 'Discover', schema: FILE_LIST },
)

const files = ((found && found.files) || []).slice(0, MAX_FILES)
if (!files.length) {
  return { files: [], summary: `No files matched: ${args.pattern}` }
}
if ((found.files || []).length > MAX_FILES) {
  log(`${found.files.length} files matched; sweeping first ${MAX_FILES} — re-run for the remainder (no silent full coverage)`)
}
log(`Transforming ${files.length} file(s)`)

const transforms = await pipeline(
  files,
  file => agent(
    `Apply this migration to ${file} and ONLY ${file}: ${args.instruction}\nMatch the file's existing style. If the file turns out not to need the change, change nothing and say so. Set changed accordingly.`,
    { label: `transform:${file}`, phase: 'Transform', schema: TRANSFORM },
  ).then(t => ({ file, ...(t || { changed: false, summary: 'transform agent did not complete' }) })),
)

const done = transforms.filter(Boolean)
const changed = done.filter(t => t.changed)

const verification = await agent(
  `A mechanical migration just changed ${changed.length} file(s): ${changed.map(t => t.file).join(', ')}.\nMigration: ${args.instruction}\n1. Run the project's test suite (and type check if available).\n2. Read 3 of the changed files and confirm the transformation is correct and complete, not just syntactically applied.\nReport pass=false with specifics if anything fails.`,
  { label: 'verify', phase: 'Verify', schema: VERIFY, effort: 'high' },
)

return {
  changed: changed.map(t => ({ file: t.file, summary: t.summary })),
  skipped: done.filter(t => !t.changed).map(t => t.file),
  verification,
}
