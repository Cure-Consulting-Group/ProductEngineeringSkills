---
name: i18n
description: "Implement internationalization and localization — string extraction, RTL support, locale-aware formatting, translation workflows, and platform i18n patterns"
argument-hint: "[project-or-locale]"
---

# Internationalization & Localization

Implements production-grade i18n/l10n across Android, iOS, and web. Every output enforces strict string externalization, platform-native formatting, RTL correctness, and CI-validated translation completeness. No hardcoded user-facing strings — ever.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Core Principle: Localization is Not an Afterthought

```
Day 1 decision    →  Externalize every user-facing string from the start
Concatenation     →  Never concatenate translated strings; use parameterized templates
Formatting        →  Always use platform formatters for dates, numbers, currency
Layout            →  Design for 40% text expansion and RTL from the beginning
```

**Hard rules:**
- Zero hardcoded user-facing strings in source code — enforced by lint rules
- Never concatenate translated strings (e.g., `greeting + name`) — use ICU MessageFormat or platform equivalents
- Never format dates, numbers, or currency manually — always use `Locale`-aware platform formatters
- All string keys follow `feature.screen.element` naming convention
- Pluralization uses ICU MessageFormat rules — never `if count == 1` branches
- Translation files are source-controlled and validated in CI
- RTL support is not optional for any app targeting Arabic, Hebrew, Farsi, or Urdu locales

## Step 1: Classify the i18n Need

| Request | Primary Output | Action |
|---------|---------------|--------|
| Greenfield i18n setup | Full i18n architecture + string extraction plan | Scaffold i18n layer |
| Add new locale | Translation file templates + locale routing | Add locale |
| RTL support | Layout mirroring rules + bidirectional text handling | Implement RTL |
| Translation workflow | Export/import pipeline + CI validation | Design workflow |
| i18n audit | Hardcoded string report + compliance gaps | Audit codebase |
| Locale-aware formatting | Date/number/currency formatter setup | Configure formatters |

## Step 2: Gather Context

Before generating, confirm:
1. **Platforms** — Android, iOS, web, or all three?
2. **Target locales** — which languages and regions? (e.g., en-US, es-MX, ar-SA, ja-JP)
3. **RTL requirement** — any RTL locales in scope?
4. **Current state** — greenfield or existing app with hardcoded strings?
5. **Content volume** — how many strings? (<100 small, 100-1000 medium, >1000 large)
6. **Translation provider** — in-house, agency, crowdsourced, or AI-assisted?
7. **Dynamic content** — any server-driven strings (feature flags, Remote Config)?
8. **Accessibility** — VoiceOver/TalkBack locale requirements?

## Step 3: String Management Architecture

### Source of Truth by Platform

**Android:**
```
res/values/strings.xml              ← Default (English)
res/values-es/strings.xml           ← Spanish
res/values-ar/strings.xml           ← Arabic
res/values-ja/strings.xml           ← Japanese
res/values-es-rMX/strings.xml      ← Spanish (Mexico) — region-specific
```

**iOS:**
```
Localizable.xcstrings               ← String Catalog (Xcode 15+, preferred)
  OR
en.lproj/Localizable.strings        ← Legacy format
es.lproj/Localizable.strings
ar.lproj/Localizable.strings
```

**Web (Next.js):**
```
messages/en.json                     ← next-intl JSON files
messages/es.json
messages/ar.json
middleware.ts                        ← Locale detection + routing
i18n.ts                              ← Configuration
```

### Key Naming Convention

All string keys use dot-separated hierarchy: `feature.screen.element`

```
# Good
auth.login.title = "Sign In"
auth.login.email_placeholder = "Email address"
auth.login.submit_button = "Sign In"
auth.login.error.invalid_credentials = "Invalid email or password"
profile.settings.language_label = "Language"
orders.detail.status.shipped = "Shipped"

# Bad
login_title                          ← No feature namespace
btnSignIn                            ← camelCase, no hierarchy
error1                               ← Meaningless key
```

### Pluralization Rules

Use ICU MessageFormat for all plurals — never hand-roll plural logic.

**Android (strings.xml):**
```xml
<plurals name="orders.count">
    <item quantity="zero">No orders</item>
    <item quantity="one">%d order</item>
    <item quantity="other">%d orders</item>
</plurals>
```

**iOS (String Catalog):**
```
"orders.count" = "%lld order(s)";
  ← Xcode String Catalogs handle plural variants automatically per locale
```

**Web (ICU MessageFormat):**
```json
{
  "orders.count": "{count, plural, =0 {No orders} one {# order} other {# orders}}"
}
```

### String Interpolation Rules

- Never concatenate: `"Hello, " + name` is WRONG
- Always parameterize: `"Hello, {name}"` is correct
- Parameter order may differ across locales — named parameters preferred over positional
- Android: use `%1$s`, `%2$d` positional format specifiers
- iOS: use String Catalog automatic parameter extraction
- Web: use ICU `{name}` named parameters with next-intl

### Hardcoded String Detection

