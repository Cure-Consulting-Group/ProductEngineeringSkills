---
name: mcp-server-builder
description: "Design and build MCP (Model Context Protocol) servers — the protocol agents use to call tools, expose resources, and consume prompts"
when_to_use: "Use when building or migrating an MCP server (Python/TypeScript SDK), wrapping a REST API as MCP, or designing tool schemas for agents. NOT for consuming an MCP server (.mcp.json) or general API design (api-architect)."
argument-hint: "[server-name]"
---

# MCP Server Builder

Design and ship production MCP servers. Cure standard: tools are explicit, schemas are strict, secrets never leak into responses, and every mutation is confirmable. For protocol reference, see `modelcontextprotocol.io`.

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

Additionally gather (domain-specific):
- Grep for existing MCP usage: `@modelcontextprotocol|mcp\.server|FastMCP|stdio_server` to extend rather than duplicate
- Read `.mcp.json` at repo root if present — see how this server will be consumed

## Step 1: Classify the Build

| Trigger | Pattern |
|---------|---------|
| Have OpenAPI spec | Generate tool stubs from spec, hand-tune schemas |
| Building from scratch | Define tool surface first, implement second |
| Wrapping existing internal API | Thin tool layer, reuse auth, no business logic in server |
| Wrapping third-party SaaS | Add caching + rate limit shim; SaaS quotas are not MCP's concern |
| REST → MCP migration | Map endpoints to tools; collapse CRUD into fewer, semantic tools |
| Multi-tenant / hosted MCP | Use HTTP transport with auth; never stdio |
| Local dev tool (lint, db, file) | stdio, single user, no network |

If unclear, ask one question: *"Will this server run as a local subprocess, or be hosted and called over the network?"*

## Step 2: Gather Context

1. **Language** — Python (`mcp` SDK) or TypeScript (`@modelcontextprotocol/sdk`)? Default: match the surrounding codebase. See `rules/python.md` and `rules/web.md`.
2. **Transport** — stdio, SSE, or streamable HTTP? (Decision matrix below.)
3. **Auth model** — none (local), API key, OAuth, mTLS?
4. **Tool count** — under 10, 10–30, over 30? Over 30 means split into multiple servers.
5. **Resources vs tools** — does the agent need to *read* documents, or *do* things? Often both.
6. **Side effects** — read-only, mutating, irreversible? Mutating tools require explicit `confirm` parameter.
7. **Latency budget** — agent-perceived. Tools over 5s should stream progress or be made async with a separate "check status" tool.
8. **Distribution** — npm/PyPI for general use, internal registry, or single-user `.mcp.json` install?

## Step 3: Tool Schema Design

### Naming Rules

```
verb_object pattern, snake_case:
  GOOD:  search_orders, create_invoice, get_customer
  BAD:   orderSearch, doSearch, things, helper

Namespace prefix when wrapping a known service:
  stripe_create_charge, github_open_pr, jira_assign_ticket

Avoid generic names that collide across servers:
  BAD:   query, search, get, list   (every server has these)
  GOOD:  search_jira_issues, list_github_prs
```

Aim for 5–20 tools. Over 30 confuses model tool-selection — split the server.

### Input Schema (JSON Schema, Strict)

```json
{
  "name": "search_orders",
  "description": "Find orders by customer email or order ID. Returns up to 50 results sorted by created_at desc.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "email":    { "type": "string", "format": "email" },
      "order_id": { "type": "string", "pattern": "^ord_[a-zA-Z0-9]{16}$" },
      "limit":    { "type": "integer", "minimum": 1, "maximum": 50, "default": 20 }
    },
    "oneOf": [
      { "required": ["email"] },
      { "required": ["order_id"] }
    ],
    "additionalProperties": false
  }
}
```

Rules:
- `additionalProperties: false` on every object — block schema drift
- Use `enum` over free-form strings whenever possible
- `description` is read by the model — write it for an LLM, not a human (action-oriented, mention output shape, mention limits)
- For mutating tools, require an explicit `confirm: { type: "boolean", const: true }` argument

