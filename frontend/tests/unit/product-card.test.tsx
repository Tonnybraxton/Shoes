import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProductCard } from '@/components/product-card';
import { safeHref, money } from '@/lib/api';
import type { Product } from '@/lib/types';
vi.mock('@/components/store-provider', () => ({
  useStore: () => ({ wishlist: [], compare: [], toggleWish: vi.fn(), toggleCompare: vi.fn() }),
}));
vi.mock('next/link', () => ({
  default: ({ children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a {...props}>{children}</a>
  ),
}));
const product = {
  id: 1,
  slug: 'test-runner',
  name: 'Test Runner',
  subtitle: 'Running shoes',
  brand: { name: 'TEST' },
  badges: [],
  max_card_swatches: 4,
  default_variant_id: 1,
  review_count: 0,
  variants: [
    {
      id: 1,
      color_name: 'Black',
      color_code: '#000000',
      image: '/black.svg',
      images: [],
      price: '100.00',
      in_stock: true,
    },
    {
      id: 2,
      color_name: 'White',
      color_code: '#ffffff',
      image: '/white.svg',
      images: [
        {
          url: '/white.svg',
          width: 1000,
          height: 800,
          renditions: [{ url: '/white-480.webp', width: 480, height: 384 }],
        },
      ],
      price: '120.00',
      in_stock: false,
    },
  ],
} as unknown as Product;
describe('product cards', () => {
  it('changes image, link, price, and stock together for a colorway', () => {
    render(<ProductCard product={product} />);
    fireEvent.click(screen.getByRole('button', { name: 'Select White colorway' }));
    expect(screen.getByRole('img')).toHaveAttribute('src', '/white.svg');
    expect(screen.getByRole('img')).toHaveAttribute(
      'srcset',
      '/white-480.webp 480w, /white.svg 1000w',
    );
    expect(screen.getByRole('button', { name: 'Select White colorway' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(screen.getByText(/White · Out of stock/)).toBeInTheDocument();
    expect(screen.getByText(/KSh\s120/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'TEST Test Runner, White' })).toHaveAttribute(
      'href',
      '/products/test-runner?color=2',
    );
  });
});
describe('untrusted merchandising links', () => {
  it.each([
    'javascript:alert(1)',
    '//evil.example',
    'https://evil.example',
    '/\\evil.example',
    '/\nevil.example',
    null,
    {},
  ])('rejects %s', (value) => {
    expect(safeHref(value)).toBe('/shop');
  });
  it('allows local shop routes', () => expect(safeHref('/shop?new=true')).toBe('/shop?new=true'));
});
describe('currency display', () => {
  it('uses KSh consistently and preserves fractional prices', () => {
    expect(money('1234.50').replace(/\s/g, ' ')).toBe('KSh 1,234.5');
    expect(money('120.00').replace(/\s/g, ' ')).toBe('KSh 120');
  });
});
