import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import { Article, getArticlesByCategory } from "@/lib/articles";
import { getCategoryBySlug } from "@/lib/categories";
import NotFound from "@/pages/NotFound";

const PER_PAGE = 12;

export default function CategoryPage() {
  const { category = "" } = useParams();
  const def = getCategoryBySlug(category);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setPage(1);
    if (!def?.hasPipeline) { setLoading(false); return; }
    setLoading(true);
    getArticlesByCategory(def.slug, 240).then((a) => {
      setArticles(a);
      setLoading(false);
    });
  }, [def?.slug, def?.hasPipeline]);

  const totalPages = Math.max(1, Math.ceil(articles.length / PER_PAGE));
  const visible = useMemo(
    () => articles.slice((page - 1) * PER_PAGE, page * PER_PAGE),
    [articles, page]
  );

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
              {visible.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" hideCategory />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-16">
                <button
                  onClick={() => { setPage((p) => Math.max(1, p - 1)); window.scrollTo({ top: 0, behavior: "smooth" }); }}
                  disabled={page === 1}
                  className="smallcaps px-4 py-2 border border-rule rounded-full disabled:opacity-30 hover:text-primary hover:border-primary transition-colors"
                >
                  ← Prev
                </button>
                <span className="smallcaps text-foreground/70 px-4">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => { setPage((p) => Math.min(totalPages, p + 1)); window.scrollTo({ top: 0, behavior: "smooth" }); }}
                  disabled={page === totalPages}
                  className="smallcaps px-4 py-2 border border-rule rounded-full disabled:opacity-30 hover:text-primary hover:border-primary transition-colors"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
