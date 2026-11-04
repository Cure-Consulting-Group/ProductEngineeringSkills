// T89: the hooks that manifest.hooks describes must live in the `hooks` key of
// .claude/settings.json. Claude Code reads project hooks only from
// .claude/settings.json and .claude/settings.local.json; a .claude/hooks/hooks.json
// is never loaded (verified against code.claude.com/docs/en/hooks, 2026-11-03).
//
// The merge keeps every other settings key and every hook the user wrote. Generated
// groups are recognised by their command strings, which the manifest records under
// manifest.generated[SETTINGS_HOOKS_KEY].commands, so a re-run replaces them in place
// and never duplicates them. A generated command that is no longer on disk (edited or
// removed by hand) is a CONFLICT, the same decision the other generated files use.
import { renderTemplate } from "../template/render.mjs";
import { sha256 } from "../blocks/hash.mjs";

export const SETTINGS_PATH = ".claude/settings.json";
export const SETTINGS_HOOKS_KEY = `${SETTINGS_PATH}#hooks`;
export const HOOKS_TEMPLATE = "claude-hooks.json.ejs";
export const LEGACY_HOOKS_PATH = ".claude/hooks/hooks.json";

export function renderHooks(manifest) {
  const parsed = JSON.parse(renderTemplate(HOOKS_TEMPLATE, manifest));
  return parsed.hooks ?? {};
}

export function commandsOf(hooks) {
  const out = [];
  for (const groups of Object.values(hooks ?? {})) {
    for (const g of groups ?? []) for (const h of g.hooks ?? []) if (h.command) out.push(h.command);
  }
  return out;
}

function isGenerated(group, known) {
  const cmds = (group.hooks ?? []).map((h) => h.command);
  return cmds.length > 0 && cmds.every((c) => known.has(c));
}

/**
 * Merge the rendered hooks into the existing settings object.
 * Returns { settings, foundStored } where foundStored counts stored generated
 * commands still present on disk (for conflict detection).
 */
export function mergeHooks({ settings, rendered, storedCommands = [] }) {
  const renderedCommands = commandsOf(rendered);
  const known = new Set([...storedCommands, ...renderedCommands]);
  const existing = settings.hooks && typeof settings.hooks === "object" ? settings.hooks : {};
  const stored = new Set(storedCommands);
  let foundStored = 0;
  const next = {};

  for (const [event, groups] of Object.entries(existing)) {
    const kept = [];
    for (const g of groups ?? []) {
      if (isGenerated(g, known)) {
        for (const h of g.hooks ?? []) if (stored.has(h.command)) foundStored++;
        continue;
      }
      kept.push(g);
    }
    if (kept.length > 0) next[event] = kept;
  }
  for (const [event, groups] of Object.entries(rendered)) {
    if (!groups?.length) continue;
    next[event] = [...(next[event] ?? []), ...groups];
  }

  const out = { ...settings };
  if (Object.keys(next).length > 0) out.hooks = next;
  else delete out.hooks;
  return { settings: out, foundStored, renderedCommands };
}

export function planSettingsHooks({ manifest, baseText }) {
  const rendered = renderHooks(manifest);
  const storedEntry = manifest.generated?.[SETTINGS_HOOKS_KEY];
  const storedCommands = storedEntry?.commands ?? [];
  const renderedHash = sha256(JSON.stringify(rendered));

  let base = {};
  let parseError = null;
  if (baseText != null && baseText.trim() !== "") {
    try { base = JSON.parse(baseText); } catch (e) { parseError = e; }
  }

  const common = { target: SETTINGS_HOOKS_KEY, writePath: SETTINGS_PATH, template: HOOKS_TEMPLATE, renderedHash };

  if (parseError) {
    return { ...common, decision: "conflict", rendered: JSON.stringify({ hooks: rendered }, null, 2) + "\n",
      targetContent: baseText, targetHash: storedEntry?.hash ?? renderedHash, commands: storedCommands,
      reason: `${SETTINGS_PATH} is not valid JSON` };
  }

  const { settings, foundStored, renderedCommands } = mergeHooks({ settings: base, rendered, storedCommands });

  if (storedCommands.length > 0 && foundStored < storedCommands.length) {
    return { ...common, decision: "conflict", rendered: JSON.stringify({ hooks: rendered }, null, 2) + "\n",
      targetContent: baseText, targetHash: storedEntry?.hash ?? renderedHash, commands: storedCommands,
      reason: "a generated hook was edited or removed by hand" };
  }

  // Unchanged when the merge adds and removes nothing: compare objects, not text,
  // so the template's own formatting of settings.json is never rewritten.
  const sameShape = JSON.stringify(settings) === JSON.stringify(base);
  if (baseText == null && renderedCommands.length === 0) {
    return { ...common, decision: "unchanged", rendered: null, targetContent: null, targetHash: renderedHash, commands: [] };
  }
  if (baseText != null && sameShape) {
    return { ...common, decision: "unchanged", rendered: baseText, targetContent: baseText, targetHash: sha256(baseText), commands: renderedCommands };
  }
  const nextText = JSON.stringify(settings, null, 2) + "\n";
  return { ...common, decision: baseText == null ? "create" : "update", rendered: nextText, targetContent: baseText,
    targetHash: baseText == null ? renderedHash : sha256(baseText), commands: renderedCommands };
}
