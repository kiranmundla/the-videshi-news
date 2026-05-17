import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";

/* ── helpers ────────────────────────────────────────── */

function parseImageDimensions(url: string | null | undefined): { w: number; h: number } | null {
  if (!url) return null;
  try {
    const params = new URL(url).searchParams;
    const w = parseInt(params.get("w") || "");
    const h = parseInt(params.get("h") || "");
    if (w > 0 && h > 0) return { w, h };
  } catch {}
  return null;
}

function getImageOrientation(url: string | null | undefined): "landscape" | "portrait" | null {
  const dims = parseImageDimensions(url);
  if (!dims) return null;
  return dims.w / dims.h > 1.2 ? "landscape" : "portrait";
}

const CATEGORY_COLORS: Record<string, string> = {
  news: "#C62828",
  "nri-world": "#1565C0",
  entertainment: "#AD1457",
  sports: "#2E7D32",
  technology: "#4527A0",
  "markets-finance": "#E65100",
  "lifestyle-health": "#00838F",
  food: "#BF360C",
};

function categoryColor(cat: string): string {
  return CATEGORY_COLORS[cat] || "hsl(var(--primary))";
}

function categoryLabel(cat: string): string {
  return (cat || "news").replace(/-/g, " ").toUpperCase();
}

/* ── Slide (single article) ─────────────────────────── */

function Slide({ article, active }: { article: Article; active: boolean }) {
  const href = `/articles/${article.slug}`;
  const url = article.hero_image_url || "";
  const isFlag = /flag/i.test(url);
  const hasImage = isValidImage(url) && !isFlag;
  const orient = hasImage ? getImageOrientation(article.hero_image_url) : null;

  const pill = (
    <span
      className="inline-block px-2.5 py-0.5 text-[10px] font-bold tracking-[0.14em] uppercase rounded-sm mr-2"
      style={{ background: categoryColor(article.category), color: "#fff" }}
    >
      {categoryLabel(article.category)}
    </span>
  );

  // Portrait layout
  if (hasImage && orient === "portrait") {
    return (
      <div
        className="absolute inset-0 flex items-center gap-6 px-5 md:px-12 py-6 md:py-8 transition-opacity duration-500 ease-in-out"
        style={{ opacity: active ? 1 : 0, pointerEvents: active ? "auto" : "none", background: "#1C1C1E" }}
      >
        <div className="flex-1">
          <Link to={href} className="block max-w-2xl">
            <p className="smallcaps text-white/90 mb-2">{pill}</p>
            <h1
              className="font-display text-white leading-[1.1] hover:underline"
              style={{ fontWeight: 800, fontSize: "clamp(22px, 3.6vw, 32px)" }}
            >
              {article.title}
            </h1>
            {article.excerpt && (
              <p className="font-body-serif text-white/85 mt-2 text-sm md:text-base max-w-xl line-clamp-2">
                {article.excerpt}
              </p>
            )}
          </Link>
        </div>
        <div className="hidden md:block w-[180px] lg:w-[220px] flex-shrink-0">
          <img
            src={article.hero_image_url}
            alt={article.title}
            loading="eager"
            referrerPolicy="no-referrer"
            className="w-full h-auto rounded object-cover"
          />
        </div>
      </div>
    );
  }

  // Landscape layout — full bleed image
  if (hasImage) {
    return (
      <div
        className="absolute inset-0 transition-opacity duration-500 ease-in-out"
        style={{ opacity: active ? 1 : 0, pointerEvents: active ? "auto" : "none" }}
      >
        <img
          src={article.hero_image_url}
          alt={article.title}
          loading="eager"
          referrerPolicy="no-referrer"
          className="w-full h-full object-cover"
          style={{ objectPosition: "center 20%" }}
        />
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.45) 50%, rgba(0,0,0,0.05) 100%)",
          }}
        />
        <div className="absolute inset-x-0 bottom-0 px-5 md:px-12 pb-6 md:pb-8">
          <Link to={href} className="block max-w-4xl">
            <p className="smallcaps text-white/90 mb-2">{pill}</p>
            <h1
              className="font-display text-white leading-[1.1] hover:underline"
              style={{ fontWeight: 800, fontSize: "clamp(22px, 3.6vw, 32px)" }}
            >
              {article.title}
            </h1>
            {article.excerpt && (
              <p className="font-body-serif text-white/85 mt-2 text-sm md:text-base max-w-3xl line-clamp-2">
                {article.excerpt}
              </p>
            )}
          </Link>
        </div>
      </div>
    );
  }

  // No-image layout
  return (
    <div
      className="absolute inset-0 flex items-center px-6 md:px-10 transition-opacity duration-500 ease-in-out"
      style={{ opacity: active ? 1 : 0, pointerEvents: active ? "auto" : "none", background: "#1C1C1E" }}
    >
      <Link to={href} className="block max-w-4xl">
        <p className="smallcaps mb-3">{pill}</p>
        <h1
          className="font-display text-white leading-[1.1] hover:opacity-90"
          style={{ fontWeight: 800, fontSize: "clamp(22px, 3.6vw, 32px)" }}
        >
          {article.title}
        </h1>
        {article.excerpt && (
          <p className="font-body-serif text-white/80 mt-3 text-sm md:text-base max-w-3xl line-clamp-2">
            {article.excerpt}
          </p>
        )}
      </Link>
    </div>
  );
}

