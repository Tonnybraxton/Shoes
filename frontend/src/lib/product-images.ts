import type { Variant } from './types';

// The backend has already validated and encoded these files. Let the browser
// choose a rendition without another image-processing request through Next.js.
export function imageSrcSet(image: Variant['images'][number] | undefined) {
  if (!image?.renditions?.length) return undefined;
  return [...image.renditions, { url: image.url, width: image.width }]
    .map(({ url, width }) => `${url} ${width}w`)
    .join(', ');
}
