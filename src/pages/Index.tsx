import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import MoreStoriesButton from "@/components/MoreStoriesButton";
import ArticleCarousel from "@/components/ArticleCarousel";

import FeaturedHero from "@/components/FeaturedHero";
import EventCluster from "@/components/EventCluster";
import TopStoriesCard from "@/components/TopStoriesCard";
import {
  Article,
  getArticlesByCategory,
  getFeaturedArticle,
  getTopStories,
} from "@/lib/articles";

type SectionDef = { slug: string; label: string; href: string };

const CATEGORY_SECTIONS: SectionDef[] = [
  { slug: "nri-world", label: "Indians Around the World", href: "/nri-world" },
  { slug: "markets-finance", label: "Markets & Finance", href: "/markets-finance" },
  { slug: "sports", label: "Sports", href: "/sports" },
  { slug: "technology", label: "Technology", href: "/technology" },
  { slug: "entertainment", label: "Entertainment", href: "/entertainment" },
  { slug: "lifestyle-health", label: "Lifestyle & Health", href: "/lifestyle-health" },
  { slug: "travel", label: "Travel", href: "/travel" },
  { slug: "food", label: "Food", href: "/food" },
];

const CLUSTERS: { label: string; tags: string[] }[] = [
  { label: "BENGAL: BJP TAKES POWER", tags: ["bengal elections", "bjp bengal", "suvendu"] },
  { label: "TAMIL NADU: VIJAY'S GOVERNMENT", tags: ["tamil nadu", "vijay cm", "tvk"] },
  { label: "GULF CRISIS: OIL & WAR", tags: ["iran", "us-iran", "hormuz"] },
  { label: "IPL 2026 PLAYOFF RACE", tags: ["ipl 2026", "ipl playoffs"] },
];

function tagsLower(a: Article) {
  return (a.tags ?? []).map((t) => t.toLowerCase());
}
function matchesCluster(a: Article, tags: string[]) {
  const at = tagsLower(a);
  return tags.some((t) => at.some((x) => x === t || x.includes(t)));
}

function SectionHeader({ label, id }: { label: string; id?: string }) {
  return (
    <div
      id={id}
      className="flex items-center justify-between mt-14 mb-6 gap-4 pb-3 scroll-mt-24"
      style={{ borderBottom: "1px solid hsl(var(--rule))" }}
    >
      <span
        className="font-bold uppercase"
        style={{ fontSize: 11, letterSpacing: "0.12em", color: "#888" }}
      >
        {label}
      </span>
    </div>
  );
}

function OrphanGrid({ articles }: { articles: Article[] }) {
  const fullCount = Math.floor(articles.length / 3) * 3;
  const full = articles.slice(0, fullCount);
  const orphans = articles.slice(fullCount);

  return (
    <>
      {full.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 md:gap-8 auto-rows-fr items-stretch">
          {full.map((a) => (
            <div key={a.id} className="h-full">
              <ArticleCard article={a} variant="card" hideCategory />
            </div>
          ))}
        </div>
      )}
      {orphans.length === 1 && (
        <div className={full.length > 0 ? "mt-5 md:mt-8" : ""}>
          <ArticleCard article={orphans[0]} variant="long" hideCategory />
        </div>
      )}
      {orphans.length === 2 && (
        <div
          className={`grid grid-cols-1 sm:grid-cols-2 gap-5 md:gap-8 auto-rows-fr items-stretch ${
            full.length > 0 ? "mt-5 md:mt-8" : ""
          }`}
        >
          {orphans.map((a) => (
            <div key={a.id} className="h-full">
              <ArticleCard article={a} variant="card" hideCategory />
            </div>
          ))}
        </div>
      )}
    </>
  );
}

