'use client';
import { useEffect, useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { FieldDefinition } from '../app/dashboard/ModelForm';

type User = { id: number; email: string; first_name: string; last_name: string; role: string; status: string; is_active: boolean };
type Account = { fields: FieldDefinition[]; own?: boolean; name?: string; title?: string; items?: User[] };
export default function AccountPortal({ id, create = false }: { id?: string; create?: boolean }) {
  const router = useRouter();
  const [data, setData] = useState<Account>();
  const [message, setMessage] = useState('');
  const [pending, setPending] = useState(false);
  const endpoint = id ? `/api/frontend/accounts/profile/${id}/` : `/api/frontend/accounts/users/${create ? '?mode=create' : ''}`;
  useEffect(() => {
    fetch(endpoint, { redirect: 'manual', cache: 'no-store' }).then(async response => {
      if (response.type === 'opaqueredirect' || response.status === 302) { router.replace('/accounts/login/'); return; }
      if (!response.ok) throw new Error(response.status === 403 ? 'Permission denied.' : 'Unable to load account.');
      setData(await response.json());
    }).catch(error => setMessage(error.message));
  }, [endpoint, router]);
  async function submit(event: FormEvent<HTMLFormElement>, password = false) {
    event.preventDefault(); setMessage(''); setPending(true);
    const body = new FormData(event.currentTarget);
    try {
      const { csrfToken } = await fetch('/api/frontend/csrf/').then(response => response.json());
      const response = await fetch(password ? `/api/frontend/accounts/password/${id}/` : endpoint, { method: 'POST', body, headers: { 'X-CSRFToken': csrfToken } });
      const payload = await response.json();
      if (!response.ok) throw new Error(Object.values(payload.errors || {}).flat().join(' ') || payload.detail || 'Unable to save.');
      if (payload.redirect) { router.push(payload.redirect); router.refresh(); }
      else if (create) router.push('/accounts/users_list/');
      else setMessage('Profile updated successfully.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Unable to save.'); }
    finally { setPending(false); }
  }
  return <><div className="my-4 page-header-breadcrumb"><h1 className="page-title fw-semibold fs-18 mb-0">{create ? 'Add User' : id ? data?.title || 'Profile' : 'Users'}</h1></div>{message && <p role="status" className="alert alert-info">{message}</p>}{!data && !message && <p>Loading…</p>}{data && <>
    {!id && !create ? <div className="card custom-card"><div className="card-header justify-content-between"><div className="card-title">Users List</div><Link className="btn btn-primary" href="/accounts/Add_user/">Add User</Link></div><div className="card-body table-responsive"><table className="table table-bordered text-nowrap"><thead><tr>{['#', 'Email', 'First name', 'Last name', 'Role', 'Status', 'Action'].map(label => <th key={label}>{label}</th>)}</tr></thead><tbody>{data.items?.map((user, index) => <tr key={user.id}><td>{index + 1}</td><td>{user.email}</td><td>{user.first_name}</td><td>{user.last_name}</td><td>{user.role}</td><td>{user.status}</td><td><Link href={`/accounts/profile/${user.id}/`} aria-label="Edit user"><i className="bx bx-edit" /></Link></td></tr>)}</tbody></table></div></div> : <div className="card custom-card"><div className="card-header"><div className="card-title">{data.name || 'User Information'}</div></div><form onSubmit={event => submit(event)}><div className="card-body row gy-3">{data.fields.map(field => <div className="col-md-6" key={field.name}><label htmlFor={field.id} className="form-label">{field.label}</label>{field.choices.length ? <select id={field.id} name={field.name} className="form-control" multiple={field.multiple} defaultValue={field.multiple ? (Array.isArray(field.value) ? field.value.map(String) : []) : String(field.value ?? '')}>{field.choices.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select> : field.type === 'checkbox' ? <input className="form-check-input" id={field.id} name={field.name} type="checkbox" defaultChecked={field.value === true} /> : <input className="form-control" id={field.id} name={field.name} type={field.type} defaultValue={field.type === 'file' || field.type === 'password' ? undefined : String(field.value ?? '')} />}</div>)}</div><div className="card-footer"><button className="btn btn-success" disabled={pending}>Save</button></div></form></div>}
    {id && <div className="card custom-card"><div className="card-header"><div className="card-title">{data.own ? 'Change Password' : 'Reset Password'}</div></div><form onSubmit={event => submit(event, true)}><div className="card-body">{(data.own ? ['current_password', 'new_password', 'retype_new_password'] : ['new_password', 'retype_new_password']).map(name => <div className="mb-3" key={name}><label htmlFor={name} className="form-label">{name.replaceAll('_', ' ')}</label><input type="password" id={name} name={name} className="form-control" required autoComplete={name === 'current_password' ? 'current-password' : 'new-password'} /></div>)}</div><div className="card-footer"><button className="btn btn-success" disabled={pending}>Change Password</button></div></form></div>}
  </>}</>;
}
