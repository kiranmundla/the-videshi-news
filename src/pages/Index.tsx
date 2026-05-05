import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import SectionRule from "@/components/SectionRule";
import { Article, getPublishedArticles } from "@/lib/articles";

export default function Index() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPublishedArticles().then((a) => {
      setArticles(a);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  if (!articles.length) {
    return (
      <div className="min-h-screen flex flex-col">
        <Helmet>
          <title>The Videshi — News for the global Indian diaspora</title>
        </Helmet>
        <Masthead />
        <main className="container flex-1 py-24 md:py-32 text-center">
          <p className="smallcaps text-primary">The Videshi</p>
          <h1 className="font-serif text-4xl md:text-6xl mt-4 font-bold">Coming soon</h1>
          <p className="mt-5 max-w-xl mx-auto text-foreground/75 font-serif italic text-lg">
            News and reporting for the global Indian diaspora is on its way. Check back shortly.
          </p>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const [hero, f1, f2, m1, m2, c1, c2, c3, longRead, also1, also2] = articles;

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
        {hero && <ArticleCard article={hero} variant="hero" />}

        {/* Two featured */}
        {(f1 || f2) && (
          <div className="grid md:grid-cols-2 gap-8 md:gap-10 mt-12 pt-10 border-t hairline">
            {f1 && <ArticleCard article={f1} variant="featured" />}
            {f2 && <ArticleCard article={f2} variant="featured" />}
          </div>
        )}

        {/* Money & Markets */}
        {(m1 || m2) && (
          <>
            <SectionRule label="Money & Markets" />
            <div className="grid md:grid-cols-2 gap-8 md:gap-10">
              {m1 && <ArticleCard article={m1} variant="featured" />}
              {m2 && <ArticleCard article={m2} variant="featured" />}
            </div>
          </>
        )}

        {/* India & Culture */}
        {(c1 || c2 || c3) && (
          <>
            <SectionRule label="India & Culture" />
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
              {c1 && <ArticleCard article={c1} variant="card" />}
              {c2 && <ArticleCard article={c2} variant="card" />}
              {c3 && <ArticleCard article={c3} variant="card" />}
            </div>
          </>
        )}

        {/* Long read */}
        {longRead && (
          <div className="mt-16">
            <ArticleCard article={longRead} variant="long" />
          </div>
        )}

        {/* Also Today */}
        {(also1 || also2) && (
          <>
            <SectionRule label="Also Today" />
            <div className="grid md:grid-cols-2 gap-8">
              {also1 && <ArticleCard article={also1} variant="compact" />}
              {also2 && <ArticleCard article={also2} variant="compact" />}
            </div>
          </>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
