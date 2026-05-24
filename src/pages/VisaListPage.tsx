import { useState, useMemo } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { ChevronLeft } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { VISA_HOLDER_LABELS, type VisaHolderStatus } from "@/lib/travel";
import {
  getVisaList,
  getVisaCategoriesForStatus,
  type VisaCountryEntry,
} from "@/lib/visa-country-lists";

/* ── Status tab labels ─────────────────────────────────────────────── */
const STATUS_TABS: { key: VisaHolderStatus; short: string }[] = [
  { key: "indian-passport", short: "Indian Passport" },
  { key: "us-citizen", short: "US Citizen" },
  { key: "green-card", short: "Green Card" },
];

/* ── Category display order per status ─────────────────────────────── */
const CATEGORY_ORDER: Record<string, { key: string; label: string }[]> = {
  "indian-passport": [
    { key: "visa-free", label: "Visa-Free" },
    { key: "voa", label: "Visa on Arrival" },
    { key: "e-visa", label: "e-Visa" },
    { key: "us-gc-perks", label: "US GC Perks" },
  ],
  "us-citizen": [
    { key: "visa-free", label: "Visa-Free" },
    { key: "voa", label: "Visa on Arrival" },
    { key: "e-visa", label: "e-Visa / ETA" },
    { key: "visa-required", label: "Visa Required" },
  ],
  "green-card": [
    { key: "visa-free-gc", label: "Visa-Free" },
    { key: "voa-gc", label: "VOA" },
    { key: "e-visa-gc", label: "e-Visa" },
    { key: "visa-required-gc", label: "Still Need Visa" },
  ],
};

/* map category keys between statuses by ordinal position */
function mapCategoryToStatus(fromStatus: string, fromCat: string, toStatus: string): string {
  const fromOrder = CATEGORY_ORDER[fromStatus] || [];
  const toOrder = CATEGORY_ORDER[toStatus] || [];
  const idx = fromOrder.findIndex((c) => c.key === fromCat);
  if (idx >= 0 && toOrder[idx]) return toOrder[idx].key;
  return toOrder[0]?.key || fromCat;
}

/* ================================================================== */
/* Country Row                                                        */
/* ================================================================== */
function CountryRow({ entry, idx }: { entry: VisaCountryEntry; idx: number }) {
  return (
    <div
      className={`flex items-start gap-3 px-4 py-3 ${
        idx % 2 === 0 ? "bg-card" : "bg-foreground/[0.02]"
      }`}
    >
      <span className="text-xl flex-shrink-0 leading-none mt-0.5">{entry.flag || "🏳️"}</span>
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-sm">{entry.country}</h3>
        {entry.notes && (
          <p className="text-xs text-foreground/50 mt-0.5 leading-relaxed">{entry.notes}</p>
        )}
      </div>
    </div>
  );
}

/* ================================================================== */
/* Main Page                                                          */
/* ================================================================== */
export default function VisaListPage() {
  const { status = "indian-passport", category = "visa-free" } = useParams();
  const navigate = useNavigate();

  const data = useMemo(() => getVisaList(status, category), [status, category]);
  const categories = CATEGORY_ORDER[status] || [];

  const [search, setSearch] = useState("");

  if (!data) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 py-20 text-center">
          <h1 className="font-serif text-2xl mb-4">Not Found</h1>
          <p className="text-foreground/50 mb-6">This visa list doesn't exist.</p>
          <Link to="/travel" className="text-primary font-semibold text-sm">
            ← Back to Travel
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const filtered = search.trim()
    ? data.countries.filter(
        (c) =>
          c.country.toLowerCase().includes(search.toLowerCase()) ||
          (c.notes || "").toLowerCase().includes(search.toLowerCase())
      )
    : data.countries;

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{data.meta.title} {data.meta.subtitle} — The Videshi Travel</title>
        <meta
          name="description"
          content={`Full list of ${data.meta.count}+ ${data.meta.title.toLowerCase()} ${data.meta.subtitle.toLowerCase()}. Updated visa requirements and travel tips for NRIs.`}
        />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-6 pb-12">
        {/* Breadcrumb */}
        <Link
          to="/travel"
          className="inline-flex items-center gap-1 text-xs text-foreground/50 hover:text-primary mb-4"
        >
          <ChevronLeft className="h-3 w-3" /> Back to Travel
        </Link>

        {/* Title */}
        <div className="flex items-center gap-3 mb-1">
          <span className="text-2xl">{data.meta.emoji}</span>
          <h1 className="font-serif text-2xl md:text-3xl font-bold">{data.meta.title}</h1>
        </div>
        <p className="text-foreground/50 text-sm mb-5 ml-10">
          {data.meta.subtitle} — <span className={`font-bold ${data.meta.textColor}`}>{data.countries.length}</span> countries listed
        </p>

        {/* Status tabs */}
        <div className="flex gap-2 mb-3 overflow-x-auto" style={{ WebkitOverflowScrolling: "touch" }}>
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => {
                const newCat = mapCategoryToStatus(status, category, tab.key);
                navigate(`/travel/visa-list/${tab.key}/${newCat}`, { replace: true });
              }}
              className={`whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${
                status === tab.key
                  ? "bg-primary text-primary-foreground border-primary"
                  : "border-rule text-foreground/70 hover:text-primary hover:border-primary"
              }`}
            >
              {tab.short}
            </button>
          ))}
        </div>

        {/* Category pills */}
        <div className="flex gap-2 mb-5 overflow-x-auto" style={{ WebkitOverflowScrolling: "touch" }}>
          {categories.map((cat) => (
            <Link
              key={cat.key}
              to={`/travel/visa-list/${status}/${cat.key}`}
              className={`whitespace-nowrap px-3 py-1 rounded-full text-[11px] font-semibold border transition-colors ${
                category === cat.key
                  ? `${data.meta.color} ${data.meta.textColor} border-current`
                  : "border-rule text-foreground/50 hover:text-foreground/80"
              }`}
            >
              {cat.label}
            </Link>
          ))}
        </div>

        {/* Search */}
        <div className="mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search countries…"
            className="w-full max-w-md px-3 py-2 rounded-lg border border-rule bg-card text-sm focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* Country list */}
        <div className="border border-border rounded-xl overflow-hidden">
          <div className={`px-4 py-2.5 border-b border-border ${data.meta.color}`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-foreground/60">
                {filtered.length} {filtered.length === 1 ? "country" : "countries"}
                {search.trim() ? ` matching "${search}"` : ""}
              </span>
              <span className="text-[10px] text-foreground/40">
                Last updated: May 2026
              </span>
            </div>
          </div>
          {filtered.length === 0 ? (
            <div className="px-4 py-12 text-center text-foreground/40 text-sm">
              No countries matching "{search}"
            </div>
          ) : (
            filtered.map((entry, i) => (
              <CountryRow key={entry.country} entry={entry} idx={i} />
            ))
          )}
        </div>

        {/* Disclaimer */}
        <p className="text-[10px] text-foreground/30 mt-4 leading-relaxed max-w-2xl">
          ⚠️ Visa requirements change frequently. Always verify with the destination country's
          embassy or consulate before travel. This information is for general reference only and
          may not reflect the latest policy changes. Last comprehensive review: May 2026.
        </p>
      </main>

      <SiteFooter />
    </div>
  );
}
