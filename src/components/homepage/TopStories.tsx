import { Link } from "react-router-dom";
import { Article, readingTime } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";

/* ── constants ──────────────────────────────────────── */

const CATEGORY_COLORS: Record<string, string> = {
  immigration: "#1565C0",
  news: "#C62828",
  sports: "#2E7D32",
  technology: "#4527A0",
  entertainment: "#AD1457",
  "markets-finance": "#E65100",
  "nri-world": "#00695C",
  "lifestyle-health": "#00838F",
};

const CATEGORY_LABELS: Record<string, string> = {
  immigration: "IMMIGRATION",
  news: "NEWS",
  sports: "SPORTS",
  technology: "TECHNOLOGY",
  entertainment: "ENTERTAINMENT",
  "markets-finance": "MARKETS & FINANCE",
  "nri-world": "NRI WORLD",
  "lifestyle-health": "LIFESTYLE & HEALTH",
};

function categoryColor(cat: string) {
  return CATEGORY_COLORS[cat] || "hsl(var(--primary))";
}
function categoryLabel(cat: string) {
  return CATEGORY_LABELS[cat] || cat.replace(/-/g, " ").toUpperCase();
}

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

/* ── Hero card (top story overall) ──────────────────── */

function HeroCard({ article }: { article: Article }) {
  const href = `/articles/${article.slug}`;
  const hasImage = isValidImage(article.hero_image_url);
  const minutes = readingTime(article.body || "");

  return (
    <Link to={href} className="group block">
      <div className="relative overflow-hidden rounded-lg" style={{ background: "#f5f1eb" }}>
        {hasImage && (
          <img
            src={article.hero_image_url}
            alt={article.title}
            loading="eager"
            referrerPolicy="no-referrer"
            className="w-full h-auto object-cover"
            style={{ maxHeight: "340px", objectPosition: "center 20%" }}
          />
        )}
        <div className="p-4 md:p-5">
          <span
            className="inline-block px-2 py-0.5 text-[10px] font-bold tracking-[0.14em] uppercase rounded-sm text-white mb-3"
            style={{ background: categoryColor(article.category) }}
          >
            {categoryLabel(article.category)}
          </span>
          <h2 className="font-serif font-bold text-foreground text-[1.35rem] md:text-[1.6rem] leading-snug group-hover:text-primary transition-colors">
            {article.title}
          </h2>
          {article.excerpt && (
            <p className="text-foreground/60 text-sm mt-2 line-clamp-2">{article.excerpt}</p>
          )}
          <p className="text-foreground/40 text-xs mt-3">
            {minutes} min read · {timeAgo(article.published_at)}
          </p>
        </div>
      </div>
    </Link>
  );
}

/* ── Compact card (remaining categories) ────────────── */

function CompactCard({ article }: { article: Article }) {
  const href = `/articles/${article.slug}`;
  const hasImage = isValidImage(article.hero_image_url);

  return (
    <Link
      to={href}
      className="group flex gap-3 py-3 items-start"
      style={{ borderBottom: "1px solid hsl(var(--rule) / 0.5)" }}
    >
      {hasImage && (
        <img
          src={article.hero_image_url}
          alt={article.title}
          loading="lazy"
          referrerPolicy="no-referrer"
          className="w-[90px] h-[64px] md:w-[110px] md:h-[75px] object-cover rounded flex-shrink-0"
          style={{ objectPosition: "center 20%" }}
        />
      )}
      <div className="flex-1 min-w-0">
        <span
          className="inline-block px-1.5 py-px text-[9px] font-bold tracking-[0.12em] uppercase rounded-sm text-white mb-1.5"
          style={{ background: categoryColor(article.category) }}
        >
          {categoryLabel(article.category)}
        </span>
        <h3 className="font-serif font-bold text-foreground text-[0.95rem] md:text-[1.05rem] leading-snug group-hover:text-primary transition-colors line-clamp-3">
          {article.title}
        </h3>
        <p className="text-foreground/40 text-[11px] mt-1">
          {timeAgo(article.published_at)}
        </p>
      </div>
    </Link>
  );
}

/* ── Main component ─────────────────────────────────── */

export default function TopStories({ articles }: { articles: Article[] }) {
  if (!articles || articles.length === 0) return null;

  // First article = hero, rest = compact list
  const [hero, ...rest] = articles;

  return (
    <section className="mb-10">
      <div
        className="flex items-center justify-between mb-5 pb-3 gap-4"
        style={{ borderBottom: "1px solid hsl(var(--rule))" }}
      >
        <span
          className="font-bold uppercase"
          style={{ fontSize: 11, letterSpacing: "0.12em", color: "#888" }}
        >
          TOP STORIES
        </span>
      </div>

      {/* Hero — top story */}
      <HeroCard article={hero} />

      {/* Compact list — one per remaining category */}
      {rest.length > 0 && (
        <div className="mt-4">
          {rest.map((a) => (
            <CompactCard key={a.id} article={a} />
          ))}
        </div>
      )}
    </section>
  );
}
