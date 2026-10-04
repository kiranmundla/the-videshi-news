import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

/* ── Movie Reviews rail ───────────────────────────────────────
   Fed by /data/movie-reviews.json (prebuilt from the full
   published archive — every entertainment review, newest
   first). Renders nothing when empty. */

interface ReviewArticle {
  id: string;
  headline: string;
  slug: string;
  published_at: string;
  image_url?: string | null;
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

export default function MovieReviewsRail() {
  const [reviews, setReviews] = useState<ReviewArticle[]>([]);

  useEffect(() => {
    fetch("/data/movie-reviews.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (j && Array.isArray(j.articles)) setReviews(j.articles);
      })
      .catch(() => {});
  }, []);

  if (reviews.length === 0) return null;

  return (
    <section className="mb-14">
      <div className="container">
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #D4A843" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            Movie Reviews
          </h2>
          <span className="text-[11px] text-muted-foreground">
            {reviews.length} review{reviews.length === 1 ? "" : "s"}
          </span>
        </div>
        <div className="flex gap-5 overflow-x-auto pb-2 -mx-1 px-1">
          {reviews.slice(0, 12).map((a) => (
            <Link
              key={a.id}
              to={`/articles/${a.slug ?? a.id}`}
              className="group shrink-0 w-40 md:w-44"
            >
              <div className="relative w-40 md:w-44 aspect-[2/3] rounded-lg overflow-hidden bg-muted">
                {a.image_url ? (
                  <img
                    src={a.image_url}
                    alt={a.headline}
                    loading="lazy"
                    className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
                  />
                ) : (
                  <div
                    className="w-full h-full flex items-center justify-center"
                    style={{ background: "#0B1D3A" }}
                  >
                    <span
                      className="font-serif font-bold text-4xl"
                      style={{ color: "#D4A843" }}
                    >
                      V
                    </span>
                  </div>
                )}
                <span className="absolute top-2 left-2 text-[10px] font-bold tracking-[1px] uppercase text-white bg-black/60 rounded px-2 py-0.5">
                  Review
                </span>
              </div>
              <p className="mt-2 font-serif font-bold text-[0.95rem] leading-snug line-clamp-2 group-hover:text-primary transition-colors">
                {a.headline}
              </p>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                {fmtDate(a.published_at)}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
