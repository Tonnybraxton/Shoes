import { describe, expect, it } from 'vitest';
import { mediaOrigin } from '@/lib/media-origin';

describe('configured media CSP origin', () => {
  it('allows an explicit HTTPS storage origin', () => {
    expect(mediaOrigin('https://media.example.test/')).toBe('https://media.example.test');
  });
  it.each([
    undefined,
    '',
    'http://media.example.test',
    '//media.example.test',
    'https://user:secret@media.example.test',
    'https://media.example.test/path',
    'https://media.example.test; script-src *',
    'https://media.example.test/?x=y',
  ])('rejects invalid or non-origin values %s', (value) => {
    expect(mediaOrigin(value)).toBe('');
  });
});
