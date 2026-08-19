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

export default function JustInStrip() {
  const [items, setItems] = useState<JustInItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await (supabase as any)
          .from("p2_articles")
          .select("id, slug, headline, image_url, published_at, category")
          .eq("status", "published")
          .order("published_at", { ascending: false })
          .limit(6);

        if (data?.length) setItems(data);
      } catch {
        /* silent */
      } finally {
        setLoaded(true);
      }
    })();
  }, []);

  if (!loaded || items.length === 0) return null;

  return (
    <section className="mb-10">
      <div className="container">
        {/* Header */}
        <div
          className="flex items-center gap-2.5 mb-5 pb-3"
          style={{ borderBottom: "1px solid hsl(var(--rule))" }}
        >
          <span
            className="inline-block w-1.5 h-1.5 rounded-full animate-pulse"
            style={{ background: "#C62828" }}
          />
          <span
            className="font-bold uppercase"
            style={{ fontSize: 11, letterSpacing: "0.15em", color: "#888" }}
          >
            JUST IN
          </span>
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
