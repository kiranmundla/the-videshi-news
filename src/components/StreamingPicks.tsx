import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ScrollWrap from "./homepage/ScrollWrap";

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
  rank?: number;
  trending?: boolean;
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

        {/* Trending badge */}
        {pick.trending && (
          <div
            style={{
              position: "absolute",
              top: 6,
              right: 6,
              background: "linear-gradient(135deg, #ff6b35, #e50914)",
              color: "#fff",
              fontSize: 8,
              fontWeight: 700,
              padding: "2px 6px",
              borderRadius: 4,
              letterSpacing: "0.05em",
              textTransform: "uppercase" as const,
              display: "flex",
              alignItems: "center",
              gap: 2,
            }}
          >
            🔥 Trending
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

  if (!data || !data.picks.length) return null;

  return (
    <section className="mt-6 mb-4">
      <div className="container">
      <div
        className="flex items-center gap-3 mb-3 pb-2"
        style={{ borderBottom: "1px solid rgba(173,20,87,0.25)" }}
      >
        <span
          className="font-bold uppercase"
          style={{ fontSize: 11, letterSpacing: "0.12em", color: "#AD1457" }}
        >
          🎬 What to Watch This Week
        </span>
        <span style={{ marginLeft: "auto", color: "#aaa", fontSize: 10, fontStyle: "italic" }}>
          {data.week_of}
        </span>
      </div>

      <ScrollWrap className="pl-4 gap-3.5">
        {data.picks.map((pick) => (
          <PosterCard
            key={pick.slug}
            pick={pick}
            onClick={() => navigate(`/movies/${pick.slug}`)}
          />
        ))}
      </ScrollWrap>
      </div>
    </section>
  );
}
