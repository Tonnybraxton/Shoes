export default function Loading() {
  return (
    <div className="wrap section" role="status" aria-label="Loading store">
      <div className="skeleton skeleton-heading" />
      <div className="product-grid">
        {[1, 2, 3, 4].map((i) => (
          <div className="skeleton skeleton-card" key={i} />
        ))}
      </div>
    </div>
  );
}
