import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { renderTemplate, TEMPLATE_FILES } from "../template/render.mjs";
import { planFile, DECISIONS } from "../blocks/index.mjs";
import { validateManifest } from "../manifest/index.mjs";
import { resolveSkillsSource, planVendor, applyVendor, VENDOR_DECISIONS } from "../vendor/index.mjs";

export const MANIFEST_FILENAME = "claude.manifest.json";

export function buildPlan({ cwd, manifest, skillsSource }) {
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

  let vendorPlan = { decisions: [] };
  let resolvedSource = null;
  const wantsVendoring =
    (manifest.skills?.active?.length ?? 0) > 0 ||
    (manifest.agents?.active?.length ?? 0) > 0 ||
    Object.keys(manifest.vendored ?? {}).length > 0;

  if (wantsVendoring) {
    resolvedSource = resolveSkillsSource({ flag: skillsSource });
    vendorPlan = planVendor({ cwd, source: resolvedSource.path, manifest });
  }

  return { filePlans, vendorPlan, resolvedSource };
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

  const vendorResult = applyVendor({ cwd, plan: plan.vendorPlan ?? { decisions: [] }, write });
  const vendorChanged = vendorResult.writes.length > 0 || vendorResult.removes.length > 0;
  const hasChanges = writes.length > 0 || vendorChanged;

  const updatedManifest = hasChanges
    ? {
        ...manifest,
        bootstrap: { ...manifest.bootstrap, lastAppliedAt: new Date().toISOString() },
        managedBlocks: nextManagedBlocks,
        vendored: vendorResult.nextVendored,
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

  return {
    writes,
    conflicts,
    vendor: vendorResult,
    manifest: updatedManifest,
  };
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
  for (const d of plan.vendorPlan?.decisions ?? []) {
    if (d.decision === VENDOR_DECISIONS.UNCHANGED) continue;
    lines.push(`  [${d.decision.padEnd(9)}] ${d.targetPath}`);
  }
  if (plan.resolvedSource) {
    lines.push(`  (skills source: ${plan.resolvedSource.source} → ${plan.resolvedSource.path})`);
  }
  return lines.join("\n");
}
