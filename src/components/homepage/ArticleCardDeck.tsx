import { useEffect, useState, useCallback, useRef } from "react";

interface ArticleCard {
  slug: string;
  headline: string;
  category: string;
  card_url: string;
  published_at: string;
}

const CAT_LABELS: Record<string, string> = {
  immigration: "Immigration", technology: "Technology", entertainment: "Entertainment",
  news: "News", "markets-finance": "Markets", sports: "Sports", "nri-world": "NRI World",
};

export default function ArticleCardDeck() {
  const [cards, setCards] = useState<ArticleCard[]>([]);
  const [openIdx, setOpenIdx] = useState<number | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const stripRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/data/article-cards.json")
      .then((r) => r.json())
      .then((data: ArticleCard[]) => setCards(data))
      .catch(() => {});
  }, []);

  const openAt = useCallback((i: number) => { setCurrentIndex(i); setOpenIdx(i); }, []);
  const close = useCallback(() => setOpenIdx(null), []);

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const idx = Math.round(el.scrollLeft / el.clientWidth);
    if (idx >= 0 && idx < cards.length) setCurrentIndex(idx);
  }, [cards.length]);

  useEffect(() => {
    if (openIdx === null) return;
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ left: openIdx * (scrollRef.current?.clientWidth ?? 0), behavior: "instant" as ScrollBehavior });
    });
  }, [openIdx]);

  useEffect(() => {
    if (openIdx === null) return;
    const handle = (e: KeyboardEvent) => {
      const el = scrollRef.current;
      if (!el) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowRight") el.scrollTo({ left: (currentIndex + 1) * el.clientWidth, behavior: "smooth" });
      if (e.key === "ArrowLeft") el.scrollTo({ left: (currentIndex - 1) * el.clientWidth, behavior: "smooth" });
    };
    window.addEventListener("keydown", handle);
    return () => window.removeEventListener("keydown", handle);
  }, [openIdx, currentIndex, close]);

  /* pull-down-to-dismiss */
  const [dragY, setDragY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dismissing, setDismissing] = useState(false);
  const touchStartY = useRef<number | null>(null);
  const touchStartX = useRef<number | null>(null);
  const isVertical = useRef(false);

  const closeWithDismiss = useCallback(() => {
    setDismissing(true);
    setTimeout(() => { setOpenIdx(null); setDragY(0); setIsDragging(false); setDismissing(false); }, 200);
  }, []);

  const onTS = useCallback((e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
    touchStartX.current = e.touches[0].clientX;
    isVertical.current = false;
  }, []);
  const onTM = useCallback((e: React.TouchEvent) => {
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
  const onTE = useCallback(() => {
    if (isVertical.current && dragY > 120) closeWithDismiss();
    else { setDragY(0); setIsDragging(false); }
    touchStartY.current = null; touchStartX.current = null; isVertical.current = false;
  }, [dragY, closeWithDismiss]);

  const dp = Math.min(dragY / 300, 1);
  const oOp = dismissing ? 0 : 1 - dp * 0.6;
  const oSc = dismissing ? 0.9 : 1 - dp * 0.1;
  const oTy = dismissing ? 100 : dragY;

  if (cards.length === 0) return null;

  return (
    <>
      {/* ── Stories-style strip ── */}
      <section className="vs-section">
        <div className="container">
          <p className="vs-label">Visual Stories</p>
        </div>
        <div className="container">
          <div ref={stripRef} className="vs-strip">
            {cards.map((card, i) => (
              <div key={card.slug} className="vs-thumb" onClick={() => openAt(i)}>
                <div className="vs-thumb-ring">
                  <img src={card.card_url} alt={card.headline} className="vs-thumb-img" loading={i < 6 ? "eager" : "lazy"} draggable={false} />
                </div>
                <span className="vs-thumb-cat">{CAT_LABELS[card.category] ?? card.category}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Fullscreen gallery ── */}
      {openIdx !== null && (
        <div
          className="card-gallery-overlay"
          onTouchStart={onTS} onTouchMove={onTM} onTouchEnd={onTE}
          style={{ backgroundColor: `rgba(0,0,0,${0.95 * oOp})`, animation: dismissing ? "none" : "cardFadeIn 0.15s ease-out" }}
        >
          <style>{`
            @keyframes cardFadeIn { from { opacity: 0; } to { opacity: 1; } }
            .card-gallery-scroll::-webkit-scrollbar { display: none; }
          `}</style>

          <button className="card-gallery-close" onClick={close}>×</button>

          <div style={{
            flex: 1, display: "flex", flexDirection: "column",
            transform: `translateY(${oTy}px) scale(${oSc})`, opacity: oOp,
            transition: isDragging ? "none" : "transform 0.25s cubic-bezier(0.2,0,0,1), opacity 0.2s ease",
          }}>
            <p className="card-gallery-counter">{currentIndex + 1} / {cards.length}</p>

            <div ref={scrollRef} className="card-gallery-scroll" onScroll={handleScroll}>
              {cards.map((card, i) => (
                <div key={card.slug} className="card-gallery-slide">
                  <a href={`/articles/${card.slug}`} className="card-gallery-link">
                    <img src={card.card_url} alt={card.headline} className="card-gallery-img"
                      loading={Math.abs(i - currentIndex) <= 2 ? "eager" : "lazy"} draggable={false} />
                  </a>
                </div>
              ))}
            </div>

            <p className="card-gallery-caption">{cards[currentIndex]?.headline}</p>
            <p className="card-gallery-category">
              {CAT_LABELS[cards[currentIndex]?.category] ?? cards[currentIndex]?.category} · Tap to read
            </p>

            <div className="card-gallery-dots">
              {cards.map((_, i) => (
                <div key={i}
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
