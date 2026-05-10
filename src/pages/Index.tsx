import { useEffect, useMemo, useState } from "react";
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

type SectionDef = { slug: string; label: string };

const CATEGORY_SECTIONS: SectionDef[] = [
  { slug: "news", label: "India News" },
  { slug: "nri-world", label: "World News" },
  { slug: "markets-finance", label: "Markets & Finance" },
  { slug: "sports", label: "Sports" },
  { slug: "technology", label: "Technology" },
  { slug: "entertainment", label: "Entertainment" },
  { slug: "lifestyle-health", label: "Lifestyle & Health" },
  { slug: "travel", label: "Travel" },
  { slug: "food", label: "Food" },
];

type ClusterDef = { label: string; tags: string[] };

const TOP_CLUSTERS: ClusterDef[] = [
  { label: "BENGAL: BJP TAKES POWER", tags: ["bengal elections", "bjp bengal", "suvendu"] },
  { label: "TAMIL NADU: VIJAY'S GOVERNMENT", tags: ["tamil nadu", "vijay cm", "tvk"] },
  { label: "GULF CRISIS: OIL & WAR", tags: ["iran", "us-iran", "hormuz"] },
  { label: "IPL 2026 PLAYOFF RACE", tags: ["ipl 2026", "ipl playoffs"] },
];

const CATEGORY_CLUSTERS: Record<string, ClusterDef[]> = {
  news: [
    { label: "TAMIL NADU: VIJAY'S GOVERNMENT", tags: ["tamil nadu", "tamilnadu", "tvk"] },
    { label: "BENGAL: BJP TAKES POWER", tags: ["west bengal", "bjp bengal", "suvendu"] },
    { label: "KERALA: CM DEADLOCK", tags: ["kerala", "congress kerala"] },
  ],
  "nri-world": [
    { label: "GULF CRISIS: OIL & WAR", tags: ["iran", "us-iran", "hormuz", "gulf"] },
    { label: "H-1B & VISAS", tags: ["h-1b", "h1b", "visa", "silicon valley"] },
  ],
};

function tagsLower(a: Article) {
  return (a.tags ?? []).map((t) => t.toLowerCase());
}
function matchesCluster(a: Article, tags: string[]) {
  const at = tagsLower(a);
  return tags.some((t) => at.some((x) => x === t || x.includes(t)));
}

function extractClusters(pool: Article[], defs: ClusterDef[]) {
  const used = new Set<string>();
  const clusters: { label: string; items: Article[] }[] = [];
  for (const c of defs) {
    const items = pool.filter((a) => !used.has(a.id) && matchesCluster(a, c.tags));
    if (items.length >= 2) {
      clusters.push({ label: c.label, items });
      items.forEach((a) => used.add(a.id));
    }
  }
  const remaining = pool.filter((a) => !used.has(a.id));
  return { clusters, remaining };
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

// Render only complete rows of 3.
function FullRowsGrid({
  articles,
  hideCategory = false,
}: {
  articles: Article[];
  hideCategory?: boolean;
}) {
  const fullCount = Math.floor(articles.length / 3) * 3;
  const items = articles.slice(0, fullCount);
  if (items.length === 0) return null;
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 md:gap-8 auto-rows-fr items-stretch">
      {items.map((a) => (
        <div key={a.id} className="h-full">
          <ArticleCard article={a} variant="card" hideCategory={hideCategory} />
        </div>
      ))}
    </div>
  );
}

