import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Article } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";
import ScrollWrap from "./ScrollWrap";
import StreamingPicks from "@/components/StreamingPicks";

/* ── types ────────────────────────────────────────── */

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
  is_indian: boolean;
  language: string;
}

/* ── constants ────────────────────────────────────── */

const GOLD = "#D4A843";
const ENTERTAINMENT_ACCENT = "#AD1457";

/* ── helpers ──────────────────────────────────────── */

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

/* ── Box Office poster card ──────────────────────── */

function PosterCard({ movie, onClick }: { movie: TheaterMovie; onClick: () => void }) {
  const [imgErr, setImgErr] = useState(false);

  return (
    <div
      onClick={onClick}
      className="flex-shrink-0 cursor-pointer group"
      style={{ width: 112, scrollSnapAlign: "start" }}
    >
      {/* Poster */}
      <div
        className="relative overflow-hidden rounded-lg"
        style={{
          width: 112,
          aspectRatio: "2/3",
          background: "#1a1a2e",
          boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
        }}
      >
        {movie.poster_url && !imgErr ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
            loading="lazy"
            onError={() => setImgErr(true)}
            className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center px-2 text-center"
            style={{ background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)" }}
          >
            <span style={{ fontSize: 22 }}>🎬</span>
            <span className="text-white text-[10px] font-semibold mt-1 line-clamp-2">{movie.title}</span>
          </div>
        )}

        {/* Indian badge */}
        {movie.is_indian && (
          <div
            className="absolute top-1.5 right-1.5 text-[8px] font-bold px-1.5 py-0.5 rounded-sm text-white"
            style={{ background: "linear-gradient(135deg, #ff9933, #138808)" }}
          >
            🇮🇳
          </div>
        )}

        {/* Status strip */}
        <div
          className="absolute bottom-0 left-0 right-0 px-1.5 py-1"
          style={{ background: "linear-gradient(transparent, rgba(0,0,0,0.85))" }}
        >
          <span
            className="text-[8px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-sm"
            style={{
              background: movie.status === "now_playing" ? "#16a34a" : movie.status === "opening" ? "#d97706" : "#64748b",
              color: "#fff",
            }}
          >
            {movie.status === "now_playing" ? "Now Showing" : movie.status === "opening" ? "Opening" : "Coming Soon"}
          </span>
        </div>
      </div>

      {/* Title below */}
      <p
        className="text-[11px] font-semibold leading-snug mt-1.5 text-foreground group-hover:text-primary transition-colors line-clamp-2"
      >
        {movie.title}
      </p>
      <p className="text-[9px] text-foreground/40 mt-0.5">{movie.genre}</p>
    </div>
  );
}

/* ── Entertainment article card ──────────────────── */

function EntArticleCard({
  article,
  featured = false,
}: {
  article: Article;
  featured?: boolean;
}) {
  const href = `/articles/${article.slug ?? article.id}`;
  const hasImage = isValidImage(article.hero_image_url);

  if (featured) {
    return (
      <Link to={href} className="group block">
        {hasImage && (
          <div
            className="w-full overflow-hidden rounded-lg mb-3"
            style={{ aspectRatio: "16/9", background: "#f5f1eb" }}
          >
            <img
              src={article.hero_image_url}
              alt={article.title}
              loading="lazy"
              className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
              style={{ objectPosition: `center ${(article.focal_y ?? 0.3) * 100}%` }}
            />
          </div>
        )}
        <h3
          className="font-serif font-bold text-foreground text-[1.15rem] md:text-[1.3rem] leading-snug group-hover:text-primary transition-colors"
        >
          {article.title}
        </h3>
        {article.excerpt && (
          <p className="text-foreground/55 text-sm mt-1.5 line-clamp-2">{article.excerpt}</p>
        )}
        <p className="text-foreground/40 text-xs mt-2">{timeAgo(article.published_at)}</p>
      </Link>
    );
  }

  return (
    <Link to={href} className="group block">
      {hasImage && (
        <div
          className="w-full overflow-hidden rounded-lg mb-2"
          style={{ aspectRatio: "16/9", background: "#f5f1eb" }}
        >
          <img
            src={article.hero_image_url}
            alt={article.title}
            loading="lazy"
            className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
            style={{ objectPosition: `center ${(article.focal_y ?? 0.3) * 100}%` }}
          />
        </div>
      )}
      <h3
        className="font-serif font-semibold text-foreground text-[0.95rem] leading-snug group-hover:text-primary transition-colors line-clamp-3"
      >
        {article.title}
      </h3>
      <p className="text-foreground/40 text-xs mt-1.5">{timeAgo(article.published_at)}</p>
    </Link>
  );
}

/* ── Main component ──────────────────────────────── */

export default function EntertainmentSection({ pool }: { pool: Article[] }) {
  const [movies, setMovies] = useState<TheaterMovie[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/data/now-in-theaters.json")
      .then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then((d) => {
        if (d?.movies?.length) setMovies(d.movies);
      })
      .catch(() => {});
  }, []);

  const articles = pool.slice(0, 5);
  const [lead, ...rest] = articles;

  if (!lead) return null;

  return (
    <section>
      {/* Section header */}
      <div
        className="flex items-center justify-between mt-14 mb-6 gap-4 pb-3 scroll-mt-24"
        id="section-entertainment"
        style={{ borderBottom: `2px solid ${ENTERTAINMENT_ACCENT}` }}
      >
        <span
          className="font-bold uppercase"
          style={{ fontSize: 11, letterSpacing: "0.12em", color: ENTERTAINMENT_ACCENT }}
        >
          ENTERTAINMENT
        </span>
      </div>

      {/* Box Office — horizontal poster strip */}
      {movies.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[10px] font-bold uppercase tracking-[0.12em] text-foreground/50">
              🍿 In Theaters
            </span>
          </div>
          <ScrollWrap className="pl-1 gap-3">
            {movies.map((m) => (
              <PosterCard
                key={m.slug}
                movie={m}
                onClick={() => navigate(`/movies/${m.slug}`)}
              />
            ))}
          </ScrollWrap>
        </div>
      )}

      {/* Article grid: lead + 3 supporting */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
        {/* Lead — full width mobile, left half desktop */}
        <div>
          <EntArticleCard article={lead} featured />
        </div>

        {/* Right column: 3 smaller cards */}
        {rest.length > 0 && (
          <div className="grid grid-cols-1 gap-6">
            {rest.slice(0, 3).map((a) => (
              <Link
                key={a.id}
                to={`/articles/${a.slug ?? a.id}`}
                className="group flex items-start gap-3"
                style={{ borderBottom: "1px solid hsl(var(--rule) / 0.3)" }}
              >
                {isValidImage(a.hero_image_url) && (
                  <img
                    src={a.hero_image_url}
                    alt={a.title}
                    loading="lazy"
                    className="w-[100px] h-[68px] md:w-[120px] md:h-[80px] object-cover rounded flex-shrink-0 group-hover:opacity-90 transition-opacity"
                    style={{ objectPosition: `center ${(a.focal_y ?? 0.3) * 100}%` }}
                  />
                )}
                <div className="flex-1 min-w-0 py-1">
                  <h3 className="font-serif font-semibold text-foreground text-[0.9rem] leading-snug group-hover:text-primary transition-colors line-clamp-3">
                    {a.title}
                  </h3>
                  <p className="text-foreground/40 text-xs mt-1.5">{timeAgo(a.published_at)}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Streaming Picks */}
      <div className="mt-6">
        <StreamingPicks />
      </div>
    </section>
  );
}
