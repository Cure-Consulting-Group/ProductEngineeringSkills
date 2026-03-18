---
globs: "**/*.go"
---

# Go Standards — Cure Consulting Group

When editing Go files, follow these standards:

## Code Style
- Go 1.22+ — use modern features (`range over int`, `log/slog`, iterators)
- `gofmt` / `goimports` formatting — non-negotiable
- Short variable names in small scopes (`r` for reader, `ctx` for context) — descriptive names in larger scopes
- Exported names are PascalCase, unexported are camelCase

## Architecture
- Interface-based design — define interfaces where they're consumed, not where they're implemented
- Accept interfaces, return structs
- Package by domain, not by layer (`users/`, `orders/`, not `models/`, `handlers/`)
- `internal/` for packages not exposed outside the module
- `cmd/` for entrypoints, `pkg/` only if truly reusable across projects

## Error Handling
- Always check errors — `if err != nil { return fmt.Errorf("operation failed: %w", err) }`
- Wrap errors with `%w` for `errors.Is` / `errors.As` compatibility
- Use sentinel errors for expected conditions (`var ErrNotFound = errors.New("not found")`)
- Custom error types implement `error` interface — add context fields
- Never panic in library code — panic only in `main` for unrecoverable startup failures

## Concurrency
- Pass `context.Context` as first parameter to all functions that do I/O
- Use `errgroup.Group` for concurrent operations with error collection
- Channels for communication, mutexes for state — prefer channels
- Never start goroutines without a way to stop them (context cancellation, done channels)

## Testing
- Table-driven tests with `t.Run` subtests
- Test file in same package: `users_test.go`
- Use `testify/assert` or standard library — no heavy test frameworks
- `httptest.NewServer` for HTTP testing, interfaces for dependency mocking
- `go test -race` in CI — always
- Minimum 80% coverage on new code
