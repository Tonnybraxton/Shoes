import { NextRequest, NextResponse } from 'next/server';
import { mediaOrigin } from './lib/media-origin';

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const dev = process.env.NODE_ENV === 'development';
  const media = mediaOrigin(process.env.MEDIA_ORIGIN);
  const csp = `default-src 'self'; script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${dev ? " 'unsafe-eval'" : ''}; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:${media ? ' ' + media : ''}; font-src 'self'; connect-src 'self'${dev ? ' ws:' : ''}; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none';`;
  const headers = new Headers(request.headers);
  headers.set('x-nonce', nonce);
  headers.set('Content-Security-Policy', csp);
  const response = NextResponse.next({ request: { headers } });
  response.headers.set('Content-Security-Policy', csp);
  return response;
}
export const config = {
  matcher: ['/((?!api|media|_next/static|_next/image|favicon.ico|images).*)'],
};
