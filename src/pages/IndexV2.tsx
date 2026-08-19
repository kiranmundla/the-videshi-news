import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import MarketTicker from "@/components/MarketTicker";
import SiteFooter from "@/components/SiteFooter";
import DiasporaPhotoStrip from "@/components/DiasporaPhotoStrip";

import HappeningToday from "@/components/homepage/HappeningToday";
import HeroSection from "@/components/homepage/HeroSection";
import ImmigrationStrip from "@/components/homepage/ImmigrationStrip";
import NewsletterCTA from "@/components/homepage/NewsletterCTA";
import LeadListSection from "@/components/homepage/LeadListSection";
import RibbonSection from "@/components/homepage/RibbonSection";
import IndiaNewsGrid from "@/components/homepage/IndiaNewsGrid";
import NewsGrid from "@/components/homepage/NewsGrid";
import VoicesSection from "@/components/homepage/VoicesSection";
import EventsStrip from "@/components/homepage/EventsStrip";
import { useUserLocation } from "@/hooks/useUserLocation";
import TweetScroll from "@/components/homepage/TweetScroll";
import InstagramPhotoScroll from "@/components/homepage/InstagramPhotoScroll";
import WhosXSpotlight, { getSpotlightIds } from "@/components/homepage/WhosXSpotlight";
import DailyWisdomCard from "@/components/homepage/DailyWisdomCard";
import OnThisDay from "@/components/homepage/OnThisDay";
import DailyQuiz from "@/components/homepage/DailyQuiz";
import ThePulse from "@/components/homepage/ThePulse";
import FridayLaughs from "@/components/homepage/FridayLaughs";
import DevelopingStories from "@/components/homepage/DevelopingStories";
import ArticleCardDeck from "@/components/homepage/ArticleCardDeck";
import JustInStrip from "@/components/homepage/JustInStrip";
import HubStrip from "@/components/homepage/HubStrip";
import NowInTheaters from "@/components/NowInTheaters";
import StreamingPicks from "@/components/StreamingPicks";
import UpcomingTechEvents from "@/components/homepage/UpcomingTechEvents";
import AILeaderboard from "@/components/AILeaderboard";
import KeyUpdatesSection from "@/components/KeyUpdatesSection";
import ArticleCard from "@/components/ArticleCard";
import CategorySubTopics, { hasSubTopics } from "@/components/homepage/CategorySubTopics";
import SponsoredBanner from "@/components/SponsoredBanner";
import "@/components/homepage/homepage-v2.css";

import {
  Article,
  getArticlesByCategory,
  getFeaturedArticle,
  getTopStories,
} from "@/lib/articles";

// ── Types ──
type EventItem = {
  id: string;
  title: string;
  date: string;
  time?: string;
  venue_name?: string;
  city?: string;
  state?: string;
  category?: string;
};

// ── Cache ──
const CACHE_KEY = "videshi_home_v2_cache";
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

