import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";

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

function extractYouTubeId(url: string): string | null {
  const m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([A-Za-z0-9_-]{11})/);
  return m ? m[1] : null;
}

export default function WatchDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [pick, setPick] = useState<StreamingPick | null>(null);
  const [allPicks, setAllPicks] = useState<StreamingPick[]>([]);
  const [loading, setLoading] = useState(true);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    fetch("/data/streaming-picks.json")
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then((data) => {
        const picks: StreamingPick[] = data?.picks || [];
        setAllPicks(picks);
        const found = picks.find((p: StreamingPick) => p.slug === slug);
        setPick(found || null);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  if (!pick) {
    return (
      <div className="min-h-screen bg-background">
        <Masthead />
        <main className="container py-20 text-center">
          <p className="smallcaps text-primary">404</p>
          <h1 className="font-serif text-3xl mt-3">Show not found</h1>
          <Link to="/" className="text-primary mt-6 inline-block hover:underline">
            ← Back to homepage
          </Link>
        </main>
        <SiteFooter lastUpdated={null} />
      </div>
    );
  }

  const platformColor = getPlatformColor(pick.platform_icon || pick.platform.toLowerCase());
  const youtubeId = pick.trailer_url ? extractYouTubeId(pick.trailer_url) : null;
  const isYouTubeSearch = pick.trailer_url?.includes("youtube.com/results");
  const relatedPicks = allPicks.filter((p) => p.slug !== pick.slug).slice(0, 4);

  return (
    <div className="min-h-screen bg-background">
      <Helmet>
        <title>{pick.title} — What to Watch | The Videshi</title>
        <meta name="description" content={pick.why_watch} />
        {pick.poster_url && <meta property="og:image" content={pick.poster_url} />}
        <meta property="og:title" content={`${pick.title} — What to Watch | The Videshi`} />
      </Helmet>

      <Masthead />

      <main style={{ maxWidth: 720, margin: "0 auto", padding: "0 16px" }}>
        {/* Back link */}
        <div style={{ padding: "16px 0 8px" }}>
          <Link
            to="/"
            style={{
              color: "#888",
              fontSize: 12,
              textDecoration: "none",
              letterSpacing: "0.06em",
              textTransform: "uppercase" as const,
              fontWeight: 600,
            }}
          >
            ← Entertainment
          </Link>
        </div>

        {/* Hero section */}
        <div
          style={{
            position: "relative",
            borderRadius: 14,
            overflow: "hidden",
            background: "#111",
            marginBottom: 24,
          }}
        >
          {/* Poster / backdrop */}
          {(pick.poster_url || pick.backdrop_url) && !imgError ? (
            <div style={{ position: "relative" }}>
              <img
                src={pick.backdrop_url || pick.poster_url}
                alt={pick.title}
                onError={() => setImgError(true)}
                style={{
                  width: "100%",
                  maxHeight: pick.backdrop_url ? 360 : 420,
                  objectFit: "cover",
                  display: "block",
                }}
              />
              {/* Gradient overlay */}
              <div
                style={{
                  position: "absolute",
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: "60%",
                  background: "linear-gradient(transparent, rgba(0,0,0,0.85))",
                }}
              />
              {/* Title overlay */}
              <div
                style={{
                  position: "absolute",
                  bottom: 16,
                  left: 16,
                  right: 16,
                }}
              >
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8, flexWrap: "wrap" }}>
                  <span
                    style={{
                      background: platformColor,
                      color: "#fff",
                      fontSize: 11,
                      fontWeight: 700,
                      padding: "3px 8px",
                      borderRadius: 4,
                    }}
                  >
                    {pick.platform}
                  </span>
                  <span style={{ color: "rgba(255,255,255,0.7)", fontSize: 12 }}>{pick.genre}</span>
                  {pick.year > 0 && (
                    <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 12 }}>{pick.year}</span>
                  )}
                  {pick.language && pick.language !== "English" && (
                    <span
                      style={{
                        background: "rgba(255,255,255,0.15)",
                        color: "#fff",
                        fontSize: 10,
                        fontWeight: 600,
                        padding: "2px 6px",
                        borderRadius: 3,
                      }}
                    >
                      {pick.language}
                    </span>
                  )}
                </div>
                <h1
                  style={{
                    color: "#fff",
                    fontFamily: "var(--font-serif, 'Playfair Display', serif)",
                    fontSize: "clamp(22px, 5vw, 32px)",
                    fontWeight: 800,
                    lineHeight: 1.2,
                    margin: 0,
                  }}
                >
                  {pick.title}
                </h1>
              </div>
            </div>
          ) : (
            /* No-image fallback hero */
            <div
              style={{
                padding: "40px 20px 24px",
                background: `linear-gradient(135deg, ${platformColor}33 0%, #1a1a2e 50%, #0f3460 100%)`,
              }}
            >
              <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, flexWrap: "wrap" }}>
                <span
                  style={{
                    background: platformColor,
                    color: "#fff",
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "3px 8px",
                    borderRadius: 4,
                  }}
                >
                  {pick.platform}
                </span>
                <span style={{ color: "rgba(255,255,255,0.7)", fontSize: 12 }}>{pick.genre}</span>
                {pick.year > 0 && (
                  <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 12 }}>{pick.year}</span>
                )}
                {pick.language && pick.language !== "English" && (
                  <span
                    style={{
                      background: "rgba(255,255,255,0.15)",
                      color: "#fff",
                      fontSize: 10,
                      fontWeight: 600,
                      padding: "2px 6px",
                      borderRadius: 3,
                    }}
                  >
                    {pick.language}
                  </span>
                )}
              </div>
              <h1
                style={{
                  color: "#fff",
                  fontFamily: "var(--font-serif, 'Playfair Display', serif)",
                  fontSize: "clamp(24px, 5vw, 36px)",
                  fontWeight: 800,
                  lineHeight: 1.2,
                  margin: 0,
                }}
              >
                {pick.title}
              </h1>
            </div>
          )}
        </div>

        {/* Why Watch — editorial callout */}
        {pick.why_watch && (
          <div
            style={{
              borderLeft: `3px solid ${platformColor}`,
              padding: "12px 16px",
              marginBottom: 24,
              background: "hsl(var(--muted) / 0.3)",
              borderRadius: "0 8px 8px 0",
            }}
          >
            <p
              style={{
                margin: 0,
                fontFamily: "var(--font-serif, 'Source Serif 4', serif)",
                fontSize: 16,
                lineHeight: 1.6,
                fontStyle: "italic",
                color: "hsl(var(--foreground))",
              }}
            >
              {pick.why_watch}
            </p>
          </div>
        )}

        {/* Trailer */}
        {pick.trailer_url && (
          <div style={{ marginBottom: 24 }}>
            {youtubeId ? (
              <div
                style={{
                  position: "relative",
                  width: "100%",
                  paddingBottom: "56.25%",
                  borderRadius: 10,
                  overflow: "hidden",
                  background: "#000",
                }}
              >
                <iframe
                  src={`https://www.youtube.com/embed/${youtubeId}?rel=0`}
                  title={`${pick.title} trailer`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  loading="lazy"
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: "100%",
                    border: "none",
                  }}
                />
              </div>
            ) : (
              <a
                href={pick.trailer_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "12px 16px",
                  background: "#111",
                  color: "#fff",
                  borderRadius: 10,
                  textDecoration: "none",
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                <span style={{ fontSize: 20 }}>▶</span>
                {isYouTubeSearch ? "Search for trailer on YouTube" : "Watch Trailer"}
              </a>
            )}
          </div>
        )}

        {/* Synopsis */}
        {pick.synopsis && (
          <div style={{ marginBottom: 24 }}>
            <h2
              style={{
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: "0.12em",
                textTransform: "uppercase" as const,
                color: "#888",
                marginBottom: 10,
              }}
            >
              Synopsis
            </h2>
            <p
              style={{
                fontFamily: "var(--font-serif, 'Source Serif 4', serif)",
                fontSize: 16,
                lineHeight: 1.7,
                color: "hsl(var(--foreground))",
                margin: 0,
              }}
            >
              {pick.synopsis}
            </p>
          </div>
        )}

        {/* Cast & Director */}
        {(pick.cast.length > 0 || pick.director) && (
          <div style={{ marginBottom: 24 }}>
            {pick.director && (
              <div style={{ marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: "#888", letterSpacing: "0.1em", textTransform: "uppercase" as const }}>
                  Director
                </span>
                <p style={{ margin: "4px 0 0", fontSize: 15 }}>{pick.director}</p>
              </div>
            )}
            {pick.cast.length > 0 && (
              <div>
                <span style={{ fontSize: 11, fontWeight: 700, color: "#888", letterSpacing: "0.1em", textTransform: "uppercase" as const }}>
                  Cast
                </span>
                <p style={{ margin: "4px 0 0", fontSize: 15 }}>{pick.cast.join(", ")}</p>
              </div>
            )}
          </div>
        )}

        {/* Watch Now button */}
        {pick.watch_url && (
          <a
            href={pick.watch_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              background: platformColor,
              color: "#fff",
              fontSize: 14,
              fontWeight: 700,
              padding: "12px 24px",
              borderRadius: 8,
              textDecoration: "none",
              marginBottom: 32,
              transition: "opacity 0.2s",
            }}
          >
            ▶ Watch on {pick.platform}
          </a>
        )}

        {/* More picks */}
        {relatedPicks.length > 0 && (
          <div style={{ marginTop: 16, marginBottom: 40, paddingTop: 20, borderTop: "1px solid hsl(var(--rule))" }}>
            <h3
              style={{
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: "0.12em",
                textTransform: "uppercase" as const,
                color: "#888",
                marginBottom: 14,
              }}
            >
              More This Week
            </h3>
            <div style={{ display: "flex", gap: 14, overflowX: "auto", paddingBottom: 8 }}>
              {relatedPicks.map((rp) => (
                <Link
                  key={rp.slug}
                  to={`/watch/${rp.slug}`}
                  style={{ textDecoration: "none", color: "inherit", flexShrink: 0 }}
                >
                  <div
                    style={{
                      width: 110,
                      height: 165,
                      borderRadius: 8,
                      overflow: "hidden",
                      background: "#1a1a1a",
                    }}
                  >
                    {rp.poster_url ? (
                      <img
                        src={rp.poster_url}
                        alt={rp.title}
                        loading="lazy"
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                    ) : (
                      <div
                        style={{
                          width: "100%",
                          height: "100%",
                          background: `linear-gradient(135deg, ${getPlatformColor(rp.platform_icon)}22, #1a1a2e)`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          padding: 8,
                        }}
                      >
                        <span style={{ color: "#fff", fontSize: 11, fontWeight: 600, textAlign: "center" }}>
                          {rp.title}
                        </span>
                      </div>
                    )}
                  </div>
                  <div style={{ width: 110, marginTop: 4 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, lineHeight: 1.3, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {rp.title}
                    </div>
                    <div style={{ fontSize: 9, color: "#999" }}>{rp.platform}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </main>

      <SiteFooter lastUpdated={null} />
    </div>
  );
}
