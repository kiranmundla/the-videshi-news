import { useState, useEffect, useCallback, useRef } from "react";

const PHOTOS: { src: string; label: string }[] = [
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-spice-market.jpg", label: "Spice market, Old Delhi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/delhi-street-food.jpg", label: "Chandni Chowk street food, Delhi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-railway.jpg", label: "Indian Railways, en route to Varanasi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ipl-cricket.jpg", label: "IPL 2026 season opener, Lucknow" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/durga-puja-kolkata.jpg", label: "Durga Puja pandals, Kolkata, Oct 2025" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/mumbai-skyline.jpg", label: "Mumbai skyline from Marine Drive" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/pushkar-camel-fair.jpg", label: "Pushkar Camel Fair, Rajasthan, Nov 2025" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/taj-mahal-agra.jpg", label: "Taj Mahal reopens after restoration, Agra" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/jaipur-hawa-mahal.jpg", label: "Hawa Mahal, Jaipur, Rajasthan" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/onam-boat-race.jpg", label: "Onam boat race, Alleppey, Kerala, Aug 2025" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/kerala-backwaters.jpg", label: "Kerala backwaters, Alleppey" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/diwali-diyas.jpg", label: "Diwali lights at Jama Masjid, Delhi, Oct 2025" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ganesh-chaturthi-mumbai.jpg", label: "Ganesh Chaturthi immersion, Mumbai, Sep 2025" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/india-gate-delhi.jpg", label: "India Gate at sunset, New Delhi" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/republic-day-parade.jpg", label: "Republic Day Parade, New Delhi, Jan 2026" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/ram-mandir-temple.jpg", label: "Ram Mandir first anniversary, Ayodhya, Jan 2026" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/indian-wedding.jpg", label: "Wedding season in full swing, Delhi, Dec 2025" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/varanasi-ghats.jpg", label: "Dev Deepawali, Varanasi, Nov 2025" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/kumbh-mela.jpg", label: "Kumbh Mela 2025, Prayagraj" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events/holi-mathura.jpg", label: "Holi celebrations, Mathura, March 2026" },
];

export default function DiasporaPhotoStrip() {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const touchStartX = useRef<number | null>(null);

  const closeOverlay = useCallback(() => setSelectedIndex(null), []);

  const goNext = useCallback(() => {
    setSelectedIndex((prev) => (prev !== null ? (prev + 1) % PHOTOS.length : null));
  }, []);

  const goPrev = useCallback(() => {
    setSelectedIndex((prev) => (prev !== null ? (prev - 1 + PHOTOS.length) % PHOTOS.length : null));
  }, []);

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

        {/* Horizontal scroll container */}
        <div
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
          }}
        >
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

          {/* Image + arrows row */}
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              maxWidth: "95vw",
              maxHeight: "75vh",
            }}
          >
            {/* Left arrow */}
            <button
              onClick={(e) => { e.stopPropagation(); goPrev(); }}
              style={{
                background: "rgba(255,255,255,0.1)",
                border: "none",
                color: "#fff",
                fontSize: "28px",
                width: "44px",
                height: "44px",
                borderRadius: "50%",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                transition: "background 0.2s",
              }}
              onMouseEnter={(e) => { (e.target as HTMLElement).style.background = "rgba(255,255,255,0.25)"; }}
              onMouseLeave={(e) => { (e.target as HTMLElement).style.background = "rgba(255,255,255,0.1)"; }}
              aria-label="Previous photo"
            >
              ◀
            </button>

            {/* Image */}
            <img
              src={selected.src}
              alt={selected.label}
              style={{
                maxWidth: "calc(95vw - 120px)",
                maxHeight: "75vh",
                objectFit: "contain",
                borderRadius: "8px",
                flexShrink: 1,
              }}
            />

            {/* Right arrow */}
            <button
              onClick={(e) => { e.stopPropagation(); goNext(); }}
              style={{
                background: "rgba(255,255,255,0.1)",
                border: "none",
                color: "#fff",
                fontSize: "28px",
                width: "44px",
                height: "44px",
                borderRadius: "50%",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                transition: "background 0.2s",
              }}
              onMouseEnter={(e) => { (e.target as HTMLElement).style.background = "rgba(255,255,255,0.25)"; }}
              onMouseLeave={(e) => { (e.target as HTMLElement).style.background = "rgba(255,255,255,0.1)"; }}
              aria-label="Next photo"
            >
              ▶
            </button>
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
          <p
            style={{
              color: "rgba(255,255,255,0.4)",
              marginTop: "10px",
              fontSize: "11px",
              fontFamily: "var(--font-sans, sans-serif)",
            }}
          >
            Tap background to close · Swipe or use arrows to navigate
          </p>
        </div>
      )}
    </>
  );
}
