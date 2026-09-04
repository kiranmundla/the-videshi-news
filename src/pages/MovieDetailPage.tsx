import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";

/* ── Review article type ── */
interface ReviewRatings {
  type: "movie_review_ratings";
  star_rating: number;
  category_ratings: Record<string, number>;
  rating_consensus: string | null;
}

interface ReviewArticle {
  id: string;
  headline: string;
  slug: string;
  body: string;
  sources: string[];
  published_at: string;
  data_cards: ReviewRatings[] | null;
}

/* ── Types ── */

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
  cast_details?: { name: string; photo_url: string }[];
  director: string;
  why_watch: string;
  is_indian: boolean;
  ticket_url: string;
  language: string;
  trailer_url?: string;
}

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
  cast_details?: { name: string; photo_url: string }[];
  director: string;
  why_watch: string;
  is_indian: boolean;
  watch_url: string;
  language: string;
  trending?: boolean;
}

type MovieSource = "theater" | "streaming";

interface UnifiedMovie {
  source: MovieSource;
  title: string;
  slug: string;
  genre: string;
  year: number;
  poster_url: string;
  backdrop_url?: string;
  rating?: string;
  rating_source?: string;
  release_date?: string;
  status?: "now_playing" | "opening" | "coming_soon";
  platform?: string;
  platform_icon?: string;
  trailer_url?: string;
  synopsis?: string;
  cast: string[];
  cast_details?: { name: string; photo_url: string }[];
  director: string;
  why_watch: string;
  is_indian: boolean;
  ticket_url?: string;
  watch_url?: string;
  language: string;
  trending?: boolean;
}

/* ── Constants ── */

const STATUS_CONFIG: Record<string, { label: string; bg: string }> = {
  now_playing: { label: "Now Playing", bg: "#16a34a" },
  opening: { label: "Opening This Week", bg: "#d97706" },
  coming_soon: { label: "Coming Soon", bg: "#64748b" },
};

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

/* ── Helpers ── */

function extractYouTubeId(url: string): string | null {
  const m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([A-Za-z0-9_-]{11})/);
  return m ? m[1] : null;
}

function formatRelease(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}

function theaterToUnified(m: TheaterMovie): UnifiedMovie {
  return {
    source: "theater",
    title: m.title,
    slug: m.slug,
    genre: m.genre,
    year: m.year,
    poster_url: m.poster_url,
    rating: m.rating,
    rating_source: m.rating_source,
    release_date: m.release_date,
    status: m.status,
    cast: m.cast,
    cast_details: m.cast_details,
    director: m.director,
    why_watch: m.why_watch,
    is_indian: m.is_indian,
    ticket_url: m.ticket_url,
    language: m.language,
    trailer_url: m.trailer_url,
  };
}

function streamingToUnified(p: StreamingPick): UnifiedMovie {
  return {
    source: "streaming",
    title: p.title,
    slug: p.slug,
    genre: p.genre,
    year: p.year,
    poster_url: p.poster_url,
    backdrop_url: p.backdrop_url,
    trailer_url: p.trailer_url,
    synopsis: p.synopsis,
    platform: p.platform,
    platform_icon: p.platform_icon,
    cast: p.cast,
    cast_details: p.cast_details,
    director: p.director,
    why_watch: p.why_watch,
    is_indian: p.is_indian,
    watch_url: p.watch_url,
    language: p.language,
    trending: p.trending,
  };
}

/* ── Related card ── */

/* ── Cast card with photo ── */

