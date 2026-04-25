import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { loadOrgManifest, enforceOrgPolicy } from "../src/org/index.mjs";
import { diagnose, DRIFT_KINDS } from "../src/diagnose/doctor.mjs";
import { buildInventory, formatInventoryCsv } from "../src/diagnose/inventory.mjs";
import { createManifest } from "../src/manifest/index.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const SKILLS_REPO = resolve(here, "../..");
const CLI = resolve(here, "../bin/claude-bootstrap.mjs");

function tmp() { return mkdtempSync(join(tmpdir(), "claude-bootstrap-sliceB-")); }
function run(args, opts = {}) { return execFileSync("node", [CLI, ...args], { encoding: "utf8", ...opts }); }
function runCapture(args, opts = {}) {
  try { return { stdout: run(args, opts), exitCode: 0 }; }
  catch (e) { return { stdout: e.stdout?.toString() ?? "", stderr: e.stderr?.toString() ?? "", exitCode: e.status }; }
}
function readJson(path) { return JSON.parse(readFileSync(path, "utf8")); }
function writeJson(path, obj) { writeFileSync(path, JSON.stringify(obj, null, 2)); }

const baseInput = {
  projectName: "fixture", projectType: "web", primaryLanguage: "typescript",
  cliVersion: "0.1.0", skillsRepoVersion: "5.0.0",
};

function makeOrgRepo({ minVer, requiredSkills = [], forbiddenSkills = [], requiredAgents = [] }) {
  const dir = tmp();
  mkdirSync(join(dir, "skills"));
  mkdirSync(join(dir, "agents"));
  for (const s of requiredSkills) {
    mkdirSync(join(dir, "skills", s));
    writeFileSync(join(dir, "skills", s, "SKILL.md"), `# ${s}\n`);
  }
  for (const s of forbiddenSkills) {
    mkdirSync(join(dir, "skills", s));
    writeFileSync(join(dir, "skills", s, "SKILL.md"), `# ${s}\n`);
  }
  for (const a of requiredAgents) writeFileSync(join(dir, "agents", `${a}.md`), `# ${a}\n`);
  writeJson(join(dir, "org.manifest.json"), {
    manifestVersion: 1,
    bootstrap: minVer ? { minimumSkillsVersion: minVer } : undefined,
    skills: { required: requiredSkills, forbidden: forbiddenSkills },
    agents: { required: requiredAgents },
  });
  return dir;
}

test("loadOrgManifest: returns null when file missing", () => {
  const dir = tmp();
  mkdirSync(join(dir, "skills")); mkdirSync(join(dir, "agents"));
  assert.equal(loadOrgManifest({ skillsSourcePath: dir }), null);
});

test("loadOrgManifest: parses + validates", () => {
  const repo = makeOrgRepo({ minVer: "5.0.0", requiredSkills: ["security-review"] });
  const om = loadOrgManifest({ skillsSourcePath: repo });
  assert.equal(om.bootstrap.minimumSkillsVersion, "5.0.0");
});

test("loadOrgManifest: throws on invalid org manifest", () => {
  const dir = tmp(); mkdirSync(join(dir, "skills")); mkdirSync(join(dir, "agents"));
  writeJson(join(dir, "org.manifest.json"), { manifestVersion: 1, skills: { required: ["BadName"] } });
  assert.throws(() => loadOrgManifest({ skillsSourcePath: dir }), /invalid/);
});

test("enforceOrgPolicy: no org manifest → no errors", () => {
  const m = createManifest(baseInput);
  const { errors } = enforceOrgPolicy({ projectManifest: m, orgManifest: null });
  assert.equal(errors.length, 0);
});

test("enforceOrgPolicy: skills-version floor enforced", () => {
  const m = createManifest({ ...baseInput, skillsRepoVersion: "4.9.0" });
  const org = { manifestVersion: 1, bootstrap: { minimumSkillsVersion: "5.0.0" } };
  const { errors } = enforceOrgPolicy({ projectManifest: m, orgManifest: org });
  assert.equal(errors.length, 1);
  assert.equal(errors[0].code, "org/skills-version-floor");
});

test("enforceOrgPolicy: skills-version equal-or-above passes", () => {
  const m = createManifest({ ...baseInput, skillsRepoVersion: "5.0.1" });
  const org = { manifestVersion: 1, bootstrap: { minimumSkillsVersion: "5.0.0" } };
  const { errors } = enforceOrgPolicy({ projectManifest: m, orgManifest: org });
  assert.equal(errors.length, 0);
});

