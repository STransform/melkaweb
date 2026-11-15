const text = text => ({ op: 'text', text });
const value = expr => ({ op: 'value', expr });
const trans = label => ({ op: 'trans', args: JSON.stringify(label) });

const styles = `<style>
.managed-services{padding:88px 0;background:linear-gradient(180deg,#f1f8fd,#fff);color:#102c46}
.managed-services .services-intro{max-width:650px;margin:0 auto 42px;text-align:center}
.managed-services .services-eyebrow{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#0077be;margin-bottom:12px}
.managed-services .services-heading{font-family:inherit;font-size:clamp(30px,3.5vw,46px);font-weight:750;letter-spacing:-.04em;line-height:1.15;color:#102c46;margin:0 0 16px}
.managed-services .services-intro p:last-child{font-size:16px;line-height:1.8;color:#61768a;margin:0}
.managed-services .managed-services-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.managed-services .managed-service{display:flex;flex-direction:column;min-width:0;padding:30px;background:white;border:1px solid #dce9f2;border-radius:18px;box-shadow:0 8px 30px #163d6209;transition:transform .2s,box-shadow .2s,border-color .2s}
.managed-services .managed-service:hover{transform:translateY(-5px);border-color:#99cfe9;box-shadow:0 16px 40px #163d6214}
.managed-services .managed-service-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:26px}
.managed-services .managed-service-icon{display:grid;place-items:center;width:50px;height:50px;border-radius:14px;background:#e9f6ff;color:#0077be;font-size:20px}
.managed-services .managed-service-number{font-size:12px;font-weight:600;color:#8a9faf;letter-spacing:.08em}
.managed-services .managed-service h3{font-family:inherit;font-size:22px;line-height:1.35;letter-spacing:-.025em;color:#102c46;margin:0 0 15px;overflow-wrap:anywhere;text-transform:none}
.managed-services .managed-service-description{font-size:15px;line-height:1.85;color:#617183;overflow-wrap:anywhere;margin-bottom:26px}
.managed-services .managed-service-description p{margin:0 0 12px;color:inherit;line-height:inherit}
.managed-services .managed-service-image{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:12px;margin-bottom:20px}
.managed-services .managed-service-link{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-top:auto;padding-top:20px;border-top:1px solid #e9eff5;color:#0077be;font-size:14px;font-weight:700;text-decoration:none}
.managed-services .managed-service-link:hover{color:#004f82}.managed-services .managed-service-link:focus-visible{outline:3px solid #0077be;outline-offset:5px;border-radius:4px}
.managed-services .managed-service-link span{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#eef8fd;font-size:18px}
.managed-services .managed-services-grid:has(>.managed-service:only-child){grid-template-columns:minmax(0,700px);justify-content:center}
.managed-services .services-empty{text-align:center;color:#617183;padding:30px}
@media(max-width:991px){.managed-services .managed-services-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:575px){.managed-services{padding:56px 0}.managed-services .managed-services-grid{grid-template-columns:1fr;gap:18px}.managed-services .managed-service{padding:24px}.managed-services .services-intro{margin-bottom:30px}}
@media(prefers-reduced-motion:reduce){.managed-services .managed-service{transition:none}.managed-services .managed-service:hover{transform:none}}
</style>`;

