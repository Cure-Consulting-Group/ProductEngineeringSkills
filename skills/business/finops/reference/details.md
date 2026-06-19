# finops: detailed reference

> Reference material for the `finops` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Firebase-Specific Optimization

## Step 4: Firebase-Specific Optimization

### Firestore Read/Write Reduction
```
Firestore costs $0.06/100K reads and $0.18/100K writes.
At scale, reads are the dominant cost. Reduce them aggressively.

Optimization                          Estimated Savings
──────────────────────────────────────────────────────────────────
Enable offline persistence             30-50% read reduction (cached locally)
Use onSnapshot listeners wisely        1 read per change, not per poll
Pagination (limit queries to 20-50)    Prevents "read the whole collection"
Denormalize for read-heavy patterns    1 read instead of N joins
Composite indexes                      Fewer reads per query (more efficient)
Security rule optimization             Fewer get() calls in rules
Batch reads (getAll)                   1 API call instead of N

Anti-patterns to eliminate:
  ❌ Reading entire collection to filter client-side
  ❌ Polling with getDoc() instead of using onSnapshot()
  ❌ Storing computed values that could be derived
  ❌ No pagination on list screens
  ❌ get() calls in security rules for every request (cache with custom claims)
```

### Cloud Functions Optimization
```
Cloud Functions cost: invocations ($0.40/M) + compute (CPU-seconds + memory-seconds)

Optimization                          Estimated Savings
──────────────────────────────────────────────────────────────────
Right-size memory (don't use 1GB       Up to 75% compute cost reduction
  when 256MB suffices)
Increase concurrency (80 req/inst)     Fewer instances = less compute
Set maxInstances cap                   Prevents runaway costs from traffic spikes
Reduce cold starts (minInstances=0     Pay nothing when idle
  for low-traffic, =1 for critical)
Combine related functions              Fewer cold starts, shared dependencies
Use Cloud Tasks for async work         Decouple from request lifecycle
Move heavy computation to Cloud Run    Better cost model for long-running tasks

Memory right-sizing guide:
  Simple webhook handler:     128MiB
  Standard API endpoint:      256MiB
  Image processing:           512MiB-1GiB
  PDF generation:             1GiB
  ML inference:               2GiB+ (consider Cloud Run instead)
```

### Storage Lifecycle Policies
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "Delete" },
        "condition": { "age": 7, "matchesPrefix": ["tmp/", "cache/", "uploads/processing/"] }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "NEARLINE" },
        "condition": { "age": 30, "matchesPrefix": ["uploads/"] }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "COLDLINE" },
        "condition": { "age": 90, "matchesPrefix": ["backups/"] }
      },
      {
        "action": { "type": "Delete" },
        "condition": { "age": 365, "matchesPrefix": ["logs/", "analytics-exports/"] }
      }
    ]
  }
}

// Apply: gsutil lifecycle set lifecycle.json gs://BUCKET_NAME
// Estimated savings: 40-60% on storage costs for mature projects
```

### Auth Cost Awareness
```
Firebase Auth pricing:
  Phone auth:              $0.01-0.06 per SMS verification
  Email/password:          Free (unlimited)
  Google/Apple/GitHub:     Free (unlimited)
  Anonymous auth:          Free (unlimited)
  SAML/OIDC (enterprise): $0.015 per MAU above 50 free

Cost traps:
  ❌ SMS verification for every login (use phone auth only for registration)
  ❌ Anonymous auth that never converts (creates orphan accounts)
  ❌ Not cleaning up disabled/unused accounts

Optimizations:
  ✅ Use email link sign-in instead of SMS where possible
  ✅ Convert anonymous users or delete after 30 days
  ✅ Use custom claims instead of Firestore lookups for auth context
```
