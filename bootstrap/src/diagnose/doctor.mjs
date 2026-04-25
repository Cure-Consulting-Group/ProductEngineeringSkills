import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { sha256, parseBlocks } from "../blocks/index.mjs";
import { validateManifest } from "../manifest/index.mjs";
import { resolveSkillsSource } from "../vendor/index.mjs";
import { loadOrgManifest, enforceOrgPolicy } from "../org/index.mjs";

export const DRIFT_KINDS = Object.freeze({
  MANIFEST_INVALID: "manifest-invalid",
  ORG_POLICY: "org-policy",
  VENDORED_MISSING: "vendored-missing",
  VENDORED_EDITED: "vendored-edited",
  VENDORED_OUTDATED: "vendored-outdated",
  GENERATED_MISSING: "generated-missing",
  GENERATED_EDITED: "generated-edited",
  BLOCK_MISSING: "block-missing",
  BLOCK_EDITED: "block-edited",
});

export function diagnose({ cwd, manifest, skillsSourcePath }) {
  const findings = [];

  const validation = validateManifest(manifest);
  if (!validation.valid) {
    for (const e of validation.errors) {
      findings.push({ kind: DRIFT_KINDS.MANIFEST_INVALID, path: e.path, message: e.message, severity: "error" });
    }
    return { findings };
  }

  if (skillsSourcePath) {
    const orgManifest = safe(() => loadOrgManifest({ skillsSourcePath }));
    if (orgManifest) {
      const { errors } = enforceOrgPolicy({ projectManifest: manifest, orgManifest });
      for (const e of errors) {
        findings.push({ kind: DRIFT_KINDS.ORG_POLICY, path: e.path, message: e.message, severity: "error" });
      }
    }
  }

  for (const [target, entry] of Object.entries(manifest.vendored ?? {})) {
    const fullTarget = join(cwd, target);
    if (!existsSync(fullTarget)) {
      findings.push({ kind: DRIFT_KINDS.VENDORED_MISSING, path: target, message: `tracked file missing on disk`, severity: "error" });
      continue;
    }
    const onDisk = sha256(readFileSync(fullTarget, "utf8"));
    if (onDisk !== entry.hash) {
      findings.push({ kind: DRIFT_KINDS.VENDORED_EDITED, path: target, message: `on-disk hash differs from manifest record`, severity: "warn" });
    }
    if (skillsSourcePath) {
      const sourcePath = join(skillsSourcePath, entry.source);
      if (existsSync(sourcePath)) {
        const sourceHash = sha256(readFileSync(sourcePath, "utf8"));
        if (sourceHash !== entry.hash) {
          findings.push({ kind: DRIFT_KINDS.VENDORED_OUTDATED, path: target, message: `source has changed since vendoring; run apply`, severity: "info" });
        }
      }
    }
  }

  for (const [target, entry] of Object.entries(manifest.generated ?? {})) {
    const fullTarget = join(cwd, target);
    if (!existsSync(fullTarget)) {
      findings.push({ kind: DRIFT_KINDS.GENERATED_MISSING, path: target, message: `tracked generated file missing on disk`, severity: "error" });
      continue;
    }
    const onDisk = sha256(readFileSync(fullTarget, "utf8"));
    if (onDisk !== entry.hash) {
      findings.push({ kind: DRIFT_KINDS.GENERATED_EDITED, path: target, message: `generated file edited by hand`, severity: "warn" });
    }
  }

  const blocksByFile = groupBlocksByFile(manifest.managedBlocks ?? {});
  for (const [filePath, blockHashes] of blocksByFile) {
    const fullTarget = join(cwd, filePath);
    if (!existsSync(fullTarget)) {
      for (const id of Object.keys(blockHashes)) {
        findings.push({ kind: DRIFT_KINDS.BLOCK_MISSING, path: `${filePath}#${id}`, message: `file missing on disk`, severity: "error" });
      }
      continue;
    }
    const parsed = safe(() => parseBlocks(readFileSync(fullTarget, "utf8")));
    if (!parsed) {
      findings.push({ kind: DRIFT_KINDS.BLOCK_MISSING, path: filePath, message: `file unparseable (corrupt fences?)`, severity: "error" });
      continue;
    }
    for (const [id, expectedHash] of Object.entries(blockHashes)) {
      const content = parsed.blocks.get(id);
      if (content == null) {
        findings.push({ kind: DRIFT_KINDS.BLOCK_MISSING, path: `${filePath}#${id}`, message: `tracked block missing in file`, severity: "error" });
        continue;
      }
      if (sha256(content) !== expectedHash) {
        findings.push({ kind: DRIFT_KINDS.BLOCK_EDITED, path: `${filePath}#${id}`, message: `block content edited inside fences`, severity: "warn" });
      }
    }
  }

  return { findings };
}

function groupBlocksByFile(managedBlocks) {
  const out = new Map();
  for (const [key, hash] of Object.entries(managedBlocks)) {
    const idx = key.indexOf("#");
    if (idx < 0) continue;
    const filePath = key.slice(0, idx);
    const id = key.slice(idx + 1);
    if (!out.has(filePath)) out.set(filePath, {});
    out.get(filePath)[id] = hash;
  }
  return out;
}

function safe(fn) {
  try { return fn(); } catch { return null; }
}

export function summarizeDiagnose({ findings }) {
  if (findings.length === 0) return "no drift detected.";
  const lines = [];
  for (const f of findings) {
    lines.push(`  [${f.severity.padEnd(5)}] ${f.kind.padEnd(20)} ${f.path}`);
    lines.push(`           ${f.message}`);
  }
  return lines.join("\n");
}
