# MCP Server Builder

**Outcome:** a working MCP server (or a design for one) with a small, well-named tool surface, strict schemas, typed results, honest tool annotations, the right transport and auth, and contract tests. Done when each tool has a schema, annotations, an error path returning `isError`, and a test, and the server runs in at least one real client. Deliver the requested server; don't add unrequested tools.

Cure standard: tools are explicit, schemas are strict, secrets never leak into results, and destructive tools are declared as such so the host can ask for consent.

**Currency (verified 2026-09-23):** current spec revision is **2026-07-28** (modelcontextprotocol.io/specification/2026-07-28/changelog). It made the protocol stateless — no `initialize` handshake or `Mcp-Session-Id`; version and client capabilities travel in each request's `_meta`; servers must implement `server/discover`. Server-initiated requests (elicitation, sampling, roots) are replaced by Multi Round-Trip Requests (`resultType: "input_required"`); Roots, Sampling, Logging, and HTTP+SSE are deprecated; Tasks moved to an extension. SDKs implementing it: TypeScript v2 (`@modelcontextprotocol/server` 2.x — replaces the monolithic `@modelcontextprotocol/sdk` 1.x) and Python `mcp` 2.x (`MCPServer`). Existing v1 servers keep working against older clients; pin `<2` until migrated.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Existing MCP code/SDK: !`grep -rlE '@modelcontextprotocol|from mcp|FastMCP|MCPServer|McpServer' --include=*.py --include=*.ts --include=package.json --include=pyproject.toml . 2>/dev/null | grep -v node_modules | head -8 || echo "(none)"`
- Client configs present: !`ls .mcp.json .codex/config.toml mcp_config.json 2>/dev/null || echo "(none)"`

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

1. **Language** — Python (`mcp` 2.x) or TypeScript (`@modelcontextprotocol/server` 2.x)? Default: match the surrounding codebase.
2. **Transport** — stdio or Streamable HTTP (decision matrix below). Don't start new work on HTTP+SSE.
3. **Auth model** — none (local stdio), or OAuth 2.1 per the spec's authorization section for hosted servers (client registration via Client ID Metadata Documents; Dynamic Client Registration is deprecated). Static API keys only for internal service-to-service.
4. **Tool count** — under 10, 10–30, over 30? Over 30 means split into multiple servers.
5. **Resources vs tools** — does the agent need to *read* documents, or *do* things? Often both.
6. **Side effects** — read-only, mutating, irreversible? Drives tool annotations and whether the tool should ask the user for input mid-call (Step 3).
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
- Schemas may use any JSON Schema 2020-12 keyword; keep `$ref` shallow — clients bound composition depth.
- Declare **tool annotations** honestly: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`, plus a `title`. Hosts use them to decide when to ask the user for consent; clients treat them as untrusted hints, so they are not a security control — enforce authorization server-side.
- For irreversible actions, don't invent a `confirm: true` argument (the model will just set it). Mark the tool `destructiveHint: true` and, when you need the human's answer, return an `input_required` result asking for confirmation (spec's Multi Round-Trip Requests pattern) — the client shows it to the user and retries with the answer.
- Return tools from `tools/list` in a deterministic order (the spec now asks for it; it keeps client prompt caches warm).

### Output Conventions

```
Success: declare an outputSchema and return structuredContent
  (plus a short text summary in content for clients that ignore structure)
  - Strip secrets, internal IDs, debug fields
  - Cap arrays (return first N + "has_more": true), include "next_cursor" if paginated

Tool execution failure (upstream 404, validation, rate limit, business rule):
  return a normal result with isError: true and a message the model can act on
  ("order ord_… not found; search_orders by email instead"). The model sees it
  and can self-correct. SDKs do this for you when the handler throws/raises.

JSON-RPC errors are for protocol faults only: unknown tool, malformed request,
  unsupported protocol version (-32602 Invalid Params, -32601, -32603).

Never leak stack traces, file paths, SQL, or upstream auth headers in either path.
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

Expose `resources/list` and `resources/read`. Never expose huge resources unbounded — cap at ~100KB or paginate. List/read results carry `ttlMs` and `cacheScope` in the current spec; set a real TTL. Change notifications go through `subscriptions/listen` (replaces `resources/subscribe`); add them only if the data genuinely changes while an agent works.

Prompts (the third primitive): expose only when there's a known, reusable user-facing prompt — e.g., "review_pr", "summarize_incident". Skip otherwise.

## Step 5: Server Implementation Patterns

Shapes below are from the v2 SDK docs (verified 2026-09-23); check the SDK README before generating, since v2 is new.

### Python (`mcp` 2.x)

```python
# pyproject.toml: mcp>=2.2,<3
from mcp.server import MCPServer

mcp = MCPServer("cure-orders")

@mcp.tool(annotations={"readOnlyHint": True})
async def search_orders(email: str | None = None, order_id: str | None = None, limit: int = 20) -> list[OrderSummary]:
    """Find orders by customer email or order ID. Returns up to 50, newest first."""
    return await orders_service.search(email=email, order_id=order_id, limit=min(limit, 50))
    # Type hints generate inputSchema/outputSchema; a raised exception becomes an isError result.
```

Run: `uv run mcp dev server.py` (local), `uv run mcp run server.py --transport streamable-http` (hosted).

### TypeScript (`@modelcontextprotocol/server` 2.x)

