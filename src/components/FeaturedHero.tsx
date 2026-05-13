import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";

export default function FeaturedHero({ article }: { article: Article }) {
  const href = `/articles/${article.slug}`;
  const url = article.hero_image_url || "";
  const isFlag = /flag/i.test(url);
  const hasImage = isValidImage(url) && !isFlag;

  if (hasImage) {
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
