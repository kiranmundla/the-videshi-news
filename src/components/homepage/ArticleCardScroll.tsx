import { useEffect, useState } from "react";
import ScrollWrap from "./ScrollWrap";

interface ArticleCard {
  slug: string;
  headline: string;
  category: string;
  card_url: string;
  published_at: string;
}

interface ArticleCardScrollProps {
  category: string;
  label?: string;
}

export default function ArticleCardScroll({
  category,
  label,
}: ArticleCardScrollProps) {
  const [cards, setCards] = useState<ArticleCard[]>([]);

  useEffect(() => {
    fetch("/data/article-cards.json")
      .then((r) => r.json())
      .then((data: ArticleCard[]) => {
        const filtered = data.filter((c) => c.category === category);
        setCards(filtered);
      })
      .catch(() => {});
  }, [category]);

  if (cards.length === 0) return null;

  return (
    <div className="article-card-scroll">
      {label && (
        <h3 className="article-card-scroll-label">{label}</h3>
      )}
      <ScrollWrap scrollAmount={300} arrowVariant="dark">
        {cards.map((card) => (
          <a
            key={card.slug}
            href={`/articles/${card.slug}`}
            className="article-card-item"
            title={card.headline}
          >
            <img
              src={card.card_url}
              alt={card.headline}
              className="article-card-img"
              loading="lazy"
            />
          </a>
        ))}
      </ScrollWrap>
    </div>
  );
}