function CategorySection({
  slug,
  label,
  initial,
}: {
  slug: string;
  label: string;
  initial: Article[];
}) {
  const [articles, setArticles] = useState<Article[]>(initial);
  const [offset, setOffset] = useState(initial.length);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const loadMore = async () => {
    setLoading(true);
    try {
      const more = await getArticlesByCategory(slug, 3, offset);
      if (more.length < 3) setHasMore(false);
      if (more.length > 0) {
        setArticles((prev) => [...prev, ...more]);
        setOffset((prev) => prev + more.length);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <SectionHeader label={label} id={`section-${slug}`} />
      <OrphanGrid articles={articles} />
      <MoreStoriesButton onClick={loadMore} loading={loading} hasMore={hasMore} />
    </section>
  );
}

function TopStoriesSection({ initial }: { initial: Article[] }) {
  const [articles, setArticles] = useState<Article[]>(initial);
  const [offset, setOffset] = useState(20);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const loadMore = async () => {
    setLoading(true);
    try {
      const more = await getTopStories(3, offset);
      const seen = new Set(articles.map((a) => a.id));
      const fresh = more.filter((a) => !seen.has(a.id));
      if (more.length < 3) setHasMore(false);
      if (fresh.length > 0) {
        setArticles((prev) => [...prev, ...fresh]);
      }
      setOffset((prev) => prev + 3);
    } finally {
      setLoading(false);
    }
  };

  // First two articles form the hero row (2-col + 1-col); remainder uses orphan-aware grid.
  const hero = articles.slice(0, 2);
  const rest = articles.slice(2);

  return (
    <section>
      <SectionHeader label="Top Stories" id="section-top" />
      {hero.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6 auto-rows-fr">
          {hero.map((a, i) => (
            <div key={a.id} className={i === 0 ? "md:col-span-2" : ""}>
              <TopStoriesCard article={a} size={i === 0 ? "lg" : "md"} />
            </div>
          ))}
        </div>
      )}
      {rest.length > 0 && (
        <div className="mt-5 md:mt-6">
          <OrphanGrid articles={rest} />
        </div>
      )}
      <MoreStoriesButton onClick={loadMore} loading={loading} hasMore={hasMore} />
    </section>
  );
}

export default function Index() {
  const [topPool, setTopPool] = useState<Article[]>([]);
  const [sectionPools, setSectionPools] = useState<Record<string, Article[]>>({});
  const [featuredArticle, setFeaturedArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    const sectionFetches = CATEGORY_SECTIONS.map((s) =>
      getArticlesByCategory(s.slug, 3).then((items) => [s.slug, items] as const)
    );
    Promise.all([
      getTopStories(20),
      getFeaturedArticle(),
      ...sectionFetches,
    ]).then((results) => {
      const [top, featured, ...sectionResults] = results as [
        Article[],
        Article | null,
        ...(readonly [string, Article[]])[]
      ];
      setTopPool(top);
      setFeaturedArticle(featured);
      setSectionPools(
        Object.fromEntries(sectionResults as (readonly [string, Article[]])[])
      );
      setLastUpdated(new Date());
      setLoading(false);
    });
  }, []);

  // Save scroll position when leaving the homepage
  useEffect(() => {
    return () => {
      sessionStorage.setItem("homeScrollY", window.scrollY.toString());
    };
  }, []);

  // Restore scroll position once content has rendered
  useEffect(() => {
    if (loading) return;
    const savedY = sessionStorage.getItem("homeScrollY");
    if (!savedY) return;
    const t = setTimeout(() => {
      window.scrollTo(0, parseInt(savedY, 10));
      sessionStorage.removeItem("homeScrollY");
    }, 100);
    return () => clearTimeout(t);
  }, [loading]);

  const layout = useMemo(() => {
    const featuredId = featuredArticle?.id;
    const filtered = featuredId ? topPool.filter((a) => a.id !== featuredId) : topPool;

    const used = new Set<string>();
    const clusters: { label: string; items: Article[] }[] = [];
    for (const c of CLUSTERS) {
      const items = filtered.filter(
        (a) => !used.has(a.id) && matchesCluster(a, c.tags)
      );
      if (items.length >= 2) {
        clusters.push({ label: c.label, items });
        items.forEach((a) => used.add(a.id));
      }
    }
    const topClusters = clusters.slice(0, 2);
    topClusters.forEach((c) => c.items.forEach((a) => used.add(a.id)));

    const topStories = filtered.filter((a) => !used.has(a.id)).slice(0, 6);

    const sections = CATEGORY_SECTIONS.map((s) => ({
      ...s,
      items: (sectionPools[s.slug] ?? [])
        .filter((a) => a.id !== featuredId)
        .slice(0, 3),
    })).filter((s) => s.items.length >= 2);

    return { topClusters, topStories, sections };
  }, [topPool, sectionPools, featuredArticle]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <CategoryPills />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  const { topClusters, topStories, sections } = layout;

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
        {featuredArticle && <meta property="og:image" content={featuredArticle.hero_image_url} />}
        <link rel="canonical" href="/" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      {featuredArticle && <FeaturedHero article={featuredArticle} />}

      <main className="container flex-1 pt-8 md:pt-10">
        {topStories.length >= 2 && <TopStoriesSection initial={topStories} />}

        {topClusters.length > 0 && (
          <section className="mt-12">
            {topClusters.map((c) => (
              <EventCluster key={c.label} label={c.label} items={c.items} />
            ))}
          </section>
        )}

        {sections.map((s) => (
          <CategorySection key={s.slug} slug={s.slug} label={s.label} initial={s.items} />
        ))}
      </main>

      <ArticleCarousel />

      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
