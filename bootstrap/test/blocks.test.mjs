import { test } from "node:test";
import assert from "node:assert/strict";
import { parseBlocks, renderBlock, planFile, sha256, DECISIONS } from "../src/blocks/index.mjs";

const fence = (id, content) => `<!-- CLAUDE-BOOTSTRAP:BEGIN ${id} -->\n${content}\n<!-- CLAUDE-BOOTSTRAP:END ${id} -->`;

test("parseBlocks: extracts a single block", () => {
  const src = `head\n${fence("preamble", "managed body")}\ntail`;
  const { blocks } = parseBlocks(src);
  assert.equal(blocks.size, 1);
  assert.equal(blocks.get("preamble"), "managed body");
});

test("parseBlocks: extracts multiple blocks and preserves text segments", () => {
  const src = [
    "before\n",
    fence("a", "alpha"),
    "\n\nmiddle\n",
    fence("b", "beta"),
    "\nafter",
  ].join("");
  const { segments, blocks } = parseBlocks(src);
  assert.equal(blocks.size, 2);
  assert.equal(blocks.get("a"), "alpha");
  assert.equal(blocks.get("b"), "beta");
  const texts = segments.filter((s) => s.kind === "text").map((s) => s.value);
  assert.deepEqual(texts, ["before\n", "\n\nmiddle\n", "\nafter"]);
});

test("parseBlocks: throws on unterminated block", () => {
  const src = "<!-- CLAUDE-BOOTSTRAP:BEGIN x -->\noops\n";
  assert.throws(() => parseBlocks(src), /unterminated/);
});

test("parseBlocks: throws on duplicate block id", () => {
  const src = `${fence("dup", "1")}\n${fence("dup", "2")}`;
  assert.throws(() => parseBlocks(src), /duplicate/);
});

test("parseBlocks: tolerates no blocks", () => {
  const { segments, blocks } = parseBlocks("plain content");
  assert.equal(blocks.size, 0);
  assert.deepEqual(segments, [{ kind: "text", value: "plain content" }]);
});

test("renderBlock: produces canonical fenced output", () => {
  const out = renderBlock("preamble", "hello");
  assert.equal(out, "<!-- CLAUDE-BOOTSTRAP:BEGIN preamble -->\nhello\n<!-- CLAUDE-BOOTSTRAP:END preamble -->");
});

test("planFile: CREATE when file does not exist", () => {
  const rendered = `intro\n${fence("a", "v1")}\nend`;
  const plan = planFile({ filePath: "CLAUDE.md", existing: null, rendered, storedHashes: {} });
  assert.equal(plan.decision, DECISIONS.CREATE);
  assert.equal(plan.nextContent, rendered);
  assert.equal(plan.nextHashes["CLAUDE.md#a"], sha256("v1"));
  assert.deepEqual(plan.blockReports, [{ id: "a", status: "new" }]);
});

test("planFile: UNCHANGED when rendered equals existing", () => {
  const same = `intro\n${fence("a", "v1")}\nend`;
  const plan = planFile({
    filePath: "CLAUDE.md",
    existing: same,
    rendered: same,
    storedHashes: { "CLAUDE.md#a": sha256("v1") },
  });
  assert.equal(plan.decision, DECISIONS.UNCHANGED);
  assert.equal(plan.nextContent, same);
});

test("planFile: UPDATE when block content differs and stored hash matches existing", () => {
  const existing = `intro\n${fence("a", "v1")}\nend`;
  const rendered = `intro\n${fence("a", "v2")}\nend`;
  const plan = planFile({
    filePath: "CLAUDE.md",
    existing,
    rendered,
    storedHashes: { "CLAUDE.md#a": sha256("v1") },
  });
  assert.equal(plan.decision, DECISIONS.UPDATE);
  assert.match(plan.nextContent, /v2/);
  assert.doesNotMatch(plan.nextContent, /v1/);
  assert.equal(plan.nextHashes["CLAUDE.md#a"], sha256("v2"));
  assert.equal(plan.blockReports[0].status, "updated");
});

