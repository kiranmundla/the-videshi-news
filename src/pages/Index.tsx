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
  { slug: "entertainment", label: "Entertainment" },
  { slug: "technology", label: "Technology" },
  { slug: "sports", label: "Sports" },
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

const MIN_SECTION_ITEMS = 2;
const NEWS_LIMIT = 6;

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

    // 1. Featured
    const featured =
      allArticles.find((a) => a.article_type === "feature") ?? allArticles[0] ?? null;
    if (featured) used.add(featured.id);

    // 2. Clusters (from news category, matching tags). Only keep if 2+ items.
    const newsAll = allArticles.filter((a) => a.category === "news");
    const visibleClusters: { label: string; items: Article[] }[] = [];
    for (const c of CLUSTERS) {
      const items = newsAll.filter(
        (a) =>
          !used.has(a.id) &&
          !(c.excludeSlugs ?? []).includes(a.slug) &&
          matchesCluster(a, c.tags)
      );
      if (items.length >= MIN_SECTION_ITEMS) {
        visibleClusters.push({ label: c.label, items });
        items.forEach((a) => used.add(a.id));
      }
    }

    // 3. Category sections — only if 2+ items. Singles get folded into News.
    const foldedSingles: Article[] = [];
    const sections = SECTION_ORDER.map((s) => {
      const items = allArticles
        .filter((a) => a.category === s.slug && !used.has(a.id))
        .slice(0, 6);
      if (items.length >= MIN_SECTION_ITEMS) {
        items.forEach((a) => used.add(a.id));
        return { ...s, items };
      }
      // Fold singles into News pool, mark used so we don't double-show
      items.forEach((a) => {
        foldedSingles.push(a);
        used.add(a.id);
      });
      return { ...s, items: [] };
    }).filter((s) => s.items.length > 0);

    // 4. News — 6 most recent from category=news not yet used, plus folded singles
    const newsSection = [
      ...newsAll.filter((a) => !used.has(a.id)),
      ...foldedSingles,
    ].slice(0, NEWS_LIMIT);
    newsSection.forEach((a) => used.add(a.id));

    return { featured, newsSection, visibleClusters, sections };
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

  const { featured, newsSection, visibleClusters, sections } = layout;

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

        {newsSection.length > 0 && (
          <section>
            <SectionHeader label="News" href="/news" />
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
              {newsSection.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" hideCategory />
              ))}
            </div>
          </section>
        )}

        {visibleClusters.map((c) => (
          <section key={c.label}>
            <SectionHeader label={c.label} />
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
              {c.items.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" hideCategory />
              ))}
            </div>
          </section>
        ))}

        {sections.map((s) => (
          <section key={s.slug}>
            <SectionHeader label={s.label} href={`/${s.slug}`} />
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-10">
              {s.items.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" hideCategory />
              ))}
            </div>
          </section>
        ))}

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

