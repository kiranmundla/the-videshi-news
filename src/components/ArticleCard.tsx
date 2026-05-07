import { Link } from "react-router-dom";
import { Article, formatShortDate, readingTime, imageCaption } from "@/lib/articles";
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
  const isFeature = article.article_type === "feature";
  const featureLabel = isFeature ? "FEATURE" : null;
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

  if (variant === "long") {
    return (
      <Link
        to={href}
        className="group grid md:grid-cols-2 gap-6 md:gap-10 items-center bg-secondary/60 p-6 md:p-10 border hairline"
      >
        <figure>
          <HeroImage
            src={article.hero_image_url}
            alt={article.title}
            loading="lazy"
            category={article.category}
            className="w-full aspect-[16/9] object-cover object-center-top"
          />
          <figcaption className="mt-2 text-xs italic text-muted-foreground">
            {imageCaption(article.title)}
          </figcaption>
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

  const headlineSize =
    variant === "hero"
      ? "text-[2rem] md:text-[2.75rem] lg:text-[3rem] leading-[1.05]"
      : variant === "featured"
      ? "text-[1.35rem] md:text-[1.5rem] leading-[1.2]"
      : "text-[1.05rem] md:text-[1.125rem] leading-snug";

  const aspect = "aspect-[16/9]";

  return (
    <Link to={href} className="group block">
      <figure className="overflow-hidden">
        <HeroImage
          src={article.hero_image_url}
          alt={article.title}
          loading={variant === "hero" ? "eager" : "lazy"}
          category={article.category}
          className={`w-full ${aspect} object-cover object-center-top group-hover:scale-[1.01] transition-transform duration-500`}
        />
        <figcaption className="mt-2 text-xs italic text-muted-foreground">
          {imageCaption(article.title)}
        </figcaption>
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
      <h2 className={`font-serif font-bold text-foreground group-hover:text-primary transition-colors ${hideCategory ? "mt-2" : ""} ${headlineSize}`}>
        {article.title}
      </h2>
      <p className="hidden mt-3 text-foreground/75 leading-relaxed text-base line-clamp-2">
        {article.excerpt}
      </p>
      <p className="mt-3 text-xs text-muted-foreground">
        {article.author ? `By ${article.author} · ` : ""}{formatShortDate(article.published_at)} · {time} min read
      </p>
    </Link>
  );
}
