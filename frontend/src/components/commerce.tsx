'use client';
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  ArrowRight,
  ChevronRight,
  Minus,
  Plus,
  ShieldCheck,
  CheckCircle2,
  ShoppingBag,
} from 'lucide-react';
import { api, post, money } from '@/lib/api';
import type { Cart, Order, Product } from '@/lib/types';
import { useStore } from './store-provider';

export function Summary({ cart, checkout = false }: { cart: Cart; checkout?: boolean }) {
  const { setCart, notify } = useStore();
  const [busy, setBusy] = useState(false);
  return (
    <aside className="order-summary">
      <h2>Your order, at a glance.</h2>
      <div className="summary-row">
        <span>Subtotal</span>
        <span>{money(cart.subtotal)}</span>
      </div>
      {Number(cart.discount) > 0 && (
        <div className="summary-row">
          <span>Promotion · {cart.promo_code}</span>
          <span>−{money(cart.discount)}</span>
        </div>
      )}
      <div className="summary-row">
        <span>Standard delivery</span>
        <span>{Number(cart.shipping) === 0 ? 'Included' : money(cart.shipping)}</span>
      </div>
      <div className="summary-row total">
        <span>Total</span>
        <span>{money(cart.total)}</span>
      </div>
      <p className="muted" style={{ fontSize: 10 }}>
        All prices in Kenyan shillings. No currency conversion.
      </p>
      {!checkout && (
        <>
          <form
            className="promo-form"
            onSubmit={async (e) => {
              e.preventDefault();
              setBusy(true);
              try {
                setCart(
                  await post<Cart>('/cart/promo/', {
                    code: new FormData(e.currentTarget).get('code'),
                  }),
                );
                notify('Promotion applied if your bag is eligible.');
              } catch (e) {
                notify((e as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            <input
              name="code"
              aria-label="Promotion code"
              placeholder="Promotion code"
              required
              maxLength={40}
            />
            <button disabled={busy}>Apply</button>
          </form>
          {cart.promo_code && (
            <button
              className="compare-toggle"
              onClick={async () => {
                try {
                  setCart(await api<Cart>('/cart/promo/', { method: 'DELETE' }));
                } catch (e) {
                  notify((e as Error).message);
                }
              }}
            >
              Remove promotion
            </button>
          )}
          <Link href="/checkout" className="button full">
            Continue to checkout
            <ArrowRight size={17} />
          </Link>
          <div className="pdp-service">
            <ShieldCheck size={16} />
            <span>Your payment details stay with the provider.</span>
          </div>
        </>
      )}
    </aside>
  );
}
export function CartPage() {
  const { cart, setCart, notify, toggleWish } = useStore();
  const [pending, setPending] = useState<number | null>(null);
  async function quantity(id: number, value: number) {
    setPending(id);
    try {
      setCart(await post<Cart>(`/cart/items/${id}/`, { quantity: value }, 'PATCH'));
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setPending(null);
    }
  }
  if (!cart)
    return (
      <div className="empty-state" role="status">
        Loading your bag…
      </div>
    );
  if (!cart.items.length)
    return (
      <div className="empty-state wrap">
        <ShoppingBag size={38} style={{ margin: '0 auto' }} />
        <h1>Room for your next move.</h1>
        <p>Your bag is empty. Find a pair that feels like you.</p>
        <Link className="button" href="/shop">
          Explore all shoes
          <ArrowRight size={18} />
        </Link>
      </div>
    );
  return (
    <div className="wrap">
      <div className="breadcrumb">
        <Link href="/">Home</Link>
        <ChevronRight size={10} />
        <span>Your bag</span>
      </div>
      <div className="page-heading">
        <h1>Your next rotation.</h1>
        <p>
          {cart.items.reduce((n, i) => n + i.quantity, 0)} items in your bag. Good choices start
          here.
        </p>
      </div>
      <div className="cart-layout">
        <section>
          <div className="shipping-progress">
            {Number(cart.free_shipping_remaining) > 0
              ? `You’re ${money(cart.free_shipping_remaining)} away from included standard delivery.`
              : 'Standard delivery is included with this bag.'}
            <div className="shipping-track">
              <div
                style={{
                  width: `${Math.max(5, 100 - Number(cart.free_shipping_remaining) / 150)}%`,
                }}
              />
            </div>
          </div>
          {cart.items.map((item) => (
            <article className="cart-item" key={item.id}>
              <img
                src={item.image}
                alt={`${item.product_name}, ${item.color_name}`}
                width="180"
                height="160"
              />
              <div className="cart-item-details">
                <span className="brand-label">{item.brand}</span>
                <h2>
                  <Link href={`/products/${item.product_slug}`}>{item.product_name}</Link>
                </h2>
                <p>{item.color_name}</p>
                <p>Size {item.size_label}</p>
                <div className="quantity" aria-label={`Quantity for ${item.product_name}`}>
                  <button
                    aria-label={`Decrease ${item.product_name} quantity`}
                    disabled={item.quantity <= 1 || pending === item.id}
                    onClick={() => void quantity(item.id, item.quantity - 1)}
                  >
                    <Minus size={13} />
                  </button>
                  <span aria-live="polite">{item.quantity}</span>
                  <button
                    aria-label={`Increase ${item.product_name} quantity`}
                    disabled={item.quantity >= Math.min(10, item.available) || pending === item.id}
                    onClick={() => void quantity(item.id, item.quantity + 1)}
                  >
                    <Plus size={13} />
                  </button>
                </div>
                {item.available < item.quantity && (
                  <p className="sale-text">Stock changed. Please adjust your quantity.</p>
                )}
                <div className="cart-item-links">
                  <Link href={`/products/${item.product_slug}`}>Change size / color</Link>
                  <button
                    onClick={async () => {
                      try {
                        const product = await api<Product>(`/products/${item.product_slug}/`);
                        await toggleWish(product);
                        setCart(await api<Cart>(`/cart/items/${item.id}/`, { method: 'DELETE' }));
                      } catch (e) {
                        notify((e as Error).message);
                      }
                    }}
                  >
                    Save for later
                  </button>
                  <button
                    onClick={async () => {
                      try {
                        setCart(await api<Cart>(`/cart/items/${item.id}/`, { method: 'DELETE' }));
                      } catch (e) {
                        notify((e as Error).message);
                      }
                    }}
                  >
                    Remove
                  </button>
                </div>
              </div>
              <span className="cart-item-price">{money(item.line_total)}</span>
            </article>
          ))}
          <Link href="/shop" className="text-link" style={{ marginTop: 27 }}>
            Keep exploring
            <ArrowRight size={16} />
          </Link>
        </section>
        <Summary cart={cart} />
      </div>
    </div>
  );
}

const checkoutSchema = z.object({
  email: z.email('Enter a valid email.'),
  first_name: z.string().min(1, 'First name is required.').max(100),
  last_name: z.string().min(1, 'Last name is required.').max(100),
  phone: z.string().regex(/^\+?[0-9 ()-]{7,25}$/, 'Enter a valid phone number.'),
  line1: z.string().min(3, 'Enter your street address.'),
  line2: z.string(),
  city: z.string().min(2, 'Enter your city.'),
  county: z.string().min(2, 'Enter your county.'),
  postal_code: z.string(),
  consent: z.literal(true, { error: 'Please agree to the checkout terms.' }),
});
type CheckoutFields = z.infer<typeof checkoutSchema>;
export function CheckoutPage() {
  const { cart, site, user, refresh } = useStore(),
    router = useRouter();
  const [busy, setBusy] = useState(false),
    [error, setError] = useState('');
  const attempt = useRef<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CheckoutFields>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      email: user?.email || '',
      first_name: user?.first_name || '',
      line2: '',
      postal_code: '',
    },
  });
  const fields = [
    ['first_name', 'First name', 'given-name'],
    ['last_name', 'Last name', 'family-name'],
    ['email', 'Email address', 'email'],
    ['phone', 'Phone number', 'tel'],
    ['line1', 'Street address', 'address-line1'],
    ['line2', 'Apartment, building (optional)', 'address-line2'],
    ['city', 'City / town', 'address-level2'],
    ['county', 'County', 'address-level1'],
    ['postal_code', 'Postal code (optional)', 'postal-code'],
  ] as const;
  async function submit(values: CheckoutFields) {
    if (busy) return;
    setBusy(true);
    setError('');
    attempt.current ||= crypto.randomUUID();
    try {
      const result = await api<{
        order: Order & { tracking_token: string };
        payment: { redirect_url: string };
        test_mode: boolean;
      }>('/checkout/', {
        method: 'POST',
        headers: { 'Idempotency-Key': attempt.current },
        body: JSON.stringify({
          email: values.email,
          first_name: values.first_name,
          last_name: values.last_name,
          phone: values.phone,
          address: {
            line1: values.line1,
            line2: values.line2,
            city: values.city,
            county: values.county,
            postal_code: values.postal_code,
            country: 'KE',
          },
          shipping_method: 'standard',
          payment_provider: site.payment_enabled ? 'stripe' : 'test',
          consent: values.consent,
        }),
      });
      if (result.test_mode) {
        await post('/payments/test/complete/', { reference: result.order.reference });
        await refresh();
        router.push(
          `/orders/${result.order.reference}?token=${encodeURIComponent(result.order.tracking_token)}`,
        );
      } else if (result.payment.redirect_url) {
        const redirect = new URL(result.payment.redirect_url);
        if (redirect.protocol !== 'https:' || redirect.hostname !== 'checkout.stripe.com')
          throw new Error('Unexpected payment provider address.');
        window.location.assign(redirect.href);
      } else throw new Error('Payment session unavailable.');
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (!cart)
    return (
      <div className="empty-state" role="status">
        Loading checkout…
      </div>
    );
  if (!cart.items.length)
    return (
      <div className="empty-state wrap">
        <h1>Your bag is empty.</h1>
        <p>Add a pair before checking out.</p>
        <Link href="/shop" className="button">
          Explore shoes
        </Link>
      </div>
    );
  return (
    <div className="wrap">
      <div className="breadcrumb">
        <Link href="/cart">Bag</Link>
        <ChevronRight size={10} />
        <span>Checkout</span>
      </div>
      <div className="page-heading">
        <h1>One step closer.</h1>
        <p>A few details, and your next move is on its way.</p>
      </div>
      <div className="cart-layout">
        <form onSubmit={(event) => void handleSubmit(submit)(event)} noValidate>
          <div className="checkout-progress">
            <strong>01 · Your details</strong>
            <ChevronRight size={12} />
            <span>02 · Payment</span>
            <ChevronRight size={12} />
            <span>03 · Confirmation</span>
          </div>
          {!user && (
            <p className="notice">
              Checking out as a guest. Already part of the rotation?{' '}
              <Link className="text-link" href="/account">
                Sign in
              </Link>
            </p>
          )}
          <section className="checkout-section">
            <h2>Contact & delivery</h2>
            <div className="form-grid">
              {fields.map(([key, label, autocomplete]) => (
                <label className="field" key={key}>
                  <span>{label}</span>
                  <input
                    {...register(key)}
                    type={key === 'email' ? 'email' : key === 'phone' ? 'tel' : 'text'}
                    autoComplete={autocomplete}
                    aria-invalid={!!errors[key]}
                    aria-describedby={errors[key] ? `error-${key}` : undefined}
                  />
                  {errors[key] && (
                    <span className="field-error" id={`error-${key}`}>
                      {errors[key]?.message}
                    </span>
                  )}
                </label>
              ))}
              <label className="field">
                <span>Country</span>
                <input value="Kenya" readOnly />
              </label>
            </div>
          </section>
          <section className="checkout-section">
            <h2>Delivery method</h2>
            <label className="radio-label">
              <input type="radio" checked readOnly name="shipping" />
              <span>
                Standard delivery · {Number(cart.shipping) ? money(cart.shipping) : 'Included'}
                <small style={{ display: 'block', marginTop: 5, color: 'var(--muted)' }}>
                  Delivery estimates will be confirmed after fulfillment.
                </small>
              </span>
            </label>
          </section>
          <section className="checkout-section">
            <h2>Payment</h2>
            {site.payment_enabled ? (
              <div className="notice">
                <ShieldCheck size={20} /> Continue to Stripe’s secure checkout to enter your payment
                details.
              </div>
            ) : site.test_payments ? (
              <div className="notice demo">
                <strong>Development checkout · No money moves.</strong>
                <p>
                  This explicit test provider simulates a verified payment for local testing. All
                  products are fictional DEMO items.
                </p>
              </div>
            ) : (
              <div className="notice">
                <strong>Payments are not configured yet.</strong>
                <p>
                  The store needs sandbox or production provider credentials before it can accept a
                  payment.
                </p>
              </div>
            )}
          </section>
          <label className="consent-check">
            <input type="checkbox" {...register('consent')} />I have reviewed my order and agree to
            the{' '}
            <Link href="/help/terms" style={{ textDecoration: 'underline' }}>
              terms of use
            </Link>
            .
          </label>
          {errors.consent && <p className="field-error">{errors.consent.message}</p>}
          {error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}
          <button
            className="button full"
            style={{ marginTop: 24 }}
            disabled={busy || (!site.payment_enabled && !site.test_payments)}
          >
            {busy
              ? 'Preparing your order…'
              : site.payment_enabled
                ? 'Continue to secure payment'
                : 'Place demonstration order'}
            <ArrowRight size={17} />
          </button>
          <p className="muted" style={{ fontSize: 10, marginTop: 14 }}>
            Prices and availability are verified again when you submit. No card data is collected on
            this site.
          </p>
        </form>
        <Summary cart={cart} checkout />
      </div>
    </div>
  );
}

export function OrderPage({ reference }: { reference: string }) {
  const query = useSearchParams(),
    { user, notify } = useStore();
  const [order, setOrder] = useState<Order | null>(null),
    [error, setError] = useState('');
  useEffect(() => {
    api<Order>(`/orders/${reference}/?token=${encodeURIComponent(query.get('token') || '')}`)
      .then(setOrder)
      .catch(() =>
        setError(
          'This order could not be opened. Sign in as its owner or use the secure link from your confirmation.',
        ),
      );
  }, [reference, query]);
  if (error)
    return (
      <div className="empty-state wrap">
        <h1>We couldn’t open that order.</h1>
        <p>{error}</p>
        <Link className="button" href="/account">
          Sign in
        </Link>
      </div>
    );
  if (!order)
    return (
      <div className="empty-state" role="status">
        Loading your order…
      </div>
    );
  return (
    <div className="wrap">
      <div className="order-confirm">
        <CheckCircle2 size={45} />
        <span className="eyebrow">YOUR ORDER · {order.status.replaceAll('_', ' ')}</span>
        <h1 style={{ marginTop: 15 }}>
          {order.status === 'paid' ? 'Your next move is in.' : 'Here’s where things stand.'}
        </h1>
        <p>
          Order reference: {order.reference}
          <br />
          Keep your secure confirmation link to check progress.
        </p>
      </div>
      <div className="order-timeline">
        {order.history.map((h, i) => (
          <div className="timeline-step" key={i}>
            <strong>{h.status.replaceAll('_', ' ')}</strong>
            <p>{new Date(h.created_at).toLocaleString('en-KE')}</p>
          </div>
        ))}
      </div>
      <div className="cart-layout">
        <div>
          {order.items.map((i) => (
            <article className="cart-item" key={i.id}>
              <img src={i.image} alt={i.product_name} width="140" height="120" />
              <div>
                <span className="brand-label">{i.brand}</span>
                <h2>{i.product_name}</h2>
                <p>
                  {i.color_name} · {i.size_label}
                </p>
                <p>Quantity {i.quantity}</p>
              </div>
              <strong className="cart-item-price">{money(i.line_total)}</strong>
            </article>
          ))}
          {user && order.status === 'delivered' && (
            <details className="notice">
              <summary>Request a return</summary>
              <form
                onSubmit={async (e) => {
                  e.preventDefault();
                  const f = new FormData(e.currentTarget);
                  try {
                    await post('/returns/', {
                      order_reference: order.reference,
                      items: order.items
                        .filter((i) => f.get(`item-${i.id}`))
                        .map((i) => ({ order_item_id: i.id, quantity: i.quantity })),
                      reason: f.get('reason'),
                      request_type: 'refund',
                    });
                    notify('Your return request has been submitted for review.');
                    setOrder({ ...order, status: 'return_requested' });
                  } catch (e) {
                    notify((e as Error).message);
                  }
                }}
              >
                {order.items.map((i) => (
                  <label key={i.id} className="consent-check">
                    <input type="checkbox" name={`item-${i.id}`} />
                    {i.product_name} · {i.quantity} item(s)
                  </label>
                ))}
                <label className="field" style={{ marginTop: 15 }}>
                  <span>Reason for return</span>
                  <textarea name="reason" required maxLength={1000} />
                </label>
                <button className="button">Submit return request</button>
              </form>
            </details>
          )}
        </div>
        <aside className="order-summary">
          <h2>Order summary</h2>
          <div className="summary-row">
            <span>Subtotal</span>
            <span>{money(order.subtotal)}</span>
          </div>
          <div className="summary-row">
            <span>Discount</span>
            <span>−{money(order.discount)}</span>
          </div>
          <div className="summary-row">
            <span>Delivery</span>
            <span>{money(order.shipping)}</span>
          </div>
          <div className="summary-row total">
            <span>Total</span>
            <span>{money(order.total)}</span>
          </div>
          <div className="divider" />
          <h3 style={{ fontSize: 18 }}>Delivering to</h3>
          <p style={{ fontSize: 12, marginTop: 15 }}>
            {Object.values(order.address).filter(Boolean).join(', ')}
          </p>
        </aside>
      </div>
    </div>
  );
}
export function Tracking() {
  const router = useRouter();
  const [error, setError] = useState('');
  return (
    <div className="wrap">
      <div className="page-heading" style={{ paddingTop: 60, textAlign: 'center' }}>
        <h1>Follow your next move.</h1>
        <p style={{ margin: '20px auto' }}>
          Use the order reference and secure tracking token from your confirmation link.
        </p>
      </div>
      <form
        className="tracking-form"
        onSubmit={async (e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget),
            reference = String(f.get('reference')),
            token = String(f.get('token'));
          try {
            await post('/tracking/', { reference, token });
            router.push(`/orders/${reference}?token=${encodeURIComponent(token)}`);
          } catch {
            setError(
              'Order not found or the secure token is invalid. Check your confirmation link.',
            );
          }
        }}
      >
        <label className="field">
          <span>Order reference</span>
          <input name="reference" required placeholder="Your order UUID" />
        </label>
        <label className="field">
          <span>Secure tracking token</span>
          <input name="token" required autoComplete="off" />
        </label>
        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}
        <button className="button full">
          Track my order
          <ArrowRight size={17} />
        </button>
      </form>
    </div>
  );
}
