---
globs: "**/*.rs"
---

# Rust Standards — Cure Consulting Group

When editing Rust files, follow these standards:

## Code Style
- Rust 2021 edition minimum — use `rustfmt` formatting (non-negotiable)
- `clippy` clean with `#![warn(clippy::all, clippy::pedantic)]`
- Prefer `&str` over `String` in function parameters — accept borrowed, return owned
- Use `thiserror` for library error types, `anyhow` for application error handling

## Architecture
- Workspace-based monorepo for multi-crate projects
- `lib.rs` exports public API — keep `main.rs` minimal (just setup + run)
- Feature flags for optional functionality — compile-time configuration
- Zero-cost abstractions — generics and traits over dynamic dispatch (`dyn Trait`)

## Error Handling
- Custom error enums with `thiserror::Error` derive
- Use `?` operator — never `.unwrap()` in production code (`.expect("reason")` only for programmer errors)
- `Result<T, E>` for fallible operations — `Option<T>` for optional values
- Map errors at boundaries (`map_err` to add context)

## Concurrency
- `tokio` for async runtime — `async fn` with `.await`
- `Arc<Mutex<T>>` for shared state — prefer message passing with channels
- No `unsafe` without a `// SAFETY:` comment explaining the invariant
- Use `rayon` for data parallelism, `tokio` for I/O concurrency

## Testing
- Unit tests in same file: `#[cfg(test)] mod tests { ... }`
- Integration tests in `tests/` directory
- Use `#[test]` and `#[tokio::test]` for async
- Property-based testing with `proptest` for core logic
- `cargo test` must pass with no warnings
