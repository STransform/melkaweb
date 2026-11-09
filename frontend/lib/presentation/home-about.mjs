const text = text => ({ op: 'text', text });
const value = expr => ({ op: 'value', expr });

export function homeAbout(original) {
  return [
    ...original.filter(node => node.op === 'block' && node.args === 'css'),
    { op: 'if', branches: [{ test: 'homepage_about or homepage_services', body: [
      text('<section class="about-section"><div class="container">'),
      { op: 'if', branches: [{ test: 'homepage_about', body: [
        text('<div class="about-hero"><h2 class="about-title">'), value('homepage_about.title'),
        text('</h2></div><div class="about-description">'), value('homepage_about.content|linebreaks'), text('</div>'),
      ] }] },
      { op: 'if', branches: [{ test: 'homepage_services', body: [
        text('<div class="about-features">'),
        { op: 'for', args: 'service in homepage_services', empty: [], body: [
          text('<article class="feature-item"><div class="feature-icon"><i class="fas fa-code" aria-hidden="true"></i></div><div class="feature-content"><h3 class="feature-title">'),
          value('service.title'), text('</h3><div class="feature-description">'), value('service.content|linebreaks'),
          text('</div></div></article>'),
        ] },
        text('</div>'),
      ] }] },
      text('</div></section>'),
    ] }] },
  ];
}
