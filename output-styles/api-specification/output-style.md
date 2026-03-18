---
name: api-specification
description: Output style for API documentation — OpenAPI endpoints, request/response schemas, error formats, and authentication flows.
---

# API Specification Output Style

When generating API documentation, follow this format:

## Structure
1. **Overview** — API name, base URL, versioning scheme, auth method
2. **Authentication** — How to authenticate (Bearer token, API key, OAuth flow)
3. **Endpoints** — Grouped by resource, each with method, path, description
4. **Schemas** — Request/response JSON schemas with types and constraints
5. **Error Responses** — Standard error format with all possible codes
6. **Rate Limits** — Limits per endpoint tier

## Endpoint Format

For each endpoint:
```
### `METHOD /path/:param`

**Description:** What it does

**Auth:** Required / Public

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|

**Request Body:**
```json
{ "field": "type — description" }
```

**Response 200:**
```json
{ "field": "type — description" }
```

**Error Responses:**
| Status | Code | Description |
|--------|------|-------------|
```

## Rules
- Always include example request/response with realistic data
- Error responses use consistent format: `{ "error": { "code": "string", "message": "string", "details": {} } }`
- Pagination format: `{ "data": [], "cursor": "string", "hasMore": boolean }`
- Timestamps in ISO 8601 format
- IDs as strings (UUIDs)
