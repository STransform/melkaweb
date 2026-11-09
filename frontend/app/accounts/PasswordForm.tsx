'use client';
import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function PasswordForm({ uid, token }: { uid?: string; token?: string }) {
  const router = useRouter();
  const [error, setError] = useState('');
  const [pending, setPending] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setPending(true);
    const body = new FormData(event.currentTarget);
    try {
      const csrf = await fetch('/api/frontend/csrf/').then(response => response.json());
      const endpoint = uid ? `${encodeURIComponent(uid)}/${encodeURIComponent(token || '')}/` : '';
      const response = await fetch(`/api/frontend/auth/password-reset/${endpoint}`, { method: 'POST', headers: { 'X-CSRFToken': csrf.csrfToken }, body });
      const payload = await response.json();
      if (!response.ok) { setError(Object.values(payload.errors || {}).flat().join(' ') || 'Unable to reset password.'); return; }
      router.replace(payload.redirect);
    } catch { setError('Unable to contact the server. Please try again.'); }
    finally { setPending(false); }
  }
  return <main className="container section"><div className="row justify-content-center"><div className="col-md-6"><h1>{uid ? 'Set new password' : 'Reset password'}</h1>{error && <p role="alert" className="text-danger">{error}</p>}<form onSubmit={submit}>{(uid ? [['new_password1', 'New password', 'password'], ['new_password2', 'Confirm new password', 'password']] : [['email', 'Email', 'email']]).map(([name, label, type]) => <div className="form-group mb-3" key={name}><label className="form-label" htmlFor={name}>{label}</label><input className="form-control" id={name} name={name} type={type} autoComplete={uid ? 'new-password' : 'email'} required /></div>)}<button className="btn btn-primary" disabled={pending}>{pending ? 'Submitting…' : uid ? 'Change password' : 'Send reset email'}</button></form><Link href="/accounts/login/">Back to login</Link></div></div></main>;
}
