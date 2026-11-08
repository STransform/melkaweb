import { cleanHtml, embedUrl, safeUrl, text, type Item } from '../lib/api';
import { localized } from '../lib/routes.mjs';

export function RichText({ value }: { value: unknown }) {
  return <div className="prose" dangerouslySetInnerHTML={{ __html: cleanHtml(value) }} />;
}
export function Card({ item, locale, compact = false }: { item: Item; locale: string; compact?: boolean }) {
  const title = text(item.title || item.infr_title || item.invn_title || item.title1 || item.full_name || item.name);
  const image = safeUrl(item.image || item.images || item.featured_image || item.infr_image || item.invn_image || item.image_one);
  const url = safeUrl(item.url);
  const file = safeUrl(item.file || item.bid_document);
  const video = embedUrl(item.link);
  return <article className={`card ${compact ? 'compact' : ''}`}>
    {image && <a href={url ? localized(url, locale) : image} tabIndex={url ? 0 : -1}><img className="card-image" src={image} alt={title} loading="lazy" /></a>}
    {video && <iframe className="video" src={video} title={title || 'Video'} loading="lazy" allowFullScreen referrerPolicy="strict-origin-when-cross-origin" />}
    <div className="card-body">{item.category ? <p className="eyebrow">{text(item.category)}</p> : null}
      {title && <h2>{url ? <a href={localized(url, locale)}>{title}</a> : title}</h2>}
      {item.position || item.role ? <p>{text(item.position || item.role)}</p> : null}
      {item.author ? <p className="meta">{text(item.author)}</p> : null}
      {['date', 'time', 'location', 'bid_open_date', 'bid_close_date', 'created_at', 'created_date', 'upload_date'].map(field => item[field] ? <p className="meta" key={field}>{field.includes('bid_') ? field === 'bid_open_date' ? 'Opens: ' : 'Closes: ' : ''}{text(item[field]).replace('T', ' ').replace(/Z$/, '')}</p> : null)}
      <div className={compact ? 'excerpt' : ''}><RichText value={item.content || item.description || item.infr_content || item.invn_content || item.content1} /></div>
      {!compact && ['mission', 'vision', 'values', 'content2', 'content3', 'management_board_content', 'execution_team_content'].map(field => item[field] ? <section key={field}><h3>{text(item[field.replace('content', 'title')] || field.replaceAll('_', ' '))}</h3><RichText value={item[field]} /></section> : null)}
      {!compact && ['image_two', 'image_three', 'execution_team_image'].map(field => safeUrl(item[field]) ? <img className="card-image" key={field} src={safeUrl(item[field])} alt={title} loading="lazy" /> : null)}
      {url && compact && <a className="text-link" href={localized(url, locale)}>Read more ↗</a>}
      {file && <a className="button" href={file}>Download document ↓</a>}
      {!video && safeUrl(item.link) && <a href={safeUrl(item.link)}>Watch video ↗</a>}
    </div>
  </article>;
}
export function Grid({ items, locale, compact = false }: { items: Item[]; locale: string; compact?: boolean }) {
  if (!items.length) return <p className="empty-state">No content has been published in this section yet.</p>;
  return <div className="content-grid">{items.map(item => <Card key={item.id} item={item} locale={locale} compact={compact} />)}</div>;
}
