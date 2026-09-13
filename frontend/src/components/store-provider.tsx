'use client';
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  ReactNode,
} from 'react';
import { api, post } from '@/lib/api';
import type { Cart, Product, Site, User } from '@/lib/types';
type State = {
  site: Site;
  user: User | null;
  cart: Cart | null;
  wishlist: number[];
  compare: number[];
  refresh: () => Promise<void>;
  toggleWish: (p: Product) => Promise<void>;
  toggleCompare: (id: number) => void;
  add: (id: number, quantity?: number) => Promise<void>;
  setCart: (cart: Cart) => void;
  notify: (text: string) => void;
};
const StoreContext = createContext<State | null>(null);
export function StoreProvider({ site, children }: { site: Site; children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null),
    [cart, setCart] = useState<Cart | null>(null),
    [wishlist, setWishlist] = useState<number[]>([]),
    [compare, setCompare] = useState<number[]>([]),
    [toast, setToast] = useState('');
  const notify = useCallback((text: string) => setToast(text), []);
  const refreshInFlight = useRef<Promise<void> | null>(null);
  const initialized = useRef(false);
  const refresh = useCallback(async () => {
    const pending = (refreshInFlight.current || Promise.resolve())
      .catch(() => {})
      .then(async () => {
        const session = await api<{ user: User | null }>('/session/');
        setUser(session.user);
        setCart(await api<Cart>('/cart/'));
        if (session.user) {
          let local: unknown = [];
          try {
            local = JSON.parse(localStorage.getItem('soleline:wishlist') || '[]');
          } catch {
            /* Ignore malformed saved IDs. */
          }
          const saved = await post<{ products: Product[] }>('/wishlist/merge/', {
            product_ids: Array.isArray(local) ? local.slice(0, 100) : [],
          });
          setWishlist(saved.products.map((p) => p.id));
          localStorage.removeItem('soleline:wishlist');
        } else {
          try {
            setWishlist(JSON.parse(localStorage.getItem('soleline:wishlist') || '[]'));
          } catch {
            setWishlist([]);
          }
        }
        try {
          setCompare(JSON.parse(sessionStorage.getItem('soleline:compare') || '[]'));
        } catch {
          setCompare([]);
        }
      });
    refreshInFlight.current = pending;
    try {
      await pending;
    } finally {
      if (refreshInFlight.current === pending) refreshInFlight.current = null;
    }
  }, []);
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    // Session and saved IDs come from external HTTP/storage after hydration.
    void refresh().catch(() =>
      notify('The store service is reconnecting. Please refresh if your bag does not load.'),
    );
  }, [refresh, notify]);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(''), 5000);
    return () => clearTimeout(t);
  }, [toast]);
  async function toggleWish(p: Product) {
    try {
      const selected = wishlist.includes(p.id);
      if (user) {
        const data = selected
          ? await api<{ products: Product[] }>(`/wishlist/${p.id}/`, { method: 'DELETE' })
          : await post<{ products: Product[] }>('/wishlist/', { product_id: p.id });
        setWishlist(data.products.map((x) => x.id));
      } else {
        const next = selected
          ? wishlist.filter((id) => id !== p.id)
          : [...wishlist, p.id].slice(-100);
        setWishlist(next);
        localStorage.setItem('soleline:wishlist', JSON.stringify(next));
      }
      notify(selected ? 'Removed from your wishlist.' : 'Saved to your wishlist.');
    } catch (e) {
      notify((e as Error).message);
    }
  }
  function toggleCompare(id: number) {
    const next = compare.includes(id)
      ? compare.filter((x) => x !== id)
      : compare.length < 4
        ? [...compare, id]
        : compare;
    if (next === compare) {
      notify('Compare up to four pairs at a time.');
      return;
    }
    setCompare(next);
    sessionStorage.setItem('soleline:compare', JSON.stringify(next));
  }
  async function add(id: number, quantity = 1) {
    // Establish the guest session before a write; a late initial cart response
    // must never replace the cookie belonging to the newly populated bag.
    await refreshInFlight.current;
    setCart(await post<Cart>('/cart/items/', { variant_size_id: id, quantity }));
    notify('Added to your bag.');
  }
  return (
    <StoreContext.Provider
      value={{
        site,
        user,
        cart,
        wishlist,
        compare,
        refresh,
        toggleWish,
        toggleCompare,
        add,
        setCart,
        notify,
      }}
    >
      {children}
      <div className={`toast ${toast ? 'visible' : ''}`} role="status" aria-live="polite">
        {toast}
      </div>
    </StoreContext.Provider>
  );
}
export function useStore() {
  const state = useContext(StoreContext);
  if (!state) throw new Error('StoreProvider is required');
  return state;
}
