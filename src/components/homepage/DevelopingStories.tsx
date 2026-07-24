import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import ScrollWrap from "./ScrollWrap";

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

interface Storyline {
  id: string;
  title: string;
  slug: string;
  summary: string | null;
  category: string | null;
  status: string;
  article_count: number;
  last_article_at: string | null;
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

export default function DevelopingStories() {
  const [stories, setStories] = useState<Storyline[]>([]);

  useEffect(() => {
    let cancelled = false;
    (supabase as any)
      .from("storylines")
      .select("id, title, slug, summary, category, status, article_count, last_article_at")
      .in("status", ["active", "emerging"])
      .order("last_article_at", { ascending: false })
      .limit(10)
      .then(({ data }: { data: Storyline[] | null }) => {
        if (cancelled || !data) return;
        /* only show storylines with 3+ articles (active threshold) */
        setStories(data.filter((s) => s.article_count >= 3));
      });
    return () => { cancelled = true; };
  }, []);

  if (stories.length === 0) return null;

  return (
    <section style={{ padding: "12px 0 8px" }}>
      {/* Section header */}
      <div className="container" style={{ padding: "0 16px", marginBottom: 8 }}>
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

      {/* Horizontal scroll strip */}
      <ScrollWrap scrollAmount={260}>
        {stories.map((s) => {
          const catColor = CATEGORY_COLORS[s.category || ""] || "#6D6D6D";
          const catLabel = CATEGORY_LABELS[s.category || ""] || (s.category || "").replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
          return (
            <Link
              key={s.id}
              to={`/stories/${s.slug}`}
              style={{
                flex: "0 0 auto",
                width: 240,
                minHeight: 72,
                padding: "10px 14px",
                borderRadius: 8,
                background: "hsl(var(--card))",
                border: "1px solid hsl(var(--rule) / 0.3)",
                borderLeft: `3px solid ${catColor}`,
                textDecoration: "none",
                color: "inherit",
                display: "flex",
                flexDirection: "column",
                gap: 6,
                transition: "box-shadow 0.15s, border-color 0.15s",
                cursor: "pointer",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.boxShadow = "0 2px 8px rgba(0,0,0,0.1)";
                (e.currentTarget as HTMLElement).style.borderColor = catColor;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.boxShadow = "none";
                (e.currentTarget as HTMLElement).style.borderColor = "hsl(var(--rule) / 0.3)";
              }}
            >
              {/* Title */}
              <span style={{
                fontSize: 13.5, fontWeight: 700, lineHeight: 1.3,
                color: "hsl(var(--foreground))",
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }}>
                {s.title}
              </span>

              {/* Meta row: category pill + article count + time */}
              <div style={{
                display: "flex", alignItems: "center", gap: 6,
                flexWrap: "wrap", marginTop: "auto",
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
            </Link>
          );
        })}
      </ScrollWrap>
    </section>
  );
}
