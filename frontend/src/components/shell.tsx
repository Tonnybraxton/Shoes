'use client';
import { useState, useEffect, useSyncExternalStore } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Search,
  Heart,
  ShoppingBag,
  UserRound,
  Menu,
  X,
  ArrowRight,
  ArrowUpRight,
  Pause,
  Play,
  ChevronDown,
  ShieldCheck,
  Truck,
  RotateCcw,
} from 'lucide-react';
import { useStore } from './store-provider';
import { Dialog } from './dialog';
import { api, post, safeHref, money } from '@/lib/api';
import type { Product } from '@/lib/types';

export function Header() {
  const { site, cart, wishlist } = useStore(),
    router = useRouter();
  const [menu, setMenu] = useState(false),
    [search, setSearch] = useState(false),
    [q, setQ] = useState(''),
    [results, setResults] = useState<Product[]>([]),
    [loading, setLoading] = useState(false),
    [error, setError] = useState(''),
    [cursor, setCursor] = useState(-1),
    [announcement, setAnnouncement] = useState(0),
    [paused, setPaused] = useState(false),
    [dismissed, setDismissed] = useState(false);
  useEffect(() => {
    if (paused || site.announcements.length < 2) return;
    const t = setInterval(() => setAnnouncement((n) => (n + 1) % site.announcements.length), 6000);
    return () => clearInterval(t);
  }, [paused, site.announcements.length]);
  useEffect(() => {
    if (q.trim().length < 2) return;
    const controller = new AbortController();
    const t = setTimeout(() => {
      setLoading(true);
      setError('');
      api<{ products: Product[] }>(`/search/?q=${encodeURIComponent(q)}`, {
        signal: controller.signal,
      })
        .then((r) => {
          setResults(r.products);
          setCursor(-1);
        })
        .catch((e) => {
          if (e.name !== 'AbortError') setError('Search is unavailable. Please try again.');
        })
        .finally(() => setLoading(false));
    }, 250);
    return () => {
      clearTimeout(t);
      controller.abort();
    };
  }, [q]);
  const a = site.announcements[announcement];
  function submitSearch() {
    setSearch(false);
    router.push(`/shop?search=${encodeURIComponent(q)}`);
  }
  return (
    <>
      {!dismissed && a && (
        <div className="announcement">
          <span>THE WORLD MOVES. MAKE IT YOURS.</span>
          <Link href={safeHref(a.href || '/shop')}>
            {a.text} <ArrowRight size={13} />
          </Link>
          <div>
            {site.announcements.length > 1 && (
              <button
                aria-label={paused ? 'Resume announcements' : 'Pause announcements'}
                onClick={() => setPaused(!paused)}
              >
                {paused ? <Play size={12} /> : <Pause size={12} />}
              </button>
            )}
            <button aria-label="Dismiss announcement" onClick={() => setDismissed(true)}>
              <X size={13} />
            </button>
          </div>
        </div>
      )}
      <header className="site-header">
        <div className="header-main wrap">
          <button
            className="icon-button mobile-menu-button"
            aria-label="Open navigation"
            onClick={() => setMenu(true)}
          >
            <Menu />
          </button>
          <Link href="/" className="wordmark" aria-label={`${site.name} home`}>
            {site.name}
            <span className="wordmark-dot" />
          </Link>
          <nav className="desktop-nav" aria-label="Main navigation">
            {site.navigation.map((n) => (
              <div className="nav-item" key={n.label}>
                <Link className={n.label === 'Sale' ? 'sale-text' : ''} href={safeHref(n.href)}>
                  {n.label}
                  {n.children.length > 0 && <ChevronDown size={11} />}
                </Link>
                {n.children.length > 0 && (
                  <div className="mega-menu">
                    <div>
                      <span className="eyebrow">FIND YOUR NEXT PAIR</span>
                      <Link href={safeHref(n.href)} className="mega-title">
                        Explore {n.label} <ArrowUpRight />
                      </Link>
                    </div>
                    <div className="mega-links">
                      {n.children.map((c) => (
                        <Link key={c.label} href={safeHref(c.href)}>
                          {c.label}
                          <ArrowRight size={14} />
                        </Link>
                      ))}
                    </div>
                    <div className="mega-feature">
                      <span>YOUR DAILY ROTATION.</span>
                      <Link href="/collections/daily-rotation">
                        Discover the edit <ArrowUpRight size={18} />
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </nav>
          <div className="header-actions">
            <button
              className="header-search"
              aria-label="Search the store"
              onClick={() => setSearch(true)}
            >
              <Search size={19} />
              <span>Find your next pair</span>
              <kbd>/</kbd>
            </button>
            <Link className="icon-button account-link" href="/account" aria-label="Your account">
              <UserRound size={21} />
            </Link>
            <Link
              className="icon-button"
              href="/wishlist"
              aria-label={`Wishlist, ${wishlist.length} saved`}
            >
              <Heart size={21} />
              {wishlist.length > 0 && <span className="count">{wishlist.length}</span>}
            </Link>
            <Link
              className="icon-button"
              href="/cart"
              aria-label={`Shopping bag, ${cart?.items.reduce((n, i) => n + i.quantity, 0) || 0} items`}
            >
              <ShoppingBag size={21} />
              <span className="count">{cart?.items.reduce((n, i) => n + i.quantity, 0) || 0}</span>
            </Link>
          </div>
        </div>
      </header>
      <Dialog open={menu} onClose={() => setMenu(false)} title="Explore SOLELINE">
        <nav className="mobile-nav" aria-label="Mobile navigation">
          {site.navigation.map((n) => (
            <div key={n.label}>
              <Link href={safeHref(n.href)} onClick={() => setMenu(false)}>
                {n.label}
                <ArrowUpRight size={18} />
              </Link>
              {n.children.length > 0 && (
                <details>
                  <summary>Shop categories</summary>
                  {n.children.map((c) => (
                    <Link href={safeHref(c.href)} key={c.label} onClick={() => setMenu(false)}>
                      {c.label}
                    </Link>
                  ))}
                </details>
              )}
            </div>
          ))}
          <Link href="/account" onClick={() => setMenu(false)}>
            My account
          </Link>
          <Link href="/tracking" onClick={() => setMenu(false)}>
            Track an order
          </Link>
        </nav>
      </Dialog>
      <Dialog open={search} onClose={() => setSearch(false)} title="Find your next pair">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitSearch();
          }}
        >
          <label htmlFor="store-search" className="sr-only">
            Search products, brands, or colors
          </label>
          <div className="search-input">
            <Search />
            <input
              id="store-search"
              placeholder="Try a brand, silhouette, or color…"
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setCursor(-1);
                if (e.target.value.trim().length < 2) setResults([]);
              }}
              autoComplete="off"
              role="combobox"
              aria-expanded={results.length > 0}
              aria-controls="search-results"
              aria-activedescendant={cursor >= 0 ? `search-option-${cursor}` : undefined}
              onKeyDown={(e) => {
                if (e.key === 'ArrowDown') {
                  e.preventDefault();
                  setCursor((x) => Math.min(x + 1, results.length - 1));
                }
                if (e.key === 'ArrowUp') {
                  e.preventDefault();
                  setCursor((x) => Math.max(x - 1, 0));
                }
                if (e.key === 'Enter' && cursor >= 0 && results[cursor]) {
                  e.preventDefault();
                  setSearch(false);
                  router.push(`/products/${results[cursor].slug}`);
                }
              }}
            />
            <button className="icon-button" type="submit" aria-label="Submit search">
              <ArrowRight />
            </button>
          </div>
        </form>
        <div aria-live="polite" className="muted search-status">
          {loading
            ? 'Searching…'
            : error ||
              (q.length < 2
                ? 'Enter at least two characters to explore the collection.'
                : `${results.length} suggestions`)}
        </div>
        <div id="search-results" role="listbox" aria-label="Search suggestions">
          {results.map((p, i) => (
            <Link
              role="option"
              aria-selected={i === cursor}
              id={`search-option-${i}`}
              className={`search-result ${i === cursor ? 'active' : ''}`}
              key={p.id}
              href={`/products/${p.slug}`}
              onClick={() => setSearch(false)}
            >
              <img src={p.variants[0]?.image} alt="" width="70" height="56" />
              <span>
                <small>{p.brand.name}</small>
                <strong>{p.name}</strong>
              </span>
              <span>{money(p.price)}</span>
              <ArrowUpRight size={17} />
            </Link>
          ))}
        </div>
        {q.length > 1 && !loading && !results.length && (
          <p>No matches yet. Try a shorter name, another color, or browse all shoes.</p>
        )}
        <Link href="/shop" className="text-link" onClick={() => setSearch(false)}>
          Explore all shoes <ArrowRight size={16} />
        </Link>
      </Dialog>
    </>
  );
}

export function Newsletter({
  title = 'Stay one step ahead.',
  subtitle = 'New rotations, upcoming drops, and stories worth opening.',
}: {
  title?: string;
  subtitle?: string;
}) {
  const [status, setStatus] = useState(''),
    [busy, setBusy] = useState(false);
  return (
    <section className="newsletter">
      <div className="wrap newsletter-inner">
        <div>
          <span className="eyebrow">GOOD THINGS, IN YOUR INBOX</span>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            const form = e.currentTarget;
            setBusy(true);
            try {
              await post('/newsletter/', { email: new FormData(form).get('email'), consent: true });
              setStatus('You’re on the list. Welcome to the rotation.');
              form.reset();
            } catch (e) {
              setStatus((e as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <label htmlFor="newsletter-email" className="sr-only">
            Email address
          </label>
          <div className="newsletter-input">
            <input
              id="newsletter-email"
              name="email"
              type="email"
              placeholder="Your email address"
              required
            />
            <button disabled={busy} aria-label="Join newsletter">
              {busy ? '…' : <ArrowRight />}
            </button>
          </div>
          <label className="consent-check">
            <input type="checkbox" required />I agree to receive emails. Unsubscribe anytime.
          </label>
          <p role="status">{status}</p>
        </form>
      </div>
    </section>
  );
}
export function Footer() {
  const { site } = useStore();
  return (
    <footer className="footer">
      <div className="trust-strip wrap">
        <span>
          <Truck /> Delivery, clearly priced
        </span>
        <span>
          <RotateCcw /> Returns through your account
        </span>
        <span>
          <ShieldCheck /> Secure provider checkout
        </span>
      </div>
      <div className="wrap footer-grid">
        <div className="footer-brand">
          <Link href="/" className="wordmark">
            {site.name}
            <span className="wordmark-dot" />
          </Link>
          <p>
            A fresh perspective on your daily rotation.
            <br />
            Find your pair. Make your move.
          </p>
          {site.demo && (
            <span className="demo-label">DEMONSTRATION STORE · FICTIONAL PRODUCTS</span>
          )}
        </div>
        <div>
          <h3>Explore</h3>
          <Link href="/shop">All shoes</Link>
          <Link href="/brands">Our brands</Link>
          <Link href="/releases">Release calendar</Link>
          <Link href="/collections">Collections</Link>
          <Link href="/sale">Sale</Link>
        </div>
        <div>
          <h3>Here to help</h3>
          <Link href="/tracking">Track your order</Link>
          <Link href="/help/shipping">Delivery</Link>
          <Link href="/help/returns">Returns & exchanges</Link>
          <Link href="/help/help">Help & contact</Link>
          <Link href="/account">Your account</Link>
        </div>
        <div>
          <h3>A little closer</h3>
          <Link href="/rewards">SOLELINE Circle</Link>
          <Link href="/wishlist">Your wishlist</Link>
          <Link href="/compare">Compare your pairs</Link>
          <Link href="/help/privacy">Privacy & cookies</Link>
          <Link href="/help/terms">Terms of use</Link>
        </div>
      </div>
      <div className="footer-bottom wrap">
        <span>
          © {new Date().getFullYear()} {site.name}. Your next move.
        </span>
        <span>
          Kenya · KSh / KES <ArrowUpRight size={14} />
        </span>
      </div>
    </footer>
  );
}

const subscribeConsent = (fn: () => void) => {
  window.addEventListener('storage', fn);
  return () => window.removeEventListener('storage', fn);
};
export function Consent() {
  const show = useSyncExternalStore(
    subscribeConsent,
    () => !localStorage.getItem('soleline:consent'),
    () => false,
  );
  function choose(value: string) {
    localStorage.setItem('soleline:consent', value);
    window.dispatchEvent(new Event('storage'));
  }
  return show ? (
    <aside className="consent-banner" aria-label="Cookie preferences">
      <div>
        <strong>A little about cookies.</strong>
        <p>
          Essential cookies keep your bag and account working. Optional analytics help improve the
          store.
        </p>
        <Link href="/help/privacy">Privacy details</Link>
      </div>
      <div>
        <button className="button secondary" onClick={() => choose('essential')}>
          Essential only
        </button>
        <button className="button" onClick={() => choose('all')}>
          Accept optional
        </button>
      </div>
    </aside>
  ) : null;
}
export function CompareBar() {
  const { compare } = useStore();
  return compare.length > 0 ? (
    <Link className="compare-bar" href="/compare">
      Compare your pairs <span>{compare.length}/4</span>
      <ArrowRight size={17} />
    </Link>
  ) : null;
}
