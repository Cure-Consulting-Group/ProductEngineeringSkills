# Stitch MCP Tool Schemas

Reference for the tools exposed by Google's hosted Stitch MCP server and by the community `stitch-mcp` proxy (`@_davideast/stitch-mcp`). Pinned to `0.9.0` (still latest on npm, last published 2026-05-28; checked 2026-10-24): it is an individual-maintained package that runs with your Google credentials, so bump the pin deliberately after reading its changelog.

## Namespace Discovery

Before calling any tool, run `list_tools` to find the Stitch MCP prefix. The prefix varies by client configuration (e.g., `stitch:`, `mcp_stitch:`). Use this prefix for all subsequent calls.

---

## Virtual Tools (Custom Proxy Tools)

These tools exist only in the stitch-mcp proxy — Google's hosted server doesn't expose them (use `get_screen` + `download_file` there). They are implemented by the proxy and combine multiple API calls for convenience.

### `build_site`

Builds a multi-page site from a Stitch project by mapping screens to routes. Returns the design HTML for each page.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Stitch project ID (numeric) |
| `routes` | array | Yes | Array of screen-to-route mappings |
| `routes[].screenId` | string | Yes | Screen ID within the project |
| `routes[].route` | string | Yes | URL route path (e.g., `/`, `/about`) |

**Output:** Object with route keys mapping to HTML content strings.

**Example Call:**
```json
{
  "tool": "build_site",
  "arguments": {
    "projectId": "13534454087919359824",
    "routes": [
      { "screenId": "abc123", "route": "/" },
      { "screenId": "def456", "route": "/about" }
    ]
  }
}
```

**When to use:** Building complete multi-page sites from Stitch projects. Prefer over individual `get_screen_code` calls when exporting an entire site.

---

### `get_screen_code`

Retrieves a screen and downloads its HTML code content.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Stitch project ID (numeric) |
| `screenId` | string | Yes | Screen ID within the project |

**Output:** String containing the full HTML/CSS source code of the screen.

**Example Call:**
```json
{
  "tool": "get_screen_code",
  "arguments": {
    "projectId": "13534454087919359824",
    "screenId": "abc123"
  }
}
```

**When to use:** Retrieving individual screen HTML for code conversion, token extraction, or local file export. Use this over `build_site` when working with a single screen.

---

### `get_screen_image`

Retrieves a screen and downloads its screenshot image as base64.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Stitch project ID (numeric) |
| `screenId` | string | Yes | Screen ID within the project |

**Output:** Base64-encoded PNG image of the screen screenshot.

**Example Call:**
```json
{
  "tool": "get_screen_image",
  "arguments": {
    "projectId": "13534454087919359824",
    "screenId": "abc123"
  }
}
```

**When to use:** Visual audits, design reviews, or generating preview thumbnails. Prefer this for audit workflows where pixel-level comparison is needed.

---

## Upstream Stitch MCP Tools

These tools come from Google's hosted server (`https://stitch.googleapis.com/mcp`) and pass through the proxy unchanged. Schemas below are from the server's live `tools/list`, checked 2026-10-24; Google changes them without notice, so re-read the schema your client shows before relying on an argument. IDs are bare (`4044680601076201931`) where the argument is `projectId`, and resource names (`projects/{id}`, `projects/{id}/screens/{screen}`, `assets/{id}`) where it is `name`.

