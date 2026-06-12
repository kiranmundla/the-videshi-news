import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import TechBuzz from "@/components/TechBuzz";
import WorldCupTracker from "@/components/WorldCupTracker";
// import CelebrityBuzz from "@/components/CelebrityBuzz"; // temporarily hidden
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

    const applyArticles = (a: Article[]) => {
      setArticles(a);
      setHasMore(a.length >= PAGE_SIZE);
      setLoading(false);
    };

    // Fast path: try pre-built static JSON (same pattern as homepage)
    fetch(`/data/category/${def.slug}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then((data) => {
        const items: Article[] = data.articles ?? [];
        applyArticles(items.slice(0, PAGE_SIZE));
        // Store full list for loadMore without hitting Supabase
        (window as any).__categoryPool = { slug: def.slug, articles: items };
      })
      .catch(() => {
        // Static feed unavailable — fall back to Supabase
        getArticlesByCategory(def.slug, PAGE_SIZE, 0)
          .then(applyArticles)
          .catch((err) => {
            console.error("[CategoryPage] fetch failed", err);
            applyArticles([]);
          });
      });
  }, [def?.slug, def?.hasPipeline]);

  const loadMore = async () => {
    if (!def?.hasPipeline || loadingMore || !hasMore) return;
    setLoadingMore(true);
    try {
      // Try loading more from cached static pool first
      const pool = (window as any).__categoryPool;
      let next: Article[];
      if (pool?.slug === def.slug && pool.articles.length > articles.length) {
        next = pool.articles.slice(articles.length, articles.length + PAGE_SIZE);
      } else {
        next = await getArticlesByCategory(def.slug, PAGE_SIZE, articles.length);
      }
      if (next.length < PAGE_SIZE) setHasMore(false);
      setFadeFrom(articles.length);
      setArticles((prev) => [...prev, ...next]);
    } catch (err) {
      console.error("[CategoryPage] loadMore failed", err);
    }
    setLoadingMore(false);
  };

  if (!def) return <NotFound />;

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{def.label} — The Videshi</title>
        <meta name="description" content={`${def.label} stories from The Videshi.`} />
        <link rel="canonical" href={`https://www.thevideshi.com${def.path}`} />
      </Helmet>
      <Masthead />
      <CategoryPills />
      <main className="container flex-1 pt-8 md:pt-10">
        <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-8">{def.label}</h1>

        {def.slug === "news" && <TechBuzz category="world" />}
        {def.slug === "news" && <TechBuzz category="india" />}
        {def.slug === "technology" && <TechBuzz category="tech" />}
        {/* {def.slug === "entertainment" && <CelebrityBuzz />} */}
        {def.slug === "sports" && <WorldCupTracker />}
        {def.slug === "sports" && <TechBuzz category="sports" />}

        {def.slug === "food" && (
          <Link
            to="/directory?category=Catering+%26+Food&subcategory=Michelin+Star"
            className="block mb-8 rounded-xl overflow-hidden border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 hover:from-amber-100 hover:to-orange-100 transition-colors"
          >
            <div className="flex items-center gap-3 px-5 py-4">
              <span className="text-2xl">⭐</span>
              <div className="flex-1 min-w-0">
                <p className="font-serif text-lg font-semibold text-foreground leading-tight">
                  Michelin-Starred Indian Restaurants
                </p>
                <p className="text-sm text-muted-foreground mt-0.5">
                  Discover the finest Indian dining across America
                </p>
              </div>
              <span className="text-muted-foreground text-xl shrink-0">→</span>
            </div>
          </Link>
        )}

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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-4 md:gap-x-10 gap-y-8 md:gap-y-16">
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
