import { useState, useEffect, useCallback, useRef } from "react";
import { optimizeImageUrl, IMAGE_SIZES } from "@/lib/imageUrl";

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

export default function PhotoScrollStrip({ photos, itemWidth = 280, itemHeight = 180, objectFit = "cover", onPhotoClick }: Props) {
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
          gap: 12,
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
              maxWidth: "calc(100vw - 32px)",
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
                src={optimizeImageUrl(photo.src, IMAGE_SIZES.gallery)}
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
