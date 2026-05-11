import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";

import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import ArticleCarousel from "@/components/ArticleCarousel";
import FeaturedHero from "@/components/FeaturedHero";
import EventCluster from "@/components/EventCluster";
import {
  Article,
  getArticlesByCategory,
  getFeaturedArticle,
} from "@/lib/articles";

const INDIA_NEWS = { slug: "news", label: "INDIA NEWS", limit: 18 };
const WORLD_NEWS = { slug: "nri-world", label: "WORLD NEWS", limit: 12 };

const CATEGORY_SECTIONS = [
  { slug: "markets-finance", label: "MARKETS & FINANCE", limit: 12 },
  { slug: "sports", label: "SPORTS", limit: 12 },
  { slug: "technology", label: "TECHNOLOGY", limit: 12 },
  { slug: "entertainment", label: "ENTERTAINMENT", limit: 12 },
  { slug: "lifestyle-health", label: "LIFESTYLE & HEALTH", limit: 12 },
  { slug: "travel", label: "TRAVEL", limit: 12 },
  { slug: "food", label: "FOOD", limit: 12 },
];

const CLUSTERS: { label: string; require: string[]; also: string[] }[] = [
  {
    label: "TAMIL NADU: VIJAY'S GOVERNMENT",
    require: ["tamil nadu", "tamilnadu"],
    also: ["vijay", "tvk", "chief minister", "swearing", "dravidian", "cm", "oath"],
  },
  {
    label: "BENGAL: BJP TAKES POWER",
    require: ["west bengal", "bengal"],
    also: ["bjp", "suvendu", "adhikari", "mamata", "trinamool", "cm"],
  },
  {
    label: "KERALA: CM DEADLOCK",
    require: ["kerala"],
    also: ["congress", "chief minister", "cm", "rahul", "pick"],
  },
  {
    label: "GULF CRISIS: OIL & WAR",
    require: ["iran", "hormuz", "gulf"],
    also: ["war", "oil", "ceasefire", "tanker", "strait", "attack"],
  },
  {
    label: "IPL 2026 PLAYOFF RACE",
    require: ["ipl", "ipl 2026"],
    also: ["playoff", "final", "match", "qualifier", "cricket"],
  },
  {
    label: "H-1B & VISAS",
    require: ["h-1b", "h1b"],
    also: ["silicon valley", "wage", "trap", "bias", "immigration", "eeoc"],
  },
];

function tagsLower(a: Article) {
  return (a.tags ?? []).map((t) => t.toLowerCase());
}

function matchesCluster(a: Article, c: typeof CLUSTERS[number]): boolean {
  const tags = tagsLower(a);
  const hasReq = c.require.some((r) => tags.some((t) => t.includes(r)));
  const hasCtx = c.also.some((x) => tags.some((t) => t.includes(x)));
  return hasReq && hasCtx;
}