### Output Conventions

```
Success: structured content with explicit shape (not raw API JSON dumped)
  - Strip secrets, internal IDs, debug fields
  - Cap arrays (return first N + "has_more": true)
  - Include a "next_cursor" if paginated

Error: throw McpError with code + message
  - InvalidParams (-32602)  — bad input
  - MethodNotFound (-32601) — unknown tool
  - InternalError (-32603)  — unexpected
  - Custom application errors as data field
  - Never leak stack traces, file paths, SQL, or upstream auth headers
```

### Rate Limiting

Built-in per-tool limits — do not rely on the agent:
```
read tools:     60/min per session
write tools:    20/min per session
expensive (LLM, search, large export): 10/min, with explicit cost note in description
```

## Step 4: Resource Design (When Tools Aren't Enough)

| Use a Tool when | Use a Resource when |
|----------------|---------------------|
| Action with side effects | Read-only document or dataset |
| Parameters change every call | Stable URI |
| Returns dynamic computed result | Returns a file-like object the agent should keep in context |
| Search, query, filter | "Here's the README", "here's the schema", "here's the changelog" |

Resource URI scheme: `{server}://{type}/{id}`
```
postgres://schema/public.users
github://repo/cure-cg/portfolio
sentry://issue/PROJ-1234
```

Expose `resources/list` and `resources/read`. Never expose huge resources unbounded — cap at ~100KB or paginate. Subscribe (`resources/subscribe`) only if the data genuinely changes during a session.

Prompts (the third primitive): expose only when there's a known, reusable user-facing prompt — e.g., "review_pr", "summarize_incident". Skip otherwise.

## Step 5: Server Implementation Patterns

### Python (mcp SDK)

```python
# pyproject.toml dep: mcp>=1.0.0
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

server = Server("cure-orders")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_orders",
            description="Find orders by email or order_id. Returns <=50 results.",
            inputSchema={ "type": "object", "properties": { ... }, "additionalProperties": False }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_orders":
        result = await orders_service.search(**arguments)  # validate + sanitize
        return [TextContent(type="text", text=json.dumps(result))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### TypeScript (@modelcontextprotocol/sdk)

```typescript
// package.json dep: "@modelcontextprotocol/sdk": "^1.0.0"
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server({ name: "cure-orders", version: "1.0.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "search_orders",
    description: "Find orders by email or order_id. Returns <=50 results.",
    inputSchema: { type: "object", properties: { /* ... */ }, additionalProperties: false }
  }]
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;
  // Validate args with zod against the inputSchema, then dispatch.
});

