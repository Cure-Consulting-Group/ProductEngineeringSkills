import { parseBlocks, renderBlock } from "./parse.mjs";
import { sha256 } from "./hash.mjs";

export const DECISIONS = Object.freeze({
  CREATE: "create",
  UPDATE: "update",
  CONFLICT: "conflict",
  UNCHANGED: "unchanged",
});

export function planFile({ filePath, existing, rendered, storedHashes }) {
  if (existing == null) {
    const { blocks } = parseBlocks(rendered);
    return {
      filePath,
      decision: DECISIONS.CREATE,
      nextContent: rendered,
      nextHashes: hashesFor(filePath, blocks),
      blockReports: [...blocks.keys()].map((id) => ({ id, status: "new" })),
      conflicts: [],
    };
  }

  const renderedParsed = parseBlocks(rendered);
  const existingParsed = parseBlocks(existing);

  const blockReports = [];
  const conflicts = [];
  const updatedBlocks = new Map();

  for (const [id, renderedContent] of renderedParsed.blocks) {
    const existingContent = existingParsed.blocks.get(id);
    const storedHash = storedHashes?.[`${filePath}#${id}`];

    if (existingContent == null) {
      updatedBlocks.set(id, renderedContent);
      blockReports.push({ id, status: "added" });
      continue;
    }

    const existingHash = sha256(existingContent);
    const renderedHash = sha256(renderedContent);

    if (existingHash === renderedHash) {
      updatedBlocks.set(id, existingContent);
      blockReports.push({ id, status: "unchanged" });
      continue;
    }

    if (storedHash && storedHash !== existingHash) {
      updatedBlocks.set(id, existingContent);
      blockReports.push({ id, status: "conflict" });
      conflicts.push({
        id,
        path: `${filePath}#${id}`,
        storedHash,
        existingHash,
        renderedContent,
      });
      continue;
    }

    updatedBlocks.set(id, renderedContent);
    blockReports.push({ id, status: "updated" });
  }

  for (const id of existingParsed.blocks.keys()) {
    if (!renderedParsed.blocks.has(id)) {
      blockReports.push({ id, status: "removed" });
    }
  }

  const nextContent = composeFromExisting(existingParsed, renderedParsed, updatedBlocks);
  const decision = pickDecision(existing, nextContent, conflicts.length > 0);
  const nextHashes = hashesFor(filePath, updatedBlocks);

  return { filePath, decision, nextContent, nextHashes, blockReports, conflicts };
}

function composeFromExisting(existingParsed, renderedParsed, updatedBlocks) {
  const seen = new Set();
  const out = [];
  for (const seg of existingParsed.segments) {
    if (seg.kind === "text") {
      out.push(seg.value);
      continue;
    }
    if (updatedBlocks.has(seg.id)) {
      out.push(renderBlock(seg.id, updatedBlocks.get(seg.id)));
      seen.add(seg.id);
    }
  }
  for (const [id, content] of updatedBlocks) {
    if (!seen.has(id)) {
      const sep = out.length > 0 && !out[out.length - 1].endsWith("\n") ? "\n\n" : "\n";
      out.push(sep + renderBlock(id, content) + "\n");
    }
  }
  return out.join("");
}

function pickDecision(existing, nextContent, hasConflicts) {
  if (hasConflicts) return DECISIONS.CONFLICT;
  if (existing === nextContent) return DECISIONS.UNCHANGED;
  return DECISIONS.UPDATE;
}

function hashesFor(filePath, blocks) {
  const out = {};
  for (const [id, content] of blocks) {
    out[`${filePath}#${id}`] = sha256(content);
  }
  return out;
}