function buildClusters(pool: Article[]) {
  const used = new Set<string>();
  const clusters: { label: string; items: Article[] }[] = [];
  for (const c of CLUSTERS) {
    const items = pool.filter((a) => !used.has(a.id) && matchesCluster(a, c));
    if (items.length >= 2) {
      clusters.push({ label: c.label, items });
      items.forEach((a) => used.add(a.id));
    }
  }
  const ungrouped = pool.filter((a) => !used.has(a.id));
  return { clusters, ungrouped };
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

function FullRowsGrid({
  articles,
  hideCategory = true,
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

function HomeCategorySection({
  label,
  slug,
  clusters,
  pool,
  hideCategory = true,
}: {
  label: string;
  slug: string;
  clusters: { label: string; items: Article[] }[];
  pool: Article[];
  hideCategory?: boolean;
}) {
  const [visibleCount, setVisibleCount] = useState(3);

  const hasContent = clusters.length > 0 || pool.length > 0;
  if (!hasContent) return null;

  const shownPool = pool.slice(0, visibleCount);
  const hasMore = pool.length > visibleCount;

  return (
    <section>
      <SectionHeader label={label} id={`section-${slug}`} />
      {clusters.map((c) => (
        <EventCluster key={c.label} label={c.label} items={c.items} />
      ))}
      <FullRowsGrid articles={shownPool} hideCategory={hideCategory} />
      {hasMore && (
        <div className="flex justify-center mt-8">
          <button
            onClick={() => setVisibleCount((v) => v + 3)}
            className="smallcaps tracking-[0.12em] text-[11px] text-foreground/60 border border-rule px-8 py-2.5 hover:border-foreground/40 hover:text-foreground/80 bg-transparent transition-colors"
          >
            MORE STORIES
          </button>
        </div>
      )}
    </section>
  );
}

export default function Index() {
  const [featuredArticle, setFeaturedArticle] = useState<Article | null>(null);
  const [newsPool, setNewsPool] = useState<Article[]>([]);
  const [nriPool, setNriPool] = useState<Article[]>([]);
  const [sectionPools, setSectionPools] = useState<Record<string, Article[]>>({});
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    Promise.all([
      getFeaturedArticle(),
      getArticlesByCategory(INDIA_NEWS.slug, INDIA_NEWS.limit),
      getArticlesByCategory(WORLD_NEWS.slug, WORLD_NEWS.limit),
      ...CATEGORY_SECTIONS.map((s) =>
        getArticlesByCategory(s.slug, s.limit).then(
          (items) => [s.slug, items] as const,
        ),
      ),
    ]).then(([featured, indiaNews, worldNews, ...catResults]) => {
      setFeaturedArticle(featured as Article | null);
      setNewsPool(indiaNews as Article[]);
      setNriPool(worldNews as Article[]);
      setSectionPools(
        Object.fromEntries(catResults as Array<readonly [string, Article[]]>),
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
    }, 150);
    return () => clearTimeout(t);
  }, [loading]);

  const layout = useMemo(() => {
    const featuredId = featuredArticle?.id;
    const shownIds = new Set<string>(
      [featuredId].filter(Boolean) as string[],
    );

    // INDIA NEWS
    const indiaPoolFiltered = newsPool.filter((a) => !shownIds.has(a.id));
    const india = buildClusters(indiaPoolFiltered);
    indiaPoolFiltered.forEach((a) => shownIds.add(a.id));

    // WORLD NEWS
    const worldPoolFiltered = nriPool.filter((a) => !shownIds.has(a.id));
    const world = buildClusters(worldPoolFiltered);
    worldPoolFiltered.forEach((a) => shownIds.add(a.id));

    // CATEGORY SECTIONS
    const sections = CATEGORY_SECTIONS.map((s) => ({
      ...s,
      pool: (sectionPools[s.slug] ?? []).filter((a) => !shownIds.has(a.id)),
    }));
    sections.forEach((s) => s.pool.forEach((a) => shownIds.add(a.id)));

    return { india, world, sections };
  }, [newsPool, nriPool, sectionPools, featuredArticle]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

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

      <main className="container flex-1 pt-6 md:pt-8">
        {featuredArticle && (
          <div className="mb-10">
            <FeaturedHero article={featuredArticle} />
          </div>
        )}

        <HomeCategorySection
          slug={INDIA_NEWS.slug}
          label={INDIA_NEWS.label}
          clusters={layout.india.clusters}
          pool={layout.india.ungrouped}
          hideCategory={false}
        />

        <HomeCategorySection
          slug={WORLD_NEWS.slug}
          label={WORLD_NEWS.label}
          clusters={layout.world.clusters}
          pool={layout.world.ungrouped}
        />

        {layout.sections
          .filter((s) => s.pool.length >= 2)
          .map((s) => (
            <HomeCategorySection
              key={s.slug}
              slug={s.slug}
              label={s.label}
              clusters={[]}
              pool={s.pool}
            />
          ))}

        <ArticleCarousel />
      </main>

      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
