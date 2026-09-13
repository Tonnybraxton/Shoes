import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { ArrowUpRight, ChevronRight } from 'lucide-react';
import { serverApi } from '@/lib/server';
import type { Page, Product, Facets, Directory, Release } from '@/lib/types';
import { Catalog } from '@/components/catalog';
import { ProductDetail } from '@/components/product-detail';
import { CartPage, CheckoutPage, OrderPage, Tracking } from '@/components/commerce';
import { Account, SavedProducts, Rewards, ReleaseDetail } from '@/components/account';
type Props = {
  params: Promise<{ path: string[] }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { path } = await params;
  if (path[0] === 'products' && path[1]) {
    try {
      const p = await serverApi<Product>(`/products/${path[1]}/`);
      return {
        title: p.seo_title || `${p.brand.name} ${p.name}`,
        description: p.seo_description || p.subtitle,
        alternates: { canonical: `/products/${p.slug}` },
        openGraph: {
          title: `${p.brand.name} ${p.name}`,
          images: p.variants[0]?.image ? [p.variants[0].image] : [],
        },
      };
    } catch {
      return { title: 'Product unavailable' };
    }
  }
  return {
    title: path[0].replaceAll('-', ' ').replace(/^./, (c) => c.toUpperCase()),
    robots: ['account', 'checkout', 'cart', 'orders', 'tracking'].includes(path[0])
      ? { index: false, follow: false }
      : undefined,
    alternates: { canonical: `/${path.join('/')}` },
  };
}
export default async function Route({ params, searchParams }: Props) {
  const { path } = await params,
    q = await searchParams,
    [section, slug] = path;
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(q))
    if (value) query.set(key, Array.isArray(value) ? value.join(',') : value);
  if (section === 'products' && slug) {
    let p: Product;
    try {
      p = await serverApi<Product>(`/products/${slug}/`);
    } catch {
      notFound();
    }
    const related = await serverApi<Page<Product>>(`/products/${slug}/related/`);
    const origin = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
    const schema = {
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: p.name,
      description: p.description,
      brand: { '@type': 'Brand', name: p.brand.name },
      image: p.variants[0]?.image ? new URL(p.variants[0].image, origin).href : undefined,
      offers: {
        '@type': 'AggregateOffer',
        priceCurrency: 'KES',
        lowPrice: Math.min(...p.variants.map((v) => Number(v.price))),
        highPrice: Math.max(...p.variants.map((v) => Number(v.price))),
        offerCount: p.variants.length,
        availability: p.variants.some((v) => v.in_stock)
          ? 'https://schema.org/InStock'
          : 'https://schema.org/OutOfStock',
      },
    };
    return (
      <>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schema).replace(/</g, '\u003c') }}
        />
        <ProductDetail product={p} related={related.results} />
      </>
    );
  }
  if (
    ['shop', 'men', 'women', 'kids', 'sale'].includes(section) ||
    (slug && ['brands', 'collections'].includes(section))
  ) {
    let title = 'Find your next pair.',
      description = 'Everyday icons. New perspectives. A rotation that feels like you.';
    if (['men', 'women', 'kids'].includes(section)) {
      query.set('gender', section);
      title = `${section === 'kids' ? 'Kids’' : section === 'men' ? 'Men’s' : 'Women’s'} shoes.`;
    }
    if (section === 'sale') {
      query.set('sale', 'true');
      title = 'Good pairs. Better prices.';
    }
    if (slug && section === 'brands') {
      query.set('brand', slug);
      title = slug.toUpperCase() + '.';
    }
    if (slug && section === 'collections') {
      query.set('collection', slug);
      title = slug.replaceAll('-', ' ') + '.';
    }
    if (query.get('search')) {
      title = `Results for “${query.get('search')}”`;
      description = 'Explore matching shoes, brands, and colorways.';
    }
    const [data, facets] = await Promise.all([
      serverApi<Page<Product>>(`/products/?${query}`),
      serverApi<Facets>('/facets/'),
    ]);
    return <Catalog data={data} facets={facets} title={title} description={description} />;
  }
  if (section === 'cart') return <CartPage />;
  if (section === 'checkout') return <CheckoutPage />;
  if (section === 'orders' && slug) return <OrderPage reference={slug} />;
  if (section === 'tracking') return <Tracking />;
  if (section === 'account') return <Account section={slug || 'profile'} />;
  if (section === 'wishlist') return <SavedProducts />;
  if (section === 'compare') return <SavedProducts kind="compare" />;
  if (section === 'recently-viewed') return <SavedProducts kind="recent" />;
  if (section === 'rewards')
    return (
      <div className="wrap section">
        <Rewards />
      </div>
    );
  if (['brands', 'collections'].includes(section)) {
    const data = await serverApi<Page<Directory>>(`/${section}/`);
    return (
      <div className="wrap">
        <div className="page-heading" style={{ paddingTop: 55 }}>
          <span className="eyebrow">EXPLORE THE ROTATION</span>
          <h1 style={{ marginTop: 14 }}>
            {section === 'brands' ? 'Different names. Shared energy.' : 'A considered collection.'}
          </h1>
          <p>
            {section === 'brands'
              ? 'Meet our fictional demonstration brands. Each with its own perspective.'
              : 'Original edits for whatever comes next.'}
          </p>
        </div>
        <div className="brand-directory">
          {data.results
            .sort((a, b) => a.name.localeCompare(b.name))
            .map((b) => (
              <Link href={`/${section}/${b.slug}`} key={b.id}>
                <h2>{b.name}</h2>
                <p>{b.description}</p>
                <span>
                  EXPLORE {b.name.toUpperCase()}
                  <ArrowUpRight size={18} />
                </span>
              </Link>
            ))}
        </div>
      </div>
    );
  }
  if (section === 'releases') {
    if (slug && !['upcoming', 'released'].includes(slug)) {
      let release: Release;
      try {
        release = await serverApi<Release>(`/releases/${slug}/`);
      } catch {
        notFound();
      }
      return <ReleaseDetail release={release} />;
    }
    if (slug) query.set('status', slug);
    const data = await serverApi<Page<Release>>(`/releases/?${query}`);
    return (
      <div className="wrap">
        <div className="page-heading" style={{ paddingTop: 55 }}>
          <span className="eyebrow">WHAT’S NEXT / WHAT’S NEW</span>
          <h1 style={{ marginTop: 14 }}>Ahead of the curve.</h1>
          <p>
            Upcoming releases and the newest additions to the rotation. All times are shown in East
            Africa Time.
          </p>
        </div>
        <nav className="tab-row" aria-label="Release status">
          <Link href="/releases" className={`pill ${!slug ? 'active' : ''}`}>
            All releases
          </Link>
          <Link className={`pill ${slug === 'upcoming' ? 'active' : ''}`} href="/releases/upcoming">
            Coming soon
          </Link>
          <Link className={`pill ${slug === 'released' ? 'active' : ''}`} href="/releases/released">
            Just released
          </Link>
        </nav>
        {data.results.length ? (
          <div className="release-grid">
            {data.results.map((r) => (
              <Link className="release-card" href={`/releases/${r.slug}`} key={r.id}>
                <img
                  src={r.image}
                  alt={`${r.name} demonstration release`}
                  width="1000"
                  height="800"
                />
                <div className="release-date">
                  <time dateTime={r.release_at}>
                    {new Date(r.release_at).toLocaleDateString('en-KE', {
                      timeZone: 'Africa/Nairobi',
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </time>
                  <span className="status-pill">{r.status}</span>
                </div>
                <h2>{r.title}</h2>
                <span className="text-link">
                  Explore release
                  <ArrowUpRight size={15} />
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h2>More good things are coming.</h2>
            <p>No releases match this view yet.</p>
            <Link href="/releases" className="button secondary">
              All releases
            </Link>
          </div>
        )}
      </div>
    );
  }
  if (section === 'help') {
    let policy: { title: string; body: string; approved: boolean };
    try {
      policy = await serverApi(`/policies/${slug || 'help'}/`);
    } catch {
      notFound();
    }
    return (
      <div className="wrap">
        <div className="breadcrumb">
          <Link href="/">Home</Link>
          <ChevronRight size={10} />
          <span>Here to help</span>
        </div>
        <div className="page-heading">
          <h1>{policy.title}</h1>
        </div>
        {!policy.approved && (
          <p className="notice demo">
            Demonstration policy draft. Business approval is required before public launch.
          </p>
        )}
        <article className="prose">{policy.body}</article>
      </div>
    );
  }
  notFound();
}
