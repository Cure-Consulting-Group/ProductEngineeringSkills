#!/usr/bin/env node
// Regenerates templates/deny-rules.json from the library's root settings.json, the one
// source of truth for Cure deny rules. The bootstrap package ships without the repo root,
// so the template reads this snapshot; test/template.test.mjs fails when it drifts.
// Usage: node scripts/sync-deny-rules.mjs [--check]
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "../../settings.json");
const target = resolve(here, "../templates/deny-rules.json");

const deny = JSON.parse(readFileSync(source, "utf8")).permissions?.deny ?? [];
const next = JSON.stringify(deny, null, 2) + "\n";
const current = (() => { try { return readFileSync(target, "utf8"); } catch { return ""; } })();

if (process.argv.includes("--check")) {
  if (current !== next) {
    console.error("templates/deny-rules.json is stale: run node scripts/sync-deny-rules.mjs");
    process.exit(1);
  }
  console.log(`deny-rules.json in sync (${deny.length} rules)`);
} else if (current !== next) {
  writeFileSync(target, next);
  console.log(`wrote templates/deny-rules.json (${deny.length} rules)`);
} else {
  console.log(`deny-rules.json already in sync (${deny.length} rules)`);
}
