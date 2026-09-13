import React, { StrictMode } from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { StoreProvider, useStore } from '@/components/store-provider';
import { api, post } from '@/lib/api';
import type { Site } from '@/lib/types';

vi.mock('@/lib/api', () => ({ api: vi.fn(), post: vi.fn() }));

function Shopper() {
  const store = useStore();
  return <button onClick={() => void store.add(42)}>Add pair</button>;
}

it('establishes one guest cart before an early add under StrictMode', async () => {
  let finishCart!: (value: unknown) => void;
  const initialCart = new Promise((resolve) => {
    finishCart = resolve;
  });
  vi.mocked(api).mockImplementation((path) => {
    if (path === '/session/') return Promise.resolve({ user: null }) as ReturnType<typeof api>;
    return initialCart as ReturnType<typeof api>;
  });
  vi.mocked(post).mockResolvedValue({ items: [{ variant_size_id: 42 }] });
  render(
    <StrictMode>
      <StoreProvider site={{} as Site}>
        <Shopper />
      </StoreProvider>
    </StrictMode>,
  );
  await waitFor(() => expect(api).toHaveBeenCalledWith('/cart/'));
  fireEvent.click(screen.getByRole('button', { name: 'Add pair' }));
  expect(post).not.toHaveBeenCalled();
  await act(async () => {
    finishCart({ items: [] });
  });
  await waitFor(() =>
    expect(post).toHaveBeenCalledWith('/cart/items/', { variant_size_id: 42, quantity: 1 }),
  );
  expect(vi.mocked(api).mock.calls.filter(([path]) => path === '/cart/')).toHaveLength(1);
  expect(screen.getByRole('status')).toHaveTextContent('Added to your bag.');
});
