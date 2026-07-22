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

  return (
    <section className="whos-x-section">
      <div className="container">
        <div className="whos-x-header">
          <h2 className="whos-x-section-title">Who's Who</h2>
          <span className="whos-x-section-sub">Notable people of Indian origin</span>
        </div>
        <div className="whos-x-scroll" ref={scrollRef}>
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
                    <HeroImage
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
