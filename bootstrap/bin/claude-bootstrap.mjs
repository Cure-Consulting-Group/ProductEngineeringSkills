#!/usr/bin/env node
import { parseArgs } from "node:util";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { createManifest, validateManifest } from "../src/manifest/index.mjs";
import { detectStack } from "../src/detect/stack.mjs";
import { buildPlan, applyPlan, readManifest, summarizePlan, MANIFEST_FILENAME } from "../src/apply/index.mjs";
import { resolveSkillsSource } from "../src/vendor/index.mjs";
import { diagnose, summarizeDiagnose } from "../src/diagnose/doctor.mjs";
import { buildInventory, formatInventoryCsv } from "../src/diagnose/inventory.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = JSON.parse(readFileSync(resolve(here, "../package.json"), "utf8"));

const HELP = `claude-bootstrap v${pkg.version}

Usage:
  claude-bootstrap init      [options]   create claude.manifest.json + scaffold managed files
  claude-bootstrap apply     [options]   re-render templates against existing manifest
  claude-bootstrap doctor    [options]   audit a project for drift; nonzero exit on findings
  claude-bootstrap inventory [paths...]  read manifests across many projects, emit CSV
  claude-bootstrap version               print version
  claude-bootstrap help                  print this help

Options:
  --cwd <path>             target project root (default: process.cwd())
  --skills-version <ver>   skills repo version to pin (init only; required for init)
  --skills-sha <sha>       skills repo commit (init, optional)
  --skills-source <path>   skills repo path; falls back to $CLAUDE_SKILLS_DIR or installed npm package
  --name <name>            project name override (init)
  --type <type>            project type override (init): android|ios|firebase|web|cli|mixed
  --language <lang>        primary language override (init)
  --phase <phase>          discovery|mvp|beta|ga|maintenance (default: discovery)
  --install-mode <mode>    symlink|vendored|plugin (default: vendored)
  --hipaa, --pci, --gdpr, --coppa, --soc2, --qsbs   compliance flags (init)
  --skill <id>             repeatable; mark skill active (init)
  --agent <id>             repeatable; mark agent active (init)
  --rule <id>              repeatable; mark path-rule active (init)
  --no-default-rules       skip auto-deriving rules from detected stack (init)
  --dry-run                print plan, do not write
  --force                  overwrite even on conflict (dangerous; preserves prior in .claude/upgrades/)
`;

const cliOptions = {
  cwd:             { type: "string" },
  "skills-version":{ type: "string" },
  "skills-sha":    { type: "string" },
  "skills-source": { type: "string" },
  name:            { type: "string" },
  type:            { type: "string" },
  language:        { type: "string" },
  phase:           { type: "string" },
  "install-mode":  { type: "string" },
  hipaa:           { type: "boolean" },
  pci:             { type: "boolean" },
  gdpr:            { type: "boolean" },
  coppa:           { type: "boolean" },
  soc2:            { type: "boolean" },
  qsbs:            { type: "boolean" },
  skill:           { type: "string", multiple: true },
  agent:           { type: "string", multiple: true },
  rule:            { type: "string", multiple: true },
  "no-default-rules": { type: "boolean" },
  "dry-run":       { type: "boolean" },
  force:           { type: "boolean" },
  help:            { type: "boolean", short: "h" },
};

function parse() {
  const { values, positionals } = parseArgs({
    options: cliOptions,
    allowPositionals: true,
    strict: true,
  });
  return { command: positionals[0] ?? "help", flags: values, positionals };
}

function fail(message, code = 1) {
  process.stderr.write(`error: ${message}\n`);
  process.exit(code);
}

function resolveCwd(flags) {
  return resolve(flags.cwd ?? process.cwd());
}

async function cmdInit(flags) {
  const cwd = resolveCwd(flags);
  const existing = readManifest(cwd);
  if (existing && !flags.force) {
    fail(`${MANIFEST_FILENAME} already exists at ${cwd}. Use 'apply' to re-render, or pass --force to recreate.`);
  }
  if (!flags["skills-version"]) {
    fail("--skills-version is required for init (e.g., --skills-version 5.0.0)");
  }

  const detected = detectStack(cwd);
  const projectName = flags.name ?? deriveProjectName(cwd);
  const manifest = createManifest({
    projectName,
    projectType: flags.type ?? detected.projectType,
    primaryLanguage: flags.language ?? detected.primaryLanguage,
    cliVersion: pkg.version,
    skillsRepoVersion: flags["skills-version"],
    skillsRepoSha: flags["skills-sha"],
    stack: detected.stack,
    phase: flags.phase ?? "discovery",
    installMode: flags["install-mode"] ?? "vendored",
    compliance: {
      hipaa: !!flags.hipaa,
      pci:   !!flags.pci,
      gdpr:  !!flags.gdpr,
      coppa: !!flags.coppa,
      soc2:  !!flags.soc2,
      qsbs:  !!flags.qsbs,
    },
    activeSkills: flags.skill ?? [],
    activeAgents: flags.agent ?? [],
    activeRules: flags.rule ?? defaultRulesForStack({
      detected,
      explicit: flags.rule,
      noDefaults: flags["no-default-rules"],
      language: flags.language ?? detected.primaryLanguage,
      type: flags.type ?? detected.projectType,
    }),
  });

  const { valid, errors } = validateManifest(manifest);
  if (!valid) {
    fail(`generated manifest is invalid:\n${errors.map((e) => `  ${e.path}: ${e.message}`).join("\n")}`);
  }

  process.stdout.write(`detected: type=${detected.projectType}, language=${detected.primaryLanguage}, stack=[${detected.stack.join(",")}]\n`);

  const plan = buildPlan({ cwd, manifest, skillsSource: flags["skills-source"] });
  process.stdout.write(`plan:\n${summarizePlan(plan)}\n`);

  if (flags["dry-run"]) {
    process.stdout.write("dry-run: no files written.\n");
    return;
  }

  const result = applyPlan({ cwd, manifest, plan, write: true });
  reportResult(result);
}

