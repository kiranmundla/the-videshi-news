import { useEffect, useMemo, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";

import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import DiasporaPhotoStrip from "@/components/DiasporaPhotoStrip";
// import CelebrityBuzz from "@/components/CelebrityBuzz"; // temporarily hidden
import TechBuzz from "@/components/TechBuzz";
import WorldCupTracker from "@/components/WorldCupTracker";
import FeaturedHero from "@/components/FeaturedHero";
import FeaturedCarousel from "@/components/FeaturedCarousel";
import MarketTicker from "@/components/MarketTicker";
import CategoryPills from "@/components/CategoryPills";
import EventCluster from "@/components/EventCluster";
import EditorsDesk from "@/components/EditorsDesk";
import TopStories from "@/components/homepage/TopStories";
import JustInStrip from "@/components/homepage/JustInStrip";
import EntertainmentSection from "@/components/homepage/EntertainmentSection";
import {
  Article,
  getArticlesByCategory,
  getFeaturedArticle,
} from "@/lib/articles";

const INDIA_NEWS = { slug: "news", label: "INDIA NEWS", limit: 18 };
const WORLD_NEWS = { slug: "nri-world", label: "WORLD NEWS", limit: 12 };

const CATEGORY_SECTIONS = [
  { slug: "technology", label: "TECHNOLOGY", limit: 30 },
  { slug: "markets-finance", label: "MARKETS & FINANCE", limit: 30 },
  { slug: "sports", label: "SPORTS", limit: 30 },
  { slug: "entertainment", label: "ENTERTAINMENT", limit: 30 },
  { slug: "lifestyle-health", label: "LIFESTYLE & HEALTH", limit: 30 },
  { slug: "food", label: "FOOD", limit: 30 },
];

const CAROUSEL_CATEGORIES = ["immigration", "news", "entertainment", "sports", "technology", "markets-finance"];

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
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-10 items-start">
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
  afterHeader,
}: {
  label: string;
  slug: string;
  clusters: { label: string; items: Article[] }[];
  pool: Article[];
  hideCategory?: boolean;
  afterHeader?: React.ReactNode;
}) {
  const [visibleCount, setVisibleCount] = useState(6);

  const hasContent = clusters.length > 0 || pool.length > 0;
  if (!hasContent) return null;

  const shownPool = pool.slice(0, visibleCount);
  const hasMore = pool.length > visibleCount;

  return (
    <section>
      <SectionHeader label={label} id={`section-${slug}`} />
      {afterHeader}
      {clusters.map((c) => (
        <EventCluster key={c.label} label={c.label} items={c.items} />
      ))}
      <FullRowsGrid articles={shownPool} hideCategory={hideCategory} />
      {hasMore && (
        <div className="flex justify-center mt-8">
          <button
            onClick={() => setVisibleCount((v) => v + 6)}
            className="smallcaps tracking-[0.12em] text-[11px] text-foreground/60 border border-rule px-8 py-2.5 hover:border-foreground/40 hover:text-foreground/80 bg-transparent transition-colors"
          >
            MORE STORIES
          </button>
        </div>
      )}
    </section>
  );
}

const CACHE_KEY = "videshi_home_cache";
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

type HomeCache = {
  ts: number;
  featured: Article | null;
  carouselArticles: Article[];
  newsPool: Article[];
  nriPool: Article[];
  sectionPools: Record<string, Article[]>;
};

function loadCache(): HomeCache | null {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const cached = JSON.parse(raw) as HomeCache;
    if (Date.now() - cached.ts > CACHE_TTL) return null;
    return cached;
  } catch {
    return null;
  }
}

function saveCache(data: HomeCache) {
  try {
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
  } catch {}
}

