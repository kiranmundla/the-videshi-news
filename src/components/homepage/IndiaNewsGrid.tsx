import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

interface Props {
  articles: Article[];
  trending: Article[];
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

const CATEGORY_COLORS: Record<string, string> = {
  news: "#C62828",
  politics: "#C62828",
  economy: "#2a7a4b",
  immigration: "#D4A843",
  technology: "#4527A0",
  entertainment: "#AD1457",
  "markets-finance": "#E65100",
  sports: "#2E7D32",
  "nri-world": "#1565C0",
};

function catColor(cat?: string) {
  return CATEGORY_COLORS[cat?.toLowerCase() ?? ""] ?? "#C62828";
}

export default function IndiaNewsGrid({ articles, trending }: Props) {
  if (articles.length === 0) return null;

  return (
    <section className="mb-14">
      <div className="container">
        {/* Section header */}
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #0B1D3A" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            India News
          </h2>
          <Link
            to="/news"
            className="text-[13px] font-semibold text-muted-foreground hover:text-foreground transition-colors"
          >
            See all →
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
          {/* Main grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
            {articles.slice(0, 6).map((a) => {
              const img = isValidImage(a.hero_image_url);
              return (
                <Link
                  key={a.id}
                  to={`/articles/${a.slug}`}
                  className="group block"
                >
                  {img ? (
                    <div className="w-full bg-stone-100 overflow-hidden rounded-lg mb-2" style={{ aspectRatio: "16/10" }}>
                      <HeroImage
                        src={a.hero_image_url}
                        alt={a.title}
                        loading="lazy"
                        className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
                        
                        
                      />
                    </div>
                  ) : (
                    <div className="w-full bg-stone-100 rounded-lg mb-2 flex items-center justify-center text-muted-foreground/30 text-xs" style={{ aspectRatio: "16/10" }}>
                      IMAGE
                    </div>
                  )}
                  <p
                    className="text-[10px] font-bold tracking-[1.2px] uppercase mb-1"
                    style={{ color: catColor(a.category) }}
                  >
                    {a.tags?.[0] ?? a.category?.replace("-", " ")}
                  </p>
                  <h4 className="font-serif text-[15px] font-bold leading-snug group-hover:text-primary transition-colors line-clamp-2">
                    {a.title}
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {timeAgo(a.published_at)}
                  </p>
                </Link>
              );
            })}
          </div>

          {/* Trending sidebar */}
          {trending.length > 0 && (
            <aside className="v2-trending-sidebar">
              <div
                className="pb-3 mb-3"
                style={{ borderBottom: "1px solid hsl(var(--rule))" }}
              >
                <h3
                  className="text-[13px] font-bold tracking-[2px] uppercase"
                  style={{ color: "#0B1D3A" }}
                >
                  Trending
                </h3>
              </div>
              {trending.slice(0, 6).map((a, i) => (
                <Link
                  key={a.id}
                  to={`/articles/${a.slug}`}
                  className="group flex gap-3 py-3 border-b last:border-b-0 transition-colors hover:bg-stone-50 rounded"
                  style={{ borderColor: "hsl(var(--rule))" }}
                >
                  <span
                    className="font-serif text-[24px] font-extrabold leading-none pt-0.5"
                    style={{ color: "#D4A843", flexShrink: 0, width: 28 }}
                  >
                    {i + 1}
                  </span>
                  <div className="min-w-0">
                    <h4 className="font-serif text-[14px] font-bold leading-snug group-hover:text-primary transition-colors line-clamp-2">
                      {a.title}
                    </h4>
                    <span className="text-[11px] text-muted-foreground mt-0.5 block">
                      {a.category?.replace("-", " ")}
                    </span>
                  </div>
                </Link>
              ))}
            </aside>
          )}
        </div>
      </div>
    </section>
  );
}
