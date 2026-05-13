const SUPABASE_BASE = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/diaspora";

const PHOTOS: { src: string; label: string }[] = [
  { src: `${SUPABASE_BASE}/mumbai-1.jpg`, label: "Mumbai" },
  { src: `${SUPABASE_BASE}/delhi-1.jpg`, label: "Delhi" },
  { src: `${SUPABASE_BASE}/london-1.jpg`, label: "London" },
  { src: `${SUPABASE_BASE}/nyc-1.jpg`, label: "New York" },
  { src: `${SUPABASE_BASE}/sydney-1.jpg`, label: "Sydney" },
  { src: `${SUPABASE_BASE}/toronto-1.jpg`, label: "Toronto" },
  { src: `${SUPABASE_BASE}/dubai-1.jpg`, label: "Dubai" },
  { src: `${SUPABASE_BASE}/singapore-1.jpg`, label: "Singapore" },
  { src: `${SUPABASE_BASE}/diwali-1.jpg`, label: "Diwali" },
  { src: `${SUPABASE_BASE}/holi-1.jpg`, label: "Holi" },
  { src: `${SUPABASE_BASE}/varanasi-1.jpg`, label: "Varanasi" },
  { src: `${SUPABASE_BASE}/tajmahal-1.jpg`, label: "Taj Mahal" },
  { src: `${SUPABASE_BASE}/kerala-1.jpg`, label: "Kerala" },
  { src: `${SUPABASE_BASE}/goldengate-1.jpg`, label: "San Francisco" },
  { src: `${SUPABASE_BASE}/hawamahal-1.jpg`, label: "Jaipur" },
  { src: `${SUPABASE_BASE}/cricket-1.jpg`, label: "Cricket" },
  { src: `${SUPABASE_BASE}/mumbai-2.jpg`, label: "Mumbai" },
  { src: `${SUPABASE_BASE}/delhi-2.jpg`, label: "Delhi" },
  { src: `${SUPABASE_BASE}/london-2.jpg`, label: "London" },
  { src: `${SUPABASE_BASE}/nyc-2.jpg`, label: "New York" },
  { src: `${SUPABASE_BASE}/toronto-2.jpg`, label: "Toronto" },
  { src: `${SUPABASE_BASE}/dubai-2.jpg`, label: "Dubai" },
  { src: `${SUPABASE_BASE}/singapore-2.jpg`, label: "Singapore" },
  { src: `${SUPABASE_BASE}/diwali-2.jpg`, label: "Diwali" },
  { src: `${SUPABASE_BASE}/holi-2.jpg`, label: "Holi" },
  { src: `${SUPABASE_BASE}/varanasi-2.jpg`, label: "Varanasi" },
  { src: `${SUPABASE_BASE}/tajmahal-2.jpg`, label: "Taj Mahal" },
  { src: `${SUPABASE_BASE}/kerala-2.jpg`, label: "Kerala" },
  { src: `${SUPABASE_BASE}/goldengate-2.jpg`, label: "San Francisco" },
  { src: `${SUPABASE_BASE}/hawamahal-2.jpg`, label: "Jaipur" },
  { src: `${SUPABASE_BASE}/cricket-2.jpg`, label: "Cricket" },
];

const PHOTO_WIDTH = 300;
const PHOTO_HEIGHT = 180;
const GAP = 12;
const SPEED_SECS = 90; // full loop duration

export default function DiasporaPhotoStrip() {
  const totalWidth = PHOTOS.length * (PHOTO_WIDTH + GAP);

  return (
    <section style={{ overflow: "hidden", margin: "2rem 0 1rem", position: "relative" }}>
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
        Around the World
      </p>

      {/* Inject keyframes */}
      <style>{`
        @keyframes diaspora-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-${totalWidth}px); }
        }
      `}</style>

      {/* Scrolling track */}
      <div
        style={{
          display: "flex",
          gap: `${GAP}px`,
          width: "max-content",
          animation: `diaspora-scroll ${SPEED_SECS}s linear infinite`,
        }}
      >
        {/* Render photos twice for seamless loop */}
        {[...PHOTOS, ...PHOTOS].map((photo, i) => (
          <div
            key={i}
            style={{
              position: "relative",
              width: `${PHOTO_WIDTH}px`,
              height: `${PHOTO_HEIGHT}px`,
              borderRadius: "6px",
              overflow: "hidden",
              flexShrink: 0,
              background: "#1C1C1E",
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
              }}
            />
            {/* Location label overlay */}
            <span
              style={{
                position: "absolute",
                bottom: "8px",
                left: "10px",
                color: "#fff",
                fontSize: "12px",
                fontWeight: 600,
                letterSpacing: "0.04em",
                textShadow: "0 1px 4px rgba(0,0,0,0.7)",
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
  );
}
