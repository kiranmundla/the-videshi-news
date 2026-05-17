import { useState, useEffect, useCallback, useRef } from "react";

const PHOTOS: { src: string; label: string }[] = [
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/durga-puja-kolkata.jpg", label: "Durga Puja pandal, Kolkata" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/holi-mathura.jpg", label: "Holi celebrations, India" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/pushkar-camel-fair.jpg", label: "Camel trader, Pushkar, Rajasthan" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ram-mandir-temple.jpg", label: "Hindu temple gopuram, South India" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-wedding.jpg", label: "Mehndi and bangles, Indian wedding" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/onam-boat-race.jpg", label: "Snake boat race, Kerala" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/delhi-street-food.jpg", label: "Curry and naan" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/mumbai-skyline.jpg", label: "Mumbai skyline from the Arabian Sea" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-railway.jpg", label: "Indian Railways" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/india-gate-delhi.jpg", label: "India Gate, New Delhi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/republic-day-parade.jpg", label: "BSF camel contingent, Republic Day parade, New Delhi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/jaipur-hawa-mahal.jpg", label: "Albert Hall Museum, Jaipur" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/kerala-backwaters.jpg", label: "Houseboat on the backwaters, Kerala" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/taj-mahal-agra.jpg", label: "Taj Mahal, Agra" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/varanasi-ghats.jpg", label: "Boats at the ghats, Varanasi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-spice-market.jpg", label: "Indian spices" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/kumbh-mela.jpg", label: "Boats on the Ganges, Varanasi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ipl-cricket.jpg", label: "Cricket practice, India" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ganesh-chaturthi-mumbai.jpg", label: "Ganesh Chaturthi idol, Mumbai" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/diwali-diyas.jpg", label: "Diwali diyas" },
];

export default function DiasporaPhotoStrip() {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const touchStartX = useRef<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const closeOverlay = useCallback(() => setSelectedIndex(null), []);

  const goNext = useCallback(() => {
    setSelectedIndex((prev) => (prev !== null ? (prev + 1) % PHOTOS.length : null));
  }, []);

  const goPrev = useCallback(() => {
    setSelectedIndex((prev) => (prev !== null ? (prev - 1 + PHOTOS.length) % PHOTOS.length : null));
  }, []);

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

  useEffect(() => {
    if (selectedIndex === null) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeOverlay();
      if (e.key === "ArrowRight") goNext();
      if (e.key === "ArrowLeft") goPrev();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [selectedIndex, closeOverlay, goNext, goPrev]);

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStartX.current === null) return;
    const deltaX = e.changedTouches[0].clientX - touchStartX.current;
    if (Math.abs(deltaX) > 50) {
      if (deltaX < 0) goNext();
      else goPrev();
    }
    touchStartX.current = null;
  };

  const selected = selectedIndex !== null ? PHOTOS[selectedIndex] : null;

  return (
    <>
      <section style={{ margin: "2rem 0 1rem", position: "relative" }}>
        {/* Section label */}
        <p
          style={{
            fontFamily: "var(--font-sans, sans-serif)",
            fontSize: "11px",
            fontWeight: 600,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "hsl(var(--muted-foreground))",
            margin: "0 0 0.75rem 1rem",
          }}
        >
          Snapshots
        </p>

        {/* Hide scrollbar styles */}
        <style>{`
          .diaspora-scroll-strip::-webkit-scrollbar { display: none; }
        `}</style>

        {/* Container with nav arrows */}
        <div style={{ position: "relative" }}>
          {/* Left arrow */}
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

          {/* Right arrow */}
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
            padding: "0 1rem",
          } as React.CSSProperties}
        >
          {PHOTOS.map((photo, i) => (
            <div
              key={i}
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
                loading="lazy"
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
              {/* Gradient overlay for readability */}
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
              {/* Label */}
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

        {/* Pexels attribution */}
        <p
          style={{
            fontFamily: "var(--font-sans, sans-serif)",
            fontSize: "10px",
            color: "hsl(var(--muted-foreground))",
            opacity: 0.6,
            margin: "0.5rem 0 0 1rem",
          }}
        >
          Photos by Pexels contributors
        </p>
      </section>

      {/* Fullscreen overlay with navigation */}
      {selected && selectedIndex !== null && (
        <div
          onClick={closeOverlay}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.95)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            cursor: "pointer",
            padding: "20px",
            animation: "snapFadeIn 0.15s ease-out",
          }}
        >
          <style>{`
            @keyframes snapFadeIn { from { opacity: 0; } to { opacity: 1; } }
            .snap-photo-transition { transition: opacity 0.2s ease; }
          `}</style>

          {/* Close button */}
          <button
            onClick={closeOverlay}
            style={{
              position: "absolute", top: 12, right: 16, zIndex: 10000,
              background: "rgba(255,255,255,0.15)", border: "none", color: "#fff",
              width: 36, height: 36, borderRadius: "50%", cursor: "pointer",
              fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center",
            }}
          >×</button>

          {/* Counter */}
          <p
            onClick={(e) => e.stopPropagation()}
            style={{
              color: "rgba(255,255,255,0.5)",
              fontSize: "13px",
              fontFamily: "var(--font-sans, sans-serif)",
              marginBottom: "12px",
              userSelect: "none",
            }}
          >
            {selectedIndex + 1} / {PHOTOS.length}
          </p>

          {/* Image */}
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              maxWidth: "90vw",
              maxHeight: "75vh",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <img
              key={selectedIndex}
              className="snap-photo-transition"
              src={selected.src}
              alt={selected.label}
              style={{
                maxWidth: "90vw",
                maxHeight: "75vh",
                objectFit: "contain",
                borderRadius: "8px",
              }}
            />
          </div>

          {/* Caption */}
          <p
            onClick={(e) => e.stopPropagation()}
            style={{
              color: "#fff",
              marginTop: "16px",
              fontSize: "15px",
              fontWeight: 600,
              fontFamily: "var(--font-sans, sans-serif)",
              letterSpacing: "0.02em",
              textAlign: "center",
              maxWidth: "600px",
            }}
          >
            {selected.label}
          </p>
        </div>
      )}
    </>
  );
}
