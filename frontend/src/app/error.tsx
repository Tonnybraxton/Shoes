'use client';
export default function Error({ reset }: { reset: () => void }) {
  return (
    <section className="empty-state wrap">
      <h1>Something interrupted your visit.</h1>
      <p>Please try again. Your saved bag stays with your session.</p>
      <button className="button" onClick={reset}>
        Try again
      </button>
    </section>
  );
}
