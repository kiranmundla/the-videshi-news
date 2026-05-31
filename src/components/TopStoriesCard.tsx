import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";
import { optimizeImageUrl, IMAGE_SIZES } from "@/lib/imageUrl";

const ACCENT: Record<string, string> = {
  news: "hsl(var(--primary))",
  politics: "hsl(var(--primary))",
  economy: "#2a7a4b",
  "markets-finance": "#2a7a4b",
  immigration: "#6b4fa0",
  "nri-world": "#6b4fa0",
  tech: "#1a6fa8",
  technology: "#1a6fa8",
  culture: "#8a6a1a",
  "lifestyle-health": "#8a6a1a",
};

function accentFor(category?: string): string {
  if (!category) return "hsl(var(--primary))";
  return ACCENT[category.toLowerCase()] ?? "hsl(var(--primary))";
}

export default function TopStoriesCard({
  article,
  size = "md",
}: {
  article: Article;
  size?: "lg" | "md";
}) {
  const href = `/articles/${article.slug}`;
  const hasImage = isValidImage(article.hero_image_url);
  const accent = accentFor(article.category);
  const headlineSize =
    size === "lg"
      ? "text-[20px] md:text-[26px]"
      : "text-[17px] md:text-[19px]";

  if (hasImage) {
    return (
      <Link
        to={href}
        className="group flex flex-col bg-card border border-rule h-full overflow-hidden"
      >
        <div className="w-full aspect-[16/9] overflow-hidden bg-muted">
          <img
            src={optimizeImageUrl(article.hero_image_url, IMAGE_SIZES.card)}
            alt={article.title}
            loading="lazy"
            decoding="async"
            referrerPolicy="no-referrer"
            className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-500"
            width="400"
            height="225"
            style={{ objectPosition: "center" }}
          />
        </div>
        <div className="flex-1 flex flex-col p-4">
          <p className="smallcaps text-primary mb-2">{article.category}</p>
          <h3
            className={`font-display font-bold leading-snug text-foreground group-hover:text-primary transition-colors ${headlineSize}`}
            style={{ fontWeight: 700 }}
          >
            {article.title}
          </h3>
          {article.excerpt && (
            <p className="font-body-serif mt-2 text-foreground/70 text-sm line-clamp-2">
              {article.excerpt}
            </p>
          )}
        </div>
      </Link>
    );
  }

  return (
    <Link
      to={href}
      className="group flex flex-col justify-center border-l-4 p-5 md:p-6 h-full"
      style={{ background: "#FAFAFA", borderLeftColor: accent, minHeight: 220 }}
    >
      <p className="smallcaps mb-2" style={{ color: accent }}>
        {article.category}
      </p>
      <h3
        className="font-display font-bold leading-snug text-foreground group-hover:text-primary transition-colors text-[22px] md:text-[24px]"
        style={{ fontWeight: 700 }}
      >
        {article.title}
      </h3>
      {article.excerpt && (
        <p className="font-body-serif mt-2 text-foreground/70 text-sm line-clamp-3">
          {article.excerpt}
        </p>
      )}
    </Link>
  );
}
