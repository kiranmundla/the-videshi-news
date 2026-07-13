import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import LoadMoreButton from "@/components/LoadMoreButton";
import KeyUpdatesSection from "@/components/KeyUpdatesSection";
import { Article, getArticlesByCategory } from "@/lib/articles";
import { getCategoryBySlug } from "@/lib/categories";
import { getSubTopicDef, SUB_TOPIC_SEO } from "@/components/homepage/CategorySubTopics";
import NotFound from "@/pages/NotFound";

const PAGE_SIZE = 18;

export default function SubTopicPage() {
  const { category = "", subtopic = "" } = useParams();
  const catDef = getCategoryBySlug(category);
  const stDef = getSubTopicDef(category, subtopic);

  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [fadeFrom, setFadeFrom] = useState(0);

  useEffect(() => {
    if (!catDef?.hasPipeline || !stDef) {
      setArticles([]);
      setLoading(false);
      setHasMore(false);
      return;
    }

    setLoading(true);
    setHasMore(true);
    setFadeFrom(0);

    // Fetch category articles, then filter by sub-topic tags client-side
    const tagSet = new Set(stDef.tags);

    const filterByTags = (items: Article[]) =>
      items.filter((a) =>
        (a.tags ?? []).some((t: string) => tagSet.has(t.toLowerCase()))
      );

    // Try static JSON first, then Supabase
    fetch(`/data/category/${catDef.slug}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then((data) => {
        const all: Article[] = data.articles ?? [];
        const filtered = filterByTags(all);
        setArticles(filtered.slice(0, PAGE_SIZE));
        setHasMore(filtered.length > PAGE_SIZE);
        // Cache full filtered list for load-more
        (window as any).__subTopicPool = {
          key: `${category}/${subtopic}`,
          articles: filtered,
        };
        setLoading(false);
      })
      .catch(() => {
        // Fallback to Supabase — fetch a larger batch to filter
        getArticlesByCategory(catDef.slug, 100, 0)
          .then((all) => {
            const filtered = filterByTags(all);
            setArticles(filtered.slice(0, PAGE_SIZE));
            setHasMore(filtered.length > PAGE_SIZE);
            (window as any).__subTopicPool = {
              key: `${category}/${subtopic}`,
              articles: filtered,
            };
            setLoading(false);
          })
          .catch(() => {
            setArticles([]);
            setLoading(false);
            setHasMore(false);
          });
      });
  }, [catDef?.slug, catDef?.hasPipeline, stDef, category, subtopic]);

  const loadMore = () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    const pool = (window as any).__subTopicPool;
    if (pool?.key === `${category}/${subtopic}`) {
      const next = pool.articles.slice(
        articles.length,
        articles.length + PAGE_SIZE
      );
      if (next.length < PAGE_SIZE) setHasMore(false);
      setFadeFrom(articles.length);
      setArticles((prev: Article[]) => [...prev, ...next]);
    } else {
      setHasMore(false);
    }
    setLoadingMore(false);
  };

  if (!catDef || !stDef) return <NotFound />;

  const seo = SUB_TOPIC_SEO[subtopic] ?? {
    title: `${stDef.label} — ${catDef.label} — The Videshi`,
    description: `Latest ${stDef.label.toLowerCase()} news and analysis for the Indian diaspora.`,
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{seo.title}</title>
        <meta name="description" content={seo.description} />
        <link
          rel="canonical"
          href={`https://www.thevideshi.com/${category}/${subtopic}`}
        />
      </Helmet>
      <Masthead />
      <CategoryPills />
      <main className="container flex-1 pt-8 md:pt-10">
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-[2px] text-muted-foreground mb-1">
            {catDef.label}
          </p>
          <h1 className="font-serif text-3xl md:text-5xl text-foreground">
            {stDef.label}
          </h1>
        </div>

        <KeyUpdatesSection category={catDef.slug} limit={10} className="mb-10" />

        {loading ? (
          <p className="py-20 text-center text-muted-foreground">Loading…</p>
        ) : articles.length === 0 ? (
          <p className="py-20 text-center text-muted-foreground">
            No stories yet — check back soon.
          </p>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-4 md:gap-x-10 gap-y-8 md:gap-y-16">
              {articles.map((a, i) => (
                <div
                  key={a.id}
                  className={i >= fadeFrom ? "animate-fade-in" : ""}
                >
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
