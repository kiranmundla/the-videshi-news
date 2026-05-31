import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { supabase } from "@/integrations/supabase/client";

interface Article {
  id: string;
  slug: string;
  headline: string;
  image_url: string | null;
  category: string | null;
  instagrammed_at: string;
}

export default function LinksPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const { data } = await supabase
        .from("p2_articles")
        .select("id,slug,headline,image_url,category,instagrammed_at")
        .eq("status", "published")
        .not("instagrammed_at", "is", null)
        .order("instagrammed_at", { ascending: false })
        .limit(10);
      setArticles((data as unknown as Article[]) ?? []);
      setLoading(false);
    })();
  }, []);

  const categoryColors: Record<string, string> = {
    news: "#ef4444",
    immigration: "#3b82f6",
    "nri-world": "#8b5cf6",
    sports: "#22c55e",
    entertainment: "#ec4899",
    markets: "#f59e0b",
    technology: "#06b6d4",
    travel: "#14b8a6",
    lifestyle: "#f97316",
    food: "#84cc16",
  };

  return (
    <>
      <Helmet>
        <title>Links · The Videshi</title>
        <meta name="description" content="Latest articles from The Videshi — your daily source for Indian diaspora news." />
        <meta name="robots" content="noindex" />
              <link rel="canonical" href="https://www.thevideshi.com/links" />
      </Helmet>

      <div
        style={{
          minHeight: "100vh",
          background: "linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
          padding: "0",
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        <div style={{ maxWidth: 480, margin: "0 auto", padding: "32px 16px 48px" }}>
          {/* Logo + Branding */}
          <div style={{ textAlign: "center", marginBottom: 32 }}>
            <img
              src="/logo.jpg"
              alt="The Videshi"
              style={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                margin: "0 auto 12px",
                display: "block",
                border: "3px solid rgba(212, 168, 67, 0.4)",
              }}
            />
            <h1
              style={{
                fontFamily: '"Playfair Display", Georgia, serif',
                fontSize: 24,
                fontWeight: 700,
                color: "#ffffff",
                margin: "0 0 4px",
              }}
            >
              The Videshi
            </h1>
            <p style={{ fontSize: 14, color: "rgba(255,255,255,0.6)", margin: 0 }}>
              Your daily source for Indian diaspora news
            </p>
          </div>

          {/* Website CTA */}
          <a
            href="https://www.thevideshi.com"
            style={{
              display: "block",
              textAlign: "center",
              padding: "14px 20px",
              background: "linear-gradient(135deg, #d4a843, #b8860b)",
              color: "#1a1a2e",
              fontWeight: 700,
              fontSize: 15,
              borderRadius: 12,
              textDecoration: "none",
              marginBottom: 24,
              letterSpacing: "0.3px",
            }}
          >
            🌐 Visit thevideshi.com
          </a>

          {/* Articles */}
          {loading ? (
            <div style={{ textAlign: "center", padding: 40 }}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  border: "3px solid rgba(212,168,67,0.3)",
                  borderTopColor: "#d4a843",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite",
                  margin: "0 auto",
                }}
              />
              <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
          ) : articles.length === 0 ? (
            <p style={{ textAlign: "center", color: "rgba(255,255,255,0.5)", fontSize: 14 }}>
              No articles posted yet. Check back soon!
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <p
                style={{
                  fontSize: 11,
                  textTransform: "uppercase",
                  letterSpacing: "1.5px",
                  color: "rgba(255,255,255,0.4)",
                  fontWeight: 600,
                  margin: "0 0 4px 4px",
                }}
              >
                Latest Stories
              </p>
              {articles.map((a) => (
                <a
                  key={a.id}
                  href={`/articles/${a.slug}`}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    padding: 12,
                    background: "rgba(255,255,255,0.06)",
                    borderRadius: 12,
                    textDecoration: "none",
                    transition: "background 0.2s, transform 0.15s",
                    border: "1px solid rgba(255,255,255,0.08)",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "rgba(212,168,67,0.12)";
                    e.currentTarget.style.borderColor = "rgba(212,168,67,0.3)";
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "rgba(255,255,255,0.06)";
                    e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)";
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  {/* Thumbnail */}
                  <div
                    style={{
                      width: 56,
                      height: 56,
                      minWidth: 56,
                      borderRadius: 8,
                      overflow: "hidden",
                      background: "rgba(255,255,255,0.1)",
                    }}
                  >
                    {a.image_url ? (
                      <img
                        src={a.image_url}
                        alt=""
                        loading="lazy"
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                    ) : (
                      <div
                        style={{
                          width: "100%",
                          height: "100%",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 22,
                        }}
                      >
                        📰
                      </div>
                    )}
                  </div>

                  {/* Text */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {a.category && (
                      <span
                        style={{
                          display: "inline-block",
                          fontSize: 10,
                          fontWeight: 700,
                          textTransform: "uppercase",
                          letterSpacing: "0.8px",
                          color: categoryColors[a.category] ?? "#d4a843",
                          marginBottom: 3,
                        }}
                      >
                        {a.category.replace(/-/g, " ")}
                      </span>
                    )}
                    <p
                      style={{
                        fontSize: 14,
                        lineHeight: 1.35,
                        fontWeight: 600,
                        color: "#ffffff",
                        margin: 0,
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {a.headline}
                    </p>
                  </div>

                  {/* Arrow */}
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="rgba(255,255,255,0.3)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    style={{ minWidth: 16 }}
                  >
                    <polyline points="9 18 15 12 9 6" />
                  </svg>
                </a>
              ))}
            </div>
          )}

          {/* Social Links */}
          <div style={{ marginTop: 32, textAlign: "center" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: 16,
                marginBottom: 16,
              }}
            >
              {/* Instagram */}
              <a
                href="https://www.instagram.com/the.videshi"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 44,
                  height: 44,
                  borderRadius: "50%",
                  background: "rgba(255,255,255,0.08)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  textDecoration: "none",
                  transition: "background 0.2s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(212,168,67,0.15)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.08)")}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="5" />
                  <circle cx="12" cy="12" r="5" />
                  <circle cx="17.5" cy="6.5" r="1.2" fill="#ffffff" stroke="none" />
                </svg>
              </a>

              {/* X / Twitter */}
              <a
                href="https://x.com/thevideshi"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 44,
                  height: 44,
                  borderRadius: "50%",
                  background: "rgba(255,255,255,0.08)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  textDecoration: "none",
                  transition: "background 0.2s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(212,168,67,0.15)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.08)")}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="#ffffff">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>

              {/* Website */}
              <a
                href="https://www.thevideshi.com"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 44,
                  height: 44,
                  borderRadius: "50%",
                  background: "rgba(255,255,255,0.08)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  textDecoration: "none",
                  transition: "background 0.2s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(212,168,67,0.15)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.08)")}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
              </a>
            </div>

            <p style={{ fontSize: 12, color: "rgba(255,255,255,0.3)", margin: 0 }}>
              © {new Date().getFullYear()} The Videshi
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
