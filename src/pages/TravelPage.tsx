import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import FlightDeals from "@/components/FlightDeals";
import {
  DestinationsByMonth,
  HolidayPlanner,
  InIndiaStrip,
} from "@/components/TravelPlannerSections";
import {
  REGIONS,
  DESTINATIONS,
  VISA_DASHBOARD_BY_STATUS,
  VISA_HOLDER_LABELS,
  getTravelNews,
  visaBadgeColor,
  visaBadgeLabel,
} from "@/lib/travel";
import type { Destination, VisaHolderStatus } from "@/lib/travel";

/* ------------------------------------------------------------------ */
/* Travel News Strip                                                  */
/* ------------------------------------------------------------------ */
function TravelNewsStrip({ news }: { news: any[] }) {
  if (!news.length) return null;
  return (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <span className="text-xl">📰</span>
          <h2 className="font-serif text-xl font-bold">Latest Travel News</h2>
        </div>
      </div>
      <style>{`.travel-news-strip::-webkit-scrollbar { display: none; }`}</style>
      <div
        className="travel-news-strip flex gap-4 overflow-x-auto pb-4"
        style={{
          scrollSnapType: "x mandatory",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
        } as React.CSSProperties}
      >
        {news.map((article: any) => (
          <Link
            key={article.id}
            to={`/articles/${article.slug}`}
            className="block group flex-shrink-0"
            style={{ width: "280px", scrollSnapAlign: "start" }}
          >
            <article className="bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg h-full">
              {article.image_url && (
                <div className="h-36 overflow-hidden">
                  <img
                    src={article.image_url}
                    alt=""
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                </div>
              )}
              <div className="p-4">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Travel</span>
                  <span className="text-[10px] text-foreground/40">
                    {new Date(article.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  </span>
                </div>
                <h3 className="font-semibold text-sm group-hover:text-primary transition-colors line-clamp-2">{article.title}</h3>
                {article.excerpt && (
                  <p className="text-xs text-foreground/50 mt-1 line-clamp-2">{article.excerpt}</p>
                )}
              </div>
            </article>
          </Link>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Visa Dashboard                                                     */
/* ------------------------------------------------------------------ */
const VISA_TABS: VisaHolderStatus[] = ["indian-passport", "us-citizen", "green-card"];
const VISA_TAB_SHORT: Record<VisaHolderStatus, string> = {
  "indian-passport": "US Visa Holder",
  "us-citizen": "US Citizen",
  "green-card": "Green Card",
};

function VisaDashboard({
  activeTab,
}: {
  activeTab: VisaHolderStatus;
}) {
  const cards = VISA_DASHBOARD_BY_STATUS[activeTab];

  return (
    <section className="mb-12">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">🛂</span>
        <h2 className="font-serif text-xl font-bold">Visa Quick Reference</h2>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {cards.map((card) => (
          <Link
            key={card.key}
            to={`/travel/visa-list/${activeTab}/${card.key}`}
            className="block bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg"
          >
            <div className={`px-4 py-2.5 border-b border-border ${card.color}`}>
              <div className="flex items-center gap-2">
                <span className="text-lg">{card.emoji}</span>
                <h3 className="font-serif font-bold text-[13px] leading-tight">{card.label}</h3>
              </div>
            </div>
            <div className="px-4 py-3">
              <div className="flex items-baseline gap-1.5 mb-2">
                <span className={`text-2xl font-bold ${card.textColor}`}>{card.count}+</span>
                <span className="text-[11px] text-foreground/40">countries</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {card.topDestinations.slice(0, 5).map((d) => (
                  <span
                    key={d}
                    className="text-[10px] px-1.5 py-0.5 bg-foreground/5 rounded-full text-foreground/60"
                  >
                    {d}
                  </span>
                ))}
              </div>
              <div className="mt-2 text-[10px] text-primary/60 font-medium">View all →</div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Destination Card                                                   */
/* ------------------------------------------------------------------ */
const HOLDER_SHORT_LABEL: Record<VisaHolderStatus, string> = {
  "indian-passport": "US Visa holder (H-1B, B1/B2)",
  "us-citizen": "US citizen",
  "green-card": "Green Card holder",
};

function DestinationCard({ dest, holderStatus }: { dest: Destination; holderStatus: VisaHolderStatus }) {
  const region = REGIONS.find((r) => r.key === dest.region);
  const visaInfo = dest.visa[holderStatus];
  return (
    <Link
      to={dest.hasGuide ? `/travel/${dest.key}` : "#"}
      className={`block group ${!dest.hasGuide ? "cursor-default" : ""}`}
      onClick={dest.hasGuide ? undefined : (e) => e.preventDefault()}
    >
      <div className="bg-card border border-border rounded-xl p-4 h-full hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 flex flex-col gap-2">
        {/* Top row: name + region emoji */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h3 className="font-semibold text-sm group-hover:text-primary transition-colors leading-tight">
              {region?.emoji} {dest.label}
            </h3>
            <p className="text-[11px] text-foreground/50 leading-tight mt-0.5">{dest.description}</p>
          </div>
          {dest.hasGuide && (
            <ChevronRight className="h-4 w-4 text-foreground/20 group-hover:text-primary transition-colors flex-shrink-0 mt-0.5" />
          )}
        </div>

        {/* Visa badge + note */}
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${visaBadgeColor(visaInfo.status)}`}>
              {visaBadgeLabel(visaInfo.status)}
            </span>
            <span className="text-[10px] text-foreground/40">📅 {dest.bestMonths}</span>
          </div>
          <span className="text-[9px] text-foreground/35 leading-tight pl-0.5">{visaInfo.note}</span>
        </div>

        <div className="flex items-center gap-3 text-[10px] text-foreground/40 mt-auto">
          <span>💰 {dest.budget}</span>
          {dest.hasGuide ? (
            <span className="text-[10px] text-primary/60 font-medium">📖 Guide</span>
          ) : (
            <span className="text-[10px] text-foreground/30 italic">Guide coming soon</span>
          )}
        </div>
      </div>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Main TravelPage                                                    */
/* ------------------------------------------------------------------ */
const DESTINATION_GROUPS: { key: string; heading: string; blurb: string; match: (d: Destination) => boolean }[] = [
  {
    key: "india",
    heading: "🇮🇳 In India",
    blurb: "Side trips and slow travel once you've landed — every state guide we publish.",
    match: (d) => d.region === "india",
  },
  {
    key: "usa-canada",
    heading: "🇺🇸 USA & Canada",
    blurb: "Weekends and road trips from home base.",
    match: (d) => d.region === "usa-canada",
  },
  {
    key: "international",
    heading: "🌍 International",
    blurb: "The big trips — with visa notes for every passport status below.",
    match: (d) => d.region !== "india" && d.region !== "usa-canada",
  },
];

export default function TravelPage() {
  const [holderStatus, setHolderStatus] = useState<VisaHolderStatus>("indian-passport");
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTravelNews(10).then((n) => {
      setNews(n);
      setLoading(false);
    });
  }, []);

  return (
    <>
      <Helmet>
        <title>Travel Hub — Holiday Planner, Flight Deals, Destinations & Visa Guide | The Videshi</title>
        <meta name="description" content="Plan the trip home and the next getaway: holiday travel windows with book-by dates, real US–India fare snapshots, best destinations by month, 49 diaspora guides, and visa quick-reference for Indian passport holders, US citizens, and Green Card holders." />
        <meta property="og:title" content="Travel Hub — The Videshi" />
        <meta property="og:description" content="Destinations, visa quick-reference, and travel news for NRIs and the Indian diaspora." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/travel" />
              <link rel="canonical" href="https://www.thevideshi.com/travel" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* ── Hero ─────────────────────────────────────────── */}
        <section className="relative mb-10 -mx-4 px-4 py-12 md:py-16 rounded-2xl overflow-hidden bg-[#1a2e1a] border border-[#2a4a2a]/40">
          <div
            className="absolute inset-0 opacity-[0.06]"
            style={{
              backgroundImage:
                "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
            }}
          />
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/8 rounded-full blur-3xl" />

          <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-emerald-300 bg-emerald-500/15 px-3 py-1 rounded-full">
                ✈️ Travel Hub
              </span>
            </div>
            <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] text-white">
              Explore the World,<br />
              <span className="text-emerald-400">NRI Style.</span>
            </h1>
            <p className="text-white/70 mt-4 text-lg md:text-xl max-w-2xl leading-relaxed">
              Destinations, visa requirements, and travel news — curated for the Indian diaspora. Know before you go.
            </p>
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* ── Holiday Planner (lead) ─────────────────────── */}
            <HolidayPlanner />

            {/* ── Destinations by Month ──────────────────────── */}
            <DestinationsByMonth />

            {/* ── Flight Deals / India Price Calendar ────────── */}
            <FlightDeals />

            {/* ── While You're in India ──────────────────────── */}
            <InIndiaStrip />

            {/* ── Holder Status Toggle (page-level) ──────────── */}
            <section className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">🧳</span>
                <h2 className="font-serif text-base font-bold">I'm traveling as</h2>
              </div>
              <div className="flex gap-2 overflow-x-auto" style={{ WebkitOverflowScrolling: "touch" }}>
                {VISA_TABS.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setHolderStatus(tab)}
                    className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-semibold border transition-colors ${
                      holderStatus === tab
                        ? "bg-primary text-primary-foreground border-primary"
                        : "border-rule text-foreground/80 hover:text-primary hover:border-primary"
                    }`}
                  >
                    {VISA_TAB_SHORT[tab]}
                  </button>
                ))}
              </div>
            </section>

            {/* ── Visa Dashboard ─────────────────────────────── */}
            <VisaDashboard activeTab={holderStatus} />

            {/* ── All Destinations index ──────────────────────── */}
            <section className="mb-12" id="destinations">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">🗺️</span>
                <h2 className="font-serif text-xl font-bold">All Destinations</h2>
              </div>
              <p className="text-sm text-foreground/55 mb-6 max-w-2xl leading-relaxed">
                Every guide we publish — {DESTINATIONS.length} destinations, one
                travel home. Visa badges update with the “traveling as” choice above.
              </p>

              {DESTINATION_GROUPS.map((group) => {
                const dests = DESTINATIONS.filter(group.match);
                if (!dests.length) return null;
                return (
                  <div key={group.key} className="mb-8">
                    <h3 className="font-serif text-base font-bold mb-1">
                      {group.heading}
                      <span className="text-foreground/40 font-sans text-xs font-semibold ml-2">
                        {dests.length} guides
                      </span>
                    </h3>
                    <p className="text-[12px] text-foreground/45 mb-3">{group.blurb}</p>
                    <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                      {dests.map((d) => (
                        <DestinationCard key={d.key} dest={d} holderStatus={holderStatus} />
                      ))}
                    </div>
                  </div>
                );
              })}
            </section>

            {/* ── Travel News Strip ──────────────────────────── */}
            <div id="travel-news" className="scroll-mt-24">
              <TravelNewsStrip news={news} />
            </div>

            {/* ── Travel Agent CTA ───────────────────────────── */}
            <section className="mb-12">
              <div className="relative p-8 bg-[#1a2e1a] rounded-2xl border border-[#2a4a2a]/40 text-center overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl" />
                <div className="relative z-10">
                  <span className="text-4xl mb-3 block">🧳</span>
                  <h3 className="font-serif text-2xl font-bold text-white mb-2">Find a Travel Agent</h3>
                  <p className="text-white/60 text-sm mb-5 max-w-lg mx-auto">
                    Browse our directory of travel agencies specializing in India trips, NRI packages, and visa assistance.
                  </p>
                  <Link
                    to="/directory?category=Travel"
                    className="inline-flex items-center gap-2 bg-emerald-500 text-black font-semibold text-sm py-2.5 px-6 rounded-full hover:bg-emerald-400 transition-colors"
                  >
                    Browse Travel Agents <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
