#!/usr/bin/env node
import { parseArgs } from "node:util";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { createManifest, validateManifest } from "../src/manifest/index.mjs";
import { detectStack } from "../src/detect/stack.mjs";
import { buildPlan, applyPlan, readManifest, summarizePlan, MANIFEST_FILENAME } from "../src/apply/index.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = JSON.parse(readFileSync(resolve(here, "../package.json"), "utf8"));

const HELP = `claude-bootstrap v${pkg.version}

Usage:
  claude-bootstrap init    [options]   create claude.manifest.json + scaffold managed files
  claude-bootstrap apply   [options]   re-render templates against existing manifest
  claude-bootstrap version             print version
  claude-bootstrap help                print this help

Options:
  --cwd <path>             target project root (default: process.cwd())
  --skills-version <ver>   skills repo version to pin (init only; required for init)
  --skills-sha <sha>       skills repo commit (init, optional)
  --name <name>            project name override (init)
  --type <type>            project type override (init): android|ios|firebase|web|cli|mixed
  --language <lang>        primary language override (init)
  --phase <phase>          discovery|mvp|beta|ga|maintenance (default: discovery)
  --install-mode <mode>    symlink|vendored|plugin (default: vendored)
  --hipaa, --pci, --gdpr, --coppa, --soc2, --qsbs   compliance flags (init)
  --skill <id>             repeatable; mark skill active (init)
  --agent <id>             repeatable; mark agent active (init)
  --dry-run                print plan, do not write
  --force                  overwrite even on conflict (dangerous; preserves prior in .claude/upgrades/)
`;

const cliOptions = {
  cwd:             { type: "string" },
  "skills-version":{ type: "string" },
  "skills-sha":    { type: "string" },
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
  return { command: positionals[0] ?? "help", flags: values };
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
  });

  const { valid, errors } = validateManifest(manifest);
  if (!valid) {
    fail(`generated manifest is invalid:\n${errors.map((e) => `  ${e.path}: ${e.message}`).join("\n")}`);
  }

  process.stdout.write(`detected: type=${detected.projectType}, language=${detected.primaryLanguage}, stack=[${detected.stack.join(",")}]\n`);

  const plan = buildPlan({ cwd, manifest });
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

  const plan = buildPlan({ cwd, manifest });
  process.stdout.write(`plan:\n${summarizePlan(plan)}\n`);

  if (flags["dry-run"]) {
    process.stdout.write("dry-run: no files written.\n");
    return;
  }

  const result = applyPlan({ cwd, manifest, plan, write: true });
  reportResult(result);
}

function reportResult({ writes, conflicts }) {
  for (const w of writes) process.stdout.write(`  ${w.decision.padEnd(9)} ${w.filePath}\n`);
  if (conflicts.length > 0) {
    process.stdout.write(`\n${conflicts.length} conflict(s); rendered content saved under .claude/upgrades/. Existing content preserved in target.\n`);
    process.exit(2);
  }
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
    case "init":    return cmdInit(flags);
    case "apply":   return cmdApply(flags);
    case "version": return process.stdout.write(`${pkg.version}\n`);
    default:        fail(`unknown command: ${command}`);
  }
}

main().catch((e) => fail(e.stack ?? e.message));
