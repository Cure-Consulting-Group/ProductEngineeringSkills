import { existsSync, readFileSync, readdirSync, statSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { join, dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { sha256 } from "../blocks/hash.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const SKILLS_PKG_NAME = "@cure-consulting-group/product-engineering-skills";

export const VENDOR_DECISIONS = Object.freeze({
  CREATE: "create",
  UPDATE: "update",
  CONFLICT: "conflict",
  UNCHANGED: "unchanged",
  REMOVE: "remove",
});

export function resolveSkillsSource({ flag, env = process.env, cwd = process.cwd() } = {}) {
  if (flag) {
    const path = resolve(cwd, flag);
    if (looksLikeSkillsRepo(path)) return { path, source: "--skills-source" };
    throw new Error(`--skills-source path is not a valid skills repo (missing skills/ or agents/): ${path}`);
  }
  if (env.CLAUDE_SKILLS_DIR) {
    const path = resolve(env.CLAUDE_SKILLS_DIR);
    if (looksLikeSkillsRepo(path)) return { path, source: "$CLAUDE_SKILLS_DIR" };
    throw new Error(`$CLAUDE_SKILLS_DIR is not a valid skills repo (missing skills/ or agents/): ${path}`);
  }

  const fallbacks = [];
  try {
    const req = createRequire(here + "/");
    const pkgPath = req.resolve(`${SKILLS_PKG_NAME}/package.json`);
    fallbacks.push({ tag: "node-resolution", path: dirname(pkgPath) });
  } catch {}
  fallbacks.push({ tag: "monorepo-sibling", path: resolve(here, "../../../") });

  for (const c of fallbacks) {
    if (looksLikeSkillsRepo(c.path)) return { path: c.path, source: c.tag };
  }

  const tried = fallbacks.map((c) => `  ${c.tag}: ${c.path}`).join("\n");
  throw new Error(
    `cannot locate skills source. Pass --skills-source <path>, set $CLAUDE_SKILLS_DIR, or install '${SKILLS_PKG_NAME}'.\nTried:\n${tried}`,
  );
}

function looksLikeSkillsRepo(path) {
  if (!existsSync(path)) return false;
  return existsSync(join(path, "skills")) && existsSync(join(path, "agents"));
}

function listFilesShallow(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .map((name) => ({ name, full: join(dir, name) }))
    .filter((e) => statSync(e.full).isFile());
}

function collectExpectedFiles({ source, manifest }) {
  const expected = [];
  for (const skill of manifest.skills?.active ?? []) {
    const skillDir = join(source, "skills", skill);
    if (!existsSync(skillDir)) {
      throw new Error(`skill '${skill}' not found in source: expected ${skillDir}`);
    }
    for (const f of listFilesShallow(skillDir)) {
      const targetPath = join(".claude", "skills", skill, f.name);
      const sourceRel = relative(source, f.full);
      expected.push({ targetPath, sourceAbs: f.full, sourceRel });
    }
  }
  for (const agent of manifest.agents?.active ?? []) {
    const sourceAbs = join(source, "agents", `${agent}.md`);
    if (!existsSync(sourceAbs)) {
      throw new Error(`agent '${agent}' not found in source: expected ${sourceAbs}`);
    }
    expected.push({
      targetPath: join(".claude", "agents", `${agent}.md`),
      sourceAbs,
      sourceRel: relative(source, sourceAbs),
    });
  }
  return expected;
}

export function planVendor({ cwd, source, manifest }) {
  const expected = collectExpectedFiles({ source, manifest });
  const stored = manifest.vendored ?? {};
  const decisions = [];
  const seenTargets = new Set();

  for (const ex of expected) {
    seenTargets.add(ex.targetPath);
    const sourceContent = readFileSync(ex.sourceAbs, "utf8");
    const sourceHash = sha256(sourceContent);

    const fullTarget = join(cwd, ex.targetPath);
    const targetExists = existsSync(fullTarget);
    const targetContent = targetExists ? readFileSync(fullTarget, "utf8") : null;
    const targetHash = targetContent != null ? sha256(targetContent) : null;
    const storedEntry = stored[ex.targetPath];

    let decision;
    if (!targetExists) {
      decision = VENDOR_DECISIONS.CREATE;
    } else if (storedEntry && storedEntry.hash !== targetHash) {
      decision = VENDOR_DECISIONS.CONFLICT;
    } else if (targetHash === sourceHash) {
      decision = VENDOR_DECISIONS.UNCHANGED;
    } else {
      decision = VENDOR_DECISIONS.UPDATE;
    }

    decisions.push({
      targetPath: ex.targetPath,
      sourceAbs: ex.sourceAbs,
      sourceRel: ex.sourceRel,
      decision,
      sourceContent,
      sourceHash,
      targetContent,
      targetHash,
    });
  }

  for (const target of Object.keys(stored)) {
    if (!seenTargets.has(target)) {
      decisions.push({
        targetPath: target,
        sourceRel: stored[target].source,
        decision: VENDOR_DECISIONS.REMOVE,
        sourceHash: stored[target].hash,
      });
    }
  }

  return { decisions };
}

export function applyVendor({ cwd, plan, write = true }) {
  const writes = [];
  const removes = [];
  const conflicts = [];
  const nextVendored = {};

  for (const d of plan.decisions) {
    switch (d.decision) {
      case VENDOR_DECISIONS.CREATE:
      case VENDOR_DECISIONS.UPDATE:
        writes.push(d);
        nextVendored[d.targetPath] = { source: d.sourceRel, hash: d.sourceHash };
        break;
      case VENDOR_DECISIONS.UNCHANGED:
        nextVendored[d.targetPath] = { source: d.sourceRel, hash: d.sourceHash };
        break;
      case VENDOR_DECISIONS.CONFLICT:
        conflicts.push(d);
        nextVendored[d.targetPath] = { source: d.sourceRel, hash: d.targetHash };
        break;
      case VENDOR_DECISIONS.REMOVE:
        removes.push(d);
        break;
    }
  }

  if (write) {
    for (const w of writes) {
      const full = join(cwd, w.targetPath);
      mkdirSync(dirname(full), { recursive: true });
      writeFileSync(full, w.sourceContent, "utf8");
    }
    for (const r of removes) {
      const full = join(cwd, r.targetPath);
      if (existsSync(full)) rmSync(full);
    }
    for (const c of conflicts) {
      const conflictPath = join(cwd, ".claude", "upgrades", `${c.targetPath.replace(/[\/]/g, "_")}.conflict`);
      mkdirSync(dirname(conflictPath), { recursive: true });
      writeFileSync(conflictPath, c.sourceContent, "utf8");
    }
  }

  return { writes, removes, conflicts, nextVendored };
}
