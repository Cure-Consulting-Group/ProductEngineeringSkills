---
paths:
  - "**/*.kt"
  - "**/*.java"
---

# Android Development Standards

- Use Clean Architecture: domain (pure Kotlin), data (DTOs + repos), presentation (ViewModels + Compose)
- MVI pattern: sealed UiState, UiEvent, and side effects via Channels
- Jetpack Compose for all UI — no XML layouts
- Hilt for dependency injection — annotate modules, never manual DI
- Coroutines + Flow for async — no callbacks, no RxJava in new code
- DTOs map to domain models at the repository boundary — never expose DTOs to the domain layer
- Use cases are single-responsibility classes with `operator fun invoke()`
- Compose screens receive state and emit events — no business logic in composables
- Navigation via sealed Route classes
- Testing: JUnit5 + MockK for unit tests, Compose testing for UI
