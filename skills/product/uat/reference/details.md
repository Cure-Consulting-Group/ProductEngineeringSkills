# uat: detailed reference

> Reference material for the `uat` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: UAT Execution Framework

## Step 4: UAT Execution Framework

### 4.1 Session-Based Testing

Structure UAT into timeboxed exploratory sessions. Do not let UAT become an open-ended, unstructured activity.

```
SESSION CHARTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session ID:      UAT-S[NNN]
Tester:          [Name]
Duration:        60-90 minutes (hard stop)
Mission:         [What to explore and why]
Scenarios:       UAT-001 through UAT-008
Environment:     [Staging URL / Build number]
Device:          [Device + OS version]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

During session, record:
  - Scenarios executed (pass/fail)
  - Bugs found (with reproduction steps)
  - Questions / ambiguities discovered
  - Areas NOT covered (deferred to next session)

Post-session debrief (15 min):
  - Findings shared with UAT Lead immediately
  - Blockers escalated same-day
  - Next session scope adjusted based on findings
```

### 4.2 Bug Triage During UAT

Every bug found during UAT gets triaged immediately. No bug sits unclassified overnight.

| Severity | Definition | Action | Release Impact |
|---|---|---|---|
| **P0 — Blocker** | Core functionality broken, data loss, security vulnerability, crash on critical path | Fix immediately, re-test same day | Blocks release — no exceptions |
| **P1 — Must-Fix** | Important flow broken, significant UX degradation, accessibility barrier | Fix before release, re-test within UAT window | Blocks release unless risk accepted by PO in writing |
| **P2 — Known Issue** | Minor UX issue, cosmetic defect, edge case with workaround | Document in release notes, fix next sprint | Can ship — documented in release notes |
| **P3 — Enhancement** | Not a bug — a new requirement or improvement discovered during UAT | Add to backlog, do NOT scope-creep the release | No impact on release |

**Bug report format (mandatory for P0 and P1):**
```
BUG REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:              UAT-BUG-[NNN]
Severity:        P0 / P1 / P2 / P3
Scenario:        UAT-[NNN] (link to test scenario)
Summary:         [One-line description]
Device/Browser:  [Device, OS version, browser]
Steps:
  1. [Step]
  2. [Step]
  3. [Step]
Expected:        [What should happen]
Actual:          [What actually happened]
Evidence:        [Screenshot / screen recording — REQUIRED for P0/P1]
Workaround:      [If any]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.3 Device and Browser Matrix

Test on real devices. Simulators and emulators miss real-world issues.

#### Android
| Device Category | Examples | Required? |
|---|---|---|
| Flagship current | Pixel 8 / Samsung S24 | Yes |
| Mid-range | Pixel 7a / Samsung A54 | Yes |
| Low-end (if targeting) | Samsung A14 / Redmi Note 12 | Market-dependent |
| Tablet (if applicable) | Pixel Tablet / Samsung Tab S9 | Only if tablet layout exists |
| Minimum supported OS | Android [minSdk version] | Yes |
| Latest OS | Android 15 | Yes |

**Play Store internal testing track:** Upload the release build to the internal testing track before UAT begins. Testers install via Play Store — this verifies the distribution pipeline, not just the app.

#### iOS
| Device Category | Examples | Required? |
|---|---|---|
| Latest iPhone | iPhone 15 / 16 | Yes |
| Previous generation | iPhone 14 / 13 | Yes |
| Oldest supported | iPhone [minimum target] | Yes |
| iPad (if applicable) | iPad Air / iPad Pro | Only if iPad layout exists |
| Minimum supported iOS | iOS [deployment target] | Yes |
| Latest iOS | iOS 18 | Yes |

**TestFlight distribution:** Upload the release build to TestFlight. All UAT testers install via TestFlight — this verifies the distribution pipeline, provisioning profiles, and entitlements.

#### Web
| Browser | Version | OS | Required? |
|---|---|---|---|
| Chrome | Latest | macOS, Windows | Yes |
| Safari | Latest | macOS, iOS | Yes |
| Firefox | Latest | macOS, Windows | Yes |
| Edge | Latest | Windows | Yes |
| Chrome Mobile | Latest | Android | Yes |
| Safari Mobile | Latest | iOS | Yes |

**Responsive breakpoints:** Test at minimum 320px, 768px, 1024px, 1440px viewport widths. Verify no horizontal overflow, no overlapping elements, no hidden content.

#### Firebase-Specific Verification
```
FIREBASE STAGING CHECKLIST
[ ] Firestore security rules deployed to staging project
[ ] Security rules tested with /security-review output
[ ] Test data seeded in Firestore staging (realistic volume)
[ ] Cloud Functions deployed to staging with correct env vars
[ ] Authentication providers configured in staging project
[ ] Storage rules deployed and verified
[ ] Remote Config values set for UAT (feature flags, thresholds)
[ ] Firestore data integrity: schema matches client expectations
    (cross-reference with /firebase-architect skill output)
```

### 4.4 Accessibility Verification During UAT

Accessibility is not a separate phase — it is verified alongside every scenario. At minimum:

```
ACCESSIBILITY PASS (WCAG AA)
[ ] Screen reader walkthrough of all new/changed screens
    - Android: TalkBack enabled, swipe through every element
    - iOS: VoiceOver enabled, swipe through every element
    - Web: NVDA + Chrome, VoiceOver + Safari
[ ] Keyboard-only navigation (Web): complete flow without mouse
[ ] Touch target sizes: 48x48dp (Android), 44x44pt (iOS), 24x24px minimum (Web)
[ ] Color contrast: 4.5:1 normal text, 3:1 large text
[ ] Dynamic Type / text scaling: test at 200% (Web), AX5 (iOS), largest (Android)
[ ] Reduced motion: animations respect system preference
[ ] Error states announced to screen readers
```

For a full accessibility audit, invoke the `/accessibility-audit` skill.

### 4.5 Offline and Degraded Connectivity (Mobile)

Every mobile feature must handle connectivity loss gracefully. Test these scenarios:

```
CONNECTIVITY SCENARIOS
[ ] Complete feature flow in airplane mode (if offline-capable)
[ ] Start flow online, lose connectivity mid-flow → verify graceful handling
[ ] Restore connectivity → verify sync/recovery
[ ] Slow connection (throttle to 3G / 200kbps) → verify no timeouts on critical paths
[ ] Switch between WiFi and cellular mid-flow → verify no dropped requests
```
