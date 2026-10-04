import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import Lightbox from "@/components/Lightbox";

type Photo = { src: string; label: string; source?: string; added_date?: string };

const FALLBACK_PHOTOS: Photo[] = [
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/jaipur-hawa-mahal.jpg", label: "Albert Hall Museum, Jaipur" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/republic-day-parade.jpg", label: "BSF camel contingent, Republic Day parade, New Delhi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/delhi-street-food.jpg", label: "Curry and naan" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ganesh-chaturthi-mumbai.jpg", label: "Ganesh Chaturthi idol, Mumbai" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-railway.jpg", label: "Indian Railways" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/durga-puja-kolkata.jpg", label: "Durga Puja pandal, Kolkata" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-spice-market.jpg", label: "Indian spices" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/india-gate-delhi.jpg", label: "India Gate, New Delhi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ram-mandir-temple.jpg", label: "Hindu temple gopuram, South India" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ipl-cricket.jpg", label: "Cricket practice, India" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/varanasi-ghats.jpg", label: "Boats at the ghats, Varanasi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/kerala-backwaters.jpg", label: "Houseboat on the backwaters, Kerala" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/kumbh-mela.jpg", label: "Boats on the Ganges, Varanasi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/taj-mahal-agra.jpg", label: "Taj Mahal, Agra" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/pushkar-camel-fair.jpg", label: "Camel trader, Pushkar, Rajasthan" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/onam-boat-race.jpg", label: "Snake boat race, Kerala" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/holi-mathura.jpg", label: "Holi celebrations, India" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/mumbai-skyline.jpg", label: "Mumbai skyline from the Arabian Sea" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/diwali-diyas.jpg", label: "Diwali diyas" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-wedding.jpg", label: "Mehndi and bangles, Indian wedding" },
];

const DISPLAY_COUNT = 20;

