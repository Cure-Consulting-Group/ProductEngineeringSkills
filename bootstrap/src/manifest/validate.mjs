import Ajv from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { manifestSchema } from "./schema.mjs";

const ajv = new Ajv({ allErrors: true, strict: true, allowUnionTypes: false });
addFormats(ajv);
const compiled = ajv.compile(manifestSchema);

function formatAjvErrors(errors) {
  return errors.map((e) => ({
    path: e.instancePath || "/",
    message: e.message ?? "invalid",
    code: e.keyword,
    params: e.params,
  }));
}

const COMPLIANCE_REQUIRES_VENDORED = ["hipaa", "pci"];

function crossFieldErrors(m) {
  const errors = [];

  const triggered = COMPLIANCE_REQUIRES_VENDORED.filter((k) => m.compliance?.[k]);
  if (triggered.length > 0 && m.bootstrap?.installMode === "symlink") {
    errors.push({
      path: "/bootstrap/installMode",
      message: `installMode 'symlink' is forbidden when compliance flags are set: ${triggered.join(", ")}. Use 'vendored'.`,
      code: "compliance/installMode",
      params: { triggered },
    });
  }

  const active = new Set(m.skills?.active ?? []);
  const disabled = new Set(m.skills?.disabled ?? []);
  for (const s of disabled) {
    if (active.has(s)) {
      errors.push({
        path: "/skills/disabled",
        message: `skill '${s}' appears in both active and disabled`,
        code: "skills/conflict",
        params: { skill: s },
      });
    }
  }

  for (const pinned of Object.keys(m.skills?.pinned ?? {})) {
    if (!active.has(pinned)) {
      errors.push({
        path: `/skills/pinned/${pinned}`,
        message: `pinned skill '${pinned}' is not in skills.active`,
        code: "skills/pinned-not-active",
        params: { skill: pinned },
      });
    }
  }

  return errors;
}

export function validateManifest(manifest) {
  const valid = compiled(manifest);
  const schemaErrors = valid ? [] : formatAjvErrors(compiled.errors ?? []);
  const crossErrors = schemaErrors.length === 0 ? crossFieldErrors(manifest) : [];
  const errors = [...schemaErrors, ...crossErrors];
  return { valid: errors.length === 0, errors };
}
