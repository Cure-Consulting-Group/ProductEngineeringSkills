---
paths:
  - "**/*.rs"
  - "**/Cargo.toml"
---

# Rust Standards — Cure Consulting Group

When editing Rust files, follow these standards:

## Code Style
- `edition = "2024"` for new crates, with `rust-version` (MSRV) set in `Cargo.toml`; `rustfmt` formatting is non-negotiable
- Lints in the `[lints]` table of `Cargo.toml` (`clippy::all`, `clippy::pedantic` at warn), not crate-level attributes; CI runs `cargo clippy -- -D warnings`
- Prefer `&str` over `String` in function parameters — accept borrowed, return owned
- `thiserror` for library error types, `anyhow` for application error handling

## Edition 2024 Habits
- Inside `unsafe fn`, wrap each unsafe operation in an `unsafe {}` block (`unsafe_op_in_unsafe_fn` warns by default)
- `unsafe extern "C" { … }` blocks and `#[unsafe(no_mangle)]` / `#[unsafe(export_name)]` attributes
- `gen` is a reserved keyword; `impl Trait` in return position captures all in-scope lifetimes — use `use<..>` to narrow

## Architecture
- Cargo workspace for multi-crate projects; set `resolver = "3"` in a virtual workspace root (edition 2024 packages default to it)
- `lib.rs` exports the public API — keep `main.rs` minimal (setup + run)
- Cargo features for optional functionality
- Generics and traits over dynamic dispatch (`dyn Trait`) unless binary size or compile time says otherwise

## Error Handling
- Custom error enums with `#[derive(thiserror::Error)]`
- Use `?` — never `.unwrap()` in production code (`.expect("reason")` only for programmer errors)
- `Result<T, E>` for fallible operations, `Option<T>` for optional values
- Map errors at boundaries (`map_err` / `.context()` to add context)

## Concurrency
- `tokio` for async I/O; `rayon` for CPU-bound data parallelism
- Message passing (channels) by default; `Arc<Mutex<T>>` when state is genuinely shared — `std::sync::Mutex` unless the guard is held across `.await`, then `tokio::sync::Mutex`
- No `unsafe` without a `// SAFETY:` comment explaining the invariant

## Testing
- Unit tests in the same file: `#[cfg(test)] mod tests { ... }`; integration tests in `tests/`
- `#[test]`, and `#[tokio::test]` for async
- `proptest` for core logic
- `cargo test` passes with no warnings

Verified 2026-10-24: Rust 2024 is the newest edition (stable since 1.85); Rust 1.99.1 released 2026-10-15 (blog.rust-lang.org).
