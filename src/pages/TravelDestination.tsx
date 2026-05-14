import { useEffect, useState, useMemo } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import ReactMarkdown from "react-markdown";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { Article, getArticlesByCategory, readingTime } from "@/lib/articles";
import { supabase } from "@/integrations/supabase/client";

/* ─── destination metadata ─── */
interface DestMeta {
  title: string;
  bestMonths: string;
  budget: string;
  flights: string;
  visa: string;
  articleSlug: string;
}

const DESTINATIONS: Record<string, DestMeta> = {
  rajasthan:    { title: "Rajasthan",       bestMonths: "Oct – Mar",          budget: "$30–150/day", flights: "Delhi, Jaipur direct",       visa: "Indian passport: no visa",   articleSlug: "rajasthan-travel-guide-diaspora" },
  kerala:       { title: "Kerala",          bestMonths: "Sep – Mar",          budget: "$25–120/day", flights: "Kochi, Trivandrum direct",   visa: "Indian passport: no visa",   articleSlug: "kerala-travel-guide-diaspora" },
  goa:          { title: "Goa",             bestMonths: "Nov – Feb",          budget: "$20–100/day", flights: "Goa/Dabolim direct",         visa: "Indian passport: no visa",   articleSlug: "goa-travel-guide-diaspora" },
  maldives:     { title: "Maldives",        bestMonths: "Nov – Apr",          budget: "$80–500/day", flights: "Malé from Delhi, Mumbai",    visa: "Free 30-day on arrival",     articleSlug: "maldives-travel-guide-diaspora" },
  "sri-lanka":  { title: "Sri Lanka",       bestMonths: "Dec – Mar",          budget: "$30–100/day", flights: "Colombo from Chennai, Delhi",visa: "ETA online",                 articleSlug: "sri-lanka-travel-guide-diaspora" },
  bali:         { title: "Bali",            bestMonths: "Apr – Oct",          budget: "$30–150/day", flights: "Denpasar via Singapore/KL",  visa: "Free 30-day on arrival",     articleSlug: "bali-travel-guide-diaspora" },
  london:       { title: "London & UK",     bestMonths: "May – Sep",          budget: "$80–250/day", flights: "Direct from Delhi, Mumbai",  visa: "UK visa required",           articleSlug: "london-uk-travel-guide-diaspora" },
  switzerland:  { title: "Switzerland",     bestMonths: "Jun – Sep, Dec – Feb",budget: "$100–350/day",flights: "Zürich via Europe",          visa: "Schengen visa required",     articleSlug: "switzerland-travel-guide-diaspora" },
  "new-zealand":{ title: "New Zealand",     bestMonths: "Dec – Feb",          budget: "$80–200/day", flights: "Auckland via Singapore",     visa: "eVisa or NZeTA",             articleSlug: "new-zealand-travel-guide-diaspora" },
  mexico:       { title: "Mexico",          bestMonths: "Nov – Apr",          budget: "$40–150/day", flights: "Mexico City direct from US", visa: "Visa-free with US visa",     articleSlug: "mexico-travel-guide-diaspora" },
};

const DEST_KEYS = Object.keys(DESTINATIONS);

/* ─── helpers ─── */
function extractSections(body: string): { id: string; label: string }[] {
  const re = /^## (.+)$/gm;
  const out: { id: string; label: string }[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(body)) !== null) {
    const label = m[1].trim();
    const id = label.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    out.push({ id, label });
  }
  return out;
}

