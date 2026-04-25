import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const FILE_SIGNALS = [
  { file: "build.gradle.kts", stack: "android", lang: "kotlin", projectType: "android" },
  { file: "build.gradle",     stack: "android", lang: "kotlin", projectType: "android" },
  { file: "Package.swift",    stack: "ios",     lang: "swift",  projectType: "ios" },
  { file: "Podfile",          stack: "ios",     lang: "swift",  projectType: "ios" },
  { file: "go.mod",           stack: "go",      lang: "go",     projectType: "cli" },
  { file: "Cargo.toml",       stack: "rust",    lang: "rust",   projectType: "cli" },
  { file: "pyproject.toml",   stack: "python",  lang: "python", projectType: "cli" },
  { file: "requirements.txt", stack: "python",  lang: "python", projectType: "cli" },
  { file: "firebase.json",    stack: "firebase", lang: null,    projectType: "firebase" },
  { file: "Dockerfile",       stack: "docker",   lang: null,    projectType: null },
  { file: "terraform.tf",     stack: "terraform", lang: null,   projectType: null },
];

const PKG_SIGNALS = [
  { dep: "next",            stack: "nextjs",      lang: "typescript", projectType: "web" },
  { dep: "react",           stack: "react",       lang: "typescript", projectType: "web" },
  { dep: "stripe",          stack: "stripe",      lang: null,         projectType: null },
  { dep: "@stripe/stripe-js", stack: "stripe",    lang: null,         projectType: null },
  { dep: "firebase",        stack: "firebase",    lang: null,         projectType: null },
  { dep: "firebase-admin",  stack: "firebase",    lang: null,         projectType: "firebase" },
  { dep: "@anthropic-ai/sdk", stack: "anthropic", lang: null,         projectType: null },
  { dep: "fastify",         stack: "fastify",     lang: "typescript", projectType: "cli" },
  { dep: "express",         stack: "express",     lang: "typescript", projectType: "cli" },
];

export function detectStack(cwd) {
  const stack = new Set();
  let primaryLanguage = null;
  let projectType = null;

  for (const sig of FILE_SIGNALS) {
    if (existsSync(join(cwd, sig.file))) {
      stack.add(sig.stack);
      if (!primaryLanguage && sig.lang) primaryLanguage = sig.lang;
      if (!projectType && sig.projectType) projectType = sig.projectType;
    }
  }

  const pkgPath = join(cwd, "package.json");
  if (existsSync(pkgPath)) {
    try {
      const pkg = JSON.parse(readFileSync(pkgPath, "utf8"));
      const deps = { ...(pkg.dependencies ?? {}), ...(pkg.devDependencies ?? {}) };
      for (const sig of PKG_SIGNALS) {
        if (deps[sig.dep]) {
          stack.add(sig.stack);
          if (!primaryLanguage && sig.lang) primaryLanguage = sig.lang;
          if (!projectType && sig.projectType) projectType = sig.projectType;
        }
      }
      if (!primaryLanguage) {
        primaryLanguage = existsSync(join(cwd, "tsconfig.json")) ? "typescript" : "javascript";
      }
      if (!projectType && (deps.react || deps.next || deps.vue)) projectType = "web";
      if (!projectType) projectType = "cli";
    } catch {
      // malformed package.json — skip pkg signals
    }
  }

  if (stack.size > 1 && projectType == null) projectType = "mixed";
  if (!projectType) projectType = "cli";
  if (!primaryLanguage) primaryLanguage = "typescript";

  return {
    projectType,
    primaryLanguage,
    stack: [...stack],
  };
}
