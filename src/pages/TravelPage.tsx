import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import FlightDeals from "@/components/FlightDeals";
import TrendingDestinations from "@/components/TrendingDestinations";
import {
  REGIONS,
  DESTINATIONS,
  VISA_DASHBOARD_BY_STATUS,
  VISA_HOLDER_LABELS,
  getTravelNews,
  visaBadgeColor,
  visaBadgeLabel,
  visaNoteAddsInfo,
} from "@/lib/travel";
import type { Destination, VisaHolderStatus } from "@/lib/travel";

/* ------------------------------------------------------------------ */
/* Section header system — the redesign's one treatment for every     */
/* /travel section (Kiran approved mockup, 2026-10-15): gold kicker,  */
/* serif navy title, hairline with a gold tick. TrendingDestinations  */
/* and FlightDeals render the same treatment inline (the rail needs   */
/* its counter pill in the title row; the fares header sits inside    */
/* the cream panel, so its hairline is navy-tinted).                  */
/* ------------------------------------------------------------------ */
function SectionHead({
  kicker,
  title,
  sub,
}: {
  kicker: string;
  title: string;
  sub?: string;
}) {
  return (
    <div className="mb-5">
      <div className="relative border-b border-rule pb-3">
        <p className="text-[11px] font-bold uppercase tracking-[2px] text-[#7a5c14] dark:text-[#D4A843] mb-1">
          {kicker}
        </p>
        <h2
          className="font-serif text-xl font-bold leading-none"
          style={{ color: "#0B1D3A" }}
        >
          {title}
        </h2>
        <span className="absolute left-0 -bottom-px h-[2px] w-10 bg-[#D4A843]" />
      </div>
      {sub && (
        <p className="text-sm text-foreground/55 leading-relaxed mt-3">{sub}</p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Travel News Strip                                                  */
/* ------------------------------------------------------------------ */
function TravelNewsStrip({ news }: { news: any[] }) {
  if (!news.length) return null;
  return (
    <section className="mb-12">
      <SectionHead kicker="Stay current" title="Latest Travel News" />
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
      <SectionHead kicker="Before you fly" title="Visa Quick Reference" />

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

        {/* Visa badge + note — the note prints ONLY when it adds a
            condition/duration/mechanism beyond the badge (audit
            item 10); survivors get the legible 10px/50% treatment. */}
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${visaBadgeColor(visaInfo.status)}`}>
              {visaBadgeLabel(visaInfo.status)}
            </span>
            <span className="text-[10px] text-foreground/40">📅 {dest.bestMonths}</span>
          </div>
          {visaNoteAddsInfo(visaInfo) && (
            <span className="text-[10px] text-foreground/50 leading-tight pl-0.5">{visaInfo.note}</span>
          )}
        </div>

        <div className="flex items-center gap-3 text-[10px] text-foreground/40 mt-auto">
          <span>💰 {dest.budget}</span>
          {!dest.hasGuide && (
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
/* Group order is deliberate (Kiran, 2026-10-15): NO India country
   page — the India state destinations are the first group of this
   index (which follows the fares hub and the travel articles in the
   redesign order), one click through to each state page. The other
   groups keep their relative order after it. */
const DESTINATION_GROUPS: { key: string; heading: string; blurb: string; match: (d: Destination) => boolean }[] = [
  {
    key: "india",
    heading: "🇮🇳 India Destinations",
    blurb: "Flying to India — state guides for the trip home.",
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
    blurb: "The big trips — visa notes on every card for your passport status.",
    match: (d) => d.region !== "india" && d.region !== "usa-canada",
  },
];

export default function TravelPage() {
  const [holderStatus, setHolderStatus] = useState<VisaHolderStatus>("indian-passport");
  const [news, setNews] = useState<any[]>([]);

  /* UN-GATED (relook Phase 0 / "zippy" bar, 2026-10-15): the page
     used to render NOTHING until this Supabase news query resolved —
     the bottom-of-page news section held the deals hostage behind a
     full-page spinner. Sections now render independently; the news
     strip fills its own slot when its data lands (and renders
     nothing until then, as before). */
  useEffect(() => {
    getTravelNews(10).then((n) => {
      setNews(n);
    });
  }, []);

  /* Hash deep-links (e.g. /travel#india-destinations from the
     trending rail's India card, /travel#flight-deals from
     destination pages): react-router does not scroll to a hash on
     navigation, so do it here once the page has mounted. Two
     attempts — the fares hub above the index loads async and can
     shift the target's position after the first scroll. */
  useEffect(() => {
    const id = window.location.hash.replace("#", "");
    if (!id) return;
    const timers = [300, 1400].map((ms) =>
      window.setTimeout(() => {
        document
          .getElementById(id)
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, ms),
    );
    return () => timers.forEach((t) => window.clearTimeout(t));
  }, []);

  return (
    <>
      <Helmet>
        <title>Travel Hub — Cheapest Fares, Top Destinations & Visa Guide | The Videshi</title>
        <meta name="description" content="Plan the trip home and the next getaway: real US–India fare snapshots, cheapest fares to top destinations, 49 diaspora travel guides, and visa quick-reference for Indian passport holders, US citizens, and Green Card holders." />
        <meta property="og:title" content="Travel Hub — The Videshi" />
        <meta property="og:description" content="Destinations, visa quick-reference, and travel news for NRIs and the Indian diaspora." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/travel" />
              <link rel="canonical" href="https://www.thevideshi.com/travel" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-6">
        {/* ── Header — minimal (Kiran, 2026-10-15: the giant green
            "Explore the World" hero block was too big; a slim title
            row is enough — the destinations scroll opens the page).
            Navy/gold idiom, no banner block. ──────────────────── */}
        <header className="mb-6">
          <span className="inline-block text-[11px] font-bold uppercase tracking-[2px] px-2.5 py-1 rounded-full bg-[#D4A843]/20 text-[#7a5c14] dark:text-[#D4A843]">
            ✈️ Travel Hub
          </span>
          <h1 className="font-serif text-[26px] md:text-3xl font-bold tracking-tight leading-tight mt-2.5" style={{ color: "#0B1D3A" }}>
            Explore the World, <span style={{ color: "#A32D2F" }}>NRI Style.</span>
          </h1>
          {/* Narration paragraph DELETED (audit item 5): the masthead
              above already says "News for the global Indian diaspora";
              the three nouns merely named the sections below. */}
        </header>

        {/* ── Book-by urgency strip REMOVED 2026-10-15
            (Kiran: "Remove this holiday window section here
            as well" — the last Holiday Planner remnant on
            /travel). The BookByUrgencyStrip component and
            planner data stay in TravelPlannerSections.tsx /
            lib, parked — restoring is re-adding this render
            + its import. ── */}

        {/* ── 1 · Top Destinations to Visit — the destinations
            scroll OPENS the page (redesign brief #1, Kiran
            approved mockup 2026-10-15), India card included.
            NO holiday-window urgency strip anywhere on the
            page — removed entirely at Kiran's word 19:50. ───── */}
        <TrendingDestinations />

        {/* ── 2 · Cheapest Fares — the deals engine in the cream
            panel that marks it as the page's working tool
            (redesign brief #2). Opens directly with its header
            + origin dropdown; the panel owns the section's
            bottom spacing (FlightDeals renders mb-0 inside). ── */}
        <div className="rounded-[24px] border border-[#D4A843]/30 bg-[#FBF6EA] px-4 py-5 sm:px-6 mb-12">
          <FlightDeals />
        </div>

        {/* ── 3 · Travel articles — moved up from the bottom of
            the old page (redesign brief #3). Still un-gated:
            the strip fills this slot when its data lands. ──── */}
        <div id="travel-news" className="scroll-mt-24">
          <TravelNewsStrip news={news} />
        </div>

        {/* ── "While You're in India" strip REMOVED 2026-10-15
            (Kiran: drop within-India coverage for now, focus on
            USA-outbound international travel). The InIndiaStrip
            component and planner data stay in place, parked —
            restoring is re-adding this render + its import. ── */}

        {/* ── "Best Places to Go — by Month" REMOVED 2026-10-15
            (Kiran: "Park it entirely, no filter" — no slimmed
            month-filter salvage). The DestinationsByMonth
            component stays in TravelPlannerSections.tsx, parked —
            restoring is re-adding this render + its import.
            The travel-by-month data pipeline keeps running
            untouched: its season data feeds the trending score
            and the "In season now" card tags. ── */}

        {/* ── 4 · All Destinations index — the passport toggle is
            this section's CONTROL BAR (redesign brief #4): a
            light bordered strip directly under the section
            header, directly above the guide cards whose visa
            badges it drives (India Destinations first). The
            count lives in the heading (audit item 6); the
            groups carry their own counts. ───────────────────── */}
        <section className="mb-12" id="destinations">
          <SectionHead
            kicker="Plan the trip"
            title={`All Destinations · ${DESTINATIONS.length} guides`}
          />

          <div className="bg-foreground/[0.02] border border-border rounded-2xl px-4 py-3 mb-7">
            <div className="flex items-center gap-2 mb-2.5">
              <span className="text-lg">🧳</span>
              <p className="text-sm font-semibold">I'm traveling as</p>
            </div>
            <div className="flex gap-2 overflow-x-auto" style={{ WebkitOverflowScrolling: "touch" }}>
              {VISA_TABS.map((tab) => (
                <button
                  key={tab}
                  onClick={() => setHolderStatus(tab)}
                  className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-semibold border transition-colors ${
                    holderStatus === tab
                      ? "bg-primary text-primary-foreground border-primary"
                      : "border-rule text-foreground/80 hover:text-primary hover:border-primary bg-card"
                  }`}
                >
                  {VISA_TAB_SHORT[tab]}
                </button>
              ))}
            </div>
          </div>

          {DESTINATION_GROUPS.map((group) => {
            const dests = DESTINATIONS.filter(group.match);
            if (!dests.length) return null;
            return (
              <div
                key={group.key}
                className="mb-8 scroll-mt-24"
                /* The trending rail's India card links here
                   (/travel#india-destinations, Kiran 2026-10-15). */
                id={group.key === "india" ? "india-destinations" : undefined}
              >
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

        {/* ── 5 · Visa Quick Reference — below the index it
            serves (redesign brief #4). Travel news moved up to
            position 3 in the redesign; it no longer sits here. ── */}
        <VisaDashboard activeTab={holderStatus} />

        {/* ── 6 · Travel Agent CTA — navy/gold like the rest of
            the page, heading at the 20px section standard (audit
            items 21 + Q2 as decided, 2026-10-15) ────────────── */}
        <section className="mb-12">
          <div className="relative p-8 bg-[#0B1D3A] rounded-2xl border border-[#D4A843]/40 text-center overflow-hidden">
            <div className="absolute top-0 right-0 w-40 h-40 bg-[#D4A843]/10 rounded-full blur-3xl" />
            <div className="relative z-10">
              <span className="text-4xl mb-3 block">🧳</span>
              <h3 className="font-serif text-xl font-bold text-white mb-2">Find a Travel Agent</h3>
              <p className="text-white/60 text-sm mb-5 max-w-lg mx-auto">
                Browse our directory of travel agencies specializing in India trips, NRI packages, and visa assistance.
              </p>
              <Link
                to="/directory?category=Travel"
                className="inline-flex items-center gap-2 bg-[#D4A843] text-[#0B1D3A] font-semibold text-sm py-2.5 px-6 rounded-full hover:bg-[#e3bb57] transition-colors"
              >
                Browse Travel Agents <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
