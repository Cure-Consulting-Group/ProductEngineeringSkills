import { test } from "node:test";
import assert from "node:assert/strict";
import { renderTemplate, TEMPLATE_FILES } from "../src/template/render.mjs";
import { createManifest } from "../src/manifest/index.mjs";
import { parseBlocks } from "../src/blocks/index.mjs";

const baseInput = {
  projectName: "vendly-web",
  projectType: "web",
  primaryLanguage: "typescript",
  cliVersion: "0.1.0",
  skillsRepoVersion: "5.0.0",
};

test("CLAUDE.md template renders with project + skills + agents", () => {
  const m = createManifest({
    ...baseInput,
    stack: ["nextjs", "firebase"],
    activeSkills: ["stripe-integration", "firebase-architect"],
    activeAgents: ["pr-reviewer"],
    hooks: { preCommit: ["security-review"], postFeature: ["feature-audit"], prePR: ["pr-reviewer"] },
  });
  const out = renderTemplate("CLAUDE.md.ejs", m);
  assert.match(out, /vendly-web/);
  assert.match(out, /nextjs, firebase/);
  assert.match(out, /stripe-integration/);
  assert.match(out, /firebase-architect/);
  assert.match(out, /pr-reviewer/);
});

test("CLAUDE.md template emits valid managed blocks (parseable)", () => {
  const m = createManifest(baseInput);
  const out = renderTemplate("CLAUDE.md.ejs", m);
  const { blocks } = parseBlocks(out);
  assert.ok(blocks.has("preamble"));
  assert.ok(blocks.has("active-skills"));
  assert.ok(blocks.has("active-agents"));
  assert.ok(blocks.has("lifecycle-hooks"));
});

test("CLAUDE.md: HIPAA block appears only when compliance.hipaa is true", () => {
  const off = renderTemplate("CLAUDE.md.ejs", createManifest(baseInput));
  assert.doesNotMatch(off, /HIPAA notes/);
  const on = renderTemplate(
    "CLAUDE.md.ejs",
    createManifest({ ...baseInput, compliance: { hipaa: true }, installMode: "vendored" }),
  );
  assert.match(on, /HIPAA notes/);
  const { blocks } = parseBlocks(on);
  assert.ok(blocks.has("compliance-hipaa"));
});

test("CLAUDE.md: PCI + GDPR blocks compose independently", () => {
  const out = renderTemplate(
    "CLAUDE.md.ejs",
    createManifest({ ...baseInput, compliance: { pci: true, gdpr: true } }),
  );
  assert.match(out, /PCI notes/);
  assert.match(out, /GDPR notes/);
});

test("STATE.md template renders header block", () => {
  const m = createManifest({ ...baseInput, skillsRepoSha: "4a88ae5" });
  const out = renderTemplate("STATE.md.ejs", m);
  const { blocks } = parseBlocks(out);
  assert.ok(blocks.has("header"));
  assert.match(out, /4a88ae5/);
  assert.match(out, /v5\.0\.0/);
});

test("settings.json template renders parseable JSON", () => {
  const m = createManifest(baseInput);
  const out = renderTemplate("claude-settings.json.ejs", m);
  const parsed = JSON.parse(out);
  assert.equal(parsed.project.name, "vendly-web");
  assert.equal(parsed.project.skillsRepoVersion, "5.0.0");
  assert.ok(parsed.permissions.deny.length > 0);
});

test("TEMPLATE_FILES lists known mappings", () => {
  const targets = TEMPLATE_FILES.map((t) => t.target);
  assert.deepEqual(new Set(targets), new Set(["CLAUDE.md", "STATE.md", ".claude/settings.json"]));
});
