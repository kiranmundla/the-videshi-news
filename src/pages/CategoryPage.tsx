import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
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

        {!def.hasPipeline ? (
          <p className="py-20 text-center text-muted-foreground">
            {def.slug === "events" ? "Community events coming soon." : "Be the first to post."}
          </p>
        ) : loading ? (
          <p className="py-20 text-center text-muted-foreground">Loading…</p>
        ) : articles.length === 0 ? (
          <p className="py-20 text-center text-muted-foreground">No stories yet in this section.</p>
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
