import { NextRequest, NextResponse } from 'next/server';
import { resolvePage } from './lib/routes.mjs';

export function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  if (resolvePage(path) && ['GET', 'HEAD'].includes(request.method)) return NextResponse.next();
  // Forward sessions, CSRF cookies, multipart uploads and original request bodies
  // unchanged. Public API mutations likewise use Django's normal CSRF middleware.
  const destination = new URL(process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000');
  destination.pathname = path;
  destination.search = request.nextUrl.search;
  return NextResponse.rewrite(destination);
}
export const config = {
  matcher: ['/((?!_next/|favicon.ico).*)'],
};
