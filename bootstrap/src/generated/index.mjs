import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { renderTemplate } from "../template/render.mjs";
import { sha256 } from "../blocks/hash.mjs";

export const GENERATED_DECISIONS = Object.freeze({
  CREATE: "create",
  UPDATE: "update",
  CONFLICT: "conflict",
  UNCHANGED: "unchanged",
});

export const GENERATED_FILES = Object.freeze([
  { template: "claude-hooks.json.ejs", target: ".claude/hooks/hooks.json" },
  { template: "cursorrules.ejs",       target: ".cursorrules" },
  { template: "gemini-config.yaml.ejs", target: ".gemini/config.yaml" },
]);

export function planGenerated({ cwd, manifest, files = GENERATED_FILES }) {
  const stored = manifest.generated ?? {};
  const decisions = [];

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

    decisions.push({ target, template, rendered, renderedHash, targetContent, targetHash, decision });
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
        nextGenerated[d.target] = { template: d.template, hash: d.renderedHash };
        break;
      case GENERATED_DECISIONS.UNCHANGED:
        nextGenerated[d.target] = { template: d.template, hash: d.renderedHash };
        break;
      case GENERATED_DECISIONS.CONFLICT:
        conflicts.push(d);
        nextGenerated[d.target] = { template: d.template, hash: d.targetHash };
        break;
    }
  }

  if (write) {
    for (const w of writes) {
      const full = join(cwd, w.target);
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