function CategorySection({
  slug,
  label,
  initialPool,
  hideCategory = true,
}: {
  slug: string;
  label: string;
  initialPool: Article[];
  hideCategory?: boolean;
}) {
  const [pool, setPool] = useState<Article[]>(initialPool);
  const [visibleCount, setVisibleCount] = useState(3);
  const [offset, setOffset] = useState(initialPool.length);
  const [hasMore, setHasMore] = useState(false);

  // Check on mount if server has more
  useEffect(() => {
    getArticlesByCategory(slug, 1, initialPool.length).then((more) =>
      setHasMore(more.length > 0)
    );
  }, [slug, initialPool.length]);
  const [loading, setLoading] = useState(false);

  const clusterDefs = CATEGORY_CLUSTERS[slug] ?? [];

  const loadMore = async () => {
    setLoading(true);
    try {
      // If we have more in pool already (from initial fetch), reveal first.
      if (visibleCount < pool.length) {
        setVisibleCount((v) => Math.min(v + 3, pool.length));
        return;
      }
      const more = await getArticlesByCategory(slug, 3, offset);
      if (more.length < 3) setHasMore(false);
      if (more.length > 0) {
        setPool((prev) => [...prev, ...more]);
        setVisibleCount((v) => v + more.length);
        setOffset((prev) => prev + more.length);
      } else {
        setHasMore(false);
      }
    } finally {
      setLoading(false);
    }
  };

  if (pool.length < 2) return null;

  const visible = pool.slice(0, visibleCount);
  const { clusters, remaining } = clusterDefs.length
    ? extractClusters(visible, clusterDefs)
    : { clusters: [] as { label: string; items: Article[] }[], remaining: visible };

  return (
    <section>
      <SectionHeader label={label} id={`section-${slug}`} />
      {clusters.map((c) => (
        <EventCluster key={c.label} label={c.label} items={c.items} />
      ))}
      <FullRowsGrid articles={remaining} hideCategory={hideCategory} />
      <MoreStoriesButton onClick={loadMore} loading={loading} hasMore={hasMore} />
    </section>
  );
}

function TopStoriesSection({
  topStories,
  clusters,
}: {
  topStories: Article[];
  clusters: { label: string; items: Article[] }[];
}) {
  // First two articles form the hero row (2-col + 1-col); remainder uses 3-col grid (complete rows only).
  const hero = topStories.slice(0, 2);
  const restAll = topStories.slice(2);
  // Cap at total of 6 (so rest = up to 4, but keep complete rows of 3 in the grid below the hero pair).
  const restFullCount = Math.floor(Math.min(restAll.length, 4) / 3) * 3;
  const rest = restAll.slice(0, restFullCount);

  return (
    <section>
      <SectionHeader label="Top Stories" id="section-top" />
      {clusters.map((c) => (
        <EventCluster key={c.label} label={c.label} items={c.items} />
      ))}
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
          <FullRowsGrid articles={rest} hideCategory={true} />
        </div>
      )}
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
    (async () => {
      const [featured, top] = await Promise.all([
        getFeaturedArticle(),
        getTopStories(20),
      ]);

      const shownIds = new Set<string>();
      if (featured?.id) shownIds.add(featured.id);
      const filteredTop = top.filter((a) => !shownIds.has(a.id));
      filteredTop.forEach((a) => shownIds.add(a.id));

      const pools: Record<string, Article[]> = {};
      for (const s of CATEGORY_SECTIONS) {
        const items = await getArticlesByCategory(s.slug, 12);
        const filtered = items.filter((a) => !shownIds.has(a.id));
        filtered.forEach((a) => shownIds.add(a.id));
        pools[s.slug] = filtered;
      }

      setFeaturedArticle(featured);
      setTopPool(filteredTop);
      setSectionPools(pools);
      setLastUpdated(new Date());
      setLoading(false);
    })();
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
    }, 150);
    return () => clearTimeout(t);
  }, [loading]);

  const layout = useMemo(() => {
    const featuredId = featuredArticle?.id;
    const filtered = featuredId ? topPool.filter((a) => a.id !== featuredId) : topPool;

    const { clusters, remaining } = extractClusters(filtered, TOP_CLUSTERS);
    const topClusters = clusters.slice(0, 2);
    // Show only complete rows of 3, max 6 ungrouped Top Stories.
    const ungroupedAll = remaining.slice(0, 6);
    const completeCount = Math.floor(ungroupedAll.length / 3) * 3;
    const topStories = ungroupedAll.slice(0, completeCount);

    return { topClusters, topStories };
  }, [topPool, featuredArticle]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <CategoryPills />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  const { topClusters, topStories } = layout;
  const featuredId = featuredArticle?.id;

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

      <main className="container flex-1 pt-6 md:pt-8">
        {featuredArticle && (
          <div className="mb-10">
            <FeaturedHero article={featuredArticle} />
          </div>
        )}

        {(topStories.length > 0 || topClusters.length > 0) && (
          <TopStoriesSection topStories={topStories} clusters={topClusters} />
        )}

        {CATEGORY_SECTIONS.map((s) => {
          const pool = (sectionPools[s.slug] ?? []).filter((a) => a.id !== featuredId);
          if (pool.length < 2) return null;
          return (
            <CategorySection
              key={s.slug}
              slug={s.slug}
              label={s.label}
              initialPool={pool}
              hideCategory={s.slug !== "news"}
            />
          );
        })}

        <ArticleCarousel />
      </main>


      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