test("planFile: CONFLICT when user edited inside block (stored hash mismatches existing)", () => {
  const userEdited = `intro\n${fence("a", "v1-user-edited")}\nend`;
  const rendered = `intro\n${fence("a", "v2")}\nend`;
  const plan = planFile({
    filePath: "CLAUDE.md",
    existing: userEdited,
    rendered,
    storedHashes: { "CLAUDE.md#a": sha256("v1") },
  });
  assert.equal(plan.decision, DECISIONS.CONFLICT);
  assert.match(plan.nextContent, /v1-user-edited/, "user content preserved on conflict");
  assert.equal(plan.conflicts.length, 1);
  assert.equal(plan.conflicts[0].id, "a");
  assert.equal(plan.conflicts[0].renderedContent, "v2");
  assert.equal(plan.blockReports[0].status, "conflict");
});

test("planFile: preserves text outside blocks across upgrade", () => {
  const existing = [
    "## My team's notes\nDo not delete this.\n",
    fence("preamble", "v1"),
    "\n## Another section\nKeep me too.\n",
  ].join("");
  const rendered = `${fence("preamble", "v2")}`;
  const plan = planFile({
    filePath: "CLAUDE.md",
    existing,
    rendered,
    storedHashes: { "CLAUDE.md#preamble": sha256("v1") },
  });
  assert.equal(plan.decision, DECISIONS.UPDATE);
  assert.match(plan.nextContent, /My team's notes/);
  assert.match(plan.nextContent, /Another section/);
  assert.match(plan.nextContent, /v2/);
});

test("planFile: appends new block when template adds one not in existing", () => {
  const existing = `${fence("a", "alpha")}\n`;
  const rendered = `${fence("a", "alpha")}\n${fence("b", "beta")}`;
  const plan = planFile({
    filePath: "CLAUDE.md",
    existing,
    rendered,
    storedHashes: { "CLAUDE.md#a": sha256("alpha") },
  });
  assert.equal(plan.decision, DECISIONS.UPDATE);
  assert.match(plan.nextContent, /BEGIN b/);
  assert.match(plan.nextContent, /beta/);
  assert.equal(plan.nextHashes["CLAUDE.md#b"], sha256("beta"));
  const bReport = plan.blockReports.find((r) => r.id === "b");
  assert.equal(bReport.status, "added");
});

test("planFile: reports removed block but does not modify file content for it", () => {
  const existing = `${fence("a", "alpha")}\n${fence("b", "beta")}`;
  const rendered = `${fence("a", "alpha-v2")}`;
  const plan = planFile({
    filePath: "CLAUDE.md",
    existing,
    rendered,
    storedHashes: { "CLAUDE.md#a": sha256("alpha"), "CLAUDE.md#b": sha256("beta") },
  });
  const removed = plan.blockReports.find((r) => r.id === "b");
  assert.equal(removed.status, "removed");
});

test("planFile: idempotency — running plan with prior nextContent yields UNCHANGED", () => {
  const rendered = `intro\n${fence("a", "v1")}\nend`;
  const first = planFile({ filePath: "CLAUDE.md", existing: null, rendered, storedHashes: {} });
  const second = planFile({
    filePath: "CLAUDE.md",
    existing: first.nextContent,
    rendered,
    storedHashes: first.nextHashes,
  });
  assert.equal(second.decision, DECISIONS.UNCHANGED);
});

test("planFile: first-time apply with no stored hash but block content matches rendered → unchanged", () => {
  const same = `${fence("a", "v1")}`;
  const plan = planFile({ filePath: "CLAUDE.md", existing: same, rendered: same, storedHashes: {} });
  assert.equal(plan.decision, DECISIONS.UNCHANGED);
});

test("planFile: first-time apply, no stored hash, block content differs → not a conflict, treats as update", () => {
  const existing = `${fence("a", "old")}`;
  const rendered = `${fence("a", "new")}`;
  const plan = planFile({ filePath: "CLAUDE.md", existing, rendered, storedHashes: {} });
  assert.equal(plan.decision, DECISIONS.UPDATE);
  assert.match(plan.nextContent, /new/);
});
