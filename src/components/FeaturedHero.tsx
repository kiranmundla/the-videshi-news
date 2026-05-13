import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";

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
  return 'portrait';
}

export default function FeaturedHero({ article }: { article: Article }) {
  const href = `/articles/${article.slug}`;
  const url = article.hero_image_url || "";
  const isFlag = /flag/i.test(url);
  const hasImage = isValidImage(url) && !isFlag;

  if (hasImage) {
    const orient = getImageOrientation(article.hero_image_url);
    
    if (orient === 'portrait') {
      // Portrait: side-by-side — image right, text left
      return (
        <section className="relative w-full overflow-hidden rounded-lg" style={{ background: '#1C1C1E' }}>
          <div className="flex items-center gap-6 px-5 md:px-12 py-6 md:py-8">
            <div className="flex-1">
              <Link to={href} className="block max-w-2xl">
                <p className="smallcaps text-white/90 mb-2">
                  <span className="bg-primary text-primary-foreground px-2 py-1 mr-2 tracking-wider">
                    FEATURED
                  </span>
                  {article.category}
                </p>
                <h1
                  className="font-display text-white leading-[1.1] hover:underline"
                  style={{ fontWeight: 800, fontSize: 'clamp(22px, 3.6vw, 32px)' }}
                >
                  {article.title}
                </h1>
                {article.excerpt && (
                  <p className="font-body-serif text-white/85 mt-2 text-sm md:text-base max-w-xl line-clamp-2">
                    {article.excerpt}
                  </p>
                )}
              </Link>
            </div>
            <div className="hidden md:block w-[180px] lg:w-[220px] flex-shrink-0">
              <img
                src={article.hero_image_url}
                alt={article.title}
                loading="eager"
                referrerPolicy="no-referrer"
                className="w-full h-auto rounded object-cover"
              />
            </div>
          </div>
        </section>
      );
    }

    // Landscape: full-bleed background (existing)
    return (
      <section className="relative w-full h-[260px] md:h-[300px] overflow-hidden rounded-lg">
        <img
          src={article.hero_image_url}
          alt={article.title}
          loading="eager"
          referrerPolicy="no-referrer"
          className="absolute inset-0 w-full h-full object-cover"
          style={{ objectPosition: "center" }}
        />
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.45) 50%, rgba(0,0,0,0.05) 100%)",
          }}
        />
        <div className="absolute inset-x-0 bottom-0 px-5 md:px-12 pb-6 md:pb-8">
          <Link to={href} className="block max-w-4xl">
            <p className="smallcaps text-white/90 mb-2">
              <span className="bg-primary text-primary-foreground px-2 py-1 mr-2 tracking-wider">
                FEATURED
              </span>
              {article.category}
            </p>
            <h1
              className="font-display text-white leading-[1.1] hover:underline"
              style={{ fontWeight: 800, fontSize: "clamp(22px, 3.6vw, 32px)" }}
            >
              {article.title}
            </h1>
            {article.excerpt && (
              <p className="font-body-serif text-white/85 mt-2 text-sm md:text-base max-w-3xl line-clamp-2">
                {article.excerpt}
              </p>
            )}
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section
      className="relative w-full h-[260px] md:h-[300px] flex items-center px-6 md:px-10 rounded-lg overflow-hidden"
      style={{ background: "#1C1C1E" }}
    >
      <Link to={href} className="block max-w-4xl">
        <p className="smallcaps mb-3" style={{ color: "hsl(var(--primary))" }}>
          <span className="bg-primary text-primary-foreground px-2 py-1 mr-2 tracking-wider">
            FEATURED
          </span>
          {article.category}
        </p>
        <h1
          className="font-display text-white leading-[1.1] hover:opacity-90"
          style={{ fontWeight: 800, fontSize: "clamp(22px, 3.6vw, 32px)" }}
        >
          {article.title}
        </h1>
        {article.excerpt && (
          <p className="font-body-serif text-white/80 mt-3 text-sm md:text-base max-w-3xl line-clamp-2">
            {article.excerpt}
          </p>
        )}
      </Link>
    </section>
  );
}
