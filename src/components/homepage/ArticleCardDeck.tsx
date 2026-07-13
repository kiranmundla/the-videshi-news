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
  news: "India News", "markets-finance": "Markets", sports: "Sports", "nri-world": "World News",
};

export default function ArticleCardDeck() {
  const [cards, setCards] = useState<ArticleCard[]>([]);
  const [openIdx, setOpenIdx] = useState<number | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

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

  if (cards.length === 0) return null;

  return (
    <>
      {/* ── Stories-style strip ── */}
      <section className="vs-section">
        <div className="container">
          <p className="vs-label">Visual Stories</p>
        </div>
        <div className="container">
          <div className="vs-strip">
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

      {/* ── Fullscreen gallery — tap outside card to close ── */}
      {openIdx !== null && (
        <div className="card-gallery-overlay" onClick={close}>

          {/* Top zone — counter */}
          <div className="card-gallery-top" onClick={close}>
            <p className="card-gallery-counter">{currentIndex + 1} / {cards.length}</p>
          </div>

          {/* Middle — scroll-snap cards, stop propagation so tapping card doesn't close */}
          <div
            ref={scrollRef}
            className="card-gallery-scroll"
            onScroll={handleScroll}
            onClick={(e) => e.stopPropagation()}
          >
            {cards.map((card, i) => (
              <div key={card.slug} className="card-gallery-slide">
                <a href={`/articles/${card.slug}`} className="card-gallery-link">
                  <img src={card.card_url} alt={card.headline} className="card-gallery-img"
                    loading={Math.abs(i - currentIndex) <= 2 ? "eager" : "lazy"} draggable={false} />
                </a>
              </div>
            ))}
          </div>

          {/* Bottom zone — dots only (headline already on card) */}
          <div className="card-gallery-bottom" onClick={close}>
            <div className="card-gallery-dots" onClick={(e) => e.stopPropagation()}>
              {cards.map((_, i) => (
                <div key={i}
                  className={`card-gallery-dot${i === currentIndex ? " active" : ""}`}
                  onClick={() => scrollRef.current?.scrollTo({ left: i * (scrollRef.current?.clientWidth ?? 0), behavior: "smooth" })}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
