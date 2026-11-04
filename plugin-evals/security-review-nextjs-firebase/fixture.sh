#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). A small Next 16 + Firebase + Stripe app with
# four planted Cure-recurring issues: a Server Action with no auth/ownership check (IDOR), a
# Firestore rule that only checks request.auth != null on user-owned data, a Stripe webhook that
# never verifies the signature, and a legacy X-XSS-Protection header with no CSP. The AIza…
# Firebase web key is a public identifier and must NOT be reported as a leaked secret.
set -euo pipefail
mkdir -p src/app/actions src/app/api/stripe/webhook src/lib
cat > package.json <<'__FIXTURE_EOF__'
{
  "name": "acme-portal",
  "private": true,
  "scripts": { "dev": "next dev", "build": "next build" },
  "dependencies": {
    "next": "16.0.3",
    "react": "19.2.0",
    "react-dom": "19.2.0",
    "firebase": "12.4.0",
    "firebase-admin": "13.5.0",
    "stripe": "19.1.0"
  }
}
__FIXTURE_EOF__
cat > next.config.ts <<'__FIXTURE_EOF__'
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
        ],
      },
    ];
  },
};

export default nextConfig;
__FIXTURE_EOF__
cat > src/lib/firebase.ts <<'__FIXTURE_EOF__'
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: 'AIzaSyDk3Xq9vLmN0pQrStUvWxYz1234567890a',
  authDomain: 'acme-portal.firebaseapp.com',
  projectId: 'acme-portal',
  appId: '1:123456789012:web:abcdef1234567890',
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
__FIXTURE_EOF__
cat > src/lib/admin.ts <<'__FIXTURE_EOF__'
import { initializeApp, getApps, applicationDefault } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

if (!getApps().length) initializeApp({ credential: applicationDefault() });
export const db = getFirestore();
__FIXTURE_EOF__
cat > src/app/actions/profile.ts <<'__FIXTURE_EOF__'
'use server';

import { db } from '@/lib/admin';

// Called from the profile settings form.
export async function updateProfile(formData: FormData) {
  const userId = String(formData.get('userId'));
  await db.doc(`users/${userId}`).set(
    {
      displayName: String(formData.get('displayName') ?? ''),
      homeAddress: String(formData.get('homeAddress') ?? ''),
      plan: String(formData.get('plan') ?? 'free'),
    },
    { merge: true },
  );
  return { ok: true };
}
__FIXTURE_EOF__
cat > src/app/api/stripe/webhook/route.ts <<'__FIXTURE_EOF__'
import { db } from '@/lib/admin';

export async function POST(req: Request) {
  const event = await req.json();
  if (event.type === 'checkout.session.completed') {
    const uid = event.data.object.client_reference_id;
    await db.doc(`users/${uid}`).set({ plan: 'pro' }, { merge: true });
  }
  return new Response('ok', { status: 200 });
}
__FIXTURE_EOF__
cat > firestore.rules <<'__FIXTURE_EOF__'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
  }
}
__FIXTURE_EOF__
