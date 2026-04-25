import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync, existsSync, readdirSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { resolveSkillsSource, planVendor, applyVendor, VENDOR_DECISIONS } from "../src/vendor/index.mjs";
import { sha256 } from "../src/blocks/index.mjs";
import { createManifest } from "../src/manifest/index.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const SKILLS_REPO = resolve(here, "../..");
const CLI = resolve(here, "../bin/claude-bootstrap.mjs");

function tmp() {
  return mkdtempSync(join(tmpdir(), "claude-bootstrap-vendor-"));
}

function run(args, opts = {}) {
  return execFileSync("node", [CLI, ...args], { encoding: "utf8", ...opts });
}

function runCapture(args, opts = {}) {
  try {
    return { stdout: run(args, opts), exitCode: 0 };
  } catch (e) {
    return { stdout: e.stdout?.toString() ?? "", stderr: e.stderr?.toString() ?? "", exitCode: e.status };
  }
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

const baseInput = {
  projectName: "vendor-fixture",
  projectType: "web",
  primaryLanguage: "typescript",
  cliVersion: "0.1.0",
  skillsRepoVersion: "5.0.0",
};

test("resolveSkillsSource: --skills-source flag wins", () => {
  const r = resolveSkillsSource({ flag: SKILLS_REPO });
  assert.equal(r.source, "--skills-source");
  assert.equal(r.path, SKILLS_REPO);
});

test("resolveSkillsSource: $CLAUDE_SKILLS_DIR is used when no flag", () => {
  const r = resolveSkillsSource({ env: { CLAUDE_SKILLS_DIR: SKILLS_REPO } });
  assert.equal(r.source, "$CLAUDE_SKILLS_DIR");
});

test("resolveSkillsSource: --skills-source pointed at empty dir fails loudly", () => {
  const empty = tmp();
  assert.throws(
    () => resolveSkillsSource({ flag: empty, env: {} }),
    /not a valid skills repo/,
  );
});

test("resolveSkillsSource: $CLAUDE_SKILLS_DIR pointed at empty dir fails loudly", () => {
  const empty = tmp();
  assert.throws(
    () => resolveSkillsSource({ env: { CLAUDE_SKILLS_DIR: empty } }),
    /not a valid skills repo/,
  );
});

test("planVendor: CREATE for new skills and agents", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, activeSkills: ["feature-audit"], activeAgents: ["pr-reviewer"] });
  const plan = planVendor({ cwd, source: SKILLS_REPO, manifest: m });
  const decisions = plan.decisions.map((d) => ({ path: d.targetPath, decision: d.decision }));
  assert.ok(decisions.some((d) => d.path === ".claude/skills/feature-audit/SKILL.md" && d.decision === "create"));
  assert.ok(decisions.some((d) => d.path === ".claude/agents/pr-reviewer.md" && d.decision === "create"));
});

test("planVendor: UNCHANGED when target hash matches source", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, activeSkills: ["feature-audit"] });
  const sourcePath = join(SKILLS_REPO, "skills/feature-audit/SKILL.md");
  const sourceContent = readFileSync(sourcePath, "utf8");
  const targetPath = ".claude/skills/feature-audit/SKILL.md";
  mkdirSync(join(cwd, dirname(targetPath)), { recursive: true });
  writeFileSync(join(cwd, targetPath), sourceContent);
  m.vendored = { [targetPath]: { source: "skills/feature-audit/SKILL.md", hash: sha256(sourceContent) } };

  const plan = planVendor({ cwd, source: SKILLS_REPO, manifest: m });
  const d = plan.decisions.find((x) => x.targetPath === targetPath);
  assert.equal(d.decision, "unchanged");
});

test("planVendor: CONFLICT when user edited a vendored file", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, activeSkills: ["feature-audit"] });
  const sourcePath = join(SKILLS_REPO, "skills/feature-audit/SKILL.md");
  const sourceContent = readFileSync(sourcePath, "utf8");
  const targetPath = ".claude/skills/feature-audit/SKILL.md";
  mkdirSync(join(cwd, dirname(targetPath)), { recursive: true });
  writeFileSync(join(cwd, targetPath), sourceContent + "\n\n# user added section\n");
  m.vendored = { [targetPath]: { source: "skills/feature-audit/SKILL.md", hash: sha256(sourceContent) } };

  const plan = planVendor({ cwd, source: SKILLS_REPO, manifest: m });
  const d = plan.decisions.find((x) => x.targetPath === targetPath);
  assert.equal(d.decision, "conflict");
});

test("planVendor: REMOVE when skill drops out of active list", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, activeSkills: [] });
  const orphanPath = ".claude/skills/old-skill/SKILL.md";
  m.vendored = { [orphanPath]: { source: "skills/old-skill/SKILL.md", hash: "0".repeat(64) } };

  const plan = planVendor({ cwd, source: SKILLS_REPO, manifest: m });
  const d = plan.decisions.find((x) => x.targetPath === orphanPath);
  assert.equal(d.decision, "remove");
});

