#!/usr/bin/env node
/**
 * Postinstall for @cure-consulting-group/product-engineering-skills.
 *
 * Vendors the skill library into the consuming project's .claude/ directory
 * so the files get checked into that project's git repo. Anyone who pulls
 * the project then has the skills without needing this npm package.
 *
 * Layout notes:
 *   - Source has skills/<category>/<name>/SKILL.md (category folder is for
 *     upstream organization only). Claude Code's project-skill discovery
 *     walks one level deep, so we flatten to .claude/skills/<name>/SKILL.md.
 *   - Source has claude-commands/ (legacy folder name). Claude Code reads
 *     .claude/commands/, so we rename during copy.
 *
 * Behavior:
 *   - Skip-if-exists by default (won't clobber project customizations).
 *   - Set CURE_SKILLS_FORCE=1 to overwrite from upstream.
 *   - Set SKIP_CURE_SKILLS_INSTALL=1 or CI=1 to skip entirely.
 */

const fs = require("fs");
const path = require("path");

const FLAT_DIRS_INTO_DOT_CLAUDE = [
  "agents",
  "personas",
  "rules",
  "output-styles",
  "hooks",
];

const RENAMED_DIRS = [
  { src: "claude-commands", dest: "commands" },
];

const FILES_INTO_DOT_CLAUDE = ["settings.json"];

const FILES_INTO_PROJECT_ROOT = [".mcp.json", ".lsp.json"];

function main() {
  const packageRoot = __dirname;
  const projectRoot = process.env.INIT_CWD;

  if (process.env.CI || process.env.SKIP_CURE_SKILLS_INSTALL) {
    console.log("[cure-skills] Skipping vendor step (CI or opt-out detected).");
    return;
  }

  if (!projectRoot || projectRoot === packageRoot) {
    console.log("[cure-skills] Not running inside a consuming project — skipping.");
    return;
  }

  if (!fs.existsSync(path.join(projectRoot, "package.json"))) {
    console.log(`[cure-skills] No package.json at ${projectRoot} — skipping.`);
    return;
  }

  const force = process.env.CURE_SKILLS_FORCE === "1";
  const claudeDir = path.join(projectRoot, ".claude");
  fs.mkdirSync(claudeDir, { recursive: true });

  let copied = 0;
  let skipped = 0;

  // Skills: flatten skills/<category>/<name>/ → .claude/skills/<name>/
  const skillsSrc = path.join(packageRoot, "skills");
  const skillsDest = path.join(claudeDir, "skills");
  if (fs.existsSync(skillsSrc)) {
    if (fs.existsSync(skillsDest) && !force) {
      console.log("[cure-skills] skip  .claude/skills (exists)");
      skipped++;
    } else {
      const skillCount = vendorSkillsFlat(skillsSrc, skillsDest);
      console.log(`[cure-skills] copy  skills → .claude/skills (${skillCount} skills, flattened)`);
      copied++;
    }
  }

  // Renamed directories: claude-commands → commands
  for (const { src: srcName, dest: destName } of RENAMED_DIRS) {
    const src = path.join(packageRoot, srcName);
    const dest = path.join(claudeDir, destName);
    if (!fs.existsSync(src)) continue;
    if (fs.existsSync(dest) && !force) {
      console.log(`[cure-skills] skip  .claude/${destName} (exists)`);
      skipped++;
      continue;
    }
    copyRecursive(src, dest);
    console.log(`[cure-skills] copy  ${srcName} → .claude/${destName}`);
    copied++;
  }

  // Already-flat dirs: copy as-is
  for (const dir of FLAT_DIRS_INTO_DOT_CLAUDE) {
    const src = path.join(packageRoot, dir);
    const dest = path.join(claudeDir, dir);
    if (!fs.existsSync(src)) continue;
    if (fs.existsSync(dest) && !force) {
      console.log(`[cure-skills] skip  .claude/${dir} (exists)`);
      skipped++;
      continue;
    }
    copyRecursive(src, dest);
    console.log(`[cure-skills] copy  ${dir} → .claude/${dir}`);
    copied++;
  }

  for (const file of FILES_INTO_DOT_CLAUDE) {
    const src = path.join(packageRoot, file);
    const dest = path.join(claudeDir, file);
    if (!fs.existsSync(src)) continue;
    if (fs.existsSync(dest) && !force) {
      console.log(`[cure-skills] skip  .claude/${file} (exists)`);
      skipped++;
      continue;
    }
    fs.copyFileSync(src, dest);
    console.log(`[cure-skills] copy  ${file} → .claude/${file}`);
    copied++;
  }

  for (const file of FILES_INTO_PROJECT_ROOT) {
    const src = path.join(packageRoot, file);
    const dest = path.join(projectRoot, file);
    if (!fs.existsSync(src)) continue;
    if (fs.existsSync(dest) && !force) {
      console.log(`[cure-skills] skip  ${file} (exists)`);
      skipped++;
      continue;
    }
    fs.copyFileSync(src, dest);
    console.log(`[cure-skills] copy  ${file} → ${file}`);
    copied++;
  }

  console.log("");
  if (copied === 0 && skipped > 0) {
    console.log(`[cure-skills] All ${skipped} target(s) already exist. Set CURE_SKILLS_FORCE=1 to refresh from upstream.`);
  } else {
    console.log(`[cure-skills] Vendored ${copied} target(s)${skipped ? ` (${skipped} skipped)` : ""}.`);
    console.log("[cure-skills] Next: review the files, then `git add .claude/ .mcp.json .lsp.json && git commit`.");
  }
}

function vendorSkillsFlat(srcDir, destDir) {
  fs.mkdirSync(destDir, { recursive: true });
  const skillDirs = findSkillLeaves(srcDir);
  const seen = new Set();
  for (const skillDir of skillDirs) {
    const skillName = path.basename(skillDir);
    if (seen.has(skillName)) {
      console.warn(`[cure-skills] WARNING: duplicate skill name '${skillName}' — second copy ignored. Source: ${skillDir}`);
      continue;
    }
    seen.add(skillName);
    copyRecursive(skillDir, path.join(destDir, skillName));
  }
  return seen.size;
}

function findSkillLeaves(dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const childPath = path.join(dir, entry.name);
    if (fs.existsSync(path.join(childPath, "SKILL.md"))) {
      results.push(childPath);
    } else {
      results.push(...findSkillLeaves(childPath));
    }
  }
  return results;
}

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

try {
  main();
} catch (err) {
  console.warn(`[cure-skills] Vendor step failed: ${err.message}`);
  console.warn("[cure-skills] You can re-run manually with: node node_modules/@cure-consulting-group/product-engineering-skills/install-plugin.js");
}
