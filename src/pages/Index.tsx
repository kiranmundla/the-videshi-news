import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import PlaceholderCard from "@/components/PlaceholderCard";
import SectionRule from "@/components/SectionRule";
import { Article, getPublishedArticles } from "@/lib/articles";

export default function Index() {
  const [allArticles, setAllArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [searchParams] = useSearchParams();
  const category = searchParams.get("c");

  useEffect(() => {
    getPublishedArticles().then((a) => {
      setAllArticles(a);
      setLastUpdated(new Date());
      setLoading(false);
    });
  }, []);

  const articles = useMemo(() => {
    if (!category) return allArticles;
    const needle = category.toLowerCase();
    return allArticles.filter((a) =>
      (a.category ?? "").toLowerCase().includes(needle),
    );
  }, [allArticles, category]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  const [hero, f1, f2, m1, m2, c1, c2, c3, longRead, also1, also2] = articles;
  const remaining = articles.slice(11);

  const slot = (
    a: Article | undefined,
    variant: "hero" | "featured" | "card" | "long" | "compact"
  ) =>
    a ? <ArticleCard article={a} variant={variant} /> : <PlaceholderCard variant={variant} />;

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>The Videshi — News for the global Indian diaspora</title>
        <meta
          name="description"
          content="Editorial reporting and analysis for the global Indian diaspora — India, NRI affairs, US-India, business, culture, sports, and voices."
        />
        <meta property="og:title" content="The Videshi" />
        <meta property="og:description" content="News for the global Indian diaspora" />
        {hero && <meta property="og:image" content={hero.hero_image_url} />}
        <link rel="canonical" href="/" />
      </Helmet>

      <Masthead />

      <main className="container flex-1 pt-8 md:pt-10">
        {/* Hero */}
        {slot(hero, "hero")}

        {/* Two featured */}
        <div className="grid md:grid-cols-2 gap-8 md:gap-10 mt-12 pt-10 border-t hairline">
          {slot(f1, "featured")}
          {slot(f2, "featured")}
        </div>

        {/* Money & Markets */}
        <SectionRule label="Money & Markets" />
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
          {slot(m1, "card")}
          {slot(m2, "card")}
        </div>

        {/* India & Culture */}
        <SectionRule label="India & Culture" />
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
          {slot(c1, "card")}
          {slot(c2, "card")}
          {slot(c3, "card")}
        </div>

        {/* Long read */}
        <div className="mt-16">{slot(longRead, "long")}</div>

        {/* Also Today */}
        <SectionRule label="Also Today" />
        <div className="grid md:grid-cols-2 gap-8">
          {slot(also1, "compact")}
          {slot(also2, "compact")}
        </div>

        {/* More stories */}
        {remaining.length > 0 && (
          <>
            <SectionRule label="More Stories" />
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
              {remaining.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" />
              ))}
            </div>
          </>
        )}
      </main>

      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
