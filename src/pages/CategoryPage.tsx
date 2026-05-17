import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import TechBuzz from "@/components/TechBuzz";
import LoadMoreButton from "@/components/LoadMoreButton";
import { Article, getArticlesByCategory } from "@/lib/articles";
import { getCategoryBySlug } from "@/lib/categories";
import NotFound from "@/pages/NotFound";

const PAGE_SIZE = 12;

export default function CategoryPage() {
  const { category = "" } = useParams();
  const def = getCategoryBySlug(category);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [fadeFrom, setFadeFrom] = useState(0);

  useEffect(() => {
    if (!def?.hasPipeline) {
      setArticles([]);
      setLoading(false);
      setHasMore(false);
      return;
    }
    setLoading(true);
    setHasMore(true);
    setFadeFrom(0);
    getArticlesByCategory(def.slug, PAGE_SIZE, 0).then((a) => {
      setArticles(a);
      setHasMore(a.length === PAGE_SIZE);
      setLoading(false);
    });
  }, [def?.slug, def?.hasPipeline]);

  const loadMore = async () => {
    if (!def?.hasPipeline || loadingMore || !hasMore) return;
    setLoadingMore(true);
    const next = await getArticlesByCategory(def.slug, PAGE_SIZE, articles.length);
    if (next.length < PAGE_SIZE) setHasMore(false);
    setFadeFrom(articles.length);
    setArticles((prev) => [...prev, ...next]);
    setLoadingMore(false);
  };

  if (!def) return <NotFound />;

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{def.label} — The Videshi</title>
        <meta name="description" content={`${def.label} stories from The Videshi.`} />
        <link rel="canonical" href={def.path} />
      </Helmet>
      <Masthead />
      <CategoryPills />
      <main className="container flex-1 pt-8 md:pt-10">
        <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-8">{def.label}</h1>

        {def.slug === "news" && <TechBuzz category="world" />}
        {def.slug === "technology" && <TechBuzz category="tech" />}

        {def.slug === "travel" && (
          <div style={{ display: "flex", gap: 8, overflowX: "auto", paddingBottom: 20, marginBottom: 8, WebkitOverflowScrolling: "touch" as any }}>
            {[
              { key: "rajasthan", label: "Rajasthan" },
              { key: "kerala", label: "Kerala" },
              { key: "goa", label: "Goa" },
              { key: "maldives", label: "Maldives" },
              { key: "sri-lanka", label: "Sri Lanka" },
              { key: "bali", label: "Bali" },
              { key: "london", label: "London & UK" },
              { key: "switzerland", label: "Switzerland" },
              { key: "new-zealand", label: "New Zealand" },
              { key: "mexico", label: "Mexico" },
            ].map((d) => (
              <Link key={d.key} to={`/travel/${d.key}`} style={{
                padding: "7px 16px", borderRadius: 20, fontSize: 13, fontWeight: 600,
                textDecoration: "none", letterSpacing: "0.05em", textTransform: "uppercase" as any,
                background: "#1a1a1a", color: "#fff", border: "1px solid #1a1a1a",
                whiteSpace: "nowrap" as any, flexShrink: 0,
              }}>
                {d.label}
              </Link>
            ))}
          </div>
        )}

        {!def.hasPipeline ? (
          <p className="py-20 text-center text-muted-foreground">
            {def.slug === "events" ? "Community events coming soon." : "Be the first to post."}
          </p>
        ) : loading ? (
          <p className="py-20 text-center text-muted-foreground">Loading…</p>
        ) : articles.length === 0 ? (
          <p className="py-20 text-center text-muted-foreground">
            {def.slug === "travel" ? "Explore our destination guides above." : "We're publishing fresh stories — check back in a few hours."}
          </p>
        ) : (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-x-4 md:gap-x-10 gap-y-12 md:gap-y-16">
              {articles.map((a, i) => (
                <div key={a.id} className={i >= fadeFrom ? "animate-fade-in" : ""}>
                  <ArticleCard article={a} variant="card" hideCategory />
                </div>
              ))}
            </div>

            <LoadMoreButton
              onClick={loadMore}
              loading={loadingMore}
              hasMore={hasMore}
            />
          </>
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