export default function Index() {
  const initialCache = useRef(loadCache()).current;
  const [featuredArticle, setFeaturedArticle] = useState<Article | null>(initialCache?.featured ?? null);
  const [carouselArticles, setCarouselArticles] = useState<Article[]>(initialCache?.carouselArticles ?? []);
  const [newsPool, setNewsPool] = useState<Article[]>(initialCache?.newsPool ?? []);
  const [nriPool, setNriPool] = useState<Article[]>(initialCache?.nriPool ?? []);
  const [sectionPools, setSectionPools] = useState<Record<string, Article[]>>(initialCache?.sectionPools ?? {});
  const [loading, setLoading] = useState(!initialCache);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(initialCache ? new Date(initialCache.ts) : null);

  useEffect(() => {
    // If we have cached data, skip the fetch on mount (back-button case)
    if (initialCache) return;

    // Populate state from loaded homepage data
    const applyData = (
      f: Article | null,
      carousel: Article[],
      n: Article[],
      nri: Article[],
      sp: Record<string, Article[]>,
      ts: Date,
    ) => {
      setFeaturedArticle(f);
      setCarouselArticles(carousel);
      setNewsPool(n);
      setNriPool(nri);
      setSectionPools(sp);
      setLastUpdated(ts);
      setLoading(false);
      saveCache({ ts: Date.now(), featured: f, carouselArticles: carousel, newsPool: n, nriPool: nri, sectionPools: sp });
    };

    // Fallback: original Supabase fetch (14 parallel queries)
    const fetchFromSupabase = () => {
      const timeout = setTimeout(() => setLoading(false), 8000);
      Promise.all([
        getFeaturedArticle().catch(() => null),
        getArticlesByCategory(INDIA_NEWS.slug, INDIA_NEWS.limit).catch(() => []),
        getArticlesByCategory(WORLD_NEWS.slug, WORLD_NEWS.limit).catch(() => []),
        ...CATEGORY_SECTIONS.map((s) =>
          getArticlesByCategory(s.slug, s.limit)
            .then((items) => [s.slug, items] as const)
            .catch(() => [s.slug, []] as const),
        ),
        ...CAROUSEL_CATEGORIES.map((cat) =>
          getArticlesByCategory(cat, 1)
            .then((items) => items[0] || null)
            .catch(() => null),
        ),
      ]).then((results) => {
        clearTimeout(timeout);
        const catSectionCount = CATEGORY_SECTIONS.length;
        const carouselCount = CAROUSEL_CATEGORIES.length;
        const f = results[0] as Article | null;
        const n = results[1] as Article[];
        const nri = results[2] as Article[];
        const catResults = results.slice(3, 3 + catSectionCount) as Array<readonly [string, Article[]]>;
        const carouselRaw = results.slice(3 + catSectionCount, 3 + catSectionCount + carouselCount) as Array<Article | null>;
        const sp = Object.fromEntries(catResults);
        const seenIds = new Set<string>();
        const carousel = carouselRaw.filter((a): a is Article => {
          if (!a) return false;
          if (seenIds.has(a.id)) return false;
          seenIds.add(a.id);
          return true;
        });
        applyData(f, carousel, n, nri, sp, new Date());
      });
    };

    // Fast path: try pre-built static JSON from CDN (single request)
    fetch(`/data/homepage-feed.json?v=${Date.now()}`)
      .then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then((data) => {
        const sp: Record<string, Article[]> = {};
        for (const [k, v] of Object.entries(data.sections || {})) {
          if (k !== "news" && k !== "nri-world") sp[k] = v as Article[];
        }
        applyData(
          data.featured ?? null,
          data.carousel ?? [],
          data.sections?.["news"] ?? [],
          data.sections?.["nri-world"] ?? [],
          sp,
          new Date(data.generated_at),
        );
      })
      .catch(() => {
        // Static feed unavailable or corrupt — fall back to Supabase
        fetchFromSupabase();
      });
  }, []);

  // Scroll position save/restore handled by useScrollRestore in App.tsx

  const layout = useMemo(() => {
    const featuredId = featuredArticle?.id;
    const shownIds = new Set<string>(
      [featuredId, ...carouselArticles.map((a) => a.id)].filter(Boolean) as string[],
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
  }, [newsPool, nriPool, sectionPools, featuredArticle, carouselArticles]);

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
        <link rel="canonical" href="https://www.thevideshi.com/" />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@graph": [
              {
                "@type": "NewsMediaOrganization",
                "@id": "https://www.thevideshi.com/#organization",
                name: "The Videshi",
                url: "https://www.thevideshi.com",
                logo: {
                  "@type": "ImageObject",
                  url: "https://www.thevideshi.com/logo.jpg"
                },
                sameAs: [
                  "https://www.instagram.com/thevideshi",
                  "https://x.com/thevideshi"
                ],
                description: "Editorial reporting and analysis for the global Indian diaspora — news, travel, lifestyle & health, markets, technology, and sports."
              },
              {
                "@type": "WebSite",
                "@id": "https://www.thevideshi.com/#website",
                url: "https://www.thevideshi.com",
                name: "The Videshi",
                publisher: { "@id": "https://www.thevideshi.com/#organization" },
                potentialAction: {
                  "@type": "SearchAction",
                  target: {
                    "@type": "EntryPoint",
                    urlTemplate: "https://www.thevideshi.com/search?q={search_term_string}"
                  },
                  "query-input": "required name=search_term_string"
                }
              }
            ]
          })}
        </script>
      </Helmet>

      <Masthead />
      <CategoryPills />
      <div className="mt-3" />
      <MarketTicker />

      <main className="container flex-1 pt-6 md:pt-8">
        <EditorsDesk />

        <JustInStrip />

        {carouselArticles.length > 1 ? (
          <div className="mb-10">
            <FeaturedCarousel articles={carouselArticles} />
          </div>
        ) : featuredArticle ? (
          <div className="mb-10">
            <FeaturedHero article={featuredArticle} />
          </div>
        ) : null}

        <TopStories articles={carouselArticles} />

        {/* FIFA World Cup 2026 — top of homepage */}
        <WorldCupTracker />

        <HomeCategorySection
          slug={INDIA_NEWS.slug}
          label={INDIA_NEWS.label}
          clusters={layout.india.clusters}
          pool={layout.india.ungrouped}
          hideCategory={true}
          afterHeader={<TechBuzz category="india" />}
        />

        <HomeCategorySection
          slug={WORLD_NEWS.slug}
          label={WORLD_NEWS.label}
          clusters={layout.world.clusters}
          pool={layout.world.ungrouped}
          afterHeader={<TechBuzz category="world" />}
        />

        {layout.sections
          .filter((s) => s.pool.length >= 3)
          .map((s) => (
            <section key={s.slug}>
              {s.slug === "markets-finance" && null}
              {s.slug === "entertainment" ? (
                <EntertainmentSection pool={s.pool} />
              ) : (
                <HomeCategorySection
                  slug={s.slug}
                  label={s.label}
                  clusters={[]}
                  pool={s.pool}
                  afterHeader={
                    s.slug === "technology" ? <TechBuzz category="tech" /> :
                    s.slug === "sports" ? <TechBuzz category="sports" /> :
                    undefined
                  }
                />
              )}
            </section>
          ))}

        <DiasporaPhotoStrip />
      </main>

      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
