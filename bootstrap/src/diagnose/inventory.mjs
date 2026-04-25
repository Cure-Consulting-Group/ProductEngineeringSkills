import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { diagnose } from "./doctor.mjs";

export const INVENTORY_COLUMNS = Object.freeze([
  "project",
  "type",
  "phase",
  "skillsRepoVersion",
  "cliVersion",
  "lastAppliedAt",
  "installMode",
  "compliance",
  "skills",
  "agents",
  "rules",
  "drift",
]);

export function buildInventory({ projectPaths, skillsSourcePath }) {
  const rows = [];
  for (const p of projectPaths) {
    const cwd = resolve(p);
    const manifestPath = join(cwd, "claude.manifest.json");
    if (!existsSync(manifestPath)) {
      rows.push({ project: cwd, error: "no claude.manifest.json" });
      continue;
    }
    let manifest;
    try {
      manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
    } catch (e) {
      rows.push({ project: cwd, error: `manifest unparseable: ${e.message}` });
      continue;
    }
    const compliance = Object.entries(manifest.compliance ?? {})
      .filter(([, v]) => v === true)
      .map(([k]) => k);

    const drift = diagnose({ cwd, manifest, skillsSourcePath }).findings;
    rows.push({
      project: manifest.project?.name ?? cwd,
      type: manifest.project?.type ?? "?",
      phase: manifest.project?.phase ?? "?",
      skillsRepoVersion: manifest.bootstrap?.skillsRepoVersion ?? "?",
      cliVersion: manifest.bootstrap?.cliVersion ?? "?",
      lastAppliedAt: manifest.bootstrap?.lastAppliedAt ?? "?",
      installMode: manifest.bootstrap?.installMode ?? "?",
      compliance: compliance.join("|") || "-",
      skills: (manifest.skills?.active ?? []).length,
      agents: (manifest.agents?.active ?? []).length,
      rules: (manifest.rules?.active ?? []).length,
      drift: drift.length,
    });
  }
  return { rows };
}

export function formatInventoryCsv(inv) {
  const headers = INVENTORY_COLUMNS;
  const out = [headers.join(",")];
  for (const r of inv.rows) {
    if (r.error) {
      out.push(`${csvEscape(r.project)},ERROR: ${csvEscape(r.error)}`);
      continue;
    }
    out.push(headers.map((h) => csvEscape(String(r[h] ?? ""))).join(","));
  }
  return out.join("\n");
}

function csvEscape(s) {
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}
