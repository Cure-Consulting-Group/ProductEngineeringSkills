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

  // Skip if running in CI or if SKIP_CLAUDE_PLUGIN_INSTALL is set
  if (process.env.CI || process.env.SKIP_CLAUDE_PLUGIN_INSTALL) {
    console.log("[cure-plugin] Skipping plugin install (CI or opt-out detected).");
    return;
  }

  try {
    fs.mkdirSync(claudePluginsDir, { recursive: true });

    // Remove existing symlink or directory at the destination
    if (fs.existsSync(pluginDest)) {
      const stat = fs.lstatSync(pluginDest);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(pluginDest);
      } else {
        // Don't clobber a real directory (e.g. a git clone) — warn instead
        console.log(
          `[cure-plugin] ${pluginDest} already exists (not a symlink). Skipping — remove it manually to use the npm-installed version.`
        );
        return;
      }
    }

    // Create symlink: ~/.claude/plugins/ProductEngineeringSkills -> <node_modules>/...
    fs.symlinkSync(packageRoot, pluginDest, "dir");
    console.log(`[cure-plugin] Linked plugin to ${pluginDest}`);

    // Register in user-level Claude settings
    const settingsPath = path.join(os.homedir(), ".claude", "settings.json");
    let settings = {};
    if (fs.existsSync(settingsPath)) {
      try {
        settings = JSON.parse(fs.readFileSync(settingsPath, "utf-8"));
      } catch {
        // If settings file is malformed, start fresh
        settings = {};
      }
    }

    const plugins = settings.enabledPlugins || [];
    if (!plugins.includes(PLUGIN_NAME)) {
      plugins.push(PLUGIN_NAME);
      settings.enabledPlugins = plugins;
      fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + "\n");
      console.log(`[cure-plugin] Registered "${PLUGIN_NAME}" in ${settingsPath}`);
    }

    console.log("[cure-plugin] Done! Plugin is ready for all Claude Code sessions.");
  } catch (err) {
    // Non-fatal — don't break npm install if plugin linking fails
    console.warn(`[cure-plugin] Could not auto-install plugin: ${err.message}`);
    console.warn("[cure-plugin] You can manually load it with: claude --plugin-dir <path>");
  }
}

main();
