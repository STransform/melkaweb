'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export const dynamic = 'force-dynamic';

export default function LogoutPage() {
  const router = useRouter();
  useEffect(() => {
    async function signOut() {
      const csrf = await fetch('/api/frontend/csrf/').then(response => response.json());
      const response = await fetch('/api/frontend/auth/logout/', {
        method: 'POST', headers: { 'X-CSRFToken': csrf.csrfToken || '' },
      });
      const payload = await response.json();
      router.replace(payload.redirect || '/'); router.refresh();
    }
    signOut().catch(() => router.replace('/'));
  }, [router]);
  return <main className="container section"><p>Signing out…</p></main>;
}
