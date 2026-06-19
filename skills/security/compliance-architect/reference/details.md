# compliance-architect: detailed reference

> Reference material for the `compliance-architect` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 6: Platform-Specific Compliance Patterns

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
