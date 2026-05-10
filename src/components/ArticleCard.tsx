import { Link } from "react-router-dom";
import { Article, formatShortDate, readingTime } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

type Variant = "hero" | "featured" | "card" | "long" | "compact";

const ACCENT: Record<string, string> = {
  news: "hsl(var(--primary))",
  politics: "hsl(var(--primary))",
  economy: "#2a7a4b",
  "markets-finance": "#2a7a4b",
  immigration: "#6b4fa0",
  "nri-world": "#6b4fa0",
  diaspora: "#6b4fa0",
  tech: "#1a6fa8",
  technology: "#1a6fa8",
  culture: "#8a6a1a",
  "lifestyle-health": "#8a6a1a",
};

function accentFor(category?: string): string {
  if (!category) return "hsl(var(--primary))";
  return ACCENT[category.toLowerCase()] ?? "hsl(var(--primary))";
}

export default function ArticleCard({
  article,
  variant = "card",
  hideCategory = false,
  featured = false,
}: {
  article: Article;
  variant?: Variant;
  hideCategory?: boolean;
  featured?: boolean;
}) {
  const time = readingTime(article.body);
  const href = `/articles/${article.slug}`;
  const featureLabel = featured ? "FEATURED" : null;
  const hasImage = isValidImage(article.hero_image_url);
  const accent = accentFor(article.category);
  const saveScroll = () => {
    sessionStorage.setItem("homeScrollY", window.scrollY.toString());
  };

  // ===================== COMPACT =====================
  if (variant === "compact") {
    return (
      <Link to={href} className="group flex gap-4 items-start">
        {hasImage && (
          <HeroImage
            src={article.hero_image_url}
            alt={article.title}
            loading="lazy"
            className="w-20 h-20 object-cover object-[center_25%] flex-shrink-0"
          />
        )}
        <div
          className={`min-w-0 ${hasImage ? "" : "border-l-2 pl-3"}`}
          style={hasImage ? undefined : { borderColor: accent }}
        >
          <p className="smallcaps text-primary mb-1">
            {featureLabel && (
              <span className="bg-primary text-primary-foreground px-1 py-0.5 mr-1.5 tracking-wider">
                {featureLabel}
              </span>
            )}
            {article.category}
          </p>
          <h3 className="font-serif font-semibold text-[0.95rem] md:text-base leading-snug text-foreground group-hover:text-primary transition-colors">
            {article.title}
          </h3>
        </div>
      </Link>
    );
  }

  // ===================== LONG =====================
  if (variant === "long") {
    if (!hasImage) {
      return (
        <Link
          to={href}
          className="group block bg-secondary/60 p-6 md:p-10 border hairline border-l-2"
          style={{ borderLeftColor: accent }}
        >
          <p className="smallcaps text-primary mb-3">
            {featureLabel ? "Feature" : "Long read"} · {article.category}
          </p>
          <h2 className="font-serif font-bold text-[1.75rem] md:text-[2.5rem] leading-[1.15] text-foreground group-hover:text-primary transition-colors">
            {article.title}
          </h2>
          {article.excerpt && (
            <p className="mt-4 text-foreground/75 leading-relaxed text-[0.98rem] line-clamp-3">
              {article.excerpt}
            </p>
          )}
          <p className="mt-5 text-xs text-muted-foreground">
            {article.author ? `By ${article.author} · ` : ""}{time} min read
          </p>
        </Link>
      );
    }
    return (
      <Link
        to={href}
        className="group grid md:grid-cols-2 gap-6 md:gap-10 items-center bg-secondary/60 p-6 md:p-10 border hairline"
      >
        <figure>
          <div className="w-full aspect-[16/9] overflow-hidden">
            <HeroImage
              src={article.hero_image_url}
              alt={article.title}
              loading="lazy"
              className="w-full h-full object-cover object-[center_25%]"
            />
          </div>
        </figure>
        <div>
          <p className="smallcaps text-primary mb-3">
            {featureLabel ? "Feature" : "Long read"} · {article.category}
          </p>
          <h2 className="font-serif font-bold text-2xl md:text-4xl leading-[1.15] text-foreground group-hover:text-primary transition-colors">
            {article.title}
          </h2>
          <p className="mt-4 text-foreground/75 leading-relaxed text-[0.98rem]">
            {article.excerpt}
          </p>
          <p className="mt-5 text-xs text-muted-foreground">
            {article.author ? `By ${article.author} · ` : ""}{time} min read
          </p>
        </div>
      </Link>
    );
  }

  // ===================== HERO / FEATURED / CARD =====================
  // Headline sizes (text-first cards bump up ~20%)
  const headlineSizeWithImage =
    variant === "hero"
      ? "text-[2rem] md:text-[2.75rem] lg:text-[3rem] leading-[1.05]"
      : variant === "featured"
      ? "text-[1.35rem] md:text-[1.5rem] leading-[1.2]"
      : "text-[1.05rem] md:text-[1.125rem] leading-snug";

  const headlineSizeNoImage =
    variant === "hero"
      ? "text-[2.4rem] md:text-[3.25rem] lg:text-[3.6rem] leading-[1.05]"
      : variant === "featured"
      ? "text-[1.6rem] md:text-[1.8rem] leading-[1.2]"
      : "text-[1.25rem] md:text-[1.35rem] leading-snug";

  if (!hasImage) {
    // Text-first card — denser layout with uniform red left accent bar.
    const isLarge = variant === "hero" || variant === "featured";
    const RED = "#C0392B";
    return (
      <Link
        to={href}
        className={`group block bg-secondary/50 border-l-4 hairline border-t border-r border-b ${
          isLarge ? "p-6 md:p-8" : "p-4"
        } md:max-h-none max-h-[160px] overflow-hidden`}
        style={{ borderLeftColor: RED }}
      >
        {!hideCategory && (
          <p className="smallcaps mb-2" style={{ color: RED }}>
            {featureLabel && (
              <span className="bg-primary text-primary-foreground px-1.5 py-0.5 mr-2 tracking-wider">
                {featureLabel}
              </span>
            )}
            {article.category}
          </p>
        )}
        <h2
          className={`font-serif font-bold text-foreground group-hover:text-primary transition-colors ${
            isLarge ? headlineSizeNoImage : "text-[18px] leading-snug"
          }`}
        >
          {article.title}
        </h2>
        {article.excerpt && (
          <p
            className={`mt-3 text-foreground/70 leading-relaxed hidden md:block ${
              isLarge ? "text-base md:text-lg line-clamp-3" : "text-[0.95rem] line-clamp-3"
            }`}
          >
            {article.excerpt}
          </p>
        )}
        <p className="mt-3 text-xs text-muted-foreground">
          {article.author ? `By ${article.author} · ` : ""}
          {formatShortDate(article.published_at)} · {time} min read
        </p>
      </Link>
    );
  }

  return (
    <Link to={href} className="group block">
      <figure className="w-full">
        <div className="w-full aspect-[16/9] overflow-hidden">
          <HeroImage
            src={article.hero_image_url}
            alt={article.title}
            loading={variant === "hero" ? "eager" : "lazy"}
            className="w-full h-full object-cover object-[center_25%] group-hover:scale-[1.01] transition-transform duration-500"
          />
        </div>
      </figure>
      {!hideCategory && (
        <p className="smallcaps text-primary mt-4 mb-2">
          {featureLabel && (
            <span className="bg-primary text-primary-foreground px-1.5 py-0.5 mr-2 tracking-wider">
              {featureLabel}
            </span>
          )}
          {article.category}
        </p>
      )}
      <h2
        className={`font-serif font-bold text-foreground group-hover:text-primary transition-colors ${
          hideCategory ? "mt-2" : ""
        } ${headlineSizeWithImage}`}
      >
        {article.title}
      </h2>
      <p className="mt-3 text-xs text-muted-foreground">
        {article.author ? `By ${article.author} · ` : ""}
        {formatShortDate(article.published_at)} · {time} min read
      </p>
    </Link>
  );
}
