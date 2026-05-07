import { Link } from "react-router-dom";
import { Article, formatShortDate, readingTime } from "@/lib/articles";
import HeroImage from "@/components/HeroImage";

type Variant = "hero" | "featured" | "card" | "long" | "compact";

export default function ArticleCard({
  article,
  variant = "card",
  hideCategory = false,
}: {
  article: Article;
  variant?: Variant;
  hideCategory?: boolean;
}) {
  const time = readingTime(article.body);
  const href = `/articles/${article.slug}`;

  if (variant === "compact") {
    return (
      <Link to={href} className="group flex gap-4 items-start">
        <HeroImage
          src={article.hero_image_url}
          alt={article.title}
          loading="lazy"
          category={article.category}
          className="w-20 h-20 object-cover flex-shrink-0"
        />
        <div className="min-w-0">
          <p className="smallcaps text-primary mb-1">{article.category}</p>
          <h3 className="font-serif text-[0.95rem] md:text-base leading-snug text-foreground group-hover:text-primary transition-colors">
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
        <HeroImage
          src={article.hero_image_url}
          alt={article.title}
          loading="lazy"
          category={article.category}
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
      ? "text-[2rem] md:text-[2.75rem] lg:text-[3rem] leading-[1.05]"
      : variant === "featured"
      ? "text-[1.35rem] md:text-[1.5rem] leading-[1.2]"
      : "text-[1.05rem] md:text-[1.125rem] leading-snug";

  const aspect =
    variant === "hero"
      ? "aspect-[16/9]"
      : "aspect-[3/2]";

  return (
    <Link to={href} className="group block">
      <div className="overflow-hidden">
        <HeroImage
          src={article.hero_image_url}
          alt={article.title}
          loading={variant === "hero" ? "eager" : "lazy"}
          category={article.category}
          className={`w-full ${aspect} object-cover object-center group-hover:scale-[1.01] transition-transform duration-500`}
        />
      </div>
      {!hideCategory && <p className="smallcaps text-primary mt-4 mb-2">{article.category}</p>}
      <h2 className={`font-serif text-foreground group-hover:text-primary transition-colors ${hideCategory ? "mt-2" : ""} ${headlineSize}`}>
        {article.title}
      <p className="hidden md:block mt-3 text-foreground/75 leading-relaxed text-base line-clamp-2">
        {article.excerpt}
      </p>
      <p className="mt-3 text-xs text-muted-foreground">
        {article.author ? `By ${article.author} · ` : ""}{formatShortDate(article.published_at)} · {time} min read
      </p>
    </Link>
  );
}
