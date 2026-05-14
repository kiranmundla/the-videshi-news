import { useState, useEffect, useCallback, useRef } from "react";

const PHOTOS: { src: string; label: string }[] = [
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-ba562d29-cfdc-40d0-9ee8-2690437b2aba-1778782507942.jpg", label: "UK Doctor Stranded in India Four Months Over Facebook Pos... · NRI World" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/8be40a78-98b8-45a8-8427-b03aaae65038.jpg?w=960&h=702", label: "GB News Doc: Ex-Google Worker Says Indians Shared Intervi... · NRI World" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-3a4c5c35-ecfb-4efe-939e-f162f6093c47-1778782509742.jpg", label: "US Moves to Drop Adani Fraud Case, SEC Eyes Settlement · Markets" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-0b09fa0e-b283-41a9-995c-2b32b36b61aa-1778771707678.jpg", label: "Kevin Warsh Confirmed as Federal Reserve Chair in 54-45 S... · Markets" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/a56fe97d-b34e-481a-bacb-af06780ecd3b.jpg?w=960&h=714", label: "Indian Man, 27, Killed in Rare Bear Attack at Canadian Ur... · NRI World" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-8419a4ff-5c34-402e-9e6b-e672206ac183-1778771709172.jpg", label: "UAE Warns Workers: Change Jobs Wrong, Face a One-Year Per... · NRI World" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/d03319c6-46d9-423e-9d50-ab75ae281ffd.jpg?w=960&h=960", label: "Deepika Padukone Returns to Mumbai After Filming 'King' W... · Entertainment" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/ef6d8ff9-5175-44d4-949b-65171339957a.jpg?w=800&h=1075", label: "Kohli's Unbeaten 105 Powers RCB to Top of IPL 2026 Table · Sports" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/c0526080-b213-4179-ae44-affd8eb9b6bd.jpg?w=960&h=960", label: "Newsom Taps Indian-American Rohit Chopra to Lead Californ... · India News" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/4f2429e2-2d93-429d-b8d3-d502e538a11d.jpg?w=960&h=513", label: "ICICI Bank Launches India's First USD Debit Card for NRIs... · Markets" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-19cea1f5-ed83-487d-a7bf-ba46d9483856-1778768105736.png", label: "ICE Exposes Massive OPT Visa Fraud, 10,000 Foreign Studen... · NRI World" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-6e5b1629-f1e1-485d-b04c-1efbe5cff29f-1778706904167.png", label: "India May Miss FIFA World Cup 2026 on TV as Broadcast Rig... · Sports" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/dae5f29a-6db2-43c4-b814-bb85b7440d43.jpg?w=960&h=722", label: "Apple and Meta Fight Canada Encryption Bill, Warn of Mass... · Technology" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/0559587b-af53-4ad6-9a5b-f81855899d24.jpg?w=960&h=702", label: "Google and SpaceX Explore Orbital Data Centers in AI Arms... · Technology" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/a6eb9bc3-4dba-4bd3-b8bc-da2d3ff530f1.jpg?w=809&h=1080", label: "Suriya and Trisha Reunite After 20 Years as Karuppu Cross... · Entertainment" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-40d5a644-540a-4ed5-988c-8f28700cde9a-1778706905946.jpg", label: "Two Indian American CMU Professors Win National Research ... · NRI World" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/p2-c4f29c76-1fb6-453d-9ffa-3329e71de49c-1778706908776.jpg", label: "GM Cuts 600 IT Workers, Pivots to AI-Native Hiring · Technology" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/fdaab7da-f836-48a0-89c7-a55fd8a5c0f3.jpg?w=800&h=1040", label: "Jensen Huang Overtakes Michael Dell, Nears $200 Billion F... · Markets" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/f7c64430-274a-4065-9739-d79715a29582.jpg?w=960&h=1396", label: "CM Vijay Wins Tamil Nadu Floor Test With 144 Votes, Cemen... · India News" },
  { src: "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/e3fe4389-c2aa-474c-9859-995c25618251.jpg?w=960&h=1276", label: "Kash Patel Denies Drinking Claims in Fiery Senate Showdown · NRI World" },
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
