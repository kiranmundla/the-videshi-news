import { useState, useEffect, useCallback } from "react";

const SUPABASE_BASE =
  "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora/events";

const PHOTOS: { src: string; label: string }[] = [
  { src: `${SUPABASE_BASE}/diwali-celebration.jpg`, label: "Diwali Celebrations" },
  { src: `${SUPABASE_BASE}/holi-festival.jpg`, label: "Holi Festival" },
  { src: `${SUPABASE_BASE}/cricket-match.jpg`, label: "Cricket Finals" },
  { src: `${SUPABASE_BASE}/indian-wedding.jpg`, label: "Indian Wedding" },
  { src: `${SUPABASE_BASE}/temple-ceremony.jpg`, label: "Temple Ceremony" },
  { src: `${SUPABASE_BASE}/yoga-meditation.jpg`, label: "Yoga & Meditation" },
  { src: `${SUPABASE_BASE}/classical-dance.jpg`, label: "Classical Dance" },
  { src: `${SUPABASE_BASE}/mumbai-lights.jpg`, label: "Mumbai Nights" },
  { src: `${SUPABASE_BASE}/street-food.jpg`, label: "Street Food" },
  { src: `${SUPABASE_BASE}/taj-mahal.jpg`, label: "Taj Mahal" },
  { src: `${SUPABASE_BASE}/harvest-season.jpg`, label: "Harvest Season" },
  { src: `${SUPABASE_BASE}/ganesh-chaturthi.jpg`, label: "Ganesh Chaturthi" },
  { src: `${SUPABASE_BASE}/varanasi-ghats.jpg`, label: "Varanasi Ghats" },
  { src: `${SUPABASE_BASE}/spice-market.jpg`, label: "Spice Market" },
  { src: `${SUPABASE_BASE}/rangoli-art.jpg`, label: "Rangoli Art" },
  { src: `${SUPABASE_BASE}/coastal-sunset.jpg`, label: "Coastal Sunset" },
  { src: `${SUPABASE_BASE}/kerala-backwaters.jpg`, label: "Kerala Backwaters" },
  { src: `${SUPABASE_BASE}/durga-puja.jpg`, label: "Durga Puja" },
  { src: `${SUPABASE_BASE}/republic-day.jpg`, label: "Republic Day" },
  { src: `${SUPABASE_BASE}/kumbh-mela.jpg`, label: "Kumbh Mela" },
];

export default function DiasporaPhotoStrip() {
  const [selected, setSelected] = useState<{ src: string; label: string } | null>(null);

  const closeOverlay = useCallback(() => setSelected(null), []);

  useEffect(() => {
    if (!selected) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeOverlay();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [selected, closeOverlay]);

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
              onClick={() => setSelected(photo)}
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
                  height: "60px",
                  background: "linear-gradient(transparent, rgba(0,0,0,0.65))",
                  pointerEvents: "none",
                }}
              />
              {/* Label */}
              <span
                style={{
                  position: "absolute",
                  bottom: "10px",
                  left: "12px",
                  color: "#fff",
                  fontSize: "13px",
                  fontWeight: 600,
                  letterSpacing: "0.03em",
                  textShadow: "0 1px 4px rgba(0,0,0,0.8)",
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

      {/* Fullscreen overlay */}
      {selected && (
        <div
          onClick={closeOverlay}
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
          <img
            src={selected.src}
            alt={selected.label}
            style={{
              maxWidth: "95vw",
              maxHeight: "80vh",
              objectFit: "contain",
              borderRadius: "8px",
            }}
          />
          <p
            style={{
              color: "#fff",
              marginTop: "16px",
              fontSize: "16px",
              fontWeight: 600,
              fontFamily: "var(--font-sans, sans-serif)",
              letterSpacing: "0.02em",
            }}
          >
            {selected.label}
          </p>
          <p
            style={{
              color: "rgba(255,255,255,0.5)",
              marginTop: "8px",
              fontSize: "12px",
              fontFamily: "var(--font-sans, sans-serif)",
            }}
          >
            Tap anywhere to close
          </p>
        </div>
      )}
    </>
  );
}
