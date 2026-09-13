'use client';
import { useOptimistic, useState, useTransition } from 'react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowRight, ChevronRight, SlidersHorizontal, X } from 'lucide-react';
import type { Facets, Page, Product } from '@/lib/types';
import { ProductCard } from './product-card';
import { Dialog } from './dialog';
export function Catalog({
  data,
  facets,
  title,
  description,
}: {
  data: Page<Product>;
  facets: Facets;
  title: string;
  description: string;
}) {
  const router = useRouter(),
    path = usePathname(),
    query = useSearchParams();
  const [pending, startTransition] = useTransition(),
    [open, setOpen] = useState(false);
  const [optimisticQuery, setOptimisticQuery] = useOptimistic(query.toString());
  const activeQuery = new URLSearchParams(optimisticQuery);
  function change(key: string, value: string, multiple = false) {
    const next = new URLSearchParams(activeQuery);
    if (multiple) {
      const old = (next.get(key) || '').split(',').filter(Boolean);
      const values = old.includes(value) ? old.filter((v) => v !== value) : [...old, value];
      if (values.length) next.set(key, values.join(','));
      else next.delete(key);
    } else if (value) next.set(key, value);
    else next.delete(key);
    if (key !== 'page') next.delete('page');
    startTransition(() => {
      setOptimisticQuery(next.toString());
      router.push(`${path}?${next}`, { scroll: false });
    });
  }
  const selected = (key: string, value: string) =>
    (activeQuery.get(key) || '').split(',').includes(value);
  const filters = (
    <>
      <details className="filter-section" open>
        <summary>Brand</summary>
        <div className="filter-options">
          {facets.brands.map((b) => (
            <label key={b.slug}>
              <input
                type="checkbox"
                checked={selected('brand', b.slug)}
                onChange={() => change('brand', b.slug, true)}
              />
              {b.name}
              <span>{b.count}</span>
            </label>
          ))}
        </div>
      </details>
      <details className="filter-section" open>
        <summary>Size · EU</summary>
        <div className="filter-sizes">
          {facets.sizes
            .filter((s) => s.system === 'EU')
            .map((s) => (
              <button
                key={s.id}
                aria-pressed={selected('size', s.label)}
                className={selected('size', s.label) ? 'active' : ''}
                onClick={() => change('size', s.label, true)}
              >
                {s.label}
              </button>
            ))}
        </div>
      </details>
      <details className="filter-section" open>
        <summary>Category</summary>
        <div className="filter-options">
          {facets.categories.map((c) => (
            <label key={c.slug}>
              <input
                type="checkbox"
                checked={selected('category', c.slug)}
                onChange={() => change('category', c.slug, true)}
              />
              {c.name}
              <span>{c.count}</span>
            </label>
          ))}
        </div>
      </details>
      <details className="filter-section" open>
        <summary>Color</summary>
        <div className="filter-options">
          {facets.colors.map((c) => (
            <label key={c.name}>
              <input
                type="checkbox"
                checked={selected('color', c.name)}
                onChange={() => change('color', c.name, true)}
              />
              <i
                className="color-dot"
                style={{
                  background: c.code,
                  width: 11,
                  height: 11,
                  borderRadius: '50%',
                  border: '1px solid #a5aa9f',
                }}
              />
              {c.name}
              <span>{c.count}</span>
            </label>
          ))}
        </div>
      </details>
      <details className="filter-section">
        <summary>Price · KSh</summary>
        <form
          className="filter-price"
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            const next = new URLSearchParams(activeQuery);
            for (const key of ['min_price', 'max_price']) {
              const value = String(form.get(key) || '');
              if (value) next.set(key, value);
              else next.delete(key);
            }
            next.delete('page');
            startTransition(() => {
              setOptimisticQuery(next.toString());
              router.push(`${path}?${next}`, { scroll: false });
            });
          }}
        >
          <input
            name="min_price"
            type="number"
            min="0"
            aria-label="Minimum price"
            placeholder="Min"
            defaultValue={query.get('min_price') || ''}
          />
          <input
            name="max_price"
            type="number"
            min="0"
            aria-label="Maximum price"
            placeholder="Max"
            defaultValue={query.get('max_price') || ''}
          />
          <button aria-label="Apply price range">
            <ArrowRight size={15} />
          </button>
        </form>
      </details>
      <details className="filter-section" open>
        <summary>The finer details</summary>
        <div className="filter-options">
          {[
            ['in_stock', 'In stock'],
            ['sale', 'On sale'],
            ['new', 'New arrivals'],
            ['best', 'Bestsellers'],
            ['limited', 'Limited releases'],
            ['promo_eligible', 'Promo eligible'],
            ['free_shipping', 'Free shipping'],
          ].map(([key, label]) => (
            <label key={key}>
              <input
                type="checkbox"
                checked={activeQuery.get(key) === 'true'}
                onChange={() => change(key, activeQuery.get(key) === 'true' ? '' : 'true')}
              />
              {label}
            </label>
          ))}
        </div>
      </details>
    </>
  );
  const chips = Array.from(activeQuery.entries()).filter(
    ([key]) => !['sort', 'page'].includes(key),
  );
  return (
    <div className="wrap">
      <div className="breadcrumb">
        <Link href="/">Home</Link>
        <ChevronRight size={10} />
        <span>{title}</span>
      </div>
      <div className="page-heading">
        <span className="eyebrow">FIND YOUR NEXT ROTATION</span>
        <h1 style={{ marginTop: 12 }}>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="list-toolbar">
        <button className="filter-mobile" onClick={() => setOpen(true)}>
          <SlidersHorizontal size={16} />
          Filters {chips.length > 0 && `(${chips.length})`}
        </button>
        <span className="result-count" role="status">
          {pending ? 'Updating collection…' : `${data.count} pairs to make your own`}
        </span>
        <label>
          Sort by{' '}
          <select
            value={activeQuery.get('sort') || 'featured'}
            onChange={(e) => change('sort', e.target.value)}
            aria-label="Sort products"
          >
            {[
              ['featured', 'Featured'],
              ['newest', 'New arrivals'],
              ['bestselling', 'Bestselling'],
              ['rating', 'Customer rating'],
              ['price_asc', 'Price: low to high'],
              ['price_desc', 'Price: high to low'],
              ['name', 'Name: A–Z'],
            ].map(([v, l]) => (
              <option value={v} key={v}>
                {l}
              </option>
            ))}
          </select>
        </label>
      </div>
      {chips.length > 0 && (
        <div className="active-filters">
          {chips.map(([k, v]) => (
            <button key={k} onClick={() => change(k, '')} aria-label={`Remove ${k} filter`}>
              {k.replaceAll('_', ' ')}: {v.replaceAll(',', ' / ')}
              <X size={12} />
            </button>
          ))}
          <button onClick={() => router.push(path, { scroll: false })}>Clear all</button>
        </div>
      )}
      <div className="catalog-layout">
        <aside className="filter-sidebar" aria-label="Product filters">
          {filters}
        </aside>
        <div aria-busy={pending} style={{ opacity: pending ? 0.6 : 1 }}>
          {data.results.length ? (
            <div className="product-grid catalog-grid">
              {data.results.map((p) => (
                <ProductCard product={p} key={p.id} />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <h2>No pairs in this combination.</h2>
              <p>Try removing a filter or search for another style.</p>
              <button className="button secondary" onClick={() => router.push(path)}>
                Reset filters
              </button>
            </div>
          )}
          {data.count > 24 && (
            <div className="pagination">
              <button
                className="button secondary"
                disabled={!data.previous}
                onClick={() => change('page', String(Number(query.get('page') || 1) - 1))}
              >
                Previous
              </button>
              <span>Page {query.get('page') || 1}</span>
              <button
                className="button secondary"
                disabled={!data.next}
                onClick={() => change('page', String(Number(query.get('page') || 1) + 1))}
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
      <Dialog open={open} onClose={() => setOpen(false)} title="Find your pair">
        {filters}
        <button className="button full" style={{ marginTop: 25 }} onClick={() => setOpen(false)}>
          Show {data.count} pairs
        </button>
      </Dialog>
    </div>
  );
}
