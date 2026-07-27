import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import HeroImage, { isValidImage } from "@/components/HeroImage";

/* "Who's Who" — horizontal scroll of all "who is" profiles,
   latest first, with the newest card rendered larger. */

interface SpotlightArticle {
  id: string;
  slug: string;
  headline: string;
  subheadline: string | null;
  image_url: string | null;
  image_caption: string | null;
  published_at: string | null;
  tags: string[] | null;
  focal_x?: number | null;
  focal_y?: number | null;
}

function extractName(headline: string): string | null {
  const m = headline.match(/who\s+is\s+(.+?)[\?:—–\-]/i);
  return m ? m[1].trim() : null;
}

function extractTagline(article: SpotlightArticle): string {
  if (article.subheadline) return article.subheadline;
  if (article.headline.includes("?"))
    return article.headline.split("?").slice(1).join("?").trim();
  return "";
}

/** IDs of articles in the spotlight, so the homepage can exclude them
 *  from hero / category sections. Updated after fetch. */
let _spotlightIds: string[] = [];
export function getSpotlightIds(): string[] {
  return _spotlightIds;
}

export default function WhosXSpotlight() {
  const [articles, setArticles] = useState<SpotlightArticle[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    (async () => {
      const { data } = await (supabase as any)
        .from("p2_articles")
        .select(
          "id, slug, headline, subheadline, image_url, image_caption, published_at, tags, focal_x, focal_y"
        )
        .eq("status", "published")
        .contains("tags", ["who is"])
        .order("published_at", { ascending: false })
        .limit(20);

      if (data && data.length > 0) {
        setArticles(data);
        _spotlightIds = data.map((a: SpotlightArticle) => a.id);
      }
    })();
  }, []);

  if (articles.length === 0) return null;

  /* When only 1-2 profiles exist, show a full-width horizontal banner on desktop
     instead of a grid with empty columns. */
  const isFew = articles.length <= 2;

  return (
    <section className="whos-x-section">
      <div className="container">
        <div className="whos-x-header">
          <h2 className="whos-x-section-title">Who's Who</h2>
          <span className="whos-x-section-sub">Notable people of Indian origin</span>
        </div>

        {/* ── Desktop: full-width banner when few profiles ── */}
        {isFew && (
          <div className="hidden md:flex flex-col gap-4">
            {articles.map((article) => {
              const personName = extractName(article.headline);
              const tagline = extractTagline(article);
              const articleUrl = `/articles/${article.slug}`;
              const hasImage = isValidImage(article.image_url);
              return (
                <Link
                  key={article.id}
                  to={articleUrl}
                  className="group flex items-stretch rounded-xl overflow-hidden bg-[#0B1D3A] text-white no-underline hover:shadow-lg transition-shadow"
                  style={{ maxHeight: 200 }}
                >
                  {hasImage && (
                    <div className="w-[280px] flex-shrink-0 overflow-hidden">
                      <HeroImage zoomable={false}
                        src={article.image_url!}
                        alt={personName || article.headline}
                        focalX={article.focal_x ?? 0.5}
                        focalY={article.focal_y ?? 0.5}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="flex flex-col justify-center px-8 py-5 gap-1.5">
                    <span className="text-[10px] font-bold uppercase tracking-[2px] text-[#D4A843]">Who's Who</span>
                    {personName && (
                      <h3 className="text-2xl font-extrabold leading-tight" style={{ fontFamily: "var(--font-heading, 'Inter', system-ui, sans-serif)" }}>
                        {personName}
                      </h3>
                    )}
                    {tagline && (
                      <p className="text-sm text-slate-300 leading-snug line-clamp-2 max-w-lg">{tagline}</p>
                    )}
                    <span className="text-xs font-semibold text-[#D4A843] mt-1 group-hover:underline">Read Profile →</span>
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        {/* ── Mobile (always) or Desktop with 3+ profiles: card grid/scroll ── */}
        <div className={`whos-x-scroll ${isFew ? "md:hidden" : ""}`} ref={scrollRef}>
          {articles.map((article, idx) => {
            const personName = extractName(article.headline);
            const tagline = extractTagline(article);
            const articleUrl = `/articles/${article.slug}`;
            const hasImage = isValidImage(article.image_url);
            const isLatest = idx === 0;

            return (
              <Link
                to={articleUrl}
                className={`whos-x-card ${isLatest ? "whos-x-card--featured" : "whos-x-card--compact"}`}
                key={article.id}
              >
                {hasImage && (
                  <div className="whos-x-photo">
                    <HeroImage zoomable={false}
                      src={article.image_url!}
                      alt={personName || article.headline}
                      focalX={article.focal_x ?? 0.5}
                      focalY={article.focal_y ?? 0.5}
                    />
                  </div>
                )}
                <div className="whos-x-text">
                  <span className="whos-x-label">Who's</span>
                  {personName && <h3 className="whos-x-name">{personName}</h3>}
                  {isLatest && tagline && (
                    <p className="whos-x-tagline">{tagline}</p>
                  )}
                  <span className="whos-x-cta">Read →</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
