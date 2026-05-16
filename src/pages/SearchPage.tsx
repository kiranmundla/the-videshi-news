import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import { Article } from "@/lib/articles";
import { searchArticles } from "@/lib/articles";

export default function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [results, setResults] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setSearched(false);
      return;
    }
    setLoading(true);
    searchArticles(query.trim())
      .then((data) => {
        setResults(data);
        setSearched(true);
      })
      .catch(() => {
        setResults([]);
        setSearched(true);
      })
      .finally(() => setLoading(false));
  }, [query]);

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{query ? `"${query}" — Search — The Videshi` : "Search — The Videshi"}</title>
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 py-8">
        <h1 className="font-serif text-2xl md:text-3xl font-bold mb-1">
          Search
        </h1>
        {query && (
          <p className="text-muted-foreground text-sm mb-6">
            {loading
              ? "Searching…"
              : searched
              ? `${results.length} result${results.length !== 1 ? "s" : ""} for "${query}"`
              : ""}
          </p>
        )}

        {!query && !searched && (
          <p className="text-muted-foreground mt-4">Enter a search term to find articles.</p>
        )}

        {searched && results.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground text-lg">No articles found for "{query}"</p>
            <Link to="/" className="text-primary hover:underline text-sm mt-2 inline-block">
              ← Back to homepage
            </Link>
          </div>
        )}

        {results.length > 0 && (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {results.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
