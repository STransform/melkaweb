import { NextRequest, NextResponse } from 'next/server';

export function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  // Django remains the data/file server and supplies its own third-party
  // administration tools. All website screens are rendered by Next.js.
  if (!/^\/(?:(?:ax|ox)\/)?(?:api|static|media|internalAdmin|filer|jsi18n|i18n)(?:\/|$)/.test(path)
      && !/^\/(?:(?:ax|ox)\/)?dashboard\/translator(?:\/|$)/.test(path)) return NextResponse.next();
  const destination = new URL(process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000');
  destination.pathname = path;
  destination.search = request.nextUrl.search;
  return NextResponse.rewrite(destination);
}
export const config = { matcher: ['/((?!_next/|favicon.ico).*)'] };
