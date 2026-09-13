import { safeHref } from './api';

export type CategoryTile = { title: string; subtitle: string; href: string };
export type SectionSettings = {
  eyebrow: string;
  image_alt: string;
  footnote: string;
  edition: string;
  caption: string;
  tiles: CategoryTile[];
};

const record = (value: unknown): Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};

const text = (value: unknown, limit = 240) =>
  typeof value === 'string' ? value.trim().slice(0, limit) : '';

// Admin validation is authoritative; this also makes old or malformed content safe to render.
export function sectionSettings(value: unknown): SectionSettings {
  const settings = record(value);
  const tiles = Array.isArray(settings.tiles)
    ? settings.tiles.slice(0, 6).flatMap((value) => {
        const tile = record(value);
        const title = text(tile.title, 80);
        const href = text(tile.href, 500);
        if (!title || !href || safeHref(href) !== href) return [];
        return [{ title, subtitle: text(tile.subtitle, 160), href }];
      })
    : [];
  return {
    eyebrow: text(settings.eyebrow, 120),
    image_alt: text(settings.image_alt, 240),
    footnote: text(settings.footnote, 160),
    edition: text(settings.edition, 80),
    caption: text(settings.caption, 240),
    tiles,
  };
}
