import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Lightbox from "@/components/Lightbox";

/* ── Latest Trailers rail ─────────────────────────
   Fed by /data/trailers.json (prebuilt from entertainment
   articles' YouTube embeds, gated to official trailer/
   teaser uploads only). Renders nothing when empty.

   Tapping a card opens the shared Lightbox with the
   video player — click the play button to watch. The
   article link lives below the player. */

interface Trailer {
  video_id: string;
  title: string;
  channel?: string;
  article_slug: string;
  article_title: string;
  published_at: string;
  thumbnail: string;
}

function TrailerPlayer({ videoId, title, thumbnail }: { videoId: string; title: string; thumbnail: string }) {
  const [playing, setPlaying] = useState(false);

  if (!playing) {
    return (
      <button
        onClick={() => setPlaying(true)}
        aria-label={`Play ${title}`}
        style={{
          position: "relative",
          width: "min(calc(100vw - 40px), 800px)",
          aspectRatio: "16 / 9",
          borderRadius: "8px",
          overflow: "hidden",
          border: "none",
          padding: 0,
          cursor: "pointer",
          background: "#000",
        }}
      >
        <img
          src={thumbnail}
          alt=""
          draggable={false}
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
        />
        <span
          style={{
            position: "absolute", inset: 0,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
        >
          <span
            style={{
              width: 64, height: 64, borderRadius: "50%",
              background: "rgba(163,45,47,0.92)",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
              <path d="M8 5v14l11-7z" />
            </svg>
          </span>
        </span>
      </button>
    );
  }

  return (
    <iframe
      src={`https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`}
      title={title}
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
      style={{
        width: "min(calc(100vw - 40px), 800px)",
        aspectRatio: "16 / 9",
        borderRadius: "8px",
        border: "none",
        background: "#000",
      }}
    />
  );
}

export default function TrailersRail() {
  const [trailers, setTrailers] = useState<Trailer[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

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

  const renderSlide = (i: number) => {
    const t = trailers[i];
    if (!t) return null;
    return <TrailerPlayer videoId={t.video_id} title={t.title} thumbnail={t.thumbnail} />;
  };

  const renderBelow = (i: number) => {
    const t = trailers[i];
    if (!t) return null;
    return (
      <div style={{ padding: "8px 20px 0", textAlign: "center" }}>
        <p style={{
          color: "#fff", fontSize: "15px", fontWeight: 600, lineHeight: 1.4,
          fontFamily: "var(--font-sans, sans-serif)",
          margin: "0 0 6px",
        }}>
          {t.title}
        </p>
        {t.channel && (
          <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "12px", margin: "0 0 12px" }}>
            via {t.channel}
          </p>
        )}
        <Link
          to={`/articles/${t.article_slug}`}
          style={{
            display: "inline-flex", alignItems: "center", gap: "6px",
            color: "#D4A843", fontSize: "13px", fontWeight: 600,
            textDecoration: "none",
            fontFamily: "var(--font-sans, sans-serif)",
          }}
        >
          Read the story <span>→</span>
        </Link>
      </div>
    );
  };

  return (
    <>
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
            {trailers.map((t, idx) => (
              <div
                key={t.video_id}
                onClick={() => setSelectedIndex(idx)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    setSelectedIndex(idx);
                  }
                }}
                className="group shrink-0 w-64 md:w-72 cursor-pointer"
              >
                <div className="relative w-64 md:w-72 aspect-video rounded-lg overflow-hidden bg-muted">
                  <img
                    src={t.thumbnail}
                    alt={t.title}
                    loading="lazy"
                    className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500 pointer-events-none"
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
              </div>
            ))}
          </div>
        </div>
      </section>

      <Lightbox
        open={selectedIndex !== null}
        initialIndex={selectedIndex ?? 0}
        count={trailers.length}
        onClose={() => setSelectedIndex(null)}
        renderSlide={renderSlide}
        renderBelow={renderBelow}
      />
    </>
  );
}
