import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import Ajv from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const schemaUrl = new URL("../../schemas/org-manifest.v1.json", import.meta.url);
const orgSchema = JSON.parse(readFileSync(fileURLToPath(schemaUrl), "utf8"));

const ajv = new Ajv({ allErrors: true, strict: true });
addFormats(ajv);
const compiled = ajv.compile(orgSchema);

export const ORG_MANIFEST_FILENAME = "org.manifest.json";

export function loadOrgManifest({ skillsSourcePath } = {}) {
  if (!skillsSourcePath) return null;
  const path = join(skillsSourcePath, ORG_MANIFEST_FILENAME);
  if (!existsSync(path)) return null;
  const parsed = JSON.parse(readFileSync(path, "utf8"));
  if (!compiled(parsed)) {
    const formatted = (compiled.errors ?? []).map((e) => `  ${e.instancePath || "/"}: ${e.message}`).join("\n");
    throw new Error(`org.manifest.json is invalid:\n${formatted}`);
  }
  return parsed;
}

export function enforceOrgPolicy({ projectManifest, orgManifest }) {
  const errors = [];
  if (!orgManifest) return { errors };

  const minVer = orgManifest.bootstrap?.minimumSkillsVersion;
  if (minVer && cmpSemver(projectManifest.bootstrap.skillsRepoVersion, minVer) < 0) {
    errors.push({
      path: "/bootstrap/skillsRepoVersion",
      message: `pinned skills version ${projectManifest.bootstrap.skillsRepoVersion} is below org minimum ${minVer}`,
      code: "org/skills-version-floor",
      params: { pinned: projectManifest.bootstrap.skillsRepoVersion, minimum: minVer },
    });
  }

  for (const kind of ["skills", "agents", "rules"]) {
    const required = orgManifest[kind]?.required ?? [];
    const forbidden = orgManifest[kind]?.forbidden ?? [];
    const active = new Set(projectManifest[kind]?.active ?? []);
    for (const id of required) {
      if (!active.has(id)) {
        errors.push({
          path: `/${kind}/active`,
          message: `org policy requires ${kind.slice(0, -1)} '${id}' in active list`,
          code: `org/${kind}-required`,
          params: { id },
        });
      }
    }
    for (const id of forbidden) {
      if (active.has(id)) {
        errors.push({
          path: `/${kind}/active`,
          message: `org policy forbids ${kind.slice(0, -1)} '${id}'`,
          code: `org/${kind}-forbidden`,
          params: { id },
        });
      }
    }
  }

  return { errors };
}

function cmpSemver(a, b) {
  const pa = a.split(/[-+]/)[0].split(".").map(Number);
  const pb = b.split(/[-+]/)[0].split(".").map(Number);
  for (let i = 0; i < 3; i++) {
    if (pa[i] > pb[i]) return 1;
    if (pa[i] < pb[i]) return -1;
  }
  return 0;
}
