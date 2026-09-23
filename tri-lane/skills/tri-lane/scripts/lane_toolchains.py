#!/usr/bin/env python3
"""lane_toolchains: detect a repo's build toolchains and the user-level caches each one must be able to write.

The Codex sandbox (workspace-write) confines writes to the worktree, so Gradle cannot take its lock in
~/.gradle, npm cannot write ~/.npm, and the lane can never build or test what it wrote (HoopTrace, 3 Sep 2026).
Callers pass the returned paths as `--add-dir` (codex exec) or `sandbox_workspace_write.writable_roots`
(codex sandbox). Paths are resolved to their physical form: the sandbox rejects symlinked roots.

Also usable standalone:  python3 lane_toolchains.py [repo]   (prints JSON)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HOME = Path.home()

# (toolchain, repo markers, cache dirs relative to home, env var that relocates the cache)
TOOLCHAINS = (
    ("gradle", ("gradlew", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"), (".gradle", ".android", ".m2"), "GRADLE_USER_HOME"),
    ("maven", ("pom.xml",), (".m2",), "MAVEN_OPTS"),
    ("node", ("package.json",), (".npm", ".cache/node", ".yarn", "Library/Caches/pnpm", ".pnpm-store", ".bun"), "npm_config_cache"),
    ("python", ("pyproject.toml", "setup.py", "requirements.txt", "uv.lock", "poetry.lock"), (".cache/pip", ".cache/uv", "Library/Caches/pip", ".cache/pypoetry"), "PIP_CACHE_DIR"),
    ("rust", ("Cargo.toml",), (".cargo", ".rustup"), "CARGO_HOME"),
    ("go", ("go.mod",), ("go", "Library/Caches/go-build", ".cache/go-build"), "GOMODCACHE"),
    ("swift", ("Package.swift", "Podfile"), ("Library/Caches/CocoaPods", "Library/Developer/Xcode/DerivedData", ".swiftpm"), "CP_HOME_DIR"),
    ("flutter", ("pubspec.yaml",), (".pub-cache",), "PUB_CACHE"),
    ("firebase", ("firebase.json",), (".cache/firebase",), None),
)


def detect(repo: str | os.PathLike) -> list[dict]:
    root = Path(repo)
    found = []
    for name, markers, caches, env in TOOLCHAINS:
        hit = [m for m in markers if (root / m).exists()]
        if not hit:
            continue
        env_override = os.environ.get(env) if env else None
        dirs = []
        missing = []
        # both the env-relocated cache (this shell) and the defaults (a lane may run under a different environment)
        candidates = ([Path(env_override).expanduser()] if env_override else []) + [HOME / c for c in caches]
        for c in candidates:
            if c.exists():
                dirs.append(str(c.resolve()))
            else:
                missing.append(str(c))
        found.append({"toolchain": name, "markers": hit, "writable": sorted(set(dirs)), "missing": missing, "env": env})
    return found


def writable_roots(repo: str | os.PathLike, extra: list[str] | None = None) -> list[str]:
    roots = {d for t in detect(repo) for d in t["writable"]}
    for e in extra or []:
        p = Path(e).expanduser()
        if p.exists():
            roots.add(str(p.resolve()))
    return sorted(roots)


def agy_workspace_path(path: str | os.PathLike, roots: list[str] | None = None) -> str:
    """The form of `path` to hand agy as `--add-dir`: the opposite rule to codex.

    Headless `agy -p` has no workspace unless `--add-dir` names one (measured on agy 1.2.9: 17 skills listed
    without it, 120 with it; workspace rules and `.agents/` customizations load only with it), and Antigravity
    matches trust against the path as written, so a physical `/Volumes/...` path under a trusted `~/CureVault/...`
    symlink is rewritten to the trusted form. Paths under no trusted root come back absolute and unchanged.
    """
    if roots is None:
        try:
            cfg = json.loads((HOME / ".gemini" / "antigravity-cli" / "settings.json").read_text())
            roots = list(cfg.get("trustedWorkspaces", []))
        except (OSError, ValueError):
            roots = []
    target = os.path.abspath(os.fspath(path))
    real = os.path.realpath(target)
    for root in roots:
        root = root.rstrip("/")
        if target == root or target.startswith(root + "/"):
            return target
        rr = os.path.realpath(root)
        if real == rr or real.startswith(rr + "/"):
            return root + real[len(rr):]
    return target


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(json.dumps({"repo": str(Path(repo).resolve()), "toolchains": detect(repo), "writable_roots": writable_roots(repo)}, indent=2))
