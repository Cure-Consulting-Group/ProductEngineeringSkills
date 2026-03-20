# Stitch MCP Tool Schemas

Complete reference for all tools exposed by the `stitch-mcp` proxy (`@_davideast/stitch-mcp`).

## Namespace Discovery

Before calling any tool, run `list_tools` to find the Stitch MCP prefix. The prefix varies by client configuration (e.g., `stitch:`, `mcp_stitch:`). Use this prefix for all subsequent calls.

---

## Virtual Tools (Custom Proxy Tools)

These tools are implemented by the stitch-mcp proxy and combine multiple API calls for convenience.

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

These tools are proxied directly from the Stitch API.

### `list_projects`

Lists all Stitch projects accessible to the authenticated user.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filter` | string | No | Filter string (e.g., `"view=owned"` for user-owned projects) |

**Output:** Array of project objects with `name` (path format: `projects/{id}`), `title`, `description`, `designTheme`, and metadata.

**Example Call:**
```json
{
  "tool": "list_projects",
  "arguments": {
    "filter": "view=owned"
  }
}
```

**When to use:** Discovering project IDs when the user provides a project name or URL instead of a numeric ID.

---

### `list_screens`

Lists all screens within a Stitch project.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Stitch project ID (numeric only, not the full path) |

**Output:** Array of screen objects with `name`, `title`, `width`, `height`, `deviceType`, and asset URLs.

**Example Call:**
```json
{
  "tool": "list_screens",
  "arguments": {
    "projectId": "13534454087919359824"
  }
}
```

**When to use:** Enumerating screens for sync or audit workflows. Always call this before iterating over screens.

---

### `get_screen`

Retrieves complete screen metadata including asset download URLs.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Project ID (numeric) |
| `screenId` | string | Yes | Screen ID (numeric) |

**Output:** Full screen object including:
- `screenshot.downloadUrl` — URL to download the screen image
- `htmlCode.downloadUrl` — URL to download the HTML source
- `width`, `height` — Screen dimensions
- `deviceType` — Target device type
- `title` — Screen title

**Example Call:**
```json
{
  "tool": "get_screen",
  "arguments": {
    "projectId": "13534454087919359824",
    "screenId": "abc123"
  }
}
```

**When to use:** When you need full screen metadata (dimensions, device type) alongside the code. For code-only retrieval, prefer `get_screen_code`.

---

### `generate_screen` / `generate_screen_from_text`

Generates a new screen from a natural language prompt.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Project ID to add the screen to |
| `prompt` | string | Yes | Natural language description of the desired screen |
| `designSystem` | string | No | DESIGN.md content to apply during generation |
| `width` | number | No | Screen width in pixels (default: 1440 for web, 390 for mobile) |
| `height` | number | No | Screen height in pixels |
| `deviceType` | string | No | Target device (`desktop`, `mobile`, `tablet`) |

**Output:** Screen object with the generated screen's ID, title, and asset URLs.

**Example Call:**
```json
{
  "tool": "generate_screen",
  "arguments": {
    "projectId": "13534454087919359824",
    "prompt": "A modern checkout page with order summary, payment form with card inputs, and a green 'Complete Purchase' CTA button. Clean white background with subtle gray card containers.",
    "designSystem": "# Design System: Vendly\n## Color Palette\n- Primary: #00A859...",
    "deviceType": "mobile"
  }
}
```

**When to use:** Creating new screens. Always enhance the prompt using the Prompt Enhancement Protocol (SKILL.md Section 4) before calling this tool.

---

### `edit_screen` / `edit_screens`

Modifies an existing screen based on natural language instructions.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Project ID |
| `screenId` | string | Yes | Screen ID to edit |
| `prompt` | string | Yes | Edit instructions in natural language |

**Output:** Updated screen object.

**Example Call:**
```json
{
  "tool": "edit_screen",
  "arguments": {
    "projectId": "13534454087919359824",
    "screenId": "abc123",
    "prompt": "Change the header background to dark navy (#1B2A4A) and make the CTA button gold (#C9A84C)"
  }
}
```

**When to use:** Iterative refinement of existing screens. Prefer this over regeneration for targeted changes — it preserves the existing design context.

---

### `extract_design_system`

Extracts a design system specification from an existing Stitch project's screens.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `projectId` | string | Yes | Project ID to analyze |

**Output:** Markdown-formatted design system document with colors, typography, spacing, and component patterns extracted from the project's screens.

**Example Call:**
```json
{
  "tool": "extract_design_system",
  "arguments": {
    "projectId": "13534454087919359824"
  }
}
```

**When to use:** Bootstrapping a DESIGN.md from an existing Stitch project. Run this first, then refine the output into a proper DESIGN.md seed.

---

### `get_project`

Retrieves full project metadata including design theme configuration.

**Input Schema:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Project name in path format: `projects/{id}` |

**Output:** Project object with `designTheme` (color mode, fonts, roundness, custom colors), description, and device type preferences.

**Example Call:**
```json
{
  "tool": "get_project",
  "arguments": {
    "name": "projects/13534454087919359824"
  }
}
```

**When to use:** Extracting project-level design theme settings. Use when creating or updating DESIGN.md from project metadata.

---

## CLI Commands (Non-MCP)

These commands run directly via the stitch-mcp CLI, not through the MCP protocol:

| Command | Description |
|---|---|
| `npx @_davideast/stitch-mcp init` | Guided setup: auth, gcloud, MCP config |
| `npx @_davideast/stitch-mcp serve -p <id>` | Local dev server for project screens |
| `npx @_davideast/stitch-mcp site -p <id>` | Generate Astro project from screens |
| `npx @_davideast/stitch-mcp view` | Interactive terminal browser |
| `npx @_davideast/stitch-mcp tool [name]` | Invoke any MCP tool from CLI |
| `npx @_davideast/stitch-mcp tool -s` | List all tools with schemas |
| `npx @_davideast/stitch-mcp proxy` | Run MCP proxy for IDE agents |

## Environment Variables

| Variable | Purpose |
|---|---|
| `STITCH_API_KEY` | Direct API key authentication (bypasses OAuth) |
| `STITCH_ACCESS_TOKEN` | Pre-existing access token |
| `STITCH_USE_SYSTEM_GCLOUD` | Set to `"1"` to use system gcloud instead of bundled |
| `STITCH_PROJECT_ID` | Override the GCP project ID |
| `GOOGLE_CLOUD_PROJECT` | Alternative GCP project ID variable |
| `STITCH_HOST` | Custom Stitch API endpoint |
