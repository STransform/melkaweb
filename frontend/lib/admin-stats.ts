import { cache } from 'react';
import type { AdminIdentity } from '../components/AdminShell';

export type AdminStatsPayload = {
  user: AdminIdentity;
  site_title: string;
  counts: Record<string, number>;
  messages: {
    id: number;
    full_name: string;
    email: string;
    phone: string;
    subject: string;
    sent_date: string;
  }[];
};

export const getAdminStats = cache(async (cookie: string): Promise<{ status: number; ok: boolean; data: AdminStatsPayload | null }> => {
  const response = await fetch(`${process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000'}/api/frontend/admin-stats/`, {
    cache: 'no-store',
    redirect: 'manual',
    headers: { cookie },
  });
  return {
    status: response.status,
    ok: response.ok,
    data: response.ok ? await response.json() : null,
  };
});

