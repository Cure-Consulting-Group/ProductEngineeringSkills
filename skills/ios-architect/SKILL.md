---
name: ios-architect
description: "Scaffold iOS features with Swift/SwiftUI, Clean Architecture, MVVM, and structured concurrency"
argument-hint: "[feature-name]"
---

# iOS Architect

Production Swift/SwiftUI architecture. Clean Architecture with Swift Concurrency. Mirrors Android scaffold structure for cross-platform consistency.

## Architecture Options

Default: **Clean Architecture + MVVM + Swift Concurrency**
Alternative: **The Composable Architecture (TCA)** — ask if user specifies TCA

```
Presentation Layer  →  SwiftUI Views + ViewModels (@Observable / ObservableObject)
Domain Layer        →  Use Cases + Repository Protocols (pure Swift, no frameworks)
Data Layer          →  Repository Impls + Data Sources (URLSession, Firebase, CoreData)
DI Layer            →  DIContainer or swift-dependencies (TCA)
```

## Feature Scaffold Structure

```
Feature/[FeatureName]/
├── Domain/
│   ├── Models/         [FeatureName].swift           ← Pure Swift value types
│   ├── Repositories/   [FeatureName]Repository.swift ← Protocol only
│   └── UseCases/       [Action][FeatureName]UseCase.swift
├── Data/
│   ├── DTOs/           [FeatureName]DTO.swift        ← Codable + mapper
│   ├── DataSources/    [FeatureName]RemoteDataSource.swift
│   └── Repositories/   [FeatureName]RepositoryImpl.swift
├── Presentation/
│   ├── [FeatureName]ViewModel.swift                 ← @Observable or @MainActor
│   ├── [FeatureName]View.swift                      ← SwiftUI root view
│   ├── [FeatureName]State.swift                     ← State/action enums
│   └── Components/     [Component]View.swift
└── DI/
    └── [FeatureName]Module.swift
```

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify Request

| Request | Action |
|---------|--------|
| Full feature scaffold | Generate all layers |
| SwiftUI view + ViewModel | Generate presentation layer |
| Data layer + networking | Generate data layer |
| StoreKit 2 subscriptions | Generate StoreKit integration |
| Firebase iOS integration | Generate Firebase data layer |
| TCA architecture | Generate TCA pattern |
| Testing scaffold | Generate XCTest files |

## Step 2: Gather Context

1. **Feature name** — e.g., "PlayerProfile"
2. **Architecture preference** — Clean + MVVM (default) or TCA?
3. **Data source** — REST API / Firebase / Core Data / SwiftData / combined?
4. **iOS deployment target** — iOS 17+ recommended (enables @Observable, SwiftData)
5. **Auth requirement** — Firebase Auth / Sign in with Apple / both?
6. **Existing patterns** — any established conventions in the codebase?

## Step 3: Core Swift Patterns (Always Apply)

### State Management Selection
```
iOS 17+: @Observable macro (preferred)
iOS 16 and below: ObservableObject + @Published
TCA: Store<State, Action> + Reducer
```

### Concurrency Rules
- All network/IO calls: `async throws` — never DispatchQueue or completion handlers
- UI updates: `@MainActor` — annotate ViewModels
- Shared mutable state: `actor` — never raw class with locks
- Structured concurrency: `async let` for parallel work, `TaskGroup` for dynamic parallelism
- Cancellation: `Task { }` stored as property, cancel in `deinit` / `.onDisappear`

### Error Handling Pattern
```swift
enum [Feature]Error: LocalizedError {
    case notFound(id: String)
    case networkUnavailable
    case unauthorized
    case unknown(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .notFound(let id): return "Item \(id) not found."
        case .networkUnavailable: return "No internet connection."
        case .unauthorized: return "You don't have access."
        case .unknown: return "An unexpected error occurred."
        }
    }
}
```

### Repository Protocol Pattern
```swift
protocol [Feature]Repository {
    func get(id: String) async throws -> [Feature]
    func observe(id: String) -> AsyncThrowingStream<[Feature], Error>
    func update(_ item: [Feature]) async throws
}
```

## Step 4: Code Generation Order

1. Domain models (struct, enum)
2. Repository protocol
3. Use case(s)
4. DTO + Codable + mapper
5. Data source (networking or Firebase)
6. Repository implementation
7. State / Action enums
8. ViewModel (`@Observable @MainActor`)
9. SwiftUI root view
10. Subcomponent views
11. DI wiring
12. XCTest scaffold

## Code Generation (Required)

You MUST generate actual Swift files using the Write tool:

1. **Domain**: `Domain/Models/{Feature}.swift`, `Domain/UseCases/{Feature}UseCase.swift`, `Domain/Repositories/{Feature}RepositoryProtocol.swift`
2. **Data**: `Data/DTOs/{Feature}DTO.swift`, `Data/Repositories/{Feature}Repository.swift`, `Data/Mappers/{Feature}Mapper.swift`
3. **Presentation**: `Presentation/{Feature}/{Feature}ViewModel.swift`, `Presentation/{Feature}/{Feature}View.swift`
4. **DI**: `DI/{Feature}Assembly.swift`
5. **Tests**: `Tests/{Feature}/{Feature}ViewModelTests.swift`, `Tests/{Feature}/{Feature}UseCaseTests.swift`

Before generating, use Glob to find existing feature modules (`**/*ViewModel.swift`, `**/*UseCase.swift`) and match conventions.

## Cross-References

- `/database-architect` — for CoreData/SwiftData schema design and migrations
- `/testing-strategy` — for XCTest standards and coverage expectations
- `/ci-cd-pipeline` — for iOS Fastlane and TestFlight workflows
- `/accessibility-audit` — for SwiftUI accessibility modifiers and VoiceOver compliance

## Tech Stack Defaults

```yaml
language: Swift 5.10+
ui: SwiftUI (UIKit interop where needed)
state: @Observable (iOS 17+) or ObservableObject
concurrency: Swift Concurrency (async/await, Actor, AsyncStream)
networking: URLSession with async/await
serialization: Codable (JSONDecoder with .convertFromSnakeCase)
di: Manual DIContainer or swift-dependencies
firebase: FirebaseFirestore, FirebaseAuth (Swift SDK)
payments: StoreKit 2
persistence: SwiftData (iOS 17+) or Core Data
testing: XCTest + Swift Testing framework (iOS 17+)
ui_testing: XCUITest + snapshot testing (swift-snapshot-testing)
package_manager: Swift Package Manager
linting: SwiftLint
```