test("enforceOrgPolicy: required skills must be active", () => {
  const m = createManifest(baseInput);
  const org = { manifestVersion: 1, skills: { required: ["security-review"] } };
  const { errors } = enforceOrgPolicy({ projectManifest: m, orgManifest: org });
  assert.equal(errors[0].code, "org/skills-required");
});

test("enforceOrgPolicy: forbidden skills cannot be active", () => {
  const m = createManifest({ ...baseInput, activeSkills: ["legacy-skill"] });
  const org = { manifestVersion: 1, skills: { forbidden: ["legacy-skill"] } };
  const { errors } = enforceOrgPolicy({ projectManifest: m, orgManifest: org });
  assert.equal(errors[0].code, "org/skills-forbidden");
});

test("integration: apply fails when project violates org floor", () => {
  const repo = makeOrgRepo({ minVer: "5.0.0", requiredSkills: ["security-review"] });
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", repo,
       "--name", "x", "--skill", "security-review"]);
  const m = readJson(join(dir, "claude.manifest.json"));
  m.bootstrap.skillsRepoVersion = "4.9.0";
  m.skills.active = [];
  writeJson(join(dir, "claude.manifest.json"), m);
  const r = runCapture(["apply", "--cwd", dir, "--skills-source", repo]);
  assert.equal(r.exitCode, 1);
  assert.match(r.stderr, /org policy violation/);
});

test("integration: init succeeds when manifest meets org floor", () => {
  const repo = makeOrgRepo({ minVer: "5.0.0", requiredSkills: ["security-review"] });
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", repo,
       "--name", "x", "--skill", "security-review", "--no-default-rules"]);
});

test("doctor: clean install reports no drift", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--skill", "feature-audit", "--no-default-rules"]);
  const r = runCapture(["doctor", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(r.exitCode, 0);
  assert.match(r.stdout, /no drift/);
});

test("doctor: detects user-edited vendored file", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--skill", "feature-audit", "--no-default-rules"]);
  const skillPath = join(dir, ".claude/skills/feature-audit/SKILL.md");
  writeFileSync(skillPath, readFileSync(skillPath, "utf8") + "\n# user edit\n");
  const r = runCapture(["doctor", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(r.exitCode, 1);
  assert.match(r.stdout, /vendored-edited/);
});

test("doctor: detects edited managed block in CLAUDE.md", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--no-default-rules"]);
  const claudePath = join(dir, "CLAUDE.md");
  const before = readFileSync(claudePath, "utf8");
  writeFileSync(claudePath, before.replace("Project type:", "X Project type:"));
  const r = runCapture(["doctor", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(r.exitCode, 1);
  assert.match(r.stdout, /block-edited/);
});

test("doctor: detects deleted vendored file", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--skill", "feature-audit", "--no-default-rules"]);
  const skillPath = join(dir, ".claude/skills/feature-audit/SKILL.md");
  rmSync(skillPath);
  const findings = diagnose({
    cwd: dir,
    manifest: readJson(join(dir, "claude.manifest.json")),
    skillsSourcePath: SKILLS_REPO,
  }).findings;
  assert.ok(findings.some((f) => f.kind === DRIFT_KINDS.VENDORED_MISSING));
});

test("inventory: emits CSV for multiple projects", () => {
  const dirA = tmp(); const dirB = tmp();
  run(["init", "--cwd", dirA, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "alpha", "--no-default-rules"]);
  run(["init", "--cwd", dirB, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "beta", "--skill", "feature-audit", "--no-default-rules"]);
  const out = run(["inventory", "--skills-source", SKILLS_REPO, dirA, dirB]);
  const lines = out.trim().split("\n");
  assert.equal(lines[0], "project,type,phase,skillsRepoVersion,cliVersion,lastAppliedAt,installMode,compliance,skills,agents,rules,drift");
  assert.equal(lines.length, 3);
  assert.match(lines[1], /alpha/);
  assert.match(lines[2], /beta/);
});

test("inventory: missing manifest produces ERROR row", () => {
  const empty = tmp();
  const inv = buildInventory({ projectPaths: [empty], skillsSourcePath: SKILLS_REPO });
  assert.ok(inv.rows[0].error);
  const csv = formatInventoryCsv(inv);
  assert.match(csv, /ERROR:/);
});

test("inventory: drift in any project causes nonzero exit", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--skill", "feature-audit", "--no-default-rules"]);
  const skillPath = join(dir, ".claude/skills/feature-audit/SKILL.md");
  writeFileSync(skillPath, readFileSync(skillPath, "utf8") + "\n# drift\n");
  const r = runCapture(["inventory", "--skills-source", SKILLS_REPO, dir]);
  assert.equal(r.exitCode, 1);
  assert.match(r.stdout, /,1$/m, "drift count column should be 1");
});
