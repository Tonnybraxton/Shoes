# Local performance evidence

Measured on 2026-09-09 against the Next.js production build and local Django development server with PostgreSQL. Run `npm run measure:local` from `frontend` to repeat the sample. The script requires a loopback host and the installed Playwright Chromium browser.

Each page/viewport has three samples in fresh browser contexts after warming the server. No CPU or network throttling was applied. The mobile-width sample uses a 390 × 844 viewport; it is not a phone hardware simulation. The observation ends 1.5 seconds after initial page resources and fonts load. Consent is set to essential before navigation. INP was not measured.

## Page results after the loading-layout fix

| Viewport | Route | Median LCP | Largest observed CLS |
| --- | --- | --- | --- |
| Desktop, 1440 × 1000 | Home | 940 ms | 0.0147 |
| Desktop, 1440 × 1000 | Catalogue | 1124 ms | 0 |
| Desktop, 1440 × 1000 | Product detail | 596 ms | 0 |
| Mobile width, 390 × 844 | Home | 692 ms | 0.0147 |
| Mobile width, 390 × 844 | Catalogue | 1076 ms | 0 |
| Mobile width, 390 × 844 | Product detail | 1036 ms | 0 |

The initial sample recorded CLS as high as 0.8851. Layout-shift attribution showed the footer entering the first viewport during streamed loading and then moving away when content arrived. Reserving at least one viewport of height for the main region reduced the largest observed CLS to 0.0147. Residual homepage shifts are recorded in the raw results. Timing differences between runs are workstation samples and are not attributed solely to the CSS change.

## API results

One warmup plus 25 sequential GET requests per endpoint, through the frontend proxy, including response-body transfer. The reported p95 uses the nearest-rank method.

| Endpoint | Median | p95 |
| --- | --- | --- |
| `/api/v1/site/` | 281.36 ms | 390.14 ms |
| `/api/v1/products/` | 184.91 ms | 302.57 ms |
| `/api/v1/products/velocity-02/` | 40.29 ms | 63.05 ms |

The site and catalogue endpoints exceeded the provisional 300 ms p95 target in this local sample. That target remains unverified at representative production load. Profile queries and payload size, configure and measure the production server/cache, and test realistic catalogue size and concurrency before making latency commitments.

These results do not establish field Core Web Vitals, production throughput, real mobile network performance, or a service-level guarantee. Manual accessibility, representative load tests and deployment integrations remain separate work.

## Raw evidence

- [Initial sample](local-performance-before.json)
- [Sample after the layout fix](local-performance.json), including individual timings, viewport sizes, browser/runtime versions and shift attribution
- [Testing and reproduction instructions](TESTING.md)