/** Simple seeded PRNG (mulberry32) for date-stable shuffle */
function seededRng(seed: number) {
  return () => {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

/** Shuffle array in place using a seeded RNG */
function seededShuffle<T>(arr: T[], seed: number): T[] {
  const rng = seededRng(seed);
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/** Date seed: same value all day so shuffle is stable across re-renders */
function todaySeed(): number {
  const d = new Date();
  return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
}

export default function DiasporaPhotoStrip() {
  const [pool, setPool] = useState<Photo[]>(FALLBACK_PHOTOS);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  // Fetch pool from JSON on mount
  useEffect(() => {
    fetch("/data/snapshots-pool.json")
      .then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then((data: Photo[]) => { if (Array.isArray(data) && data.length > 0) setPool(data); })
      .catch(() => { /* keep FALLBACK_PHOTOS */ });
  }, []);

  // Pick 20 photos from the pool with a date-stable shuffle
  const photos = useMemo(() => {
    if (pool.length <= DISPLAY_COUNT) return pool;
    const shuffled = seededShuffle(pool, todaySeed());
    return shuffled.slice(0, DISPLAY_COUNT);
  }, [pool]);

  // Preload all images when the lightbox opens
  useEffect(() => {
    if (selectedIndex === null) return;
    photos.forEach((p) => {
      const img = new Image();
      img.src = p.src;
    });
  }, [selectedIndex, photos]);

  // Strip scroll buttons
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

  // Preload first 4 strip images eagerly on mount
  useEffect(() => {
    photos.slice(0, 4).forEach((p) => {
      const img = new Image();
      img.src = p.src;
    });
  }, [photos]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateScrollButtons();
    el.addEventListener("scroll", updateScrollButtons, { passive: true });
    window.addEventListener("resize", updateScrollButtons);
    return () => {
      el.removeEventListener("scroll", updateScrollButtons);
      window.removeEventListener("resize", updateScrollButtons);
    };
  }, [updateScrollButtons]);

  return (
    <>
      <section style={{ margin: "2rem 0 1rem", position: "relative" }}>
        {/* Section label */}
        <div className="container">
        <p
          style={{
            fontFamily: "var(--font-sans, sans-serif)",
            fontSize: "11px",
            fontWeight: 600,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "hsl(var(--muted-foreground))",
            margin: "0 0 0.75rem 0",
          }}
        >
          Snapshots
        </p>
        </div>

        <style>{`
          .diaspora-scroll-strip::-webkit-scrollbar { display: none; }
        `}</style>

        {/* Container with nav arrows */}
        <div className="container" style={{ position: "relative" }}>
          {canScrollLeft && (
            <button
              onClick={() => scrollStrip("left")}
              aria-label="Scroll left"
              style={{
                position: "absolute",
                left: "4px",
                top: "50%",
                transform: "translateY(-50%)",
                zIndex: 10,
                background: "rgba(0,0,0,0.6)",
                backdropFilter: "blur(4px)",
                border: "none",
                color: "#fff",
                fontSize: "18px",
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "background 0.2s, opacity 0.2s",
                opacity: 0.9,
              }}
              onMouseEnter={(e) => { (e.target as HTMLElement).style.background = "rgba(0,0,0,0.85)"; }}
              onMouseLeave={(e) => { (e.target as HTMLElement).style.background = "rgba(0,0,0,0.6)"; }}
            >
              ‹
            </button>
          )}

          {canScrollRight && (
            <button
              onClick={() => scrollStrip("right")}
              aria-label="Scroll right"
              style={{
                position: "absolute",
                right: "4px",
                top: "50%",
                transform: "translateY(-50%)",
                zIndex: 10,
                background: "rgba(0,0,0,0.6)",
                backdropFilter: "blur(4px)",
                border: "none",
                color: "#fff",
                fontSize: "18px",
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "background 0.2s, opacity 0.2s",
                opacity: 0.9,
              }}
              onMouseEnter={(e) => { (e.target as HTMLElement).style.background = "rgba(0,0,0,0.85)"; }}
              onMouseLeave={(e) => { (e.target as HTMLElement).style.background = "rgba(0,0,0,0.6)"; }}
            >
              ›
            </button>
          )}

          {/* Horizontal scroll container */}
          <div
            ref={scrollRef}
            className="diaspora-scroll-strip"
            style={{
              display: "flex",
              gap: "12px",
              overflowX: "auto",
              overflowY: "hidden",
              WebkitOverflowScrolling: "touch",
              scrollbarWidth: "none",
              msOverflowStyle: "none",
            } as React.CSSProperties}
          >
            {photos.map((photo, i) => (
              <div
                key={photo.src}
                onClick={() => setSelectedIndex(i)}
                style={{
                  position: "relative",
                  minWidth: "260px",
                  width: "300px",
                  height: "200px",
                  borderRadius: "8px",
                  overflow: "hidden",
                  flexShrink: 0,
                  background: "#1C1C1E",
                  cursor: "pointer",
                }}
              >
                <img
                  src={photo.src}
                  alt={photo.label}
                  loading={i < 4 ? "eager" : "lazy"}
                  draggable={false}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    display: "block",
                    transition: "transform 0.3s ease",
                  }}
                  onMouseEnter={(e) => { (e.target as HTMLImageElement).style.transform = "scale(1.05)"; }}
                  onMouseLeave={(e) => { (e.target as HTMLImageElement).style.transform = "scale(1)"; }}
                />
                <div
                  style={{
                    position: "absolute",
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: "70px",
                    background: "linear-gradient(transparent, rgba(0,0,0,0.75))",
                    pointerEvents: "none",
                  }}
                />
                <span
                  style={{
                    position: "absolute",
                    bottom: "10px",
                    left: "12px",
                    right: "12px",
                    color: "#fff",
                    fontSize: "12px",
                    fontWeight: 600,
                    lineHeight: "1.3",
                    letterSpacing: "0.02em",
                    textShadow: "0 1px 4px rgba(0,0,0,0.9)",
                    fontFamily: "var(--font-sans, sans-serif)",
                  }}
                >
                  {photo.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="container">
        <p
          style={{
            fontFamily: "var(--font-sans, sans-serif)",
            fontSize: "10px",
            color: "hsl(var(--muted-foreground))",
            opacity: 0.6,
            margin: "0.5rem 0 0 0",
          }}
        >
          Photos by Pexels contributors
        </p>
        </div>
      </section>

      {/* Fullscreen lightbox (shared) */}
      <Lightbox
        open={selectedIndex !== null}
        initialIndex={selectedIndex ?? 0}
        count={photos.length}
        onClose={() => setSelectedIndex(null)}
        renderSlide={(i) => (
          <img
            src={photos[i]?.src}
            alt={photos[i]?.label}
            loading={Math.abs(i - (selectedIndex ?? 0)) <= 2 ? "eager" : "lazy"}
            draggable={false}
            style={{
              maxWidth: "calc(100vw - 40px)",
              maxHeight: "calc(100vh - 140px)",
              objectFit: "contain",
              borderRadius: "8px",
              userSelect: "none",
              WebkitUserSelect: "none",
            } as React.CSSProperties}
          />
        )}
        renderBelow={(i) => (
          <p style={{
            color: "#fff", fontSize: "15px", fontWeight: 600,
            fontFamily: "var(--font-sans, sans-serif)", letterSpacing: "0.02em",
            textAlign: "center", padding: "8px 20px 0", margin: 0,
          }}>
            {photos[i]?.label}
          </p>
        )}
      />
    </>
  );
}
