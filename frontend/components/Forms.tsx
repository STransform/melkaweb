'use client';
import { useState, type FormEvent } from 'react';

export default function ContentForm({ locale, blogId, labels = {} }: { locale: string; blogId?: number; labels?: Record<string, string> }) {
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const prefix = locale === 'en' ? '' : `/${locale}`;
  const t = (label: string) => labels[label] || label;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setPending(true); setMessage(''); setErrors({});
    try {
      const csrfResponse = await fetch(`${prefix}/api/frontend/csrf/`, { cache: 'no-store' });
      if (!csrfResponse.ok) throw new Error('Unable to prepare the form. Please retry.');
      const { csrfToken } = await csrfResponse.json();
      const endpoint = blogId ? `blogs/${blogId}/comments/` : 'contact/';
      const response = await fetch(`${prefix}/api/frontend/${endpoint}`, {
        method: 'POST', headers: { 'X-CSRFToken': csrfToken }, body: new FormData(form),
      });
      if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('Unable to submit the form. Refresh and try again.');
      const result = await response.json();
      if (!response.ok) { setErrors(result.errors || {}); throw new Error('Please check the form and try again.'); }
      setMessage(result.message); form.reset();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Please try again.'); }
    finally { setPending(false); }
  }
  const fields = blogId
    ? [['author', 'Your name'], ['email', 'Email'], ['message', 'Message']]
    : [['full_name', 'Your name'], ['email', 'Email'], ['phone', 'Phone'], ['subject', 'Subject'], ['message', 'Message']];
  return <form className="content-form" onSubmit={submit}>
    {fields.map(([name, label]) => <label key={name} htmlFor={name}>{t(label)}
      {name === 'message' ? <textarea id={name} name={name} rows={6} required aria-invalid={!!errors[name]} aria-describedby={errors[name] ? `${name}-error` : undefined} /> :
        <input id={name} name={name} type={name === 'email' ? 'email' : name === 'phone' ? 'tel' : 'text'} required maxLength={name === 'subject' ? 300 : name === 'email' ? 254 : 100} pattern={name === 'phone' ? '[+]?[0-9 ]+' : undefined} aria-invalid={!!errors[name]} aria-describedby={errors[name] ? `${name}-error` : undefined} />}
      {errors[name] && <span id={`${name}-error`} className="field-error">{errors[name].join(' ')}</span>}
    </label>)}
    <button className="button" disabled={pending}>{pending ? 'Sending…' : blogId ? 'Post comment' : t('Send message')}</button>
    <p role="status" aria-live="polite">{message}</p>
  </form>;
}
