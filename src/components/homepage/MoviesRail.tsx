import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

/* ── Movies rail (unified) ──────────────────────────────────────
   Fed by /data/movies.json — merges now-in-theaters, our critic
   reviews, and box office figures into one horizontal scroll.
   Each card shows poster, title, our star rating (if reviewed),
   and box office numbers (if available). Tapping goes to the
   review article if one exists, otherwise the movie detail page.
   Renders nothing when empty. */

interface Movie {
  title: string;
  slug: string | null;
  poster_url: string | null;
  language: string | null;
  genre: string | null;
  director: string | null;
  release_date: string | null;
  is_indian: boolean;
  status: string;
  ticket_url: string | null;
  review_slug: string | null;
  star_rating: number | null;
  india_net_crore: number | null;
  worldwide_gross_crore: number | null;
  verdict: string | null;
}

interface MoviesData {
  week_of?: string;
  count: number;
  movies: Movie[];
}

function fmtCr(n: number | null): string | null {
  if (n === null || n === undefined) return null;
  return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 1 })} cr`;
}

function Stars({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-0.5" aria-label={`${rating} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((i) => {
        const fill = rating >= i ? "#D4A843" : rating >= i - 0.5 ? "url(#half)" : "#ddd";
        return (
          <svg key={i} width="11" height="11" viewBox="0 0 24 24">
            <defs>
              <linearGradient id="half">
                <stop offset="50%" stopColor="#D4A843" />
                <stop offset="50%" stopColor="#ddd" />
              </linearGradient>
            </defs>
            <path
              d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7-6.2-3.7-6.2 3.7 1.6-7L2 9.2l7.1-.6z"
              fill={fill}
            />
          </svg>
        );
      })}
      <span className="ml-1 text-[11px] font-bold" style={{ color: "#0B1D3A" }}>
        {rating.toFixed(1)}
      </span>
    </span>
  );
}

function MovieCard({ movie }: { movie: Movie }) {
  const navigate = useNavigate();
  const [imgError, setImgError] = useState(false);

  const go = () => {
    if (movie.review_slug) navigate(`/articles/${movie.review_slug}`);
    else if (movie.slug) navigate(`/movies/${movie.slug}`);
  };

  const indiaNet = fmtCr(movie.india_net_crore);
  const worldwide = fmtCr(movie.worldwide_gross_crore);

  return (
    <div
      onClick={go}
      className="group shrink-0 w-40 md:w-44 cursor-pointer"
    >
      <div className="relative w-40 md:w-44 aspect-[2/3] rounded-lg overflow-hidden bg-muted">
        {movie.poster_url && !imgError ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
            loading="lazy"
            onError={() => setImgError(true)}
            className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
          />
        ) : (
          <div
            className="w-full h-full flex items-center justify-center p-3 text-center"
            style={{ background: "#0B1D3A" }}
          >
            <span className="font-serif font-bold text-lg" style={{ color: "#D4A843" }}>
              {movie.title}
            </span>
          </div>
        )}
        {/* Badges */}
        <div className="absolute top-2 left-2 flex gap-1">
          {movie.review_slug && (
            <span className="text-[10px] font-bold tracking-[1px] uppercase text-white bg-black/60 rounded px-2 py-0.5">
              Review
            </span>
          )}
          {movie.language && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-black/60 text-white">
              {movie.language}
            </span>
          )}
        </div>
        {movie.is_indian && (
          <span className="absolute top-2 right-2 text-[10px] font-bold px-1.5 py-0.5 rounded bg-green-600 text-white">
            🇮🇳
          </span>
        )}
      </div>
      <p className="mt-2 font-serif font-bold text-[0.95rem] leading-snug line-clamp-1 group-hover:text-primary transition-colors">
        {movie.title}
      </p>
      {/* Rating */}
      {movie.star_rating !== null && movie.star_rating !== undefined && (
        <div className="mt-1">
          <Stars rating={movie.star_rating} />
        </div>
      )}
      {/* Box office */}
      {(indiaNet || worldwide) && (
        <div className="mt-0.5 text-[11px] text-muted-foreground leading-tight">
          {indiaNet && (
            <p>
              India net: <span className="font-semibold text-foreground">{indiaNet}</span>
            </p>
          )}
          {worldwide && !indiaNet && (
            <p>
              Worldwide: <span className="font-semibold text-foreground">{worldwide}</span>
            </p>
          )}
        </div>
      )}
      {movie.genre && !movie.star_rating && !indiaNet && (
        <p className="text-[11px] text-muted-foreground mt-0.5 line-clamp-1">{movie.genre}</p>
      )}
    </div>
  );
}

export default function MoviesRail() {
  const [data, setData] = useState<MoviesData | null>(null);

  useEffect(() => {
    fetch("/data/movies.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (j && Array.isArray(j.movies) && j.movies.length > 0) setData(j);
      })
      .catch(() => {});
  }, []);

  if (!data) return null;

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
            🍿 Movies
          </h2>
          <span className="text-[11px] text-muted-foreground">
            {data.week_of || `${data.count} movies`}
          </span>
        </div>
        <div className="flex gap-5 overflow-x-auto pb-2 -mx-1 px-1">
          {data.movies.slice(0, 20).map((m, i) => (
            <MovieCard key={`${m.title}-${i}`} movie={m} />
          ))}
        </div>
      </div>
    </section>
  );
}
