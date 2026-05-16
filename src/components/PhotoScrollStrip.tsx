import { useState, useEffect, useCallback, useRef } from "react";

interface Photo {
  src: string;
  caption: string;
}

interface Props {
  photos: Photo[];
  itemWidth?: number;
  itemHeight?: number;
  onPhotoClick?: (photos: Photo[], index: number) => void;
}

export default function PhotoScrollStrip({ photos, itemWidth = 280, itemHeight = 180, onPhotoClick }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

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
  }, [photos, updateScrollButtons]);

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
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.2s, opacity 0.2s",
    opacity: 0.9,
  };

  return (
    <div style={{ position: "relative" }}>
      <style>{`.photo-scroll-strip::-webkit-scrollbar { display: none; }`}</style>

      {canScrollLeft && (
        <button
          onClick={() => scrollStrip("left")}
          aria-label="Scroll left"
          style={{ ...arrowStyle, left: 4 }}
          onMouseEnter={(e) => { (e.currentTarget.style.background) = "rgba(0,0,0,0.85)"; }}
          onMouseLeave={(e) => { (e.currentTarget.style.background) = "rgba(0,0,0,0.6)"; }}
        >‹</button>
      )}

      {canScrollRight && (
        <button
          onClick={() => scrollStrip("right")}
          aria-label="Scroll right"
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
          gap: 12,
          overflowX: "auto",
          overflowY: "hidden",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
        } as React.CSSProperties}
      >
        {photos.map((photo, i) => (
          <div
            key={i}
            onClick={() => onPhotoClick?.(photos, i)}
            style={{
              position: "relative",
              width: itemWidth,
              height: itemHeight,
              borderRadius: 8,
              overflow: "hidden",
              flexShrink: 0,
              background: "#1a1a1a",
              cursor: onPhotoClick ? "pointer" : "default",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            }}
          >
            <img
              src={photo.src}
              alt={photo.caption}
              loading="lazy"
              style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
            />
            <div style={{
              position: "absolute", bottom: 0, left: 0, right: 0,
              padding: "20px 10px 8px",
              background: "linear-gradient(transparent, rgba(0,0,0,0.7))",
              color: "white", fontSize: "0.75rem", fontWeight: 500,
            }}>
              {photo.caption}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