Configure lint rules to catch violations:
- **Android:** custom Lint check or detekt rule flagging `android:text="..."` in XML and string literals in `Text()` composables
- **iOS:** SwiftLint custom rule flagging raw string literals in SwiftUI `Text()` views
- **Web:** ESLint plugin (eslint-plugin-i18next) flagging untranslated JSX text content

## Step 4: Platform-Specific Implementation

### Android

```kotlin
// Compose — always use stringResource()
Text(text = stringResource(R.string.auth_login_title))
Text(text = pluralStringResource(R.plurals.orders_count, count, count))

// ViewModel — inject StringProvider interface (domain layer stays platform-free)
interface StringProvider {
    fun getString(@StringRes resId: Int): String
    fun getQuantityString(@PluralsRes resId: Int, quantity: Int, vararg args: Any): String
}

// Locale change — Compose recomposes automatically via LocalConfiguration
// For programmatic locale change:
val locale = Locale("es", "MX")
AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(locale.toLanguageTag()))
```

### iOS

```swift
// SwiftUI — String Catalogs handle localization automatically
Text("auth.login.title")  // Looked up in Localizable.xcstrings

// Programmatic string lookup
let message = String(localized: "orders.count \(count)")

// Locale override for previews
Text("auth.login.title")
    .environment(\.locale, Locale(identifier: "ar-SA"))
```

### Web (Next.js + next-intl)

```typescript
// middleware.ts — locale routing
import createMiddleware from 'next-intl/middleware';
export default createMiddleware({
  locales: ['en', 'es', 'ar', 'ja'],
  defaultLocale: 'en',
  localePrefix: 'always'  // /en/about, /es/about
});

// Server Component
import { getTranslations } from 'next-intl/server';
export default async function LoginPage() {
  const t = await getTranslations('auth.login');
  return <h1>{t('title')}</h1>;
}

// Client Component
'use client';
import { useTranslations } from 'next-intl';
export function LoginForm() {
  const t = useTranslations('auth.login');
  return <button>{t('submit_button')}</button>;
}
```

### Firebase Remote Config for Dynamic Strings

- Use Remote Config for A/B testing copy, promotional banners, and feature announcements
- Key convention: `i18n_{locale}_{feature}_{key}` (e.g., `i18n_en_promo_banner_text`)
- Always provide fallback defaults in the local string files
- Cache Remote Config strings locally — never block UI on network fetch

## Step 5: RTL Support

### Layout Mirroring

- **Android:** `android:supportsRtl="true"` in manifest; use `start`/`end` instead of `left`/`right` everywhere
- **iOS:** use leading/trailing constraints, never left/right; SwiftUI handles this automatically with `.leading`/`.trailing`
- **Web:** `dir="auto"` on the `<html>` tag; use CSS logical properties (`margin-inline-start`, `padding-inline-end`) instead of `margin-left`/`padding-right`

### Directional Icons

- Mirror navigation arrows, back buttons, progress indicators for RTL
- Do NOT mirror: clocks, checkmarks, media playback controls, phone icons, brand logos
- Maintain separate icon variants where mirroring via CSS/transform is insufficient

### Bidirectional Text

- Wrap user-generated content in Unicode bidi isolates (`\u2066...\u2069`) when embedding LTR text in RTL context or vice versa
- Phone numbers, URLs, and code snippets are always LTR — isolate them explicitly
- Test mixed-direction content: Arabic sentence containing an English brand name

### Pseudolocale Testing

- **Android:** enable pseudolocales in Developer Options (`en-XA` for accents/expansion, `ar-XB` for RTL)
- **iOS:** use `NSDoubleLocalizedStrings` launch argument for expansion testing
- **Web:** generate pseudolocale JSON files that add accents and padding to every string
- All pseudolocale tests run in CI on every PR

## Step 6: Locale-Aware Formatting

### Dates and Times

```
NEVER: "${month}/${day}/${year}"
ALWAYS: platform date formatter with locale
```

- **Android:** `DateTimeFormatter.ofLocalizedDate(FormatStyle.MEDIUM).withLocale(locale)`
- **iOS:** `Date.FormatStyle.dateTime.locale(locale)` or `DateFormatter` with `locale` set
- **Web:** `Intl.DateTimeFormat(locale, options)` — never `moment.js` format strings

### Numbers and Currency

- **Android:** `NumberFormat.getCurrencyInstance(locale)`
- **iOS:** `Decimal.FormatStyle.currency(code:).locale(locale)`
- **Web:** `Intl.NumberFormat(locale, { style: 'currency', currency: 'USD' })`
- Always pass the currency code explicitly — never assume USD
- Decimal separators differ (1,000.00 vs 1.000,00) — formatters handle this

### Phone Numbers

- Use libphonenumber (Android/web) or Apple's built-in formatter (iOS)
- Store in E.164 format (`+15551234567`), display in local format
- Never regex-validate phone numbers — use the library

### Addresses

- Address field order varies by country (Japan: postal code first; US: street first)
- Use platform address formatters or Google's Address Metadata API
- Never assume address structure (street, city, state, zip)

