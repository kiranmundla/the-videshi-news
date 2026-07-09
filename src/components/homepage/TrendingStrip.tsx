import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

interface Props {
  articles: Article[];
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

export default function TrendingStrip({ articles }: Props) {
  if (articles.length === 0) return null;
  const items = articles.slice(0, 6);

  return (
    <div className="v2-trending-strip">
      <div className="container">
        <div className="v2-trending-strip-inner">
          {items.map((a, i) => (
            <Link
              key={a.id}
              to={`/articles/${a.slug}`}
              className="flex items-start gap-2 shrink-0"
              style={{ minWidth: 260 }}
            >
              <span
                className="font-serif text-[22px] font-extrabold leading-none"
                style={{ color: "#D4A843" }}
              >
                {i + 1}
              </span>
              <span
                className="text-[13px] font-semibold leading-snug line-clamp-2"
                style={{ color: "#0B1D3A" }}
              >
                {a.title}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
