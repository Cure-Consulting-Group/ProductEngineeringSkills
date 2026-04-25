import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync, existsSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { renderTemplate } from "../src/template/render.mjs";
import { createManifest } from "../src/manifest/index.mjs";
import { planGenerated, applyGenerated } from "../src/generated/index.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const SKILLS_REPO = resolve(here, "../..");
const CLI = resolve(here, "../bin/claude-bootstrap.mjs");

function tmp() {
  return mkdtempSync(join(tmpdir(), "claude-bootstrap-sliceA-"));
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
  projectName: "fixture",
  projectType: "web",
  primaryLanguage: "typescript",
  cliVersion: "0.1.0",
  skillsRepoVersion: "5.0.0",
};

test("rules: planVendor includes rules in manifest.rules.active", async () => {
  const { planVendor } = await import("../src/vendor/index.mjs");
  const cwd = tmp();
  const m = createManifest({ ...baseInput, activeRules: ["web", "firebase"] });
  const plan = planVendor({ cwd, source: SKILLS_REPO, manifest: m });
  const targets = plan.decisions.map((d) => d.targetPath);
  assert.ok(targets.includes(".claude/rules/web.md"));
  assert.ok(targets.includes(".claude/rules/firebase.md"));
});

test("integration: --rule flag vendors path-rule files", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--rule", "web", "--rule", "firebase"]);
  assert.ok(existsSync(join(dir, ".claude/rules/web.md")));
  assert.ok(existsSync(join(dir, ".claude/rules/firebase.md")));
  const m = readJson(join(dir, "claude.manifest.json"));
  assert.deepEqual(m.rules.active, ["web", "firebase"]);
});

test("integration: rules auto-derived from detected stack", () => {
  const dir = tmp();
  writeFileSync(join(dir, "package.json"), JSON.stringify({
    name: "vendly-web",
    dependencies: { next: "14", firebase: "10" },
  }));
  writeFileSync(join(dir, "tsconfig.json"), "{}");
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO]);

  const m = readJson(join(dir, "claude.manifest.json"));
  assert.ok(m.rules.active.includes("web"));
  assert.ok(m.rules.active.includes("firebase"));
  assert.ok(existsSync(join(dir, ".claude/rules/web.md")));
});

test("integration: --no-default-rules skips auto-derivation", () => {
  const dir = tmp();
  writeFileSync(join(dir, "package.json"), JSON.stringify({
    name: "x", dependencies: { next: "14" },
  }));
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO, "--no-default-rules"]);
  const m = readJson(join(dir, "claude.manifest.json"));
  assert.deepEqual(m.rules.active, []);
});

test("generated: hooks.json renders parseable JSON when manifest hooks are populated", () => {
  const m = createManifest({
    ...baseInput,
    hooks: {
      preCommit: ["security-review"],
      postFeature: ["feature-audit", "product-marketing"],
      prePR: ["pr-reviewer"],
    },
  });
  const out = renderTemplate("claude-hooks.json.ejs", m);
  const parsed = JSON.parse(out);
  assert.ok(parsed.hooks.PostToolUse);
  assert.ok(parsed.hooks.PreToolUse);
  assert.equal(parsed.$project, "fixture");
  const postEdit = parsed.hooks.PostToolUse.find((h) => h.matcher === "Edit|Write");
  assert.ok(postEdit, "post-feature wired to Edit|Write");
  assert.match(postEdit.hooks[0].command, /feature-audit/);
});

test("generated: hooks.json with no hooks renders parseable JSON with empty events", () => {
  const m = createManifest(baseInput);
  const out = renderTemplate("claude-hooks.json.ejs", m);
  const parsed = JSON.parse(out);
  assert.deepEqual(parsed.hooks, {});
});

test("generated: .cursorrules renders project metadata + rule list", () => {
  const m = createManifest({
    ...baseInput,
    stack: ["nextjs", "firebase"],
    activeRules: ["web", "firebase"],
    compliance: { gdpr: true },
  });
  const out = renderTemplate("cursorrules.ejs", m);
  assert.match(out, /fixture/);
  assert.match(out, /Stack:/);
  assert.match(out, /GDPR/);
  assert.match(out, /web\.md/);
  assert.match(out, /firebase\.md/);
});

test("generated: .gemini/config.yaml renders skills/agents/rules", () => {
  const m = createManifest({
    ...baseInput,
    activeSkills: ["feature-audit"],
    activeAgents: ["pr-reviewer"],
    activeRules: ["web"],
    compliance: { gdpr: true },
  });
  const out = renderTemplate("gemini-config.yaml.ejs", m);
  assert.match(out, /feature-audit/);
  assert.match(out, /pr-reviewer/);
  assert.match(out, /- web/);
  assert.match(out, /- gdpr/);
});

test("planGenerated: CREATE then UNCHANGED on idempotent re-run", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, hooks: { preCommit: [], postFeature: ["feature-audit"], prePR: [] } });

  const p1 = planGenerated({ cwd, manifest: m });
  for (const d of p1.decisions) assert.equal(d.decision, "create");
  const r1 = applyGenerated({ cwd, plan: p1, write: true });

  const m2 = { ...m, generated: r1.nextGenerated };
  const p2 = planGenerated({ cwd, manifest: m2 });
  for (const d of p2.decisions) assert.equal(d.decision, "unchanged");
});

test("planGenerated: CONFLICT when user edited a generated file", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, hooks: { preCommit: [], postFeature: ["feature-audit"], prePR: [] } });
  const p1 = planGenerated({ cwd, manifest: m });
  const r1 = applyGenerated({ cwd, plan: p1, write: true });

  const hookPath = join(cwd, ".claude/hooks/hooks.json");
  writeFileSync(hookPath, readFileSync(hookPath, "utf8") + "\n// user edit\n");

  const m2 = { ...m, generated: r1.nextGenerated };
  const p2 = planGenerated({ cwd, manifest: m2 });
  const conflict = p2.decisions.find((d) => d.target === ".claude/hooks/hooks.json");
  assert.equal(conflict.decision, "conflict");
});

test("integration: init produces hooks.json, .cursorrules, .gemini/config.yaml", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--skill", "feature-audit"]);
  assert.ok(existsSync(join(dir, ".claude/hooks/hooks.json")));
  assert.ok(existsSync(join(dir, ".cursorrules")));
  assert.ok(existsSync(join(dir, ".gemini/config.yaml")));

  const m = readJson(join(dir, "claude.manifest.json"));
  assert.ok(m.generated[".claude/hooks/hooks.json"]);
  assert.ok(m.generated[".cursorrules"]);
  assert.ok(m.generated[".gemini/config.yaml"]);
});

test("integration: re-running apply after manifest hooks change updates hooks.json", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO, "--name", "x"]);
  const m = readJson(join(dir, "claude.manifest.json"));
  m.hooks.postFeature = ["feature-audit"];
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  run(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  const hooks = readJson(join(dir, ".claude/hooks/hooks.json"));
  assert.ok(hooks.hooks.PostToolUse);
});

test("integration: hand-edited hooks.json produces conflict on apply", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO, "--name", "x"]);

  const hookPath = join(dir, ".claude/hooks/hooks.json");
  writeFileSync(hookPath, readFileSync(hookPath, "utf8") + "\n");

  const m = readJson(join(dir, "claude.manifest.json"));
  m.hooks.postFeature = ["feature-audit"];
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  const r = runCapture(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(r.exitCode, 2);
  assert.match(r.stdout, /conflict/i);
});