## Step 7: Translation Workflow

### Pipeline

```
1. Developer adds strings to source locale file (en.json / strings.xml / .xcstrings)
2. CI extracts new/changed strings → export to translation platform
3. Translators translate in platform (Lokalise, Phrase, Crowdin)
4. Translated files imported back via CI pull request
5. CI validates: no missing keys, no untranslated strings, no broken format specifiers
6. Merge → deploy
```

### CI Validation Checks

- **Completeness:** every key in the source locale exists in all target locales
- **Format specifier parity:** `%1$s` count matches across all translations of a key
- **No empty values:** flag keys with empty string translations
- **Max length warnings:** flag translations exceeding platform UI limits (Android: ~40 chars for buttons)
- **ICU syntax validation:** parse all ICU MessageFormat strings for syntax errors

### Missing String Detection

- CI fails if any string key exists in the source locale but is missing from a target locale
- Exception: new locales under active translation may use a `[WIP]` marker in CI config
- Runtime fallback: always fall back to the default locale if a translation is missing — never show a raw key to users

## Step 8: Testing

### Pseudolocale Testing

- Run UI tests with pseudolocale enabled to catch:
  - Text truncation (pseudolocale adds ~40% length)
  - Hardcoded strings (they won't have pseudo-accents)
  - Layout breaks from expanded text

### RTL Layout Verification

- Automated screenshot tests for every screen in both LTR and RTL locales
- **Android:** Roborazzi or Paparazzi screenshot tests with `ar` locale
- **iOS:** snapshot tests with `.environment(\.layoutDirection, .rightToLeft)`
- **Web:** Playwright tests with `locale: 'ar'` configuration

### Screenshot Tests Per Locale

- Generate screenshot baselines for each supported locale
- Run on every PR — diff against baselines to catch regressions
- Minimum: default locale + one RTL locale + longest-text locale (often German)

### Manual QA Checklist

- [ ] All user-facing strings translated and displaying correctly
- [ ] Plurals correct for locales with complex plural rules (Arabic has 6 plural forms)
- [ ] Dates, numbers, currency formatted correctly per locale
- [ ] RTL layout fully mirrored (if applicable)
- [ ] No text truncation or overlap
- [ ] Accessibility labels localized (VoiceOver/TalkBack reads translated text)
- [ ] Deep links and push notifications use correct locale
- [ ] App language switch works without restart (or restart is clearly communicated)

## Step 9: Output Templates

For every i18n implementation, deliver:

1. **String file scaffolds** — source locale files with key naming convention applied
2. **Platform i18n configuration** — locale list, routing, formatter setup
3. **CI validation config** — linting rules and missing-string checks
4. **RTL implementation checklist** — layout mirroring changes needed per screen
5. **Translation workflow diagram** — export/import pipeline with tooling choices

### String Key Audit Table
```
| Key | Source (en) | Status | Notes |
|-----|-------------|--------|-------|
| auth.login.title | "Sign In" | Translated | — |
| auth.login.error.network | "Connection failed" | Missing: ar, ja | Needs translation |
```

## Tech Stack Defaults

```yaml
android:
  string_resources: res/values-{locale}/strings.xml
  locale_switching: AppCompatDelegate.setApplicationLocales()
  compose: stringResource(), pluralStringResource()
  lint: custom detekt rule for hardcoded strings
ios:
  string_catalogs: Localizable.xcstrings (Xcode 15+)
  swiftui: automatic Text() localization
  locale_override: environment(\.locale)
  lint: SwiftLint custom rule
web:
  framework: next-intl 3.x
  routing: middleware locale detection + /[locale]/ prefix
  icu: ICU MessageFormat for plurals and select
  lint: eslint-plugin-i18next
translation_platforms:
  recommended: Lokalise, Phrase, or Crowdin
  export_format: XLIFF (cross-platform), JSON (web), XML (Android)
testing:
  pseudolocale: en-XA (expansion) + ar-XB (RTL)
  screenshots: per-locale baseline comparison in CI
```

## Code Generation (Required)

Generate i18n infrastructure using Write:

1. **String extractor config**: ESLint rule, detekt rule, or SwiftLint rule to flag hardcoded strings
2. **Translation files**: `locales/en.json` — base English strings extracted from codebase
3. **i18n setup**: `src/i18n/config.ts` — i18next or react-intl configuration
4. **Pseudolocale generator**: `scripts/generate-pseudolocale.ts` — generates en-XA for testing
5. **Missing translation detector**: `scripts/check-translations.sh` — finds keys in code without translations

Before generating, Grep for existing i18n setup (`i18next|react-intl|NSLocalizedString|getString|stringResource`) and hardcoded user-facing strings.

## Cross-References

- `/product-design` — design for text expansion and RTL from wireframe stage
- `/accessibility-audit` — ensure localized strings include accessibility labels
- `/testing-strategy` — integrate i18n test suite into testing pyramid
- `/release-management` — coordinate translation completion with release schedule
- `/customer-onboarding` — localize onboarding flows and activation emails
