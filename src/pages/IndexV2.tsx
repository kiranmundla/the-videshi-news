import { useEffect, useMemo, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import MarketTicker from "@/components/MarketTicker";
import SiteFooter from "@/components/SiteFooter";
import DiasporaPhotoStrip from "@/components/DiasporaPhotoStrip";

import TrendingStrip from "@/components/homepage/TrendingStrip";
import HeroSection from "@/components/homepage/HeroSection";
import ImmigrationStrip from "@/components/homepage/ImmigrationStrip";
import NewsletterCTA from "@/components/homepage/NewsletterCTA";
import VoicesTeaser from "@/components/homepage/VoicesTeaser";
import LeadListSection from "@/components/homepage/LeadListSection";
import RibbonSection from "@/components/homepage/RibbonSection";
import IndiaNewsGrid from "@/components/homepage/IndiaNewsGrid";
import NewsGrid from "@/components/homepage/NewsGrid";
import VoicesSection from "@/components/homepage/VoicesSection";
import EventsStrip from "@/components/homepage/EventsStrip";
import TweetScroll from "@/components/homepage/TweetScroll";
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

// ── Component ──
export default function IndexV2() {
  const initialCache = useRef(loadCache()).current;
  const [featured, setFeatured] = useState<Article | null>(initialCache?.featured ?? null);
  const [sections, setSections] = useState<Record<string, Article[]>>(initialCache?.sections ?? {});
  const [events, setEvents] = useState<EventItem[]>(initialCache?.events ?? []);
  const [loading, setLoading] = useState(!initialCache);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(
    initialCache ? new Date(initialCache.ts) : null
  );

  useEffect(() => {
    if (initialCache) return;

    const applyData = (
      f: Article | null,
      sp: Record<string, Article[]>,
      ev: EventItem[],
      ts: Date
    ) => {
      setFeatured(f);
      setSections(sp);
      setEvents(ev);
      setLastUpdated(ts);
      setLoading(false);
      saveCache({ ts: Date.now(), featured: f, sections: sp, events: ev });
    };

    // Try static JSON first (CDN fast path)
    const fetchStaticJSON = async () => {
      try {
        const [feedResp, eventsResp] = await Promise.all([
          fetch("/data/homepage-feed.json"),
          fetch("/data/events.json"),
        ]);

        if (!feedResp.ok) throw new Error("Feed unavailable");

        const feedData = await feedResp.json();
        const eventsData = eventsResp.ok ? await eventsResp.json() : [];

        const sp: Record<string, Article[]> = {};
        for (const [k, v] of Object.entries(feedData.sections || {})) {
          sp[k] = v as Article[];
        }

        applyData(
          feedData.featured ?? null,
          sp,
          Array.isArray(eventsData) ? eventsData : [],
          new Date(feedData.generated_at)
        );

        // Fetch immigration separately (not in homepage-feed.json)
        try {
          const immArticles = await getArticlesByCategory("immigration", 12);
          setSections((prev) => ({ ...prev, immigration: immArticles }));
        } catch {}
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
        };

        // Fetch events
        let ev: EventItem[] = [];
        try {
          const evResp = await fetch("/data/events.json");
          if (evResp.ok) ev = await evResp.json();
        } catch {}

        applyData(f, sp, ev, new Date());
      } catch {
        clearTimeout(timeout);
        setLoading(false);
      }
    };

    fetchStaticJSON();
  }, []);

  // ── Scroll position save/restore ──
  useEffect(() => {
    return () => {
      sessionStorage.setItem("homeScrollY", window.scrollY.toString());
    };
  }, []);

  useEffect(() => {
    if (loading) return;
    const savedY = sessionStorage.getItem("homeScrollY");
    if (!savedY) return;
    const targetY = parseInt(savedY, 10);
    if (targetY <= 0) return;
    sessionStorage.removeItem("homeScrollY");

    requestAnimationFrame(() => {
      window.scrollTo(0, targetY);
      let attempts = 0;
      const retry = () => {
        if (Math.abs(window.scrollY - targetY) > 50 && attempts < 10) {
          window.scrollTo(0, targetY);
          attempts++;
          requestAnimationFrame(retry);
        }
      };
      requestAnimationFrame(retry);
    });
  }, [loading]);

  // ── Derive layout data ──
  const layout = useMemo(() => {
    const shownIds = new Set<string>();

    // Featured
    if (featured) shownIds.add(featured.id);

    // All pools
    const allArticles = Object.values(sections).flat();

    // Trending: top 6 by recency across all sections
    const trending = [...allArticles]
      .filter((a) => !shownIds.has(a.id))
      .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime())
      .slice(0, 6);

    // Hero: featured + 3 side articles from top stories
    const heroSide = allArticles
      .filter((a) => !shownIds.has(a.id) && a.id !== featured?.id)
      .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime())
      .slice(0, 3);
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

      {/* 4. Market Ticker */}
      <MarketTicker />

      {/* 5. Trending Strip */}
      <TrendingStrip articles={layout.trending} />

      <main className="flex-1">
        {/* 6. Hero Section */}
        <HeroSection lead={featured} side={layout.heroSide} />

        {/* 7. Immigration Strip */}
        <ImmigrationStrip articles={layout.immigration} />

        {/* 8. Newsletter CTA */}
        <NewsletterCTA />

        {/* 9. Voices Teaser */}
        <VoicesTeaser article={layout.voicesTeaser} />

        {/* 10. Technology (lead + list) */}
        <LeadListSection
          title="Technology"
          borderColor="#4527A0"
          categorySlug="technology"
          articles={layout.technology}
        />
        <div className="container"><TweetScroll category="technology" /></div>

        {/* 11. Entertainment (horizontal ribbon — portrait, 8 cards) */}
        <RibbonSection
          title="Entertainment"
          borderColor="#AD1457"
          categorySlug="entertainment"
          articles={layout.entertainment}
          aspectRatio="portrait"
          cardCount={8}
        />

        {/* 12. India News + Trending Sidebar */}
        <IndiaNewsGrid
          articles={layout.news}
          trending={layout.trending}
        />
        <div className="container"><TweetScroll category="news" label="India News" /></div>

        {/* 13. Markets & Finance (lead + list) */}
        <LeadListSection
          title="Markets & Finance"
          borderColor="#E65100"
          categorySlug="markets-finance"
          articles={layout.markets}
        />

        {/* 14. NRI World (3-col grid) */}
        <NewsGrid
          title="NRI World"
          borderColor="#1565C0"
          categorySlug="nri-world"
          articles={layout.nriWorld}
          columns={3}
        />

        {/* 15. Sports (horizontal ribbon — landscape) */}
        <RibbonSection
          title="Sports"
          borderColor="#2E7D32"
          categorySlug="sports"
          articles={layout.sports}
          aspectRatio="landscape"
          cardCount={4}
        />
        <div className="container"><TweetScroll category="sports" /></div>

        {/* 16. Voices (full section) */}
        <VoicesSection />

        {/* 17. Events */}
        <EventsStrip events={events} />

        {/* 18. Snapshots */}
        <DiasporaPhotoStrip />
      </main>

      {/* 19. Footer */}
      <SiteFooter lastUpdated={lastUpdated} />
    </div>
  );
}
