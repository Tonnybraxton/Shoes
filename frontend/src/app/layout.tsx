import Link from 'next/link';
import type { Metadata } from 'next';
import './globals.css';
import { serverApi } from '@/lib/server';
import type { Site } from '@/lib/types';
import { StoreProvider } from '@/components/store-provider';
import { Header, Footer, Consent, CompareBar } from '@/components/shell';
export const dynamic = 'force-dynamic';
export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: { default: 'SOLELINE — Find your next move', template: '%s | SOLELINE' },
  description:
    'A fresh perspective on your daily rotation. Explore footwear, colorways, and upcoming releases at SOLELINE.',
};
export default async function RootLayout({ children }: { children: React.ReactNode }) {
  let site: Site;
  try {
    site = await serverApi<Site>('/site/');
  } catch {
    return (
      <html lang="en">
        <body>
          <main className="service-error">
            <span className="wordmark">SOLELINE</span>
            <h1>The store is taking a moment.</h1>
            <p>We couldn’t connect to the catalog. Please try again shortly.</p>
            <Link className="button" href="/">
              Try again
            </Link>
          </main>
        </body>
      </html>
    );
  }
  return (
    <html lang="en-KE" data-scroll-behavior="smooth">
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <StoreProvider site={site}>
          <Header />
          <main id="main">{children}</main>
          <Footer />
          <Consent />
          <CompareBar />
        </StoreProvider>
      </body>
    </html>
  );
}
