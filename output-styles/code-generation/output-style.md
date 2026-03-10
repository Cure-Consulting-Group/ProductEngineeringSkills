# Code Generation Style

When generating code (scaffolds, implementations, configurations, migrations):

## Formatting Rules

- Lead with a file tree showing all files that will be created/modified
- Present files in dependency order (models → repositories → use cases → ViewModels → UI)
- Use complete, runnable code — no `// TODO` placeholders unless explicitly flagged
- Include imports in every file
- Add brief inline comments only where logic is non-obvious
- Use code fences with language identifier: ```kotlin, ```swift, ```typescript, ```json

## File Presentation

```
Files to create:
├── domain/model/Feature.kt          (data model)
├── domain/usecase/GetFeatureUseCase.kt (business logic)
├── data/dto/FeatureDto.kt            (API/DB mapping)
├── data/repository/FeatureRepoImpl.kt (data access)
├── presentation/FeatureViewModel.kt   (state management)
└── presentation/FeatureScreen.kt      (UI)
```

Then present each file with its full path as a header.

## Code Quality

- Follow platform conventions (Kotlin naming, Swift style, TypeScript strict)
- Every class has a single responsibility
- Public APIs are minimal — expose only what's needed
- Error handling is explicit — no swallowed exceptions
- Tests accompany implementations when the skill specifies it

## After Code

- Summarize what was generated (file count, pattern used)
- List integration steps (wire up DI, add routes, update navigation)
- Note any manual steps required (API keys, environment config)
