import type { ReactNode } from 'react';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import AdminShell, { type AdminIdentity } from '../../components/AdminShell';

export default async function AdminLayout({ children }: { children: ReactNode }) {
  const incoming = await headers();
  const response = await fetch(`${process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000'}/api/frontend/admin-stats/`, { cache: 'no-store', redirect: 'manual', headers: { cookie: incoming.get('cookie') || '' } });
  if (response.status === 302 || response.status === 401) redirect('/accounts/login/');
  if (!response.ok) throw new Error('Unable to load administrator session.');
  const data: { user: AdminIdentity; site_title: string } = await response.json();
  return <AdminShell user={data.user} title={data.site_title}>{children}</AdminShell>;
}
