import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import { Article, getPublishedArticles } from "@/lib/articles";
import { CATEGORIES } from "@/lib/categories";

const SECTION_ORDER: { slug: string; label: string }[] = [
  { slug: "markets-finance", label: "Markets & Finance" },
  { slug: "technology", label: "Technology" },
  { slug: "sports", label: "Sports" },
  { slug: "lifestyle-health", label: "Lifestyle & Health" },
  { slug: "travel", label: "Travel" },
];

const PLACEHOLDER_SECTIONS = [
  { slug: "events", label: "Events", message: "Community events coming soon." },
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

function SectionHeader({ label, href }: { label: string; href?: string }) {
  return (
    <div className="flex items-end justify-between mt-14 mb-7 gap-4">
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

    const featured =
      allArticles.find((a) => a.article_type === "feature") ?? allArticles[0] ?? null;
    if (featured) used.add(featured.id);

    const newsAll = allArticles.filter((a) => a.category === "news");

    // Build clusters
    const clusters: { label: string; items: Article[] }[] = [];
    const clusteredIds = new Set<string>();
    for (const c of CLUSTERS) {
      const items = newsAll.filter(
        (a) =>
          !used.has(a.id) &&
          !(c.excludeSlugs ?? []).includes(a.slug) &&
          matchesCluster(a, c.tags)
      );
      if (items.length > 0) {
        clusters.push({ label: c.label, items });
        items.forEach((a) => clusteredIds.add(a.id));
      }
    }

    const remainingNews = newsAll.filter((a) => !used.has(a.id) && !clusteredIds.has(a.id));
    // Pick latest news, ensuring all clustered items are included
    const newsItemsForLatest: Article[] = [];
    clusters.forEach((c) => c.items.forEach((a) => newsItemsForLatest.push(a)));
    remainingNews.forEach((a) => newsItemsForLatest.push(a));
    const latestNews = newsItemsForLatest.slice(0, 9);
    latestNews.forEach((a) => used.add(a.id));

    // Trim cluster items to those in latestNews
    const latestNewsIds = new Set(latestNews.map((a) => a.id));
    const visibleClusters = clusters
      .map((c) => ({ label: c.label, items: c.items.filter((a) => latestNewsIds.has(a.id)) }))
      .filter((c) => c.items.length > 0);
    const clusteredVisibleIds = new Set<string>();
    visibleClusters.forEach((c) => c.items.forEach((a) => clusteredVisibleIds.add(a.id)));
    const ungroupedNews = latestNews.filter((a) => !clusteredVisibleIds.has(a.id));

    const sections = SECTION_ORDER.map((s) => {
      const items = allArticles
        .filter((a) => a.category === s.slug && !used.has(a.id))
        .slice(0, 6);
      items.forEach((a) => used.add(a.id));
      return { ...s, items };
    });

    return { featured, visibleClusters, ungroupedNews, sections };
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

  const { featured, visibleClusters, ungroupedNews, sections } = layout;

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

        {(visibleClusters.length > 0 || ungroupedNews.length > 0) && (
          <section>
            <SectionHeader label="Latest News" href="/news" />

            {visibleClusters.map((c) => (
              <div key={c.label} className="mb-10">
                <p className="smallcaps text-foreground/70 mb-4">{c.label}</p>
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
                  {c.items.map((a) => (
                    <ArticleCard key={a.id} article={a} variant="card" hideCategory />
                  ))}
                </div>
              </div>
            ))}

            {ungroupedNews.length > 0 && (
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
                {ungroupedNews.map((a) => (
                  <ArticleCard key={a.id} article={a} variant="card" hideCategory />
                ))}
              </div>
            )}
          </section>
        )}

        {sections.map((s) =>
          s.items.length > 0 ? (
            <section key={s.slug}>
              <SectionHeader label={s.label} href={`/${s.slug}`} />
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
                {s.items.map((a) => (
                  <ArticleCard key={a.id} article={a} variant="card" hideCategory />
                ))}
              </div>
            </section>
          ) : null
        )}

        {PLACEHOLDER_SECTIONS.map((s) => (
          <section key={s.slug}>
            <SectionHeader label={s.label} href={`/${s.slug}`} />
            <p className="py-8 text-center text-muted-foreground">{s.message}</p>
          </section>
        ))}
      </main>

      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