/* ── Carousel ───────────────────────────────────────── */

const AUTO_INTERVAL = 5000; // ms

export default function FeaturedCarousel({ articles }: { articles: Article[] }) {
  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);
  const touchStartX = useRef(0);
  const count = articles.length;

  const next = useCallback(() => setCurrent((i) => (i + 1) % count), [count]);
  const prev = useCallback(() => setCurrent((i) => (i - 1 + count) % count), [count]);
  const goTo = useCallback((i: number) => setCurrent(i), []);

  // Auto-advance
  useEffect(() => {
    if (paused || count <= 1) return;
    const id = setInterval(next, AUTO_INTERVAL);
    return () => clearInterval(id);
  }, [paused, count, next]);

  if (count === 0) return null;

  return (
    <section
      className="relative w-full overflow-hidden rounded-lg select-none"
      style={{ minHeight: "260px", maxHeight: "500px", height: "clamp(260px, 40vw, 500px)" }}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onTouchStart={(e) => {
        setPaused(true);
        touchStartX.current = e.touches[0].clientX;
      }}
      onTouchEnd={(e) => {
        const diff = e.changedTouches[0].clientX - touchStartX.current;
        if (Math.abs(diff) > 50) {
          diff < 0 ? next() : prev();
        }
        // Resume after a brief pause so the new slide is visible
        setTimeout(() => setPaused(false), AUTO_INTERVAL);
      }}
    >
      {/* Slides */}
      {articles.map((article, i) => (
        <Slide key={article.id} article={article} active={i === current} />
      ))}

      {/* Dot indicators */}
      {count > 1 && (
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-2 z-10">
          {articles.map((_, i) => (
            <button
              key={i}
              onClick={() => goTo(i)}
              aria-label={`Go to slide ${i + 1}`}
              className="w-2 h-2 rounded-full border-none cursor-pointer transition-all duration-300"
              style={{
                background: i === current ? "#fff" : "rgba(255,255,255,0.35)",
                transform: i === current ? "scale(1.3)" : "scale(1)",
              }}
            />
          ))}
        </div>
      )}

      {/* Arrow buttons (desktop) */}
      {count > 1 && (
        <>
          <button
            onClick={(e) => { e.stopPropagation(); prev(); }}
            className="absolute left-3 top-1/2 -translate-y-1/2 bg-black/30 hover:bg-black/50 border-none text-white text-xl w-9 h-9 rounded-full cursor-pointer z-10 hidden md:flex items-center justify-center transition-colors"
            aria-label="Previous slide"
          >
            ‹
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); next(); }}
            className="absolute right-3 top-1/2 -translate-y-1/2 bg-black/30 hover:bg-black/50 border-none text-white text-xl w-9 h-9 rounded-full cursor-pointer z-10 hidden md:flex items-center justify-center transition-colors"
            aria-label="Next slide"
          >
            ›
          </button>
        </>
      )}
    </section>
  );
}
