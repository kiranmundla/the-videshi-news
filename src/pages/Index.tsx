import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import SectionRule from "@/components/SectionRule";
import { Article, getPublishedArticles } from "@/lib/articles";

const SECTIONS = [
  { label: "India", needle: "india" },
  { label: "NRI Affairs", needle: "nri" },
  { label: "US-India", needle: "us-india" },
  { label: "Business", needle: "business" },
  { label: "Culture", needle: "culture" },
  { label: "Sports", needle: "sports" },
  { label: "Voices", needle: "voices" },
];

function matches(article: Article, needle: string) {
  return (article.category ?? "").toLowerCase().includes(needle);
}

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

  const filtered = useMemo(() => {
    if (!category) return allArticles;
    const needle = category.toLowerCase();
    return allArticles.filter((a) => matches(a, needle));
  }, [allArticles, category]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  // ---- Category view: simple chronological grid ----
  if (category) {
    const hero = filtered[0];
    const rest = filtered.slice(1);
    return (
      <div className="min-h-screen flex flex-col">
        <Helmet>
          <title>{category} — The Videshi</title>
          <meta name="description" content={`${category} stories from The Videshi.`} />
          <link rel="canonical" href={`/?c=${encodeURIComponent(category)}`} />
        </Helmet>
        <Masthead />
        <main className="container flex-1 pt-8 md:pt-10">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-2">{category}</h1>
          <p className="smallcaps text-muted-foreground mb-8">
            {filtered.length} {filtered.length === 1 ? "story" : "stories"}
          </p>
          {filtered.length === 0 ? (
            <p className="py-20 text-center text-muted-foreground">No stories yet in this section.</p>
          ) : (
            <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
              {filtered.map((a) => (
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

  // ---- Home view: hero + top 3 per section ----
  const hero = allArticles[0];
  const sectionLists = SECTIONS.map((s) => ({
    ...s,
    items: allArticles.filter((a) => matches(a, s.needle)).slice(0, 3),
  })).filter((s) => s.items.length > 0);

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
        {hero && <ArticleCard article={hero} variant="hero" />}

        {sectionLists.map((s) => (
          <section key={s.label}>
            <div className="flex items-end justify-between mt-14 mb-7 gap-4">
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <span className="smallcaps text-primary whitespace-nowrap">{s.label}</span>
                <span className="flex-1 bg-rule" style={{ height: "0.5px" }} />
              </div>
              <Link
                to={`/?c=${encodeURIComponent(s.label)}`}
                className="smallcaps text-foreground/70 hover:text-primary whitespace-nowrap"
              >
                View all →
              </Link>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
              {s.items.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" />
              ))}
            </div>
          </section>
        ))}
      </main>

      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
