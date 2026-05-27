import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";

interface StreamingPick {
  title: string;
  slug: string;
  platform: string;
  platform_icon: string;
  genre: string;
  year: number;
  poster_url: string;
  backdrop_url: string;
  trailer_url: string;
  synopsis: string;
  cast: string[];
  director: string;
  why_watch: string;
  is_indian: boolean;
  watch_url: string;
  language: string;
}

interface StreamingData {
  generated_at: string;
  week_of: string;
  editorial_intro: string;
  picks: StreamingPick[];
}

const PLATFORM_COLORS: Record<string, string> = {
  netflix: "#E50914",
  prime: "#00A8E1",
  hotstar: "#0c0c0c",
  "apple tv+": "#000",
  hulu: "#1CE783",
  hbo: "#B535F6",
  max: "#B535F6",
  "disney+": "#113CCF",
  jiocinema: "#E8078A",
  zee5: "#8230C6",
  sonyliv: "#001F5B",
};

function getPlatformColor(icon: string): string {
  return PLATFORM_COLORS[icon] || "#555";
}

/* ── Poster placeholder when no image ── */
function PosterFallback({ title, platform, genre }: { title: string; platform: string; genre: string }) {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: `linear-gradient(135deg, ${getPlatformColor(platform.toLowerCase())}22 0%, #1a1a2e 50%, #0f3460 100%)`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "16px 12px",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 28, marginBottom: 8 }}>🎬</div>
      <div
        style={{
          color: "#fff",
          fontSize: 13,
          fontWeight: 700,
          lineHeight: 1.3,
          fontFamily: "var(--font-serif, 'Playfair Display', serif)",
          display: "-webkit-box",
          WebkitLineClamp: 3,
          WebkitBoxOrient: "vertical" as const,
          overflow: "hidden",
        }}
      >
        {title}
      </div>
      <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 10, marginTop: 6 }}>{genre}</div>
    </div>
  );
}

/* ── Single poster card ── */
function PosterCard({ pick, onClick }: { pick: StreamingPick; onClick: () => void }) {
  const [imgError, setImgError] = useState(false);
  const platformColor = getPlatformColor(pick.platform_icon || pick.platform.toLowerCase());

  return (
    <div
      onClick={onClick}
      style={{
        flexShrink: 0,
        width: 140,
        cursor: "pointer",
        scrollSnapAlign: "start",
      }}
    >
      {/* Poster */}
      <div
        style={{
          width: 140,
          height: 210,
          borderRadius: 10,
          overflow: "hidden",
          background: "#1a1a1a",
          boxShadow: "0 2px 10px rgba(0,0,0,0.15)",
          position: "relative",
        }}
      >
        {pick.poster_url && !imgError ? (
          <img
            src={pick.poster_url}
            alt={pick.title}
            loading="lazy"
            onError={() => setImgError(true)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              display: "block",
            }}
          />
        ) : (
          <PosterFallback title={pick.title} platform={pick.platform} genre={pick.genre} />
        )}

        {/* Language badge */}
        {pick.language && pick.language !== "English" && (
          <div
            style={{
              position: "absolute",
              top: 6,
              left: 6,
              background: "rgba(0,0,0,0.7)",
              backdropFilter: "blur(4px)",
              color: "#fff",
              fontSize: 9,
              fontWeight: 600,
              padding: "2px 6px",
              borderRadius: 4,
              letterSpacing: "0.03em",
            }}
          >
            {pick.language}
          </div>
        )}
      </div>

      {/* Title + platform */}
      <div style={{ padding: "6px 2px 0" }}>
        <div
          style={{
            color: "#1a1a1a",
            fontSize: 12.5,
            fontWeight: 600,
            fontFamily: "var(--font-sans, system-ui, sans-serif)",
            lineHeight: 1.3,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical" as const,
            overflow: "hidden",
          }}
        >
          {pick.title}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 3 }}>
          <span
            style={{
              display: "inline-block",
              background: platformColor,
              color: "#fff",
              fontSize: 9,
              fontWeight: 700,
              padding: "1.5px 5px",
              borderRadius: 3,
              letterSpacing: "0.02em",
              lineHeight: 1.4,
            }}
          >
            {pick.platform}
          </span>
          <span style={{ color: "#999", fontSize: 10 }}>{pick.genre}</span>
        </div>
      </div>
    </div>
  );
}

