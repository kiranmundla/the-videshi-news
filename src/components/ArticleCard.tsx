import { Link } from "react-router-dom";
import { Article, formatShortDate, readingTime } from "@/lib/articles";

type Variant = "hero" | "featured" | "card" | "long" | "compact";

const FALLBACK_IMG = "/placeholder.svg";

function handleImgError(e: React.SyntheticEvent<HTMLImageElement>) {
  const img = e.currentTarget;
  if (img.src.endsWith(FALLBACK_IMG)) return;
  img.src = FALLBACK_IMG;
}

export default function ArticleCard({
  article,
  variant = "card",
}: {
  article: Article;
  variant?: Variant;
}) {
  const time = readingTime(article.body);
  const href = `/articles/${article.slug}`;

  if (variant === "compact") {
    return (
      <Link to={href} className="group flex gap-4 items-start">
        <img
          src={article.hero_image_url}
          alt={article.title}
          loading="lazy"
          className="w-24 h-24 md:w-28 md:h-28 object-cover flex-shrink-0"
        />
        <div className="min-w-0">
          <p className="smallcaps text-primary mb-1.5">{article.category}</p>
          <h3 className="font-serif text-base md:text-lg leading-snug text-foreground group-hover:text-primary transition-colors">
            {article.title}
          </h3>
        </div>
      </Link>
    );
  }

  if (variant === "long") {
    return (
      <Link
        to={href}
        className="group grid md:grid-cols-2 gap-6 md:gap-10 items-center bg-secondary/60 p-6 md:p-10 border hairline"
      >
        <img
          src={article.hero_image_url}
          alt={article.title}
          loading="lazy"
          className="w-full aspect-[4/3] object-cover"
        />
        <div>
          <p className="smallcaps text-primary mb-3">Long read · {article.category}</p>
          <h2 className="font-serif text-2xl md:text-4xl leading-[1.15] text-foreground group-hover:text-primary transition-colors">
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

  const headlineSize =
    variant === "hero"
      ? "text-[1.75rem] md:text-[2.5rem] lg:text-[3rem] leading-[1.1]"
      : variant === "featured"
      ? "text-[1.35rem] md:text-2xl leading-[1.2]"
      : "text-[1.125rem] md:text-xl leading-snug";

  const aspect = variant === "hero" ? "aspect-[16/9]" : "aspect-[16/10]";

  return (
    <Link to={href} className="group block">
      <div className="overflow-hidden">
        <img
          src={article.hero_image_url}
          alt={article.title}
          loading={variant === "hero" ? "eager" : "lazy"}
          className={`w-full ${aspect} object-cover group-hover:scale-[1.01] transition-transform duration-500`}
        />
      </div>
      <p className="smallcaps text-primary mt-4 mb-2">{article.category}</p>
      <h2 className={`font-serif text-foreground group-hover:text-primary transition-colors ${headlineSize}`}>
        {article.title}
      </h2>
      {variant !== "card" || true ? (
        <p className="mt-3 text-foreground/75 leading-relaxed text-[0.95rem] md:text-base line-clamp-2">
          {article.excerpt}
        </p>
      ) : null}
      <p className="mt-3 text-xs text-muted-foreground">
        {article.author ? `By ${article.author} · ` : ""}{formatShortDate(article.published_at)} · {time} min read
      </p>
    </Link>
  );
}
