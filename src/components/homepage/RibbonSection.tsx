import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

interface Props {
  title: string;
  borderColor: string;
  categorySlug: string;
  articles: Article[];
  aspectRatio?: "portrait" | "landscape";
  cardCount?: number;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

export default function RibbonSection({
  title,
  borderColor,
  categorySlug,
  articles,
  aspectRatio = "landscape",
  cardCount = 4,
}: Props) {
  if (articles.length === 0) return null;
  const items = articles.slice(0, cardCount);
  const isPortrait = aspectRatio === "portrait";

  return (
    <section className="mb-14">
      <div className="container">
        {/* Section header */}
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: `3px solid ${borderColor}` }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            {title}
          </h2>
          <Link
            to={`/${categorySlug}`}
            className="text-[13px] font-semibold text-muted-foreground hover:text-foreground transition-colors"
          >
            See all →
          </Link>
        </div>

        {/* Ribbon scroll */}
        <div className="v2-ribbon-scroll">
          {items.map((a) => {
            const img = isValidImage(a.hero_image_url);
            return (
              <Link
                key={a.id}
                to={`/articles/${a.slug}`}
                className="group block flex-shrink-0"
                style={{ width: isPortrait ? 200 : 280 }}
              >
                {img ? (
                  <div
                    className="w-full bg-stone-100 overflow-hidden rounded-lg mb-2.5"
                    style={{ aspectRatio: isPortrait ? "3/4" : "16/10" }}
                  >
                    <HeroImage
                      src={a.hero_image_url}
                      alt={a.title}
                      loading="lazy"
                      className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
                      width={isPortrait ? 200 : 280}
                      height={isPortrait ? 267 : 175}
                    />
                  </div>
                ) : (
                  <div
                    className="w-full bg-stone-100 flex items-center justify-center text-muted-foreground/30 text-xs rounded-lg mb-2.5"
                    style={{ aspectRatio: isPortrait ? "3/4" : "16/10" }}
                  >
                    IMAGE
                  </div>
                )}
                <p
                  className="text-[10px] font-bold tracking-[1.2px] uppercase mb-1"
                  style={{ color: borderColor }}
                >
                  {a.category?.replace("-", " ")}
                </p>
                <h4 className="font-serif text-[14px] font-bold leading-snug group-hover:text-primary transition-colors line-clamp-2">
                  {a.title}
                </h4>
                <p className="text-xs text-muted-foreground mt-1">
                  {timeAgo(a.published_at)}
                </p>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
