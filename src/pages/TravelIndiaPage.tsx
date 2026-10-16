import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import FlightDeals from "@/components/FlightDeals";
import SectionHead from "@/components/TravelSectionHead";
import TravelerToggle from "@/components/TravelerToggle";
import {
  DESTINATIONS,
  visaBadgeColor,
  visaBadgeLabel,
  visaNoteAddsInfo,
} from "@/lib/travel";
import type { Destination, VisaHolderStatus } from "@/lib/travel";
import { loadGalleries } from "@/lib/trendingDestinations";
import type { GalleryData } from "@/lib/trendingDestinations";

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
/*                                                                    */
/* Styling: Variant B — "Editorial cover" (Kiran picked B from the    */
/* mockups, 2026-10-15 20:58; design note                            */
/* research/india-page-design-2026-10-15.md): an oversized serif      */
/* cover block with a restrained tricolor rule, a labelled six-state */
/* photo mosaic, the fares hub as a clean white tool card, and       */
/* larger editorial state rows. Content, order and functionality     */
/* are unchanged from the page that shipped at 20:31.                 */
/* ------------------------------------------------------------------ */

/* Row/mosaic photo resolution — the mockup's rule: the state's
   gallery photo where a gallery exists (Goa, Kerala, Rajasthan),
   the state's published destination image (dest.image) otherwise.
   Galleries load async from the same /data file the destination
   pages read; until one lands, the destination image stands in —
   EXCEPT the Munnar tile, whose subject is specifically Kerala's
   second gallery photo (tea plantations): it waits for the gallery
   rather than sit its label over Kerala's backwater image. */
function galleryPhoto(
  galleries: GalleryData | null,
  key: string,
  idx: number,
): string | undefined {
  return galleries?.[key]?.photos?.[idx]?.src;
}

function rowPhoto(dest: Destination, galleries: GalleryData | null): string {
  return galleryPhoto(galleries, dest.key, 0) ?? dest.image;
}

/* The facts block inside each editorial row — rendered from the
   same lib/travel helpers DestinationCard uses (badge colour/label,
   the audit's note-adds-info rule, best months, budget), so the
   rows can never drift from the index cards factually. */
function RowFacts({
  dest,
  holderStatus,
}: {
  dest: Destination;
  holderStatus: VisaHolderStatus;
}) {
  const visaInfo = dest.visa[holderStatus];
  return (
    <>
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
      </div>
    </>
  );
}

/* Editorial state row (Variant B): photo left, serif name and facts
   right — one per line, every state visual. Photo is lazy: the rows
   sit below the fold, under the mosaic and the fares hub. */
function EditorialRow({
  dest,
  holderStatus,
  galleries,
}: {
  dest: Destination;
  holderStatus: VisaHolderStatus;
  galleries: GalleryData | null;
}) {
  return (
    <Link to={`/travel/${dest.key}`} className="block group">
      <div
        className="bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 flex"
        style={{ height: 138 }}
      >
        <div className="flex-shrink-0 overflow-hidden" style={{ width: 118 }}>
          <img
            src={rowPhoto(dest, galleries)}
            alt={dest.label}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
            decoding="async"
          />
        </div>
        <div className="p-4 flex flex-col gap-1.5 flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3
              className="font-serif text-lg font-bold group-hover:text-primary transition-colors leading-tight"
              style={{ color: "#0B1D3A" }}
            >
              {dest.label}
            </h3>
            <ChevronRight className="h-4 w-4 text-foreground/20 group-hover:text-primary transition-colors flex-shrink-0 mt-1" />
          </div>
          <p className="text-xs text-foreground/55 leading-snug">{dest.description}</p>
          <RowFacts dest={dest} holderStatus={holderStatus} />
        </div>
      </div>
    </Link>
  );
}

/* One labelled mosaic tile. The label renders only with its photo —
   a caption must never sit over the wrong image. */
function MosaicTile({
  src,
  label,
  span,
}: {
  src?: string;
  label: string;
  span?: boolean;
}) {
  return (
    <div className={`relative overflow-hidden rounded-md bg-stone-100 ${span ? "col-span-2" : ""}`}>
      {src && (
        <>
          <img
            src={src}
            alt={label}
            className="w-full h-full object-cover block"
            loading="eager"
            decoding="async"
          />
          <span
            className="absolute bottom-1 left-1.5 text-[9px] font-bold uppercase tracking-wider text-white"
            style={{ textShadow: "0 1px 3px rgba(0,0,0,0.8)" }}
          >
            {label}
          </span>
        </>
      )}
    </div>
  );
}

