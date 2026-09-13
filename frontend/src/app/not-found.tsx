import Link from 'next/link';
export default function NotFound() {
  return (
    <section className="empty-state wrap">
      <span className="eyebrow">404 / A DIFFERENT DIRECTION</span>
      <h1>This page has moved on.</h1>
      <p>There are plenty of good pairs still to discover.</p>
      <Link className="button" href="/shop">
        Explore the collection
      </Link>
    </section>
  );
}
