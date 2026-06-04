import { useState, useRef, useCallback, useEffect } from "react";

export interface SocialPhoto {
  src: string;
  alt?: string;
}

interface SocialPhotoStripProps {
  images: SocialPhoto[];
  via: string;          // e.g. "@BCCI"
  platform: "x" | "instagram" | "threads";
  postUrl?: string;     // link to original post
  caption?: string;     // optional text above the strip
}

const platformLabel: Record<string, string> = {
  x: "𝕏",
  instagram: "Instagram",
  threads: "Threads",
};

export default function SocialPhotoStrip({ images, via, platform, postUrl, caption }: SocialPhotoStripProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const overlayScrollRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Pull-down-to-dismiss state
  const [dragY, setDragY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dismissing, setDismissing] = useState(false);
  const touchStartY = useRef<number | null>(null);
  const touchStartX = useRef<number | null>(null);
  const isVerticalGesture = useRef(false);

  if (!images || images.length === 0) return null;

  const attrText = `${via} on ${platformLabel[platform] || platform}`;

  const closeOverlay = useCallback(() => {
    setSelectedIndex(null);
    setDragY(0);
    setIsDragging(false);
    setDismissing(false);
  }, []);

  const closeWithDismiss = useCallback(() => {
    setDismissing(true);
    setTimeout(() => {
      setSelectedIndex(null);
      setDragY(0);
      setIsDragging(false);
      setDismissing(false);
    }, 200);
  }, []);

  // Sync overlay scroll to current index
  const handleOverlayScroll = useCallback(() => {
    const el = overlayScrollRef.current;
    if (!el) return;
    const idx = Math.round(el.scrollLeft / el.clientWidth);
    if (idx >= 0 && idx < images.length) setCurrentIndex(idx);
  }, [images.length]);

  // Open lightbox at tapped index
  useEffect(() => {
    if (selectedIndex === null) return;
    setCurrentIndex(selectedIndex);
    requestAnimationFrame(() => {
      const el = overlayScrollRef.current;
      if (el) el.scrollTo({ left: selectedIndex * el.clientWidth, behavior: "instant" as ScrollBehavior });
    });
  }, [selectedIndex]);

  // Keyboard nav
  useEffect(() => {
    if (selectedIndex === null) return;
    const handleKey = (e: KeyboardEvent) => {
      const el = overlayScrollRef.current;
      if (!el) return;
      if (e.key === "Escape") closeOverlay();
      if (e.key === "ArrowRight") el.scrollTo({ left: Math.min(currentIndex + 1, images.length - 1) * el.clientWidth, behavior: "smooth" });
      if (e.key === "ArrowLeft") el.scrollTo({ left: Math.max(currentIndex - 1, 0) * el.clientWidth, behavior: "smooth" });
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [selectedIndex, currentIndex, closeOverlay, images.length]);

  // Touch handlers for pull-down
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
    touchStartX.current = e.touches[0].clientX;
    isVerticalGesture.current = false;
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (touchStartY.current === null || touchStartX.current === null) return;
    const dy = e.touches[0].clientY - touchStartY.current;
    const dx = Math.abs(e.touches[0].clientX - touchStartX.current);
    if (!isVerticalGesture.current && !isDragging) {
      if (Math.abs(dy) > 10 && Math.abs(dy) > dx * 1.2) isVerticalGesture.current = true;
      else if (dx > 10) return;
    }
    if (!isVerticalGesture.current) return;
    if (dy > 0) { setIsDragging(true); setDragY(dy); }
  }, [isDragging]);

  const handleTouchEnd = useCallback(() => {
    if (isVerticalGesture.current && dragY > 120) closeWithDismiss();
    else { setDragY(0); setIsDragging(false); }
    touchStartY.current = null;
    touchStartX.current = null;
    isVerticalGesture.current = false;
  }, [dragY, closeWithDismiss]);

  const dragProgress = Math.min(dragY / 300, 1);
  const overlayOpacity = dismissing ? 0 : 1 - dragProgress * 0.6;
  const overlayScale = dismissing ? 0.9 : 1 - dragProgress * 0.1;
  const overlayTranslateY = dismissing ? 100 : dragY;

  const singleImage = images.length === 1;

  return (
    <>
      <figure className="my-6">
        {caption && (
          <p className="text-sm text-muted-foreground mb-2 px-1">{caption}</p>
        )}

        <style>{`.social-photo-scroll::-webkit-scrollbar { display: none; } .social-lightbox::-webkit-scrollbar { display: none; }`}</style>

        {singleImage ? (
          /* Single image — full-width, rounded */
          <div
            onClick={() => setSelectedIndex(0)}
            style={{
              borderRadius: "10px",
              overflow: "hidden",
              cursor: "pointer",
              background: "#1C1C1E",
            }}
          >
            <img
              src={images[0].src}
              alt={images[0].alt || attrText}
              loading="lazy"
              draggable={false}
              style={{
                width: "100%",
                aspectRatio: "16/9",
                objectFit: "cover",
                display: "block",
              }}
            />
          </div>
        ) : (
          /* Multiple images — horizontal scroll strip */
          <div
            ref={scrollRef}
            className="social-photo-scroll"
            style={{
              display: "flex",
              gap: "8px",
              overflowX: "auto",
              overflowY: "hidden",
              WebkitOverflowScrolling: "touch",
              scrollSnapType: "x mandatory",
              scrollbarWidth: "none",
              msOverflowStyle: "none",
            } as React.CSSProperties}
          >
            {images.map((img, i) => (
              <div
                key={i}
                onClick={() => setSelectedIndex(i)}
                style={{
                  minWidth: images.length === 2 ? "calc(50% - 4px)" : "75%",
                  flexShrink: 0,
                  borderRadius: "10px",
                  overflow: "hidden",
                  scrollSnapAlign: "start",
                  cursor: "pointer",
                  background: "#1C1C1E",
                }}
              >
                <img
                  src={img.src}
                  alt={img.alt || `${attrText} photo ${i + 1}`}
                  loading={i < 3 ? "eager" : "lazy"}
                  draggable={false}
                  style={{
                    width: "100%",
                    aspectRatio: "16/9",
                    objectFit: "cover",
                    display: "block",
                  }}
                />
              </div>
            ))}
          </div>
        )}

        {/* Attribution */}
        <figcaption
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            marginTop: "8px",
            paddingLeft: "2px",
          }}
        >
          <span style={{ fontSize: "12px", color: "hsl(var(--muted-foreground))", fontFamily: "var(--font-sans, sans-serif)" }}>
            📸{" "}
            {postUrl ? (
              <a
                href={postUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "hsl(var(--muted-foreground))", textDecoration: "underline", textUnderlineOffset: "2px" }}
              >
                {attrText}
              </a>
            ) : (
              attrText
            )}
          </span>
          {/* Dots for multi-image */}
          {!singleImage && images.length <= 8 && (
            <span style={{ display: "flex", gap: "4px", marginLeft: "auto", paddingRight: "2px" }}>
              {images.map((_, i) => (
                <span key={i} style={{
                  width: "5px", height: "5px", borderRadius: "50%",
                  background: "hsl(var(--muted-foreground))",
                  opacity: 0.4,
                }} />
              ))}
            </span>
          )}
        </figcaption>
      </figure>

      {/* Fullscreen lightbox */}
      {selectedIndex !== null && (
        <div
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: `rgba(0,0,0,${0.95 * overlayOpacity})`,
            zIndex: 9999,
            display: "flex", flexDirection: "column",
            animation: dismissing ? "none" : "spsFadeIn 0.15s ease-out",
            transition: isDragging ? "none" : "background-color 0.2s ease",
          }}
        >
          <style>{`@keyframes spsFadeIn { from { opacity: 0; } to { opacity: 1; } }`}</style>

          <button
            onClick={closeOverlay}
            style={{
              position: "absolute", top: 12, right: 16, zIndex: 10000,
              background: "rgba(255,255,255,0.15)", border: "none", color: "#fff",
              width: 36, height: 36, borderRadius: "50%", cursor: "pointer",
              fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center",
            }}
          >×</button>

          <div style={{
            flex: 1, display: "flex", flexDirection: "column",
            transform: `translateY(${overlayTranslateY}px) scale(${overlayScale})`,
            opacity: overlayOpacity,
            transition: isDragging ? "none" : "transform 0.25s cubic-bezier(0.2,0,0,1), opacity 0.2s ease",
            willChange: "transform, opacity",
          }}>
            {images.length > 1 && (
              <p style={{
                color: "rgba(255,255,255,0.5)", fontSize: "13px",
                fontFamily: "var(--font-sans, sans-serif)", textAlign: "center",
                padding: "16px 0 8px", margin: 0, userSelect: "none",
              }}>
                {currentIndex + 1} / {images.length}
              </p>
            )}

            <div
              ref={overlayScrollRef}
              className="social-lightbox"
              onScroll={handleOverlayScroll}
              style={{
                flex: 1, display: "flex",
                overflowX: "auto", overflowY: "hidden",
                scrollSnapType: "x mandatory",
                WebkitOverflowScrolling: "touch",
                scrollbarWidth: "none", msOverflowStyle: "none",
              } as React.CSSProperties}
            >
              {images.map((img, i) => (
                <div key={i} style={{
                  minWidth: "100vw", width: "100vw", height: "100%",
                  scrollSnapAlign: "start", display: "flex",
                  alignItems: "center", justifyContent: "center",
                  flexShrink: 0, padding: "0 20px", boxSizing: "border-box",
                }}>
                  <img
                    src={img.src} alt={img.alt || `Photo ${i + 1}`}
                    loading={Math.abs(i - (selectedIndex ?? 0)) <= 2 ? "eager" : "lazy"}
                    draggable={false}
                    style={{
                      maxWidth: "calc(100vw - 40px)", maxHeight: "calc(100vh - 140px)",
                      objectFit: "contain", borderRadius: "8px",
                      userSelect: "none", WebkitUserSelect: "none",
                    } as React.CSSProperties}
                  />
                </div>
              ))}
            </div>

            {/* Dots */}
            {images.length > 1 && (
              <div style={{ display: "flex", justifyContent: "center", gap: "6px", padding: "12px 0" }}>
                {images.map((_, i) => (
                  <div key={i} onClick={() => {
                    const el = overlayScrollRef.current;
                    if (el) el.scrollTo({ left: i * el.clientWidth, behavior: "smooth" });
                  }} style={{
                    width: i === currentIndex ? "18px" : "6px", height: "6px",
                    borderRadius: "3px", cursor: "pointer",
                    background: i === currentIndex ? "#c9a84c" : "rgba(255,255,255,0.3)",
                    transition: "all 0.2s ease",
                  }} />
                ))}
              </div>
            )}

            {isDragging && (
              <div style={{
                textAlign: "center", paddingBottom: "8px",
                color: dragY > 120 ? "#c9a84c" : "rgba(255,255,255,0.4)",
                fontSize: "12px", fontFamily: "var(--font-sans, sans-serif)",
              }}>
                {dragY > 120 ? "Release to close" : "↓ Pull down to close"}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

/** Parse a social-photos HTML comment block */
export function parseSocialPhotos(comment: string): SocialPhotoStripProps | null {
  try {
    const jsonStr = comment.replace(/^<!--\s*social-photos\s*\n?/, "").replace(/\n?\s*-->$/, "").trim();
    const data = JSON.parse(jsonStr);
    if (!data.images || !Array.isArray(data.images) || data.images.length === 0) return null;
    return {
      images: data.images.map((src: string) => ({ src })),
      via: data.via || "Unknown",
      platform: data.platform || "x",
      postUrl: data.post_url,
      caption: data.caption,
    };
  } catch {
    return null;
  }
}
