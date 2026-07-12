import { useEffect, useState, useCallback } from "react";

interface ArticleCard {
  slug: string;
  headline: string;
  category: string;
  card_url: string;
  published_at: string;
}

export default function ArticleCardDeck() {
  const [cards, setCards] = useState<ArticleCard[]>([]);
  const [idx, setIdx] = useState(0);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetch("/data/article-cards.json")
      .then((r) => r.json())
      .then((data: ArticleCard[]) => setCards(data))
      .catch(() => {});
  }, []);

  const next = useCallback(() => {
    if (cards.length === 0) return;
    setIdx((i) => (i + 1) % cards.length);
  }, [cards.length]);

  const prev = useCallback(() => {
    if (cards.length === 0) return;
    setIdx((i) => (i - 1 + cards.length) % cards.length);
  }, [cards.length]);

  /* swipe support */
  const [touchX, setTouchX] = useState<number | null>(null);
  const onTouchStart = (e: React.TouchEvent) =>
    setTouchX(e.touches[0].clientX);
  const onTouchEnd = (e: React.TouchEvent) => {
    if (touchX === null) return;
    const diff = e.changedTouches[0].clientX - touchX;
    if (Math.abs(diff) > 40) {
      diff < 0 ? next() : prev();
    }
    setTouchX(null);
  };

  const handleCardClick = (card: ArticleCard) => {
    if (expanded) {
      window.location.href = `/articles/${card.slug}`;
    } else {
      setExpanded(true);
    }
  };

  const handleOverlayClick = () => setExpanded(false);

  if (cards.length === 0) return null;

  /* show up to 3 stacked cards behind the front one */
  const visibleCount = Math.min(3, cards.length);
  const stack = Array.from({ length: visibleCount }, (_, i) => {
    const ci = (idx + i) % cards.length;
    return { ...cards[ci], _offset: i };
  });

  return (
    <>
      <div
        className="card-deck-wrap"
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
      >
        <div className="card-deck-stack">
          {stack
            .slice()
            .reverse()
            .map((card) => (
              <div
                key={card.slug + card._offset}
                className="card-deck-card"
                style={{
                  transform: `translateX(${card._offset * 8}px) translateY(${card._offset * -4}px) scale(${1 - card._offset * 0.04})`,
                  zIndex: visibleCount - card._offset,
                  opacity: card._offset === 0 ? 1 : 0.6,
                }}
                onClick={() =>
                  card._offset === 0 && handleCardClick(card)
                }
              >
                <img
                  src={card.card_url}
                  alt={card.headline}
                  className="card-deck-img"
                  draggable={false}
                />
              </div>
            ))}
        </div>
        <div className="card-deck-nav">
          <button className="card-deck-arrow" onClick={prev} aria-label="Previous card">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6" /></svg>
          </button>
          <span className="card-deck-counter">
            {idx + 1} / {cards.length}
          </span>
          <button className="card-deck-arrow" onClick={next} aria-label="Next card">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 6 15 12 9 18" /></svg>
          </button>
        </div>
      </div>

      {/* expanded overlay */}
      {expanded && (
        <div className="card-deck-overlay" onClick={handleOverlayClick}>
          <div
            className="card-deck-expanded"
            onClick={(e) => {
              e.stopPropagation();
              window.location.href = `/articles/${cards[idx].slug}`;
            }}
          >
            <img
              src={cards[idx].card_url}
              alt={cards[idx].headline}
              className="card-deck-expanded-img"
            />
            <p className="card-deck-expanded-hint">Tap to read article</p>
          </div>
        </div>
      )}
    </>
  );
}
