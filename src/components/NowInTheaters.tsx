import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ScrollWrap from "./homepage/ScrollWrap";

interface TheaterMovie {
  title: string;
  slug: string;
  genre: string;
  year: number;
  poster_url: string;
  rating: string;
  rating_source: string;
  release_date: string;
  status: "now_playing" | "opening" | "coming_soon";
  cast: string[];
  director: string;
  why_watch: string;
  is_indian: boolean;
  ticket_url: string;
  language: string;
}

interface TheaterData {
  generated_at: string;
  week_of: string;
  editorial_intro: string;
  movies: TheaterMovie[];
}

const STATUS_CONFIG: Record<string, { label: string; bg: string; color: string }> = {
  now_playing: { label: "Now Playing", bg: "#16a34a", color: "#fff" },
  opening: { label: "Opening This Week", bg: "#d97706", color: "#fff" },
  coming_soon: { label: "Coming Soon", bg: "#64748b", color: "#fff" },
};

/* ── Poster fallback ── */
function PosterFallback({ title, genre }: { title: string; genre: string }) {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
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

/* ── Format release date ── */
function formatRelease(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/* ── Single movie card ── */
function MovieCard({ movie, onClick }: { movie: TheaterMovie; onClick: () => void }) {
  const [imgError, setImgError] = useState(false);
  const statusCfg = STATUS_CONFIG[movie.status] || STATUS_CONFIG.coming_soon;

  return (
    <div
      onClick={onClick}
      style={{
        flexShrink: 0,
        width: 150,
        cursor: "pointer",
        scrollSnapAlign: "start",
      }}
    >
      {/* Poster */}
      <div
        style={{
          width: 150,
          height: 225,
          borderRadius: 10,
          overflow: "hidden",
          background: "#1a1a1a",
          boxShadow: "0 2px 10px rgba(0,0,0,0.15)",
          position: "relative",
        }}
      >
        {movie.poster_url && !imgError ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
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
          <PosterFallback title={movie.title} genre={movie.genre} />
        )}

        {/* Language badge (non-English) */}
        {movie.language && movie.language !== "English" && (
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
            {movie.language}
          </div>
        )}

        {/* Indian flag badge */}
        {movie.is_indian && (
          <div
            style={{
              position: "absolute",
              top: 6,
              right: 6,
              background: "linear-gradient(135deg, #ff9933, #138808)",
              color: "#fff",
              fontSize: 8,
              fontWeight: 700,
              padding: "2px 6px",
              borderRadius: 4,
              letterSpacing: "0.05em",
              textTransform: "uppercase" as const,
            }}
          >
            🇮🇳 Desi
          </div>
        )}

        {/* Status badge at bottom of poster */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            background: "linear-gradient(transparent, rgba(0,0,0,0.85))",
            padding: "16px 8px 6px",
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <span
            style={{
              background: statusCfg.bg,
              color: statusCfg.color,
              fontSize: 8,
              fontWeight: 700,
              padding: "2px 5px",
              borderRadius: 3,
              letterSpacing: "0.03em",
              textTransform: "uppercase" as const,
            }}
          >
            {movie.status === "now_playing" ? statusCfg.label : formatRelease(movie.release_date)}
          </span>
          {movie.rating && (
            <span
              style={{
                color: "#fbbf24",
                fontSize: 9,
                fontWeight: 600,
              }}
            >
              ★ {movie.rating}
            </span>
          )}
        </div>
      </div>

      {/* Title + genre below poster */}
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
          {movie.title}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 3 }}>
          <span style={{ color: "#999", fontSize: 10 }}>{movie.genre}</span>
          {movie.director && (
            <span style={{ color: "#bbb", fontSize: 9 }}>· {movie.director}</span>
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Main component ── */
export default function NowInTheaters() {
  const [data, setData] = useState<TheaterData | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/data/now-in-theaters.json")
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then((d: TheaterData) => {
        if (d?.movies?.length) setData(d);
      })
      .catch(() => {});
  }, []);

  if (!data || !data.movies.length) return null;

  return (
    <section className="mt-6 mb-2">
      <div className="container">
      <div
        className="flex items-center gap-3 mb-3 pb-2"
        style={{ borderBottom: "1px solid rgba(173,20,87,0.25)" }}
      >
        <span
          className="font-bold uppercase"
          style={{ fontSize: 11, letterSpacing: "0.12em", color: "#AD1457" }}
        >
          🍿 Now in Theaters
        </span>
        <span style={{ marginLeft: "auto", color: "#aaa", fontSize: 10, fontStyle: "italic" }}>
          {data.week_of}
        </span>
      </div>

      <ScrollWrap className="pl-4 gap-3.5">
        {[...data.movies].sort((a, b) => b.release_date.localeCompare(a.release_date)).map((movie) => (
          <MovieCard
            key={movie.slug}
            movie={movie}
            onClick={() => navigate(`/movies/${movie.slug}`)}
          />
        ))}
      </ScrollWrap>
      </div>
    </section>
  );
}