export default function TravelIndiaPage() {
  const [holderStatus, setHolderStatus] = useState<VisaHolderStatus>("indian-passport");
  const [galleries, setGalleries] = useState<GalleryData | null>(null);
  const [fxRate, setFxRate] = useState<number | null>(null);
  const indiaDests = DESTINATIONS.filter((d) => d.region === "india");
  const indiaByKey = (key: string) => indiaDests.find((d) => d.key === key)!;

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

  /* Galleries + the USD/INR rate — the same public data files the
     destination pages and the Hub already read. Both fill their
     slots when they land; tile and row dimensions are fixed, so
     nothing shifts. The rate is never hardcoded: the cover's fact
     line gains its "$1 = ₹…" segment only once the live rate is in. */
  useEffect(() => {
    let alive = true;
    loadGalleries().then((g) => {
      if (alive) setGalleries(g);
    });
    fetch("/data/usdinr.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (alive && d && typeof d.rate === "number") setFxRate(d.rate);
      })
      .catch(() => {});
    return () => {
      alive = false;
    };
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
        {/* ── Cover block (Variant B) — gold kicker, oversized
            serif headline, standfirst, small-caps fact line, and
            the restrained tricolor rule (saffron / gold / green,
            3px — a design accent, no flag imagery). ─────────── */}
        <header className="mb-5">
          <p className="text-[11px] font-bold uppercase tracking-[2px] text-[#7a5c14] dark:text-[#D4A843] mb-2">
            Travel · The Trip Home
          </p>
          <h1
            className="font-serif font-black tracking-tight m-0"
            style={{ fontSize: 64, lineHeight: 0.95, color: "#0B1D3A" }}
          >
            India
          </h1>
          <p className="text-foreground/65 leading-relaxed mt-3" style={{ fontSize: 15, maxWidth: "34ch" }}>
            Flights from the US to five Indian metros, checked weekly — and the nine
            state guides for the trip home.
          </p>
          <p className="text-[11px] font-semibold uppercase tracking-wider text-foreground/45 mt-3">
            Best Jan–Mar · Oct–Dec&ensp;·&ensp;5 gateways&ensp;·&ensp;9 guides
            {fxRate !== null && <>&ensp;·&ensp;$1 = ₹{fxRate.toFixed(2)}</>}
          </p>
          <div className="flex mt-4 rounded-full overflow-hidden" aria-hidden="true">
            <span className="flex-1" style={{ height: 3, backgroundColor: "#E8862E" }} />
            <span className="flex-1" style={{ height: 3, backgroundColor: "#D4A843" }} />
            <span className="flex-1" style={{ height: 3, backgroundColor: "#2E7D4F" }} />
          </div>
        </header>

        {/* ── Photo mosaic — six states at a glance, labelled.
            Gallery photos where a state has a gallery, published
            destination images otherwise (the mockup's mix). ── */}
        <div className="grid grid-cols-4 gap-1.5 mb-10" style={{ gridAutoRows: 104 }}>
          <MosaicTile src={galleryPhoto(galleries, "rajasthan", 0) ?? indiaByKey("rajasthan").image} label="Rajasthan" span />
          <MosaicTile src={galleryPhoto(galleries, "kerala", 0) ?? indiaByKey("kerala").image} label="Kerala" />
          <MosaicTile src={galleryPhoto(galleries, "goa", 1) ?? indiaByKey("goa").image} label="Goa" />
          <MosaicTile src={indiaByKey("kashmir").image} label="Kashmir" />
          <MosaicTile src={galleryPhoto(galleries, "kerala", 1)} label="Munnar" />
          <MosaicTile src={indiaByKey("karnataka").image} label="Karnataka" span />
        </div>

        {/* ── 1 · Flights to India — the full fares hub (origin
            dropdown defaulted from the reader's location and the
            shared origin preference, selectable metros rail,
            calendars, booking links, pricing promise), presented
            as a clean white tool card (Variant B). The white-card
            styling lives ONLY in this wrapper: FlightDeals itself
            is unchanged, so its other surfaces keep their current
            presentation. ─────────────────────────────────────── */}
        <div className="bg-card border border-border rounded-[24px] shadow-sm px-4 py-5 sm:px-6 mb-12">
          <FlightDeals />
        </div>

        {/* ── 2 · Destinations in India — the shared passport
            toggle driving editorial state rows (photo + facts);
            badges flip with the toggle exactly as the index
            cards' did, and each row opens its state page. ───── */}
        <section className="mb-12">
          <SectionHead
            kicker="Plan the trip"
            title={`India Destinations · ${indiaDests.length} guides`}
          />

          <TravelerToggle holderStatus={holderStatus} onChange={setHolderStatus} />

          <div className="flex flex-col gap-3">
            {indiaDests.map((d) => (
              <EditorialRow key={d.key} dest={d} holderStatus={holderStatus} galleries={galleries} />
            ))}
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
