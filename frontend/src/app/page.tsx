import Link from 'next/link';
import { ArrowUpRight, ArrowRight } from 'lucide-react';
import { serverApi } from '@/lib/server';
import { safeHref } from '@/lib/api';
import { sectionSettings } from '@/lib/section-settings';
import type { Site, Page, Directory } from '@/lib/types';
import { ProductCard } from '@/components/product-card';
import { Newsletter } from '@/components/shell';
export default async function Home() {
  const [site, brands] = await Promise.all([
    serverApi<Site>('/site/'),
    serverApi<Page<Directory>>('/brands/'),
  ]);
  return (
    <>
      {site.sections.map((section) => {
        const settings = sectionSettings(section.settings);
        if (section.type === 'HERO')
          return (
            <section className="hero wrap" key={section.id}>
              <div className="hero-art">
                <img
                  src={section.image || '/images/hero-original.png'}
                  alt={settings.image_alt}
                  width="1536"
                  height="1024"
                  fetchPriority="high"
                />
              </div>
              <div className="hero-content">
                {settings.eyebrow && (
                  <span className="eyebrow">
                    <span className="green-dot" />
                    {settings.eyebrow}
                  </span>
                )}
                <h1>{section.title}</h1>
                <p>{section.body || section.subtitle}</p>
                <Link className="button" href={safeHref(section.href)}>
                  {section.cta}
                  <ArrowUpRight size={19} />
                </Link>
                {(settings.footnote || settings.edition) && (
                  <div className="hero-footnote">
                    <span>{settings.footnote}</span>
                    <span>{settings.edition}</span>
                  </div>
                )}
              </div>
              {settings.caption && (
                <div className="hero-caption">
                  <span>{settings.caption}</span>
                  <ArrowUpRight size={32} />
                </div>
              )}
            </section>
          );
        if (section.type === 'PRODUCT_CAROUSEL')
          return (
            <section className="section wrap" key={section.id}>
              <div className="section-heading">
                <div>
                  {settings.eyebrow && <span className="eyebrow">{settings.eyebrow}</span>}
                  <h2>{section.title}</h2>
                  <p>{section.subtitle}</p>
                </div>
                <Link className="text-link" href={safeHref(section.href)}>
                  {section.cta}
                  <ArrowUpRight size={17} />
                </Link>
              </div>
              <div className="product-grid home-grid">
                {section.products.map((p) => (
                  <ProductCard product={p} key={p.id} />
                ))}
              </div>
            </section>
          );
        if (section.type === 'CATEGORY_GRID' && settings.tiles.length > 0)
          return (
            <section className="section wrap" key={section.id}>
              <div className="section-heading">
                <div>
                  {settings.eyebrow && <span className="eyebrow">{settings.eyebrow}</span>}
                  <h2>{section.title}</h2>
                </div>
                <p>{section.subtitle}</p>
              </div>
              <div className="category-grid">
                {settings.tiles.map(({ title, subtitle, href }, i) => (
                  <Link
                    className={`category-tile category-${i % 3}`}
                    href={href}
                    key={`${href}-${i}`}
                  >
                    <span className="category-number">0{i + 1}</span>
                    <div className="category-type">{title.toUpperCase()}</div>
                    <div>
                      <span>{subtitle}</span>
                      <ArrowUpRight />
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          );
        if (section.type === 'EDITORIAL_SPLIT')
          return (
            <section className="editorial wrap" key={section.id}>
              <div className="editorial-image">
                <img
                  src={section.image || '/images/hero-original.png'}
                  alt={settings.image_alt}
                  width="1536"
                  height="1024"
                  loading="lazy"
                />
                {settings.caption && <span>{settings.caption}</span>}
              </div>
              <div className="editorial-copy">
                <span className="eyebrow">{section.subtitle}</span>
                <h2>{section.title}</h2>
                <p>{section.body}</p>
                <Link className="button" href={safeHref(section.href)}>
                  {section.cta}
                  <ArrowUpRight size={19} />
                </Link>
              </div>
            </section>
          );
        if (section.type === 'BRAND_GRID')
          return (
            <section className="brand-section section wrap" key={section.id}>
              <div className="section-heading">
                <div>
                  <h2>{section.title}</h2>
                  <p>{section.subtitle}</p>
                </div>
                <Link className="text-link" href="/brands">
                  All brands
                  <ArrowUpRight size={18} />
                </Link>
              </div>
              <div className="brand-grid">
                {brands.results.map((b, i) => (
                  <Link
                    className={`brand-logo brand-logo-${i % 3}`}
                    href={`/brands/${b.slug}`}
                    key={b.id}
                  >
                    {b.name}
                    <span>↗</span>
                  </Link>
                ))}
              </div>
            </section>
          );
        if (section.type === 'NEWSLETTER')
          return <Newsletter key={section.id} title={section.title} subtitle={section.subtitle} />;
        if (['RICH_TEXT', 'PROMO_BANNER', 'REWARDS', 'TRUST_BAR'].includes(section.type))
          return (
            <section className="section wrap content-block" key={section.id}>
              <h2>{section.title}</h2>
              <p>{section.body || section.subtitle}</p>
              {section.href && (
                <Link className="text-link" href={safeHref(section.href)}>
                  {section.cta || 'Explore'}
                  <ArrowRight size={18} />
                </Link>
              )}
            </section>
          );
        return null;
      })}
    </>
  );
}
