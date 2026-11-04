import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, readdirSync } from "node:fs";
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

const SETTINGS = ".claude/settings.json";
const HOOKS_KEY = ".claude/settings.json#hooks";
const LEGACY = ".claude/hooks/hooks.json";

test("planGenerated: CREATE then UNCHANGED on idempotent re-run", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, hooks: { preCommit: [], postFeature: ["feature-audit"], prePR: [] } });

  const p1 = planGenerated({ cwd, manifest: m });
  for (const d of p1.decisions) assert.equal(d.decision, "create", d.target);
  const r1 = applyGenerated({ cwd, plan: p1, write: true });

  const m2 = { ...m, generated: r1.nextGenerated };
  const p2 = planGenerated({ cwd, manifest: m2 });
  for (const d of p2.decisions) assert.equal(d.decision, "unchanged", d.target);
});

test("planGenerated (T89): hooks land in settings.json#hooks, never in .claude/hooks/hooks.json", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, hooks: { preCommit: ["test-runner"], postFeature: ["feature-audit"], prePR: [] } });
  const p1 = planGenerated({ cwd, manifest: m });
  const r1 = applyGenerated({ cwd, plan: p1, write: true });

  assert.ok(!existsSync(join(cwd, LEGACY)), "no .claude/hooks/hooks.json");
  const settings = readJson(join(cwd, SETTINGS));
  assert.ok(settings.hooks.PostToolUse, "PostToolUse group present");
  assert.ok(settings.hooks.PreToolUse, "PreToolUse group present");
  const post = settings.hooks.PostToolUse[0].hooks[0].command;
  assert.match(post, /hookSpecificOutput/);
  assert.match(post, /"hookEventName":"PostToolUse"/);
  assert.match(post, /additionalContext/);
  assert.match(post, /feature-audit/);
  assert.ok(!/"reminder"/.test(post), "plain {reminder} stdout reaches nobody");
  assert.ok(r1.nextGenerated[HOOKS_KEY]);
  assert.equal(r1.nextGenerated[HOOKS_KEY].commands.length, 2);
  assert.ok(!r1.nextGenerated[LEGACY]);
});

test("planGenerated (T89): existing settings keys and user hooks survive; re-run adds no duplicates", () => {
  const cwd = tmp();
  mkdirSync(join(cwd, ".claude"), { recursive: true });
  const user = {
    permissions: { allow: ["Bash(npm test*)"] },
    model: "opus",
    hooks: { PostToolUse: [{ matcher: "Edit", hooks: [{ type: "command", command: "echo user-hook" }] }] },
  };
  writeFileSync(join(cwd, SETTINGS), JSON.stringify(user, null, 2) + "\n");

  const m = createManifest({ ...baseInput, hooks: { preCommit: [], postFeature: ["feature-audit"], prePR: [] } });
  const p1 = planGenerated({ cwd, manifest: m });
  const d1 = p1.decisions.find((d) => d.target === HOOKS_KEY);
  assert.equal(d1.decision, "update");
  const r1 = applyGenerated({ cwd, plan: p1, write: true });

  const s1 = readJson(join(cwd, SETTINGS));
  assert.deepEqual(s1.permissions, user.permissions);
  assert.equal(s1.model, "opus");
  assert.equal(s1.hooks.PostToolUse.length, 2, "user group + generated group");
  assert.equal(s1.hooks.PostToolUse[0].hooks[0].command, "echo user-hook");

  // second run: UNCHANGED and byte-identical
  const text1 = readFileSync(join(cwd, SETTINGS), "utf8");
  const m2 = { ...m, generated: r1.nextGenerated };
  const p2 = planGenerated({ cwd, manifest: m2 });
  assert.equal(p2.decisions.find((d) => d.target === HOOKS_KEY).decision, "unchanged");
  applyGenerated({ cwd, plan: p2, write: true });
  assert.equal(readFileSync(join(cwd, SETTINGS), "utf8"), text1);
  assert.equal(readJson(join(cwd, SETTINGS)).hooks.PostToolUse.length, 2);

  // manifest change: the generated group is replaced, not appended
  const m3 = { ...m2, hooks: { preCommit: ["test-runner"], postFeature: ["feature-audit", "code-reviewer"], prePR: [] } };
  const p3 = planGenerated({ cwd, manifest: m3 });
  assert.equal(p3.decisions.find((d) => d.target === HOOKS_KEY).decision, "update");
  applyGenerated({ cwd, plan: p3, write: true });
  const s3 = readJson(join(cwd, SETTINGS));
  assert.equal(s3.hooks.PostToolUse.length, 2);
  assert.match(s3.hooks.PostToolUse[1].hooks[0].command, /code-reviewer/);
  assert.equal(s3.hooks.PreToolUse.length, 1);
});

