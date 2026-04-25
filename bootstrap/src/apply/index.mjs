import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { renderTemplate, TEMPLATE_FILES } from "../template/render.mjs";
import { planFile, DECISIONS } from "../blocks/index.mjs";
import { validateManifest } from "../manifest/index.mjs";

export const MANIFEST_FILENAME = "claude.manifest.json";

export function buildPlan({ cwd, manifest }) {
  const { valid, errors } = validateManifest(manifest);
  if (!valid) {
    const formatted = errors.map((e) => `  ${e.path}: ${e.message}`).join("\n");
    throw new Error(`manifest is invalid:\n${formatted}`);
  }

  const filePlans = [];
  const storedHashes = manifest.managedBlocks ?? {};

  for (const { template, target } of TEMPLATE_FILES) {
    const rendered = renderTemplate(template, manifest);
    const targetPath = join(cwd, target);
    const existing = existsSync(targetPath) ? readFileSync(targetPath, "utf8") : null;
    const plan = planFile({ filePath: target, existing, rendered, storedHashes });
    filePlans.push(plan);
  }

  return { filePlans };
}

export function applyPlan({ cwd, manifest, plan, write = true }) {
  const writes = [];
  const conflicts = [];
  const nextManagedBlocks = { ...(manifest.managedBlocks ?? {}) };

  for (const fp of plan.filePlans) {
    if (fp.decision === DECISIONS.UNCHANGED) continue;
    if (fp.decision === DECISIONS.CONFLICT) {
      conflicts.push(...fp.conflicts.map((c) => ({ ...c, file: fp.filePath })));
    }
    Object.assign(nextManagedBlocks, fp.nextHashes);
    writes.push({ filePath: fp.filePath, content: fp.nextContent, decision: fp.decision });
  }

  const hasChanges = writes.length > 0;
  const updatedManifest = hasChanges
    ? {
        ...manifest,
        bootstrap: { ...manifest.bootstrap, lastAppliedAt: new Date().toISOString() },
        managedBlocks: nextManagedBlocks,
      }
    : manifest;

  if (write) {
    for (const w of writes) {
      const fullPath = join(cwd, w.filePath);
      mkdirSync(dirname(fullPath), { recursive: true });
      writeFileSync(fullPath, w.content, "utf8");
    }
    if (hasChanges) {
      writeFileSync(
        join(cwd, MANIFEST_FILENAME),
        JSON.stringify(updatedManifest, null, 2) + "\n",
        "utf8",
      );
    }
    for (const c of conflicts) {
      const conflictPath = join(cwd, ".claude", "upgrades", `${c.file.replace(/[\/]/g, "_")}.${c.id}.conflict`);
      mkdirSync(dirname(conflictPath), { recursive: true });
      writeFileSync(conflictPath, c.renderedContent, "utf8");
    }
  }

  return { writes, conflicts, manifest: updatedManifest };
}

export function readManifest(cwd) {
  const path = join(cwd, MANIFEST_FILENAME);
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, "utf8"));
}

export function summarizePlan(plan) {
  const lines = [];
  for (const fp of plan.filePlans) {
    const tag = fp.decision.padEnd(9);
    lines.push(`  [${tag}] ${fp.filePath}`);
    for (const r of fp.blockReports) {
      if (r.status === "unchanged") continue;
      lines.push(`             - ${r.id}: ${r.status}`);
    }
  }
  return lines.join("\n");
}
