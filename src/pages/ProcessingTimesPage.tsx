import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  ProcessingTimeRow,
  getProcessingTimes,
  KEY_FORMS,
} from "@/lib/immigration";

/* ------------------------------------------------------------------ */
/* Form groups                                                        */
/* ------------------------------------------------------------------ */
const FORM_GROUPS = [
  {
    label: "Employment-Based",
    emoji: "💼",
    forms: ["I-140", "I-485", "I-765", "I-131", "I-129"],
  },
  {
    label: "Family-Based",
    emoji: "👨‍👩‍👧‍👦",
    forms: ["I-130", "I-539"],
  },
  {
    label: "Citizenship",
    emoji: "🇺🇸",
    forms: ["N-400"],
  },
];

/* ------------------------------------------------------------------ */
/* Processing Times Page                                              */
/* ------------------------------------------------------------------ */
export default function ProcessingTimesPage() {
  const [data, setData] = useState<ProcessingTimeRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterForm, setFilterForm] = useState<string>("all");
  const [filterOffice, setFilterOffice] = useState<string>("all");

  useEffect(() => {
    getProcessingTimes().then((d) => {
      setData(d);
      setLoading(false);
    });
  }, []);

  const offices = useMemo(() => [...new Set(data.map((r) => r.office_code))].sort(), [data]);
  const forms = useMemo(() => [...new Set(data.map((r) => r.form_number))].sort(), [data]);

  const filtered = useMemo(() => {
    let list = data;
    if (filterForm !== "all") list = list.filter((r) => r.form_number === filterForm);
    if (filterOffice !== "all") list = list.filter((r) => r.office_code === filterOffice);
    return list;
  }, [data, filterForm, filterOffice]);

  // Group for display
  const grouped = useMemo(() => {
    const map: Record<string, ProcessingTimeRow[]> = {};
    for (const row of filtered) {
      if (!map[row.form_number]) map[row.form_number] = [];
      map[row.form_number].push(row);
    }
    return map;
  }, [filtered]);

  // Fastest service center for I-140
  const fastestI140 = useMemo(() => {
    const i140s = data.filter((r) => r.form_number === "I-140" && r.processing_time_months != null);
    if (i140s.length === 0) return null;
    i140s.sort((a, b) => (a.processing_time_months ?? 99) - (b.processing_time_months ?? 99));
    return i140s[0];
  }, [data]);

  return (
    <>
      <Helmet>
        <title>USCIS Processing Times — I-140, I-485, EAD, N-400 | The Videshi</title>
        <meta name="description" content="Check current USCIS processing times for I-140, I-485, I-765 (EAD), I-131, N-400, and more by service center. Updated monthly." />
        <meta property="og:title" content="USCIS Processing Times | The Videshi" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration/processing-times" />
              <link rel="canonical" href="https://www.thevideshi.com/immigration/processing-times" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* Hero */}
        <section className="relative mb-8 -mx-4 px-4 py-10 md:py-14 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-3xl">
            <Link to="/immigration" className="text-xs text-amber-300/70 hover:text-amber-300 mb-3 inline-block">← Immigration Hub</Link>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              USCIS Processing Times
            </h1>
            <p className="text-white/60 mt-3 text-base md:text-lg">
              How long is USCIS taking to process your application? Check by form and service center.
            </p>
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* Fastest I-140 banner */}
            {fastestI140 && (
              <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl flex items-center gap-3">
                <span className="text-2xl">⚡</span>
                <div>
                  <p className="text-sm font-semibold">
                    Fastest I-140 processing: <span className="text-green-500">{fastestI140.office}</span>
                  </p>
                  <p className="text-xs text-foreground/50">
                    {fastestI140.processing_time_months} months (80% of cases)
                    {fastestI140.form_category && ` · ${fastestI140.form_category}`}
                  </p>
                </div>
              </div>
            )}

            {/* Filters */}
            <div className="flex flex-wrap gap-3 mb-6">
              <select
                value={filterForm}
                onChange={(e) => setFilterForm(e.target.value)}
                className="px-3 py-2 text-sm rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
              >
                <option value="all">All Forms</option>
                {forms.map((f) => (
                  <option key={f} value={f}>{f} — {KEY_FORMS.find((k) => k.number === f)?.name || ""}</option>
                ))}
              </select>
              <select
                value={filterOffice}
                onChange={(e) => setFilterOffice(e.target.value)}
                className="px-3 py-2 text-sm rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
              >
                <option value="all">All Service Centers</option>
                {offices.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
              {(filterForm !== "all" || filterOffice !== "all") && (
                <button
                  onClick={() => { setFilterForm("all"); setFilterOffice("all"); }}
                  className="text-sm text-primary hover:text-primary/80 font-medium"
                >
                  Clear filters
                </button>
              )}
              <span className="text-sm text-foreground/40 ml-auto self-center">
                {filtered.length} result{filtered.length !== 1 ? "s" : ""}
              </span>
            </div>

            {/* Processing times by form group */}
            {filterForm === "all" ? (
              FORM_GROUPS.map((group) => {
                const groupForms = group.forms.filter((f) => grouped[f]);
                if (groupForms.length === 0) return null;
                return (
                  <section key={group.label} className="mb-8">
                    <h2 className="font-serif text-lg font-bold mb-3 flex items-center gap-2">
                      <span>{group.emoji}</span> {group.label}
                    </h2>
                    <div className="bg-card border border-border rounded-xl overflow-hidden">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-border bg-foreground/[0.02]">
                              <th className="text-left py-2.5 px-4 text-foreground/50 font-medium">Form</th>
                              <th className="text-left py-2.5 px-4 text-foreground/50 font-medium">Category</th>
                              <th className="text-left py-2.5 px-4 text-foreground/50 font-medium">Service Center</th>
                              <th className="text-right py-2.5 px-4 text-foreground/50 font-medium">Processing Time</th>
                              <th className="text-right py-2.5 px-4 text-foreground/50 font-medium">Range</th>
                            </tr>
                          </thead>
                          <tbody>
                            {groupForms.flatMap((form) =>
                              (grouped[form] || []).map((row) => (
                                <tr key={row.id} className="border-b border-border/50 hover:bg-foreground/[0.02]">
                                  <td className="py-2.5 px-4 font-semibold">{row.form_number}</td>
                                  <td className="py-2.5 px-4 text-foreground/60">{row.form_category || row.form_name}</td>
                                  <td className="py-2.5 px-4 text-foreground/60">{row.office}</td>
                                  <td className="py-2.5 px-4 text-right font-mono font-semibold">
                                    {row.processing_time_months != null ? `${row.processing_time_months} mo` : "—"}
                                  </td>
                                  <td className="py-2.5 px-4 text-right font-mono text-foreground/50">
                                    {row.estimated_range_low != null && row.estimated_range_high != null
                                      ? `${row.estimated_range_low}–${row.estimated_range_high} mo`
                                      : "—"}
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </section>
                );
              })
            ) : (
              /* Filtered view */
              <div className="bg-card border border-border rounded-xl overflow-hidden mb-8">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border bg-foreground/[0.02]">
                        <th className="text-left py-2.5 px-4 text-foreground/50 font-medium">Form</th>
                        <th className="text-left py-2.5 px-4 text-foreground/50 font-medium">Category</th>
                        <th className="text-left py-2.5 px-4 text-foreground/50 font-medium">Service Center</th>
                        <th className="text-right py-2.5 px-4 text-foreground/50 font-medium">Processing Time</th>
                        <th className="text-right py-2.5 px-4 text-foreground/50 font-medium">Range</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map((row) => (
                        <tr key={row.id} className="border-b border-border/50 hover:bg-foreground/[0.02]">
                          <td className="py-2.5 px-4 font-semibold">{row.form_number}</td>
                          <td className="py-2.5 px-4 text-foreground/60">{row.form_category || row.form_name}</td>
                          <td className="py-2.5 px-4 text-foreground/60">{row.office}</td>
                          <td className="py-2.5 px-4 text-right font-mono font-semibold">
                            {row.processing_time_months != null ? `${row.processing_time_months} mo` : "—"}
                          </td>
                          <td className="py-2.5 px-4 text-right font-mono text-foreground/50">
                            {row.estimated_range_low != null && row.estimated_range_high != null
                              ? `${row.estimated_range_low}–${row.estimated_range_high} mo`
                              : "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Disclaimer */}
            <div className="text-xs text-foreground/40 mt-4">
              <p>Processing times are based on USCIS data showing 80% of cases completed within the listed timeframe. Actual times may vary. Premium processing (15 business days) is available for some forms.</p>
            </div>
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