| Tool | Required arguments | Optional | Returns / notes |
|---|---|---|---|
| `list_projects` | — | `filter`: `view=owned` (default) or `view=shared` | Projects with `name` (`projects/{id}`), title, theme |
| `get_project` | `name` (`projects/{id}`) | — | Project metadata, design theme, and screen instances (needed by `apply_design_system`) |
| `create_project` | — | `title` | New project |
| `delete_project` | `name` | — | Irreversible; confirm with the user first |
| `list_screens` | `projectId` | — | Screens with `html_code.name` and `screenshot.name` file references |
| `get_screen` | `name` (`projects/{p}/screens/{s}`) | — | Screen metadata and file references |
| `download_file` | `name` (`projects/{p}/files/{f}`, from `html_code.name` / `screenshot.name`) | — | `html` for HTML files; base64 `image` + `image_metadata` for screenshots. Use this, not `download_url` (needs credentials, returns a JSON wrapper) |
| `generate_screen_from_text` | `projectId`, `prompt` | `designSystem` (asset ID `assets/{id}`, **not** DESIGN.md text), `deviceType` (`MOBILE`, `DESKTOP`, `TABLET`, `AGNOSTIC`), `modelId` (`GEMINI_3_8_FLASH`, `GEMINI_3_5_FLASH_LITE`) | Takes minutes. On timeout don't retry; poll `get_screen` every 30 s, up to 10 times. Relay any `output_components` suggestions to the user |
| `edit_screens` | `projectId`, `selectedScreenIds` (array, bare IDs), `prompt` | `deviceType`, `modelId` | Targeted edits; prefer over regeneration |
| `generate_variants` | `projectId`, `selectedScreenIds`, `prompt`, `variantOptions` | `variantOptions.variantCount` 1–5 (default 3), `creativeRange` `REFINE`/`EXPLORE`/`REIMAGINE`, `aspects` (`LAYOUT`, `COLOR_SCHEME`, `IMAGES`, `TEXT_FONT`, `TEXT_CONTENT`) | Explore alternatives of existing screens |
| `list_design_systems` | — | `projectId` (empty = global) | Design-system asset IDs |
| `create_design_system` | `designSystem` (`displayName`, `theme`: `colorMode`, `headlineFont`, `bodyFont`, `roundness`, `customColor`) | `projectId`, `theme.designMd`, `typography`, `spacing`, override colors | Follow with `update_design_system` to apply it |
| `update_design_system` | `name` (`assets/{id}`), `projectId`, `designSystem` | — | Changes a project's theme |
| `upload_design_md` | `projectId`, `designMdBase64` (valid UTF-8) | — | Follow immediately with `create_design_system_from_design_md` |
| `create_design_system_from_design_md` | `projectId`, `selectedScreenInstance` (from the upload) | `deviceType` | Turns an uploaded DESIGN.md into a Stitch design system |
| `apply_design_system` | `projectId`, `selectedScreenInstances` (from `get_project`), `assetId` (bare) | — | Restyles the chosen screens with that design system |

There is no `extract_design_system` tool on the hosted server: build DESIGN.md from screen HTML (`download_file`) plus the project theme (`get_project`, `list_design_systems`).

**Example — generate with an existing design system:**
```json
{
  "tool": "generate_screen_from_text",
  "arguments": {
    "projectId": "4044680601076201931",
    "prompt": "A modern checkout page with order summary, payment form, and a green 'Complete Purchase' CTA. Palette: primary #00A859 ...",
    "designSystem": "assets/15996705518239280238",
    "deviceType": "MOBILE"
  }
}
```

---

## CLI Commands (Non-MCP)

These commands run directly via the stitch-mcp CLI, not through the MCP protocol:

| Command | Description |
|---|---|
| `npx @_davideast/stitch-mcp@0.9.0 init` | Guided setup: auth, gcloud, MCP config |
| `npx @_davideast/stitch-mcp@0.9.0 serve -p <id>` | Local dev server for project screens |
| `npx @_davideast/stitch-mcp@0.9.0 site -p <id>` | Generate Astro project from screens |
| `npx @_davideast/stitch-mcp@0.9.0 view` | Interactive terminal browser |
| `npx @_davideast/stitch-mcp@0.9.0 tool [name]` | Invoke any MCP tool from CLI |
| `npx @_davideast/stitch-mcp@0.9.0 tool -s` | List all tools with schemas |
| `npx @_davideast/stitch-mcp@0.9.0 proxy` | Run MCP proxy for IDE agents |

## Environment Variables

| Variable | Purpose |
|---|---|
| `STITCH_API_KEY` | Direct API key authentication (bypasses OAuth) |
| `STITCH_ACCESS_TOKEN` | Pre-existing access token |
| `STITCH_USE_SYSTEM_GCLOUD` | Set to `"1"` to use system gcloud instead of bundled |
| `STITCH_PROJECT_ID` | Override the GCP project ID |
| `GOOGLE_CLOUD_PROJECT` | Alternative GCP project ID variable |
| `STITCH_HOST` | Custom Stitch API endpoint |
