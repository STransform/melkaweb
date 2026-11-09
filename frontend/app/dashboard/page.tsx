import Link from 'next/link';
import { headers } from 'next/headers';

type Stats = { counts: Record<string, number>; messages: { id: number; full_name: string; email: string; phone: string; subject: string; sent_date: string }[] };
async function getStats(): Promise<Stats> {
  const incoming = await headers();
  const response = await fetch(`${process.env.DJANGO_ORIGIN || 'http://127.0.0.1:8000'}/api/frontend/admin-stats/`, { cache: 'no-store', headers: { cookie: incoming.get('cookie') || '' } });
  if (!response.ok) throw new Error('Unable to load dashboard statistics.');
  return response.json();
}
const cards = [
  ['Gallery Images', 'galleries', 'GalleryImage', 'primary', 'bx bx-image'], ['Videos', 'videos', 'GalleryVideo', 'secondary', 'bx bx-video'], ['Documents', 'documents', 'Document', 'warning', 'bx bx-file'], ['Vacancies', 'jobs', 'Job', 'success', 'bx bx-briefcase'], ['Blogs', 'blogs', 'Blog', 'secondary', 'bx bx-news'], ['Contact Us messages', 'messages', 'ContactUs', 'success', 'bx bx-envelope'],
];
export default async function DashboardPage() {
  const { counts, messages } = await getStats();
  return <>
    <div className="d-md-flex d-block align-items-center justify-content-between my-4 page-header-breadcrumb"><h1 className="page-title fw-semibold fs-18 mb-0">Admin</h1><nav><ol className="breadcrumb mb-0"><li className="breadcrumb-item">Dashboards</li><li className="breadcrumb-item active">Admin</li></ol></nav></div>
    <div className="col-xl-12"><div className="card custom-card"><div className="card-header justify-content-between"><div className="card-title">Web Statics</div></div><div className="card-body"><div className="row gy-xl-0 gy-3">{cards.map(([label, key, model, color, icon]) => <div className="col-xxl-3 col-xl-3 col-lg-6 col-md-6 col-sm-6 col-12" key={model}><Link href={`/dashboard/list/${model}/`} className={`category-link ${color} text-center`}><i className={`${icon} category-svg`} style={{ fontSize: '3rem' }} /><p className="fs-14 mb-1 text-default fw-semibold">{label}</p><span className="fs-11 text-muted">{counts[key] || 0}</span></Link></div>)}</div></div></div></div>
    <div className="row"><div className="col-xl-12"><div className="card custom-card"><div className="card-header"><h5>Latest Messages From Visitor</h5></div><div className="card-body"><div className="table-responsive"><table className="table table-bordered text-nowrap w-100"><thead><tr>{['Name', 'Email', 'Phone', 'Subject', 'Date'].map(label => <th key={label}>{label}</th>)}</tr></thead><tbody>{messages.map(message => <tr key={message.id}><td>{message.full_name.length > 20 ? message.full_name.slice(0, 19) + '…' : message.full_name}</td><td>{message.email.length > 20 ? message.email.slice(0, 19) + '…' : message.email}</td><td>{message.phone}</td><td>{message.subject}</td><td>{message.sent_date}</td></tr>)}</tbody></table></div></div></div></div></div>
  </>;
}
