const BEGIN = /<!--\s*CLAUDE-BOOTSTRAP:BEGIN\s+([a-z][a-z0-9-]*)\s*-->/g;

export function parseBlocks(source) {
  const segments = [];
  const blocks = new Map();
  let cursor = 0;

  BEGIN.lastIndex = 0;
  let match;
  while ((match = BEGIN.exec(source)) !== null) {
    const id = match[1];
    const beginStart = match.index;
    const beginEnd = BEGIN.lastIndex;

    const endTag = `<!-- CLAUDE-BOOTSTRAP:END ${id} -->`;
    const endStart = source.indexOf(endTag, beginEnd);
    if (endStart === -1) {
      throw new Error(`unterminated managed block '${id}' starting at offset ${beginStart}`);
    }
    const endEnd = endStart + endTag.length;

    if (blocks.has(id)) {
      throw new Error(`duplicate managed block '${id}'`);
    }

    if (beginStart > cursor) {
      segments.push({ kind: "text", value: source.slice(cursor, beginStart) });
    }

    const inner = source.slice(beginEnd, endStart);
    const content = stripBoundaryNewlines(inner);
    segments.push({ kind: "block", id, content });
    blocks.set(id, content);

    cursor = endEnd;
    BEGIN.lastIndex = endEnd;
  }

  if (cursor < source.length) {
    segments.push({ kind: "text", value: source.slice(cursor) });
  }

  return { segments, blocks };
}

function stripBoundaryNewlines(s) {
  let out = s;
  if (out.startsWith("\r\n")) out = out.slice(2);
  else if (out.startsWith("\n")) out = out.slice(1);
  if (out.endsWith("\r\n")) out = out.slice(0, -2);
  else if (out.endsWith("\n")) out = out.slice(0, -1);
  return out;
}

export function renderBlock(id, content) {
  return `<!-- CLAUDE-BOOTSTRAP:BEGIN ${id} -->\n${content}\n<!-- CLAUDE-BOOTSTRAP:END ${id} -->`;
}
