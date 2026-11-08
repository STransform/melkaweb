import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { api, ContentNotFound, embedUrl, text, type Item, type Site } from '../../lib/api';
import { localized, resolvePage } from '../../lib/routes.mjs';
import SiteShell from '../../components/Site';
import { Card, Grid, RichText } from '../../components/Content';
import ContentForm from '../../components/Forms';
import Hero from '../../components/Hero';

type Props = { params: Promise<{ path?: string[] }>; searchParams: Promise<Record<string, string | string[] | undefined>> };
type Collection = { title: string; items: Item[]; team?: Item[]; page: number; pages: number; total: number };
type Home = Record<string, Item[]> & { director: Item | null; visitors: number; hero_copy: { title: string; description: string; badge: string } };
export const dynamic = 'force-dynamic';
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { path = [] } = await params;
  const route = resolvePage('/' + path.join('/'));
  return { title: route?.resource ? route.resource.replaceAll('_', ' ') : route?.kind === 'contact' ? 'Contact us' : 'MelkaTech' };
}

export default async function Page({ params, searchParams }: Props) {
  const { path = [] } = await params;
  const query = await searchParams;
  const pathname = '/' + path.join('/') + (path.length ? '/' : '');
  const route = resolvePage(pathname);
  if (!route) notFound();
  const { locale } = route;
  const site = await api<Site>('site/', locale);
  const href = (url: string) => localized(url, locale);
  const t = (label: string) => site.labels[label] || label;
  let content;
  if (route.kind === 'home') {
    const data = await api<Home>('home/', locale);
    const sections = [
      ['services', 'Our services', '/about-us/services/'], ['companyvalues', 'Our values', '/about-us/companyvalues/'],
      ['visionmission', 'Vision and mission', '/about-us/visionmission/'], ['vision', 'Our vision', '/about-us/vision/'],
      ['otech_excellence', 'Excellence in everything we do', '/about-us/otech_excellence/'],
      ['elevating_skills', 'Elevating skills', '/about-us/elevating_skills/'],
      ['blogs', 'Latest insights', '/blogs/blogs/'], ['news', 'Latest news', '/news/news_view/'],
      ['people_saying', 'What people say', '/about-us/people_saying/'],
      ['documents', 'Resources', '/documents/list-documents/'], ['gallery-images', 'Our gallery', '/gallery-images/'],
    ];
    content = <>
      <Hero slides={data.featured_works as unknown as Parameters<typeof Hero>[0]['slides']} locale={locale} copy={data.hero_copy} />
      <section className="section container intro"><p className="eyebrow">CONNECTION · TRANSFORMATION · GROWTH</p><h2>About MelkaTech</h2><p className="lead">Transforming Ideas into Intelligent Solutions that Shape the Future.</p><p>MelkaTech derives its name from “Melka,” a powerful point of convergence where streams unite. We bring together technology, creativity, intelligence, and expertise to build transformative digital solutions.</p><a className="text-link" href={href('/about-us/about/')}>Discover our story ↗</a></section>
      <section className="section container"><div className="section-heading"><h2>Our services</h2></div><Grid items={data.service_highlights} locale={locale} compact /></section>
      {data.director && <section className="section container"><Card item={data.director} locale={locale} /></section>}
      {sections.map(([key, title, url]) => data[key]?.length ? <section className="section container" key={key}><div className="section-heading"><div><p className="eyebrow">MELKATECH</p><h2>{title}</h2></div><a className="text-link" href={href(url)}>View all ↗</a></div><Grid items={data[key].slice(0, key === 'gallery-images' ? 6 : 4)} locale={locale} compact /></section> : null)}
      {!!data.our_partners?.length && <section className="section container"><h2>Our partners</h2><Grid items={data.our_partners} locale={locale} /></section>}
      {!!data.faqs?.length && <section className="section container faq"><p className="eyebrow">HOW CAN WE HELP?</p><h2>Frequently asked questions</h2>{data.faqs.map(item => <details key={item.id}><summary>{text(item.question)}</summary><RichText value={item.answer} /></details>)}</section>}
      {!!data.about_footer?.length && <section className="section container"><Grid items={data.about_footer} locale={locale} /></section>}
      <section className="cta"><div className="container"><p className="eyebrow">LET’S BUILD SOMETHING TOGETHER</p><h2>Connect with MelkaTech.</h2><a className="button" href={href('/contact-us/')}>{t('Contact us')} ↗</a><p className="meta">{data.visitors} visits</p></div></section>
    </>;
  } else if (route.kind === 'contact') {
    const map = embedUrl(site.settings?.map_link);
    content = <div className="container section"><PageHeading title={t('Contact us')} /><div className="contact-grid"><div><h2>Let’s talk about your next project.</h2><p>{site.settings?.address}</p>{site.contacts.map((contact, index) => <address key={index}><p>{contact.address}</p><p><a href={`tel:${contact.phone}`}>{contact.phone}</a></p><p><a href={`mailto:${contact.email}`}>{contact.email}</a></p></address>)}{map && <iframe className="map" src={map} title="Our location" loading="lazy" referrerPolicy="no-referrer-when-downgrade" />}</div><ContentForm locale={locale} labels={site.labels} /></div></div>;
  } else if (route.kind === 'search') {
    const term = Array.isArray(query.searched_item) ? query.searched_item[0] : query.searched_item || '';
    const result = await api<{ term: string; groups: Record<string, { title: string; items: Item[] }> }>(`search/?searched_item=${encodeURIComponent(term)}`, locale);
    const found = Object.values(result.groups).some(group => group.items.length);
    content = <div className="container section"><PageHeading title={t('Search')} /><form className="search-form" action={pathname}><input aria-label={t('Search')} name="searched_item" defaultValue={term} type="search" /><button className="button">{t('Search')}</button></form><p>Results for “{result.term}”</p>{!found && <p role="status">{t('No results found.')}</p>}{Object.entries(result.groups).map(([key, group]) => group.items.length ? <section key={key} className="section"><h2>{group.title}</h2><Grid items={group.items} locale={locale} compact /></section> : null)}<a href={`${href('/vacancies/job_list/')}?search=${encodeURIComponent(term)}`}>Search careers ↗</a></div>;
  } else if (route.kind === 'detail') {
    let result;
    try { result = await api<{ title: string; item: Item }>(`content/${route.resource}/${route.id}/`, locale); }
    catch (error) { if (error instanceof ContentNotFound) notFound(); throw error; }
    const comments = (result.item.comments || []) as Item[];
    content = <div className="container section article-page"><PageHeading title={text(result.item.title)} /><Card item={result.item} locale={locale} />{route.resource === 'blogs' && <section className="comments"><h2>Comments</h2>{comments.map(comment => <article key={comment.id}><h3>{text(comment.author)}</h3><p>{text(comment.message)}</p></article>)}<h2>Leave a comment</h2><ContentForm locale={locale} blogId={result.item.id} labels={site.labels} /></section>}</div>;
  } else {
    const params = new URLSearchParams();
    for (const name of ['page', 'q', 'category']) if (typeof query[name] === 'string') params.set(name, query[name] as string);
    const result = await api<Collection>(`content/${route.resource}/?${params}`, locale);
    const pageHref = (page: number) => { const p = new URLSearchParams(params); p.set('page', String(page)); return `${pathname}?${p}`; };
    const editorial = pathname.includes('/about-us/');
    content = <div className={`container section ${editorial ? 'editorial' : ''}`}><PageHeading title={result.title} /><form className="search-form" action={pathname}><input name="q" type="search" defaultValue={params.get('q') || ''} aria-label={`Search ${result.title}`} placeholder={`Search ${result.title.toLowerCase()}`} /><button className="button">{t('Search')}</button></form><p className="meta">{result.total} results</p><Grid items={result.items} locale={locale} compact={!editorial && ['news', 'blogs'].includes(route.resource || '')} />{!!result.team?.length && <section className="section"><h2>Our team</h2><Grid items={result.team} locale={locale} /></section>}{result.pages > 1 && <nav className="pagination" aria-label="Pagination">{result.page > 1 && <a href={pageHref(result.page - 1)}>{t('Previous')}</a>}<span>Page {result.page} / {result.pages}</span>{result.page < result.pages && <a href={pageHref(result.page + 1)}>{t('Next')}</a>}</nav>}</div>;
  }
  return <div lang={locale === 'ax' ? 'am' : locale === 'ox' ? 'om' : 'en'}><SiteShell site={site} locale={locale} pathname={pathname}>{content}</SiteShell></div>;
}
function PageHeading({ title }: { title: string }) {
  return <header className="page-heading"><p className="eyebrow">MELKATECH</p><h1>{title}</h1></header>;
}
