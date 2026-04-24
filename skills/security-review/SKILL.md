---
name: security-review
version: "1.0.0"
description: "OWASP Top 10 security audit for codebases — scans auth flows, API endpoints, data storage, secrets handling, and dependency supply chain across .kt, .swift, .ts, .py, .go, .rs, and infrastructure files"
when_to_use: "Use before launch, after adding auth/payment/PII features, or when asked to 'check security', 'find vulnerabilities', or 'run a security audit'. NOT for compliance frameworks (use compliance-architect). NOT for WCAG (use accessibility-audit)."
argument-hint: "[target-system]"
allowed-tools: ["Read", "Grep", "Glob"]
context: fork
---

# Security Review

Structured security review for mobile apps, web apps, APIs, and cloud infrastructure. Run before every launch, after major features, and quarterly on production systems.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Automated Vulnerability Scan (Before Manual Review)

Before applying the security framework, scan the codebase with Grep:

1. **Secrets Detection**:
   - Grep for: `sk-[a-zA-Z0-9]`, `pk_[a-zA-Z0-9]`, `ghp_`, `AIza`, `AKIA`, `password\s*=\s*["']`
   - Grep for: hardcoded URLs with credentials (`://.*:.*@`)
2. **Input Validation**:
   - Grep for: `req.body\.` or `request\.` without adjacent validation (`zod|joi|yup|validate`)
   - Grep for: `innerHTML|dangerouslySetInnerHTML` (XSS vectors)
   - Grep for: raw SQL concatenation (`\+ .*query|` + `.*sql`)
3. **Auth Gaps**:
   - Grep for: API routes without auth middleware (`app.get|app.post` without `auth|protect|verify`)
   - Grep for: Firestore rules with `allow read: if true` or `allow write: if true`
4. **Dependency Check**:
   - Run: `npm audit --json 2>/dev/null | head -50` to check for known vulnerabilities
5. **Sensitive Files**:
   - Glob for: `**/.env`, `**/credentials*`, `**/serviceAccount*`, `**/*.pem` that might be committed

Report all findings with file:line references before proceeding to the manual framework.

## Step 1: Classify the Review Type

| Trigger | Scope |
|---------|-------|
| Pre-launch | Full review — all categories below |
| New feature with auth/payments | Auth + data + API sections |
| Dependency update | Supply chain section |
| Quarterly review | Full review + dependency audit |
| Incident response | Targeted review of affected area |

## Step 2: Gather Context

1. **What's being reviewed** — app, API, infrastructure, or specific feature?
2. **Data handled** — PII, financial, health, children's data?
3. **Auth mechanism** — Firebase Auth, OAuth, JWT, API keys?
4. **Deployment** — Firebase, Vercel, AWS, GCP?
5. **Third-party services** — Stripe, analytics, LLM APIs?
6. **Compliance requirements** — SOC 2, HIPAA, GDPR, CCPA, COPPA?

## Step 3: Authentication & Authorization

### Checklist
- [ ] Passwords hashed with bcrypt/scrypt/argon2 (never MD5/SHA1)
- [ ] Session tokens are cryptographically random, sufficient length (>=128 bits)
- [ ] Tokens expire (access: 15min-1hr, refresh: 7-30 days)
- [ ] Failed login rate limiting (5 attempts → lockout or CAPTCHA)
- [ ] MFA available for sensitive operations (payments, account deletion)
- [ ] OAuth state parameter validated (prevents CSRF on OAuth flow)
- [ ] Firebase Auth: email enumeration protection enabled
- [ ] Authorization checked on EVERY server endpoint (not just client-side)
- [ ] Role-based access: users cannot escalate their own permissions
- [ ] API keys scoped to minimum required permissions

### Common Vulnerabilities
```
IDOR (Insecure Direct Object Reference):
  BAD:  /api/users/123/profile  (any user can access any profile)
  GOOD: /api/users/me/profile   (server resolves from auth token)

Broken Access Control:
  BAD:  Client hides admin button → user modifies request → accesses admin
  GOOD: Server validates role on every admin endpoint
```

## Step 4: Data Protection

### In Transit
- [ ] HTTPS everywhere (no mixed content)
- [ ] HSTS header set with includeSubdomains and preload
- [ ] TLS 1.2 minimum (prefer 1.3)
- [ ] Certificate pinning on mobile (for sensitive apps)
- [ ] API responses don't leak data in error messages

