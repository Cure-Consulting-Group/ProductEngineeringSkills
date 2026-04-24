---
name: compliance-architect
version: "1.0.0"
description: "Architect compliance frameworks for HIPAA, COPPA, GDPR, CCPA, and PCI — consent flows, audit trails, data classification, and privacy-by-design"
when_to_use: "Use for HIPAA, COPPA, GDPR, CCPA, or PCI compliance frameworks. NOT for QSBS (use qsbs-compliance). NOT for FERPA or ECAG (use dedicated skills when available). NOT for OWASP security (use security-review)."
argument-hint: "[regulation-or-project]"
context: fork
---

# Compliance Architect

Designs production-grade compliance architectures for regulated applications. Covers HIPAA, COPPA, GDPR, CCPA, PCI DSS, and SOC 2 — from data classification through consent management, audit trails, and vendor assessment. Every recommendation targets Cure Consulting Group's Firebase-first stack with Android, iOS, and web clients.

**Hard rules:**
- Privacy by design — compliance is an architecture concern, not an afterthought
- Data minimization — never collect what you don't need, never retain what you no longer use
- Consent must be granular, revocable, and provably recorded
- PHI, PCI data, and children's data require encryption at rest AND in transit with key separation
- All compliance controls must be testable and auditable — no "trust me" security

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Automated Compliance Scan

Scan codebase for compliance signals before framework application:

1. **PII Detection**: Grep for fields likely containing PII:
   - `email|phone|ssn|social_security|date_of_birth|address|name` in data models
2. **Consent Tracking**: Grep for consent mechanisms:
   - `consent|gdpr|opt_in|opt_out|cookie` — flag if absent in user-facing code
3. **Data Retention**: Grep for deletion/retention logic:
   - `delete|remove|purge|retain|expire|ttl` in data layer code
4. **Audit Trail**: Grep for logging of data access:
   - `audit|log.*access|track.*change` — flag if absent in data layer
5. **Encryption**: Grep for encryption usage:
   - `encrypt|decrypt|AES|RSA|bcrypt|argon2|hash` — flag if absent for sensitive data

Report compliance posture before detailed framework analysis.

## Step 1: Classify the Regulation

| Regulation | Trigger | Key Requirements | Penalty Range |
|-----------|---------|-----------------|---------------|
| HIPAA | Health data (PHI) for US persons | BAA chain, access controls, encryption, audit logs, breach notification within 60 days | $100–$50,000 per violation, up to $1.5M/year per category |
| COPPA | Users under 13 (US) | Verifiable parental consent, data minimization, no behavioral advertising, deletion on request | $50,120 per violation (FTC) |
| GDPR | EU/EEA residents' personal data | Lawful basis, DPO, DPIA, 72-hour breach notification, right to erasure, data portability | Up to 4% of global annual revenue or 20M EUR |
| CCPA/CPRA | California residents' personal information | Right to know, delete, opt-out of sale, no discrimination, 45-day response window | $2,500 per violation, $7,500 per intentional violation |
| PCI DSS | Credit card processing/storage | Network segmentation, encryption, access control, vulnerability management, quarterly scans | $5,000–$100,000/month from payment brands |
| SOC 2 | B2B SaaS / enterprise customers | Trust Service Criteria (security, availability, confidentiality, processing integrity, privacy) | No direct penalty — loss of enterprise deals |
| Multi-Regulation | Multiple of above | Union of all applicable requirements; strictest standard wins on conflicts | Compounding risk |

If the project handles **health data for users under 13**, both HIPAA and COPPA apply — COPPA's consent requirements are stricter and take precedence for consent flows.

## Step 2: Gather Context

Before generating compliance architecture, confirm:

1. **Data types collected** — PII (name, email, phone), PHI (diagnoses, medications, vitals), financial (card numbers, bank accounts), behavioral (usage patterns, location), children's data?
2. **User demographics** — age ranges, geographic distribution (US, EU, California specifically), known vulnerable populations?
3. **Data flow** — where is data collected (mobile, web, API), where is it stored (Firestore, Cloud SQL, local device), where does it transit (Cloud Functions, third-party APIs)?
4. **Third-party services** — analytics providers, payment processors, LLM APIs, email services, crash reporting — do they receive regulated data?
5. **Existing controls** — current auth mechanism, encryption state, logging, access controls?
6. **Business requirements** — do you need to process payments directly (PCI scope), store health records (HIPAA scope), serve children (COPPA scope)?
7. **Timeline** — greenfield (design from scratch) or retrofitting compliance onto existing system?

