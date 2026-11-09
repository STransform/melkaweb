import { notFound, redirect } from 'next/navigation';
import { headers } from 'next/headers';
import ModelForm, { FieldDefinition } from '../../ModelForm';

type Props = {
  params: Promise<{ model: string }>;
};

type SchemaResponse = {
  model: string;
  title: string;
  formFields?: FieldDefinition[];
  csrfToken?: string;
};

async function getSchema(model: string): Promise<SchemaResponse | null> {
  try {
    const incoming = await headers();
    const res = await fetch(`${process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000'}/api/frontend/admin/${model}/`, {
      cache: 'no-store',
      headers: {
        cookie: incoming.get('cookie') || '',
      },
    });
    if (res.status === 404) return null;
    if (res.status === 302 || res.status === 403) {
      redirect('/accounts/login/?next=' + encodeURIComponent(`/dashboard/create/${model}/`));
    }
    return await res.json();
  } catch (e) {
    if (e && typeof e === 'object' && 'digest' in e) throw e;
    return null;
  }
}

export default async function CreatePage({ params }: Props) {
  const { model } = await params;
  const data = await getSchema(model);
  if (!data) notFound();

  return (
    <ModelForm
      model={data.model}
      title={data.title}
      fields={data.formFields || []}
      csrfToken={data.csrfToken}
    />
  );
}
