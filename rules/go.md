---
paths:
  - "**/*.go"
  - "**/go.mod"
---

# Go Standards — Cure Consulting Group

When editing Go files, follow these standards:

## Code Style
- Go 1.26+ (1.27 is current; only the two newest releases get security fixes) — set `go` and `toolchain` in `go.mod`
- Use the modern stdlib: `for i := range n`, range-over-func iterators with `slices`/`maps` helpers, `log/slog`, `sync.WaitGroup.Go`
- Dev tools via `tool` directives in `go.mod` (`go get -tool`), not a `tools.go` file
- `gofmt` / `goimports` formatting — non-negotiable; `go vet` and `golangci-lint` clean
- Short variable names in small scopes (`r`, `ctx`) — descriptive names in larger scopes
- Exported names are PascalCase, unexported are camelCase

## Architecture
- Define interfaces where they're consumed, not where they're implemented
- Accept interfaces, return structs
- Package by domain, not by layer (`users/`, `orders/`, not `models/`, `handlers/`)
- `internal/` for packages not exposed outside the module
- `cmd/` for entrypoints, `pkg/` only if truly reusable across projects

## Error Handling
- Always check errors — `if err != nil { return fmt.Errorf("load user %s: %w", id, err) }`
- Wrap with `%w` for `errors.Is` / `errors.As`
- Sentinel errors for expected conditions (`var ErrNotFound = errors.New("not found")`)
- Custom error types implement `error` and carry context fields
- Never panic in library code — panic only in `main` for unrecoverable startup failures

## Concurrency
- Pass `context.Context` as the first parameter to every function that does I/O
- `errgroup.Group` for concurrent work that can fail; `wg.Go(fn)` when it can't
- Pick the primitive by the job: a mutex guards shared state; a channel hands off ownership or signals events. Don't force either
- Never start a goroutine without a way to stop it (context cancellation or a done channel)

## Testing
- Table-driven tests with `t.Run` subtests; `t.Context()` for test-scoped contexts, `b.Loop()` in benchmarks
- Test file in the same package: `users_test.go`
- Standard library or `testify` — no heavy test frameworks; `testing/synctest` for time- and goroutine-dependent code
- `httptest.NewServer` for HTTP tests, consumer-side interfaces for mocks
- `go test -race` in CI — always
- 80% diff coverage on new code (gate defined by `testing-strategy`)

Verified 2026-10-24: go1.27 released 2026-08-19, go1.26 2026-02-10; go1.25 is unsupported (go.dev/doc/devel/release).