```typescript
import { McpServer } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import { z } from "zod";

function build() {
  const server = new McpServer({ name: "cure-orders", version: "1.0.0" });
  server.registerTool(
    "search_orders",
    {
      title: "Search orders",
      description: "Find orders by customer email or order ID. Returns up to 50, newest first.",
      inputSchema: z.object({ email: z.string().email().optional(), orderId: z.string().optional(), limit: z.number().int().max(50).default(20) }),
      outputSchema: z.object({ orders: z.array(OrderSummary), hasMore: z.boolean() }),
      annotations: { readOnlyHint: true },
    },
    async (args) => {
      const result = await ordersService.search(args);
      return { structuredContent: result, content: [{ type: "text", text: `${result.orders.length} orders` }] };
    },
  );
  return server;
}

serveStdio(build); // hosted: createMcpHandler(build) + toNodeHandler from @modelcontextprotocol/node
```

The HTTP handler trusts its caller: put Host/Origin validation and token verification in front of it. The factory runs per request, so the endpoint is stateless and scales horizontally; cross-call state goes in explicit handles passed as tool arguments.

### Server Hygiene

- One server, one domain — don't bundle "everything for client X" into a single MCP
- All env config via env vars (`MCP_SERVER_API_KEY`), never CLI flags
- Log to stderr only (stdio) or OpenTelemetry — stdout is reserved for the protocol, and MCP Logging is deprecated
- Graceful shutdown on SIGINT/SIGTERM, flush in-flight requests
- Version your tool schemas. Breaking schema change → new tool name (`search_orders_v2`), keep old for one release

## Step 6: Testing

### Contract Tests (Required)

For every tool:
1. Schema validation: invalid input → `isError` result with an actionable message; valid input → result matching `outputSchema`
2. Authorization: missing/expired creds → typed error, never raw upstream response
3. Output shape: response matches declared output schema
4. Idempotency for mutating tools: same input twice → same effect (or explicit error on duplicate)

### Run it in real clients

Wire it into the client the team uses (env vars for secrets, never inline):

| Client | Config |
|---|---|
| Claude Code | `.mcp.json` `mcpServers.<name>` `{command, args, env}` or `claude mcp add`; check with `claude mcp list` |
| Codex CLI | `~/.codex/config.toml` `[mcp_servers.<name>]` with `command`, `args`, `env` |
| Antigravity | `mcp_config.json` (workspace or plugin) — confirm the current path in the agy docs before use |
| Any | MCP Inspector (`npx @modelcontextprotocol/inspector`) for protocol-level debugging |

Manual loop: server listed → call each tool → bad input yields an `isError` result the agent reacts to, not a stack trace → kill the server mid-call and confirm the client reports a disconnect instead of hanging.

### Eval

Maintain a small golden set: 10–20 representative tool calls + expected output shapes. Run on every PR. If schemas drift, eval fails before users notice.

## Step 7: Distribution

| Audience | Distribution |
|----------|--------------|
| Single client / engagement | Internal git, install via `pip install -e` or `npm link`, wired in `.mcp.json` |
| Cure-wide, multiple clients | Internal PyPI / npm registry, semver pinned in `.mcp.json` |
| Public | PyPI / npm, README with client config snippets, `serverInfo` version returned in result `_meta` |
| Hosted (multi-tenant) | Containerized, behind auth, HTTP transport, versioned URL `/v1/mcp` |

Versioning rules (semver, strict):
- **Patch**: bug fix in tool implementation, no schema change
- **Minor**: new tool added, new optional field added, new resource added
- **Major**: any field renamed, removed, type changed; tool removed; required arg added

## Decision Matrix: Transport

| Transport | Use When | Avoid When |
|-----------|----------|------------|
| **stdio** | Local subprocess (Claude Code, Codex, Antigravity). Single user. No network. | Multi-tenant, hosted, or remote consumption |
| **Streamable HTTP** | Hosted, multi-tenant, OAuth 2.1. Stateless per request in the 2026-07-28 spec. | Local dev tools (overhead not worth it) |
| HTTP+SSE | Deprecated — only to keep an existing legacy client working | Anything new |

## Anti-Patterns

- Destructive tool without `destructiveHint: true` (or with a model-settable `confirm` flag standing in for user consent).
- Throwing protocol errors for tool failures — the model never sees them and can't recover; return `isError`.
- Output drifting from the declared `outputSchema`; version the tool instead.
- More than ~30 tools on one server, or generic names (`query`, `get`) that collide across servers.
- No hard timeout on upstream calls — a hung upstream blocks the agent.
- Returning raw upstream JSON when 5 of 200 fields matter.
- Building MCP when a CLI would do: one local user, one tool, already a CLI.

## When NOT to Use This Skill

- **Consuming an existing MCP server** — just edit the client config, no skill needed
- **Designing a public REST/GraphQL API** — use `api-architect`
- **Building a Claude Code plugin (skill, agent, hook)** — plugin territory, not MCP
- **One-off internal CLI tool with one user** — a CLI is simpler; consider MCP only if an agent needs to discover and choose among tools
- **General LLM feature work** — use `ai-feature-builder`

## Code/Artifact Generation

Applies when Step 1 is a build or migration and the user wants files. Glob `**/*server*.{py,ts}` first and extend existing servers.

- Server entry (`src/server.{py,ts}`) with the transport chosen in Step 2
- One module per tool under `src/tools/` (schema, annotations, handler together); declared output types (Pydantic / Zod)
- `pyproject.toml` or `package.json` pinned to the v2 SDK major (or `<2` if the user must stay on v1)
- Contract tests per tool (`tests/`): schema rejects bad input with `isError`, happy path matches `outputSchema`, auth failure is typed
- README: tool list with annotations, env vars, client config snippets for Claude Code and Codex
