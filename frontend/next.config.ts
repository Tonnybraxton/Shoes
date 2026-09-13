import type { NextConfig } from 'next';
const backend = process.env.INTERNAL_API_URL || 'http://127.0.0.1:8000';
const config: NextConfig = {
  skipTrailingSlashRedirect: true,
  turbopack: { root: process.cwd() },
  output: 'standalone',
  poweredByHeader: false,
  async rewrites() {
    return [
      { source: '/api/:path*', destination: `${backend}/api/:path*/` },
      { source: '/media/:path*', destination: `${backend}/media/:path*` },
    ];
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
        ],
      },
    ];
  },
};
export default config;
