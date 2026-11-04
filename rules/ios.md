---
paths:
  - "**/*.swift"
---

# iOS Development Standards

- Swift 6 language mode, complete strict concurrency — never `@unchecked Sendable`, `DispatchQueue` or completion handlers to quiet the checker
- Xcode 26+ app targets default to MainActor isolation (SE-0466): UI and view models stay main-actor; repositories, data sources and mappers are `nonisolated`; `@concurrent` for work that must leave the caller's actor
- Domain models and DTOs are `Sendable` value types; shared mutable state lives in an `actor`
- Clean Architecture: Domain (protocols + models), Data (implementations), Presentation (view models + views)
- `@Observable` view models held with `@State` in the owning view — no `ObservableObject`/`@Published` in new code; TCA only when state complexity warrants it
- async/await and `AsyncSequence` — no Combine in new code unless maintaining legacy
- Start view work in `.task {}` / `.task(id:)` so it cancels with the view; don't store a `Task` and cancel it in `deinit`
- Protocol-typed dependencies injected through initializers from a composition root (or swift-dependencies) — no singletons reached from views
- SwiftUI views are render functions — no business logic in views
- Testing: Swift Testing (`@Test`, `#expect`) for unit tests; XCTest/XCUITest for UI tests
- SPM for all dependencies — no CocoaPods in new projects
- Minimum deployment target: iOS 17 (required for `@Observable` and SwiftData); confirm against the client's device analytics

Verified 2026-10-24: Swift 6.4 is current (swift.org, released 2026-09-15). Matches `ios-architect`.
