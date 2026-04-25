import { test } from "node:test";
import assert from "node:assert/strict";
import { validateManifest, createManifest, manifestSchemaId } from "../src/manifest/index.mjs";

const baseInput = {
  projectName: "vendly-web",
  projectType: "web",
  primaryLanguage: "typescript",
  cliVersion: "0.1.0",
  skillsRepoVersion: "5.0.0",
};

test("schema id is the canonical URL", () => {
  assert.equal(manifestSchemaId, "https://cure.dev/schemas/claude-manifest/v1.json");
});

test("createManifest produces a valid minimal manifest", () => {
  const m = createManifest(baseInput);
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, true, `expected valid, got errors: ${JSON.stringify(errors)}`);
});

test("createManifest: missing required input throws", () => {
  assert.throws(() => createManifest({ ...baseInput, projectName: undefined }), /projectName/);
  assert.throws(() => createManifest({ ...baseInput, primaryLanguage: undefined }), /primaryLanguage/);
  assert.throws(() => createManifest({ ...baseInput, skillsRepoVersion: undefined }), /skillsRepoVersion/);
});

test("createManifest accepts compliance, skills, agents, hooks, sha", () => {
  const m = createManifest({
    ...baseInput,
    skillsRepoSha: "4a88ae5",
    stack: ["nextjs", "firebase", "stripe"],
    compliance: { gdpr: true, pci: true },
    activeSkills: ["stripe-integration", "firebase-architect", "feature-audit"],
    activeAgents: ["pr-reviewer", "qa-engineer"],
    hooks: { preCommit: ["security-review"], postFeature: ["feature-audit"], prePR: ["pr-reviewer"] },
    owners: ["rashad@cure.dev"],
    phase: "beta",
  });
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, true, JSON.stringify(errors));
  assert.equal(m.bootstrap.skillsRepoSha, "4a88ae5");
  assert.equal(m.compliance.gdpr, true);
  assert.equal(m.project.phase, "beta");
});

test("validateManifest: rejects missing required top-level fields", () => {
  const m = createManifest(baseInput);
  delete m.project;
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.code === "required" && e.params?.missingProperty === "project"));
});

test("validateManifest: rejects bad enum on project.type", () => {
  const m = createManifest(baseInput);
  m.project.type = "desktop";
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.path === "/project/type"));
});

test("validateManifest: rejects non-semver skillsRepoVersion", () => {
  const m = createManifest(baseInput);
  m.bootstrap.skillsRepoVersion = "v5";
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.path === "/bootstrap/skillsRepoVersion"));
});

test("validateManifest: rejects non-kebab project.name", () => {
  const m = createManifest({ ...baseInput, projectName: "Vendly_Web" });
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.path === "/project/name"));
});

test("validateManifest: rejects unknown installMode", () => {
  const m = createManifest(baseInput);
  m.bootstrap.installMode = "yolo";
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.path === "/bootstrap/installMode"));
});

test("validateManifest: cross-field — HIPAA + symlink is rejected", () => {
  const m = createManifest({ ...baseInput, compliance: { hipaa: true }, installMode: "symlink" });
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  const err = errors.find((e) => e.code === "compliance/installMode");
  assert.ok(err, "expected compliance/installMode error");
  assert.deepEqual(err.params.triggered, ["hipaa"]);
});

test("validateManifest: cross-field — PCI + symlink is rejected", () => {
  const m = createManifest({ ...baseInput, compliance: { pci: true }, installMode: "symlink" });
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.code === "compliance/installMode"));
});

test("validateManifest: cross-field — HIPAA + vendored is allowed", () => {
  const m = createManifest({ ...baseInput, compliance: { hipaa: true }, installMode: "vendored" });
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, true, JSON.stringify(errors));
});

test("validateManifest: cross-field — GDPR alone does not constrain installMode", () => {
  const m = createManifest({ ...baseInput, compliance: { gdpr: true }, installMode: "symlink" });
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, true, JSON.stringify(errors));
});

test("validateManifest: cross-field — skill in both active and disabled is rejected", () => {
  const m = createManifest({ ...baseInput, activeSkills: ["feature-audit"] });
  m.skills.disabled = ["feature-audit"];
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.code === "skills/conflict"));
});

test("validateManifest: cross-field — pinned skill must be active", () => {
  const m = createManifest({ ...baseInput, activeSkills: ["feature-audit"] });
  m.skills.pinned = { "stripe-integration": "5.0.0" };
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.code === "skills/pinned-not-active"));
});

test("validateManifest: managedBlocks must be sha256 hex", () => {
  const m = createManifest(baseInput);
  m.managedBlocks = { "CLAUDE.md#preamble": "not-a-hash" };
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
});

test("validateManifest: managedBlocks accepts valid sha256", () => {
  const m = createManifest(baseInput);
  m.managedBlocks = { "CLAUDE.md#preamble": "a".repeat(64) };
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, true, JSON.stringify(errors));
});

test("validateManifest: rejects unknown top-level key", () => {
  const m = createManifest(baseInput);
  m.surprise = true;
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.code === "additionalProperties"));
});

test("validateManifest: rejects bad email in owners", () => {
  const m = createManifest({ ...baseInput, owners: ["not-an-email"] });
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.path?.startsWith("/project/owners")));
});

test("validateManifest: rejects bad date-time on lastAppliedAt", () => {
  const m = createManifest(baseInput);
  m.bootstrap.lastAppliedAt = "yesterday";
  const { valid, errors } = validateManifest(m);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.path === "/bootstrap/lastAppliedAt"));
});