type HomeCache = {
  ts: number;
  featured: Article | null;
  sections: Record<string, Article[]>;
  events: EventItem[];
  justIn?: Article[];
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





/* ── Category Nav (above Featured section on homepage) ── */
const HOME_CATEGORIES = [
  { slug: "", label: "Home", path: "/" },
  { slug: "news", label: "India", path: "/news" },
  { slug: "nri-world", label: "World", path: "/nri-world" },
  { slug: "immigration", label: "Immigration", path: "/immigration" },
  { slug: "technology", label: "Technology", path: "/technology" },
  { slug: "sports", label: "Sports", path: "/sports" },
  { slug: "markets-finance", label: "Markets", path: "/markets-finance" },
  { slug: "entertainment", label: "Entertainment", path: "/entertainment" },
  { slug: "lifestyle-health", label: "Lifestyle", path: "/lifestyle-health" },
  { slug: "travel", label: "Travel", path: "/travel" },
  { slug: "food", label: "Food", path: "/food" },
];

function HomeCategoryNav({ selected, onSelect }: { selected: string; onSelect: (slug: string) => void }) {
  return (
    <div className="v2-home-cat-nav">
      <div className="v2-home-cat-nav-inner">
        {HOME_CATEGORIES.map((cat) => (
          <button
            key={cat.slug}
            onClick={() => onSelect(cat.slug)}
            className={`v2-home-cat-pill${cat.slug === selected ? " active" : ""}`}
          >
            {cat.label}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ── Entertainment Vertical Grid ── */
function EntertainmentGrid({ articles }: { articles: Article[] }) {
  const [visibleCount, setVisibleCount] = useState(6);
  if (articles.length === 0) return null;

  // Trim to multiples of 3 for clean grid rows
  const fullCount = Math.floor(Math.min(visibleCount, articles.length) / 3) * 3;
  const shown = articles.slice(0, fullCount || Math.min(articles.length, 3));
  const hasMore = articles.length > visibleCount;

  return (
    <section className="mb-14">
      <div className="container">
        <div
          className="flex items-center mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #AD1457" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            Entertainment
          </h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-10 items-start">
          {shown.map((a) => (
            <ArticleCard key={a.id} article={a} variant="card" />
          ))}
        </div>
        {hasMore && (
          <div className="flex justify-center mt-8">
            <button
              onClick={() => setVisibleCount((v) => v + 6)}
              className="text-[11px] font-bold tracking-[0.12em] uppercase text-foreground/60 border border-rule px-8 py-2.5 hover:border-foreground/40 hover:text-foreground/80 bg-transparent transition-colors"
            >
              MORE STORIES
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

/* ── Live Events Strip (rendered after hub icons on homepage) ── */
const LIVE_EVENTS = [
  { slug: "world-cup", label: "FIFA World Cup", path: "/world-cup", icon: "⚽" },
];

function LiveStrip() {
  if (LIVE_EVENTS.length === 0) return null;
  return (
    <div className="v2-home-live-strip">
      <span className="v2-home-live-dot-wrap">
        <span className="v2-home-live-ping" />
        <span className="v2-home-live-dot" />
      </span>
      <span className="v2-home-live-label">Live</span>
      {LIVE_EVENTS.map((e) => (
        <Link key={e.slug} to={e.path} className="v2-home-live-link">
          <span className="v2-home-live-icon">{e.icon}</span>
          <span className="v2-home-live-text">{e.label}</span>
        </Link>
      ))}
    </div>
  );
}

// ── Component ──
export default function IndexV2() {
  const { location: userLocation } = useUserLocation();
  const initialCache = useRef(loadCache()).current;
  const [featured, setFeatured] = useState<Article | null>(initialCache?.featured ?? null);
  const [sections, setSections] = useState<Record<string, Article[]>>(initialCache?.sections ?? {});
  const [events, setEvents] = useState<EventItem[]>(initialCache?.events ?? []);
  const [justIn, setJustIn] = useState<Article[]>(initialCache?.justIn ?? []);
  const [loading, setLoading] = useState(!initialCache);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(
    initialCache ? new Date(initialCache.ts) : null
  );
  const [selectedCategory, setSelectedCategory] = useState("");
  const [categoryArticles, setCategoryArticles] = useState<Article[]>([]);
  const [catLoading, setCatLoading] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const catNavRef = useRef<HTMLDivElement>(null);

  // Read ?cat= from URL on mount / URL change
  useEffect(() => {
    const catParam = searchParams.get("cat");
    if (catParam) {
      setSelectedCategory(catParam);
      // Clear the query param so URL stays clean
      setSearchParams({}, { replace: true });
      // Scroll to category nav area
      setTimeout(() => {
        catNavRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    }
  }, [searchParams, setSearchParams]);

  // Reset category when logo is clicked (even if already on /)
  useEffect(() => {
    const reset = () => setSelectedCategory("");
    window.addEventListener("videshi-go-home", reset);
    return () => window.removeEventListener("videshi-go-home", reset);
  }, []);

  useEffect(() => {
    if (initialCache) return;

    const applyData = (
      f: Article | null,
      sp: Record<string, Article[]>,
      ev: EventItem[],
      ts: Date,
      ji?: Article[]
    ) => {
      setFeatured(f);
      setSections(sp);
      setEvents(ev);
      if (ji) setJustIn(ji);
      setLastUpdated(ts);
      setLoading(false);
      saveCache({ ts: Date.now(), featured: f, sections: sp, events: ev, justIn: ji ?? [] });
    };

    // Try static JSON first (CDN fast path)
    const fetchStaticJSON = async () => {
      try {
        const [feedResp, eventsResp] = await Promise.all([
          fetch(`/data/homepage-feed.json?v=${Date.now()}`),
          fetch(`/data/events-homepage.json?v=${Date.now()}`),
        ]);

        if (!feedResp.ok) throw new Error("Feed unavailable");

        const feedData = await feedResp.json();
        // If feed is older than 30 minutes, treat as stale and fallback to Supabase
        const feedAge = Date.now() - new Date(feedData.generated_at).getTime();
        if (feedAge > 30 * 60 * 1000) throw new Error("Feed stale");
        const eventsData = eventsResp.ok ? await eventsResp.json() : [];

        const sp: Record<string, Article[]> = {};
        for (const [k, v] of Object.entries(feedData.sections || {})) {
          sp[k] = v as Article[];
        }

        applyData(
          feedData.featured ?? null,
          sp,
          Array.isArray(eventsData) ? eventsData : [],
          new Date(feedData.generated_at),
          (feedData.just_in ?? []) as Article[]
        );
      } catch {
        // Fallback to Supabase
        fetchFromSupabase();
      }
    };

    const fetchFromSupabase = async () => {
      const timeout = setTimeout(() => setLoading(false), 8000);
      try {
        const [
          f,
          newsPool,
          nriPool,
          techPool,
          entPool,
          marketsPool,
          sportsPool,
          immPool,
          lifestylePool,
          foodPool,
          travelPool,
        ] = await Promise.all([
          getFeaturedArticle().catch(() => null),
          getArticlesByCategory("news", 20).catch(() => []),
          getArticlesByCategory("nri-world", 12).catch(() => []),
          getArticlesByCategory("technology", 12).catch(() => []),
          getArticlesByCategory("entertainment", 12).catch(() => []),
          getArticlesByCategory("markets-finance", 12).catch(() => []),
          getArticlesByCategory("sports", 12).catch(() => []),
          getArticlesByCategory("immigration", 12).catch(() => []),
          getArticlesByCategory("lifestyle-health", 8).catch(() => []),
          getArticlesByCategory("food", 8).catch(() => []),
          getArticlesByCategory("travel", 8).catch(() => []),
        ]);

        clearTimeout(timeout);

        const sp: Record<string, Article[]> = {
          news: newsPool,
          "nri-world": nriPool,
          technology: techPool,
          entertainment: entPool,
          "markets-finance": marketsPool,
          sports: sportsPool,
          immigration: immPool,
          "lifestyle-health": lifestylePool,
          food: foodPool,
          travel: travelPool,
        };

        // Fetch events
        let ev: EventItem[] = [];
        try {
          const evResp = await fetch("/data/events-homepage.json");
          if (evResp.ok) ev = await evResp.json();
        } catch {}

        // Build just_in from all pools (purely chronological, most recent 20 candidates)
        const allPool = [
          ...newsPool, ...nriPool, ...techPool, ...entPool,
          ...marketsPool, ...sportsPool, ...immPool,
          ...lifestylePool, ...foodPool, ...travelPool,
        ]
          .filter((a) => a.hero_image_url)
          .sort((a, b) => {
            const aTime = new Date(a.event_at || a.published_at).getTime();
            const bTime = new Date(b.event_at || b.published_at).getTime();
            return bTime - aTime;
          })
          .slice(0, 20);

        applyData(f, sp, ev, new Date(), allPool);
      } catch {
        clearTimeout(timeout);
        setLoading(false);
      }
    };

    fetchStaticJSON();
  }, []);

  // ── Fetch articles when a category is selected ──
  useEffect(() => {
    if (!selectedCategory) {
      setCategoryArticles([]);
      return;
    }
    setCatLoading(true);
    // Try static JSON first, fallback to Supabase
    const fetchLimit = hasSubTopics(selectedCategory) ? 60 : 30;
    fetch(`/data/category/${selectedCategory}.json`)
      .then((r) => {
        if (!r.ok) throw new Error("not found");
        return r.json();
      })
      .then((data) => {
        setCategoryArticles(data.articles ?? []);
        setCatLoading(false);
      })
      .catch(() => {
        // Fallback to Supabase for categories without static JSON (e.g. immigration)
        getArticlesByCategory(selectedCategory, fetchLimit)
          .then((articles) => {
            setCategoryArticles(articles);
            setCatLoading(false);
          })
          .catch(() => setCatLoading(false));
      });
  }, [selectedCategory]);

  // ── Scroll position save/restore ── (handled by useScrollRestore in App.tsx)

  // ── Derive layout data ──
  const layout = useMemo(() => {
    const shownIds = new Set<string>();

    // Exclude Who's Who spotlight articles from all pools
    for (const sid of getSpotlightIds()) shownIds.add(sid);

    // Featured
    if (featured) shownIds.add(featured.id);

    // All pools
    const allArticles = Object.values(sections).flat();

    // Trending: top 6 by recency across all sections
    const trending = [...allArticles]
      .filter((a) => !shownIds.has(a.id))
      .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime())
      .slice(0, 6);

    // Hero side: top article from each major category (excluding featured's category)
    const HERO_CATS: { slug: string }[] = [
      { slug: "immigration" },
      { slug: "news" },
      { slug: "nri-world" },
      { slug: "technology" },
      { slug: "entertainment" },
      { slug: "markets-finance" },
      { slug: "sports" },
    ];
    const heroSide: Article[] = [];
    const featuredCat = featured?.category ?? "";
    for (const { slug } of HERO_CATS) {
      if (slug === featuredCat) continue;
      const pool = sections[slug] ?? [];
      const pick = pool.find((a) => !shownIds.has(a.id));
      if (pick) heroSide.push(pick);
    }
    heroSide.forEach((a) => shownIds.add(a.id));

    // Immigration
    const immigration = (sections.immigration ?? []).filter((a) => !shownIds.has(a.id));

    // Technology
    const technology = (sections.technology ?? []).filter((a) => !shownIds.has(a.id));

    // Entertainment
    const entertainment = (sections.entertainment ?? []).filter((a) => !shownIds.has(a.id));

    // India News
    const news = (sections.news ?? []).filter((a) => !shownIds.has(a.id));

    // Markets & Finance
    const markets = (sections["markets-finance"] ?? []).filter((a) => !shownIds.has(a.id));

    // NRI World
    const nriWorld = (sections["nri-world"] ?? []).filter((a) => !shownIds.has(a.id));

    // Sports
    const sports = (sections.sports ?? []).filter((a) => !shownIds.has(a.id));

    // Lifestyle & Health
    const lifestyle = (sections["lifestyle-health"] ?? []).filter((a) => !shownIds.has(a.id));

    // Food
    const food = (sections.food ?? []).filter((a) => !shownIds.has(a.id));

    // Travel
    const travel = (sections.travel ?? []).filter((a) => !shownIds.has(a.id));

    // Voices teaser: pick an immigration or NRI article with good excerpt
    const voicesTeaser =
      immigration.find((a) => a.excerpt && a.excerpt.length > 80) ??
      nriWorld.find((a) => a.excerpt && a.excerpt.length > 80) ??
      null;

    return {
      trending,
      heroSide,
      immigration,
      technology,
      entertainment,
      news,
      markets,
      nriWorld,
      sports,
      lifestyle,
      food,
      travel,
      voicesTeaser,
    };
  }, [featured, sections]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">
          Loading…
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>The Videshi — News for the global Indian diaspora</title>
        <meta
          name="description"
          content="Editorial reporting and analysis for the global Indian diaspora — immigration, technology, entertainment, markets, NRI world, and sports."
        />
        <meta property="og:title" content="The Videshi" />
        <meta property="og:description" content="News for the global Indian diaspora" />
        {featured && <meta property="og:image" content={featured.hero_image_url} />}
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
                  url: "https://www.thevideshi.com/logo.jpg",
                },
                sameAs: [
                  "https://www.instagram.com/thevideshi",
                  "https://x.com/thevideshi",
                ],
                description:
                  "Editorial reporting and analysis for the global Indian diaspora — immigration, technology, entertainment, markets, NRI world, and sports.",
              },
              {
                "@type": "WebSite",
                "@id": "https://www.thevideshi.com/#website",
                url: "https://www.thevideshi.com",
                name: "The Videshi",
                publisher: {
                  "@id": "https://www.thevideshi.com/#organization",
                },
                potentialAction: {
                  "@type": "SearchAction",
                  target: {
                    "@type": "EntryPoint",
                    urlTemplate:
                      "https://www.thevideshi.com/search?q={search_term_string}",
                  },
                  "query-input": "required name=search_term_string",
                },
              },
            ],
          })}
        </script>
      </Helmet>

      {/* 1. Masthead (includes category pills + community nav row) */}
      <Masthead />

      {/* 2. Hub Icons */}
      <HubStrip />

      {/* 4. Market Ticker */}
      <div className="container">
        <MarketTicker />
      </div>

      {/* 5. Happening Today */}
      <HappeningToday />

      <main className="flex-1 v2-main-sections">
        {/* Category Nav */}
        <div ref={catNavRef}>
          <HomeCategoryNav selected={selectedCategory} onSelect={setSelectedCategory} />
        </div>

        {selectedCategory ? (
          /* ── Category-filtered view ── */
          <>
            <KeyUpdatesSection category={selectedCategory} />
            {selectedCategory === "technology" && <AILeaderboard />}
            {selectedCategory === "technology" && <UpcomingTechEvents />}
            {catLoading ? (
              <div className="container py-12 text-center text-muted-foreground">Loading…</div>
            ) : categoryArticles.length === 0 ? (
              <div className="container py-12 text-center text-muted-foreground">No articles yet.</div>
            ) : hasSubTopics(selectedCategory) ? (
              /* Sub-topic grouped view */
              <CategorySubTopics category={selectedCategory} articles={categoryArticles} />
            ) : (
              /* Flat grid for categories without sub-topics */
              <section className="container" style={{ padding: "24px 16px" }}>
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                  gap: "20px",
                }}>
                  {categoryArticles.map((a) => (
                    <ArticleCard key={a.id} article={a} variant="card" />
                  ))}
                </div>
              </section>
            )}
          </>
        ) : (
          /* ── Full homepage view ── */
          <>
        <HeroSection lead={featured} side={layout.heroSide} />
        <DevelopingStories />

        {/* Just In — purely chronological, newest articles across all categories */}
        <JustInStrip articles={justIn.filter((a) => a.id !== featured?.id && !layout.heroSide.some((h) => h.id === a.id))} />

        {/* Daily Wisdom — picture-framed spiritual quote */}
        <DailyWisdomCard />

        {/* On This Day — daily diaspora history card */}
        <OnThisDay />

        {/* Daily 7 Quiz */}
        <DailyQuiz />

        {/* The Pulse — community poll */}
        <ThePulse />

        {/* Who's X — weekly spotlight */}
        <WhosXSpotlight />

        {/* Visual Stories */}
        <ArticleCardDeck />

        {/* 7. Immigration Strip */}
        <ImmigrationStrip articles={layout.immigration} />

        {/* 8. Newsletter CTA */}
        <NewsletterCTA />

        {/* 9. (VoicesTeaser removed — VoicesSection below covers Voices) */}

        {/* 10. Technology (lead + list) */}
        <UpcomingTechEvents />
        <LeadListSection
          title="Technology"
          borderColor="#4527A0"
          categorySlug="technology"
          articles={layout.technology}
          listCount={9}
        />
        <TweetScroll category="technology" />

        {/* 11. Entertainment (vertical grid) */}
        <SponsoredBanner />
        <EntertainmentGrid articles={layout.entertainment} />
        <NowInTheaters />
        <StreamingPicks />
        <FridayLaughs />

        {/* 12. India News + Trending Sidebar */}
        <IndiaNewsGrid
          articles={layout.news}
        />
        <TweetScroll category="news" label="India News" />

        {/* 13. World News (3-col grid) */}
        <NewsGrid
          title="World News"
          borderColor="#1565C0"
          categorySlug="nri-world"
          articles={layout.nriWorld}
          columns={3}
        />
        <TweetScroll category="world-leaders" label="World Leaders" />

        {/* 14. Markets & Finance (lead + list) */}
        <LeadListSection
          title="Markets & Finance"
          borderColor="#E65100"
          categorySlug="markets-finance"
          articles={layout.markets}
          listCount={6}
        />

        {/* 15. Sports (horizontal ribbon — landscape) */}
        <RibbonSection
          title="Sports"
          borderColor="#2E7D32"
          categorySlug="sports"
          articles={layout.sports}
          aspectRatio="landscape"
        />
        <TweetScroll category="sports" />

        {/* 16. Travel (horizontal ribbon — landscape) */}
        {layout.travel.length > 0 && (
          <RibbonSection
            title="Travel"
            borderColor="#00695C"
            categorySlug="travel"
            articles={layout.travel}
            aspectRatio="landscape"
          />
        )}

        {/* 17. Lifestyle & Health (lead + list) */}
        {layout.lifestyle.length > 0 && (
          <LeadListSection
            title="Lifestyle & Health"
            borderColor="#6A1B9A"
            categorySlug="lifestyle-health"
            articles={layout.lifestyle}
            listCount={6}
          />
        )}

        {/* 18. Food (horizontal ribbon — landscape) */}
        {layout.food.length > 0 && (
          <RibbonSection
            title="Food"
            borderColor="#BF360C"
            categorySlug="food"
            articles={layout.food}
            aspectRatio="landscape"
          />
        )}

        {/* 19. Voices (full section) */}
        <VoicesSection />

        {/* 17. Events */}
        <EventsStrip
          events={events}
          userLat={userLocation?.latitude}
          userLng={userLocation?.longitude}
          userCity={userLocation?.city}
        />

        {/* 18. Snapshots */}
        <DiasporaPhotoStrip />
          </>
        )}
      </main>

      {/* 19. Footer */}
      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
