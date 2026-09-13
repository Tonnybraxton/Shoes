'use client';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  Heart,
  Plus,
  Truck,
  RotateCcw,
  Maximize2,
  ChevronRight,
  ArrowRight,
  Bell,
  Check,
} from 'lucide-react';
import type { Product, Page } from '@/lib/types';
import { api, post, money } from '@/lib/api';
import { imageSrcSet } from '@/lib/product-images';
import { useStore } from './store-provider';
import { Dialog } from './dialog';
import { ProductCard } from './product-card';
type Review = {
  id: number;
  author: string;
  rating: number;
  title: string;
  body: string;
  verified_purchase: boolean;
};
export function ProductDetail({ product, related }: { product: Product; related: Product[] }) {
  const query = useSearchParams(),
    { add, wishlist, toggleWish, notify, user, toggleCompare, compare } = useStore();
  const [color, setColor] = useState(Number(query.get('color')) || product.default_variant_id),
    [size, setSize] = useState<number | null>(null),
    [image, setImage] = useState(0),
    [zoom, setZoom] = useState(false),
    [guide, setGuide] = useState(false),
    [fit, setFit] = useState(false),
    [fitResult, setFitResult] = useState(''),
    [restock, setRestock] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(''),
    [reviews, setReviews] = useState<Review[]>([]);
  const variant = product.variants.find((v) => v.id === color) || product.variants[0],
    chosen = variant?.sizes.find((s) => s.id === size),
    picture = variant?.images[image] || variant?.images[0];
  useEffect(() => {
    api<Page<Review>>(`/products/${product.slug}/reviews/`)
      .then((r) => setReviews(r.results))
      .catch(() => {});
    if (localStorage.getItem('soleline:consent') === 'all') {
      try {
        const ids: number[] = JSON.parse(localStorage.getItem('soleline:recent') || '[]');
        localStorage.setItem(
          'soleline:recent',
          JSON.stringify([product.id, ...ids.filter((id) => id !== product.id)].slice(0, 12)),
        );
      } catch {}
    }
  }, [product.slug, product.id]);
  if (!variant)
    return (
      <div className="empty-state">
        <h1>This product is being prepared.</h1>
        <Link href="/shop">Explore available shoes</Link>
      </div>
    );
  const changeColor = (id: number) => {
    setColor(id);
    setSize(null);
    setImage(0);
    setError('');
    const next = new URL(window.location.href);
    next.searchParams.set('color', String(id));
    window.history.replaceState(null, '', next);
  };
  async function addToBag() {
    if (!chosen) {
      setError('Choose a size before adding this pair.');
      document.getElementById('size-picker')?.focus();
      return;
    }
    if (chosen.available <= 0) {
      setRestock(true);
      return;
    }
    setBusy(true);
    setError('');
    try {
      await add(chosen.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="wrap">
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <Link href="/">Home</Link>
        <ChevronRight size={10} />
        <Link href="/shop">Shoes</Link>
        <ChevronRight size={10} />
        <Link href={`/brands/${product.brand.slug}`}>{product.brand.name}</Link>
        <ChevronRight size={10} />
        <span>{product.name}</span>
      </nav>
      <div className="pdp">
        <div className="pdp-gallery">
          <button
            className="pdp-main-image"
            onClick={() => setZoom(true)}
            aria-label={`Zoom ${product.name} ${variant.color_name}`}
          >
            <img
              key={`${color}-${image}`}
              src={picture?.url || variant.image}
              srcSet={imageSrcSet(picture)}
              sizes="(max-width: 900px) 100vw, 55vw"
              alt={picture?.alt || `${product.name} ${variant.color_name}`}
              width="1000"
              height="800"
              fetchPriority="high"
            />
            <span className="zoom-hint">
              <Maximize2 size={19} />
            </span>
          </button>
          <div className="gallery-thumbs" aria-label="Product views">
            {variant.images.map((img, i) => (
              <button
                className={i === image ? 'active' : ''}
                aria-label={`View ${img.view_type.toLowerCase()}`}
                aria-pressed={i === image}
                key={img.id}
                onClick={() => setImage(i)}
              >
                <img
                  src={img.url}
                  srcSet={imageSrcSet(img)}
                  sizes="100px"
                  alt=""
                  width="100"
                  height="80"
                />
              </button>
            ))}
          </div>
          <div className="notice demo">
            Fictional demonstration merchandise. Images and specifications are illustrative.
          </div>
        </div>
        <div className="pdp-info">
          <Link className="brand-label" href={`/brands/${product.brand.slug}`}>
            {product.brand.name}
          </Link>
          <h1>{product.name}</h1>
          <p className="muted">{product.subtitle}</p>
          <div className="price">
            <span>{product.see_price_in_bag ? 'See price in bag' : money(variant.price)}</span>
            {variant.compare_at_price &&
              Number(variant.compare_at_price) > Number(variant.price) && (
                <del>{money(variant.compare_at_price)}</del>
              )}
          </div>
          {product.review_count > 0 && (
            <a href="#reviews" className="text-link">
              ★ {product.rating} · {product.review_count} verified reviews
            </a>
          )}
          <div className="pdp-color-label" aria-live="polite">
            Color: <strong>{variant.color_name}</strong>
          </div>
          <div className="pdp-colors">
            {product.variants.map((v) => (
              <button
                key={v.id}
                className={v.id === color ? 'active' : ''}
                aria-label={`Select ${v.color_name} colorway`}
                aria-pressed={v.id === color}
                onClick={() => changeColor(v.id)}
              >
                <img
                  src={v.image}
                  srcSet={imageSrcSet(v.images[0])}
                  sizes="100px"
                  alt=""
                  width="100"
                  height="80"
                />
              </button>
            ))}
          </div>
          <div className="size-heading">
            <strong>Select size · {variant.sizes[0]?.system || 'EU'}</strong>
            <button onClick={() => setGuide(true)}>Size guide</button>
          </div>
          <div
            className="sizes-grid"
            id="size-picker"
            tabIndex={-1}
            role="group"
            aria-label="Choose your size"
          >
            {variant.sizes.map((s) => (
              <button
                key={s.id}
                className={s.id === size ? 'active' : ''}
                aria-pressed={s.id === size}
                aria-disabled={s.available <= 0}
                aria-label={`Size ${s.system} ${s.label}${s.available <= 0 ? ', out of stock, request notification' : ''}`}
                onClick={() => {
                  setSize(s.id);
                  setError('');
                  if (s.available <= 0) setRestock(true);
                }}
              >
                {s.label}
              </button>
            ))}
          </div>
          <p className="size-notice" aria-live="polite">
            {chosen
              ? chosen.available === 0
                ? 'This size is currently unavailable.'
                : chosen.available <= 3
                  ? `Only ${chosen.available} left in this size.`
                  : 'Your size is in stock.'
              : product.fit === 'true'
                ? 'Designed to fit true to size.'
                : `This style runs ${product.fit}.`}
          </p>
          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}
          <div className="pdp-actions">
            <button className="button" onClick={() => void addToBag()} disabled={busy}>
              {busy
                ? 'Adding…'
                : chosen?.available === 0
                  ? 'Notify me when available'
                  : 'Add to bag'}
              {chosen?.available === 0 ? <Bell size={17} /> : <ArrowRight size={18} />}
            </button>
            <button
              className={`icon-button ${wishlist.includes(product.id) ? 'selected' : ''}`}
              aria-label="Save to wishlist"
              aria-pressed={wishlist.includes(product.id)}
              onClick={() => void toggleWish(product)}
            >
              <Heart size={21} />
            </button>
          </div>
          <div className="pdp-service">
            <Truck size={17} />
            <span>Delivery calculated in your bag. Shipping within Kenya.</span>
          </div>
          <div className="pdp-service">
            <RotateCcw size={17} />
            <Link href="/help/returns">View returns & exchange information</Link>
          </div>
          <div className="fit-tools">
            <button className="button secondary" onClick={() => setFit(true)}>
              Find your fit
            </button>
            <button className="compare-toggle" onClick={() => toggleCompare(product.id)}>
              {compare.includes(product.id) ? <Check size={13} /> : <Plus size={13} />}Compare this
              pair
            </button>
          </div>
          <div className="pdp-accordion">
            <details open>
              <summary>A closer look</summary>
              <p>{product.description}</p>
              <ul>
                {product.details.map((d) => (
                  <li key={d}>{d}</li>
                ))}
              </ul>
            </details>
            <details>
              <summary>Fit & feel</summary>
              <p>
                This style runs {product.fit === 'true' ? 'true to size' : product.fit}, with a{' '}
                {product.width} width. Fit guidance is illustrative for this DEMO product.
              </p>
            </details>
            <details>
              <summary>Delivery & returns</summary>
              <p>Delivery costs and eligible promotions are calculated securely at checkout.</p>
              <Link className="text-link" href="/help/shipping">
                Delivery details
              </Link>
            </details>
          </div>
        </div>
      </div>
      <section id="reviews" className="review-section">
        <h2>From the rotation.</h2>
        <p>
          {reviews.length
            ? `${reviews.length} verified customer reviews`
            : 'No reviews yet. Reviews are accepted from customers after their order is delivered.'}
        </p>
        {reviews.map((r) => (
          <article className="review" key={r.id}>
            <span className="eyebrow">
              {'★'.repeat(r.rating)} · {r.author} · Verified purchase
            </span>
            <h3>{r.title}</h3>
            <p>{r.body}</p>
          </article>
        ))}
        {user && (
          <details>
            <summary>Review your delivered purchase</summary>
            <form
              style={{ maxWidth: 500, marginTop: 20 }}
              onSubmit={async (e) => {
                e.preventDefault();
                const f = new FormData(e.currentTarget);
                try {
                  await post(`/products/${product.slug}/reviews/`, {
                    rating: Number(f.get('rating')),
                    title: f.get('title'),
                    body: f.get('body'),
                    comfort: Number(f.get('comfort')),
                    fit: f.get('fit'),
                  });
                  notify('Review submitted for moderation.');
                } catch (e) {
                  notify((e as Error).message);
                }
              }}
            >
              <label className="field">
                <span>Rating</span>
                <select name="rating">
                  {[5, 4, 3, 2, 1].map((n) => (
                    <option key={n} value={n}>
                      {n} stars
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Title</span>
                <input name="title" required maxLength={120} />
              </label>
              <label className="field">
                <span>Your experience</span>
                <textarea name="body" required maxLength={2000} />
              </label>
              <div className="form-grid">
                <label className="field">
                  <span>Fit</span>
                  <select name="fit">
                    <option value="true">True to size</option>
                    <option value="small">Runs small</option>
                    <option value="large">Runs large</option>
                  </select>
                </label>
                <label className="field">
                  <span>Comfort</span>
                  <select name="comfort">
                    {[5, 4, 3, 2, 1].map((n) => (
                      <option key={n}>{n}</option>
                    ))}
                  </select>
                </label>
              </div>
              <button className="button">Submit review</button>
            </form>
          </details>
        )}
      </section>
      {related.length > 0 && (
        <section className="section">
          <div className="section-heading">
            <div>
              <h2>Keep good company.</h2>
              <p>Similar styles and more from {product.brand.name}.</p>
            </div>
          </div>
          <div className="product-grid">
            {related.slice(0, 4).map((p) => (
              <ProductCard product={p} key={p.id} />
            ))}
          </div>
        </section>
      )}
      <Dialog
        open={zoom}
        onClose={() => setZoom(false)}
        title={`${product.name} · ${variant.color_name}`}
      >
        <img
          className="zoom-image"
          src={picture?.url || variant.image}
          alt={picture?.alt || product.name}
          width="1000"
          height="800"
        />
        {variant.images.length > 1 && (
          <div className="pagination">
            <button
              className="button secondary"
              onClick={() => setImage((image + variant.images.length - 1) % variant.images.length)}
            >
              Previous view
            </button>
            <button
              className="button secondary"
              onClick={() => setImage((image + 1) % variant.images.length)}
            >
              Next view
            </button>
          </div>
        )}
      </Dialog>
      <Dialog open={guide} onClose={() => setGuide(false)} title="A note on sizing">
        <p>
          Choose the size system shown on this product. Sizes are normalized per brand and model;
          conversions should be verified against the brand’s chart before purchase.
        </p>
        <div className="notice">
          This DEMO catalog uses EU sizes. No unverified cross-system conversion is provided.
        </div>
        <div className="filter-sizes">
          {variant.sizes.map((s) => (
            <span className="pill" key={s.id}>
              {s.system} {s.label}
            </span>
          ))}
        </div>
      </Dialog>
      <Dialog open={fit} onClose={() => setFit(false)} title="Find your fit">
        <p className="muted">
          A simple recommendation based on your usual size and this style’s fit profile.
        </p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget),
              usual = Number(f.get('usual')),
              preference = f.get('preference');
            const target =
              usual +
              (product.fit === 'small' ? 1 : product.fit === 'large' ? -1 : 0) +
              (preference === 'roomy' ? 1 : preference === 'snug' ? -1 : 0);
            const closest = variant.sizes.reduce((best, s) =>
              Math.abs(Number(s.label) - target) < Math.abs(Number(best.label) - target) ? s : best,
            );
            setFitResult(
              `Try ${closest.system} ${closest.label}. Your usual size is ${usual}; this style runs ${product.fit === 'true' ? 'true to size' : product.fit} and you prefer a ${preference} fit. This is guidance, not a fit guarantee.`,
            );
          }}
        >
          <label className="field" style={{ marginTop: 22 }}>
            <span>Your usual EU size</span>
            <select name="usual">
              {variant.sizes.map((s) => (
                <option key={s.id}>{s.label}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Your preferred fit</span>
            <select name="preference">
              <option value="regular">Regular</option>
              <option value="snug">Snug</option>
              <option value="roomy">Roomy</option>
            </select>
          </label>
          <button className="button">Get my recommendation</button>
        </form>
        {fitResult && (
          <p className="notice" role="status">
            {fitResult}
          </p>
        )}
      </Dialog>
      <Dialog open={restock} onClose={() => setRestock(false)} title="Your size. Back in the loop.">
        <p>
          We’ll notify you about {product.name} in {variant.color_name}, {chosen?.system}{' '}
          {chosen?.label}.
        </p>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            try {
              await post('/restock-alerts/', {
                email: new FormData(e.currentTarget).get('email'),
                variant_size_id: chosen?.id,
                consent: true,
              });
              notify('Your restock notification is saved.');
              setRestock(false);
            } catch (e) {
              notify((e as Error).message);
            }
          }}
        >
          <label className="field" style={{ marginTop: 22 }}>
            <span>Email address</span>
            <input name="email" type="email" defaultValue={user?.email} required />
          </label>
          <label className="consent-check">
            <input type="checkbox" required />
            Email me about this exact size and colorway.
          </label>
          <button className="button full" style={{ marginTop: 20 }}>
            Notify me
          </button>
        </form>
      </Dialog>
    </div>
  );
}
