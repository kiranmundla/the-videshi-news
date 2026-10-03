import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

/* ── Latest Trailers rail ─────────────────────────
   Fed by /data/trailers.json (prebuilt from entertainment
   articles' YouTube embeds). Renders nothing when empty. */

interface Trailer {
  video_id: string;
  title: string;
  article_slug: string;
  article_title: string;
  published_at: string;
  thumbnail: string;
}

export default function TrailersRail() {
  const [trailers, setTrailers] = useState<Trailer[]>([]);

  useEffect(() => {
    fetch("/data/trailers.json")
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then((d) => {
        if (d?.trailers?.length) setTrailers(d.trailers.slice(0, 12));
      })
      .catch(() => {});
  }, []);

  if (trailers.length === 0) return null;

  return (
    <section className="mb-14">
      <div className="container">
        <div
          className="flex items-center mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #A32D2F" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            Latest Trailers
          </h2>
        </div>
        <div className="flex gap-5 overflow-x-auto pb-2 -mx-1 px-1">
          {trailers.map((t) => (
            <Link
              key={t.video_id}
              to={`/articles/${t.article_slug}`}
              className="group shrink-0 w-64 md:w-72"
            >
              <div className="relative w-64 md:w-72 aspect-video rounded-lg overflow-hidden bg-muted">
                <img
                  src={t.thumbnail}
                  alt={t.title}
                  loading="lazy"
                  className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-black/25 group-hover:bg-black/10 transition-colors" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span
                    className="w-12 h-12 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform"
                    style={{ background: "rgba(163,45,47,0.92)" }}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </span>
                </div>
              </div>
              <p className="mt-2 font-serif font-bold text-[0.95rem] leading-snug line-clamp-2 group-hover:text-primary transition-colors">
                {t.title}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
