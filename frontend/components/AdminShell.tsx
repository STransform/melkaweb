'use client';

import { useEffect, useState, type ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import './admin-shell.css';

export type AdminIdentity = { id: number; name: string; first_name: string; role: string; profile_pic: string | null; permissions: string[]; is_superuser: boolean };
type Entry = { label: string; model?: string; href?: string; permission?: string; icon?: string; children?: Entry[] };
const model = (label: string, code: string, app: string): Entry => ({ label, model: code, permission: `${app}.view_${code.toLowerCase()}`, href: `/dashboard/list/${code}/` });
const sections: { title: string; entries: Entry[] }[] = [
  { title: 'Main Pages', entries: [{ label: 'Website', href: '/', icon: 'bx-globe' }, { label: 'Dashboard', href: '/dashboard/', icon: 'bx-table' }] },
  { title: 'Web Manager', entries: [
    { label: 'Home Page', icon: 'bx-home', children: [model('Home Sliders', 'FeaturedWork', 'dashboard'), model('CEO Message', 'DirectorateMessage', 'dashboard')] },
    { label: 'About Us', icon: 'bx-medal', children: [model('Team', 'TeamMember', 'about_us'), model('Services', 'Service', 'about_us'), model('About Us', 'About', 'about_us'), model('Vision & Mission', 'VisionMission', 'about_us'), model('Company Value', 'CompanyValues', 'about_us'), model('Vision', 'Vision', 'about_us'), model('Otech Excellence', 'OtechExcellence', 'about_us'), model('Elevating Skills', 'ElevatingSkills', 'about_us'), model('What People Says About Us', 'WhatPeopleSays', 'about_us'), model('Our Partners', 'OurPartners', 'about_us')] },
    { label: 'Services', icon: 'bx-medal', children: [model('Technology services slide head', 'Technology', 'about_us'), model('Infrastructure & Deployment', 'Infrastructure', 'about_us'), model('Consulting & Innovation', 'Innovation', 'about_us')] },
    { label: 'Announcements', icon: 'bx-task', children: [model('Bids', 'Bid', 'dashboard'), model('Document', 'Document', 'documents'), model('Vacancies', 'Job', 'vacancies'), { label: 'Applicant List', href: '/vacancies/application_list/', permission: 'vacancies.view_application' }] },
    { label: 'Blogs', icon: 'bx-news', children: [{ label: 'Blogs', children: [model('Blogs', 'Blog', 'blogs'), model('Blog Comments', 'BlogComment', 'blogs'), model('Blog Categories', 'BlogCategory', 'blogs')] }] },
    { label: 'Gallery', icon: 'bx-image', children: [model('Images', 'GalleryImage', 'dashboard'), model('Videos', 'GalleryVideo', 'dashboard'), model('Categories', 'GalleryCategory', 'dashboard')] },
    { label: 'Contact Us', icon: 'bxs-envelope', children: [model('About Us(For footer)', 'AboutOtechFooter', 'about_us'), model('FAQs', 'FAQ', 'dashboard'), model('Quick Links', 'QuickLink', 'dashboard'), model('Contact', 'Contact', 'dashboard'), model('Contact Us Messages', 'ContactUs', 'core')] },
  ] },
  { title: 'Web Settings', entries: [{ ...model('Main Setting', 'Settings', 'core'), icon: 'bx-cog' }, { ...model('Page Controller', 'Pages', 'core'), icon: 'bx-list-check' }, { label: 'Translation Dictionary', href: '/dashboard/translator/', icon: 'bx-cog', permission: 'core.view_settings' }] },
  { title: 'User Manager', entries: [{ label: 'Users', href: '/accounts/users_list/', icon: 'bx-user', permission: 'accounts.view_userprofile' }, { ...model('User Permission Groups', 'Group', 'auth'), icon: 'bx-home' }] },
];

export default function AdminShell({ user, title, children }: { user: AdminIdentity; title: string; children: ReactNode }) {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [collapsed, setCollapsed] = useState(false);
  const [dark, setDark] = useState(false);
  const [welcome, setWelcome] = useState(true);
  useEffect(() => {
    const root = document.documentElement;
    const attributes = { 'data-nav-layout': 'vertical', 'data-theme-mode': dark ? 'dark' : 'light', 'data-header-styles': 'light', 'data-menu-styles': 'dark', 'data-toggled': collapsed ? 'icon-overlay-close' : 'close' };
    const before = Object.fromEntries(Object.keys(attributes).map(key => [key, root.getAttribute(key)]));
    Object.entries(attributes).forEach(([key, value]) => root.setAttribute(key, value));
    document.body.classList.add('melka-admin');
    return () => { Object.entries(before).forEach(([key, value]) => value === null ? root.removeAttribute(key) : root.setAttribute(key, value)); document.body.classList.remove('melka-admin'); };
  }, [collapsed, dark]);
  const allowed = (entry: Entry): boolean => entry.children ? entry.children.some(allowed) : !entry.permission || user.is_superuser || user.permissions.includes(entry.permission);
  const active = (entry: Entry): boolean => entry.children ? entry.children.some(active) : entry.href === pathname || !!entry.model && pathname.includes(`/${entry.model}/`);
  function renderEntry(entry: Entry, level = 0): ReactNode {
    if (!allowed(entry)) return null;
    const key = `${level}-${entry.label}`;
    const open = expanded[key] ?? active(entry);
    return <li className={`slide ${entry.children ? 'has-sub' : ''} ${active(entry) ? 'active' : ''} ${open ? 'open' : ''}`} key={key}>
      {entry.children ? <><button type="button" className={`side-menu__item ${active(entry) ? 'active' : ''}`} aria-expanded={open} onClick={() => setExpanded(value => ({ ...value, [key]: !open }))}>{entry.icon && <i className={`bx ${entry.icon} side-menu__icon`} />}<span className="side-menu__label">{entry.label}</span><i className="fe fe-chevron-right side-menu__angle" /></button><ul className={`slide-menu child${level + 1}`} style={{ display: open ? 'block' : 'none' }}>{entry.children.map(child => renderEntry(child, level + 1))}</ul></> : <Link href={entry.href || '/dashboard/'} className={`side-menu__item ${active(entry) ? 'active' : ''}`} aria-current={active(entry) ? 'page' : undefined}>{entry.icon && <i className={`bx ${entry.icon} side-menu__icon`} />}<span className="side-menu__label">{entry.label}</span></Link>}
    </li>;
  }
  return <div className={`legacy-admin ${collapsed ? 'sidebar-collapsed' : ''}`} data-menu-styles="dark" data-theme-mode={dark ? 'dark' : 'light'}>
    <link rel="stylesheet" href="/static/dashboard/libs/bootstrap/css/bootstrap.min.css" />
    <link rel="stylesheet" href="/static/dashboard/css/styles.min.css" />
    <link rel="stylesheet" href="/static/dashboard/css/icons.css" />
    <div className="admin-toolbar"><Link href="/">{title}</Link><details><summary>Language</summary><div className="admin-toolbar-menu"><a href="/i18n/setlang/">Language settings</a><a href="/dashboard/translator/">Translation Dictionary</a></div></details><div className="ms-auto d-flex align-items-center gap-4"><button aria-label="Toggle color mode" onClick={() => setDark(value => !value)}>◐</button><details><summary className="btn btn-outline-light">Create</summary><div className="admin-toolbar-menu"><Link href="/dashboard/create/Blog/">Blog</Link><Link href="/dashboard/create/FeaturedWork/">Home Slider</Link><Link href="/dashboard/create/Event/">Event</Link></div></details></div></div>
    <div className="page"><header className="app-header"><div className="main-header-container container-fluid"><div className="header-content-left"><div className="header-element"><button aria-label="Toggle sidebar" className="sidemenu-toggle header-link animated-arrow hor-toggle" onClick={() => setCollapsed(value => !value)}><span /></button></div></div><div className="header-content-right"><div className="header-element"><details className="admin-profile"><summary className="header-link"><div className="d-flex align-items-center"><div className="me-sm-2 me-0"><img src={user.profile_pic || '/static/front/imgs/team/user.png'} alt="" width="32" height="32" className="rounded-circle" /></div><div className="d-sm-block d-none"><p className="fw-semibold mb-0 lh-1">{user.first_name}</p><span className="op-7 fw-normal d-block fs-11">{user.role}</span></div></div></summary><div className="dropdown-menu show dropdown-menu-end"><Link className="dropdown-item" href={`/accounts/profile/${user.id}/`}><i className="ti ti-user-circle fs-18 me-2 op-7" />Profile</Link><Link className="dropdown-item" href="/accounts/logout/"><i className="ti ti-logout fs-18 me-2 op-7" />Log Out</Link></div></details></div></div></div></header>
      <aside className="app-sidebar sticky" id="sidebar"><div className="main-sidebar" id="sidebar-scroll"><nav className="main-menu-container nav nav-pills flex-column sub-open"><ul className="main-menu">{sections.filter(section => section.entries.some(allowed)).map(section => <li className="admin-menu-section" key={section.title}><div className="slide__category"><span className="category-name">{section.title}</span></div><ul>{section.entries.map(entry => renderEntry(entry))}</ul></li>)}</ul></nav></div></aside>
      <main className="main-content app-content">{pathname === '/dashboard/' && welcome && <div className="alert alert-success alert-dismissible fade show custom-alert-icon shadow-sm" role="status">Welcome back {user.name}<button type="button" className="btn-close" aria-label="Close welcome message" onClick={() => setWelcome(false)} /></div>}<div className="container-fluid">{children}</div></main>
      <footer className="footer mt-auto py-3 bg-white text-center"><span>Developed by : </span><a href="https://www.stransform.com/" className="fw-semibold text-primary text-decoration-underline">OTech Engineering</a><span> &amp; Technology Solutions</span></footer>
    </div>
  </div>;
}
