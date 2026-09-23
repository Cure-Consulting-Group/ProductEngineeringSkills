# Android Feature Scaffold

**Outcome:** a compiling feature module in the project's existing conventions — domain, data,
presentation, DI, navigation entry, and unit tests — following `rules/android.md` (Claude Code loads
it for `*.kt`; elsewhere read it from the plugin). Done when every file in the Step 3 layout exists,
the feature is registered in navigation and DI, and the ViewModel and use-case tests run.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Versions: `grep -hE "compose-bom|hilt|navigation|kotlin|lifecycle|junit|mockk|turbine" gradle/libs.versions.toml 2>/dev/null | head -12 || echo "(no version catalog)"`
- Existing features: `find . -path "*/feature/*" -name "*ViewModel.kt" 2>/dev/null | head -8`

Match the existing features' package structure and naming before applying the defaults below.

## Step 1: Classify

| Request | Output |
|---|---|
| Full feature | All layers (Step 3) |
| Screen + ViewModel only | Presentation layer + contract + tests |
| Data layer only | DTO, mapper, data source, repository + tests |
| Question / review of existing feature | Answer or findings against Step 4 rules — no new files |

## Step 2: Gather Requirements

Ask only what the context doesn't answer: feature name (e.g. `PlayerProfile`); entity and data
source (Firestore, REST, Room, combination); user actions; navigation entry/exit points and
arguments; auth requirement.

## Step 3: File Layout (one layout — use it everywhere)

```
:feature:{name}/src/main/kotlin/.../{name}/
├── domain/
│   ├── model/{Feature}.kt                  pure Kotlin
│   ├── repository/{Feature}Repository.kt   interface
│   └── usecase/Get{Feature}UseCase.kt      one class per use case
├── data/
│   ├── dto/{Feature}Dto.kt
│   ├── mapper/{Feature}Mapper.kt           Dto ↔ domain
│   ├── source/{Feature}RemoteDataSource.kt
│   └── repository/{Feature}RepositoryImpl.kt
├── presentation/
│   ├── {Feature}Contract.kt                UiState + UiAction + UiEvent
│   ├── {Feature}ViewModel.kt
│   ├── {Feature}Screen.kt                  route composable + stateless content
│   └── components/
├── navigation/{Feature}Navigation.kt       @Serializable route + graph builder
└── di/{Feature}Module.kt                   Hilt
:feature:{name}/src/test/kotlin/.../{name}/  {Feature}ViewModelTest.kt, Get{Feature}UseCaseTest.kt
```

Generation order: domain model → repository interface → use case → DTO + mapper → data source →
repository impl → contract → ViewModel → screen → navigation → Hilt module → tests.

## Step 4: Rules With Non-Obvious Reasons

**MVI contract** (in `{Feature}Contract.kt`):
```kotlin
sealed interface {Feature}UiState {
    data object Loading : {Feature}UiState
    data object Empty : {Feature}UiState
    data class Success(val data: {Feature}) : {Feature}UiState
    data class Error(@StringRes val message: Int) : {Feature}UiState
}
sealed interface {Feature}UiAction { data object Refresh : {Feature}UiAction; data class OnItemClick(val id: String) : {Feature}UiAction }
sealed interface {Feature}UiEvent { data class ShowSnackbar(@StringRes val message: Int) : {Feature}UiEvent; data class OpenDetail(val id: String) : {Feature}UiEvent; data object NavigateBack : {Feature}UiEvent }
```
Events carry typed data, never route strings — the screen maps them to navigation calls.

**Cancellation-safe error handling.** Never wrap suspend calls in `runCatching`: it catches
`CancellationException`, so a cancelled scope keeps running and emits stale Error states. Use:
```kotlin
suspend inline fun <T> suspendRunCatching(block: () -> T): Result<T> =
    try { Result.success(block()) }
    catch (e: CancellationException) { throw e }
    catch (e: Exception) { Result.failure(e) }
```

**Type-safe navigation.** Routes are `@Serializable` objects/data classes (Navigation Compose 2.8+:
`composable<{Feature}Route> { … }`, `navController.navigate({Feature}Route(id))`, args via
`backStackEntry.toRoute()` or `SavedStateHandle.toRoute()`). If the app already uses Navigation 3
(`androidx.navigation3`, stable since 1.0.0), make the route a `NavKey` and add an `entry<…>`
instead. No string routes.

**Lifecycle-aware collection.** Screens collect with `collectAsStateWithLifecycle()`; one-shot
events are collected in a `LaunchedEffect` using `repeatOnLifecycle(Lifecycle.State.STARTED)`.
ViewModel exposes `StateFlow` built
with `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), Loading)`.

**Layering.** ViewModels depend on use cases, never repositories. No business logic in
composables. Screen = route composable (gets ViewModel via `hiltViewModel()`) + stateless content
composable that takes state and lambdas — previews and UI tests target the stateless one.

**UI hygiene.** Strings in `strings.xml` (ViewModels emit `@StringRes`, not text); every async
operation emits Loading first; `@Preview` light + dark for each state; `contentDescription` on
meaningful icons.

**Tests.** JUnit 5 + MockK + Turbine + `kotlinx-coroutines-test` (`runTest`, a `MainDispatcher`
extension). Coverage targets come from `testing-strategy`.

## Code/Artifact Generation

Applies when Step 1 is a build request; a question or review gets an answer, not files. Write the
Step 3 files, register the route and Hilt module, then output a table of files by layer. Deliver the
requested feature; don't refactor adjacent modules.

## Cross-References

`database-architect` (Room schema/migrations) · `testing-strategy` (pyramid, coverage) ·
`ci-cd-pipeline` (Android build/distribution) · `accessibility-audit` (Compose semantics) ·
`android-design-expert` (M3 specs). In Claude Code these are `/cure-product-engineering:<name>`;
in Codex `$<name>`.
