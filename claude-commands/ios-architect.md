# iOS Architect

**Outcome:** a feature that compiles cleanly under the Swift 6 language mode (complete concurrency
checking, zero warnings), in the project's existing conventions — domain, data, presentation, DI,
and tests. Done when every file in the Step 3 layout exists, the feature is wired into the DI
container and navigation, and the view-model and use-case tests pass. Mirrors
`android-feature-scaffold` so Cure's two mobile codebases read alike.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Toolchain / settings: !`grep -rhoE "SWIFT_VERSION = [0-9.]+|IPHONEOS_DEPLOYMENT_TARGET = [0-9.]+|SWIFT_DEFAULT_ACTOR_ISOLATION = [A-Za-z]+|SWIFT_STRICT_CONCURRENCY = [a-z]+" --include=project.pbxproj . 2>/dev/null | sort | uniq -c | head -8 || echo "(no Xcode project)"`
- Packages: !`grep -hoE 'url: "[^"]+"|swift-tools-version:[0-9.]+|defaultIsolation\([^)]*\)' Package.swift 2>/dev/null | head -8 || echo "(no Package.swift)"`
- Existing features: !`find . -name "*ViewModel.swift" -not -path "*/.build/*" 2>/dev/null | head -6`

Match existing features' structure and naming before applying the defaults below.

## Step 1: Classify

| Request | Output |
|---|---|
| Full feature | All layers (Step 3) |
| SwiftUI view + view model | Presentation layer + tests |
| Data layer / networking / Firebase | DTOs, data source, repository + tests |
| StoreKit 2 purchases / subscriptions | Store service per Step 4 + tests with a `.storekit` config |
| Project already uses TCA | Follow its reducer/`@Dependency` conventions; same layering below the store |
| Question / review | Answer or findings against Step 4 — no new files |

Don't introduce TCA into a non-TCA codebase; MVVM is the Cure default.

## Step 2: Gather Context

Ask only what the context doesn't answer: feature name; data source (REST, Firebase, SwiftData,
Core Data); deployment target (Cure floor: iOS 17 — needed for `@Observable` and SwiftData; confirm
against the client's device analytics); auth (Firebase Auth, Sign in with Apple); any purchase flow.

## Step 3: File Layout (one naming scheme — use it everywhere)

```
Features/{Feature}/
├── Domain/
│   ├── Models/{Feature}.swift                   value types, Sendable
│   ├── Repositories/{Feature}Repository.swift   protocol
│   └── UseCases/Get{Feature}UseCase.swift
├── Data/
│   ├── DTOs/{Feature}DTO.swift                  Codable
│   ├── Mappers/{Feature}Mapper.swift            DTO ↔ domain
│   ├── DataSources/{Feature}RemoteDataSource.swift
│   └── Repositories/{Feature}RepositoryImpl.swift
├── Presentation/
│   ├── {Feature}ViewModel.swift                 @Observable, main-actor isolated
│   ├── {Feature}View.swift
│   └── Components/
└── DI/{Feature}Module.swift                     registers the feature in the app container
Tests/{Feature}Tests/  {Feature}ViewModelTests.swift, Get{Feature}UseCaseTests.swift
```

Generation order: model → repository protocol → use case → DTO + mapper → data source → repository
impl → view model → view → DI → tests.

## Step 4: Rules With Non-Obvious Reasons

**Concurrency (Swift 6 language mode).** Swift 6.2 added default actor isolation (SE-0466): new
Xcode 26+ app targets default to `MainActor`, so unannotated types are main-actor isolated. Check
the setting in the context above and write code that is correct under it:
- UI and view models: main-actor (implicit under the default, explicit `@MainActor` otherwise).
- Data sources, repositories, mappers: mark `nonisolated` (or keep in a module/package without
  MainActor default) so decoding and I/O don't run on the main actor. Use `@concurrent` for
  functions that must leave the caller's actor.
- Domain models and DTOs are `Sendable` value types; shared mutable state lives in an `actor`.
- Core Data / codegen classes inherit MainActor under the default — access `NSManagedObject`s only
  inside their context's `perform`.
- No `DispatchQueue`, completion handlers, or `@unchecked Sendable` to silence the checker.

**Task lifetime.** Start view work with SwiftUI `.task { await viewModel.load() }` (or
`.task(id:)`), which cancels automatically when the view disappears. Don't store a `Task` and
cancel it in `deinit`: a task whose closure captures `self` keeps the view model alive, so `deinit`
never runs, and a main-actor class's `deinit` is nonisolated unless declared `isolated deinit`.

**Observation and DI.** `@Observable` view models, held with `@State` in the owning view and passed
down or via `@Environment(Type.self)`. Dependencies are protocol-typed and injected through the
initializer from a composition root; no singletons reached from views.

**Errors.** Each feature defines a `LocalizedError` enum (`notFound`, `networkUnavailable`,
`unauthorized`, `unknown(underlying:)`); user-facing text comes from the String Catalog. Map
transport errors at the repository boundary; view models never see `URLError`.

**Repository shape.** `get(id:) async throws -> Model`, `observe(id:) -> AsyncThrowingStream<Model,
Error>` (finish the stream and remove Firebase listeners in `onTermination`), `update(_:) async throws`.

**StoreKit 2.** One `@MainActor` store service. Start a `Transaction.updates` listener at app
launch (missed renewals and Ask-to-Buy approvals arrive there); `finish()` every verified
transaction; derive entitlements from `Transaction.currentEntitlements`, not local flags. Validate
server-side with App Store Server Notifications V2 when the backend grants access. Test with a
`.storekit` configuration file.

**Tests.** Swift Testing (`@Test`, `#expect`) for unit tests; XCTest for UI tests. Coverage targets
come from `testing-strategy`.

## Code/Artifact Generation

Applies when Step 1 is a build request; a question or review gets an answer, not files. Write the
Step 3 files, wire DI and navigation, then list files by layer. Deliver the requested feature;
don't refactor adjacent features.

## Defaults (verified 2026-09-23)

Swift 6 language mode on the current Xcode toolchain (Swift 6.4 released 2026-09-15, swift.org) ·
SwiftUI (UIKit via representables where needed) · `@Observable` · URLSession async/await ·
`Codable` · SwiftData (iOS 17+) or Core Data · Firebase Apple SDK via SPM · StoreKit 2 ·
Swift Testing + XCTest UI · SwiftLint.

## Cross-References

`database-architect` (SwiftData/Core Data schema) · `testing-strategy` · `ci-cd-pipeline` (Fastlane,
TestFlight) · `accessibility-audit` (VoiceOver) · `ios-design-expert` (HIG specs).
