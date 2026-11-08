// These routes have React implementations. Everything else stays with Django
// until it has an equivalent implementation and workflow coverage.
export const resources = {
  'news/news_view': 'news', 'blogs/blogs': 'blogs',
  'documents/list-documents': 'documents', 'gallery-images': 'gallery-images',
  'gallery-videos': 'gallery-videos', events: 'events', bids: 'bids',
};
for (const name of ['about', 'services', 'technology', 'infrastructure', 'innovation', 'companyvalues', 'visionmission', 'vision', 'otech_excellence', 'people_saying', 'about_footer', 'elevating_skills', 'our_partners', 'bureau_structure']) {
  resources[`about-us/${name}`] = name;
}
export function resolvePage(pathname) {
  const parts = pathname.split('/').filter(Boolean);
  const locale = ['ax', 'ox'].includes(parts[0]) ? parts.shift() : 'en';
  const path = parts.join('/');
  if (!path) return { locale, kind: 'home' };
  if (path === 'contact-us') return { locale, kind: 'contact' };
  if (path === 'search') return { locale, kind: 'search' };
  if (resources[path]) return { locale, kind: 'collection', resource: resources[path] };
  let match = path.match(/^news\/(\d+)$/);
  if (match) return { locale, kind: 'detail', resource: 'news', id: match[1] };
  match = path.match(/^blogs\/blogs\/(\d+)$/);
  if (match) return { locale, kind: 'detail', resource: 'blogs', id: match[1] };
  return null;
}
export function localized(path, locale) {
  if (!path.startsWith('/') || path.startsWith('//')) return path;
  if (/^\/(ax|ox)(\/|$)/.test(path) || /^\/(static|media|_next)(\/|$)/.test(path)) return path;
  return locale === 'en' ? path : `/${locale}${path}`;
}
