/**
 * Harness contracts: the Controls table in AGENTS.md, as code.
 *
 * Each test enforces one rule an agent is likely to break because it has only read about it.
 * Failure messages state the rule and the fix, because the reader is usually an agent that has
 * never seen this file. Put it in a CI job that runs on every PR.
 *
 * Template from the cure-product-engineering `agent-harness` skill. The first four tests apply to
 * any repo; replace the last with the repo's own top rules, and mutation-check each one.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const ROOT = join(__dirname, ".."); // adjust if this file is not one level below the root
const read = (rel: string): string => readFileSync(join(ROOT, rel), "utf8");
const git = (...args: string[]): string =>
  execFileSync("git", args, { cwd: ROOT, encoding: "utf8", maxBuffer: 256 * 1024 * 1024 });
const tracked = (...paths: string[]): string[] => git("ls-files", "--", ...paths).split("\n").filter(Boolean);
const ignored = (rel: string): boolean => {
  try {
    git("check-ignore", "-q", "--no-index", rel);
    return true;
  } catch {
    return false;
  }
};

describe("Harness", () => {
  // Backticked tokens under these roots are repo paths; agents act on them as fact.
  it("agent_docs_name_only_paths_that_exist", () => {
    const roots = ["src/", "scripts/", "docs/", ".claude/", ".github/"]; // the repo's top-level dirs
    const missing: string[] = [];
    for (const doc of ["AGENTS.md", "CLAUDE.md"].filter((d) => existsSync(join(ROOT, d)))) {
      for (const span of read(doc).match(/`[^`\n]+`/g) ?? []) {
        for (let token of span.slice(1, -1).split(/[\s=]+/)) {
          token = token.replace(/^["'(]+|["'),;:.]+$/g, "");
          if (!roots.some((r) => token.startsWith(r))) continue;
          if (/[*?<>{}…]/.test(token)) continue; // globs and placeholders
          if (/(^|\/)(dist|build)(\/|$)/.test(token)) continue; // build output
          if (ignored(token)) continue; // machine-local paths are named on purpose
          if (!existsSync(join(ROOT, token))) missing.push(`${doc}: \`${token}\``);
        }
      }
    }
    expect(missing, `Agent docs name paths that do not exist. Fix the path or drop the claim:\n  ${missing.join("\n  ")}`).toEqual([]);
  });

  // Org policy 2026-08-08: no scheduled GitHub Actions anywhere.
  it("no_scheduled_workflows", () => {
    const dir = join(ROOT, ".github", "workflows");
    const offenders: string[] = [];
    for (const file of existsSync(dir) ? readdirSync(dir).filter((f) => /\.ya?ml$/.test(f)) : []) {
      readFileSync(join(dir, file), "utf8").split("\n").forEach((line, i) => {
        if (/^\s*schedule\s*:/.test(line) || /^\s*-?\s*cron\s*:/.test(line)) offenders.push(`${file}:${i + 1}`);
      });
    }
    expect(offenders, `Scheduled workflow trigger (org policy 2026-08-08). Trigger on push, pull_request or workflow_dispatch:\n  ${offenders.join("\n  ")}`).toEqual([]);
  });

  // The Cure library comes from the user-scope plugin. A vendored copy shadows it with a stale
  // version, and the npm package's postinstall re-vendors it on every `npm ci`.
  it("cure_library_is_a_plugin_not_vendored", () => {
    const vendored = tracked(".claude/agents", ".claude/commands", ".claude/output-styles", ".claude/personas", ".claude/hooks/hooks.json");
    expect(vendored, `Vendored Cure library files are tracked. Delete them; the plugin provides them:\n  ${vendored.slice(0, 10).join("\n  ")}`).toEqual([]);
    const pkg = existsSync(join(ROOT, "package.json")) ? JSON.parse(read("package.json")) : {};
    const deps = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies });
    expect(
      deps.filter((d) => d === "@cure-consulting-group/product-engineering-skills"),
      "package.json depends on @cure-consulting-group/product-engineering-skills, whose postinstall re-vendors the library into .claude/. Remove it; install the plugin instead.",
    ).toEqual([]);
  });

  // Reports and notes go under docs/, not the repo root.
  it("no_root_level_reports", () => {
    const allowed = new Set(["README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "STATE.md", "CHANGELOG.md"]);
    const extra = tracked("*.md").filter((f) => !f.includes("/") && !allowed.has(f));
    expect(extra, `Root-level markdown outside the allowed set. Put it under docs/:\n  ${extra.join("\n  ")}`).toEqual([]);
  });

  // Replace with the repo's own rules. Proven examples:
  // - every deploy script runs the project guard before `firebase deploy`
  // - every getFirestore() names the database; `(default)` silently returns nothing
  // - every backfill script ships with a paired test
  // - the state file stays under N lines; older entries move to docs/state-archive/
});
