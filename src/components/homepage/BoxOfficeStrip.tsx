import { useState, useEffect } from "react";

/* ── Box Office strip ─────────────────────────────────────────
   Fed by /data/boxoffice.json (compiled weekly by the Monday
   entertainment refresh from trade sources). Renders nothing
   when empty. Figures in ₹ crore. */

interface BoxOfficeSource {
  name: string;
  url: string;
}

interface BoxOfficeFilm {
  title: string;
  language: string;
  release_date: string;
  india_net_crore: number | null;
  worldwide_gross_crore: number | null;
  budget_crore: number | null;
  verdict: string | null;
  poster_url?: string | null;
  sources: BoxOfficeSource[];
}

interface BoxOfficeData {
  as_of: string;
  week_of?: string;
  films: BoxOfficeFilm[];
}

const VERDICT_STYLES: Record<string, { bg: string; fg: string }> = {
  "All-Time Blockbuster": { bg: "#D4A843", fg: "#0B1D3A" },
  Blockbuster: { bg: "#D4A843", fg: "#0B1D3A" },
  "Super Hit": { bg: "#1a7a3c", fg: "#ffffff" },
  Hit: { bg: "#1a7a3c", fg: "#ffffff" },
  Average: { bg: "#8a8a8a", fg: "#ffffff" },
  Flop: { bg: "#A32D2F", fg: "#ffffff" },
};

function fmt(n: number | null): string {
  if (n === null || n === undefined) return "—";
  return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 1 })} cr`;
}

function FilmCard({ film }: { film: BoxOfficeFilm }) {
  const [imgError, setImgError] = useState(false);
  const v = film.verdict ? VERDICT_STYLES[film.verdict] : null;

  return (
    <div className="shrink-0 w-52 md:w-60">
      <div className="relative w-52 md:w-60 aspect-[2/3] rounded-lg overflow-hidden bg-muted">
        {film.poster_url && !imgError ? (
          <img
            src={film.poster_url}
            alt={film.title}
            loading="lazy"
            onError={() => setImgError(true)}
            className="w-full h-full object-cover"
          />
        ) : (
          <div
            className="w-full h-full flex items-center justify-center p-4 text-center"
            style={{ background: "#0B1D3A" }}
          >
            <span className="font-serif font-bold text-lg" style={{ color: "#D4A843" }}>
              {film.title}
            </span>
          </div>
        )}
        {v && (
          <span
            className="absolute top-2 left-2 text-[11px] font-bold px-2 py-1 rounded"
            style={{ background: v.bg, color: v.fg }}
          >
            {film.verdict}
          </span>
        )}
        <span className="absolute top-2 right-2 text-[11px] font-semibold px-2 py-1 rounded bg-black/70 text-white">
          {film.language}
        </span>
      </div>
      <p className="mt-2 font-serif font-bold text-[0.95rem] leading-snug line-clamp-1">
        {film.title}
      </p>
      <div className="mt-1 text-[0.8rem] text-muted-foreground space-y-0.5">
        <p>
          India net: <span className="font-semibold text-foreground">{fmt(film.india_net_crore)}</span>
        </p>
        <p>
          Worldwide: <span className="font-semibold text-foreground">{fmt(film.worldwide_gross_crore)}</span>
        </p>
      </div>
    </div>
  );
}

export default function BoxOfficeStrip() {
  const [data, setData] = useState<BoxOfficeData | null>(null);

  useEffect(() => {
    fetch("/data/boxoffice.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (j && Array.isArray(j.films) && j.films.length > 0) setData(j);
      })
      .catch(() => {});
  }, []);

  if (!data) return null;

  const sourceNames = Array.from(
    new Set(data.films.flatMap((f) => (f.sources || []).map((s) => s.name)))
  );

  return (
    <section className="mb-14">
      <div className="container">
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #A32D2F" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            Box Office
          </h2>
          <span className="text-[11px] text-muted-foreground">
            Updated {data.as_of}
            {sourceNames.length > 0 && ` · Sources: ${sourceNames.join(", ")}`}
          </span>
        </div>
        <div className="flex gap-5 overflow-x-auto pb-2 -mx-1 px-1">
          {data.films.map((f) => (
            <FilmCard key={f.title} film={f} />
          ))}
        </div>
        <p className="mt-2 text-[11px] text-muted-foreground">
          Figures in ₹ crore. Verdicts follow trade convention (collections vs reported budget).
        </p>
      </div>
    </section>
  );
}
