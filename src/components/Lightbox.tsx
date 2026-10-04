import { useState, useEffect, useCallback, useRef, type ReactNode } from "react";

/* ── Lightbox ─────────────────────────────────────
   Shared full-screen swipeable lightbox (Snapshots,
   Star Buzz, ...). Scroll-snap paging, dots, counter,
   Esc/arrows, pull-down-to-dismiss.

   `renderSlide(i)` fills the viewport area (image,
   video, or any content). `renderBelow(i)` fills the
   caption/footer area under it. */

interface LightboxProps {
  open: boolean;
  initialIndex: number;
  count: number;
  onClose: () => void;
  renderSlide: (index: number) => ReactNode;
  renderBelow?: (index: number) => ReactNode;
  showCounter?: boolean;
}

export default function Lightbox({
  open,
  initialIndex,
  count,
  onClose,
  renderSlide,
  renderBelow,
  showCounter = true,
}: LightboxProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  // ── Pull-down-to-dismiss state ──
  const [dragY, setDragY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dismissing, setDismissing] = useState(false);
  const touchStartY = useRef<number | null>(null);
  const touchStartX = useRef<number | null>(null);
  const isVerticalGesture = useRef(false);

  const handleOverlayScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const idx = Math.round(el.scrollLeft / el.clientWidth);
    if (idx >= 0 && idx < count) setCurrentIndex(idx);
  }, [count]);

  // When overlay opens, jump to the tapped item instantly
  useEffect(() => {
    if (!open) return;
    setCurrentIndex(initialIndex);
    setDragY(0);
    setIsDragging(false);
    setDismissing(false);
    requestAnimationFrame(() => {
      const el = scrollRef.current;
      if (el) {
        el.scrollTo({ left: initialIndex * el.clientWidth, behavior: "instant" as ScrollBehavior });
      }
    });
    // Lock body scroll while open
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = prev; };
  }, [open, initialIndex]);

  const closeWithDismiss = useCallback(() => {
    setDismissing(true);
    setTimeout(() => {
      onClose();
      setDragY(0);
      setIsDragging(false);
      setDismissing(false);
    }, 200);
  }, [onClose]);

  // Keyboard nav
  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => {
      const el = scrollRef.current;
      if (!el) return;
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") {
        const next = Math.min(currentIndex + 1, count - 1);
        el.scrollTo({ left: next * el.clientWidth, behavior: "smooth" });
      }
      if (e.key === "ArrowLeft") {
        const prev = Math.max(currentIndex - 1, 0);
        el.scrollTo({ left: prev * el.clientWidth, behavior: "smooth" });
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, currentIndex, onClose, count]);

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
      if (Math.abs(dy) > 10 && Math.abs(dy) > dx * 1.2) {
        isVerticalGesture.current = true;
      } else if (dx > 10) return;
    }
    if (!isVerticalGesture.current) return;
    if (dy > 0) { setIsDragging(true); setDragY(dy); }
  }, [isDragging]);

  const handleTouchEnd = useCallback(() => {
    if (isVerticalGesture.current && dragY > 120) {
      closeWithDismiss();
    } else {
      setDragY(0);
      setIsDragging(false);
    }
    touchStartY.current = null;
    touchStartX.current = null;
    isVerticalGesture.current = false;
  }, [dragY, closeWithDismiss]);

  if (!open) return null;

  const dragProgress = Math.min(dragY / 300, 1);
  const overlayOpacity = dismissing ? 0 : 1 - dragProgress * 0.6;
  const overlayScale = dismissing ? 0.9 : 1 - dragProgress * 0.1;
  const overlayTranslateY = dismissing ? 100 : dragY;

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        position: "fixed",
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: `rgba(0,0,0,${0.95 * overlayOpacity})`,
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        animation: dismissing ? "none" : "videshiLightboxFadeIn 0.15s ease-out",
        transition: isDragging ? "none" : "background-color 0.2s ease",
      }}
    >
      <style>{`
        @keyframes videshiLightboxFadeIn { from { opacity: 0; } to { opacity: 1; } }
        .videshi-lightbox-scroll::-webkit-scrollbar { display: none; }
      `}</style>

      {/* Close button */}
      <button
        onClick={onClose}
        aria-label="Close"
        style={{
          position: "absolute", top: 12, right: 16, zIndex: 10000,
          background: "rgba(255,255,255,0.15)", border: "none", color: "#fff",
          width: 36, height: 36, borderRadius: "50%", cursor: "pointer",
          fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center",
        }}
      >×</button>

      {/* Inner content — moves with vertical drag */}
      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        transform: `translateY(${overlayTranslateY}px) scale(${overlayScale})`,
        opacity: overlayOpacity,
        transition: isDragging ? "none" : "transform 0.25s cubic-bezier(0.2,0,0,1), opacity 0.2s ease",
        willChange: "transform, opacity",
        minHeight: 0,
      }}>
        {/* Counter */}
        {showCounter && (
          <p style={{
            color: "rgba(255,255,255,0.5)", fontSize: "13px",
            fontFamily: "var(--font-sans, sans-serif)", textAlign: "center",
            padding: "16px 0 8px", margin: 0, userSelect: "none",
          }}>
            {currentIndex + 1} / {count}
          </p>
        )}

        {/* Scroll-snap container */}
        <div
          ref={scrollRef}
          className="videshi-lightbox-scroll"
          onScroll={handleOverlayScroll}
          style={{
            flex: 1, display: "flex", minHeight: 0,
            overflowX: "auto", overflowY: "hidden",
            scrollSnapType: "x mandatory",
            WebkitOverflowScrolling: "touch",
            scrollbarWidth: "none", msOverflowStyle: "none",
          } as React.CSSProperties}
        >
          {Array.from({ length: count }, (_, i) => (
            <div key={i} style={{
              minWidth: "100vw", width: "100vw",
              scrollSnapAlign: "start", display: "flex",
              alignItems: "center", justifyContent: "center",
              flexShrink: 0, padding: "0 20px", boxSizing: "border-box",
            }}>
              {renderSlide(i)}
            </div>
          ))}
        </div>

        {/* Below-viewport content (caption, actions, ...) */}
        {renderBelow && (
          <div style={{ maxWidth: "600px", alignSelf: "center", width: "100%" }}>
            {renderBelow(currentIndex)}
          </div>
        )}

        {/* Dot indicators */}
        <div style={{ display: "flex", justifyContent: "center", gap: "6px", padding: "12px 0" }}>
          {Array.from({ length: count }, (_, i) => (
            <div key={i} onClick={() => {
              const el = scrollRef.current;
              if (el) el.scrollTo({ left: i * el.clientWidth, behavior: "smooth" });
            }} style={{
              width: i === currentIndex ? "18px" : "6px", height: "6px",
              borderRadius: "3px", cursor: "pointer",
              background: i === currentIndex ? "#c9a84c" : "rgba(255,255,255,0.3)",
              transition: "all 0.2s ease",
            }} />
          ))}
        </div>

        {/* Pull-down hint */}
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
  );
}
