import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import TrendingDestinations from "@/components/TrendingDestinations";
import SectionHead from "@/components/TravelSectionHead";
import DestinationCard from "@/components/DestinationCard";
import TravelerToggle from "@/components/TravelerToggle";
import {
  DESTINATIONS,
  VISA_DASHBOARD_BY_STATUS,
  getTravelNews,
} from "@/lib/travel";
import type { Destination, VisaHolderStatus } from "@/lib/travel";

/* ------------------------------------------------------------------ */
/* Travel News List                                                   */
/* ------------------------------------------------------------------ */
/* VERTICAL stacked list (Kiran, 2026-10-15 20:42: "Let's make news
   articles vertical instead") — full-width cards stacked top to
   bottom, same card idiom and fields as the old horizontal rail
   (image, date, headline, excerpt, /articles/<slug> links), all
   articles received. No horizontal scroll, no scroll-snap. */
function TravelNewsStrip({ news }: { news: any[] }) {
  if (!news.length) return null;
  return (
    <section className="mb-12">
      <SectionHead kicker="Stay current" title="Latest Travel News" />
      <div className="flex flex-col gap-4">
        {news.map((article: any) => (
          <Link
            key={article.id}
            to={`/articles/${article.slug}`}
            className="block group"
          >
            <article className="bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg">
              {article.image_url && (
                <div className="aspect-[16/9] overflow-hidden">
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

/* Destination cards render via the shared DestinationCard component
   (src/components/DestinationCard.tsx) — TravelIndiaPage renders the
   same cards for the India group, so the two can never drift apart. */

/* ------------------------------------------------------------------ */
/* Main TravelPage                                                    */
/* ------------------------------------------------------------------ */
/* Index groups (Kiran, 2026-10-15 20:42): the India state
   destinations LEFT this index — they live on India's own page,
   /travel/india (metro fares hub + the 9 state cards + their own
   passport toggle) — so /travel's All Destinations index is USA &
   Canada + International only. The international match still
   excludes region "india" so the states can never leak back in
   here via the catch-all. */
const DESTINATION_GROUPS: { key: string; heading: string; blurb: string; match: (d: Destination) => boolean }[] = [
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

/* The ENTIRE travel section as one block — /travel renders it
   between its Masthead and footer, and the homepage renders the
   SAME block in place when the Travel tab is picked (Kiran,
   2026-10-16: "include the entire travel section stuff here when
   user clicks travel option"). One implementation, two homes —
   never fork the sections. */
export function TravelPageContent() {
  const [holderStatus, setHolderStatus] = useState<VisaHolderStatus>("indian-passport");
  const [news, setNews] = useState<any[]>([]);

  /* The heading count is what the index actually renders (the sum
     over the groups below), never DESTINATIONS.length — the full
     record list still contains the 9 India states, which render
     on /travel/india instead (Kiran, 2026-10-15 20:42). */
  const indexGuideCount = DESTINATION_GROUPS.reduce(
    (n, g) => n + DESTINATIONS.filter(g.match).length,
    0,
  );

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

  /* Hash deep-links (e.g. /travel#travel-news): react-router does
     not scroll to a hash on navigation, so do it here once the
     page has mounted. Two attempts — sections above the index load
     async and can shift the target's position after the first
     scroll. (The fares hub's #flight-deals anchor lives on the
     India page, /travel/india, since 2026-10-15.) */
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

        {/* ── Cheapest Fares hub MOVED to /travel/india
            2026-10-15 (Kiran, 20:20–20:21: "India is just
            another destination" / "India should get its own
            page"). India was the only fares market on this
            page, so as a standalone position-2 section it
            special-cased one destination. The full hub
            (FlightDeals) now lives on the India page, above
            its state destinations; every other destination's
            fares stay on its own page (Phase 2). ──────────── */}

        {/* ── 2 · Travel articles — moved up from the bottom of
            the old page (redesign brief #3); position 2 since
            the fares hub left for the India page. Still
            un-gated: the strip fills this slot when its data
            lands. ─────────────────────────────────────────── */}
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

        {/* ── 3 · All Destinations index — the passport toggle is
            this section's CONTROL BAR (redesign brief #4): a
            light bordered strip directly under the section
            header, directly above the guide cards whose visa
            badges it drives. The count lives in the heading
            (audit item 6) and counts only what renders here —
            the 9 India states moved to /travel/india (Kiran,
            2026-10-15 20:42); the groups carry their own
            counts. The toggle renders via the shared
            TravelerToggle component — the India page carries
            the same control over its state cards. ──────────── */}
        <section className="mb-12" id="destinations">
          <SectionHead
            kicker="Plan the trip"
            title={`All Destinations · ${indexGuideCount} guides`}
          />

          <TravelerToggle holderStatus={holderStatus} onChange={setHolderStatus} />

          {DESTINATION_GROUPS.map((group) => {
            const dests = DESTINATIONS.filter(group.match);
            if (!dests.length) return null;
            return (
              <div key={group.key} className="mb-8 scroll-mt-24">
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

        {/* ── 4 · Visa Quick Reference — below the index it
            serves (redesign brief #4). Travel news sits at
            position 2; it no longer lives down here. ──────── */}
        <VisaDashboard activeTab={holderStatus} />

        {/* ── 5 · Travel Agent CTA — navy/gold like the rest of
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
  );
}

export default function TravelPage() {
  const indexGuideCount = DESTINATION_GROUPS.reduce(
    (n, g) => n + DESTINATIONS.filter(g.match).length,
    0,
  );
  return (
    <>
      <Helmet>
        <title>{`Travel Hub — Top Destinations, ${indexGuideCount} Guides & Visa Guide | The Videshi`}</title>
        <meta name="description" content={`Plan the trip home and the next getaway: top destinations, ${indexGuideCount} diaspora travel guides with visa notes for your passport status, and the latest travel news for Indian passport holders, US citizens, and Green Card holders.`} />
        <meta property="og:title" content="Travel Hub — The Videshi" />
        <meta property="og:description" content="Destinations, visa quick-reference, and travel news for NRIs and the Indian diaspora." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/travel" />
        <link rel="canonical" href="https://www.thevideshi.com/travel" />
      </Helmet>
      <Masthead />
      <CategoryPills />
      <TravelPageContent />
      <SiteFooter />
    </>
  );
}