/* ─── component ─── */
export default function TravelDestination() {
  const { destination = "" } = useParams();
  const navigate = useNavigate();
  const meta = DESTINATIONS[destination];

  const [article, setArticle] = useState<Article | null>(null);
  const [allTravel, setAllTravel] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  /* fetch article + related */
  useEffect(() => {
    if (!meta) { setLoading(false); return; }
    setLoading(true);

    const sb = supabase as any;

    const fetchArticle = sb
      .from("p2_articles")
      .select("id, slug, headline, subheadline, body, vertical, category, status, is_featured, published_at, created_at, sources, diaspora_angle, tags, image_url, image_attribution")
      .eq("slug", meta.articleSlug)
      .eq("status", "published")
      .limit(1)
      .single()
      .then(({ data }: any) => {
        if (data) {
          setArticle({
            id: data.id,
            slug: data.slug ?? data.id,
            title: data.headline,
            excerpt: data.subheadline ?? "",
            body: data.body ?? "",
            category: data.category ?? data.vertical ?? "",
            hero_image_url: data.image_url ?? "",
            image_caption: null,
            image_credit: data.image_attribution ?? null,
            published_at: data.published_at ?? data.created_at,
            created_at: data.created_at,
            status: "published" as const,
            sources: [],
            article_type: "news" as const,
          });
        }
      });

    const fetchAll = getArticlesByCategory("travel", 20).then(setAllTravel);

    Promise.all([fetchArticle, fetchAll]).finally(() => setLoading(false));
  }, [meta, destination]);

  const sections = useMemo(() => (article ? extractSections(article.body) : []), [article]);

  const related = useMemo(() => {
    return allTravel
      .filter((a) => a.slug !== article?.slug)
      .sort(() => Math.random() - 0.5)
      .slice(0, 3);
  }, [allTravel, article]);

  /* ─── 404 ─── */
  if (!meta && !loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <Masthead />
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", padding: 40 }}>
          <h2 style={{ fontFamily: "serif", fontSize: 32, marginBottom: 16 }}>Destination not found</h2>
          <Link to="/travel" style={{ color: "#b91c1c", textDecoration: "underline" }}>← Back to Travel</Link>
        </div>
        <SiteFooter />
      </div>
    );
  }

  if (loading || !meta) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <Masthead />
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 40 }}>
          <p style={{ color: "#888", fontFamily: "serif", fontSize: 18 }}>Loading…</p>
        </div>
        <SiteFooter />
      </div>
    );
  }

  const heroUrl = article?.hero_image_url || "";

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Helmet>
        <title>{meta.title} Travel Guide — The Videshi</title>
        <meta name="description" content={`Complete diaspora travel guide to ${meta.title}. Best months, budget tips, visa info, and more.`} />
      </Helmet>

      <Masthead />

      {/* ─── Destination pills nav ─── */}
      <div style={{ background: "#fafaf8", borderBottom: "1px solid #e5e5e0" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 20px", overflowX: "auto", WebkitOverflowScrolling: "touch" }}>
          <div style={{ display: "flex", gap: 8, padding: "12px 0", whiteSpace: "nowrap" as const }}>
            <Link to="/travel" style={{
              padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600,
              textDecoration: "none", letterSpacing: "0.05em", textTransform: "uppercase" as const,
              background: "transparent", color: "#666", border: "1px solid #ccc",
            }}>All</Link>
            {DEST_KEYS.map((key) => {
              const active = key === destination;
              return (
                <Link key={key} to={`/travel/${key}`} style={{
                  padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600,
                  textDecoration: "none", letterSpacing: "0.05em", textTransform: "uppercase" as const,
                  background: active ? "#1a1a1a" : "transparent",
                  color: active ? "#fff" : "#666",
                  border: active ? "1px solid #1a1a1a" : "1px solid #ccc",
                  transition: "all 0.2s",
                }}>
                  {DESTINATIONS[key].title}
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* ─── Breadcrumb ─── */}
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "14px 20px 0" }}>
        <nav style={{ fontSize: 13, color: "#888", letterSpacing: "0.03em", textTransform: "uppercase" as const }}>
          <Link to="/" style={{ color: "#888", textDecoration: "none" }}>Home</Link>
          <span style={{ margin: "0 6px" }}>›</span>
          <Link to="/travel" style={{ color: "#888", textDecoration: "none" }}>Travel</Link>
          <span style={{ margin: "0 6px" }}>›</span>
          <span style={{ color: "#333" }}>{meta.title}</span>
        </nav>
      </div>

      {/* ─── Hero ─── */}
      <div style={{
        position: "relative", width: "100%", maxWidth: 1200, margin: "16px auto 0",
        height: 420, overflow: "hidden", borderRadius: 8,
        background: "#1a1a1a",
      }}>
        {heroUrl && (
          <img src={heroUrl} alt={meta.title}
            style={{ width: "100%", height: "100%", objectFit: "cover", display: "block", opacity: 0.85 }} />
        )}
        <div style={{
          position: "absolute", inset: 0,
          background: "linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.1) 100%)",
        }} />
        <div style={{
          position: "absolute", bottom: 0, left: 0, right: 0, padding: "40px 36px",
        }}>
          <p style={{ color: "rgba(255,255,255,0.7)", fontSize: 13, letterSpacing: "0.12em", textTransform: "uppercase" as const, marginBottom: 8, fontWeight: 600 }}>
            Diaspora Travel Guide
          </p>
          <h1 style={{ fontFamily: "serif", fontSize: 48, fontWeight: 900, color: "#fff", lineHeight: 1.1, margin: 0 }}>
            {meta.title}
          </h1>
          {article && (
            <p style={{ color: "rgba(255,255,255,0.8)", fontSize: 15, marginTop: 12, maxWidth: 600, lineHeight: 1.5 }}>
              {article.excerpt || article.title}
            </p>
          )}
        </div>
      </div>

      {/* ─── Quick Facts Bar ─── */}
      <div style={{
        maxWidth: 1200, margin: "0 auto", padding: "0 20px",
      }}>
        <div style={{
          display: "flex", flexWrap: "wrap" as const, gap: 0,
          background: "#f5f5f0", borderRadius: "0 0 8px 8px",
          overflow: "hidden",
        }}>
          {[
            { icon: "🗓", label: "Best Months", value: meta.bestMonths },
            { icon: "💰", label: "Budget", value: meta.budget },
            { icon: "✈️", label: "Flights", value: meta.flights },
            { icon: "🛂", label: "Visa", value: meta.visa },
          ].map((fact, i) => (
            <div key={i} style={{
              flex: "1 1 140px", padding: "16px 20px",
              borderRight: i < 3 ? "1px solid #e5e5e0" : "none",
              minWidth: 140,
            }}>
              <div style={{ fontSize: 11, color: "#888", textTransform: "uppercase" as const, letterSpacing: "0.08em", marginBottom: 4, fontWeight: 600 }}>
                {fact.icon} {fact.label}
              </div>
              <div style={{ fontSize: 14, color: "#333", fontWeight: 500 }}>{fact.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ─── Main content + sidebar ─── */}
      <div style={{ maxWidth: 1200, margin: "32px auto 0", padding: "0 20px", display: "flex", gap: 40, alignItems: "flex-start" }}>

        {/* Article content */}
        <article style={{ flex: "1 1 0%", minWidth: 0, maxWidth: 780 }}>
          {article ? (
            <div className="prose-article" style={{ fontFamily: "Georgia, serif", fontSize: 17, lineHeight: 1.8, color: "#222" }}>
              <ReactMarkdown
                components={{
                  h1: ({ children }) => <h1 style={{ fontFamily: "serif", fontSize: 32, fontWeight: 800, margin: "32px 0 16px", color: "#111", lineHeight: 1.2 }}>{children}</h1>,
                  h2: ({ children }) => {
                    const text = String(children);
                    const id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
                    return <h2 id={id} style={{ fontFamily: "serif", fontSize: 26, fontWeight: 700, margin: "36px 0 14px", color: "#111", lineHeight: 1.25, borderBottom: "1px solid #e5e5e0", paddingBottom: 8 }}>{children}</h2>;
                  },
                  h3: ({ children }) => <h3 style={{ fontFamily: "serif", fontSize: 20, fontWeight: 600, margin: "28px 0 10px", color: "#222" }}>{children}</h3>,
                  p: ({ children }) => <p style={{ margin: "0 0 18px", lineHeight: 1.8 }}>{children}</p>,
                  ul: ({ children }) => <ul style={{ margin: "0 0 18px", paddingLeft: 24 }}>{children}</ul>,
                  ol: ({ children }) => <ol style={{ margin: "0 0 18px", paddingLeft: 24 }}>{children}</ol>,
                  li: ({ children }) => <li style={{ marginBottom: 8, lineHeight: 1.7 }}>{children}</li>,
                  strong: ({ children }) => <strong style={{ fontWeight: 700, color: "#111" }}>{children}</strong>,
                  blockquote: ({ children }) => <blockquote style={{ borderLeft: "3px solid #b91c1c", paddingLeft: 16, margin: "20px 0", color: "#555", fontStyle: "italic" }}>{children}</blockquote>,
                }}
              >
                {article.body}
              </ReactMarkdown>
            </div>
          ) : (
            <p style={{ color: "#888", fontStyle: "italic" }}>Guide content is being prepared…</p>
          )}
        </article>

        {/* Sidebar */}
        <aside style={{ width: 300, flexShrink: 0, position: "sticky" as const, top: 24 }}
          className="travel-sidebar"
        >
          {/* Quick Links */}
          {sections.length > 0 && (
            <div style={{ marginBottom: 28, background: "#fafaf8", borderRadius: 8, padding: "20px 20px 12px", border: "1px solid #e5e5e0" }}>
              <h3 style={{ fontFamily: "serif", fontSize: 16, fontWeight: 700, margin: "0 0 12px", color: "#333", textTransform: "uppercase" as const, letterSpacing: "0.06em" }}>
                In This Guide
              </h3>
              {sections.map((s) => (
                <a key={s.id} href={`#${s.id}`} style={{
                  display: "block", padding: "7px 0", fontSize: 14, color: "#555",
                  textDecoration: "none", borderBottom: "1px solid #eee",
                  transition: "color 0.2s",
                }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = "#b91c1c")}
                  onMouseLeave={(e) => (e.currentTarget.style.color = "#555")}
                >
                  {s.label}
                </a>
              ))}
            </div>
          )}

          {/* At a Glance */}
          <div style={{ marginBottom: 28, background: "#fafaf8", borderRadius: 8, padding: 20, border: "1px solid #e5e5e0" }}>
            <h3 style={{ fontFamily: "serif", fontSize: 16, fontWeight: 700, margin: "0 0 14px", color: "#333", textTransform: "uppercase" as const, letterSpacing: "0.06em" }}>
              At a Glance
            </h3>
            {[
              { label: "Best Months", value: meta.bestMonths },
              { label: "Daily Budget", value: meta.budget },
              { label: "Flights", value: meta.flights },
              { label: "Visa", value: meta.visa },
            ].map((row, i) => (
              <div key={i} style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: "#888", textTransform: "uppercase" as const, letterSpacing: "0.08em", fontWeight: 600 }}>{row.label}</div>
                <div style={{ fontSize: 14, color: "#333", marginTop: 2 }}>{row.value}</div>
              </div>
            ))}
          </div>

          {/* Ad Space placeholder */}
          <div style={{
            marginBottom: 28, borderRadius: 8, padding: 40,
            border: "2px dashed #ddd", textAlign: "center" as const,
          }}>
            <p style={{ color: "#bbb", fontSize: 12, textTransform: "uppercase" as const, letterSpacing: "0.1em", margin: 0 }}>Advertisement</p>
          </div>

          {/* Other Destinations */}
          {related.length > 0 && (
            <div style={{ marginBottom: 28 }}>
              <h3 style={{ fontFamily: "serif", fontSize: 16, fontWeight: 700, margin: "0 0 14px", color: "#333", textTransform: "uppercase" as const, letterSpacing: "0.06em" }}>
                More Destinations
              </h3>
              {related.map((r) => {
                const destKey = DEST_KEYS.find((k) => r.slug.includes(k)) || "";
                return (
                  <Link key={r.slug} to={destKey ? `/travel/${destKey}` : `/articles/${r.slug}`}
                    style={{ display: "flex", gap: 12, marginBottom: 14, textDecoration: "none", alignItems: "center" }}>
                    {r.hero_image_url && (
                      <img src={r.hero_image_url} alt={r.title}
                        style={{ width: 70, height: 50, objectFit: "cover", borderRadius: 6, flexShrink: 0 }} />
                    )}
                    <span style={{ fontFamily: "serif", fontSize: 14, fontWeight: 600, color: "#333", lineHeight: 1.3 }}>
                      {r.title}
                    </span>
                  </Link>
                );
              })}
            </div>
          )}
        </aside>
      </div>

      {/* ─── Related Destinations (full-width bottom section) ─── */}
      {related.length > 0 && (
        <div style={{ maxWidth: 1200, margin: "48px auto 0", padding: "0 20px 40px" }}>
          <div style={{ borderTop: "1px solid #e5e5e0", paddingTop: 28 }}>
            <h2 style={{ fontFamily: "serif", fontSize: 22, fontWeight: 700, marginBottom: 20, color: "#222" }}>
              Explore More Destinations
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 24 }}>
              {related.map((r) => {
                const destKey = DEST_KEYS.find((k) => r.slug.includes(k)) || "";
                const destMeta = destKey ? DESTINATIONS[destKey] : null;
                return (
                  <Link key={r.slug} to={destKey ? `/travel/${destKey}` : `/articles/${r.slug}`}
                    style={{ textDecoration: "none", borderRadius: 8, overflow: "hidden", border: "1px solid #e5e5e0", transition: "box-shadow 0.2s" }}
                    onMouseEnter={(e) => (e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.1)")}
                    onMouseLeave={(e) => (e.currentTarget.style.boxShadow = "none")}
                  >
                    <div style={{ position: "relative", height: 180, overflow: "hidden" }}>
                      {r.hero_image_url && (
                        <img src={r.hero_image_url} alt={r.title}
                          style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                      )}
                      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(0,0,0,0.5), transparent)" }} />
                      <div style={{ position: "absolute", bottom: 12, left: 14 }}>
                        <span style={{ fontFamily: "serif", fontSize: 20, fontWeight: 800, color: "#fff" }}>
                          {destMeta?.title || r.title}
                        </span>
                      </div>
                    </div>
                    <div style={{ padding: "12px 14px" }}>
                      <p style={{ fontSize: 13, color: "#666", margin: 0, lineHeight: 1.4 }}>{r.title}</p>
                      {destMeta && (
                        <p style={{ fontSize: 12, color: "#999", margin: "6px 0 0", letterSpacing: "0.03em" }}>
                          🗓 {destMeta.bestMonths} · 💰 {destMeta.budget}
                        </p>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      )}

      <div style={{ flex: 1 }} />
      <SiteFooter />

      {/* ─── Responsive: hide sidebar on mobile ─── */}
      <style>{`
        @media (max-width: 840px) {
          .travel-sidebar { display: none !important; }
        }
      `}</style>
    </div>
  );
}
