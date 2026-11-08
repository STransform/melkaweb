import { NextRequest } from 'next/server';
import { presentationDocument } from './response';

const MEDIA_TYPE = 'application/vnd.melka.page+json';
const EXCLUDED_HEADERS = new Set(['content-encoding','content-length','connection','transfer-encoding','host']);
export async function handle(request: NextRequest) {
  const origin = process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000';
  const url = new URL(request.nextUrl.pathname + request.nextUrl.search, origin);
  // Legacy explicit error routes do not end with a slash.
  url.pathname = url.pathname.replace(/\/(403|404|500)\/$/, '/$1');
  const headers = new Headers(request.headers);
  for (const name of ['host','connection','content-length','accept-encoding']) headers.delete(name);
  headers.set('Accept', MEDIA_TYPE);
  headers.set('X-Forwarded-Host', request.headers.get('host') || request.nextUrl.host);
  headers.set('X-Forwarded-Proto', request.nextUrl.protocol.replace(':', ''));
  const response = await fetch(url, {
    method: request.method, headers, redirect: 'manual', cache: 'no-store',
    body: ['GET','HEAD'].includes(request.method) ? undefined : await request.arrayBuffer(),
    signal: AbortSignal.timeout(60000),
  });
  const outgoing = new Headers();
  for (const [key,value] of response.headers) if (!EXCLUDED_HEADERS.has(key) && key !== 'set-cookie') outgoing.append(key,value);
  for (const cookie of response.headers.getSetCookie()) outgoing.append('set-cookie',cookie);
  outgoing.set('cache-control','private, no-store');
  outgoing.set('X-Melka-Frontend','Next.js');
  if (response.status >= 300 && response.status < 400) {
    const location = outgoing.get('location');
    if (location?.startsWith(origin)) outgoing.set('location', location.slice(origin.length) || '/');
    return new Response(null,{status:response.status,headers:outgoing});
  }
  const type = response.headers.get('content-type') || '';
  if (type.includes('application/json')) {
    const payload = await response.json();
    if (payload.template && payload.context) {
      outgoing.set('content-type','text/html; charset=utf-8');
      try {
        return new Response(request.method === 'HEAD' ? null : presentationDocument(payload), {status:response.status,headers:outgoing});
      } catch (error) {
        console.error('Presentation rendering failed', request.nextUrl.pathname, error);
        return new Response('Unable to render this page.', {status:500, headers:outgoing});
      }
    }
    return new Response(JSON.stringify(payload), {status:response.status,headers:outgoing});
  }
  // Binary downloads and third-party Django administration remain backend
  // resources. Application pages must never silently fall back to backend HTML.
  if (type.includes('text/html')) {
    console.error('Unexpected HTML response from application backend:', url.pathname, response.status);
    outgoing.set('content-type','text/html; charset=utf-8');
    return new Response('<!doctype html><html><head><title>Page unavailable</title></head><body><h1>Page unavailable</h1><a href="/">Home</a></body></html>', {status: response.status >= 400 ? response.status : 502,headers:outgoing});
  }
  return new Response(request.method === 'HEAD' ? null : response.body,{status:response.status,headers:outgoing});
}
