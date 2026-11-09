export async function GET(request: Request) {
  return Response.redirect(new URL('/static/dashboard/images/brand-logos/favicon.ico',request.url),307);
}
