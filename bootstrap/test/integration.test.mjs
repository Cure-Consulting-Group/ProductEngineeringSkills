import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync, existsSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const CLI = resolve(here, "../bin/claude-bootstrap.mjs");

function tmp() {
  return mkdtempSync(join(tmpdir(), "claude-bootstrap-int-"));
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

test("init: scaffolds CLAUDE.md, STATE.md, .claude/settings.json and a valid manifest in an empty dir", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "fixture-cli"]);

  assert.ok(existsSync(join(dir, "claude.manifest.json")));
  assert.ok(existsSync(join(dir, "CLAUDE.md")));
  assert.ok(existsSync(join(dir, "STATE.md")));
  assert.ok(existsSync(join(dir, ".claude/settings.json")));

  const m = readJson(join(dir, "claude.manifest.json"));
  assert.equal(m.project.name, "fixture-cli");
  assert.equal(m.bootstrap.skillsRepoVersion, "5.0.0");
  assert.equal(m.manifestVersion, 1);
  assert.ok(m.managedBlocks["CLAUDE.md#preamble"], "manifest records block hashes");
});

test("init: detected stack from package.json populates project.stack and type=web", () => {
  const dir = tmp();
  writeFileSync(join(dir, "package.json"), JSON.stringify({
    name: "vendly-web", dependencies: { next: "14", react: "18", stripe: "14" },
  }));
  writeFileSync(join(dir, "tsconfig.json"), "{}");

  run(["init", "--cwd", dir, "--skills-version", "5.0.0",
       "--skill", "stripe-integration", "--skill", "feature-audit",
       "--agent", "pr-reviewer"]);

  const m = readJson(join(dir, "claude.manifest.json"));
  assert.equal(m.project.type, "web");
  assert.equal(m.project.primaryLanguage, "typescript");
  for (const s of ["nextjs", "react", "stripe"]) assert.ok(m.project.stack.includes(s));
  assert.deepEqual(m.skills.active, ["stripe-integration", "feature-audit"]);
  assert.deepEqual(m.agents.active, ["pr-reviewer"]);

  const claudeMd = readFileSync(join(dir, "CLAUDE.md"), "utf8");
  assert.match(claudeMd, /stripe-integration/);
  assert.match(claudeMd, /pr-reviewer/);
});

test("init: refuses to run twice without --force", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x"]);
  const r = runCapture(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x"]);
  assert.equal(r.exitCode, 1);
  assert.match(r.stderr, /already exists/);
});

test("init --dry-run: writes nothing", () => {
  const dir = tmp();
  const r = run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x", "--dry-run"]);
  assert.match(r, /dry-run/);
  assert.deepEqual(readdirSync(dir), []);
});

test("apply is idempotent: second run is all UNCHANGED", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x"]);
  const out = run(["apply", "--cwd", dir]);
  for (const line of out.split("\n")) {
    if (line.startsWith("  [")) {
      assert.match(line, /unchanged/, `expected unchanged, got: ${line}`);
    }
  }
});

test("apply preserves user content outside managed blocks", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x"]);
  const claudePath = join(dir, "CLAUDE.md");
  const before = readFileSync(claudePath, "utf8");
  const userAddition = "\n## My team's notes\nDo not delete.\n";
  writeFileSync(claudePath, before + userAddition);

  run(["apply", "--cwd", dir]);
  const after = readFileSync(claudePath, "utf8");
  assert.match(after, /My team's notes/);
  assert.match(after, /Do not delete/);
});

test("apply detects conflict when user edits inside a managed block", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x"]);
  const claudePath = join(dir, "CLAUDE.md");
  const original = readFileSync(claudePath, "utf8");
  const tampered = original.replace(
    "Edits inside `CLAUDE-BOOTSTRAP:BEGIN/END`",
    "USER MODIFIED THIS — Edits inside `CLAUDE-BOOTSTRAP:BEGIN/END`",
  );
  writeFileSync(claudePath, tampered);

  const m = readJson(join(dir, "claude.manifest.json"));
  m.bootstrap.skillsRepoVersion = "5.0.1";
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  const r = runCapture(["apply", "--cwd", dir]);
  assert.equal(r.exitCode, 2, "apply should exit 2 on conflict");
  assert.match(r.stdout, /conflict/);

  const post = readFileSync(claudePath, "utf8");
  assert.match(post, /USER MODIFIED THIS/, "user-edited block content preserved");

  const upgradesDir = join(dir, ".claude/upgrades");
  assert.ok(existsSync(upgradesDir), "upgrades dir created");
  const conflictFiles = readdirSync(upgradesDir);
  assert.ok(conflictFiles.length >= 1, "at least one .conflict file written");
});

test("apply with HIPAA flag flipped post-init re-renders to add the HIPAA block", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x", "--install-mode", "vendored"]);
  const claudeMd1 = readFileSync(join(dir, "CLAUDE.md"), "utf8");
  assert.doesNotMatch(claudeMd1, /HIPAA notes/);

  const m = readJson(join(dir, "claude.manifest.json"));
  m.compliance.hipaa = true;
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  run(["apply", "--cwd", dir]);
  const claudeMd2 = readFileSync(join(dir, "CLAUDE.md"), "utf8");
  assert.match(claudeMd2, /HIPAA notes/);

  const m2 = readJson(join(dir, "claude.manifest.json"));
  assert.ok(m2.managedBlocks["CLAUDE.md#compliance-hipaa"], "new block hash recorded");
});

test("apply rejects manifest with cross-field violation (HIPAA + symlink)", () => {
  const dir = tmp();
  run(["init", "--cwd", dir, "--skills-version", "5.0.0", "--name", "x"]);

  const m = readJson(join(dir, "claude.manifest.json"));
  m.compliance.hipaa = true;
  m.bootstrap.installMode = "symlink";
  writeFileSync(join(dir, "claude.manifest.json"), JSON.stringify(m, null, 2));

  const r = runCapture(["apply", "--cwd", dir]);
  assert.equal(r.exitCode, 1);
  assert.match(r.stderr, /symlink.*forbidden|forbidden.*symlink/i);
});

test("init without --skills-version fails clearly", () => {
  const dir = tmp();
  const r = runCapture(["init", "--cwd", dir, "--name", "x"]);
  assert.equal(r.exitCode, 1);
  assert.match(r.stderr, /skills-version/);
});

test("version command prints version", () => {
  const out = run(["version"]);
  assert.match(out, /^\d+\.\d+\.\d+\n$/);
});

test("help command prints usage", () => {
  const out = run(["help"]);
  assert.match(out, /Usage:/);
  assert.match(out, /init/);
  assert.match(out, /apply/);
});
