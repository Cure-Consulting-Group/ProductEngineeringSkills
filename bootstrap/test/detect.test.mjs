import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { detectStack } from "../src/detect/stack.mjs";

function tmp() {
  return mkdtempSync(join(tmpdir(), "claude-bootstrap-detect-"));
}

test("empty dir → cli/typescript with no stack", () => {
  const r = detectStack(tmp());
  assert.equal(r.projectType, "cli");
  assert.equal(r.primaryLanguage, "typescript");
  assert.deepEqual(r.stack, []);
});

test("Next.js + Stripe + Firebase web project", () => {
  const dir = tmp();
  writeFileSync(join(dir, "package.json"), JSON.stringify({
    dependencies: { next: "14", react: "18", stripe: "14", firebase: "10" },
  }));
  writeFileSync(join(dir, "tsconfig.json"), "{}");
  const r = detectStack(dir);
  assert.equal(r.projectType, "web");
  assert.equal(r.primaryLanguage, "typescript");
  for (const s of ["nextjs", "react", "stripe", "firebase"]) assert.ok(r.stack.includes(s), `missing ${s}`);
});

test("Android project", () => {
  const dir = tmp();
  writeFileSync(join(dir, "build.gradle.kts"), "");
  const r = detectStack(dir);
  assert.equal(r.projectType, "android");
  assert.equal(r.primaryLanguage, "kotlin");
  assert.ok(r.stack.includes("android"));
});

test("iOS project (Package.swift)", () => {
  const dir = tmp();
  writeFileSync(join(dir, "Package.swift"), "");
  const r = detectStack(dir);
  assert.equal(r.projectType, "ios");
  assert.equal(r.primaryLanguage, "swift");
});

test("Firebase Functions project (firebase-admin in deps)", () => {
  const dir = tmp();
  mkdirSync(join(dir, "functions"));
  writeFileSync(join(dir, "package.json"), JSON.stringify({
    dependencies: { "firebase-admin": "12", "firebase-functions": "5" },
  }));
  const r = detectStack(dir);
  assert.equal(r.projectType, "firebase");
  assert.ok(r.stack.includes("firebase"));
});

test("malformed package.json does not throw", () => {
  const dir = tmp();
  writeFileSync(join(dir, "package.json"), "{ broken");
  const r = detectStack(dir);
  assert.ok(r.projectType);
});

test("multiple signals + ambiguous → mixed", () => {
  const dir = tmp();
  writeFileSync(join(dir, "Dockerfile"), "");
  writeFileSync(join(dir, "terraform.tf"), "");
  const r = detectStack(dir);
  assert.equal(r.projectType, "mixed");
});
