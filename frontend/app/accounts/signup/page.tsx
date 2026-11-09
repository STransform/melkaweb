'use client';

import { FormEvent, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export const dynamic = 'force-dynamic';

const fieldStyle = { padding: '11px 14px', border: '1px solid #cbd5e1', borderRadius: '8px', fontSize: '0.95rem' };

export default function SignupPage() {
  const router = useRouter();
  const [csrfToken, setCsrfToken] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [message, setMessage] = useState('');
  const [pending, setPending] = useState(false);
  useEffect(() => { fetch('/api/frontend/csrf/').then(response => response.json()).then(data => setCsrfToken(data.csrfToken || '')).catch(() => {}); }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setErrors({}); setMessage(''); setPending(true);
    try {
      const response = await fetch('/api/frontend/auth/signup/', {
        method: 'POST', headers: { 'X-CSRFToken': csrfToken }, body: new FormData(event.currentTarget),
      });
      const data = await response.json();
      if (!response.ok) { setErrors(data.errors || {}); return; }
      setMessage(data.message || 'Account created.');
      router.replace('/accounts/login/');
    } catch { setMessage('Unable to contact the server. Please try again.'); }
    finally { setPending(false); }
  }
  const error = (name: string) => errors[name]?.join(' ');
  return <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: '24px', background: '#f1f5f9' }}>
    <form onSubmit={submit} style={{ width: 'min(100%, 520px)', background: 'white', borderRadius: '14px', boxShadow: '0 14px 36px #0f172a1a', padding: '36px', display: 'grid', gap: '16px' }}>
      <div><Link href="/" style={{ color: '#0284c7', fontWeight: 800, textDecoration: 'none' }}>MelkaTech</Link><h1 style={{ fontSize: '1.6rem', margin: '10px 0 4px' }}>Create account</h1><p style={{ color: '#64748b', margin: 0 }}>Register a portal account.</p></div>
      {message && <p role="status" style={{ color: '#b45309', margin: 0 }}>{message}</p>}
      {[['email', 'Email address', 'email'], ['first_name', 'First name', 'text'], ['last_name', 'Last name', 'text'], ['password', 'Password', 'password'], ['password2', 'Confirm password', 'password']].map(([name, label, type]) => <label key={name} style={{ display: 'grid', gap: '6px', fontWeight: 600, fontSize: '.9rem' }}>{label}<input name={name} type={type} required style={fieldStyle} autoComplete={name.includes('password') ? 'new-password' : undefined}/>{error(name) && <span style={{ color: '#b91c1c', fontWeight: 400 }}>{error(name)}</span>}</label>)}
      <label style={{ display: 'grid', gap: '6px', fontWeight: 600, fontSize: '.9rem' }}>Role<select name="role" defaultValue="staff" style={fieldStyle}><option value="staff">Staff</option><option value="teamleader">Team Leader</option><option value="admin">Admin</option></select>{error('role') && <span style={{ color: '#b91c1c', fontWeight: 400 }}>{error('role')}</span>}</label>
      <button disabled={pending} style={{ padding: '12px', border: 0, borderRadius: '8px', background: '#0284c7', color: 'white', fontWeight: 700, cursor: 'pointer' }}>{pending ? 'Creating…' : 'Create account'}</button>
      <p style={{ margin: 0, textAlign: 'center', color: '#64748b' }}>Already have an account? <Link href="/accounts/login/" style={{ color: '#0284c7' }}>Sign in</Link></p>
    </form>
  </main>;
}
