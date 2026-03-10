---
paths:
  - "**/*.swift"
---

# iOS Development Standards

- Use Clean Architecture: Domain (protocols + models), Data (implementations), Presentation (ViewModels + Views)
- MVVM with SwiftUI — or TCA (The Composable Architecture) when state complexity warrants it
- Swift structured concurrency (async/await) — no Combine in new code unless maintaining legacy
- Protocol-based dependency injection via DIContainer or swift-dependencies
- SwiftUI views are pure render functions — no business logic in views
- Actors for shared mutable state
- Testing: XCTest for unit tests, ViewInspector or XCUITest for UI
- SPM for all dependency management — no CocoaPods in new projects
- Minimum deployment target: iOS 16+
