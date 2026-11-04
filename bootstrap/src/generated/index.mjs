import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { renderTemplate } from "../template/render.mjs";
import { sha256 } from "../blocks/hash.mjs";
import { planSettingsHooks, SETTINGS_HOOKS_KEY, LEGACY_HOOKS_PATH } from "./settings-hooks.mjs";

export { SETTINGS_HOOKS_KEY, LEGACY_HOOKS_PATH, SETTINGS_PATH, HOOKS_TEMPLATE } from "./settings-hooks.mjs";

export const GENERATED_DECISIONS = Object.freeze({
  CREATE: "create",
  UPDATE: "update",
  CONFLICT: "conflict",
  UNCHANGED: "unchanged",
});

// Hooks are not a file of their own: they merge into .claude/settings.json#hooks
// (see settings-hooks.mjs, T89). Claude Code never loads .claude/hooks/hooks.json.
export const GENERATED_FILES = Object.freeze([
  { template: "cursorrules.ejs",       target: ".cursorrules" },
  { template: "gemini-config.yaml.ejs", target: ".gemini/config.yaml" },
]);

export function planGenerated({ cwd, manifest, files = GENERATED_FILES, settingsBase }) {
  const stored = manifest.generated ?? {};
  const decisions = [];

  // settingsBase: the settings.json text the apply will have written by the time the
  // generated step runs (the template plan's nextContent), else what is on disk.
  const settingsPath = join(cwd, ".claude/settings.json");
  const baseText = settingsBase !== undefined ? settingsBase : existsSync(settingsPath) ? readFileSync(settingsPath, "utf8") : null;
  decisions.push(planSettingsHooks({ manifest, baseText }));

  for (const { template, target } of files) {
    const rendered = renderTemplate(template, manifest);
    const renderedHash = sha256(rendered);
    const fullTarget = join(cwd, target);
    const targetExists = existsSync(fullTarget);
    const targetContent = targetExists ? readFileSync(fullTarget, "utf8") : null;
    const targetHash = targetContent != null ? sha256(targetContent) : null;
    const storedEntry = stored[target];

    let decision;
    if (!targetExists) {
      decision = GENERATED_DECISIONS.CREATE;
    } else if (storedEntry && storedEntry.hash !== targetHash) {
      decision = GENERATED_DECISIONS.CONFLICT;
    } else if (targetHash === renderedHash) {
      decision = GENERATED_DECISIONS.UNCHANGED;
    } else {
      decision = GENERATED_DECISIONS.UPDATE;
    }

    decisions.push({ target, writePath: target, template, rendered, renderedHash, targetContent, targetHash, decision });
  }

  return { decisions };
}

export function applyGenerated({ cwd, plan, write = true }) {
  const writes = [];
  const conflicts = [];
  const nextGenerated = {};

  for (const d of plan.decisions) {
    switch (d.decision) {
      case GENERATED_DECISIONS.CREATE:
      case GENERATED_DECISIONS.UPDATE:
        writes.push(d);
        nextGenerated[d.target] = entryFor(d, d.renderedHash);
        break;
      case GENERATED_DECISIONS.UNCHANGED:
        nextGenerated[d.target] = entryFor(d, d.renderedHash);
        break;
      case GENERATED_DECISIONS.CONFLICT:
        conflicts.push(d);
        nextGenerated[d.target] = entryFor(d, d.targetHash);
        break;
    }
  }

  if (write) {
    for (const w of writes) {
      const full = join(cwd, w.writePath ?? w.target);
      mkdirSync(dirname(full), { recursive: true });
      writeFileSync(full, w.rendered, "utf8");
    }
    for (const c of conflicts) {
      const conflictPath = join(cwd, ".claude", "upgrades", `${c.target.replace(/[\/]/g, "_")}.conflict`);
      mkdirSync(dirname(conflictPath), { recursive: true });
      writeFileSync(conflictPath, c.rendered, "utf8");
    }
  }

  return { writes, conflicts, nextGenerated };
}

function entryFor(d, hash) {
  const entry = { template: d.template, hash };
  if (d.target === SETTINGS_HOOKS_KEY) entry.commands = d.commands ?? [];
  return entry;
}
