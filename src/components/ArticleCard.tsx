import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { Article, formatShortDate, readingTime } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

type Variant = "hero" | "featured" | "card" | "long" | "compact";

/* Mini gallery thumbnails for article cards with multiple images */
function ArticleGallery({ images, title }: { images: { url: string; caption?: string }[]; title: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    // Always reset to first image
    el.scrollLeft = 0;
    const onScroll = () => {
      const idx = Math.round(el.scrollLeft / el.clientWidth);
      setCurrent(Math.min(idx, images.length - 1));
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, [images.length]);

  return (
    <div className="relative rounded-lg overflow-hidden">
      <style>{`.card-gallery::-webkit-scrollbar { display: none; }`}</style>
      <div
        ref={scrollRef}
        className="card-gallery flex overflow-x-auto"
        style={{
          scrollSnapType: "x mandatory",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          WebkitOverflowScrolling: "touch",
        } as React.CSSProperties}
        onClick={(e) => e.preventDefault()}
      >
        {images.map((img, i) => (
          <div
            key={i}
            className="w-full flex-shrink-0 bg-stone-100"
            style={{ scrollSnapAlign: "start" }}
          >
            <img
              src={img.url}
              alt={img.caption || title}
              loading={i === 0 ? "eager" : "lazy"}
              className="w-full rounded-lg"
              style={{ maxHeight: "50vh", objectFit: "contain", background: "#f5f5f0" }}
            />
          </div>
        ))}
      </div>
      {/* Dots */}
      <div style={{
        position: "absolute", bottom: 8, left: "50%", transform: "translateX(-50%)",
        display: "flex", gap: 5,
      }}>
        {images.map((_, i) => (
          <div
            key={i}
            style={{
              width: i === current ? 7 : 5,
              height: i === current ? 7 : 5,
              borderRadius: "50%",
              background: i === current ? "#fff" : "rgba(255,255,255,0.5)",
              transition: "all 0.15s",
              boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
            }}
          />
        ))}
      </div>
    </div>
  );
}
function MiniGallery({ images }: { images: { url: string; caption: string }[] }) {
  if (!images || images.length === 0) return null;
  return (
    <div
      className="flex gap-1.5 mt-2 overflow-x-auto"
      style={{ scrollbarWidth: "none", msOverflowStyle: "none" } as React.CSSProperties}
    >
      <style>{`.mini-gallery::-webkit-scrollbar { display: none; }`}</style>
      {images.slice(0, 5).map((img, i) => (
        <div
          key={i}
          className="flex-shrink-0 w-16 h-12 md:w-20 md:h-14 rounded overflow-hidden bg-stone-100"
        >
          <img
            src={img.url}
            alt={img.caption || ""}
            loading="lazy"
            className="w-full h-full object-cover"
          />
        </div>
      ))}
      {images.length > 5 && (
        <div className="flex-shrink-0 w-16 h-12 md:w-20 md:h-14 rounded bg-stone-200 flex items-center justify-center">
          <span className="text-xs text-stone-500 font-medium">+{images.length - 5}</span>
        </div>
      )}
    </div>
  );
}

function parseImageDimensions(url: string | null | undefined): { w: number; h: number } | null {
  if (!url) return null;
  try {
    const params = new URL(url).searchParams;
    const w = parseInt(params.get('w') || '');
    const h = parseInt(params.get('h') || '');
    if (w > 0 && h > 0) return { w, h };
  } catch {}
  return null;
}

function getImageOrientation(url: string | null | undefined): 'landscape' | 'portrait' | null {
  const dims = parseImageDimensions(url);
  if (!dims) return null;
  const ratio = dims.w / dims.h;
  if (ratio > 1.2) return 'landscape';
  return 'portrait'; // portrait and square both get side-by-side treatment
}

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

  // Runtime orientation detection for images without w/h URL params
  const urlOrientation = getImageOrientation(article.hero_image_url);
  const [runtimeOrientation, setRuntimeOrientation] = useState<"landscape" | "portrait" | null>(null);
  const effectiveOrientation = urlOrientation ?? runtimeOrientation;

  // ===================== COMPACT =====================
  if (variant === "compact") {
    return (
      <Link to={href} onClick={saveScroll} className="group flex gap-4 items-start">
        {hasImage && (
          <HeroImage
            src={article.hero_image_url}
            alt={article.title}
            loading="lazy"
            className="w-20 h-20 object-cover flex-shrink-0"
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
        <Link onClick={saveScroll}
          to={href}
          className="group block bg-secondary/60 p-6 md:p-10 border hairline border-l-2"
          style={{ borderLeftColor: accent }}
        >
          <p className="smallcaps text-primary mb-3">
            {article.category}
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
      <Link onClick={saveScroll}
        to={href}
        className="group grid md:grid-cols-2 gap-6 md:gap-10 items-center bg-secondary/60 p-6 md:p-10 border hairline"
      >
        <figure>
          <div className="w-full aspect-[16/9] bg-stone-100 overflow-hidden">
            <HeroImage
              src={article.hero_image_url}
              alt={article.title}
              loading="lazy"
              className="w-full h-full object-cover"
              style={{ objectPosition: "center 20%" }}
            />
          </div>
        </figure>
        <div>
          <p className="smallcaps text-primary mb-3">
            {article.category}
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
    // Text-first card — denser layout with red top accent bar.
    const isLarge = variant === "hero" || variant === "featured";
    const RED = "#C0392B";
    return (
      <Link
        onClick={saveScroll}
        to={href}
        className={`group block h-auto bg-stone-50 border-t-[3px] hairline border-l border-r border-b ${
          isLarge ? "p-5 md:p-10" : "p-4 md:p-5"
        }`}
        style={{ borderTopColor: RED }}
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
            isLarge ? headlineSizeNoImage : "text-[1.1rem] md:text-[1.2rem] leading-snug"
          }`}
        >
          {article.title}
        </h2>
        {article.excerpt && (
          <p
            className={`mt-2 text-muted-foreground leading-snug hidden md:block ${
              isLarge ? "text-base line-clamp-2 md:line-clamp-3" : "text-sm line-clamp-2"
            }`}
          >
            {article.excerpt}
          </p>
        )}
        <p className="mt-2 text-xs text-muted-foreground">
          {article.author ? `By ${article.author} · ` : ""}
          {formatShortDate(article.published_at)} · {time} min read
        </p>
      </Link>
    );
  }

  // Portrait/square images → side-by-side layout (only for "card" variant)
  if (effectiveOrientation === 'portrait' && variant === 'card') {
    return (
      <Link to={href} onClick={saveScroll} className="group flex gap-4">
        <div className="w-[120px] md:w-[160px] flex-shrink-0">
          <HeroImage
            src={article.hero_image_url}
            alt={article.title}
            loading="lazy"
            className="w-full h-auto rounded object-cover"
            onOrientationDetected={setRuntimeOrientation}
          />
        </div>
        <div className="flex-1 min-w-0">
          {!hideCategory && (
            <p className="smallcaps text-primary mb-1">
              {featureLabel && (
                <span className="bg-primary text-primary-foreground px-1.5 py-0.5 mr-2 tracking-wider">
                  {featureLabel}
                </span>
              )}
              {article.category}
            </p>
          )}
          <h2
            className={`font-serif font-bold text-foreground group-hover:text-primary transition-colors ${headlineSizeWithImage}`}
          >
            {article.title}
          </h2>
          <p className="mt-2 text-xs text-muted-foreground">
            {article.author ? `By ${article.author} · ` : ""}
            {formatShortDate(article.published_at)} · {time} min read
          </p>
        </div>
      </Link>
    );
  }

  // Landscape or unknown orientation → image on top (default)
  const gallery = article.gallery_images;
  // Combine hero + gallery into one scroll strip when gallery exists
  const allImages = gallery && gallery.length > 0
    ? [
        { url: article.hero_image_url!, caption: article.title },
        ...gallery.filter(g => g.url !== article.hero_image_url),
      ]
    : null;

  return (
    <Link to={href} onClick={saveScroll} className="group block">
      {allImages && allImages.length > 1 ? (
        <ArticleGallery images={allImages} title={article.title} />
      ) : (
        <figure className="w-full">
          <div className="w-full aspect-[16/9] bg-stone-100 overflow-hidden rounded-lg">
            <HeroImage
              src={article.hero_image_url}
              alt={article.title}
              loading={variant === "hero" ? "eager" : "lazy"}
              className="w-full h-full object-cover group-hover:scale-[1.01] transition-transform duration-500"
              style={{ objectPosition: "center 20%" }}
              onOrientationDetected={setRuntimeOrientation}
            />
          </div>
        </figure>
      )}
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
