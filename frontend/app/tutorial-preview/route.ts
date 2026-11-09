import { tutorialMarkdown } from '../../lib/tutorial-markdown.mjs';

export async function POST(request: Request) {
  if (Number(request.headers.get('content-length') || 0) > 600000) return Response.json({ detail: 'Preview is too large.' }, { status: 413 });
  const body = await request.text();
  if (body.length > 600000) return Response.json({ detail: 'Preview is too large.' }, { status: 413 });
  try {
    const data = JSON.parse(body);
    const preview = tutorialMarkdown(data.content, data.format);
    // Preview images should load immediately, even below a long editor.
    preview.html = preview.html.replaceAll('loading="lazy"', 'loading="eager"');
    return Response.json(preview, { headers: { 'Cache-Control': 'no-store' } });
  } catch { return Response.json({ detail: 'Invalid preview.' }, { status: 400 }); }
}
