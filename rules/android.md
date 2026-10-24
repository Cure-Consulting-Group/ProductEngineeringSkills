---
paths:
  - "**/*.kt"
  - "**/*.kts"
  - "**/*.java"
  - "**/libs.versions.toml"
---

# Android Development Standards

- Clean Architecture: domain (pure Kotlin), data (DTOs + repositories), presentation (ViewModels + Compose)
- MVI: immutable `UiState` exposed as `StateFlow` (`stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), Loading)`); one-shot effects via a `Channel`, collected under `repeatOnLifecycle(STARTED)`
- Jetpack Compose for all UI — no XML layouts; screens collect with `collectAsStateWithLifecycle()`
- Screen = route composable (gets the ViewModel via `hiltViewModel()`) + stateless content composable that takes state and lambdas; no business logic in composables
- Hilt for dependency injection — no manual DI, no service locators
- Coroutines + Flow for async — no callbacks, no RxJava in new code
- DTOs map to domain models at the repository boundary — never expose DTOs to the domain layer
- Use cases are single-responsibility classes with `operator fun invoke()`; ViewModels depend on use cases, never repositories
- Type-safe navigation: routes are `@Serializable` objects/data classes (Navigation Compose 2.8+, args via `toRoute()`); in Navigation 3 apps, routes are `NavKey`s. No string routes
- Build: Kotlin 2.x (K2 compiler) with the Compose compiler Gradle plugin; KSP, not kapt (kapt is in maintenance mode); versions in `gradle/libs.versions.toml`; Compose via the BOM
- Testing: JUnit 5 + MockK + Turbine + `kotlinx-coroutines-test`; Compose UI tests target the stateless content composable

Verified 2026-10-24: Kotlin 2.4.21 is current (kotlinlang.org/docs/releases, 2026-10-08); kapt maintenance mode per developer.android.com/build/migrate-to-ksp. Matches `android-feature-scaffold`.
