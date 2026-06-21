# MCP servers — opt-in per project

MCP servers are **not** shipped auto-enabled by this plugin. They each need
project-specific credentials (a Firestore service account, a database URL) or
interactive auth (GitHub, Sentry), so auto-loading them makes every project that
*doesn't* have those secrets show a wall of connection errors.

Instead, the library ships a template — `.mcp.json.example` — that a project
opts into when it actually wants those integrations.

## Enable for a project

1. Copy the template into the project root and activate it:
   ```bash
   cp .mcp.json.example .mcp.json
   ```
   (Or copy just the server entries you want into an existing `.mcp.json`.)

2. Set the environment variables the servers reference, e.g. in your shell
   profile or the project's `.env`:

   | Server | Required env | Notes |
   |---|---|---|
   | `github` | — | Interactive auth on first use (`/mcp` → authenticate) |
   | `sentry` | — | OAuth on first use (`/mcp` → authenticate) |
   | `firebase-firestore` | `GOOGLE_APPLICATION_CREDENTIALS` (path to service-account JSON), `FIREBASE_PROJECT_ID` | |
   | `postgres` | `DATABASE_URL` | e.g. `postgres://user:pass@host:5432/db` |

3. Restart Claude Code (or run `/mcp`) and authenticate any that need it.

## Remove servers you don't use

Delete the entries you don't need from your project's `.mcp.json`. A server you
don't configure but leave in place will report a connection error every session.

## Why opt-in (design note)

A shared library plugin is loaded by many projects with different stacks. An MCP
server that needs a `DATABASE_URL` is meaningful only in the projects that have a
database. Shipping it enabled-by-default fails everywhere else. Opt-in keeps the
default install quiet and correct; projects turn on exactly the integrations they
have credentials for.
