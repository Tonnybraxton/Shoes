import 'server-only';
import { ApiError } from './api';
export async function serverApi<T>(path: string): Promise<T> {
  const response = await fetch(
    `${process.env.INTERNAL_API_URL || 'http://127.0.0.1:8000'}/api/v1${path}`,
    { cache: 'no-store', signal: AbortSignal.timeout(15000) },
  );
  if (!response.ok) throw new ApiError('The store is temporarily unavailable.', response.status);
  return response.json() as Promise<T>;
}
