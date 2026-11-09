'use client';
import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

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
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [pending, setPending] = useState(false);
  const editing = id != null;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setErrors({});
    const response = await fetch(`/api/frontend/admin/${model}/${editing ? `${id}/` : ''}`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken || '' },
      body: new FormData(event.currentTarget),
    });
    const payload = await response.json();
    if (response.ok) {
      if (single) {
        router.push('/dashboard/');
      } else {
        router.push(`/dashboard/list/${model}/`);
      }
      router.refresh();
    } else {
      setErrors(payload.errors || {});
    }
    setPending(false);
  }

  const cancelHref = single ? '/dashboard/' : `/dashboard/list/${model}/`;

  return (
    <div className="row">
      <div className="col-xl-12">
        <div className="d-md-flex d-block align-items-center justify-content-between my-4 page-header-breadcrumb">
          <h1 className="page-title fw-semibold fs-18 mb-0">
            {editing ? 'Update' : 'Add New'} {title}
          </h1>
          <strong>N.B. Please note that all fields ending with * are mandatory and should be filled.</strong>
        </div>
        <form onSubmit={submit} encType="multipart/form-data">
          <div className="card custom-card">
            <div className="card-body col-md-8 col-sm-12">
              {fields.map((field, index) => {
                const value = field.value == null ? '' : String(field.value);
                const error = errors[field.name]?.[0] || field.errors?.[0];
                const isBool = field.type === 'checkbox';
                const isChecked = value.toLowerCase() === 'true' || value === '1';

                return (
                  <div key={field.name} className="form-group mt-2 mb-4" style={{ paddingLeft: '2.5em' }}>
                    <label htmlFor={field.id} className="form-label">
                      {index + 1}. {field.label}
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
              <button type="submit" disabled={pending} className="btn btn-success float-end m-2">
                {pending ? 'Saving...' : 'Save'}
              </button>
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