await server.connect(new StdioServerTransport());
```

### Server Hygiene

- One server, one domain — don't bundle "everything for client X" into a single MCP
- All env config via env vars (`MCP_SERVER_API_KEY`), never CLI flags
- Log to stderr only — stdout is reserved for the protocol
- Graceful shutdown on SIGINT/SIGTERM, flush in-flight requests
- Version your tool schemas. Breaking schema change → new tool name (`search_orders_v2`), keep old for one release

## Step 6: Testing

### Contract Tests (Required)

For every tool:
1. Schema validation: invalid input → `InvalidParams` error, valid input → success
2. Authorization: missing/expired creds → typed error, never raw upstream response
3. Output shape: response matches declared output schema
4. Idempotency for mutating tools: same input twice → same effect (or explicit error on duplicate)

### Integration with Claude Code

Add to `.mcp.json`:
```json
{
  "mcpServers": {
    "cure-orders": {
      "command": "python",
      "args": ["-m", "cure_orders.server"],
      "env": { "CURE_ORDERS_API_KEY": "${CURE_ORDERS_API_KEY}" }
    }
  }
}
```

Manual test loop:
1. `claude mcp list` — server appears
2. `claude --debug` and invoke a tool — inspect stderr for protocol errors
3. Bad input — confirm typed error reaches the agent, not a stack trace
4. Kill the server mid-call — agent should get a clean disconnect, not hang

### Eval

Maintain a small golden set: 10–20 representative tool calls + expected output shapes. Run on every PR. If schemas drift, eval fails before users notice.

## Step 7: Distribution

| Audience | Distribution |
|----------|--------------|
| Single client / engagement | Internal git, install via `pip install -e` or `npm link`, wired in `.mcp.json` |
| Cure-wide, multiple clients | Internal PyPI / npm registry, semver pinned in `.mcp.json` |
| Public | PyPI / npm, README with `.mcp.json` snippet, version in `_meta` field |
| Hosted (multi-tenant) | Containerized, behind auth, HTTP transport, versioned URL `/v1/mcp` |

Versioning rules (semver, strict):
- **Patch**: bug fix in tool implementation, no schema change
- **Minor**: new tool added, new optional field added, new resource added
- **Major**: any field renamed, removed, type changed; tool removed; required arg added

## Decision Matrix: Transport

| Transport | Use When | Avoid When |
|-----------|----------|------------|
| **stdio** | Local subprocess (Claude Code, Codex desktop). Single user. No network. | Multi-tenant, hosted, or remote consumption |
| **SSE** | Legacy hosted servers, server-pushed events to single client. | New builds — prefer streamable HTTP |
| **Streamable HTTP** | Hosted, multi-tenant, browser-reachable, standard auth (Bearer/OAuth). | Local dev tools (overhead not worth it) |

Default: **stdio for local, streamable HTTP for hosted.** SSE only for backwards compat.

## Anti-Patterns

- **Mutating tool with no `confirm`**. Model misfires happen. Every irreversible action needs an explicit boolean.
- **Schema drift**: returning extra fields not in the declared output. Pin shape, version when changing.
- **Leaking secrets in tool responses**. Never echo back the API key, internal user IDs, or upstream auth headers in success or error paths. Audit with: `grep -rE "api_key|token|secret|password" responses_log/`
- **Stuffing 50 tools into one server**. Model tool-selection degrades sharply past ~30 tools. Split by domain.
- **Generic tool names** (`query`, `get`, `do`). Collide across servers, model picks wrong one.
- **stdout for logging**. Corrupts the protocol. stderr only.
- **No timeout**. A hung upstream blocks the agent indefinitely. Every external call gets a hard timeout.
- **Returning raw upstream JSON**. The agent doesn't need 200 fields when 5 matter. Shape the output.
- **No versioning strategy**. First breaking change → angry consumers. Decide v1/v2 strategy before shipping v1.
- **Building MCP when a CLI would do**. If only one user uses it locally and it's already a CLI, MCP is overhead. MCP shines when the agent needs to choose between many tools.

## When NOT to Use This Skill

- **Consuming an existing MCP server** — just edit `.mcp.json`, no skill needed
- **Designing a public REST/GraphQL API** — use `api-architect`
- **Building a Claude Code plugin (skill, agent, hook)** — use `sdlc` or a domain skill; this is plugin territory, not MCP
- **One-off internal CLI tool with one user** — a CLI is simpler; consider MCP only if an agent needs to discover and choose among tools
- **General LLM feature work** — use `ai-feature-builder`

## Code Generation (Required)

Generate actual scaffolding using Write:

1. **Server entry point**: `src/server.{py,ts}` with `list_tools` + `call_tool` handlers, stdio transport
2. **Tool schemas**: `src/tools/{tool_name}.{py,ts}` — one file per tool, schema + handler colocated
3. **Output types**: `src/types.{py,ts}` — declared output shapes (Pydantic / Zod)
4. **Config**: `pyproject.toml` or `package.json` with the right SDK pin
5. **`.mcp.json` snippet** in README showing how to install
6. **Contract tests**: `tests/test_tools.{py,ts}` — schema validation + happy path per tool
7. **README.md**: tool list, install snippet, env vars required

Before generating, Glob `**/*server*.{py,ts}` and Read existing servers to extend rather than duplicate.