function CastCard({ name, photoUrl }: { name: string; photoUrl: string }) {
  const [imgErr, setImgErr] = useState(false);
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div style={{ flexShrink: 0, textAlign: "center", width: 80 }}>
      {photoUrl && !imgErr ? (
        <img
          src={photoUrl}
          alt={name}
          loading="lazy"
          onError={() => setImgErr(true)}
          style={{
            width: 72,
            height: 72,
            borderRadius: "50%",
            objectFit: "cover",
            margin: "0 auto",
            display: "block",
            border: "2px solid rgba(255,255,255,0.08)",
          }}
        />
      ) : (
        <div
          style={{
            width: 72,
            height: 72,
            borderRadius: "50%",
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "linear-gradient(135deg, #333, #222)",
            border: "2px solid rgba(255,255,255,0.08)",
            color: "#888",
            fontSize: 18,
            fontWeight: 700,
            letterSpacing: "0.05em",
          }}
        >
          {initials}
        </div>
      )}
      <div
        style={{
          marginTop: 6,
          fontSize: 11,
          fontWeight: 500,
          lineHeight: 1.3,
          color: "hsl(var(--foreground))",
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {name}
      </div>
    </div>
  );
}

function RelatedCard({ movie }: { movie: UnifiedMovie }) {
  const [imgErr, setImgErr] = useState(false);
  const accentColor = movie.source === "streaming"
    ? getPlatformColor(movie.platform_icon || movie.platform?.toLowerCase() || "")
    : "#AD1457";

  return (
    <Link
      to={`/movies/${movie.slug}`}
      style={{ textDecoration: "none", color: "inherit", flexShrink: 0 }}
    >
      <div
        style={{
          width: 120,
          height: 180,
          borderRadius: 8,
          overflow: "hidden",
          background: "#1a1a1a",
        }}
      >
        {movie.poster_url && !imgErr ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
            loading="lazy"
            onError={() => setImgErr(true)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background: `linear-gradient(135deg, ${accentColor}22, #1a1a2e)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 8,
            }}
          >
            <span style={{ color: "#fff", fontSize: 11, fontWeight: 600, textAlign: "center" }}>
              {movie.title}
            </span>
          </div>
        )}
      </div>
      <div style={{ width: 120, marginTop: 4 }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            lineHeight: 1.3,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {movie.title}
        </div>
        <div style={{ fontSize: 9, color: "#999" }}>
          {movie.source === "streaming" ? movie.platform : movie.genre}
        </div>
      </div>
    </Link>
  );
}

/* ── Main page ── */

export default function MovieDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [movie, setMovie] = useState<UnifiedMovie | null>(null);
  const [related, setRelated] = useState<UnifiedMovie[]>([]);
  const [reviewArticle, setReviewArticle] = useState<ReviewArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        // Fetch both sources in parallel
        const [theaterRes, streamingRes] = await Promise.allSettled([
          fetch("/data/now-in-theaters.json").then((r) => r.ok ? r.json() : null),
          fetch("/data/streaming-picks.json").then((r) => r.ok ? r.json() : null),
        ]);

        if (cancelled) return;

        const theaterData = theaterRes.status === "fulfilled" ? theaterRes.value : null;
        const streamingData = streamingRes.status === "fulfilled" ? streamingRes.value : null;

        const theaterMovies: UnifiedMovie[] = (theaterData?.movies || []).map(theaterToUnified);
        const streamingMovies: UnifiedMovie[] = (streamingData?.picks || []).map(streamingToUnified);

        // Theater takes priority
        const found =
          theaterMovies.find((m) => m.slug === slug) ||
          streamingMovies.find((m) => m.slug === slug) ||
          null;

        setMovie(found);

        // Related: same source first, then other source
        if (found) {
          const sameSource = (found.source === "theater" ? theaterMovies : streamingMovies)
            .filter((m) => m.slug !== slug);
          const otherSource = (found.source === "theater" ? streamingMovies : theaterMovies)
            .filter((m) => m.slug !== slug);
          setRelated([...sameSource, ...otherSource].slice(0, 6));
        }
      } catch {
        // ignore
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [slug]);

  /* Reset image error on slug change */
  useEffect(() => { setImgError(false); }, [slug]);

  /* Fetch matching review article from Supabase */
  useEffect(() => {
    if (!movie?.title) return;
    let cancelled = false;

    async function fetchReview() {
      try {
        // Build search words from movie title
        const titleWords = movie!.title
          .toLowerCase()
          .replace(/[^a-z0-9\s]/g, "")
          .split(/\s+/)
          .filter((w) => w.length >= 3 && !["the", "and", "for"].includes(w));

        // Search for review articles matching movie title
        const { data } = await (supabase as any)
          .from("p2_articles")
          .select("id, headline, slug, body, sources, published_at, data_cards")
          .eq("category", "entertainment")
          .eq("status", "published")
          .ilike("slug", `%review%`)
          .order("published_at", { ascending: false })
          .limit(10);

        if (cancelled || !data || data.length === 0) return;

        // Find the one whose slug contains enough title words
        const match = data.find((a: any) => {
          const s = (a.slug || "").toLowerCase();
          const h = (a.headline || "").toLowerCase();
          const matched = titleWords.filter((w) => s.includes(w) || h.includes(w));
          return matched.length >= 2;
        });

        if (match && !cancelled) {
          setReviewArticle(match as ReviewArticle);
        }
      } catch {
        // silent — review is supplementary
      }
    }

    fetchReview();
    return () => { cancelled = true; };
  }, [movie?.title]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="min-h-screen bg-background">
        <Masthead />
        <main className="container py-20 text-center">
          <p className="smallcaps text-primary">404</p>
          <h1 className="font-serif text-3xl mt-3">Movie not found</h1>
          <Link to="/" className="text-primary mt-6 inline-block hover:underline">
            ← Back to homepage
          </Link>
        </main>
        <SiteFooter lastUpdated={null} />
      </div>
    );
  }

  const isTheater = movie.source === "theater";
  const accentColor = isTheater
    ? "#AD1457"
    : getPlatformColor(movie.platform_icon || movie.platform?.toLowerCase() || "");
  const statusCfg = movie.status ? STATUS_CONFIG[movie.status] : null;
  const youtubeId = movie.trailer_url ? extractYouTubeId(movie.trailer_url) : null;
  const isYouTubeSearch = movie.trailer_url?.includes("youtube.com/results");
  const heroImage = movie.backdrop_url || movie.poster_url;
  const isPortraitHero = !movie.backdrop_url && !!movie.poster_url;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Helmet>
        <title>{movie.title} — {isTheater ? "Now in Theaters" : "What to Watch"} | The Videshi</title>
        <meta name="description" content={movie.why_watch || `${movie.title} — ${movie.genre}`} />
        {movie.poster_url && <meta property="og:image" content={movie.poster_url} />}
        <meta property="og:title" content={`${movie.title} | The Videshi`} />
        <link rel="canonical" href={`https://www.thevideshi.com/movies/${slug}`} />
      </Helmet>

      <Masthead />

      <main style={{ maxWidth: 720, margin: "0 auto", padding: "0 16px", flex: 1, width: "100%" }}>
        {/* Back link */}
        <div style={{ padding: "16px 0 8px" }}>
          <button
            onClick={() => {
              if (window.history.length > 1) navigate(-1);
              else navigate("/");
            }}
            style={{
              color: "#888",
              fontSize: 12,
              textDecoration: "none",
              letterSpacing: "0.06em",
              textTransform: "uppercase" as const,
              fontWeight: 600,
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: 0,
            }}
          >
            ← Back
          </button>
        </div>

        {/* ── Hero section ── */}
        <div
          style={{
            position: "relative",
            borderRadius: 14,
            overflow: "hidden",
            background: "#111",
            marginBottom: 24,
          }}
        >
          {heroImage && !imgError ? (
            <div style={{ position: "relative" }}>
              <img
                src={heroImage}
                alt={movie.title}
                onError={() => setImgError(true)}
                style={{
                  width: "100%",
                  maxHeight: isPortraitHero ? 420 : 360,
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
              <div style={{ position: "absolute", bottom: 16, left: 16, right: 16 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8, flexWrap: "wrap" }}>
                  {/* Source badges */}
                  {isTheater && statusCfg && (
                    <span
                      style={{
                        background: statusCfg.bg,
                        color: "#fff",
                        fontSize: 10,
                        fontWeight: 700,
                        padding: "3px 8px",
                        borderRadius: 4,
                        letterSpacing: "0.04em",
                        textTransform: "uppercase" as const,
                      }}
                    >
                      {statusCfg.label}
                    </span>
                  )}
                  {!isTheater && movie.platform && (
                    <span
                      style={{
                        background: accentColor,
                        color: "#fff",
                        fontSize: 10,
                        fontWeight: 700,
                        padding: "3px 8px",
                        borderRadius: 4,
                      }}
                    >
                      {movie.platform}
                    </span>
                  )}
                  {movie.trending && (
                    <span
                      style={{
                        background: "linear-gradient(135deg, #ff6b35, #e50914)",
                        color: "#fff",
                        fontSize: 10,
                        fontWeight: 700,
                        padding: "3px 8px",
                        borderRadius: 4,
                        letterSpacing: "0.04em",
                        textTransform: "uppercase" as const,
                      }}
                    >
                      🔥 Trending
                    </span>
                  )}
                  <span style={{ color: "rgba(255,255,255,0.7)", fontSize: 12 }}>{movie.genre}</span>
                  {movie.year > 0 && (
                    <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 12 }}>{movie.year}</span>
                  )}
                  {movie.language && movie.language !== "English" && (
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
                      {movie.language}
                    </span>
                  )}
                  {movie.is_indian && (
                    <span
                      style={{
                        background: "linear-gradient(135deg, #ff9933, #138808)",
                        color: "#fff",
                        fontSize: 9,
                        fontWeight: 700,
                        padding: "2px 6px",
                        borderRadius: 4,
                        letterSpacing: "0.04em",
                        textTransform: "uppercase" as const,
                      }}
                    >
                      🇮🇳 Desi
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
                  {movie.title}
                </h1>
              </div>
            </div>
          ) : (
            /* No-image fallback hero */
            <div
              style={{
                padding: "40px 20px 24px",
                background: `linear-gradient(135deg, ${accentColor}33 0%, #1a1a2e 50%, #0f3460 100%)`,
              }}
            >
              <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, flexWrap: "wrap" }}>
                {isTheater && statusCfg && (
                  <span
                    style={{
                      background: statusCfg.bg,
                      color: "#fff",
                      fontSize: 10,
                      fontWeight: 700,
                      padding: "3px 8px",
                      borderRadius: 4,
                      letterSpacing: "0.04em",
                      textTransform: "uppercase" as const,
                    }}
                  >
                    {statusCfg.label}
                  </span>
                )}
                {!isTheater && movie.platform && (
                  <span
                    style={{
                      background: accentColor,
                      color: "#fff",
                      fontSize: 10,
                      fontWeight: 700,
                      padding: "3px 8px",
                      borderRadius: 4,
                    }}
                  >
                    {movie.platform}
                  </span>
                )}
                <span style={{ color: "rgba(255,255,255,0.7)", fontSize: 12 }}>{movie.genre}</span>
                {movie.year > 0 && (
                  <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 12 }}>{movie.year}</span>
                )}
                {movie.language && movie.language !== "English" && (
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
                    {movie.language}
                  </span>
                )}
                {movie.is_indian && (
                  <span
                    style={{
                      background: "linear-gradient(135deg, #ff9933, #138808)",
                      color: "#fff",
                      fontSize: 9,
                      fontWeight: 700,
                      padding: "2px 6px",
                      borderRadius: 4,
                    }}
                  >
                    🇮🇳 Desi
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
                {movie.title}
              </h1>
            </div>
          )}
        </div>

        {/* ── Quick info bar ── */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            alignItems: "center",
            marginBottom: 20,
            paddingBottom: 16,
            borderBottom: "1px solid hsl(var(--rule))",
          }}
        >
          {movie.rating && (
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <span style={{ color: "#fbbf24", fontSize: 16 }}>★</span>
              <span style={{ fontSize: 15, fontWeight: 700 }}>{movie.rating}</span>
              {movie.rating_source && (
                <span style={{ fontSize: 11, color: "#999" }}>{movie.rating_source}</span>
              )}
            </div>
          )}
          {movie.release_date && (
            <span style={{ fontSize: 13, color: "#666" }}>
              {formatRelease(movie.release_date)}
            </span>
          )}
          {movie.director && (
            <span style={{ fontSize: 13, color: "#666" }}>
              Dir. {movie.director}
            </span>
          )}
        </div>

        {/* ── Why Watch — editorial callout ── */}
        {movie.why_watch && (
          <div
            style={{
              borderLeft: `3px solid ${accentColor}`,
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
              {movie.why_watch}
            </p>
          </div>
        )}

        {/* ── Trailer ── */}
        {movie.trailer_url && (
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
              Trailer
            </h2>
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
                  title={`${movie.title} trailer`}
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
                href={movie.trailer_url}
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

        {/* ── Synopsis (streaming) ── */}
        {movie.synopsis && (
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
              {movie.synopsis}
            </p>
          </div>
        )}

        {/* ── Cast & Director ── */}
        {(movie.cast.length > 0 || movie.director) && (
          <div style={{ marginBottom: 24 }}>
            {movie.director && (
              <div style={{ marginBottom: 16 }}>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#888",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase" as const,
                  }}
                >
                  Director
                </span>
                <p style={{ margin: "4px 0 0", fontSize: 15 }}>{movie.director}</p>
              </div>
            )}
            {movie.cast.length > 0 && (
              <div>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#888",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase" as const,
                    display: "block",
                    marginBottom: 12,
                  }}
                >
                  Cast
                </span>
                {movie.cast_details && movie.cast_details.length > 0 ? (
                  <div
                    style={{
                      display: "flex",
                      gap: 16,
                      overflowX: "auto",
                      paddingBottom: 8,
                      WebkitOverflowScrolling: "touch",
                      scrollbarWidth: "none",
                    }}
                  >
                    {movie.cast_details.map((actor) => (
                      <CastCard key={actor.name} name={actor.name} photoUrl={actor.photo_url} />
                    ))}
                  </div>
                ) : (
                  <p style={{ margin: "4px 0 0", fontSize: 15 }}>{movie.cast.join(", ")}</p>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── CTA Button ── */}
        <div style={{ marginBottom: 32 }}>
          {isTheater && movie.ticket_url && (
            <a
              href={movie.ticket_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                background: "#d97706",
                color: "#fff",
                fontSize: 14,
                fontWeight: 700,
                padding: "12px 24px",
                borderRadius: 8,
                textDecoration: "none",
                transition: "opacity 0.2s",
              }}
            >
              🎟️ Find Showtimes
            </a>
          )}
          {!isTheater && movie.watch_url && (
            <a
              href={movie.watch_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                background: accentColor,
                color: "#fff",
                fontSize: 14,
                fontWeight: 700,
                padding: "12px 24px",
                borderRadius: 8,
                textDecoration: "none",
                transition: "opacity 0.2s",
              }}
            >
              ▶ Watch on {movie.platform}
            </a>
          )}
        </div>

        {/* ── Critics Review Section ── */}
        {reviewArticle && (
          <div
            style={{
              marginBottom: 32,
              paddingTop: 20,
              borderTop: "1px solid hsl(var(--rule))",
            }}
          >
            <h2
              style={{
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: "0.12em",
                textTransform: "uppercase" as const,
                color: "#888",
                marginBottom: 14,
              }}
            >
              What Critics Are Saying
            </h2>
            {/* ── Ratings Scorecard ── */}
            {(() => {
              const ratingsCard = reviewArticle.data_cards?.find(
                (c: any) => c.type === "movie_review_ratings"
              ) as ReviewRatings | undefined;
              if (!ratingsCard) return null;

              const categoryLabels: Record<string, string> = {
                acting: "Acting",
                direction: "Direction",
                story: "Story",
                music: "Music",
                visuals: "Visuals",
              };

              const renderStars = (rating: number, size = 16) => {
                const stars = [];
                for (let i = 1; i <= 5; i++) {
                  if (rating >= i) {
                    stars.push(<span key={i} style={{ color: "#D4A843", fontSize: size }}>★</span>);
                  } else if (rating >= i - 0.5) {
                    stars.push(
                      <span key={i} style={{ position: "relative", display: "inline-block", fontSize: size }}>
                        <span style={{ color: "#ddd" }}>★</span>
                        <span style={{
                          position: "absolute", left: 0, top: 0,
                          overflow: "hidden", width: "50%", color: "#D4A843",
                        }}>★</span>
                      </span>
                    );
                  } else {
                    stars.push(<span key={i} style={{ color: "#ddd", fontSize: size }}>★</span>);
                  }
                }
                return stars;
              };

              return (
                <div
                  style={{
                    marginBottom: 24,
                    padding: "20px 20px 16px",
                    background: "hsl(var(--muted) / 0.3)",
                    borderRadius: 12,
                    border: "1px solid hsl(var(--rule))",
                  }}
                >
                  {/* Overall rating */}
                  <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                    <span style={{
                      fontSize: 36, fontWeight: 800, color: "#D4A843",
                      fontFamily: "var(--font-serif, 'Playfair Display', serif)",
                      lineHeight: 1,
                    }}>
                      {ratingsCard.star_rating}
                    </span>
                    <div>
                      <div style={{ display: "flex", gap: 2 }}>
                        {renderStars(ratingsCard.star_rating, 20)}
                      </div>
                      <span style={{ fontSize: 11, color: "#888", fontWeight: 600, letterSpacing: "0.05em" }}>
                        THE VIDESHI RATING
                      </span>
                    </div>
                  </div>
                  {/* Category ratings */}
                  {ratingsCard.category_ratings && Object.keys(ratingsCard.category_ratings).length > 0 && (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px 20px" }}>
                      {Object.entries(ratingsCard.category_ratings).map(([cat, rating]) => (
                        <div key={cat} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                          <span style={{ fontSize: 12, color: "#666", fontWeight: 600 }}>
                            {categoryLabels[cat] || cat}
                          </span>
                          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                            <div style={{ display: "flex", gap: 1 }}>{renderStars(rating, 12)}</div>
                            <span style={{ fontSize: 11, color: "#999", fontWeight: 600, minWidth: 20, textAlign: "right" }}>
                              {rating}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {/* Consensus line */}
                  {ratingsCard.rating_consensus && (
                    <div style={{
                      marginTop: 12, paddingTop: 10,
                      borderTop: "1px solid hsl(var(--rule) / 0.5)",
                      fontSize: 12, color: "#888", fontStyle: "italic",
                    }}>
                      {ratingsCard.rating_consensus}
                    </div>
                  )}
                </div>
              );
            })()}
            <div
              className="article-body review-body"
              style={{
                fontFamily: "var(--font-serif, 'Source Serif 4', serif)",
                fontSize: 16,
                lineHeight: 1.7,
                color: "hsl(var(--foreground))",
              }}
              dangerouslySetInnerHTML={{ __html: reviewArticle.body }}
            />
            {reviewArticle.sources && reviewArticle.sources.length > 0 && (
              <div style={{ marginTop: 16, paddingTop: 12, borderTop: "1px solid hsl(var(--rule) / 0.5)" }}>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    letterSpacing: "0.1em",
                    textTransform: "uppercase" as const,
                    color: "#999",
                  }}
                >
                  Sources
                </span>
                <div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {reviewArticle.sources.map((src, i) => {
                    let domain = "";
                    try { domain = new URL(src).hostname.replace("www.", ""); } catch { domain = src; }
                    return (
                      <a
                        key={i}
                        href={src}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: 12,
                          color: "#666",
                          textDecoration: "none",
                          padding: "3px 8px",
                          border: "1px solid hsl(var(--rule))",
                          borderRadius: 4,
                        }}
                      >
                        {domain}
                      </a>
                    );
                  })}
                </div>
              </div>
            )}
            <Link
              to={`/article/${reviewArticle.slug}`}
              style={{
                display: "inline-block",
                marginTop: 14,
                fontSize: 13,
                fontWeight: 600,
                color: "#D4A843",
                textDecoration: "none",
              }}
            >
              Read full review roundup →
            </Link>
          </div>
        )}

        {/* ── More to Watch ── */}
        {related.length > 0 && (
          <div
            style={{
              marginBottom: 40,
              paddingTop: 20,
              borderTop: "1px solid hsl(var(--rule))",
            }}
          >
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
              More to Watch
            </h3>
            <div
              style={{
                display: "flex",
                gap: 14,
                overflowX: "auto",
                paddingBottom: 8,
                WebkitOverflowScrolling: "touch",
                scrollbarWidth: "none",
              }}
            >
              {related.map((rm) => (
                <RelatedCard key={rm.slug} movie={rm} />
              ))}
            </div>
          </div>
        )}
      </main>

      <SiteFooter lastUpdated={null} />
    </div>
  );
}
