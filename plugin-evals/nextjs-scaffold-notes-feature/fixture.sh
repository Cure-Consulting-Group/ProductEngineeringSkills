#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). A Next 16 App Router project (cacheComponents on,
# Zod 4) with an existing projects route, a session helper, and a data module. The feature must
# use Next 16's async params, check auth inside the Server Action, validate with Zod 4 (no
# deprecated error.flatten()), and ship the route boundaries.
set -euo pipefail
mkdir -p 'src/app/projects/[id]' src/lib
cat > package.json <<'__FIXTURE_EOF__'
{
  "name": "teamboard",
  "private": true,
  "scripts": { "dev": "next dev", "build": "next build", "test": "vitest run" },
  "dependencies": {
    "next": "16.0.3",
    "react": "19.2.0",
    "react-dom": "19.2.0",
    "zod": "4.1.12"
  },
  "devDependencies": {
    "typescript": "5.9.3",
    "vitest": "3.2.4",
    "@testing-library/react": "16.3.0"
  }
}
__FIXTURE_EOF__
cat > next.config.ts <<'__FIXTURE_EOF__'
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  cacheComponents: true,
};

export default nextConfig;
__FIXTURE_EOF__
cat > tsconfig.json <<'__FIXTURE_EOF__'
{
  "compilerOptions": {
    "target": "ES2022", "lib": ["dom", "dom.iterable", "esnext"], "strict": true,
    "module": "esnext", "moduleResolution": "bundler", "jsx": "preserve",
    "paths": { "@/*": ["./src/*"] }, "plugins": [{ "name": "next" }]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"]
}
__FIXTURE_EOF__
cat > src/lib/auth.ts <<'__FIXTURE_EOF__'
import 'server-only';
import { cookies } from 'next/headers';

export type Session = { userId: string; email: string };

// Returns the signed-in user, or null.
export async function getSession(): Promise<Session | null> {
  const token = (await cookies()).get('session')?.value;
  if (!token) return null;
  return { userId: token.split('.')[0], email: 'user@example.com' };
}
__FIXTURE_EOF__
cat > src/lib/db.ts <<'__FIXTURE_EOF__'
import 'server-only';

export type Project = { id: string; name: string; ownerId: string };
export type Note = { id: string; projectId: string; authorId: string; body: string; createdAt: Date };

const projects = new Map<string, Project>([['p1', { id: 'p1', name: 'Launch', ownerId: 'u1' }]]);
const notes: Note[] = [];

export async function getProject(id: string): Promise<Project | null> {
  return projects.get(id) ?? null;
}

export async function listNotes(projectId: string): Promise<Note[]> {
  return notes.filter((n) => n.projectId === projectId);
}

export async function addNote(projectId: string, authorId: string, body: string): Promise<Note> {
  const note = { id: crypto.randomUUID(), projectId, authorId, body, createdAt: new Date() };
  notes.push(note);
  return note;
}
__FIXTURE_EOF__
cat > 'src/app/projects/[id]/page.tsx' <<'__FIXTURE_EOF__'
import { notFound } from 'next/navigation';
import { getProject } from '@/lib/db';

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const project = await getProject(id);
  if (!project) notFound();
  return <h1>{project.name}</h1>;
}
__FIXTURE_EOF__
