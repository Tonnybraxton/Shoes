export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public fields: unknown = {},
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
let csrfToken = '';
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (options.method && !['GET', 'HEAD'].includes(options.method) && !csrfToken) {
    const session = await api<{ csrf_token: string }>('/session/');
    csrfToken = session.csrf_token;
  }
  const response = await fetch(`/api/v1${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
      ...options.headers,
    },
  });
  if (response.status === 204) return undefined as T;
  const data = await response
    .json()
    .catch(() => ({ error: { message: 'The service could not be reached. Please try again.' } }));
  if (!response.ok)
    throw new ApiError(
      data.error?.message || 'Something went wrong.',
      response.status,
      data.error?.fields,
    );
  if (data.csrf_token) csrfToken = data.csrf_token;
  return data as T;
}
export const post = <T>(path: string, body: unknown, method = 'POST') =>
  api<T>(path, { method, body: JSON.stringify(body) });
export function money(value: string | number, currency = 'KES') {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })
    .formatToParts(Number(value))
    .map((part) => (part.type === 'currency' && currency === 'KES' ? 'KSh' : part.value))
    .join('');
}
export function safeHref(href: unknown) {
  return typeof href === 'string' &&
    /^\/(?![\/\\])/.test(href) &&
    !/[\\\u0000-\u0020\u007f]/.test(href)
    ? href
    : '/shop';
}
