import type { ReactNode } from 'react';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import AdminShell from '../../components/AdminShell';
import { getAdminStats } from '../../lib/admin-stats';

export default async function AdminLayout({ children }: { children: ReactNode }) {
  const incoming = await headers();
  const result = await getAdminStats(incoming.get('cookie') || '');
  if (result.status === 302 || result.status === 401) redirect('/accounts/login/');
  if (!result.ok || !result.data) throw new Error('Unable to load administrator session.');
  return <AdminShell user={result.data.user} title={result.data.site_title}>{children}</AdminShell>;
}
