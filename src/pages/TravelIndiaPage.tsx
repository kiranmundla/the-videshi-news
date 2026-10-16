import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import FlightDeals from "@/components/FlightDeals";
import SectionHead from "@/components/TravelSectionHead";
import DestinationCard from "@/components/DestinationCard";
import TravelerToggle from "@/components/TravelerToggle";
import { DESTINATIONS } from "@/lib/travel";
import type { VisaHolderStatus } from "@/lib/travel";

/* ------------------------------------------------------------------ */
/* /travel/india — India's destination page (Kiran, 2026-10-15        */
/* 20:21: "India should get its own page", completing 20:20's         */
/* "India is just another destination"). Every destination has its    */
/* own page; India's carries the experience Kiran described at        */
/* 19:49: flights to the Indian metros first (selectable, from the   */
/* reader's origin), and the destinations in India directly below —   */
/* each opening its own state page. NO guide file and NO index        */
/* record: the 49-guide index on /travel is unchanged, and India      */
/* stays out of the trending rankings.                                */
/* ------------------------------------------------------------------ */
export default function TravelIndiaPage() {
  const [holderStatus, setHolderStatus] = useState<VisaHolderStatus>("indian-passport");
  const indiaDests = DESTINATIONS.filter((d) => d.region === "india");

  /* Hash deep-links (e.g. /travel/india#flight-deals from the Hub
     metro rail and destination pages' "See all fares" links):
     react-router does not scroll to a hash on navigation, so do it
     here once the page has mounted. Two attempts — the fares hub
     loads async and its section only exists once data lands. */
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
        <title>India Travel — Cheapest US–India Fares & State Guides | The Videshi</title>
        <meta name="description" content="The trip home, on one page: real round-trip fare snapshots from US metros to Delhi, Mumbai, Bengaluru, Hyderabad and Kolkata, plus 9 India state guides — Goa, Kerala, Karnataka, Rajasthan and more — with visa notes for your passport status." />
        <meta property="og:title" content="India Travel — The Videshi" />
        <meta property="og:description" content="Cheapest flights from the US to India's metros, and the state guides for the trip home." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/travel/india" />
        <link rel="canonical" href="https://www.thevideshi.com/travel/india" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-6">
        {/* ── Header — minimal, same pattern as /travel: pill +
            serif title + one line, then the page's content. ── */}
        <header className="mb-6">
          <span className="inline-block text-[11px] font-bold uppercase tracking-[2px] px-2.5 py-1 rounded-full bg-[#D4A843]/20 text-[#7a5c14] dark:text-[#D4A843]">
            ✈️ Travel Hub
          </span>
          <h1 className="font-serif text-[26px] md:text-3xl font-bold tracking-tight leading-tight mt-2.5" style={{ color: "#0B1D3A" }}>
            India
          </h1>
          <p className="text-sm text-foreground/55 leading-relaxed mt-1.5">
            The trip home: cheapest flights from the US to India's metros — then the state guides.
          </p>
        </header>

        {/* ── 1 · Flights to India — the full fares hub in the
            cream panel treatment it carried on /travel (origin
            dropdown defaulted from the reader's location and
            the shared origin preference, selectable metros
            rail, calendars, booking links, pricing promise).
            FlightDeals is reused unchanged; it renders its own
            "Fly for less / Cheapest Fares" header inside the
            panel and owns no bottom margin — the panel does. ── */}
        <div className="rounded-[24px] border border-[#D4A843]/30 bg-[#FBF6EA] px-4 py-5 sm:px-6 mb-12">
          <FlightDeals />
        </div>

        {/* ── 2 · Destinations in India — the same passport
            toggle + card grid the India group carries on
            /travel (shared TravelerToggle + DestinationCard),
            so badges, best months and budgets render
            identically; each card opens its state page. ────── */}
        <section className="mb-12">
          <SectionHead
            kicker="Plan the trip"
            title={`India Destinations · ${indiaDests.length} guides`}
          />

          <TravelerToggle holderStatus={holderStatus} onChange={setHolderStatus} />

          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
            {indiaDests.map((d) => (
              <DestinationCard key={d.key} dest={d} holderStatus={holderStatus} />
            ))}
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
