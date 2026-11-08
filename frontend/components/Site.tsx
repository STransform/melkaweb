import type { ReactNode } from 'react';
import { safeUrl, type Site } from '../lib/api';
import { localized } from '../lib/routes.mjs';

export default function SiteShell({ site, locale, pathname, children }: { site: Site; locale: string; pathname: string; children: ReactNode }) {
  const t = (label: string) => site.labels[label] || label;
  const href = (url: string) => localized(url, locale);
  const nav = [
    ['Home', '/', ''], ['About us', '/about-us/about/', 'about'], ['Services', '/about-us/services/', 'services'],
    ['News', '/news/news_view/', 'news'], ['Blogs', '/blogs/blogs/', 'blogs'],
    ['Contact us', '/contact-us/', 'contact_us'],
  ];
  const more = [
    ['Documents', '/documents/list-documents/', 'documents'], ['Events', '/events/', 'events'],
    ['Gallery images', '/gallery-images/', 'gallery'], ['Gallery videos', '/gallery-videos/', 'gallery'],
    ['Bids', '/bids/', 'bid'], ['Careers', '/vacancies/job_list/', 'vacancy'], ['Suppliers', '/suppliers/locked_supplier_list/', 'blocked_suppliers'],
    ['Our structure', '/about-us/bureau_structure/', 'structure'], ['Technology', '/about-us/technology/', 'services'],
    ['Infrastructure', '/about-us/infrastructure/', 'services'], ['Innovation', '/about-us/innovation/', 'services'],
    ['Our values', '/about-us/companyvalues/', 'about'], ['Vision and mission', '/about-us/visionmission/', 'about'],
    ['Our partners', '/about-us/our_partners/', 'about'],
  ];
  const visible = (entry: string[]) => !entry[2] || site.pages?.[entry[2]] !== false;
  const title = site.settings?.title || 'MelkaTech';
  const unlocalizedPath = pathname.replace(/^\/(ax|ox)(?=\/|$)/, '') || '/';
  return <>
    <a href="#main" className="skip-link">Skip to content</a>
    <header className="site-header"><div className="container header-inner">
      <a className="brand" href={href('/')} aria-label={`${title} home`}>
        {site.settings?.logo ? <img src={safeUrl(site.settings.logo)} alt="" width={44} height={44} /> : <span className="brand-mark" aria-hidden="true">M<span>↗</span></span>}
        <span>{title}</span>
      </a>
      <nav aria-label="Main navigation">
        <details className="mobile-nav"><summary>Menu</summary><div>{nav.concat(more).filter(visible).map(([label, url]) => <a key={url} href={href(url)}>{t(label)}</a>)}</div></details>
        <div className="desktop-nav">{nav.filter(visible).map(([label, url]) => <a key={url} href={href(url)} aria-current={pathname === href(url) ? 'page' : undefined}>{t(label)}</a>)}
          <details className="nav-more"><summary>Explore</summary><div>{more.filter(visible).map(([label, url]) => <a key={url} href={href(url)}>{t(label)}</a>)}</div></details>
        </div>
      </nav>
      <div className="account-nav"><a href={href(site.user.authenticated ? '/accounts/logout/' : '/accounts/login/')}>{t(site.user.authenticated ? 'Sign out' : 'Sign in')}</a>{site.user.staff && <a href={href('/dashboard/')}>{t('Dashboard')}</a>}</div>
    </div></header>
    <div className="utility-bar"><div className="container utilities">
      <form action={href('/search/')} role="search"><input name="searched_item" type="search" aria-label={t('Search')} placeholder={`${t('Search')}…`} /><button aria-label={t('Search')}>↗</button></form>
      <nav aria-label="Language">{[['en', 'English'], ['ax', 'አማርኛ'], ['ox', 'Afaan Oromoo']].map(([code, label]) => <a key={code} href={localized(unlocalizedPath, code)} hrefLang={code === 'ax' ? 'am' : code === 'ox' ? 'om' : 'en'} aria-current={locale === code ? 'true' : undefined}>{label}</a>)}</nav>
    </div></div>
    <main id="main">{children}</main>
    <footer className="site-footer"><div className="container footer-grid">
      <div><a className="brand" href={href('/')}>{title}</a><p>Transforming ideas into intelligent solutions.</p><div className="socials">{['facebook', 'youtube', 'instagram', 'twitter', 'linkedin'].map(name => safeUrl(site.settings?.[name]) && <a key={name} href={safeUrl(site.settings?.[name])} rel="noopener noreferrer">{name}</a>)}</div></div>
      <div><h2>Explore</h2>{nav.concat(more).filter(visible).map(([label, url]) => <a key={url} href={href(url)}>{t(label)}</a>)}</div>
      <div><h2>Contact</h2><p>{site.settings?.address}</p>{site.contacts.map((contact, index) => <div key={index}><p>{contact.address}</p><a href={`tel:${contact.phone}`}>{contact.phone}</a><a href={`mailto:${contact.email}`}>{contact.email}</a></div>)}<a href={`mailto:${site.settings?.email || ''}`}>{site.settings?.email}</a><p>{site.settings?.working_hours}</p></div>
      {!!site.quick_links.length && <div><h2>Quick links</h2>{site.quick_links.map(link => <a key={link.id} href={safeUrl(link.url)}>{link.title}</a>)}</div>}
    </div><div className="container copyright">© {new Date().getFullYear()} {title}</div></footer>
  </>;
}
