import { redirect, notFound } from 'next/navigation';
import { headers } from 'next/headers';
import DataTable from './DataTable';

type Props = {
  params: Promise<{ model: string }>;
};

type ModelResponse = {
  model: string;
  title: string;
  fields: string[];
  items: Array<{ id: number; [key: string]: unknown }>;
  csrfToken?: string;
  redirect?: string;
};

async function getModelData(modelName: string): Promise<ModelResponse | null> {
  try {
    const incoming = await headers();
    const res = await fetch(`${process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000'}/api/frontend/admin/${modelName}/`, {
      cache: 'no-store',
      headers: {
        cookie: incoming.get('cookie') || '',
      },
    });
    if (res.status === 404) return null;
    if (res.status === 302 || res.status === 403) {
      redirect('/accounts/login/?next=' + encodeURIComponent(`/dashboard/list/${modelName}/`));
    }
    return await res.json();
  } catch (e) {
    if (e && typeof e === 'object' && 'digest' in e) throw e;
    return null;
  }
}

export default async function ModelListPage({ params }: Props) {
  const { model } = await params;
  const data = await getModelData(model);
  if (!data) notFound();

  if (data.redirect) {
    redirect(data.redirect);
  }

  return (
    <DataTable
      model={data.model}
      title={data.title}
      fields={data.fields}
      initialItems={data.items}
      csrfToken={data.csrfToken}
    />
  );
}
