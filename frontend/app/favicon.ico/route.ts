export async function GET(request: Request) {
  return new Response(null, {
    status: 307,
    headers: {
      Location: new URL('/static/dashboard/images/brand-logos/favicon.ico', request.url).toString(),
      'Cache-Control': 'public, max-age=86400',
    },
  });
}
