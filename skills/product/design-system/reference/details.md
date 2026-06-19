# design-system: detailed reference

> Reference material for the `design-system` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Component Library Per Platform

## Step 4: Component Library Per Platform

### Android — Jetpack Compose

```kotlin
// design-system/src/main/kotlin/com/example/ds/theme/Theme.kt
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content
    )
}

// design-system/src/main/kotlin/com/example/ds/components/Button.kt
@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    loading: Boolean = false,
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(48.dp),  // minimum touch target
        enabled = enabled && !loading,
        shape = MaterialTheme.shapes.medium,
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary,
            contentColor = MaterialTheme.colorScheme.onPrimary,
        ),
    ) {
        if (loading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                color = MaterialTheme.colorScheme.onPrimary,
                strokeWidth = 2.dp,
            )
        } else {
            Text(text = text, style = MaterialTheme.typography.labelLarge)
        }
    }
}

// Component structure:
// design-system/
//   src/main/kotlin/com/example/ds/
//     theme/        — Theme.kt, Color.kt, Typography.kt, Shape.kt
//     tokens/       — Generated token values from Style Dictionary
//     components/   — Button, Card, TextField, Dialog, etc.
//     icons/        — Icon set (Material Icons extended or custom)
```

### iOS — SwiftUI

```swift
// DesignSystem/Sources/Theme/AppTheme.swift
public struct AppTheme {
    public let colors: AppColors
    public let typography: AppTypography
    public let spacing: AppSpacing

    public static let light = AppTheme(
        colors: .light,
        typography: .default,
        spacing: .default
    )

    public static let dark = AppTheme(
        colors: .dark,
        typography: .default,
        spacing: .default
    )
}

// DesignSystem/Sources/Components/PrimaryButton.swift
public struct PrimaryButton: View {
    let title: String
    let action: () -> Void
    var isLoading: Bool = false
    var isEnabled: Bool = true

    @Environment(\.appTheme) private var theme

    public var body: some View {
        Button(action: action) {
            Group {
                if isLoading {
                    ProgressView()
                        .tint(theme.colors.onPrimary)
                } else {
                    Text(title)
                        .font(theme.typography.labelLarge)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 48)  // minimum touch target
        }
        .buttonStyle(.borderedProminent)
        .tint(theme.colors.primary)
        .disabled(!isEnabled || isLoading)
        .accessibilityLabel(title)
        .accessibilityHint(isLoading ? "Loading" : "")
    }
}

// Package structure:
// DesignSystem/
//   Sources/
//     Theme/        — AppTheme, AppColors, AppTypography, AppSpacing
//     Tokens/       — Generated token values from Style Dictionary
//     Components/   — Button, Card, TextField, etc.
//     Modifiers/    — Custom ViewModifiers (shadow, shimmer, etc.)
//   Tests/          — Snapshot tests for components
```

### Web — React + Tailwind

```typescript
// design-system/src/theme/tailwind-tokens.ts
// Generated from Style Dictionary — do not edit manually
export const tokens = {
  colors: {
    primary: {
      DEFAULT: 'var(--color-primary)',
      foreground: 'var(--color-on-primary)',
    },
    secondary: {
      DEFAULT: 'var(--color-secondary)',
      foreground: 'var(--color-on-secondary)',
    },
    surface: {
      DEFAULT: 'var(--color-surface)',
      foreground: 'var(--color-on-surface)',
    },
    destructive: {
      DEFAULT: 'var(--color-error)',
      foreground: 'var(--color-on-error)',
    },
  },
} as const;

// design-system/src/components/button.tsx
// Following shadcn/Radix patterns — composable, accessible by default
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "../utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium " +
  "ring-offset-background transition-colors focus-visible:outline-none " +
  "focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none " +
  "disabled:opacity-50",
  {
    variants: {
      variant: {
        primary:     "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary:   "bg-secondary text-secondary-foreground hover:bg-secondary/90",
        outline:     "border border-input bg-background hover:bg-accent",
        ghost:       "hover:bg-accent hover:text-accent-foreground",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        sm: "h-9 px-3",
        md: "h-10 px-4 py-2",
        lg: "h-12 px-8 text-base",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

export function Button({
  className, variant, size, asChild, loading, children, disabled, ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Spinner className="mr-2 h-4 w-4" /> : null}
      {children}
    </Comp>
  );
}

// Package structure:
// design-system/
//   src/
//     theme/        — tokens, CSS custom properties, Tailwind config
//     components/   — Button, Card, Input, Dialog, etc. (Radix primitives)
//     utils/        — cn(), token helpers
//   stories/        — Storybook stories for each component
```
