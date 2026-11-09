'use client';
import { useEffect, useRef, useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import TutorialEditor from '../../components/TutorialEditor';

export type FieldDefinition = {
  name: string;
  id: string;
  label: string;
  helpText: string;
  required: boolean;
  type: string;
  textarea: boolean;
  multiple: boolean;
  disabled?: boolean;
  choices: [string, string][];
  value: unknown;
  errors: string[];
};

export default function ModelForm({
  model,
  title,
  id,
  fields,
  csrfToken,
  single,
}: {
  model: string;
  title: string;
  id?: number;
  fields: FieldDefinition[];
  csrfToken?: string;
  single?: boolean;
}) {
  const router = useRouter();
  const params = useSearchParams();
  const publishIntent = useRef<'Published' | 'Hold'>('Hold');
  const errorSummary = useRef<HTMLDivElement>(null);
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [pending, setPending] = useState(false);
  const [showTranslations, setShowTranslations] = useState(false);
  const editing = id != null;
  const saved = params.get('saved');
  useEffect(() => {
    if (!Object.keys(errors).length) return;
    if (Object.keys(errors).some(name => /_(ax|ox)$/.test(name))) setShowTranslations(true);
    errorSummary.current?.focus();
    errorSummary.current?.scrollIntoView({block:'center'});
  }, [errors]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    if (event.currentTarget.querySelector('.tutorial-editor[data-uploading="true"]')) {
      setErrors({'__all__':['Please wait for the screenshot upload to finish before saving.']});
      return;
    }
    setPending(true);
    setErrors({});
    try {
    const body = new FormData(event.currentTarget);
    const action = (event.nativeEvent as SubmitEvent).submitter?.getAttribute('value') || publishIntent.current;
    if (model === 'Blog' && (action === 'Hold' || action === 'Published')) {
      body.set('publish_action', action);
      body.set('published_status', action);
    }
    const freshToken = await fetch('/api/frontend/csrf/', {cache:'no-store',signal:AbortSignal.timeout(15000)}).then(r => r.json());
    const response = await fetch(`/api/frontend/admin/${model}/${editing ? `${id}/` : ''}`, {
      method: 'POST',
      headers: { 'X-CSRFToken': freshToken.csrfToken || csrfToken || '' },
      body,
      signal: AbortSignal.timeout(30000),
    });
    const payload = await response.json();
    if (response.ok) {
      if (model === 'Blog') fields.filter(field=>field.name.startsWith('content_')).forEach(field=>{try{localStorage.removeItem(`melka-blog-${id || 'new'}-${field.name}`);}catch{/* Storage may be disabled. */}});
      if (model === 'Blog' && payload.id) {
        window.location.assign(`/dashboard/change/Blog/${payload.id}/?saved=${encodeURIComponent(payload.published_status || action)}`);
        return;
      }
      if (single && payload.id) {
        router.push(`/dashboard/change/${model}/${payload.id}/`);
      } else if (single) {
        router.push('/dashboard/');
      } else {
        router.push(`/dashboard/list/${model}/`);
      }
      router.refresh();
    } else {
      setErrors(payload.errors || {'__all__':[payload.detail || 'Unable to save. Please check your permissions and try again.']});
    }
    } catch { setErrors({'__all__':['Unable to save. Please try again. Your writing is still here.']}); }
    finally { setPending(false); }
  }

  const cancelHref = single ? '/dashboard/' : `/dashboard/list/${model}/`;

  return (
    <div className="row">
      {model === 'Blog' && <link rel="stylesheet" href="/static/front/css/tutorials.css" />}
      {model === 'Blog' && <link rel="stylesheet" href="/static/front/css/tutorial-code.css" />}
      <div className="col-xl-12">
        <div className="d-md-flex d-block align-items-center justify-content-between my-4 page-header-breadcrumb">
          <h1 className="page-title fw-semibold fs-18 mb-0">
            {editing ? 'Update' : 'Add New'} {title}
          </h1>
          {model === 'Blog' ? <button type="button" className="btn btn-light" aria-pressed={showTranslations} onClick={()=>setShowTranslations(value=>!value)}>{showTranslations?'Hide translations':'Show Amharic / Afaan Oromoo fields'}</button> : <strong>N.B. Please note that all fields ending with * are mandatory and should be filled.</strong>}
        </div>
        {model === 'Blog' && <p className="text-muted">Your tutorial workspace. Drafts stay private until you publish. Start with a clear title, a short summary, and one useful lesson.</p>}
        {model === 'Blog' && editing && saved && <div className="alert alert-success" role="status">{saved === 'Published' ? <>Tutorial published successfully. <a className="fw-semibold text-decoration-underline" href={`/blogs/blogs/${id}/`} target="_blank" rel="noreferrer">Open on the public portal ↗</a></> : 'Draft saved. It will remain private until you publish it.'}</div>}
        <form onSubmit={submit} noValidate={model === 'Blog'} encType="multipart/form-data" aria-busy={pending}>
          {Object.keys(errors).length > 0 && <div ref={errorSummary} tabIndex={-1} className="alert alert-danger" role="alert"><strong>Nothing was saved. Please fix the following:</strong><ul className="mb-0">{Object.entries(errors).map(([name,messages]) => <li key={name}>{name === '__all__' ? '' : `${fields.find(field=>field.name===name)?.label.replace(/\s*\*$/, '') || name}: `}{messages.join(' ')}</li>)}</ul></div>}
          <div className="card custom-card">
            <div className={`card-body ${model === 'Blog' ? 'col-lg-10 mx-auto' : 'col-md-8'} col-sm-12`}>
              {fields.map((field, index) => {
                if (model === 'Blog' && field.name === 'published_status') return <input key={field.name} type="hidden" name={field.name} value={String(field.value || 'Hold')} />;
                const value = field.value == null ? '' : String(field.value);
                const error = errors[field.name]?.[0] || field.errors?.[0];
                const isBool = field.type === 'checkbox';
                const isChecked = value.toLowerCase() === 'true' || value === '1';

                return (
                  <div key={field.name} className="form-group mt-2 mb-4" hidden={model === 'Blog' && /_(ax|ox)$/.test(field.name) && !showTranslations} style={{ paddingLeft: model === 'Blog' ? 0 : '2.5em' }}>
                    <label htmlFor={field.id} className="form-label">
                      {model === 'Blog' ? '' : `${index + 1}. `}{field.label}
                    </label>
                    {isBool ? (
                      <div className="form-check form-switch" style={{ display: 'inline-flex', marginLeft: '1rem' }}>
                        <input
                          id={field.id}
                          name={field.name}
                          type="checkbox"
                          className="form-check-input"
                          defaultChecked={isChecked}
                        />
                      </div>
                    ) : field.choices && field.choices.length > 0 ? (
                      <select
                        id={field.id}
                        name={field.name}
                        className="form-control"
                        defaultValue={value}
                        multiple={field.multiple}
                      >
                        {!field.required && <option value="">---------</option>}
                        {field.choices.map(([key, label]) => (
                          <option key={key} value={key}>{label}</option>
                        ))}
                      </select>
                    ) : model === 'Blog' && /^content(?:_|$)/.test(field.name) ? (
                      <TutorialEditor name={field.name} id={field.id} initial={value} required={field.required} draftKey={`melka-blog-${id || 'new'}-${field.name}`} />
                    ) : field.textarea ? (
                      <textarea
                        id={field.id}
                        name={field.name}
                        className="form-control"
                        rows={5}
                        defaultValue={value}
                      />
                    ) : (
                      <input
                        id={field.id}
                        name={field.name}
                        type={field.type || 'text'}
                        className="form-control"
                        defaultValue={field.type === 'file' ? undefined : value}
                        required={field.required && field.type !== 'file'}
                      />
                    )}
                    {field.type === 'file' && typeof field.value === 'string' && field.value && (
                      <div style={{ marginTop: '8px' }}>
                        {/\.(png|jpe?g|webp|gif|svg)$/i.test(field.value) && (
                          <img
                            src={field.value}
                            alt={field.label}
                            style={{
                              maxWidth: 220,
                              maxHeight: 140,
                              objectFit: 'cover',
                              borderRadius: 8,
                              border: '1px solid #cbd5e1',
                              display: 'block',
                              marginBottom: 6,
                            }}
                          />
                        )}
                        <a href={field.value} target="_blank" rel="noreferrer" style={{ fontSize: '0.85rem' }}>
                          Current uploaded file: {field.value.split('/').pop()}
                        </a>
                      </div>
                    )}
                    {error && (
                      <ul className="errorlist">
                        <li>{error}</li>
                      </ul>
                    )}
                    {field.helpText && (
                      <small className="fw-semibold mb-1 text-muted" style={{ display: 'block', marginTop: 4 }}>
                        {field.helpText}
                      </small>
                    )}
                  </div>
                );
              })}
            </div>
            <div className="card-footer px-5">
              {model === 'Blog' && <><button type="submit" name="publish_action" value="Published" onClick={()=>{publishIntent.current='Published';}} disabled={pending} className="btn btn-primary float-end m-2">{pending && publishIntent.current==='Published'?'Publishing…':'Publish tutorial'}</button><button type="submit" name="publish_action" value="Hold" onClick={()=>{publishIntent.current='Hold';}} disabled={pending} className="btn btn-outline-primary float-end m-2">{pending && publishIntent.current==='Hold'?'Saving…':'Save draft'}</button>{editing && fields.find(field=>field.name==='published_status')?.value==='Published' && <a href={`/blogs/blogs/${id}/`} className="btn btn-light float-end m-2" target="_blank" rel="noreferrer">View published tutorial ↗</a>}</>}
              {model !== 'Blog' &&
              <button type="submit" disabled={pending} className="btn btn-success float-end m-2">
                {pending ? 'Saving...' : 'Save'}
              </button>}
              <Link className="btn btn-light btn-outline float-end m-2" href={cancelHref}>
                Cancel
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
