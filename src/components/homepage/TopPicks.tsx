import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";

interface CategoryPick {
  label: string;
  color: string;
  slug: string;
  articles: Article[];
}

interface Props {
  categories: CategoryPick[];
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

export default function TopPicks({ categories }: Props) {
  const picks = categories
    .map((c) => ({ ...c, article: c.articles[0] }))
    .filter((c) => c.article);

  if (picks.length < 3) return null;

  return (
    <section className="tp-section">
      <div className="tp-header">
        <h2 className="tp-title">Top Stories</h2>
        <span className="tp-subtitle">Top from every section</span>
      </div>
      <div className="tp-grid">
        {picks.map(({ label, color, slug, article }) => {
          const hasImg = isValidImage(article.hero_image_url);
          return (
            <Link
              key={slug}
              to={`/articles/${article.slug}`}
              className="tp-card"
            >
              {hasImg && (
                <img
                  src={article.hero_image_url}
                  alt={article.title}
                  className="tp-card-img"
                  loading="lazy"
                />
              )}
              <div className="tp-card-body">
                <span className="tp-cat" style={{ color }}>{label}</span>
                <h3 className="tp-headline">{article.title}</h3>
                <span className="tp-time">{timeAgo(article.published_at)}</span>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
