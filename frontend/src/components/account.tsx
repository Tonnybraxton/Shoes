'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ArrowRight, ArrowUpRight, Heart, Check, ChevronRight } from 'lucide-react';
import { api, post, money } from '@/lib/api';
import type { Product, Order, Page, Release } from '@/lib/types';
import { useStore } from './store-provider';
import { ProductCard } from './product-card';

export function Account({ section = 'profile' }: { section?: string }) {
  const { user, refresh, notify } = useStore(),
    query = useSearchParams();
  const [mode, setMode] = useState('login'),
    [error, setError] = useState(''),
    [busy, setBusy] = useState(false),
    [orders, setOrders] = useState<Order[]>([]),
    [profile, setProfile] = useState<Record<string, string>>({}),
    [profileUserId, setProfileUserId] = useState<number | null>(null),
    [addresses, setAddresses] = useState<Record<string, string | number>[]>([]);
  const userId = user?.id;
  useEffect(() => {
    if (!userId) return;
    let cancelled = false;
    api<Record<string, string>>('/account/')
      .then((data) => {
        if (!cancelled) {
          setProfile(data);
          setProfileUserId(userId);
        }
      })
      .catch(() => {
        if (!cancelled) notify('Your profile could not be loaded. Please refresh to retry.');
      });
    api<Page<Order>>('/orders/')
      .then((r) => {
        if (!cancelled) setOrders(r.results);
      })
      .catch(() => {});
    api<Page<Record<string, string | number>>>('/addresses/')
      .then((r) => {
        if (!cancelled) setAddresses(r.results);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [userId, notify]);
  if (section === 'verify' || section === 'reset')
    return (
      <div className="wrap">
        <div className="auth-card">
          <h1>{section === 'verify' ? 'Confirm your email.' : 'A fresh start.'}</h1>
          <p>
            {section === 'verify'
              ? 'Confirm the email address for your SOLELINE account.'
              : 'Choose a new, strong password for your account.'}
          </p>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              setBusy(true);
              setError('');
              try {
                const data = await post<{ message: string }>(
                  section === 'verify' ? '/auth/verify/' : '/auth/password-reset/confirm/',
                  {
                    token: query.get('token'),
                    uid: query.get('uid'),
                    password: new FormData(e.currentTarget).get('password'),
                  },
                );
                setError(data.message);
              } catch (e) {
                setError((e as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            {section === 'reset' && (
              <label className="field">
                <span>New password</span>
                <input
                  type="password"
                  name="password"
                  required
                  minLength={10}
                  autoComplete="new-password"
                />
              </label>
            )}
            <button className="button full" disabled={busy}>
              {section === 'verify' ? 'Verify email' : 'Update password'}
            </button>
            <p className="notice" role="status" hidden={!error}>
              {error}
            </p>
          </form>
          <Link href="/account" className="text-link">
            Back to sign in
            <ArrowRight size={15} />
          </Link>
        </div>
      </div>
    );
  if (!user)
    return (
      <div className="wrap">
        <div className="auth-card">
          <span className="eyebrow">YOUR PERSONAL ROTATION</span>
          <h1 style={{ marginTop: 17 }}>
            {mode === 'register'
              ? 'Make yourself at home.'
              : mode === 'reset'
                ? 'Let’s get you back in.'
                : 'Good to see you.'}
          </h1>
          <p>
            {mode === 'register'
              ? 'Save your favorites, follow your orders, and get closer to what’s next.'
              : mode === 'reset'
                ? 'We’ll send a reset link if an account exists for your email.'
                : 'Sign in to your SOLELINE account.'}
          </p>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              setBusy(true);
              setError('');
              try {
                const result = await post<{ message?: string }>(
                  `/auth/${mode === 'reset' ? 'password-reset' : mode}/`,
                  Object.fromEntries(f),
                );
                if (mode === 'reset') setError(result.message || 'Check your inbox.');
                else await refresh();
              } catch (e) {
                setError((e as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            {mode === 'register' && (
              <div className="form-grid">
                <label className="field">
                  <span>First name</span>
                  <input name="first_name" autoComplete="given-name" required />
                </label>
                <label className="field">
                  <span>Last name</span>
                  <input name="last_name" autoComplete="family-name" required />
                </label>
              </div>
            )}
            <label className="field">
              <span>Email address</span>
              <input name="email" type="email" autoComplete="email" required />
            </label>
            {mode !== 'reset' && (
              <div className="field">
                <label htmlFor="account-password">Password</label>
                <input
                  id="account-password"
                  name="password"
                  type="password"
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  required
                  minLength={mode === 'register' ? 10 : 1}
                  aria-describedby={mode === 'register' ? 'password-help' : undefined}
                />
                {mode === 'register' && (
                  <small className="muted" id="password-help">
                    At least 10 characters. Avoid common passwords.
                  </small>
                )}
              </div>
            )}
            {error && (
              <p className="error-message" role="alert">
                {error}
              </p>
            )}
            <button className="button full" disabled={busy}>
              {busy
                ? 'One moment…'
                : mode === 'register'
                  ? 'Create account'
                  : mode === 'reset'
                    ? 'Send reset link'
                    : 'Sign in'}
              <ArrowRight size={16} />
            </button>
          </form>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
            <button
              className="text-link"
              onClick={() => {
                setMode(mode === 'register' ? 'login' : 'register');
                setError('');
              }}
            >
              {mode === 'register'
                ? 'Already have an account? Sign in'
                : 'New here? Create an account'}
            </button>
            <button
              className="text-link"
              onClick={() => {
                setMode(mode === 'reset' ? 'login' : 'reset');
                setError('');
              }}
            >
              {mode === 'reset' ? 'Back to sign in' : 'Forgot your password?'}
            </button>
          </div>
        </div>
      </div>
    );
  return (
    <div className="wrap">
      <div className="breadcrumb">
        <Link href="/">Home</Link>
        <ChevronRight size={10} />
        <span>Your account</span>
      </div>
      <div className="page-heading">
        <h1>Your space, {user.first_name || 'your way'}.</h1>
        <p>Everything in your rotation, all in one place.</p>
      </div>
      <div className="account-layout">
        <nav className="account-nav" aria-label="Account navigation">
          {[
            ['profile', 'Your profile'],
            ['orders', 'Your orders'],
            ['addresses', 'Saved addresses'],
            ['rewards', 'Your rewards'],
          ].map(([key, label]) => (
            <Link
              href={key === 'profile' ? '/account' : `/account/${key}`}
              className={section === key ? 'active' : ''}
              key={key}
            >
              {label}
            </Link>
          ))}
          <Link href="/wishlist">Wishlist</Link>
          <button
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await post('/auth/logout/', {});
                setMode('login');
                setError('');
                setProfile({});
                setProfileUserId(null);
                setOrders([]);
                setAddresses([]);
                await refresh();
              } catch (e) {
                notify((e as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            Sign out
          </button>
        </nav>
        <section>
          {section === 'orders' ? (
            <>
              <h2>Your orders</h2>
              {orders.length ? (
                orders.map((o) => (
                  <Link
                    href={`/orders/${o.reference}`}
                    className="order-list-item"
                    key={o.reference}
                  >
                    <div>
                      <strong>{o.items.map((i) => i.product_name).join(', ')}</strong>
                      <p>
                        {new Date(o.created_at).toLocaleDateString('en-KE')} ·{' '}
                        {o.reference.slice(0, 8)}
                      </p>
                    </div>
                    <span className="status-pill">{o.status.replaceAll('_', ' ')}</span>
                    <strong>{money(o.total)}</strong>
                    <ArrowUpRight size={17} />
                  </Link>
                ))
              ) : (
                <p className="notice">
                  Your first rotation is waiting. <Link href="/shop">Explore the collection.</Link>
                </p>
              )}
            </>
          ) : section === 'rewards' ? (
            <Rewards />
          ) : section === 'addresses' ? (
            <>
              <h2>Saved addresses</h2>
              {addresses.map((a) => (
                <div className="order-list-item" key={a.id}>
                  <div>
                    <strong>{a.label}</strong>
                    <p>{[a.line1, a.city, a.county].join(', ')}</p>
                  </div>
                  <button
                    className="text-link"
                    onClick={async () => {
                      try {
                        await api(`/addresses/${a.id}/`, { method: 'DELETE' });
                        setAddresses(addresses.filter((x) => x.id !== a.id));
                      } catch (e) {
                        notify((e as Error).message);
                      }
                    }}
                  >
                    Remove
                  </button>
                </div>
              ))}
              <h3 style={{ margin: '30px 0 20px' }}>Add an address</h3>
              <form
                onSubmit={async (e) => {
                  e.preventDefault();
                  const form = e.currentTarget;
                  try {
                    const address = await post<Record<string, string | number>>('/addresses/', {
                      ...Object.fromEntries(new FormData(form)),
                      country: 'KE',
                    });
                    setAddresses([...addresses, address]);
                    form.reset();
                    notify('Address saved.');
                  } catch (e) {
                    notify((e as Error).message);
                  }
                }}
              >
                <div className="form-grid">
                  {[
                    ['label', 'Label'],
                    ['line1', 'Street address'],
                    ['line2', 'Apartment (optional)'],
                    ['city', 'City / town'],
                    ['county', 'County'],
                    ['postal_code', 'Postal code (optional)'],
                  ].map(([key, label]) => (
                    <label className="field" key={key}>
                      <span>{label}</span>
                      <input name={key} required={!['line2', 'postal_code'].includes(key)} />
                    </label>
                  ))}
                </div>
                <button className="button">Save address</button>
              </form>
            </>
          ) : (
            <>
              <h2>Your details</h2>
              {profileUserId !== user.id ? (
                <p role="status">Loading your details…</p>
              ) : (
                <form
                  style={{ marginTop: 28, maxWidth: 600 }}
                  onSubmit={async (e) => {
                    e.preventDefault();
                    try {
                      const updated = await post<Record<string, string>>(
                        '/account/',
                        Object.fromEntries(new FormData(e.currentTarget)),
                        'PATCH',
                      );
                      setProfile(updated);
                      await refresh();
                      notify('Your profile is up to date.');
                    } catch (e) {
                      notify((e as Error).message);
                    }
                  }}
                >
                  <div className="form-grid">
                    {[
                      ['first_name', 'First name'],
                      ['last_name', 'Last name'],
                      ['phone', 'Phone number'],
                      ['usual_size', 'Usual shoe size'],
                    ].map(([key, label]) => (
                      <label className="field" key={key}>
                        <span>{label}</span>
                        <input
                          name={key}
                          defaultValue={profile[key] || ''}
                          key={profile[key] || key}
                        />
                      </label>
                    ))}
                    <label className="field">
                      <span>Size system</span>
                      <select name="size_system" defaultValue={profile.size_system || 'EU'}>
                        {['EU', 'UK', 'US Men', 'US Women', 'US Kids'].map((s) => (
                          <option key={s}>{s}</option>
                        ))}
                      </select>
                    </label>
                    <label className="field">
                      <span>Preferred fit</span>
                      <select
                        name="fit_preference"
                        defaultValue={profile.fit_preference || 'regular'}
                      >
                        <option value="regular">Regular</option>
                        <option value="snug">Snug</option>
                        <option value="roomy">Roomy</option>
                      </select>
                    </label>
                  </div>
                  <p className="notice">
                    Account email: {user.email}. Password resets are available from the sign-in
                    screen.
                  </p>
                  <button className="button">
                    Save changes
                    <Check size={16} />
                  </button>
                </form>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}
export function SavedProducts({ kind = 'wishlist' }: { kind?: 'wishlist' | 'compare' | 'recent' }) {
  const { wishlist, compare, toggleCompare } = useStore();
  const [products, setProducts] = useState<Product[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState('');
  const ids = kind === 'compare' ? compare : wishlist;
  useEffect(() => {
    let selected = ids;
    if (kind === 'recent') {
      try {
        selected = JSON.parse(localStorage.getItem('soleline:recent') || '[]');
      } catch {
        selected = [];
      }
    }
    (selected.length
      ? api<Page<Product>>(`/products/?ids=${selected.join(',')}`)
      : Promise.resolve({ results: [] })
    )
      .then((r) => setProducts(r.results))
      .catch(() => setError('Your saved pairs could not be loaded. Please refresh to try again.'))
      .finally(() => setLoading(false));
  }, [ids, kind]);
  const title =
    kind === 'compare'
      ? 'A side-by-side perspective.'
      : kind === 'recent'
        ? 'Back in your orbit.'
        : 'Your personal shortlist.';
  if (loading)
    return (
      <div className="empty-state" role="status">
        Finding your pairs…
      </div>
    );
  return (
    <div className="wrap">
      <div className="page-heading" style={{ paddingTop: 55 }}>
        <span className="eyebrow">
          {kind === 'compare'
            ? 'COMPARE UP TO FOUR PAIRS'
            : kind === 'recent'
              ? 'RECENTLY VIEWED'
              : 'YOUR WISHLIST'}
        </span>
        <h1 style={{ marginTop: 14 }}>{title}</h1>
        <p>
          {kind === 'compare'
            ? 'The details that help you find the right fit.'
            : 'A little inspiration for your next rotation.'}
        </p>
      </div>
      {error ? (
        <p className="error-message">{error}</p>
      ) : !products.length ? (
        <div className="empty-state">
          <Heart size={35} style={{ margin: '0 auto' }} />
          <h2 style={{ marginTop: 20 }}>Good things are worth saving.</h2>
          <p>Explore the collection and keep your favorites close.</p>
          <Link className="button" href="/shop">
            Find your next pair
            <ArrowRight size={17} />
          </Link>
        </div>
      ) : kind === 'compare' ? (
        <div className="table-scroll">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>At a glance</th>
                {products.map((p) => (
                  <th key={p.id}>
                    <img src={p.variants[0]?.image} alt={p.name} width="200" height="160" />
                    <h3>{p.name}</h3>
                    <button className="text-link" onClick={() => toggleCompare(p.id)}>
                      Remove
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                ['Brand', ...products.map((p) => p.brand.name)],
                ['Price', ...products.map((p) => money(p.price))],
                ['Style', ...products.map((p) => p.style)],
                ['Sport', ...products.map((p) => p.sport)],
                [
                  'Fit',
                  ...products.map((p) => (p.fit === 'true' ? 'True to size' : `Runs ${p.fit}`)),
                ],
                ['Width', ...products.map((p) => p.width)],
                [
                  'Colorways',
                  ...products.map((p) => p.variants.map((v) => v.color_name).join(', ')),
                ],
                [
                  'Available sizes',
                  ...products.map((p) =>
                    Array.from(
                      new Set(
                        p.variants.flatMap((v) =>
                          v.sizes
                            .filter((s) => s.available > 0)
                            .map((s) => `${s.system} ${s.label}`),
                        ),
                      ),
                    ).join(', '),
                  ),
                ],
              ].map(([label, ...values]) => (
                <tr key={label}>
                  <th>{label}</th>
                  {values.map((value, i) => (
                    <td key={i}>{value || '—'}</td>
                  ))}
                </tr>
              ))}
              <tr>
                <th>Find your fit</th>
                {products.map((p) => (
                  <td key={p.id}>
                    <Link className="button" href={`/products/${p.slug}`}>
                      Choose size
                    </Link>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      ) : (
        <div className="product-grid">
          {products.map((p) => (
            <ProductCard product={p} key={p.id} />
          ))}
        </div>
      )}
    </div>
  );
}
type RewardData = {
  name: string;
  points: number;
  tier: string;
  enabled: boolean;
  points_per_100: number;
  ledger: { points: number; reason: string; created_at: string }[];
};
export function Rewards() {
  const { user } = useStore();
  const [data, setData] = useState<RewardData | null>(null);
  useEffect(() => {
    api<RewardData>('/rewards/')
      .then(setData)
      .catch(() => {});
  }, []);
  return (
    <section>
      {data ? (
        <>
          <div className="reward-panel">
            <span className="eyebrow">{data.name}</span>
            <h2 style={{ margin: '20px 0' }}>Your moves add up.</h2>
            {user ? (
              <>
                <strong>{data.points}</strong> points
                <p>
                  {data.tier} · {data.points_per_100} point per KSh 100 of qualifying purchases.
                </p>
              </>
            ) : (
              <>
                <p>
                  Join the circle. Earn points on qualifying purchases and follow your progress.
                </p>
                <Link className="button" href="/account" style={{ marginTop: 25 }}>
                  Join the rotation
                  <ArrowRight size={16} />
                </Link>
              </>
            )}
          </div>
          {user && (
            <>
              <h3 style={{ marginTop: 35 }}>Your points history</h3>
              {data.ledger.length ? (
                data.ledger.map((entry, i) => (
                  <div className="summary-row" key={i}>
                    <span>
                      {entry.reason} · {new Date(entry.created_at).toLocaleDateString('en-KE')}
                    </span>
                    <strong>{entry.points} points</strong>
                  </div>
                ))
              ) : (
                <p className="notice">
                  Points appear after a verified purchase. Redemption offers are not currently
                  configured.
                </p>
              )}
            </>
          )}
        </>
      ) : (
        <p role="status">Loading your circle…</p>
      )}
    </section>
  );
}
export function ReleaseDetail({ release }: { release: Release }) {
  const { user, notify } = useStore();
  const [remaining, setRemaining] = useState('');
  useEffect(() => {
    const offset = new Date(release.server_time).getTime() - Date.now();
    function tick() {
      const seconds = Math.max(
        0,
        Math.floor((new Date(release.release_at).getTime() - Date.now() - offset) / 1000),
      );
      setRemaining(
        seconds
          ? `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
          : 'Released',
      );
    }
    const initial = setTimeout(tick, 0);
    const t = setInterval(tick, 60000);
    return () => {
      clearTimeout(initial);
      clearInterval(t);
    };
  }, [release]);
  return (
    <div className="wrap">
      <div className="breadcrumb">
        <Link href="/releases">Release calendar</Link>
        <ChevronRight size={10} />
        <span>{release.title}</span>
      </div>
      <div className="pdp">
        <img
          src={release.image}
          alt={`${release.title} demonstration release`}
          width="1000"
          height="800"
        />
        <div className="pdp-info">
          <span className="eyebrow">
            {release.status} · {remaining}
          </span>
          <h1>{release.title}</h1>
          <p>
            {new Date(release.release_at).toLocaleString('en-KE', {
              timeZone: 'Africa/Nairobi',
              dateStyle: 'long',
              timeStyle: 'short',
            })}{' '}
            EAT
          </p>
          <p className="notice">{release.description}</p>
          {release.status === 'released' && release.product ? (
            <Link className="button" href={`/products/${release.product.slug}`}>
              Explore this release
            </Link>
          ) : (
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                try {
                  await post('/release-alerts/', {
                    email: new FormData(e.currentTarget).get('email'),
                    release_id: release.id,
                    consent: true,
                  });
                  notify('You’re on the release notification list.');
                } catch (e) {
                  notify((e as Error).message);
                }
              }}
            >
              <label className="field">
                <span>Your email address</span>
                <input type="email" name="email" required defaultValue={user?.email} />
              </label>
              <label className="consent-check">
                <input type="checkbox" required />
                Notify me about this release.
              </label>
              <button className="button full" style={{ marginTop: 22 }}>
                Keep me in the loop
                <ArrowRight size={16} />
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
