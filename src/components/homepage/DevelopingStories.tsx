import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import HeroImage from "@/components/HeroImage";

/* ── brand palette ────────────────────────────────────────────────────── */
const CATEGORY_COLORS: Record<string, string> = {
  immigration: "#D4A843",
  technology: "#4527A0",
  entertainment: "#AD1457",
  "markets-finance": "#E65100",
  sports: "#2E7D32",
  "nri-world": "#1565C0",
  news: "#C62828",
  "lifestyle-health": "#00838F",
  travel: "#00695C",
  food: "#BF360C",
};
const CATEGORY_LABELS: Record<string, string> = {
  news: "India",
  "nri-world": "World",
  "markets-finance": "Markets",
  "lifestyle-health": "Lifestyle",
};

interface LinkedArticle {
  id: string;
  headline: string;
  slug: string;
  category: string | null;
  image_url: string | null;
  published_at: string | null;
}

interface Storyline {
  id: string;
  title: string;
  slug: string;
  summary: string | null;
  category: string | null;
  status: string;
  article_count: number;
  last_article_at: string | null;
  articles: LinkedArticle[];
}

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function formatDateShort(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

const MAX_INLINE_ARTICLES = 4;

export default function DevelopingStories() {
  const [stories, setStories] = useState<Storyline[]>([]);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      // 1) Fetch active/emerging storylines
      const { data: rawStorylines } = await (supabase as any)
        .from("storylines")
        .select("id, title, slug, summary, category, status, article_count, last_article_at")
        .in("status", ["active", "emerging"])
        .order("last_article_at", { ascending: false })
        .limit(5);

      if (cancelled || !rawStorylines) return;
      const valid: any[] = rawStorylines.filter((s: any) => s.article_count >= 5).slice(0, 2);
      if (valid.length === 0) { setStories([]); return; }

      // 2) Fetch linked articles for all storylines in one query
      const ids = valid.map((s: any) => s.id);
      const { data: links } = await (supabase as any)
        .from("storyline_articles")
        .select("storyline_id, p2_articles(id, headline, slug, category, image_url, published_at)")
        .in("storyline_id", ids)
        .order("added_at", { ascending: false });

      if (cancelled) return;

      // Group articles by storyline
      const articleMap: Record<string, LinkedArticle[]> = {};
      for (const link of (links || [])) {
        const art = link.p2_articles;
        if (!art) continue;
        const sid = link.storyline_id;
        if (!articleMap[sid]) articleMap[sid] = [];
        articleMap[sid].push(art);
      }

      // Sort each storyline's articles by published_at desc
      for (const sid of Object.keys(articleMap)) {
        articleMap[sid].sort((a, b) => {
          const da = a.published_at ? new Date(a.published_at).getTime() : 0;
          const db = b.published_at ? new Date(b.published_at).getTime() : 0;
          return db - da;
        });
      }

      const enriched: Storyline[] = valid.map((s: any) => ({
        ...s,
        articles: articleMap[s.id] || [],
      }));

      setStories(enriched);
    })();

    return () => { cancelled = true; };
  }, []);

  if (stories.length === 0) return null;

  return (
    <section style={{ padding: "12px 0 8px" }}>
      {/* Section header */}
      <div className="container" style={{ padding: "0 16px", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{
            fontSize: 14, fontWeight: 700, color: "hsl(var(--foreground))",
            textTransform: "uppercase", letterSpacing: "0.04em",
          }}>
            Developing Stories
          </span>
          <span style={{
            fontSize: 10, background: "#C62828", color: "#fff",
            borderRadius: 3, padding: "1px 5px", fontWeight: 700,
            letterSpacing: "0.05em", lineHeight: "16px",
          }}>
            LIVE
          </span>
        </div>
      </div>

      {/* Storylines grid — 2-col on desktop, stacked on mobile */}
      <div className="container grid grid-cols-1 md:grid-cols-2 items-start" style={{ padding: "0 16px", gap: 12 }}>
        {stories.map((s, idx) => {
          const catColor = CATEGORY_COLORS[s.category || ""] || "#6D6D6D";
          const catLabel = CATEGORY_LABELS[s.category || ""] || (s.category || "").replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
          const isFirst = idx === 0;
          const heroArticle = s.articles[0];
          const heroImage = isFirst && heroArticle?.image_url ? heroArticle.image_url : null;
          const displayArticles = s.articles.slice(0, MAX_INLINE_ARTICLES);
          const hasMore = s.articles.length > MAX_INLINE_ARTICLES;

          return (
            <div
              key={s.id}
              style={{
                borderRadius: 10,
                background: "hsl(var(--card))",
                border: "1px solid hsl(var(--rule) / 0.2)",
                borderLeft: `3px solid ${catColor}`,
                overflow: "hidden",
              }}
            >
              {/* Hero image for first storyline only */}
              {heroImage && (
                <Link to={`/developing/${s.slug}`} style={{ display: "block" }}>
                  <div style={{
                    width: "100%", height: 180, overflow: "hidden",
                    background: "hsl(var(--muted) / 0.3)",
                  }}>
                    <HeroImage zoomable={false}
                      src={heroImage}
                      alt=""
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  </div>
                </Link>
              )}

              {/* Storyline header */}
              <div
                style={{
                  padding: "12px 14px",
                }}
              >
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <Link to={`/developing/${s.slug}`} style={{ textDecoration: "none", color: "inherit" }}>
                      <span style={{
                        fontSize: 15, fontWeight: 700, lineHeight: 1.3,
                        color: "hsl(var(--foreground))",
                      }}>
                        {s.title}
                      </span>
                    </Link>

                    {/* Meta row */}
                    <div style={{
                      display: "flex", alignItems: "center", gap: 6,
                      flexWrap: "wrap", marginTop: 6,
                    }}>
                      <span style={{
                        fontSize: 10, fontWeight: 600, color: catColor,
                        background: `${catColor}15`,
                        borderRadius: 3, padding: "1px 5px",
                        textTransform: "uppercase", letterSpacing: "0.03em",
                        lineHeight: "15px", whiteSpace: "nowrap",
                      }}>
                        {catLabel}
                      </span>
                      <span style={{
                        fontSize: 11, color: "hsl(var(--muted-foreground))",
                        fontWeight: 500, whiteSpace: "nowrap",
                      }}>
                        {s.article_count} articles
                      </span>
                      <span style={{
                        fontSize: 10, color: "hsl(var(--muted-foreground) / 0.7)",
                        whiteSpace: "nowrap",
                      }}>
                        · {timeAgo(s.last_article_at)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Inline timeline of articles */}
              {displayArticles.length > 0 && (
                <div style={{
                  padding: "0 14px 12px",
                  borderTop: "1px solid hsl(var(--rule) / 0.12)",
                }}>
                  <div style={{ position: "relative", paddingLeft: 20, marginTop: 10 }}>
                    {/* Vertical timeline line */}
                    <div style={{
                      position: "absolute", left: 4, top: 6, bottom: 6,
                      width: 2, background: `${catColor}30`,
                      borderRadius: 1,
                    }} />

                    {displayArticles.map((article, ai) => (
                      <Link
                        key={article.id}
                        to={`/articles/${article.slug}`}
                        style={{
                          display: "block",
                          padding: "8px 0",
                          textDecoration: "none",
                          color: "inherit",
                          position: "relative",
                          borderBottom: ai < displayArticles.length - 1 ? "1px solid hsl(var(--rule) / 0.08)" : "none",
                        }}
                      >
                        {/* Timeline dot */}
                        <div style={{
                          position: "absolute",
                          left: -18,
                          top: 14,
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          background: ai === 0 ? catColor : "hsl(var(--rule) / 0.4)",
                          border: ai === 0 ? `2px solid ${catColor}` : "2px solid hsl(var(--rule) / 0.2)",
                          boxShadow: ai === 0 ? `0 0 0 2px ${catColor}25` : "none",
                        }} />

                        <div style={{ fontSize: 10, color: "hsl(var(--muted-foreground))", marginBottom: 2, fontWeight: 500 }}>
                          {formatDateShort(article.published_at)}
                        </div>
                        <div style={{
                          fontSize: 13.5, fontWeight: 600, lineHeight: 1.3,
                          color: "hsl(var(--foreground))",
                        }}>
                          {article.headline}
                        </div>
                      </Link>
                    ))}
                  </div>

                  {/* "See full story" link */}
                  {hasMore && (
                    <Link
                      to={`/developing/${s.slug}`}
                      style={{
                        display: "block", textAlign: "center",
                        fontSize: 12, fontWeight: 600,
                        color: catColor,
                        padding: "8px 0 2px",
                        textDecoration: "none",
                      }}
                    >
                      See all {s.article_count} articles →
                    </Link>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
