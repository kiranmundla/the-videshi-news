import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import HeroCarousel from "@/components/HeroCarousel";
import { Article, getPublishedArticles } from "@/lib/articles";

type SectionDef = { slug: string; label: string; limit: number; href: string };

const NEWS_SECTION: SectionDef = {
  slug: "news",
  label: "News",
  limit: 6,
  href: "/news",
};

const CATEGORY_SECTIONS: SectionDef[] = [
  { slug: "markets-finance", label: "Markets & Finance", limit: 3, href: "/markets-finance" },
  { slug: "entertainment", label: "Entertainment", limit: 3, href: "/entertainment" },
  { slug: "technology", label: "Technology", limit: 3, href: "/technology" },
  { slug: "sports", label: "Sports", limit: 3, href: "/sports" },
  { slug: "travel", label: "Travel", limit: 3, href: "/travel" },
  { slug: "lifestyle-health", label: "Lifestyle & Health", limit: 3, href: "/lifestyle-health" },
  { slug: "food", label: "Food", limit: 3, href: "/food" },
];

const PLACEHOLDER_SECTIONS = [
  { slug: "events", label: "Events", message: "Coming soon." },
  { slug: "classifieds", label: "Classifieds", message: "Be the first to post." },
];

const CLUSTERS: { label: string; tags: string[]; excludeSlugs?: string[] }[] = [
  {
    label: "Bengal Elections",
    tags: ["west bengal", "mamata", "bjp bengal"],
    excludeSlugs: ["election-commission-seizures-1400-crore-assembly-polls-2025"],
  },
  { label: "Tamil Nadu", tags: ["tamil nadu", "tamilnadu"] },
];

function tagsLower(a: Article) {
  return (a.tags ?? []).map((t) => t.toLowerCase());
}
function matchesCluster(a: Article, tags: string[]) {
  const at = tagsLower(a);
  return tags.some((t) => at.some((x) => x === t || x.includes(t)));
}

function SectionHeader({ label, href, id }: { label: string; href?: string; id?: string }) {
  return (
    <div id={id} className="flex items-end justify-between mt-14 mb-7 gap-4 scroll-mt-24">
      <div className="flex items-center gap-4 flex-1 min-w-0">
        <span className="smallcaps text-primary whitespace-nowrap">{label}</span>
        <span className="flex-1 bg-rule" style={{ height: "0.5px" }} />
      </div>
      {href && (
        <Link to={href} className="smallcaps text-foreground/70 hover:text-primary whitespace-nowrap">
          View all →
        </Link>
      )}
    </div>
  );
}

function EmptyPlaceholder({ message }: { message: string }) {
  return <p className="py-8 text-center text-muted-foreground">{message}</p>;
}

export default function Index() {
  const [allArticles, setAllArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    getPublishedArticles().then((a) => {
      setAllArticles(a);
      setLastUpdated(new Date());
      setLoading(false);
    });
  }, []);

  const layout = useMemo(() => {
    const used = new Set<string>();

    // 1. Featured
    const featured =
      allArticles.find((a) => a.article_type === "feature") ?? allArticles[0] ?? null;
    if (featured) used.add(featured.id);

    // 2. News + clusters within News
    const newsAll = allArticles.filter((a) => a.category === "news" && !used.has(a.id));
    const newsClusters: { label: string; items: Article[] }[] = [];
    for (const c of CLUSTERS) {
      const items = newsAll.filter(
        (a) =>
          !used.has(a.id) &&
          !(c.excludeSlugs ?? []).includes(a.slug) &&
          matchesCluster(a, c.tags)
      );
      if (items.length >= 2) {
        newsClusters.push({ label: c.label, items });
        items.forEach((a) => used.add(a.id));
      }
    }
    const newsUngrouped = newsAll
      .filter((a) => !used.has(a.id))
      .slice(0, NEWS_SECTION.limit);
    newsUngrouped.forEach((a) => used.add(a.id));

    // 3. Category sections
    const sections = CATEGORY_SECTIONS.map((s) => {
      const items = allArticles
        .filter((a) => a.category === s.slug && !used.has(a.id))
        .slice(0, s.limit);
      items.forEach((a) => used.add(a.id));
      return { ...s, items };
    });

    return { featured, newsClusters, newsUngrouped, sections };
  }, [allArticles]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <CategoryPills />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  const { featured, newsClusters, newsUngrouped, sections } = layout;
  const hasNewsContent = newsClusters.length > 0 || newsUngrouped.length > 0;

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>The Videshi — News for the global Indian diaspora</title>
        <meta
          name="description"
          content="Editorial reporting and analysis for the global Indian diaspora — news, travel, lifestyle & health, markets, technology, and sports."
        />
        <meta property="og:title" content="The Videshi" />
        <meta property="og:description" content="News for the global Indian diaspora" />
        {featured && <meta property="og:image" content={featured.hero_image_url} />}
        <link rel="canonical" href="/" />
      </Helmet>

      <Masthead />
      <CategoryPills />
      <HeroCarousel />

      <main className="container flex-1 pt-8 md:pt-10">
        {featured && (
          <div>
            <div className="flex items-center gap-4 mb-5">
              <span className="smallcaps text-primary whitespace-nowrap">Featured</span>
              <span className="flex-1 bg-rule" style={{ height: "0.5px" }} />
            </div>
            <ArticleCard article={featured} variant="hero" />
          </div>
        )}

        <section>
          <SectionHeader label={NEWS_SECTION.label} href={NEWS_SECTION.href} id="section-news" />
          {hasNewsContent ? (
            <>
              {newsClusters.map((c) => (
                <div key={c.label} className="mb-10">
                  <p className="smallcaps text-foreground/70 mb-4">{c.label}</p>
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
                    {c.items.map((a) => (
                      <ArticleCard key={a.id} article={a} variant="card" hideCategory />
                    ))}
                  </div>
                </div>
              ))}
              {newsUngrouped.length > 0 && (
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
                  {newsUngrouped.map((a) => (
                    <ArticleCard key={a.id} article={a} variant="card" hideCategory />
                  ))}
                </div>
              )}
            </>
          ) : (
            <EmptyPlaceholder message="More stories coming soon." />
          )}
        </section>

        {sections.map((s) => (
          <section key={s.slug}>
            <SectionHeader label={s.label} href={s.href} id={`section-${s.slug}`} />
            {s.items.length > 0 ? (
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
                {s.items.map((a) => (
                  <ArticleCard key={a.id} article={a} variant="card" hideCategory />
                ))}
              </div>
            ) : (
              <EmptyPlaceholder message="More stories coming soon." />
            )}
          </section>
        ))}

        {PLACEHOLDER_SECTIONS.map((s) => (
          <section key={s.slug}>
            <SectionHeader label={s.label} id={`section-${s.slug}`} />
            <EmptyPlaceholder message={s.message} />
          </section>
        ))}
      </main>

      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
