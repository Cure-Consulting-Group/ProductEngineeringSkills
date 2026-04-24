---
name: android-feature-scaffold
version: "1.0.0"
description: "Scaffold Android features with Clean Architecture, MVI, Jetpack Compose, Hilt, and Kotlin"
when_to_use: "Use when scaffolding a new Android feature module with Clean Architecture, MVI, Compose, and Hilt. NOT for design guidance (use android-design-expert)."
argument-hint: "[feature-name]"
---

# Android Feature Scaffold

Generates complete, production-ready Android feature scaffolding using Clean Architecture, MVI, Jetpack Compose, Hilt, and Kotlin Coroutines/Flow.

## Architecture Layers Generated

```
:feature:[name]/
├── domain/
│   ├── model/          [FeatureName].kt                  ← Domain model (pure Kotlin)
│   └── usecase/        Get[FeatureName]UseCase.kt        ← UseCase(s)
├── data/
│   ├── dto/            [FeatureName]Dto.kt               ← Firestore/API DTO + mapper
│   ├── source/         [FeatureName]DataSource.kt        ← Remote/local data source
│   └── repository/     [FeatureName]RepositoryImpl.kt   ← Repository implementation
├── presentation/
│   ├── [FeatureName]ViewModel.kt                        ← MVI ViewModel
│   ├── [FeatureName]Screen.kt                           ← Compose screen
│   ├── [FeatureName]UiState.kt                          ← Sealed UI state
│   └── components/     [FeatureName]*.kt                ← Extracted composables
└── di/
    └── [FeatureName]Module.kt                           ← Hilt module
```

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Gather Requirements

Ask if not clear:
1. **Feature name** — e.g., "PlayerProfile"
2. **Domain context** — what entity/data does this feature show or manipulate?
3. **Data source** — Firestore? REST API? Local Room? Multiple?
4. **Actions** — what can the user do? (view, create, edit, delete, search?)
5. **Navigation** — entry point(s) and exit point(s)?
6. **Auth** — does this feature require a logged-in user?

## Step 2: Generate All Layers

Generate code following Clean Architecture patterns with full separation between domain, data, and presentation layers. For a full feature scaffold, generate ALL layers before outputting.

## Step 3: MVI State Contract (Always Apply)

Every feature follows this exact state pattern:

```kotlin
// [Feature]UiState.kt
sealed interface [Feature]UiState {
    data object Loading : [Feature]UiState
    data class Success(val data: [Feature]Data) : [Feature]UiState
    data class Error(val message: String) : [Feature]UiState
    data object Empty : [Feature]UiState
}

// [Feature]UiEvent.kt (one-shot events)
sealed interface [Feature]UiEvent {
    data class ShowSnackbar(val message: String) : [Feature]UiEvent
    data class NavigateTo(val route: String) : [Feature]UiEvent
    data object NavigateBack : [Feature]UiEvent
}

// [Feature]UiAction.kt (user intents → ViewModel)
sealed interface [Feature]UiAction {
    data object Refresh : [Feature]UiAction
    data class OnItemClick(val id: String) : [Feature]UiAction
    data object OnBackClick : [Feature]UiAction
}
```

## Step 4: Code Generation Rules

1. **No hardcoded strings** — all UI strings go to `strings.xml`
2. **No magic numbers** — dimensions in `dimens.xml` or Compose tokens
3. **Error handling** — every suspend call wrapped in `runCatching` or `Result`
4. **Loading states** — every async operation emits Loading before result
5. **No business logic in Compose** — all logic in ViewModel or UseCase
6. **Preview annotations** — every Compose screen has `@Preview` (light + dark)
7. **Accessibility** — all interactive elements have `contentDescription`
8. **No direct repo in ViewModel** — always mediated by UseCase(s)

## Output Format

Generate code in this order:
1. Domain model
2. DTO + mapper
3. Repository interface (in domain)
4. Repository implementation (in data)
5. UseCase(s)
6. UiState / UiEvent / UiAction sealed classes
7. ViewModel
8. Compose Screen + components
9. Hilt Module
10. Navigation registration
11. Unit test scaffold (ViewModel + UseCase)

After code generation, output a summary table:
```
| File | Layer | Status |
|------|-------|--------|
| PlayerProfile.kt | Domain | Generated |
| PlayerProfileDto.kt | Data | Generated |
...
```

## Tech Stack Defaults

```yaml
language: Kotlin
ui: Jetpack Compose
architecture: MVI + Clean Architecture
di: Hilt
async: Coroutines + StateFlow
testing: JUnit5 + MockK + Turbine
```

## Code Generation (Required)

You MUST generate actual code files, not just describe patterns. Use the Write tool to create:

1. **Domain layer**: `domain/model/{Feature}.kt`, `domain/usecase/{Feature}UseCase.kt`
2. **Data layer**: `data/dto/{Feature}Dto.kt`, `data/repository/{Feature}RepositoryImpl.kt`, `data/mapper/{Feature}Mapper.kt`
3. **Presentation layer**: `presentation/{feature}/{Feature}ViewModel.kt`, `presentation/{feature}/{Feature}Screen.kt`, `presentation/{feature}/{Feature}Contract.kt` (MVI state/event/effect)
4. **DI module**: `di/{Feature}Module.kt` (Hilt)
5. **Tests**: `test/{feature}/{Feature}ViewModelTest.kt`, `test/{feature}/{Feature}UseCaseTest.kt`

Before generating, use Glob to find existing feature modules and match their package structure and naming conventions.

## Cross-References

- `/database-architect` — for Room schema design and migration strategies when local persistence is needed
- `/testing-strategy` — for test pyramid standards and coverage rules
- `/ci-cd-pipeline` — for Android build and distribution workflows
- `/accessibility-audit` — for Compose accessibility and content description standards
