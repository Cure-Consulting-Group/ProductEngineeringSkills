# MCP servers — opt-in per project

MCP servers are **not** shipped auto-enabled by this plugin. They each need
project-specific credentials (a GitHub token, a Firebase login, a database URL)
or interactive auth (Sentry), so auto-loading them makes every project that
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
   profile. Claude Code expands `${VAR}` in `.mcp.json` `command`, `args`, `env`,
   `url` and `headers`; an unset variable leaves that server failing to connect.

   | Server | Package / endpoint | Auth and env | Verified |
   |---|---|---|---|
   | `github` | remote `https://api.githubcopilot.com/mcp/` | `CURE_GITHUB_MCP_PAT` (fine-grained PAT), sent as `Authorization: Bearer ${CURE_GITHUB_MCP_PAT}`. A project-specific name on purpose: Claude Code reads some well-known credential variables as empty in remote `headers`, so don't reuse `GITHUB_TOKEN`/`GH_TOKEN`. GitHub's Claude Code guide documents PAT-in-header only for the remote server; OAuth is not documented for it | https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md, 2026-10-24 |
   | `sentry` | remote `https://mcp.sentry.dev/mcp` | OAuth on first use (`/mcp` → authenticate) | — |
   | `firebase` | official `firebase-tools@15.33.0 mcp` (pinned; Firebase's docs use `@latest`) | the Firebase CLI's own credentials: `firebase login`, or Application Default Credentials. No service-account key in the config. Optional args: `--dir <abs path to firebase.json dir>`, `--only auth,firestore,storage` | firebase.google.com/docs/ai-assistance/mcp-server, 2026-10-24 |
   | `postgres` | `@bytebase/dbhub@1.5.0 --transport stdio` (pinned) | `DATABASE_URL`, passed to DBHub as `DSN` (DBHub reads `--dsn`, then `DSN`, then `DB_*`; `DB_URL` is not read) | dbhub.ai/config/command-line, 2026-10-24 |

   Before Wave 7 this template used `mcp-firestore` (third-party, unpinned, needed
   a service-account key) and passed the database URL as `DB_URL`, which DBHub
   ignores. If your project copied the old template, replace both entries.

3. Restart Claude Code (or run `/mcp`) and authenticate any that need it.

## Pinned versions

Every `npx` package in `.mcp.json.example` and `.lsp.json` is pinned to an exact
version, so a compromised or broken `latest` can't reach every consumer at once.
Bump deliberately: `npm view <pkg> version time`, pick a release at least two
weeks old, and update both files in one commit.

| File | Package | Pinned |
|---|---|---|
| `.mcp.json.example` | `firebase-tools` | 15.33.0 |
| `.mcp.json.example` | `@bytebase/dbhub` | 1.5.0 |
| `.lsp.json` | `typescript-language-server` (uses the workspace's `typescript`; needs Node ≥ 22.22.2) | 6.0.2 |
| `.lsp.json` | `pyright` (`pyright-langserver` bin) | 1.1.414 |

## Remove servers you don't use

Delete the entries you don't need from your project's `.mcp.json`. A server you
don't configure but leave in place will report a connection error every session.

## Why opt-in (design note)

A shared library plugin is loaded by many projects with different stacks. An MCP
server that needs a `DATABASE_URL` is meaningful only in the projects that have a
database. Shipping it enabled-by-default fails everywhere else. Opt-in keeps the
default install quiet and correct; projects turn on exactly the integrations they
have credentials for.