export function serviceCards(collection = 'homepage_services', home = true) {
  const content = [
    text(styles + `<section class="managed-services${home ? '' : ' services-catalogue'}"${home ? '' : ' id="service-catalogue"'} aria-label="Our services"><div class="container">`),
    ...(home ? [text('<header class="services-intro"><p class="services-eyebrow">'), trans('What we do'),
      text('</p><h2 class="services-heading">'), trans('Our Services'),
      text('</h2><p>'), trans('Technology solutions built around your business.'), text('</p></header>')] : []),
    ...(!home ? [text('<header class="services-catalogue-head"><div><p class="services-page-eyebrow">WHAT WE DO</p><h2>Find the right solution for your business.</h2></div><span>'), value('services|length'), text(' services to explore</span></header>')] : []),
    text('<div class="managed-services-grid">'),
    { op: 'for', args: `service in ${collection}`, empty: [], body: [
      text('<article class="managed-service"><div class="managed-service-top"><div class="managed-service-icon" aria-hidden="true"><i class="fas '),
      { op: 'cycle', args: "'fa-code' 'fa-server' 'fa-lightbulb'" },
      text('"></i></div><span class="managed-service-number" aria-hidden="true">'), value('forloop.counter'),
      text('</span></div>'),
      { op: 'if', branches: [{ test: 'service.image_url', body: [text('<img class="managed-service-image" loading="lazy" src="'), value('service.image_url'), text('" alt="">')] }] },
      text('<h3>'), value('service.title'), text('</h3><div class="managed-service-description">'), value('service.content|linebreaks'),
      text('</div><a class="managed-service-link" href="'), { op: 'url', args: "'contact_us'" },
      text('?subject='), value('service.title|urlencode'), text('">'), trans('Discuss your project'), text('<span aria-hidden="true">↗</span></a></article>'),
    ] },
    text('</div>'),
    ...(!home ? [{ op: 'if', branches: [{ test: `not ${collection}`, body: [text('<p class="services-empty">'), trans('Our services will be available here soon.'), text('</p>')] }] }] : []),
    text('</div></section>'),
    ...(!home ? [text('<section class="services-project-callout"><div class="container"><div><p class="services-page-eyebrow">LET’S BUILD SOMETHING USEFUL</p><h2>Have a challenge in mind?</h2><p>Tell us what you want to achieve. We’ll help you find a way forward.</p></div><a class="services-primary-action" href="'), {op:'url', args:"'contact_us'"}, text('">Start a conversation <span aria-hidden="true">↗</span></a></div></section>')] : []),
  ];
  return home ? [{ op: 'if', branches: [{ test: collection, body: content }] }] : content;
}

// Retain both configured and fallback navigation, with one direct Services link.
export function serviceNavigation(nodes) {
  const result = structuredClone(nodes);
  function visit(list) {
    for (let i = 0; i < list.length; i++) {
      const node = list[i];
      if (node.op === 'trans' && /^['"]Services['"]$/.test(node.args)) {
        let start = i - 1;
        while (start >= 0 && !list[start].text?.includes('<li class="dropdown">')) start--;
        if (start >= 0 && list[i + 1]?.text?.includes('dropdown-menu')) {
          const opening = list[start].text.lastIndexOf('<li class="dropdown">');
          list[start].text = list[start].text.slice(0, opening) + list[start].text.slice(opening).replace('<li class="dropdown">', '<li class="services-menu">');
          let end = i + 2;
          while (end < list.length && !list[end].text?.includes('</li>')) end++;
          if (end < list.length) {
            const suffix = list[end].text.slice(list[end].text.indexOf('</li>') + 5);
            list.splice(i + 1, end - i, text('</a></li>' + suffix));
          }
        }
      }
      if (node.body) visit(node.body);
      if (node.empty) visit(node.empty);
      for (const branch of node.branches || []) visit(branch.body);
    }
  }
  visit(result);
  return result;
}

export function serviceHeader() {
  return [text(`<link rel="stylesheet" href="/static/front/css/services.css"><header class="services-page-hero"><div class="container"><nav class="services-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span>Services</span></nav><div class="services-page-hero-layout"><div><p class="services-page-eyebrow">EXPERTISE THAT MOVES YOU FORWARD</p><h1>`), value('page_title'), text('</h1><p class="services-page-deck">'), value('page_subtitle'), text('</p><div class="services-page-actions"><a class="services-primary-action" href="#service-catalogue">Explore our services <span aria-hidden="true">↓</span></a><a class="services-secondary-action" href="'), {op:'url',args:"'contact_us'"}, text(`">Let’s talk about your project ↗</a></div></div><div class="services-page-visual" aria-hidden="true"><div class="services-visual-symbol">&lt;/&gt;</div><span>IDEA → SOLUTION → IMPACT</span><div class="services-visual-labels"><span>Thoughtful design</span><span>Practical technology</span><span>Built around you</span></div></div></div></div></header>`)];
}
