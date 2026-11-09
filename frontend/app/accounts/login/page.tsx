'use client';

import { useState, useEffect, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';

export const dynamic = 'force-dynamic';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [csrfToken, setCsrfToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    fetch('/api/frontend/csrf/')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.csrfToken) {
          setCsrfToken(data.csrfToken);
        }
      })
      .catch(() => {});
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(''); setLoading(true);
    try {
      const body = new FormData(event.currentTarget);
      const csrf = await fetch('/api/frontend/csrf/', { cache: 'no-store' }).then(response => response.json());
      body.set('csrfmiddlewaretoken', csrf.csrfToken);
      const response = await fetch('/api/frontend/auth/login/', {
        method: 'POST', headers: { 'X-CSRFToken': csrf.csrfToken }, body,
      });
      const payload = await response.json();
      if (!response.ok) {
        setError(Object.values(payload.errors || {}).flat().join(' ') || 'Unable to sign in.');
        return;
      }
      router.replace(payload.redirect || '/'); router.refresh();
    } catch { setError('Unable to contact the server. Please try again.'); }
    finally { setLoading(false); }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      fontFamily: 'Inter, system-ui, sans-serif',
      padding: '20px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '420px',
        background: 'white',
        borderRadius: '16px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
        padding: '36px',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <Link href="/" style={{ textDecoration: 'none', color: '#0f172a' }}>
            <span style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
              Melka<span style={{ color: '#0284c7' }}>Tech</span>
            </span>
          </Link>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '14px 0 4px', color: '#1e293b' }}>
            Sign In to Portal
          </h2>
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>
            Enter your credentials to access the administration dashboard.
          </p>
        </div>

        {error && (
          <div style={{
            background: '#fee2e2',
            color: '#dc2626',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            marginBottom: '20px',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
          <input type="hidden" name="next" value={params.get('next') || ''} />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label htmlFor="id_email" style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
              Email address
            </label>
            <input
              id="id_email"
              name="email"
              type="email"
              required
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@example.com"
              style={{
                padding: '11px 14px',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                fontSize: '0.95rem',
                outline: 'none',
              }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="id_password" style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                Password
              </label>
              <Link href="/accounts/reset_password/" style={{ fontSize: '0.8rem', color: '#0284c7', textDecoration: 'none' }}>
                Forgot password?
              </Link>
            </div>
            <input
              id="id_password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                padding: '11px 14px',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                fontSize: '0.95rem',
                outline: 'none',
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: '6px',
              padding: '12px',
              background: '#0284c7',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '0.95rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background 0.15s',
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '24px', paddingTop: '18px', borderTop: '1px solid #f1f5f9', fontSize: '0.85rem', color: '#64748b' }}>
          Back to{' '}
          <Link href="/" style={{ color: '#0284c7', textDecoration: 'none', fontWeight: 600 }}>
            Public Homepage
          </Link>
        </div>
      </div>
    </div>
  );
}
