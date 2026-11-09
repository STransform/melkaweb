'use client';
import { useCallback, useEffect, useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { FieldDefinition } from '../dashboard/ModelForm';

type Task = { id: number; task_name: string; task_description: string; key_tasks: string; status: string; priority: string; assigned_date: string; due_date: string; assigned_to: string[]; monitoring: string[]; can_delete: boolean };
type Comment = { id: number; content: string; user: string; created_at: string; replies: Omit<Comment, 'replies'>[] };
type Data = { tasks?: Task[]; task?: Task; fields: FieldDefinition[]; comments?: Comment[]; can_edit?: boolean };

export default function Tasks({ scope = 'All', id }: { scope?: string; id?: string }) {
  const router = useRouter();
  const [data, setData] = useState<Data>();
  const [error, setError] = useState('');
  const [status, setStatus] = useState('All');
  const [editing, setEditing] = useState(false);
  const [pending, setPending] = useState(false);
  const endpoint = `/api/frontend/tasks/${id ? `detail/${id}` : scope}/`;
  const load = useCallback(async () => {
    const response = await fetch(endpoint, { cache: 'no-store', redirect: 'manual' });
    if (response.status === 302 || response.type === 'opaqueredirect') { router.replace('/accounts/login/'); return; }
    if (!response.ok) throw new Error('Unable to load tasks.');
    setData(await response.json());
  }, [endpoint, router]);
  useEffect(() => { load().catch(reason => setError(reason.message)); }, [load]);
  async function mutate(url: string, body?: FormData, method = 'POST') {
    setPending(true); setError('');
    try {
      const csrfResponse = await fetch('/api/frontend/csrf/', { cache: 'no-store' });
      const { csrfToken } = await csrfResponse.json();
      const response = await fetch(url, { method, body, headers: { 'X-CSRFToken': csrfToken } });
      const result = await response.json();
      if (!response.ok) throw new Error(Object.values(result.errors || {}).flat().join(' ') || 'Unable to save.');
      setEditing(false); await load(); return true;
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Request failed.'); return false; }
    finally { setPending(false); }
  }
  async function submit(event: FormEvent<HTMLFormElement>, url: string) {
    event.preventDefault(); const form = event.currentTarget;
    if (await mutate(url, new FormData(form))) form.reset();
  }
  async function remove(task: Task) {
    if (confirm('Are you sure you want to delete this task?')) {
      await mutate(`/api/frontend/tasks/detail/${task.id}/`, undefined, 'DELETE');
    }
  }
  const rows = data?.tasks?.filter(task => status === 'All' || task.status === status) || [];
  return <>
    <div className="d-md-flex d-block align-items-center justify-content-between my-4 page-header-breadcrumb"><h1 className="page-title fw-semibold fs-18 mb-0">{data?.task?.task_name || `${scope} Tasks List`}</h1><nav className="d-flex gap-3">{['All', 'Assigned', 'Monitoring', 'My'].map(value => <Link key={value} href={`/taskmanager/task_view/${value}/`}>{value} Tasks</Link>)}</nav></div>
    {error && <div className="alert alert-danger" role="alert">{error}</div>}
    {data?.tasks?.some(task => task.can_delete) && <details className="mb-3"><summary>Delete a task</summary><div className="d-flex flex-wrap gap-2 mt-2">{data.tasks.filter(task => task.can_delete).map(task => <button key={task.id} className="btn btn-sm btn-danger" disabled={pending} onClick={() => remove(task)}>{task.task_name} <i className="bx bx-trash" /></button>)}</div></details>}
    {!data && !error && <p role="status">Loading tasks…</p>}
    {data && <div className="card custom-card"><div className="card-header justify-content-between"><div className="card-title">{id ? 'Task Details' : 'Total Tasks'}</div>{(!id || data.can_edit) && <button className="btn btn-sm btn-primary" onClick={() => setEditing(true)}>{id ? 'Edit Task' : 'Create Task'}</button>}</div>
      <div className="card-body">{data.task ? <><p>{data.task.task_description}</p><h6>Key Tasks</h6><ul>{data.task.key_tasks.split('\n').filter(Boolean).map((value, index) => <li key={index}>{value}</li>)}</ul><p>Status: {data.task.status} · Priority: {data.task.priority}</p><p>Assigned To: {data.task.assigned_to.join(', ')}</p><p>Monitored by: {data.task.monitoring.join(', ')}</p><p>Due Date: {data.task.due_date}</p></> : <><ul className="nav nav-tabs mb-3 nav-style-1">{['All', 'New', 'Inprogress', 'Completed', 'Overdue'].map(value => <li className="nav-item" key={value}><button className={`nav-link ${status === value ? 'active' : ''}`} onClick={() => setStatus(value)}>{value} ({data.tasks?.filter(task => value === 'All' || task.status === value).length})</button></li>)}</ul><div className="table-responsive"><table className="table text-nowrap table-bordered"><thead><tr>{['#', 'Task', 'Assigned Date', 'Due Date', 'Status', 'Priority', 'Action'].map(value => <th key={value}>{value}</th>)}</tr></thead><tbody>{rows.map((task, index) => <tr key={task.id}><td>{index + 1}</td><td><Link href={`/taskmanager/task_details/${task.id}/`}>{task.task_name}</Link></td><td>{task.assigned_date}</td><td>{task.due_date}</td><td>{task.status}</td><td><span className="badge bg-success-transparent">{task.priority}</span></td><td><Link aria-label="Task details" href={`/taskmanager/task_details/${task.id}/`}><i className="bx bx-edit" /></Link></td></tr>)}</tbody></table></div></>}</div></div>}
    {editing && data && <div className="modal d-block" role="dialog" aria-modal="true" aria-label={id ? 'Edit Task' : 'Add Task'} style={{ background: '#0006', overflowY: 'auto' }}><div className="modal-dialog modal-lg modal-dialog-centered"><div className="modal-content"><div className="modal-header"><h6 className="modal-title">{id ? 'Edit Task' : 'Add Task'}</h6><button className="btn-close" aria-label="Close" onClick={() => setEditing(false)} /></div><form onSubmit={event => submit(event, endpoint)}><div className="modal-body px-4"><div className="row gy-2">{data.fields.map(field => <div className="col-md-6" key={field.name}><label className="form-label" htmlFor={field.id}>{field.label}</label>{field.choices.length ? <select className="form-control" id={field.id} name={field.name} multiple={field.multiple} required={field.required} defaultValue={field.multiple ? (Array.isArray(field.value) ? field.value.map(String) : []) : String(field.value ?? '')}>{field.choices.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select> : field.textarea ? <textarea className="form-control" id={field.id} name={field.name} defaultValue={String(field.value ?? '')} /> : <input className="form-control" id={field.id} name={field.name} type={field.type} required={field.required} defaultValue={String(field.value ?? '')} />}</div>)}</div></div><div className="modal-footer"><button className="btn btn-light" type="button" onClick={() => setEditing(false)}>Cancel</button><button className="btn btn-primary" disabled={pending}>{id ? 'Update Task' : 'Add Task'}</button></div></form></div></div></div>}
    {data?.task && <div className="card custom-card"><div className="card-header"><div className="card-title">Comments</div></div><div className="card-body">{data.comments?.map(comment => <article className="mb-4" key={comment.id}><p>{comment.content}</p><small>{comment.user} · {comment.created_at}</small><div className="ms-4">{comment.replies.map(reply => <p key={reply.id}>{reply.content} <small className="text-muted">{reply.user}</small></p>)}</div><details><summary>Reply</summary><form className="input-group mt-2" onSubmit={event => submit(event, `/api/frontend/tasks/${id}/comments/${comment.id}/`)}><input name="comment_content" className="form-control" required placeholder="Write a reply…" /><button className="btn btn-primary" disabled={pending}>Reply</button></form></details></article>)}</div><div className="card-footer"><form className="input-group" onSubmit={event => submit(event, `/api/frontend/tasks/${id}/comments/`)}><input name="comment_content" className="form-control" required placeholder="Write a comment..." /><button className="btn btn-primary" disabled={pending}>Post</button></form></div></div>}
  </>;
}
