import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";

/* ── helpers ────────────────────────────────────────── */

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

/* ── Slide (single article card) ────────────────────── */

function Slide({ article }: { article: Article }) {
  const href = `/articles/${article.slug}`;
  const url = article.hero_image_url || "";
  const isFlag = /flag/i.test(url);
  const hasImage = isValidImage(url) && !isFlag;

  const pill = (
    <span
      className="inline-block px-2.5 py-0.5 text-[10px] font-bold tracking-[0.14em] uppercase rounded-sm mr-2"
      style={{ background: categoryColor(article.category), color: "#fff" }}
    >
      {categoryLabel(article.category)}
    </span>
  );

  // Landscape / has image — full bleed
  if (hasImage) {
    return (
      <div className="relative w-full h-full">
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
              "linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 50%, rgba(0,0,0,0.15) 100%)",
          }}
        />
        <div className="absolute inset-x-0 bottom-0 px-5 md:px-12 pb-6 md:pb-8">
          <Link to={href} className="block max-w-4xl">
            <p className="smallcaps text-white/90 mb-2">{pill}</p>
            <h1
              className="font-display text-white leading-[1.1] hover:underline line-clamp-3"
              style={{ fontWeight: 800, fontSize: "clamp(16px, 3vw, 28px)", textShadow: "0 2px 8px rgba(0,0,0,0.7)" }}
            >
              {article.title}
            </h1>
          </Link>
        </div>
      </div>
    );
  }

  // No-image layout — dark background
  return (
    <div
      className="relative w-full h-full flex items-center px-6 md:px-10"
      style={{ background: "#1C1C1E" }}
    >
      <Link to={href} className="block max-w-4xl">
        <p className="smallcaps mb-3">{pill}</p>
        <h1
          className="font-display text-white leading-[1.1] hover:opacity-90 line-clamp-3"
          style={{ fontWeight: 800, fontSize: "clamp(16px, 3vw, 28px)", textShadow: "0 2px 8px rgba(0,0,0,0.7)" }}
        >
          {article.title}
        </h1>
      </Link>
    </div>
  );
}

/* ── Carousel ───────────────────────────────────────── */

const AUTO_INTERVAL = 5000;

export default function FeaturedCarousel({ articles }: { articles: Article[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);
  const userInteracted = useRef(false);
  const count = articles.length;

  /* ── scroll helpers ─── */
  const scrollTo = useCallback((index: number, smooth = true) => {
    const el = scrollRef.current;
    if (!el) return;
    const slideW = el.clientWidth;
    el.scrollTo({ left: slideW * index, behavior: smooth ? "smooth" : "auto" });
  }, []);

  const next = useCallback(() => {
    setCurrent((i) => {
      const n = (i + 1) % count;
      scrollTo(n);
      return n;
    });
  }, [count, scrollTo]);

  const prev = useCallback(() => {
    setCurrent((i) => {
      const n = (i - 1 + count) % count;
      scrollTo(n);
      return n;
    });
  }, [count, scrollTo]);

  /* ── track current slide from scroll position ─── */
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const slideW = el.clientWidth;
        if (slideW > 0) {
          const idx = Math.round(el.scrollLeft / slideW);
          setCurrent(Math.max(0, Math.min(idx, count - 1)));
        }
        ticking = false;
      });
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, [count]);

  /* ── auto-advance ─── */
  useEffect(() => {
    if (paused || count <= 1) return;
    const id = setInterval(() => {
      setCurrent((i) => {
        const n = (i + 1) % count;
        scrollTo(n);
        return n;
      });
    }, AUTO_INTERVAL);
    return () => clearInterval(id);
  }, [paused, count, scrollTo]);

  /* ── pause on user drag/swipe, resume after delay ─── */
  const pauseForInteraction = useCallback(() => {
    userInteracted.current = true;
    setPaused(true);
  }, []);

  const resumeAfterDelay = useCallback(() => {
    setTimeout(() => {
      userInteracted.current = false;
      setPaused(false);
    }, AUTO_INTERVAL * 2);
  }, []);

  if (count === 0) return null;

  const arrowStyle: React.CSSProperties = {
    position: "absolute",
    top: "50%",
    transform: "translateY(-50%)",
    zIndex: 10,
    background: "rgba(0,0,0,0.45)",
    backdropFilter: "blur(4px)",
    border: "none",
    color: "#fff",
    fontSize: "20px",
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    cursor: "pointer",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.2s",
  };

  return (
    <section
      className="relative w-full overflow-hidden rounded-lg select-none"
      style={{ minHeight: "260px", maxHeight: "500px", height: "clamp(260px, 40vw, 500px)" }}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => { if (!userInteracted.current) setPaused(false); }}
    >
      <style>{`.featured-scroll::-webkit-scrollbar { display: none; }`}</style>

      {/* Scrollable slide track */}
      <div
        ref={scrollRef}
        className="featured-scroll"
        style={{
          display: "flex",
          width: "100%",
          height: "100%",
          overflowX: "auto",
          overflowY: "hidden",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          scrollSnapType: "x mandatory",
        } as React.CSSProperties}
        onTouchStart={pauseForInteraction}
        onTouchEnd={resumeAfterDelay}
        onMouseDown={pauseForInteraction}
        onMouseUp={resumeAfterDelay}
      >
        {articles.map((article) => (
          <div
            key={article.id}
            style={{
              minWidth: "100%",
              width: "100%",
              height: "100%",
              flexShrink: 0,
              scrollSnapAlign: "start",
            }}
          >
            <Slide article={article} />
          </div>
        ))}
      </div>

      {/* Dot indicators */}
      {count > 1 && (
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-2 z-10">
          {articles.map((_, i) => (
            <button
              key={i}
              onClick={() => { scrollTo(i); setCurrent(i); }}
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
            aria-label="Previous slide"
            className="hidden md:flex"
            style={{ ...arrowStyle, left: 8 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.7)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.45)"; }}
          >
            ‹
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); next(); }}
            aria-label="Next slide"
            className="hidden md:flex"
            style={{ ...arrowStyle, right: 8 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.7)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.45)"; }}
          >
            ›
          </button>
        </>
      )}
    </section>
  );
}