async function cmdApply(flags) {
  const cwd = resolveCwd(flags);
  const manifest = readManifest(cwd);
  if (!manifest) fail(`no ${MANIFEST_FILENAME} at ${cwd}. Run 'init' first.`);

  const plan = buildPlan({ cwd, manifest, skillsSource: flags["skills-source"] });
  process.stdout.write(`plan:\n${summarizePlan(plan)}\n`);

  if (flags["dry-run"]) {
    process.stdout.write("dry-run: no files written.\n");
    return;
  }

  const result = applyPlan({ cwd, manifest, plan, write: true });
  reportResult(result);
}

function cmdDoctor(flags) {
  const cwd = resolveCwd(flags);
  const manifest = readManifest(cwd);
  if (!manifest) fail(`no ${MANIFEST_FILENAME} at ${cwd}.`);
  let skillsSourcePath = null;
  try { skillsSourcePath = resolveSkillsSource({ flag: flags["skills-source"] }).path; }
  catch { /* tolerated; doctor still reports manifest-level issues */ }

  const result = diagnose({ cwd, manifest, skillsSourcePath });
  process.stdout.write(`${summarizeDiagnose(result)}\n`);
  if (result.findings.some((f) => f.severity === "error")) process.exit(2);
  if (result.findings.length > 0) process.exit(1);
}

function cmdInventory(flags, paths) {
  if (paths.length === 0) fail("inventory: at least one project path is required");
  let skillsSourcePath = null;
  try { skillsSourcePath = resolveSkillsSource({ flag: flags["skills-source"] }).path; }
  catch { /* tolerated */ }
  const inv = buildInventory({ projectPaths: paths, skillsSourcePath });
  process.stdout.write(`${formatInventoryCsv(inv)}\n`);
  const anyError = inv.rows.some((r) => r.error);
  const anyDrift = inv.rows.some((r) => (r.drift ?? 0) > 0);
  if (anyError || anyDrift) process.exit(1);
}

function reportResult({ writes, conflicts, vendor, generated }) {
  for (const w of writes) process.stdout.write(`  ${w.decision.padEnd(9)} ${w.filePath}\n`);
  for (const v of vendor?.writes ?? []) process.stdout.write(`  ${v.decision.padEnd(9)} ${v.targetPath}\n`);
  for (const r of vendor?.removes ?? []) process.stdout.write(`  remove    ${r.targetPath}\n`);
  for (const g of generated?.writes ?? []) process.stdout.write(`  ${g.decision.padEnd(9)} ${g.target}\n`);
  const allConflicts = [...conflicts, ...(vendor?.conflicts ?? []), ...(generated?.conflicts ?? [])];
  if (allConflicts.length > 0) {
    process.stdout.write(`\n${allConflicts.length} conflict(s); rendered content saved under .claude/upgrades/. Existing content preserved in target.\n`);
    process.exit(2);
  }
}

function defaultRulesForStack({ detected, explicit, noDefaults, language, type }) {
  if (explicit?.length) return explicit;
  if (noDefaults) return [];
  const rules = new Set();
  const stack = detected.stack ?? [];
  if (stack.includes("nextjs") || stack.includes("react")) rules.add("web");
  if (stack.includes("firebase")) rules.add("firebase");
  if (stack.includes("docker")) rules.add("docker");
  if (stack.includes("terraform")) rules.add("terraform");
  if (language === "python") rules.add("python");
  if (language === "go") rules.add("go");
  if (language === "rust") rules.add("rust");
  if (type === "android") rules.add("android");
  if (type === "ios") rules.add("ios");
  return [...rules];
}

function deriveProjectName(cwd) {
  const pkgPath = resolve(cwd, "package.json");
  if (existsSync(pkgPath)) {
    try {
      const p = JSON.parse(readFileSync(pkgPath, "utf8"));
      if (p.name) return String(p.name).replace(/^@[^/]+\//, "").toLowerCase();
    } catch {}
  }
  return resolve(cwd).split("/").pop().toLowerCase();
}

async function main() {
  let parsed;
  try {
    parsed = parse();
  } catch (e) {
    fail(e.message);
  }
  const { command, flags } = parsed;
  if (flags.help || command === "help") return process.stdout.write(HELP);

  switch (command) {
    case "init":      return cmdInit(flags);
    case "apply":     return cmdApply(flags);
    case "doctor":    return cmdDoctor(flags);
    case "inventory": return cmdInventory(flags, parsed.positionals.slice(1));
    case "version":   return process.stdout.write(`${pkg.version}\n`);
    default:          fail(`unknown command: ${command}`);
  }
}

main().catch((e) => fail(e.stack ?? e.message));
