'use client';
import { useEffect, useState } from 'react';
import { localized } from '../lib/routes.mjs';

type Slide = { id: number; title: string; description: string; background_image?: string };
export default function Hero({ slides, locale, copy }: { slides: Slide[]; locale: string; copy: { title: string; description: string; badge: string } }) {
  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    if (paused || slides.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const timer = setInterval(() => setCurrent(index => (index + 1) % slides.length), 6000);
    return () => clearInterval(timer);
  }, [paused, slides.length]);
  const slide = slides[current];
  return <section className="hero" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)} onFocus={() => setPaused(true)} aria-roledescription="carousel" aria-label="Featured projects">
    {slide?.background_image && <img className="hero-image" src={slide.background_image} alt="" />}
    <div className="hero-content container">
      <p className="eyebrow">{copy.badge}</p>
      <h1>{slide?.title || copy.title}</h1>
      <p>{slide?.description || copy.description}</p>
      <div className="actions"><a className="button" href={localized('/about-us/services/', locale)}>Explore our services <span aria-hidden="true">↗</span></a><a className="button outline" href={localized('/contact-us/', locale)}>Get in touch</a></div>
      {slides.length > 1 && <div className="slide-controls">{slides.map((item, index) => <button key={item.id} onClick={() => setCurrent(index)} aria-label={`Show project ${index + 1}`} aria-pressed={index === current} className={index === current ? 'selected' : ''} />)}<button className="pause" onClick={() => setPaused(value => !value)} aria-label={paused ? 'Play slideshow' : 'Pause slideshow'}>{paused ? 'Play' : 'Pause'}</button></div>}
    </div>
  </section>;
}
