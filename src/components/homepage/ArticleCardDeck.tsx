import { useEffect, useState, useCallback, useRef } from "react";

interface ArticleCard {
  slug: string;
  headline: string;
  category: string;
  card_url: string;
  published_at: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  immigration: "Immigration",
  technology: "Technology",
  entertainment: "Entertainment",
  news: "News",
  "markets-finance": "Markets",
  sports: "Sports",
  "nri-world": "NRI World",
};

export default function ArticleCardDeck() {
  const [cards, setCards] = useState<ArticleCard[]>([]);
  const [open, setOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/data/article-cards.json")
      .then((r) => r.json())
      .then((data: ArticleCard[]) => setCards(data))
      .catch(() => {});
  }, []);

  const openDeck = useCallback(() => { setCurrentIndex(0); setOpen(true); }, []);
  const closeDeck = useCallback(() => setOpen(false), []);

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const idx = Math.round(el.scrollLeft / el.clientWidth);
    if (idx >= 0 && idx < cards.length) setCurrentIndex(idx);
  }, [cards.length]);

  useEffect(() => {
    if (!open) return;
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ left: 0, behavior: "instant" as ScrollBehavior });
    });
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handle = (e: KeyboardEvent) => {
      const el = scrollRef.current;
      if (!el) return;
      if (e.key === "Escape") closeDeck();
      if (e.key === "ArrowRight") el.scrollTo({ left: (currentIndex + 1) * el.clientWidth, behavior: "smooth" });
      if (e.key === "ArrowLeft") el.scrollTo({ left: (currentIndex - 1) * el.clientWidth, behavior: "smooth" });
    };
    window.addEventListener("keydown", handle);
    return () => window.removeEventListener("keydown", handle);
  }, [open, currentIndex, closeDeck]);

  /* pull-down-to-dismiss */
  const [dragY, setDragY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dismissing, setDismissing] = useState(false);
  const touchStartY = useRef<number | null>(null);
  const touchStartX = useRef<number | null>(null);
  const isVertical = useRef(false);

  const closeWithDismiss = useCallback(() => {
    setDismissing(true);
    setTimeout(() => { setOpen(false); setDragY(0); setIsDragging(false); setDismissing(false); }, 200);
  }, []);

  const onTouchStart = useCallback((e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
    touchStartX.current = e.touches[0].clientX;
    isVertical.current = false;
  }, []);
  const onTouchMove = useCallback((e: React.TouchEvent) => {
    if (touchStartY.current === null || touchStartX.current === null) return;
    const dy = e.touches[0].clientY - touchStartY.current;
    const dx = Math.abs(e.touches[0].clientX - touchStartX.current);
    if (!isVertical.current && !isDragging) {
      if (Math.abs(dy) > 10 && Math.abs(dy) > dx * 1.2) isVertical.current = true;
      else if (dx > 10) return;
    }
    if (!isVertical.current) return;
    if (dy > 0) { setIsDragging(true); setDragY(dy); }
  }, [isDragging]);
  const onTouchEnd = useCallback(() => {
    if (isVertical.current && dragY > 120) closeWithDismiss();
    else { setDragY(0); setIsDragging(false); }
    touchStartY.current = null; touchStartX.current = null; isVertical.current = false;
  }, [dragY, closeWithDismiss]);

  const dragProgress = Math.min(dragY / 300, 1);
  const overlayOpacity = dismissing ? 0 : 1 - dragProgress * 0.6;
  const overlayScale = dismissing ? 0.9 : 1 - dragProgress * 0.1;
  const overlayTranslateY = dismissing ? 100 : dragY;

  if (cards.length === 0) return null;

  const stackCount = Math.min(3, cards.length);

  return (
    <>
      {/* ── Mini deck on page ── */}
      <section className="card-deck-section">
        <div className="container">
          <p className="card-deck-label">Visual Stories</p>
        </div>
        <div className="container" style={{ position: "relative" }}>
          <div className="card-deck-strip">
            {/* Stacked deck thumbnail */}
            <div className="card-deck-stack-wrap" onClick={openDeck}>
              <div className="card-deck-stack">
                {Array.from({ length: stackCount }, (_, i) => (
                  <div
                    key={i}
                    className="card-deck-card"
                    style={{
                      transform: `translateX(${i * 6}px) translateY(${i * -3}px) scale(${1 - i * 0.03})`,
                      zIndex: stackCount - i,
                      opacity: i === 0 ? 1 : 0.5,
                    }}
                  >
                    <img src={cards[i].card_url} alt="" className="card-deck-img" draggable={false} />
                  </div>
                ))}
              </div>
              <span className="card-deck-badge">{cards.length}</span>
            </div>

            {/* Preview strip of remaining cards — horizontal scroll */}
            <div className="card-deck-preview-strip">
              {cards.slice(1, 8).map((card) => (
                <div key={card.slug} className="card-deck-preview-thumb" onClick={openDeck}>
                  <img src={card.card_url} alt={card.headline} className="card-deck-preview-img" loading="lazy" draggable={false} />
                </div>
              ))}
              <div className="card-deck-preview-more" onClick={openDeck}>
                +{Math.max(0, cards.length - 8)} more
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Fullscreen gallery (Snapshots-style) ── */}
      {open && (
        <div
          className="card-gallery-overlay"
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
          style={{
            backgroundColor: `rgba(0,0,0,${0.95 * overlayOpacity})`,
            animation: dismissing ? "none" : "cardFadeIn 0.15s ease-out",
          }}
        >
          <style>{`
            @keyframes cardFadeIn { from { opacity: 0; } to { opacity: 1; } }
            .card-gallery-scroll::-webkit-scrollbar { display: none; }
          `}</style>

          <button className="card-gallery-close" onClick={closeDeck}>×</button>

          <div style={{
            flex: 1, display: "flex", flexDirection: "column",
            transform: `translateY(${overlayTranslateY}px) scale(${overlayScale})`,
            opacity: overlayOpacity,
            transition: isDragging ? "none" : "transform 0.25s cubic-bezier(0.2,0,0,1), opacity 0.2s ease",
          }}>
            <p className="card-gallery-counter">{currentIndex + 1} / {cards.length}</p>

            <div ref={scrollRef} className="card-gallery-scroll" onScroll={handleScroll}>
              {cards.map((card, i) => (
                <div key={card.slug} className="card-gallery-slide">
                  <a href={`/articles/${card.slug}`} className="card-gallery-link">
                    <img
                      src={card.card_url}
                      alt={card.headline}
                      className="card-gallery-img"
                      loading={Math.abs(i - currentIndex) <= 2 ? "eager" : "lazy"}
                      draggable={false}
                    />
                  </a>
                </div>
              ))}
            </div>

            <p className="card-gallery-caption">{cards[currentIndex]?.headline}</p>
            <p className="card-gallery-category">
              {CATEGORY_LABELS[cards[currentIndex]?.category] ?? cards[currentIndex]?.category}
              {" · Tap to read"}
            </p>

            <div className="card-gallery-dots">
              {cards.map((_, i) => (
                <div
                  key={i}
                  className={`card-gallery-dot${i === currentIndex ? " active" : ""}`}
                  onClick={() => scrollRef.current?.scrollTo({ left: i * (scrollRef.current?.clientWidth ?? 0), behavior: "smooth" })}
                />
              ))}
            </div>

            {isDragging && (
              <div style={{ textAlign: "center", paddingBottom: 8, color: dragY > 120 ? "#c9a84c" : "rgba(255,255,255,0.4)", fontSize: 12, fontFamily: "var(--font-sans, sans-serif)" }}>
                {dragY > 120 ? "Release to close" : "↓ Pull down to close"}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