/* ── Main component ── */
export default function StreamingPicks() {
  const [data, setData] = useState<StreamingData | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/data/streaming-picks.json")
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then((d: StreamingData) => {
        if (d?.picks?.length) setData(d);
      })
      .catch(() => {});
  }, []);

  const updateScrollButtons = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 10);
  }, []);

  const scrollStrip = useCallback((direction: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const amount = el.clientWidth * 0.75;
    el.scrollBy({ left: direction === "right" ? amount : -amount, behavior: "smooth" });
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el || !data) return;
    updateScrollButtons();
    el.addEventListener("scroll", updateScrollButtons, { passive: true });
    window.addEventListener("resize", updateScrollButtons);
    return () => {
      el.removeEventListener("scroll", updateScrollButtons);
      window.removeEventListener("resize", updateScrollButtons);
    };
  }, [data, updateScrollButtons]);

  if (!data || !data.picks.length) return null;

  const arrowStyle: React.CSSProperties = {
    position: "absolute",
    top: "calc(50% - 20px)",
    transform: "translateY(-50%)",
    zIndex: 10,
    background: "rgba(0,0,0,0.55)",
    backdropFilter: "blur(4px)",
    border: "none",
    color: "#fff",
    fontSize: 16,
    width: 32,
    height: 32,
    borderRadius: "50%",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.2s, opacity 0.2s",
    opacity: 0.9,
  };

  return (
    <section className="mt-6 mb-4">
      <style>{`
        .streaming-scroll::-webkit-scrollbar { display: none; }
      `}</style>

      <div
        className="flex items-center gap-3 mb-3 pb-2"
        style={{ borderBottom: "1px solid hsl(var(--rule))" }}
      >
        <span
          className="font-bold uppercase"
          style={{ fontSize: 11, letterSpacing: "0.12em", color: "#888" }}
        >
          🎬 What to Watch This Week
        </span>
        <span style={{ marginLeft: "auto", color: "#aaa", fontSize: 10, fontStyle: "italic" }}>
          {data.week_of}
        </span>
      </div>

      <div style={{ position: "relative" }}>
        {/* Left arrow */}
        {canScrollLeft && (
          <button
            onClick={() => scrollStrip("left")}
            style={{ ...arrowStyle, left: 4 }}
            className="hidden md:flex"
            aria-label="Scroll left"
          >
            ‹
          </button>
        )}

        {/* Scroll container */}
        <div
          ref={scrollRef}
          className="streaming-scroll"
          style={{
            display: "flex",
            gap: 14,
            overflowX: "auto",
            overflowY: "hidden",
            WebkitOverflowScrolling: "touch",
            scrollbarWidth: "none",
            msOverflowStyle: "none",
            scrollSnapType: "x mandatory",
            paddingLeft: "2%",
            paddingRight: "2%",
            paddingBottom: 4,
          } as React.CSSProperties}
        >
          {data.picks.map((pick) => (
            <PosterCard
              key={pick.slug}
              pick={pick}
              onClick={() => navigate(`/watch/${pick.slug}`)}
            />
          ))}
        </div>

        {/* Right arrow */}
        {canScrollRight && (
          <button
            onClick={() => scrollStrip("right")}
            style={{ ...arrowStyle, right: 4 }}
            className="hidden md:flex"
            aria-label="Scroll right"
          >
            ›
          </button>
        )}
      </div>
    </section>
  );
}