### At Rest
- [ ] Database encryption enabled (Firestore: automatic, SQL: TDE)
- [ ] Backups encrypted
- [ ] Sensitive fields encrypted at application level (SSN, card numbers)
- [ ] File uploads scanned for malware before storage
- [ ] PII access logged for audit trail

### Secrets Management
```
NEVER in code:
  - API keys, tokens, passwords
  - Service account JSON files
  - Stripe secret keys
  - Database connection strings
  - JWT signing secrets

WHERE secrets live:
  - Firebase/GCP: Secret Manager
  - GitHub: Repository Secrets (CI/CD)
  - Local dev: .env files (in .gitignore)
  - Mobile: BuildConfig / Info.plist (non-sensitive only)
```

## Step 5: API Security

- [ ] Input validation on ALL endpoints (type, length, format)
- [ ] Rate limiting per user/IP (prevent abuse)
- [ ] Request size limits (prevent payload bombs)
- [ ] SQL injection prevention (parameterized queries, ORMs)
- [ ] NoSQL injection prevention (validate Firestore query inputs)
- [ ] File upload: validate type, size, scan content
- [ ] CORS configured to allow only known origins
- [ ] CSRF protection on state-changing endpoints
- [ ] API versioning (don't break existing clients)
- [ ] Error responses don't leak stack traces, file paths, or DB schemas

## Step 6: Mobile-Specific

### Android
- [ ] ProGuard/R8 enabled for release builds (code obfuscation)
- [ ] No sensitive data in SharedPreferences (use EncryptedSharedPreferences)
- [ ] Certificate pinning configured
- [ ] Exported activities/services/receivers intentionally exported
- [ ] No logging of sensitive data in release builds
- [ ] WebView: JavaScript disabled unless required, no file:// access

### iOS
- [ ] ATS (App Transport Security) enabled, no exceptions without justification
- [ ] Keychain used for sensitive data (not UserDefaults)
- [ ] No sensitive data in app screenshots (implement blur on background)
- [ ] Jailbreak detection for high-security apps
- [ ] No sensitive data logged with os_log in release

## Step 7: Web-Specific

### Headers (verify all present)
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0  (deprecated — use CSP instead)
Content-Security-Policy: default-src 'self'; script-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

### XSS Prevention
- [ ] All user input escaped before rendering (React does this by default)
- [ ] No `dangerouslySetInnerHTML` with user-supplied content
- [ ] CSP header blocks inline scripts
- [ ] Sanitize HTML if rich text is required (DOMPurify)

## Step 8: Supply Chain Security

- [ ] `npm audit` / `gradle dependencyCheckAnalyze` run in CI
- [ ] No dependencies with known critical CVEs
- [ ] Lock files committed (package-lock.json, Podfile.lock, gradle.lockfile)
- [ ] Dependabot or Renovate configured for automatic updates
- [ ] Review new dependencies before adding (check maintainership, download count, last update)
- [ ] No `*` version ranges in dependencies

## Step 9: Firebase-Specific

- [ ] Firestore security rules: no open reads/writes (test with emulator)
- [ ] Storage security rules: file type and size validation
- [ ] Cloud Functions: validate callable function inputs
- [ ] Auth: email enumeration protection enabled
- [ ] No service account keys in client code
- [ ] Firebase App Check enabled (prevents API abuse)

## Step 10: Audit Report Output

```
SECURITY REVIEW REPORT
Application: [NAME]
Date: [TODAY]
Reviewer: [NAME]

RISK SUMMARY
┌─────────────────────┬────────┬────────┐
│ Category            │ Status │ Issues │
├─────────────────────┼────────┼────────┤
│ Auth & Authorization│ 🟢🟡🔴 │   X    │
│ Data Protection     │ 🟢🟡🔴 │   X    │
│ API Security        │ 🟢🟡🔴 │   X    │
│ Mobile Security     │ 🟢🟡🔴 │   X    │
│ Web Security        │ 🟢🟡🔴 │   X    │
│ Supply Chain        │ 🟢🟡🔴 │   X    │
│ Firebase Config     │ 🟢🟡🔴 │   X    │
└─────────────────────┴────────┴────────┘

CRITICAL (fix before ship):
1. [Issue] — [Risk] — [Fix]

HIGH (fix within 1 sprint):
1. [Issue] — [Risk] — [Fix]

MEDIUM (schedule for next quarter):
1. [Issue] — [Risk] — [Fix]
```
