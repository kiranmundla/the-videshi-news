import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Masthead from "@/components/Masthead";
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
const STATUS_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  active: { bg: "#E8F5E9", color: "#2E7D32", label: "Active" },
  emerging: { bg: "#E3F2FD", color: "#1565C0", label: "Emerging" },
  cooling: { bg: "#FFF3E0", color: "#E65100", label: "Cooling" },
  resolved: { bg: "#ECEFF1", color: "#546E7A", label: "Resolved" },
};

interface Storyline {
  id: string;
  title: string;
  slug: string;
  summary: string | null;
  category: string | null;
  status: string;
  article_count: number;
  first_article_at: string | null;
  last_article_at: string | null;
  metadata: any | null;
}

interface LinkedArticle {
  id: string;
  headline: string;
  slug: string;
  category: string | null;
  image_url: string | null;
  published_at: string | null;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function formatDateShort(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/* ── Medal Tracker Card ───────────────────────────────────────────────── */
function MedalTracker({ data }: { data: any }) {
  if (!data) return null;
  const { gold = 0, silver = 0, bronze = 0, total = 0, updated, medalists = [] } = data;

  return (
    <div style={{
      marginBottom: 24, borderRadius: 12,
      background: "linear-gradient(135deg, #0B1D3A 0%, #1a3a5c 100%)",
      padding: "20px 24px", color: "#fff",
    }}>
      {/* Header row */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 20 }}>🇮🇳</span>
          <span style={{ fontSize: 16, fontWeight: 700, letterSpacing: "0.02em" }}>India Medal Tally</span>
        </div>
        {updated && (
          <span style={{ fontSize: 11, color: "rgba(255,255,255,0.5)" }}>
            Updated {new Date(updated + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" })}
          </span>
        )}
      </div>

      {/* Medal counts */}
      <div style={{ display: "flex", gap: 12, marginBottom: medalists.length > 0 ? 18 : 0 }}>
        {[
          { emoji: "🥇", count: gold, label: "Gold", bg: "rgba(255,215,0,0.15)", border: "rgba(255,215,0,0.3)" },
          { emoji: "🥈", count: silver, label: "Silver", bg: "rgba(192,192,192,0.15)", border: "rgba(192,192,192,0.3)" },
          { emoji: "🥉", count: bronze, label: "Bronze", bg: "rgba(205,127,50,0.15)", border: "rgba(205,127,50,0.3)" },
        ].map(m => (
          <div key={m.label} style={{
            flex: 1, textAlign: "center", padding: "12px 8px",
            borderRadius: 8, background: m.bg, border: `1px solid ${m.border}`,
          }}>
            <div style={{ fontSize: 22, marginBottom: 2 }}>{m.emoji}</div>
            <div style={{ fontSize: 24, fontWeight: 800, lineHeight: 1 }}>{m.count}</div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.6)", marginTop: 2, textTransform: "uppercase", letterSpacing: "0.05em" }}>{m.label}</div>
          </div>
        ))}
        <div style={{
          flex: 1, textAlign: "center", padding: "12px 8px",
          borderRadius: 8, background: "rgba(212,168,67,0.15)", border: "1px solid rgba(212,168,67,0.3)",
        }}>
          <div style={{ fontSize: 22, marginBottom: 2 }}>🏅</div>
          <div style={{ fontSize: 24, fontWeight: 800, lineHeight: 1 }}>{total}</div>
          <div style={{ fontSize: 10, color: "rgba(255,255,255,0.6)", marginTop: 2, textTransform: "uppercase", letterSpacing: "0.05em" }}>Total</div>
        </div>
      </div>

      {/* Medalist list */}
      {medalists.length > 0 && (
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: 14 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: "rgba(255,255,255,0.5)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Medalists
          </div>
          {medalists.map((m: any, i: number) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "6px 0",
              borderBottom: i < medalists.length - 1 ? "1px solid rgba(255,255,255,0.06)" : "none",
            }}>
              <span style={{ fontSize: 16, flex: "0 0 24px", textAlign: "center" }}>
                {m.medal === "gold" ? "🥇" : m.medal === "silver" ? "🥈" : "🥉"}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{m.name}</div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)" }}>
                  {m.sport} — {m.event}
                </div>
              </div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", flex: "0 0 auto" }}>
                {m.date ? new Date(m.date + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" }) : ""}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function StorylineTimeline() {
  const { slug } = useParams<{ slug: string }>();
  const [storyline, setStoryline] = useState<Storyline | null>(null);
  const [articles, setArticles] = useState<LinkedArticle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    let cancelled = false;

    // Fetch storyline
    (supabase as any)
      .from("storylines")
      .select("*")
      .eq("slug", slug)
      .single()
      .then(({ data }: { data: Storyline | null }) => {
        if (cancelled || !data) { setLoading(false); return; }
        setStoryline(data);

        // Fetch linked articles
        (supabase as any)
          .from("storyline_articles")
          .select("article_id, p2_articles(id, headline, slug, category, image_url, published_at)")
          .eq("storyline_id", data.id)
          .order("added_at", { ascending: false })
          .then(({ data: links }: { data: any[] | null }) => {
            if (cancelled) return;
            const arts = (links || [])
              .map((l: any) => l.p2_articles)
              .filter(Boolean)
              .sort((a: LinkedArticle, b: LinkedArticle) => {
                const da = a.published_at ? new Date(a.published_at).getTime() : 0;
                const db = b.published_at ? new Date(b.published_at).getTime() : 0;
                return db - da; // newest first
              });
            setArticles(arts);
            setLoading(false);
          });
      });

    return () => { cancelled = true; };
  }, [slug]);

  if (loading) {
    return (
      <>
        <Masthead />
        <div className="container" style={{ padding: "60px 16px", textAlign: "center", color: "hsl(var(--muted-foreground))" }}>
          Loading story...
        </div>
      </>
    );
  }

  if (!storyline) {
    return (
      <>
        <Masthead />
        <div className="container" style={{ padding: "60px 16px", textAlign: "center" }}>
          <h2 style={{ fontSize: 22, marginBottom: 8 }}>Story not found</h2>
          <Link to="/" style={{ color: "hsl(var(--primary))" }}>← Back to home</Link>
        </div>
      </>
    );
  }

  const catColor = CATEGORY_COLORS[storyline.category || ""] || "#6D6D6D";
  const catLabel = CATEGORY_LABELS[storyline.category || ""] || (storyline.category || "").replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  const statusInfo = STATUS_STYLES[storyline.status] || STATUS_STYLES.active;

  return (
    <>
      <Masthead />
      <div className="container" style={{ maxWidth: 780, margin: "0 auto", padding: "24px 16px 60px" }}>

        {/* Breadcrumb */}
        <div style={{ marginBottom: 16, fontSize: 13, color: "hsl(var(--muted-foreground))" }}>
          <Link to="/" style={{ color: "inherit", textDecoration: "none" }}>Home</Link>
          <span style={{ margin: "0 6px" }}>›</span>
          <span>Developing Stories</span>
        </div>

        {/* Header */}
        <div style={{ marginBottom: 24, borderBottom: `3px solid ${catColor}`, paddingBottom: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
            <span style={{
              fontSize: 11, fontWeight: 600, color: catColor,
              background: `${catColor}15`, borderRadius: 3,
              padding: "2px 8px", textTransform: "uppercase",
              letterSpacing: "0.04em",
            }}>
              {catLabel}
            </span>
            <span style={{
              fontSize: 11, fontWeight: 600,
              color: statusInfo.color, background: statusInfo.bg,
              borderRadius: 3, padding: "2px 8px",
            }}>
              {statusInfo.label}
            </span>
          </div>

          <h1 style={{
            fontSize: 28, fontWeight: 800, lineHeight: 1.2,
            color: "hsl(var(--foreground))", margin: "0 0 12px",
            fontFamily: "'Playfair Display', Georgia, serif",
          }}>
            {storyline.title}
          </h1>

          {storyline.summary && (
            <p style={{
              fontSize: 16, lineHeight: 1.5,
              color: "hsl(var(--muted-foreground))",
              margin: 0,
            }}>
              {storyline.summary}
            </p>
          )}

          <div style={{
            display: "flex", gap: 16, marginTop: 14,
            fontSize: 13, color: "hsl(var(--muted-foreground))",
          }}>
            <span><strong>{storyline.article_count}</strong> articles</span>
            {storyline.first_article_at && storyline.last_article_at && (
              <span>{formatDate(storyline.first_article_at)} – {formatDate(storyline.last_article_at)}</span>
            )}
          </div>
        </div>

        {/* Medal Tracker (if available) */}
        {storyline.metadata?.medal_tracker && (
          <MedalTracker data={storyline.metadata.medal_tracker} />
        )}

        {/* Timeline */}
        <div style={{ position: "relative" }}>
          {/* Vertical line */}
          <div style={{
            position: "absolute", left: 15, top: 8, bottom: 8,
            width: 2, background: "hsl(var(--rule) / 0.3)",
            borderRadius: 1,
          }} />

          {articles.map((article, i) => (
            <Link
              key={article.id}
              to={`/articles/${article.slug}`}
              style={{
                display: "flex", gap: 16, padding: "14px 0 14px 40px",
                textDecoration: "none", color: "inherit",
                position: "relative",
                borderBottom: i < articles.length - 1 ? "1px solid hsl(var(--rule) / 0.15)" : "none",
              }}
            >
              {/* Timeline dot */}
              <div style={{
                position: "absolute", left: 10, top: 22,
                width: 12, height: 12, borderRadius: "50%",
                background: i === 0 ? catColor : "hsl(var(--rule) / 0.5)",
                border: `2px solid ${i === 0 ? catColor : "hsl(var(--rule) / 0.3)"}`,
                boxShadow: i === 0 ? `0 0 0 3px ${catColor}30` : "none",
              }} />

              {/* Content */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 11, color: "hsl(var(--muted-foreground))",
                  marginBottom: 4, fontWeight: 500,
                }}>
                  {formatDateShort(article.published_at)}
                </div>
                <h3 style={{
                  fontSize: 15, fontWeight: 600, lineHeight: 1.35,
                  color: "hsl(var(--foreground))", margin: 0,
                }}>
                  {article.headline}
                </h3>
              </div>

              {/* Thumbnail */}
              {article.image_url && (
                <div style={{
                  flex: "0 0 80px", width: 80, height: 54,
                  borderRadius: 6, overflow: "hidden",
                  background: "hsl(var(--muted) / 0.3)",
                }}>
                  <HeroImage
                    src={article.image_url}
                    alt=""
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                </div>
              )}
            </Link>
          ))}
        </div>

        {articles.length === 0 && (
          <p style={{ textAlign: "center", color: "hsl(var(--muted-foreground))", padding: "40px 0" }}>
            No articles linked to this story yet.
          </p>
        )}
      </div>
    </>
  );
}
