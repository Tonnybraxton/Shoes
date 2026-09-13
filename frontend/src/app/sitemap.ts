import type { MetadataRoute } from 'next';
import { serverApi } from '@/lib/server';
import type { Page, Product } from '@/lib/types';
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
  const routes = ['', '/shop', '/men', '/women', '/kids', '/brands', '/collections', '/releases'];
  let page = 1;
  while (page <= 100) {
    const result = await serverApi<Page<Product>>(`/products/?page=${page}`);
    routes.push(...result.results.map((p) => `/products/${p.slug}`));
    if (!result.next) break;
    page++;
  }
  return routes.map((path) => ({ url: base + path, changeFrequency: 'daily' }));
}
