export async function GET(request: Request) {
  const origin = new URL(request.url).origin;
  return new Response(`User-agent: *\nAllow: /\nDisallow: /dashboard/\nDisallow: /accounts/\nDisallow: /internalAdmin/\nDisallow: /api/\nSitemap: ${origin}/tutorials/sitemap.xml\n`, {headers:{'Content-Type':'text/plain; charset=utf-8'}});
}
