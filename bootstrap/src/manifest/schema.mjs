import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const schemaUrl = new URL("../../schemas/claude-manifest.v1.json", import.meta.url);

export const manifestSchema = JSON.parse(readFileSync(fileURLToPath(schemaUrl), "utf8"));
export const manifestSchemaId = manifestSchema.$id;