## Step 3: Data Classification Matrix

Every field in your system must be classified. No exceptions.

### Classification Levels

```
┌────────────┬────────────────────────────────────────────────────────────────┐
│ Level      │ Description                                                    │
├────────────┼────────────────────────────────────────────────────────────────┤
│ PUBLIC     │ Intended for public access. No controls required.              │
│            │ Examples: app name, public profile display names, marketing    │
│            │ content, published blog posts                                  │
├────────────┼────────────────────────────────────────────────────────────────┤
│ INTERNAL   │ Not public but low sensitivity. Standard access controls.      │
│            │ Examples: internal user IDs, non-PII analytics events,         │
│            │ feature flag states, app configuration                         │
├────────────┼────────────────────────────────────────────────────────────────┤
│ CONFIDENTIAL│ PII and business-sensitive data. Encrypted, access-logged.    │
│            │ Examples: email, phone number, mailing address, date of birth, │
│            │ usage history, IP addresses, device identifiers                │
├────────────┼────────────────────────────────────────────────────────────────┤
│ RESTRICTED │ Highest sensitivity. Encrypted, access-logged, key-separated.  │
│            │ Examples: PHI (diagnoses, medications, vitals), PCI data       │
│            │ (card numbers, CVV — never store CVV), SSN, children's PII,   │
│            │ biometric data, passwords/secrets, authentication tokens       │
└────────────┴────────────────────────────────────────────────────────────────┘
```

### Classification Actions by Level

```
┌──────────────────────┬────────┬──────────┬──────────────┬────────────┐
│ Control              │ PUBLIC │ INTERNAL │ CONFIDENTIAL │ RESTRICTED │
├──────────────────────┼────────┼──────────┼──────────────┼────────────┤
│ Encryption at rest   │ No     │ Default  │ Required     │ Required + │
│                      │        │          │              │ key sep.   │
│ Encryption in transit│ TLS    │ TLS      │ TLS 1.2+    │ TLS 1.3    │
│ Access logging       │ No     │ No       │ Yes          │ Yes + alert│
│ Retention policy     │ None   │ 1 year   │ Per reg.     │ Per reg.   │
│ Backup encryption    │ No     │ Default  │ Required     │ Required   │
│ Access control       │ None   │ Role     │ Role + MFA   │ Role + MFA │
│                      │        │          │              │ + approval │
│ Data masking in logs │ No     │ No       │ Yes          │ Yes        │
│ Right to erasure     │ N/A    │ N/A      │ Required     │ Required   │
│ Cross-border transfer│ Free   │ Free     │ Restricted   │ Restricted │
│ Breach notification  │ N/A    │ Internal │ Regulatory   │ Regulatory │
│                      │        │          │              │ + users    │
└──────────────────────┴────────┴──────────┴──────────────┴────────────┘
```

### Field-Level Classification Template

```
Collection: users
┌─────────────────────┬──────────────┬─────────────┬───────────────────┐
│ Field               │ Classification│ Regulation  │ Retention         │
├─────────────────────┼──────────────┼─────────────┼───────────────────┤
│ uid                 │ INTERNAL     │ —           │ Account lifetime  │
│ email               │ CONFIDENTIAL │ GDPR/CCPA   │ Account + 30 days│
│ displayName         │ CONFIDENTIAL │ GDPR/CCPA   │ Account + 30 days│
│ dateOfBirth         │ CONFIDENTIAL │ COPPA/GDPR  │ Account + 30 days│
│ healthRecords       │ RESTRICTED   │ HIPAA       │ 6 years (HIPAA)  │
│ paymentMethodToken  │ RESTRICTED   │ PCI DSS     │ Active sub only  │
│ parentConsentRecord │ RESTRICTED   │ COPPA       │ Account + 3 years│
└─────────────────────┴──────────────┴─────────────┴───────────────────┘
```

## Step 4: Consent Management Architecture

### Consent Record Schema (Firestore)

