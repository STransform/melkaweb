// Keep admin-managed slides in the same layout as the public hero.
const text = text => ({ op: 'text', text });
const value = expr => ({ op: 'value', expr });
const url = name => ({ op: 'url', args: `'${name}'` });
const trans = label => ({ op: 'trans', args: JSON.stringify(label) });
const first = body => ({ op: 'if', branches: [{ test: 'forloop.first', body: [text(body)] }] });

export function homeHero(original) {
  const nodes = structuredClone(original);
  const condition = nodes.find(node => node.op === 'if');
  condition.branches[0].body = [
    text('<div id="techHeroCarousel" class="carousel slide managed-hero" data-bs-interval="6000" aria-label="Featured projects"><div class="carousel-inner">'),
    { op: 'for', args: 'work in featured_works', empty: [], body: [
      text('<section class="hero-section carousel-item '), first('active'),
      text('"><div class="container"><div class="hero-wrapper '),
      { op: 'if', branches: [{ test: 'not work.background_image', body: [text('hero-without-image')] }] },
      text('"><div class="hero-content"><h1 class="hero-title">'),
      value('work.title'), text('</h1><p class="hero-subtitle">'), value('work.description'),
      text('</p><div class="hero-buttons"><a class="hero-btn hero-btn-primary" href="'), url('services'),
      text('">'), trans('Start Project'), text(' <i class="fas fa-arrow-right" aria-hidden="true"></i></a><a class="hero-btn hero-btn-secondary" href="'),
      url('about'), text('">'), trans('Our Story'),
      text(' <i class="fas fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div></div>'),
      { op: 'if', branches: [{ test: 'work.background_image', body: [
        text('<div class="hero-visual"><img class="hero-mockup" src="'),
        value('work.background_image.url'), text('" alt="'), value('work.title'), text('"></div>'),
      ] }] },
      text('</div></div></section>'),
    ] },
    text('</div>'),
    { op: 'if', branches: [{ test: 'featured_works|length > 1', body: [
      text('<div class="carousel-indicators">'),
      { op: 'for', args: 'work in featured_works', empty: [], body: [
        text('<button type="button" data-bs-target="#techHeroCarousel" data-bs-slide-to="'), value('forloop.counter0'),
        text('" class="'), first('active'), text('" aria-label="Show slide '), value('forloop.counter'), text('"></button>'),
      ] },
      text('</div><button class="managed-hero-pause" type="button" aria-label="Pause slideshow" aria-pressed="false">Pause</button>'),
    ] }] },
    text('</div>'),
  ];
  nodes[nodes.length - 1] = text(`<script>
document.addEventListener('DOMContentLoaded', function () {
  var element = document.getElementById('techHeroCarousel');
  if (!element || !window.bootstrap) return;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var multiple = element.querySelectorAll('.carousel-item').length > 1;
  var carousel = new bootstrap.Carousel(element, {interval: reduced || !multiple ? false : 6000, wrap: true, keyboard: true, pause: 'hover'});
  var button = element.querySelector('.managed-hero-pause');
  var paused = reduced;
  function update() { if (button) { button.textContent = paused ? 'Play' : 'Pause'; button.setAttribute('aria-label', paused ? 'Play slideshow' : 'Pause slideshow'); button.setAttribute('aria-pressed', String(paused)); } }
  if (multiple && !paused) carousel.cycle();
  element.addEventListener('focusin', function () { carousel.pause(); });
  element.addEventListener('focusout', function (event) { if (!element.contains(event.relatedTarget) && !paused) carousel.cycle(); });
  element.addEventListener('mouseleave', function () { if (paused) carousel.pause(); });
  if (button) button.addEventListener('click', function () { paused = !paused; paused ? carousel.pause() : carousel.cycle(); update(); });
  update();
});
</script>`);
  return nodes;
}
