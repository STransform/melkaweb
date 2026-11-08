import 'server-only';
import { headers } from 'next/headers';
import sanitizeHtml from 'sanitize-html';

export type Item = { id: number; [key: string]: unknown };
export type Site = {
  settings: Record<string, string> | null;
  pages: Record<string, boolean> | null;
  contacts: Array<Record<string, string>>;
  quick_links: Array<{ id: number; title: string; url: string }>;
  user: { authenticated: boolean; staff: boolean; name: string };
  labels: Record<string, string>;
};
export async function api<T>(path: string, locale = 'en'): Promise<T> {
  const incoming = await headers();
  const prefix = locale === 'en' ? '' : `/${locale}`;
  const response = await fetch(`${process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000'}${prefix}/api/frontend/${path}`, {
    cache: 'no-store',
    headers: { cookie: incoming.get('cookie') || '', 'accept-language': locale,
      'user-agent': incoming.get('user-agent') || 'MelkaNext' },
    signal: AbortSignal.timeout(15000),
  });
  if (response.status === 404) throw new ContentNotFound();
  if (!response.ok) throw new Error(`Django API returned ${response.status}`);
  return response.json();
}
export class ContentNotFound extends Error {}
export const text = (value: unknown) => typeof value === 'string' ? value : value == null ? '' : String(value);
export function cleanHtml(value: unknown) {
  return sanitizeHtml(text(value), {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img']),
    allowedAttributes: { ...sanitizeHtml.defaults.allowedAttributes, img: ['src', 'alt', 'width', 'height', 'loading'] },
    allowedSchemes: ['http', 'https', 'mailto', 'tel'],
  });
}
export function safeUrl(value: unknown): string | undefined {
  const url = text(value).trim();
  return /^(https?:\/\/|mailto:|tel:|\/(?!\/)|#)/i.test(url) ? url : undefined;
}
export function embedUrl(value: unknown): string | undefined {
  const raw = text(value);
  const candidate = raw.match(/src=["']([^"']+)["']/)?.[1] || raw;
  try {
    const url = new URL(candidate);
    if (url.protocol !== 'https:') return undefined;
    if (['www.youtube.com', 'www.youtube-nocookie.com', 'player.vimeo.com'].includes(url.hostname)) return url.href;
    if (['maps.google.com', 'www.google.com'].includes(url.hostname) && url.pathname.startsWith('/maps')) return url.href;
  } catch {}
  return undefined;
}
