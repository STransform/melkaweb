import { marked } from 'marked';
import sanitize from 'sanitize-html';
import hljs from 'highlight.js';

const escape = text => String(text).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

export function tutorialMarkdown(source = '', format = 'markdown') {
  const input = String(source);
  const renderer = new marked.Renderer();
  renderer.code = ({ text, lang }) => {
    const language = (lang || '').split(/\s/)[0];
    const code = language && hljs.getLanguage(language) ? hljs.highlight(text, { language, ignoreIllegals: true }).value : escape(text);
    return `<pre><code class="hljs language-${escape(language || 'text')}">${code}</code></pre>`;
  };
  const raw = format === 'legacy'
    ? (/<[a-z][\s\S]*>/i.test(input) ? input : `<p>${escape(input).replaceAll('\n', '<br>')}</p>`)
    : marked.parse(input, { renderer, gfm: true, breaks: false });
  let html = sanitize(raw, {
    allowedTags: sanitize.defaults.allowedTags.concat(['img', 'details', 'summary', 'kbd', 'figure', 'figcaption', 'iframe']),
    allowedAttributes: { a: ['href', 'title', 'rel'], img: ['src', 'alt', 'title', 'loading'], code: ['class'], span: ['class'], th: ['align'], td: ['align'], iframe: ['src', 'title', 'loading', 'allow', 'allowfullscreen', 'referrerpolicy', 'style'] },
    allowedSchemes: ['http', 'https', 'mailto'], allowProtocolRelative: false,
    transformTags: {
      a: sanitize.simpleTransform('a', { rel: 'noopener noreferrer' }),
      img: sanitize.simpleTransform('img', { loading: 'lazy' }),
      iframe: (_tag, attrs) => {
        // Rebuild trusted YouTube embeds without authored scripts or attributes.
        let url;
        try { url = new URL(attrs.src); } catch { return { tagName: 'span', attribs: {} }; }
        if (url.protocol !== 'https:' || url.port || url.username || url.password ||
            !['www.youtube.com', 'youtube.com', 'www.youtube-nocookie.com', 'youtube-nocookie.com'].includes(url.hostname) ||
            !/^\/embed\/[A-Za-z0-9_-]{11}$/.test(url.pathname)) {
          return { tagName: 'span', attribs: {} };
        }
        return { tagName: 'iframe', attribs: {
          src: `${url.origin}${url.pathname}${url.search}`,
          title: attrs.title || 'YouTube video', loading: 'lazy',
          allow: 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share',
          allowfullscreen: '', referrerpolicy: 'strict-origin-when-cross-origin',
          style: 'display: block; width: 100%; aspect-ratio: 16 / 9; height: auto; border: 0',
        } };
      },
    },
  });
  // Own the player dimensions instead of relying on authored iframe sizes or
  // surrounding theme styles. The complete 16:9 player stays inside its column.
  html = html.replace(/<iframe\b([^>]*)><\/iframe>/g, (frame, attrs) => {
    const id = attrs.match(/src="https:\/\/[^/]+\/embed\/([A-Za-z0-9_-]{11})/)?.[1];
    if (!id) return frame;
    return `<div class="tutorial-video"><div class="tutorial-video-player">${frame}</div><div class="tutorial-video-footer"><span>Video lesson</span><a href="https://www.youtube.com/watch?v=${id}" target="_blank" rel="noopener noreferrer">Watch on YouTube</a></div></div>`;
  });
  // Add trusted code chrome after sanitization so authored HTML cannot inject
  // buttons or handlers, and both editor previews and articles share one layout.
  html = html.replace(/<pre>([\s\S]*?)<\/pre>/g, (_, content) => {
    if (!/<code\b/.test(content)) content=`<code class="hljs language-text">${content}</code>`;
    const language = content.match(/class="[^"]*\blanguage-([^\s"]+)/)?.[1] || 'text';
    const labels = {java:'Java',javascript:'JavaScript',js:'JavaScript',typescript:'TypeScript',ts:'TypeScript',python:'Python',py:'Python',bash:'Bash',sh:'Shell',yaml:'YAML',json:'JSON',sql:'SQL',dockerfile:'Dockerfile',plaintext:'Plain text',text:'Code'};
    const label = labels[language.toLowerCase()] || language;
    const lines = content.replace(/<[^>]+>/g,'').split('\n').length;
    return `<div class="tutorial-code-block"><div class="tutorial-code-toolbar"><div class="tutorial-code-info"><span class="tutorial-code-symbol" aria-hidden="true">&lt;/&gt;</span><span class="tutorial-code-language">${escape(label)}</span><span class="tutorial-code-lines">${lines} ${lines===1?'line':'lines'}</span></div><button type="button" class="tutorial-copy-code" data-copy-tutorial-code aria-label="Copy code">Copy code</button></div><pre tabindex="0" aria-label="${escape(label)} code example">${content}</pre></div>`;
  });
  const toc = [];
  html = html.replace(/<h([1-6])>([\s\S]*?)<\/h\1>/g, (_, level, title) => {
    const id = `section-${toc.length + 1}`;
    const depth = Math.max(2, Number(level));
    toc.push({ id, title: sanitize(title, { allowedTags: [], allowedAttributes: {} }), depth });
    return `<h${depth} id="${id}">${title}</h${depth}>`;
  });
  return { html, toc };
}
