import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import HeroImage, { isValidImage } from "@/components/HeroImage";

/* "Who's X" weekly spotlight — fetches the most recent published article
   tagged "who is" and renders a prominent profile card on the homepage. */

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

export default function WhosXSpotlight() {
  const [article, setArticle] = useState<SpotlightArticle | null>(null);

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
        .limit(1);

      if (data && data.length > 0) setArticle(data[0]);
    })();
  }, []);

  if (!article) return null;

  // Extract person name from headline — typically "Who Is <Name>? ..."
  const nameMatch = article.headline.match(/who\s+is\s+(.+?)[\?:—–\-]/i);
  const personName = nameMatch ? nameMatch[1].trim() : null;

  // One-liner: use subheadline or first sentence-ish chunk of headline after the "?"
  const tagline =
    article.subheadline ||
    (article.headline.includes("?")
      ? article.headline.split("?").slice(1).join("?").trim()
      : "");

  const articleUrl = `/articles/${article.slug}`;
  const hasImage = isValidImage(article.image_url);

  return (
    <section className="whos-x-section">
      <div className="container">
        <Link to={articleUrl} className="whos-x-card">
          {/* Photo */}
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

          {/* Text */}
          <div className="whos-x-text">
            <span className="whos-x-label">Who's</span>
            {personName && <h2 className="whos-x-name">{personName}</h2>}
            {tagline && <p className="whos-x-tagline">{tagline}</p>}
            <span className="whos-x-cta">Read their story →</span>
          </div>
        </Link>
      </div>
    </section>
  );
}
