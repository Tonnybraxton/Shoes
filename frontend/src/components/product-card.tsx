'use client';
import { useState } from 'react';
import Link from 'next/link';
import { Heart, ArrowUpRight, Check, Plus } from 'lucide-react';
import type { Product } from '@/lib/types';
import { money } from '@/lib/api';
import { imageSrcSet } from '@/lib/product-images';
import { useStore } from './store-provider';
export function ProductCard({ product }: { product: Product }) {
  const [active, setActive] = useState(product.default_variant_id),
    [expanded, setExpanded] = useState(false),
    [hover, setHover] = useState(false);
  const { wishlist, toggleWish, compare, toggleCompare } = useStore();
  const variant = product.variants.find((v) => v.id === active) || product.variants[0];
  if (!variant) return null;
  const picture =
    hover && variant.hover_image
      ? variant.images.find((img) => img.url === variant.hover_image)
      : variant.images[0];
  const sale = variant.compare_at_price && Number(variant.compare_at_price) > Number(variant.price);
  const shown = expanded
    ? product.variants
    : product.variants.slice(0, product.max_card_swatches || 4);
  return (
    <article className="product-card" data-testid="product-card" data-product-id={product.id}>
      <div
        className="product-visual"
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
      >
        <Link
          href={`/products/${product.slug}?color=${variant.id}`}
          aria-label={`${product.brand.name} ${product.name}, ${variant.color_name}`}
          className="product-image-link"
        >
          <img
            key={variant.id}
            className="product-image"
            src={
              hover && variant.hover_image
                ? variant.hover_image
                : variant.image || '/images/hero-original.png'
            }
            alt={`${product.name} in ${variant.color_name}`}
            srcSet={imageSrcSet(picture)}
            sizes="(max-width: 600px) 50vw, (max-width: 1100px) 33vw, 25vw"
            width="1000"
            height="800"
            loading="lazy"
          />
        </Link>
        {(product.badges[0] || sale) && (
          <span className={`product-badge ${sale ? 'sale-badge' : ''}`}>
            {sale ? 'Sale' : product.badges[0]}
          </span>
        )}
        <button
          className={`wish-button ${wishlist.includes(product.id) ? 'selected' : ''}`}
          aria-label={`${wishlist.includes(product.id) ? 'Remove' : 'Save'} ${product.name} ${wishlist.includes(product.id) ? 'from' : 'to'} wishlist`}
          aria-pressed={wishlist.includes(product.id)}
          onClick={() => void toggleWish(product)}
        >
          <Heart size={19} />
        </button>
        <Link href={`/products/${product.slug}?color=${variant.id}`} className="card-quick">
          Choose your size <ArrowUpRight size={17} />
        </Link>
      </div>
      <div className="swatch-row" aria-label={`${product.name} colorways`}>
        {shown.map((v) => (
          <button
            key={v.id}
            aria-label={`Select ${v.color_name} colorway`}
            aria-pressed={v.id === variant.id}
            className={`swatch ${v.id === variant.id ? 'active' : ''}`}
            style={{ '--swatch': v.color_code } as React.CSSProperties}
            onClick={() => {
              setActive(v.id);
              setHover(false);
            }}
            title={v.color_name}
          />
        ))}
        {!expanded && product.variants.length > shown.length && (
          <button
            className="swatch-more"
            aria-label={`Show ${product.variants.length - shown.length} more colorways`}
            onClick={() => setExpanded(true)}
          >
            +{product.variants.length - shown.length}
          </button>
        )}
      </div>
      <div className="product-info">
        <span className="brand-label">{product.brand.name}</span>
        <Link href={`/products/${product.slug}?color=${variant.id}`} className="product-name">
          {product.name}
        </Link>
        <p className="product-subtitle">{product.subtitle}</p>
        <p className="color-description" aria-live="polite">
          {variant.color_name}
          {!variant.in_stock ? ' · Out of stock' : ''}
        </p>
        <div className="price" aria-live="polite">
          {product.see_price_in_bag ? (
            'See price in bag'
          ) : (
            <>
              <span className={sale ? 'sale-text' : ''}>{money(variant.price)}</span>
              {sale && <del>{money(variant.compare_at_price!)}</del>}
            </>
          )}
        </div>
        {product.review_count > 0 && (
          <p className="review-small">
            ★ {product.rating} ({product.review_count} verified reviews)
          </p>
        )}
        <button
          className="compare-toggle"
          onClick={() => toggleCompare(product.id)}
          aria-pressed={compare.includes(product.id)}
        >
          {compare.includes(product.id) ? <Check size={13} /> : <Plus size={13} />}Compare
        </button>
      </div>
    </article>
  );
}
