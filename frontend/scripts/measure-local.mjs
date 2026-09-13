import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const baseURL = new URL(process.env.E2E_BASE_URL || 'http://127.0.0.1:3000');
if (!['127.0.0.1', 'localhost', '[::1]'].includes(baseURL.hostname)) {
  throw new Error('This small development sample only supports a loopback host.');
}
const output = resolve(import.meta.dirname, '../../docs/local-performance.json');
const routes = ['/', '/shop', '/products/velocity-02'];
const browser = await chromium.launch();
const report = {
  measuredAt: new Date().toISOString(),
  baseURL: baseURL.origin,
  environment: { node: process.version, chromium: browser.version(), platform: process.platform },
  method: {
    browser:
      'Three fresh browser contexts per route and viewport; warmed server; no CPU or network throttling.',
    observation:
      'Navigation through load, fonts and initially loaded images, then 1500 ms of observation.',
    api: 'One warmup followed by 25 sequential GETs per endpoint through the frontend proxy, including response body transfer.',
    limitations:
      'Local production frontend and development Django/PostgreSQL. This is not a load test or a field Core Web Vitals result; INP is not measured.',
  },
  pages: [],
  api: [],
};
const round = (value) => (value == null ? null : Math.round(value * 100) / 100);
try {
  for (const [device, viewport] of [
    ['desktop', { width: 1440, height: 1000 }],
    ['mobile-width', { width: 390, height: 844 }],
  ]) {
    for (const route of routes) {
      // Warm the server without carrying browser assets or cookies into the samples.
      const warmup = await fetch(new URL(route, baseURL));
      if (!warmup.ok) throw new Error(`Warmup failed: ${route} ${warmup.status}`);
      await warmup.arrayBuffer();
      const samples = [];
      for (let run = 0; run < 3; run++) {
        const context = await browser.newContext({ viewport });
        try {
          await context.addInitScript(() => {
            localStorage.setItem('soleline:consent', 'essential');
            window.localMetrics = { lcp: null, cls: 0, shifts: [] };
            new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) window.localMetrics.lcp = entry.startTime;
            }).observe({ type: 'largest-contentful-paint', buffered: true });
            let sessionValue = 0;
            let sessionStart = 0;
            let lastShift = 0;
            new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) {
                if (entry.hadRecentInput) continue;
                window.localMetrics.shifts.push({
                  atMs: entry.startTime,
                  value: entry.value,
                  sources: entry.sources.map((source) => ({
                    element: source.node?.nodeName,
                    className: source.node?.className,
                    previous: source.previousRect.toJSON(),
                    current: source.currentRect.toJSON(),
                  })),
                });
                if (entry.startTime - lastShift < 1000 && entry.startTime - sessionStart < 5000) {
                  sessionValue += entry.value;
                } else {
                  sessionValue = entry.value;
                  sessionStart = entry.startTime;
                }
                lastShift = entry.startTime;
                window.localMetrics.cls = Math.max(window.localMetrics.cls, sessionValue);
              }
            }).observe({ type: 'layout-shift', buffered: true });
          });
          const page = await context.newPage();
          const response = await page.goto(new URL(route, baseURL).href, { waitUntil: 'load' });
          if (!response?.ok()) throw new Error(`Page failed: ${route} ${response?.status()}`);
          await page.locator('h1').first().waitFor();
          await page.evaluate(async () => {
            await document.fonts.ready;
            await Promise.all(
              [...document.images]
                .filter((img) => img.loading !== 'lazy')
                .map((img) => img.decode().catch(() => {})),
            );
            // A defined sampling window, not a readiness condition for a functional test.
            await new Promise((resolve) => setTimeout(resolve, 1500));
          });
          samples.push(
            await page.evaluate(() => {
              const navigation = performance.getEntriesByType('navigation')[0];
              return {
                ttfbMs: navigation.responseStart - navigation.startTime,
                lcpMs: window.localMetrics.lcp,
                cls: window.localMetrics.cls,
                shifts: window.localMetrics.shifts,
                domContentLoadedMs: navigation.domContentLoadedEventEnd,
              };
            }),
          );
        } finally {
          await context.close();
        }
      }
      const median = (key) => {
        const values = samples
          .map((s) => s[key])
          .filter((n) => n !== null)
          .sort((a, b) => a - b);
        return values.length === 3 ? round(values[1]) : null;
      };
      const result = {
        device,
        viewport,
        route,
        medianTtfbMs: median('ttfbMs'),
        medianLcpMs: median('lcpMs'),
        maxObservedCls: Math.max(...samples.map((s) => s.cls)),
        samples,
      };
      report.pages.push(result);
      console.log(
        `${device} ${route}: LCP median ${result.medianLcpMs} ms, max CLS ${result.maxObservedCls}`,
      );
    }
  }
  for (const route of ['/api/v1/site/', '/api/v1/products/', '/api/v1/products/velocity-02/']) {
    const samplesMs = [];
    for (let run = 0; run < 26; run++) {
      const started = performance.now();
      const response = await fetch(new URL(route, baseURL));
      await response.arrayBuffer();
      if (!response.ok) throw new Error(`API failed: ${route} ${response.status}`);
      if (run > 0) samplesMs.push(performance.now() - started);
    }
    const sorted = [...samplesMs].sort((a, b) => a - b);
    const result = {
      route,
      requests: samplesMs.length,
      medianMs: round(sorted[12]),
      p95Ms: round(sorted[Math.ceil(sorted.length * 0.95) - 1]),
      samplesMs,
    };
    report.api.push(result);
    console.log(`${route}: median ${result.medianMs} ms, p95 ${result.p95Ms} ms`);
  }
  await mkdir(resolve(output, '..'), { recursive: true });
  await writeFile(output, `${JSON.stringify(report, null, 2)}\n`);
  console.log(`Saved ${output}`);
} finally {
  await browser.close();
}