```
Collection: consent_records
Document ID: {userId}_{consentType}_{timestamp}

{
  userId: string,              // Firebase Auth UID
  consentType: string,         // "marketing", "analytics", "data_processing", "parental"
  granted: boolean,            // true = opted in, false = opted out / withdrawn
  version: string,             // "privacy-policy-v2.1" — ties to specific policy text
  method: string,              // "in_app_toggle", "signup_checkbox", "parental_email_verification"
  ipAddress: string,           // captured at time of consent (encrypted)
  userAgent: string,           // browser/device info at time of consent
  timestamp: Timestamp,        // server timestamp — never client-provided
  expiresAt: Timestamp | null, // null = until withdrawn; COPPA = re-consent annually
  parentEmail: string | null,  // COPPA: parent/guardian email for verification
  withdrawnAt: Timestamp | null
}
```

**Immutability rule:** consent records are append-only. Never update or delete a consent record. Withdrawal creates a new record with `granted: false`.

### Opt-In Flow Requirements

```
GDPR:
  - Consent must be freely given, specific, informed, and unambiguous
  - Pre-checked boxes are NOT valid consent
  - Separate consent for each processing purpose (marketing, analytics, etc.)
  - Clear explanation of what data is collected and why
  - Link to full privacy policy before consent action

COPPA (users under 13):
  - Verifiable parental consent BEFORE collecting any data
  - Methods: signed consent form, credit card verification, video call,
    government ID check, knowledge-based authentication
  - Re-verify consent annually
  - Parent can review, delete, and refuse further collection at any time

CCPA/CPRA:
  - "Do Not Sell or Share My Personal Information" link on homepage
  - Opt-out must be as easy as opt-in (no dark patterns)
  - Financial incentive programs require separate opt-in
  - Global Privacy Control (GPC) browser signal must be honored

HIPAA:
  - Authorization form for uses beyond treatment/payment/operations
  - Must specify: what PHI, who receives it, purpose, expiration
  - Patient can revoke authorization at any time
```

### Age Gate Implementation

```
COPPA age gate flow:
  1. Ask date of birth during onboarding (DO NOT store if under 13 and no consent)
  2. If age < 13:
     a. Block account creation
     b. Collect parent/guardian email only
     c. Send verifiable parental consent request
     d. Wait for consent verification (24-72 hour window)
     e. If consent received → create restricted child account
     f. If no consent → delete parent email, show rejection screen
  3. If age >= 13 but < 18:
     a. Create account with age-appropriate content restrictions
     b. No behavioral advertising, no data sale
  4. If age >= 18:
     a. Standard consent flow

Platform implementation:
  Android: age gate screen before any data collection; store consent state
           in EncryptedSharedPreferences
  iOS:     age gate screen before any data collection; store consent state
           in Keychain
  Web:     age gate modal before any cookies/tracking; respect GPC signal
```

## Step 5: Audit Trail Implementation

### Immutable Audit Log Schema

```
Collection: audit_logs
Document ID: auto-generated

{
  eventId: string,          // UUID v4
  timestamp: Timestamp,     // server timestamp
  actorId: string,          // Firebase Auth UID or "system"
  actorRole: string,        // "user", "admin", "system", "support"
  action: string,           // "read", "create", "update", "delete", "export", "consent_granted"
  resource: string,         // "users/{uid}", "health_records/{id}"
  resourceClassification: string, // "CONFIDENTIAL", "RESTRICTED"
  fieldsAccessed: string[], // ["email", "dateOfBirth"] — for read events
  fieldsModified: string[], // ["email"] — for update events, with before/after hashes
  ipAddress: string,        // encrypted
  userAgent: string,
  result: string,           // "success", "denied", "error"
  reason: string | null,    // required for RESTRICTED data access: "patient_requested_export"
  metadata: object          // additional context as needed
}
```

### Access Tracking Rules

```
Log EVERY access to CONFIDENTIAL and RESTRICTED data:
  - User views their own profile → log (HIPAA requires it)
  - Admin views user record → log with reason
  - System process reads PHI → log with process identifier
  - Export or download → log with destination
  - Failed access attempt → log with denial reason

Retention:
  - HIPAA audit logs: 6 years minimum
  - GDPR audit logs: duration of processing + 1 year
  - PCI audit logs: 1 year readily available, archive for 3 years
  - SOC 2 audit logs: 1 year minimum

Storage:
  - Primary: Firestore collection with security rules preventing deletion
  - Archive: Cloud Storage (coldline) for logs older than 90 days
  - Never store audit logs in the same database as the data they protect
```

