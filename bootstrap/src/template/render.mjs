import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import ejs from "ejs";

const here = dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = resolve(here, "../../templates");

const EJS_OPTIONS = Object.freeze({ rmWhitespace: false, strict: true, _with: false, localsName: "ctx" });

const cache = new Map();

function compile(name) {
  const cached = cache.get(name);
  if (cached) return cached;
  const file = resolve(TEMPLATES_DIR, name);
  const source = readFileSync(file, "utf8");
  const fn = ejs.compile(source, { ...EJS_OPTIONS, filename: file });
  cache.set(name, fn);
  return fn;
}

export function renderTemplate(name, manifest) {
  const fn = compile(name);
  return fn(buildContext(manifest));
}

export function buildContext(manifest) {
  return {
    manifest,
    project: manifest.project,
    bootstrap: manifest.bootstrap,
    compliance: manifest.compliance,
    skills: manifest.skills,
    agents: manifest.agents ?? { active: [] },
    hooks: manifest.hooks ?? { preCommit: [], postFeature: [], prePR: [] },
    stack: manifest.project.stack ?? [],
    activeCompliance: Object.entries(manifest.compliance)
      .filter(([, v]) => v === true)
      .map(([k]) => k),
  };
}

export const TEMPLATE_FILES = Object.freeze([
  { template: "CLAUDE.md.ejs", target: "CLAUDE.md" },
  { template: "STATE.md.ejs", target: "STATE.md" },
  { template: "claude-settings.json.ejs", target: ".claude/settings.json" },
]);
