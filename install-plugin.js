#!/usr/bin/env node
/**
 * Postinstall script for @cure-consulting-group/product-engineering-skills
 *
 * Symlinks (or copies) the installed package into ~/.claude/plugins/
 * so Claude Code can discover it as a plugin automatically.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");

const PLUGIN_DIR_NAME = "ProductEngineeringSkills";
const PLUGIN_NAME = "cure-product-engineering";

function main() {
  // Where npm installed this package
  const packageRoot = __dirname;

  // Where Claude Code looks for plugins
  const claudePluginsDir = path.join(os.homedir(), ".claude", "plugins");
  const pluginDest = path.join(claudePluginsDir, PLUGIN_DIR_NAME);

  // Where Gemini CLI looks for extensions/skills
  const geminiExtensionsDir = path.join(os.homedir(), ".gemini", "extensions");
  const geminiDest = path.join(geminiExtensionsDir, PLUGIN_NAME);

  // Skip if running in CI or if SKIP_CLAUDE_PLUGIN_INSTALL is set
  if (process.env.CI || process.env.SKIP_CLAUDE_PLUGIN_INSTALL) {
    console.log("[cure-plugin] Skipping plugin install (CI or opt-out detected).");
    return;
  }

  try {
    // 1. Claude Install
    fs.mkdirSync(claudePluginsDir, { recursive: true });
    setupSymlink(packageRoot, pluginDest, "[Claude]");

    // Register in user-level Claude settings
    registerInClaudeSettings(PLUGIN_NAME);

    // 2. Gemini Install
    fs.mkdirSync(geminiExtensionsDir, { recursive: true });
    setupSymlink(packageRoot, geminiDest, "[Gemini]");

    console.log("[cure-plugin] Done! Plugin is ready for Claude Code and Gemini CLI sessions.");
  } catch (err) {
    // Non-fatal — don't break npm install if plugin linking fails
    console.warn(`[cure-plugin] Could not auto-install plugin: ${err.message}`);
    console.warn("[cure-plugin] You can manually load it with: claude --plugin-dir <path>");
  }
}

function setupSymlink(source, dest, label) {
  if (fs.existsSync(dest)) {
    const stat = fs.lstatSync(dest);
    if (stat.isSymbolicLink()) {
      fs.unlinkSync(dest);
    } else {
      console.log(`${label} ${dest} already exists (not a symlink). Skipping.`);
      return;
    }
  }
  fs.symlinkSync(source, dest, "dir");
  console.log(`${label} Linked plugin to ${dest}`);
}

function registerInClaudeSettings(pluginName) {
  const settingsPath = path.join(os.homedir(), ".claude", "settings.json");
  let settings = {};
  if (fs.existsSync(settingsPath)) {
    try {
      settings = JSON.parse(fs.readFileSync(settingsPath, "utf-8"));
    } catch {
      settings = {};
    }
  }

  const plugins = settings.enabledPlugins || [];
  if (!plugins.includes(pluginName)) {
    plugins.push(pluginName);
    settings.enabledPlugins = plugins;
    fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + "\n");
    console.log(`[Claude] Registered "${pluginName}" in ${settingsPath}`);
  }
}

main();
