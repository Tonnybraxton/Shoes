import { describe, expect, it } from 'vitest';
import { sectionSettings } from '@/lib/section-settings';

describe('CMS section settings', () => {
  it('reads published editorial and category content without inventing copy', () => {
    const settings = sectionSettings({
      eyebrow: 'Weekend edit',
      caption: 'An original studio photograph.',
      image_alt: 'A chalk sneaker on a stone plinth',
      tiles: [{ title: 'Trail', subtitle: 'Find your path.', href: '/shop?category=outdoor' }],
    });
    expect(settings.caption).toBe('An original studio photograph.');
    expect(settings.tiles).toEqual([
      { title: 'Trail', subtitle: 'Find your path.', href: '/shop?category=outdoor' },
    ]);
    expect(settings.footnote).toBe('');
  });

  it.each([null, [], 'invalid', 123])('tolerates invalid settings %s', (value) => {
    expect(sectionSettings(value).tiles).toEqual([]);
    expect(sectionSettings(value).caption).toBe('');
  });

  it('drops unsafe or malformed tiles and bounds presentation content', () => {
    const settings = sectionSettings({
      caption: { html: '<script>bad</script>' },
      tiles: [
        { title: 'Unsafe', href: '//outside.example' },
        { title: 'Backslash', href: '/\\outside.example' },
        null,
        { title: '', href: '/shop' },
        { title: 'A'.repeat(100), subtitle: 'B'.repeat(200), href: '/men' },
      ],
    });
    expect(settings.caption).toBe('');
    expect(settings.tiles).toEqual([
      { title: 'A'.repeat(80), subtitle: 'B'.repeat(160), href: '/men' },
    ]);
  });
});