### Data Lineage Tracking

```
For RESTRICTED data, track:
  1. Origin: where was this data first collected (signup form, API import, manual entry)?
  2. Transformations: was it anonymized, aggregated, derived?
  3. Copies: where does this data exist (Firestore, Cloud SQL, analytics, backups)?
  4. Sharing: was it sent to third parties (analytics, LLM APIs, support tools)?
  5. Retention: when is it scheduled for deletion?

Implement as a data_lineage subcollection on RESTRICTED documents:
  {
    origin: { source: "signup_form", timestamp: Timestamp, consentId: string },
    copies: [{ location: "bigquery.analytics.users", syncedAt: Timestamp }],
    shares: [{ recipient: "stripe", purpose: "payment_processing", dpaId: string }],
    scheduledDeletion: Timestamp
  }
```

## Step 6: Platform-Specific Compliance Patterns

### Android

```kotlin
// EncryptedSharedPreferences for CONFIDENTIAL/RESTRICTED local data
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Room database encryption with SQLCipher
val passphrase = SecureRandom().let { random ->
    ByteArray(32).also { random.nextBytes(it) }
}
val factory = SupportFactory(passphrase)
Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .openHelperFactory(factory)
    .build()

// COPPA: disable analytics for child accounts
if (user.isUnder13) {
    FirebaseAnalytics.getInstance(context).setAnalyticsCollectionEnabled(false)
    FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(false)
}
```

### iOS

```swift
// Keychain for RESTRICTED data
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "healthRecordEncryptionKey",
    kSecValueData as String: keyData,
    kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
]
SecItemAdd(query as CFDictionary, nil)

// COPPA: disable tracking for child accounts
if user.isUnder13 {
    Analytics.setAnalyticsCollectionEnabled(false)
    Crashlytics.crashlytics().setCrashlyticsCollectionEnabled(false)
}

// HIPAA: blur screen content when app enters background
func sceneWillResignActive(_ scene: UIScene) {
    let blurEffect = UIBlurEffect(style: .light)
    let blurView = UIVisualEffectView(effect: blurEffect)
    blurView.tag = 999
    window?.addSubview(blurView)
}
```

### Firestore Security Rules for PHI

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Health records: only the patient or authorized providers
    match /health_records/{recordId} {
      allow read: if request.auth != null
        && (request.auth.uid == resource.data.patientId
            || request.auth.token.role == 'provider'
            && request.auth.uid in resource.data.authorizedProviders);
      allow write: if request.auth != null
        && request.auth.token.role == 'provider'
        && request.auth.uid in resource.data.authorizedProviders;
      allow delete: if false; // PHI cannot be deleted via client — admin function only
    }

    // Audit logs: append-only, no client deletes or updates
    match /audit_logs/{logId} {
      allow create: if request.auth != null;
      allow read: if request.auth.token.role == 'admin'
                  || request.auth.token.role == 'compliance_officer';
      allow update, delete: if false;
    }

    // Consent records: append-only
    match /consent_records/{recordId} {
      allow create: if request.auth != null
        && request.resource.data.userId == request.auth.uid;
      allow read: if request.auth.uid == resource.data.userId
                  || request.auth.token.role == 'admin';
      allow update, delete: if false;
    }
  }
}
```

### Firebase Auth Custom Claims for Compliance Roles

```typescript
// Cloud Function to set compliance-related custom claims
export const setComplianceRole = functions.https.onCall(async (data, context) => {
  if (!context.auth?.token.role || context.auth.token.role !== 'admin') {
    throw new functions.https.HttpsError('permission-denied', 'Admin only');
  }

  const { uid, role } = data;
  const validRoles = ['user', 'provider', 'admin', 'compliance_officer'];
  if (!validRoles.includes(role)) {
    throw new functions.https.HttpsError('invalid-argument', 'Invalid role');
  }

  await admin.auth().setCustomUserClaims(uid, { role });
  // Audit log the role change
  await admin.firestore().collection('audit_logs').add({
    eventId: uuidv4(),
    timestamp: admin.firestore.FieldValue.serverTimestamp(),
    actorId: context.auth.uid,
    actorRole: context.auth.token.role,
    action: 'update',
    resource: `users/${uid}`,
    resourceClassification: 'RESTRICTED',
    fieldsModified: ['customClaims.role'],
    result: 'success',
    reason: data.reason || 'role_assignment',
  });
});
```

## Step 7: BAA/DPA Requirements and Vendor Assessment

### Business Associate Agreement (HIPAA)

```
Required BAA chain for HIPAA:
  ┌─────────────────────┬──────────────┬──────────────────────────────┐
  │ Vendor              │ BAA Status   │ Notes                        │
  ├─────────────────────┼──────────────┼──────────────────────────────┤
  │ Google Cloud / Firebase │ Available│ Must enable in GCP console   │
  │ Stripe              │ Available    │ Request via Stripe support    │
  │ SendGrid / Twilio   │ Available    │ Enterprise plan required      │
  │ OpenAI              │ Available    │ Enterprise plan, no PHI in    │
  │                     │              │ standard API without BAA     │
  │ Sentry              │ Available    │ Business plan required        │
  │ Vercel              │ Not available│ Do NOT route PHI through      │
  │ Analytics (GA4)     │ Available    │ But do NOT send PHI to GA4   │
  │ Mixpanel            │ Available    │ Enterprise plan               │
  └─────────────────────┴──────────────┴──────────────────────────────┘

