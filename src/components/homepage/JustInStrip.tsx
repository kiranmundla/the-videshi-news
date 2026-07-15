import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 2) return "Just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

const CATEGORY_COLORS: Record<string, string> = {
  immigration: "#D32F2F",
  technology: "#4527A0",
  entertainment: "#AD1457",
  news: "#1565C0",
  "markets-finance": "#E65100",
  "nri-world": "#1565C0",
  sports: "#2E7D32",
  "lifestyle-health": "#6A1B9A",
  food: "#BF360C",
  travel: "#00695C",
};

const CATEGORY_LABELS: Record<string, string> = {
  immigration: "Immigration",
  technology: "Tech",
  entertainment: "Entertainment",
  news: "India",
  "markets-finance": "Markets",
  "nri-world": "World",
  sports: "Sports",
  "lifestyle-health": "Lifestyle",
  food: "Food",
  travel: "Travel",
};

export default function JustInStrip({ articles }: { articles: Article[] }) {
  if (!articles || articles.length === 0) return null;

  return (
    <section className="mb-10">
      <div className="container">
        {/* Header */}
        <div className="flex items-center gap-2.5 mb-4">
          <span
            className="inline-block w-2 h-2 rounded-full animate-pulse"
            style={{ background: "#D32F2F" }}
          />
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#D32F2F" }}
          >
            Just In
          </h2>
        </div>

        {/* Horizontal scroll strip */}
        <div
          className="flex gap-4 overflow-x-auto pb-3 scrollbar-thin"
          style={{ scrollSnapType: "x mandatory" }}
        >
          {articles.map((a) => (
            <Link
              key={a.id}
              to={`/articles/${a.slug}`}
              className="group flex-shrink-0 block"
              style={{ width: 260, scrollSnapAlign: "start" }}
            >
              {/* Image */}
              {isValidImage(a.hero_image_url) && (
                <div
                  className="w-full bg-stone-100 overflow-hidden rounded-lg mb-2"
                  style={{ aspectRatio: "16/10" }}
                >
                  <HeroImage
                    src={a.hero_image_url}
                    alt={a.title}
                    loading="lazy"
                    focalX={a.focal_x}
                    focalY={a.focal_y}
                    className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
                  />
                </div>
              )}

              {/* Category + time */}
              <div className="flex items-center gap-2 mb-1">
                <span
                  className="text-[10px] font-bold uppercase tracking-wider"
                  style={{ color: CATEGORY_COLORS[a.category] || "#666" }}
                >
                  {CATEGORY_LABELS[a.category] || a.category}
                </span>
                <span className="text-[10px] text-muted-foreground">
                  {timeAgo(a.published_at)}
                </span>
              </div>

              {/* Headline */}
              <h3
                className="text-[14px] font-semibold leading-snug text-foreground group-hover:text-primary transition-colors"
                style={{
                  display: "-webkit-box",
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}
              >
                {a.title}
              </h3>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