test("planGenerated (T89): CONFLICT when a generated hook was edited by hand", () => {
  const cwd = tmp();
  const m = createManifest({ ...baseInput, hooks: { preCommit: [], postFeature: ["feature-audit"], prePR: [] } });
  const p1 = planGenerated({ cwd, manifest: m });
  const r1 = applyGenerated({ cwd, plan: p1, write: true });

  const s = readJson(join(cwd, SETTINGS));
  s.hooks.PostToolUse[0].hooks[0].command += " # user edit";
  writeFileSync(join(cwd, SETTINGS), JSON.stringify(s, null, 2) + "\n");

  const m2 = { ...m, generated: r1.nextGenerated };
  const p2 = planGenerated({ cwd, manifest: m2 });
  const conflict = p2.decisions.find((d) => d.target === HOOKS_KEY);
  assert.equal(conflict.decision, "conflict");
  const r2 = applyGenerated({ cwd, plan: p2, write: true });
  assert.equal(r2.conflicts.length, 1);
  assert.match(readJson(join(cwd, SETTINGS)).hooks.PostToolUse[0].hooks[0].command, /user edit$/, "user content preserved");
});

test("integration (T89): init writes hooks into settings.json, .cursorrules, .gemini/config.yaml; no hooks.json", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO,
       "--name", "x", "--skill", "feature-audit"]);
  assert.ok(!existsSync(join(dir, LEGACY)));
  assert.ok(existsSync(join(dir, SETTINGS)));
  assert.ok(existsSync(join(dir, ".cursorrules")));
  assert.ok(existsSync(join(dir, ".gemini/config.yaml")));

  const m = readJson(join(dir, "claude.manifest.json"));
  assert.ok(m.generated[HOOKS_KEY]);
  assert.ok(!m.generated[LEGACY]);
  assert.ok(m.generated[".cursorrules"]);
  assert.ok(m.generated[".gemini/config.yaml"]);
  const settings = readJson(join(dir, SETTINGS));
  assert.ok(settings.permissions.deny.length > 0, "deny rules from the template survive the hooks merge");
});

test("integration (T89): apply after a manifest hooks change writes settings.json#hooks; a second apply is a no-op", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO, "--name", "x"]);
  const m = readJson(join(dir, "claude.manifest.json"));
  m.hooks.postFeature = ["feature-audit"];
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  run(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  const settings = readJson(join(dir, SETTINGS));
  assert.ok(settings.hooks.PostToolUse);
  assert.ok(settings.permissions, "permissions key kept");
  assert.ok(!existsSync(join(dir, LEGACY)));

  const before = readFileSync(join(dir, SETTINGS), "utf8");
  const manifestBefore = readFileSync(join(dir, "claude.manifest.json"), "utf8");
  run(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(readFileSync(join(dir, SETTINGS), "utf8"), before);
  assert.equal(readFileSync(join(dir, "claude.manifest.json"), "utf8"), manifestBefore, "no-op apply leaves the manifest alone");
});

test("integration (T89): hand-edited generated hook produces conflict on apply", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO, "--name", "x"]);
  const m = readJson(join(dir, "claude.manifest.json"));
  m.hooks.postFeature = ["feature-audit"];
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));
  run(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);

  const s = readJson(join(dir, SETTINGS));
  s.hooks.PostToolUse[0].hooks[0].command = "echo edited-by-hand";
  writeFileSync(join(dir, SETTINGS), JSON.stringify(s, null, 2) + "\n");

  const r = runCapture(["apply", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(r.exitCode, 2);
  assert.match(r.stdout, /conflict/i);
  assert.equal(readJson(join(dir, SETTINGS)).hooks.PostToolUse[0].hooks[0].command, "echo edited-by-hand");
});

test("doctor (T89): a leftover .claude/hooks/hooks.json is reported as stale, not deleted", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--skills-source", SKILLS_REPO, "--name", "x"]);
  mkdirSync(join(dir, ".claude/hooks"), { recursive: true });
  writeFileSync(join(dir, LEGACY), '{"hooks":{}}\n');
  const r = runCapture(["doctor", "--cwd", dir, "--skills-source", SKILLS_REPO]);
  assert.equal(r.exitCode, 1, "warn-level finding exits 1");
  assert.match(r.stdout, /legacy-hooks/);
  assert.match(r.stdout, /stale/);
  assert.ok(existsSync(join(dir, LEGACY)), "doctor reports only");
});
