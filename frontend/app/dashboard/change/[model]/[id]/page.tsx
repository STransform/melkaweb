import { notFound, redirect } from 'next/navigation';
import { headers } from 'next/headers';
import ModelForm, { FieldDefinition } from '../../../ModelForm';

type Props = {
  params: Promise<{ model: string; id: string }>;
};

type ItemResponse = {
  model?: string;
  title?: string;
  id?: number;
  fields?: FieldDefinition[];
  formFields?: FieldDefinition[];
  csrfToken?: string;
  redirect?: string;
  single?: boolean;
};

async function getItemData(model: string, id: string): Promise<ItemResponse | null> {
  try {
    const incoming = await headers();
    const res = await fetch(`${process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000'}/api/frontend/admin/${model}/${id}/`, {
      cache: 'no-store',
      headers: {
        cookie: incoming.get('cookie') || '',
      },
    });
    if (res.status === 404) return null;
    if (res.status === 302 || res.status === 403) {
      redirect('/accounts/login/?next=' + encodeURIComponent(`/dashboard/change/${model}/${id}/`));
    }
    return await res.json();
  } catch (e) {
    if (e && typeof e === 'object' && 'digest' in e) throw e;
    return null;
  }
}

export default async function ChangePage({ params }: Props) {
  const { model, id } = await params;
  const data = await getItemData(model, id);
  if (!data) notFound();

  if (data.redirect) {
    redirect(data.redirect);
  }

  const fields = data.fields || data.formFields || [];

  return (
    <ModelForm
      key={`${model}-${id}`}
      model={data.model || model}
      title={data.title || model}
      id={data.id ?? Number(id)}
      fields={fields}
      csrfToken={data.csrfToken}
      single={data.single}
    />
  );
}