test("planVendor: throws on missing skill or agent in source", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, activeSkills: ["does-not-exist"] });
  assert.throws(() => planVendor({ cwd, source: SKILLS_REPO, manifest: m }), /not found in source/);
});

test("applyVendor: writes files for CREATE/UPDATE and tracks hashes", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, activeSkills: ["feature-audit"], activeAgents: ["pr-reviewer"] });
  const plan = planVendor({ cwd, source: SKILLS_REPO, manifest: m });
  const result = applyVendor({ cwd, plan, write: true });

  assert.ok(existsSync(join(cwd, ".claude/skills/feature-audit/SKILL.md")));
  assert.ok(existsSync(join(cwd, ".claude/agents/pr-reviewer.md")));
  assert.ok(result.nextVendored[".claude/skills/feature-audit/SKILL.md"]);
  assert.ok(result.nextVendored[".claude/agents/pr-reviewer.md"]);
  assert.equal(result.writes.length, 2);
  assert.equal(result.conflicts.length, 0);
});

test("integration: init with skill+agent vendors actual files from this repo", () => {
  const dir = tmp();
  run([
    "init", "--cwd", dir, "--skills-version", "5.0.0",
    "--skills-source", SKILLS_REPO,
    "--name", "fixture",
    "--skill", "feature-audit",
    "--skill", "stripe-integration",
    "--agent", "pr-reviewer",
  ]);

  assert.ok(existsSync(join(dir, ".claude/skills/feature-audit/SKILL.md")));
  assert.ok(existsSync(join(dir, ".claude/skills/stripe-integration/SKILL.md")));
  assert.ok(existsSync(join(dir, ".claude/agents/pr-reviewer.md")));

  const m = readJson(join(dir, "claude.manifest.json"));
  assert.ok(m.vendored[".claude/skills/feature-audit/SKILL.md"]);
  assert.ok(m.vendored[".claude/skills/stripe-integration/SKILL.md"]);
  assert.ok(m.vendored[".claude/agents/pr-reviewer.md"]);

  const targetSkill = readFileSync(join(dir, ".claude/skills/feature-audit/SKILL.md"), "utf8");
  const sourceSkill = readFileSync(join(SKILLS_REPO, "skills/feature-audit/SKILL.md"), "utf8");
  assert.equal(targetSkill, sourceSkill, "vendored content matches source byte for byte");
});

test("integration: apply is idempotent across vendored files", () => {
  const dir = tmp();
  run([
    "init", "--cwd", dir, "--skills-version", "5.0.0",
    "--skills-source", SKILLS_REPO,
    "--name", "fixture",
    "--skill", "feature-audit",
    "--agent", "pr-reviewer",
  ]);
  const out = run(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  for (const line of out.split("\n")) {
    if (line.match(/^\s*\[(create|update|conflict|remove)/)) {
      assert.fail(`expected idempotent, saw: ${line}`);
    }
  }
});

test("integration: dropping skill from manifest removes vendored file on next apply", () => {
  const dir = tmp();
  run([
    "init", "--cwd", dir, "--skills-version", "5.0.0",
    "--skills-source", SKILLS_REPO,
    "--name", "fixture",
    "--skill", "feature-audit",
  ]);
  assert.ok(existsSync(join(dir, ".claude/skills/feature-audit/SKILL.md")));

  const m = readJson(join(dir, "claude.manifest.json"));
  m.skills.active = [];
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  run(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.ok(!existsSync(join(dir, ".claude/skills/feature-audit/SKILL.md")), "removed");

  const m2 = readJson(join(dir, "claude.manifest.json"));
  assert.equal(Object.keys(m2.vendored).length, 0);
});

test("integration: hand-edited vendored file produces conflict on apply", () => {
  const dir = tmp();
  run([
    "init", "--cwd", dir, "--skills-version", "5.0.0",
    "--skills-source", SKILLS_REPO,
    "--name", "fixture",
    "--skill", "feature-audit",
  ]);

  const skillPath = join(dir, ".claude/skills/feature-audit/SKILL.md");
  writeFileSync(skillPath, readFileSync(skillPath, "utf8") + "\n# USER EDITED\n");

  const m = readJson(join(dir, "claude.manifest.json"));
  m.bootstrap.skillsRepoVersion = "5.0.1";
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  const r = runCapture(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(r.exitCode, 2);
  assert.match(r.stdout, /conflict/i);
  assert.match(readFileSync(skillPath, "utf8"), /USER EDITED/);
  assert.ok(readdirSync(join(dir, ".claude/upgrades")).length > 0);
});
