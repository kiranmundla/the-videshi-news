import { useState, useEffect, useCallback, useRef } from "react";

interface Photo {
  src: string;
  caption: string;
}

interface Props {
  photos: Photo[];
  itemWidth?: number;
  itemHeight?: number;
  objectFit?: "cover" | "contain";
  onPhotoClick?: (photos: Photo[], index: number) => void;
}

const GAP = 12;
const FADE_WIDTH = 56;

export default function PhotoScrollStrip({ photos, itemWidth = 280, itemHeight = 180, objectFit = "cover", onPhotoClick }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const nudgedRef = useRef(false);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const updateScrollState = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 10);
    const first = el.children[0] as HTMLElement | undefined;
    const step = first ? first.offsetWidth + GAP : el.clientWidth * 0.75;
    if (step > 0) {
      setCurrentIndex(Math.min(photos.length - 1, Math.max(0, Math.round(el.scrollLeft / step))));
    }
  }, [photos.length]);

  const scrollStrip = useCallback((direction: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const amount = el.clientWidth * 0.75;
    el.scrollBy({ left: direction === "right" ? amount : -amount, behavior: "smooth" });
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateScrollState();
    el.addEventListener("scroll", updateScrollState, { passive: true });
    window.addEventListener("resize", updateScrollState);
    return () => {
      el.removeEventListener("scroll", updateScrollState);
      window.removeEventListener("resize", updateScrollState);
    };
  }, [photos, updateScrollState]);

  // One-time scroll "nudge" on first view so readers discover the strip is swipeable
  useEffect(() => {
    const el = scrollRef.current;
    if (!el || nudgedRef.current || photos.length < 2) return;
    nudgedRef.current = true;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const t = setTimeout(() => {
      if (el.scrollWidth - el.clientWidth < 40) return;
      el.scrollBy({ left: 64, behavior: "smooth" });
      setTimeout(() => { el.scrollBy({ left: -64, behavior: "smooth" }); }, 650);
    }, 600);
    return () => clearTimeout(t);
  }, [photos.length]);

  if (!photos.length) return null;

  const arrowStyle: React.CSSProperties = {
    position: "absolute",
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
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.2s, opacity 0.2s",
    opacity: 0.9,
  };

  const fadeBase: React.CSSProperties = {
    position: "absolute",
    top: 0,
    bottom: 0,
    width: FADE_WIDTH,
    zIndex: 5,
    pointerEvents: "none",
  };

  return (
    <div style={{ position: "relative" }}>
      <style>{`.photo-scroll-strip::-webkit-scrollbar { display: none; }`}</style>

      {/* Edge fades — signal more content in that direction */}
      {canScrollLeft && (
        <div
          aria-hidden
          style={{
            ...fadeBase,
            left: 0,
            background: "linear-gradient(to right, hsl(var(--background)), hsl(var(--background) / 0))",
          }}
        />
      )}
      {canScrollRight && (
        <div
          aria-hidden
          style={{
            ...fadeBase,
            right: 0,
            background: "linear-gradient(to left, hsl(var(--background)), hsl(var(--background) / 0))",
          }}
        />
      )}

      {/* Photo counter — makes the total count visible at a glance */}
      {photos.length > 1 && (
        <div
          aria-hidden
          style={{
            position: "absolute",
            top: 8,
            right: 8,
            zIndex: 10,
            background: "rgba(0,0,0,0.55)",
            backdropFilter: "blur(4px)",
            color: "#fff",
            fontSize: 12,
            fontWeight: 600,
            fontVariantNumeric: "tabular-nums",
            padding: "4px 10px",
            borderRadius: 999,
            pointerEvents: "none",
            letterSpacing: "0.02em",
          }}
        >
          {currentIndex + 1} / {photos.length}
        </div>
      )}

      {canScrollLeft && (
        <button
          onClick={() => scrollStrip("left")}
          aria-label="Scroll left"
          className="hidden md:flex"
          style={{ ...arrowStyle, left: 4 }}
          onMouseEnter={(e) => { (e.currentTarget.style.background) = "rgba(0,0,0,0.85)"; }}
          onMouseLeave={(e) => { (e.currentTarget.style.background) = "rgba(0,0,0,0.6)"; }}
        >‹</button>
      )}

      {canScrollRight && (
        <button
          onClick={() => scrollStrip("right")}
          aria-label="Scroll right"
          className="hidden md:flex"
          style={{ ...arrowStyle, right: 4 }}
          onMouseEnter={(e) => { (e.currentTarget.style.background) = "rgba(0,0,0,0.85)"; }}
          onMouseLeave={(e) => { (e.currentTarget.style.background) = "rgba(0,0,0,0.6)"; }}
        >›</button>
      )}

      <div
        ref={scrollRef}
        className="photo-scroll-strip"
        style={{
          display: "flex",
          gap: GAP,
          overflowX: "auto",
          overflowY: "hidden",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          scrollSnapType: "x mandatory",
          paddingLeft: "4%",
          paddingRight: "4%",
        } as React.CSSProperties}
      >
        {photos.map((photo, i) => (
          <div
            key={i}
            onClick={() => onPhotoClick?.(photos, i)}
            style={{
              position: "relative",
              width: itemWidth,
              maxWidth: "calc(100vw - 88px)",
              flexShrink: 0,
              cursor: onPhotoClick ? "pointer" : "default",
              scrollSnapAlign: "center",
            }}
          >
            <div style={{
              width: "100%",
              height: itemHeight,
              borderRadius: 8,
              overflow: "hidden",
              background: "#1a1a1a",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            }}>
              <img
                src={photo.src}
                alt={photo.caption}
                loading="lazy"
                style={{ width: "100%", height: "100%", objectFit: objectFit, display: "block", background: objectFit === "contain" ? "#111" : undefined }}
              />
            </div>
            {photo.caption && (
              <div style={{
                padding: "6px 4px",
                color: "#666", fontSize: "0.75rem", fontStyle: "italic",
                lineHeight: 1.4,
              }}>
                {photo.caption}
              </div>
            )}
          </div>))}
      </div>
    </div>
  );
}