BAA checklist:
  - [ ] BAA signed with every vendor that touches PHI
  - [ ] BAA specifies permitted uses and disclosures
  - [ ] BAA requires breach notification within contractual timeframe
  - [ ] BAA requires vendor to implement safeguards
  - [ ] BAA inventory maintained and reviewed annually
  - [ ] No PHI sent to vendors without BAA (including LLM APIs)
```

### Data Processing Agreement (GDPR)

```
Required DPA elements:
  - [ ] Processing purposes clearly defined
  - [ ] Categories of personal data specified
  - [ ] Data subjects identified (users, employees, etc.)
  - [ ] Sub-processor list provided and updated
  - [ ] Data transfer mechanisms for non-EU transfers (SCCs, adequacy decision)
  - [ ] Data deletion/return obligations on contract termination
  - [ ] Audit rights for the data controller
  - [ ] Breach notification obligations (without undue delay)
```

### Vendor Compliance Assessment Scorecard

```
For each vendor processing regulated data, score:

┌──────────────────────────┬────────────────────────────────────┬───────┐
│ Criterion                │ Evidence Required                  │ Score │
├──────────────────────────┼────────────────────────────────────┼───────┤
│ SOC 2 Type II report     │ Current report (within 12 months)  │ /10   │
│ Encryption at rest       │ Documentation of encryption method │ /10   │
│ Encryption in transit    │ TLS version and configuration      │ /10   │
│ Access controls          │ RBAC, MFA, audit logging           │ /10   │
│ BAA/DPA availability     │ Signed agreement                   │ /10   │
│ Breach notification SLA  │ Contractual commitment             │ /10   │
│ Data residency options   │ Region selection available          │ /10   │
│ Incident response plan   │ Published IR process               │ /10   │
│ Sub-processor management │ List available, notification of changes │ /10   │
│ Data deletion capability │ API or process for data removal    │ /10   │
├──────────────────────────┼────────────────────────────────────┼───────┤
│ TOTAL                    │                                    │ /100  │
└──────────────────────────┴────────────────────────────────────┴───────┘

Scoring:  90-100 = Approved  |  70-89 = Approved with conditions  |  <70 = Rejected
```

## Step 8: Compliance Testing and Verification

### Automated Compliance Tests

```
Test categories (run in CI):

1. Data classification enforcement:
   - Verify no RESTRICTED fields in analytics events
   - Verify no PII in log output (scan for email/phone/SSN patterns)
   - Verify encryption is applied to CONFIDENTIAL/RESTRICTED fields

2. Consent verification:
   - Verify data processing is gated on consent records
   - Verify age gate blocks under-13 users without parental consent
   - Verify consent withdrawal stops data processing within 24 hours

3. Access control:
   - Verify Firestore security rules deny unauthorized access
   - Verify API endpoints require authentication
   - Verify role-based access restrictions (use Firebase Emulator)

