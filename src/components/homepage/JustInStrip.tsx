import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import HeroImage, { isValidImage } from "@/components/HeroImage";

/* ── types ────────────────────────────────────────── */

interface JustInItem {
  id: string;
  slug: string;
  headline: string;
  image_url: string | null;
  published_at: string | null;
  category: string | null;
}

/* ── helpers ───────────────────────────────────────── */

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

/* ── single item ───────────────────────────────────── */

function JustInCard({ item }: { item: JustInItem }) {
  const href = `/articles/${item.slug ?? item.id}`;
  const hasImage = isValidImage(item.image_url);

  return (
    <div
      className="py-3"
      style={{ borderBottom: "1px solid hsl(var(--rule) / 0.35)" }}
    >
      <Link to={href} className="group flex gap-4 items-start">
        {/* Thumbnail — only when image exists, no placeholder */}
        {hasImage && (
          <HeroImage
            zoomable={false}
            src={item.image_url}
            alt=""
            loading="lazy"
            className="w-[60px] h-[60px] rounded-md object-cover flex-shrink-0"
            width="60"
            height="60"
          />
        )}

        {/* Text */}
        <div
          className={`min-w-0 ${hasImage ? "" : "border-l-2 pl-3"}`}
          style={hasImage ? undefined : { borderColor: "hsl(var(--primary))" }}
        >
          <h3 className="text-sm font-medium leading-snug text-foreground group-hover:text-primary transition-colors line-clamp-2">
            {item.headline}
          </h3>
          <p className="text-xs text-foreground/50 mt-1">
            {timeAgo(item.published_at)}
          </p>
        </div>
      </Link>
    </div>
  );
}

/* ── main component ────────────────────────────────── */

/* Parent-supplied articles arrive in the lib Article / feed shape
   (title + hero_image_url); the self-fetch fallback returns DB rows
   (headline + image_url). Both normalize to JustInItem below. */
type JustInSourceArticle = {
  id: string;
  slug: string;
  title?: string;
  headline?: string;
  hero_image_url?: string | null;
  image_url?: string | null;
  published_at: string | null;
  category?: string | null;
};

/* Strip capacity — the feed supplies up to 20 (prebuild-feeds.py
   _build_just_in); both render paths cap here. */
const JUST_IN_MAX = 20;

interface JustInStripProps {
  /* Preferred path: the parent passes the feed's just_in list, already
     filtered against the featured article and hero-side picks. This
     component previously ignored the prop and self-fetched the newest 6,
     which re-listed the featured article in Just In (Kiran, 2026-10-20). */
  articles?: JustInSourceArticle[];
  /* Fallback path only: ids to exclude from the self-fetch (featured,
     hero side) so the strip never duplicates what is shown above it. */
  excludeIds?: string[];
}

function normalize(a: JustInSourceArticle): JustInItem {
  return {
    id: a.id,
    slug: a.slug,
    headline: a.title ?? a.headline ?? "",
    image_url: a.hero_image_url ?? a.image_url ?? null,
    published_at: a.published_at,
    category: a.category ?? null,
  };
}

export default function JustInStrip({ articles, excludeIds }: JustInStripProps = {}) {
  const [items, setItems] = useState<JustInItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (articles && articles.length) {
      setItems(articles.slice(0, JUST_IN_MAX).map(normalize));
      setLoaded(true);
      return;
    }
    (async () => {
      try {
        const { data } = await (supabase as any)
          .from("p2_articles")
          .select("id, slug, headline, image_url, published_at, category")
          .eq("status", "published")
          .order("published_at", { ascending: false })
          .limit(28);

        if (data?.length) {
          const excluded = new Set(excludeIds ?? []);
          setItems(
            (data as JustInItem[])
              .filter((a) => !excluded.has(a.id))
              .slice(0, JUST_IN_MAX)
          );
        }
      } catch {
        /* silent */
      } finally {
        setLoaded(true);
      }
    })();
  }, [articles, excludeIds]);

  if (!loaded || items.length === 0) return null;

  return (
    <section className="mb-10">
      <div className="container">
        {/* Header — matches other category section headers */}
        <div
          className="flex items-center gap-2.5 mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #C62828" }}
        >
          <span
            className="inline-block w-1.5 h-1.5 rounded-full animate-pulse"
            style={{ background: "#C62828" }}
          />
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            Just In
          </h2>
        </div>

        {/* Grid: 2 columns of 3 on desktop, single column on mobile */}
        <div className="grid grid-cols-1 md:grid-cols-2 md:gap-x-10">
          {items.map((item) => (
            <JustInCard key={item.id} item={item} />
          ))}
        </div>
      </div>
    </section>
  );
}