4. Audit trail:
   - Verify audit logs are created for CONFIDENTIAL/RESTRICTED data access
   - Verify audit logs cannot be modified or deleted via client
   - Verify audit log retention meets regulatory requirements

5. Data retention:
   - Verify scheduled deletion jobs run and complete
   - Verify right-to-erasure requests are fulfilled within SLA
   - Verify backups containing deleted data are purged per policy

6. Third-party data flow:
   - Verify no PHI sent to vendors without BAA
   - Verify analytics events contain no PII for child accounts
   - Verify LLM API calls strip RESTRICTED data before sending
```

### Compliance Verification Scripts

```typescript
// Firebase Emulator test: verify security rules block unauthorized PHI access
describe('Health Records Security Rules', () => {
  it('denies read access to non-patient, non-provider users', async () => {
    const db = testEnv.authenticatedContext('random-user').firestore();
    const docRef = db.collection('health_records').doc('record-1');
    await assertFails(docRef.get());
  });

  it('allows patient to read their own records', async () => {
    const db = testEnv.authenticatedContext('patient-uid').firestore();
    const docRef = db.collection('health_records').doc('record-1');
    await assertSucceeds(docRef.get());
  });

  it('prevents deletion of audit logs', async () => {
    const db = testEnv.authenticatedContext('admin-uid', { role: 'admin' }).firestore();
    const docRef = db.collection('audit_logs').doc('log-1');
    await assertFails(docRef.delete());
  });

  it('prevents update of consent records', async () => {
    const db = testEnv.authenticatedContext('user-uid').firestore();
    const docRef = db.collection('consent_records').doc('consent-1');
    await assertFails(docRef.update({ granted: false }));
  });
});
```

### Right to Erasure Verification

```
GDPR/CCPA deletion request workflow:
  1. User submits deletion request (in-app or email)
  2. Verify identity (re-authentication required)
  3. Create deletion job record with 30-day grace period (GDPR allows up to 30 days)
  4. After grace period:
     a. Delete user profile from Firestore
     b. Delete user data from Cloud SQL
     c. Delete uploaded files from Cloud Storage
     d. Remove from analytics (anonymize historical data)
     e. Remove from third-party systems (Stripe customer, email lists)
     f. Delete Firebase Auth account
     g. Create audit log of deletion (retain: deletion record only, no PII)
  5. Confirm deletion to user via email (last communication)
  6. Verify deletion in next compliance audit
```

## Compliance Report Output

```
COMPLIANCE ARCHITECTURE REPORT
Application: [NAME]
Date: [TODAY]
Architect: [NAME]

REGULATION COVERAGE
┌────────────────────┬──────────┬────────────────────────────────────┐
│ Regulation         │ Status   │ Notes                              │
├────────────────────┼──────────┼────────────────────────────────────┤
│ HIPAA              │ [Y/N/NA] │ [BAA status, PHI handling]         │
│ COPPA              │ [Y/N/NA] │ [Age gate, parental consent]       │
│ GDPR               │ [Y/N/NA] │ [DPA status, lawful basis]         │
│ CCPA/CPRA          │ [Y/N/NA] │ [Opt-out mechanism, GPC support]   │
│ PCI DSS            │ [Y/N/NA] │ [Scope reduction via tokenization] │
│ SOC 2              │ [Y/N/NA] │ [Trust criteria coverage]          │
└────────────────────┴──────────┴────────────────────────────────────┘

DATA CLASSIFICATION SUMMARY
  Public fields:       [count]
  Internal fields:     [count]
  Confidential fields: [count]
  Restricted fields:   [count]

DELIVERABLES GENERATED:
  - [ ] Data classification matrix (all collections/tables)
  - [ ] Consent management architecture (schema, flows, age gate)
  - [ ] Audit trail implementation (schema, retention, access rules)
  - [ ] Platform-specific encryption patterns (Android, iOS, Firestore)
  - [ ] BAA/DPA inventory with vendor assessment scores
  - [ ] Compliance test suite (security rules, consent, retention)
  - [ ] Right-to-erasure workflow and verification
  - [ ] Firestore security rules for regulated data

CROSS-REFERENCES:
  - /security-review — for OWASP checklist and penetration testing
  - /legal-doc-scaffold — for privacy policy and terms of service generation
  - /firebase-architect — for Firestore schema and security rules design
  - /test-accounts — for compliance-safe test data management
```
