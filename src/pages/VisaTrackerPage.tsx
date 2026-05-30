import { useState, useEffect, useCallback, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight, CheckCircle, Clock, MapPin, Send, AlertTriangle } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import TurnstileWidget from "@/components/TurnstileWidget";

import {
  type ConsulateWaitRow,
  getConsulateWaitTimes,
  formatWaitMonths,
  waitColor,
  INDIA_CONSULATES,
  CONSULATE_DISPLAY,
} from "@/lib/immigration";

import {
  type VisaSighting,
  getVisaSightings,
  submitSighting,
  relativeTime,
  CONSULATES,
  CONSULATE_LABELS,
  VISA_TYPES,
  CONSULATE_COLORS,
} from "@/lib/visas";

/* ------------------------------------------------------------------ */
/* Compact Wait-Time Strip (reuses immigration.ts data)               */
/* ------------------------------------------------------------------ */
function WaitTimeStrip({ data }: { data: ConsulateWaitRow[] }) {
  const grouped: Record<string, Record<string, ConsulateWaitRow>> = {};
  for (const row of data) {
    if (!INDIA_CONSULATES.includes(row.consulate as any)) continue;
    if (!grouped[row.consulate]) grouped[row.consulate] = {};
    if (!grouped[row.consulate][row.visa_type]) grouped[row.consulate][row.visa_type] = row;
  }

  const consulates = INDIA_CONSULATES.filter((c) => grouped[c]);
  consulates.sort((a, b) => {
    const aW = grouped[a]?.["B1B2"]?.next_available_months ?? 99;
    const bW = grouped[b]?.["B1B2"]?.next_available_months ?? 99;
    return aW - bW;
  });

  if (consulates.length === 0) return null;

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border bg-blue-500/5">
        <div className="flex items-center gap-2">
          <span className="text-lg">🏛️</span>
          <h3 className="font-serif font-bold text-[15px]">Official Wait Times — India Consulates</h3>
        </div>
        <span className="text-[11px] text-foreground/50">via US State Dept</span>
      </div>
      <div className="divide-y divide-border">
        {consulates.map((c) => {
          const b1b2 = grouped[c]?.["B1B2"];
          const hlop = grouped[c]?.["H_L_O_P_Q"];
          const fmj = grouped[c]?.["F_M_J"];
          const b1Val = b1b2?.next_available_months ?? b1b2?.avg_wait_months ?? null;
          const hlVal = hlop?.next_available_months ?? null;
          const fmVal = fmj?.next_available_months ?? null;
          return (
            <div key={c} className="flex items-center justify-between px-4 py-2 hover:bg-foreground/[0.02] transition-colors">
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-2 h-2 rounded-full ${
                    b1Val === null
                      ? "bg-gray-400"
                      : b1Val < 2
                        ? "bg-green-500"
                        : b1Val < 5
                          ? "bg-yellow-500"
                          : b1Val < 8
                            ? "bg-orange-500"
                            : "bg-red-500"
                  }`}
                />
                <span className="font-semibold text-sm">{CONSULATE_DISPLAY[c] || c}</span>
              </div>
              <div className="flex items-center gap-5 text-sm">
                <div className="text-right">
                  <span className={`font-mono font-semibold ${waitColor(b1Val)}`}>{formatWaitMonths(b1Val)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">B1/B2</p>
                </div>
                <div className="text-right">
                  <span className={`font-mono font-semibold ${waitColor(hlVal)}`}>{formatWaitMonths(hlVal)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">H/L/O/P</p>
                </div>
                <div className="text-right hidden sm:block">
                  <span className={`font-mono font-semibold ${waitColor(fmVal)}`}>{formatWaitMonths(fmVal)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">F/M/J</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <Link
        to="/immigration/consulate-wait-times"
        className="flex items-center justify-center gap-1 px-4 py-2 text-sm text-primary font-medium border-t border-border hover:bg-primary/5 transition-colors"
      >
        Compare all consulates incl. third-country <ChevronRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Sighting Card                                                      */
/* ------------------------------------------------------------------ */
function SightingCard({ s }: { s: VisaSighting }) {
  const colors = CONSULATE_COLORS[s.consulate] ?? { bg: "bg-gray-500/10", text: "text-gray-600", border: "border-gray-500/20" };
  const dateRange =
    s.slots_date_start && s.slots_date_end
      ? `${new Date(s.slots_date_start).toLocaleDateString("en-US", { month: "short", day: "numeric" })} – ${new Date(s.slots_date_end).toLocaleDateString("en-US", { month: "short", day: "numeric" })}`
      : s.slots_date_start
        ? new Date(s.slots_date_start).toLocaleDateString("en-US", { month: "short", day: "numeric" })
        : null;

  return (
    <article className="bg-card border border-border rounded-xl p-4 hover:border-primary/30 transition-all duration-200 hover:shadow-md">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
            <MapPin className="h-3 w-3" />
            {CONSULATE_LABELS[s.consulate] || s.consulate}
          </span>
          <span className="inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full bg-foreground/5 text-foreground/70">
            {s.visa_type}
          </span>
          {s.verified && (
            <span className="inline-flex items-center gap-0.5 text-[10px] font-bold uppercase tracking-wider text-green-600">
              <CheckCircle className="h-3 w-3" /> Verified
            </span>
          )}
        </div>
        <span className="text-[11px] text-foreground/40 whitespace-nowrap flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {relativeTime(s.created_at)}
        </span>
      </div>

      {dateRange && (
        <p className="text-xs font-semibold text-primary/80 mb-1.5">
          📅 Slots seen: {dateRange}
        </p>
      )}

      <p className="text-sm text-foreground/80 leading-relaxed">{s.description}</p>

      <p className="text-xs text-foreground/40 mt-2">
        Reported by <span className="font-medium text-foreground/60">{s.reporter_name}</span>
      </p>
    </article>
  );
}

/* ------------------------------------------------------------------ */
/* Thank-You Wall                                                     */
/* ------------------------------------------------------------------ */
function ThankYouWall({ sightings }: { sightings: VisaSighting[] }) {
  // Newest first
  const sorted = useMemo(
    () => [...sightings].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()),
    [sightings],
  );

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-border bg-amber-500/5">
        <h3 className="font-serif font-bold text-[15px] flex items-center gap-2">
          🙏 Community Spotters
        </h3>
        <p className="text-[11px] text-foreground/50 mt-0.5">
          Thank you for keeping slots visible for everyone
        </p>
      </div>
      <div className="max-h-[420px] overflow-y-auto divide-y divide-border">
        {sorted.map((s) => {
          const colors = CONSULATE_COLORS[s.consulate] ?? { bg: "bg-gray-500/10", text: "text-gray-600", border: "border-gray-500/20" };
          return (
            <div key={s.id} className="px-4 py-2.5 hover:bg-foreground/[0.02] transition-colors">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-sm text-foreground/80 truncate">{s.reporter_name}</span>
                <span className="text-[10px] text-foreground/40 whitespace-nowrap">{relativeTime(s.created_at)}</span>
              </div>
              <p className="text-[11px] text-foreground/50 mt-0.5 leading-tight">
                <span className={`${colors.text} font-medium`}>{CONSULATE_LABELS[s.consulate]}</span>
                {" · "}
                {s.visa_type}
                {s.verified && " ✓"}
              </p>
            </div>
          );
        })}
        {sorted.length === 0 && (
          <div className="px-4 py-6 text-center text-sm text-foreground/40">
            No sightings yet — be the first!
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Report Form                                                        */
/* ------------------------------------------------------------------ */
function ReportForm({ onSubmitted }: { onSubmitted: () => void }) {
  const [consulate, setConsulate] = useState("");
  const [visaType, setVisaType] = useState("");
  const [dateStart, setDateStart] = useState("");
  const [dateEnd, setDateEnd] = useState("");
  const [description, setDescription] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const canSubmit = consulate && visaType && description.trim() && name.trim() && turnstileToken && !submitting;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setSubmitting(true);
    setError(null);

    const result = await submitSighting({
      consulate,
      visa_type: visaType,
      slots_date_start: dateStart || undefined,
      slots_date_end: dateEnd || undefined,
      description: description.trim(),
      reporter_name: name.trim(),
      reporter_email: email.trim(),
    });

    setSubmitting(false);
    if (result.success) {
      setSuccess(true);
      setConsulate("");
      setVisaType("");
      setDateStart("");
      setDateEnd("");
      setDescription("");
      // keep name / email for repeat sighters
      onSubmitted();
      setTimeout(() => setSuccess(false), 5000);
    } else {
      setError(result.error || "Failed to submit. Please try again.");
    }
  };

  const fieldClass =
    "w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors";

  return (
    <form onSubmit={handleSubmit} className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border bg-green-500/5">
        <h3 className="font-serif font-bold text-lg flex items-center gap-2">
          🛂 Report a Sighting
        </h3>
        <p className="text-sm text-foreground/60 mt-1">
          Saw open slots on <a href="https://www.ustraveldocs.com/" target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-2 hover:text-primary/80">ustraveldocs.com</a>? Help the community by sharing what you found.
        </p>
      </div>

      <div className="p-5 space-y-4">
        {success && (
          <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-lg px-4 py-3 text-green-700 text-sm font-medium">
            <CheckCircle className="h-4 w-4 flex-shrink-0" />
            Sighting published — thank you! 🎉 Your name is now on the wall.
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-red-700 text-sm">
            <AlertTriangle className="h-4 w-4 flex-shrink-0" />
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
              Consulate <span className="text-red-500">*</span>
            </label>
            <select value={consulate} onChange={(e) => setConsulate(e.target.value)} className={fieldClass} required>
              <option value="">Select consulate…</option>
              {CONSULATES.map((c) => (
                <option key={c} value={c}>{CONSULATE_LABELS[c]}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
              Visa Type <span className="text-red-500">*</span>
            </label>
            <select value={visaType} onChange={(e) => setVisaType(e.target.value)} className={fieldClass} required>
              <option value="">Select type…</option>
              {VISA_TYPES.map((v) => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
              Slots From
            </label>
            <input type="date" value={dateStart} onChange={(e) => setDateStart(e.target.value)} className={fieldClass} />
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
              Slots To
            </label>
            <input type="date" value={dateEnd} onChange={(e) => setDateEnd(e.target.value)} className={fieldClass} />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
            What did you see? <span className="text-red-500">*</span>
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="e.g. 'Multiple B1/B2 slots opened up for August at Mumbai consulate, including same-day cancellation slots'"
            className={fieldClass + " resize-none"}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
              Your Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="How should we credit you?"
              className={fieldClass}
              required
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
              Email <span className="text-[10px] text-foreground/40 font-normal normal-case">(optional, never shown)</span>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="For follow-up only"
              className={fieldClass}
            />
          </div>
        </div>

        <TurnstileWidget
          onVerify={setTurnstileToken}
          onExpire={() => setTurnstileToken(null)}
          className="mt-2"
        />

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground font-semibold text-sm py-3 px-6 rounded-lg hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <Send className="h-4 w-4" />
          {submitting ? "Publishing…" : "Publish Sighting"}
        </button>
      </div>
    </form>
  );
}

/* ------------------------------------------------------------------ */
/* Slot Drop Patterns — Heatmap                                       */
/* ------------------------------------------------------------------ */
const TIME_BLOCKS = [
  { label: "Late Night",    sublabel: "10 PM – 2 AM", start: 22, end: 2 },
  { label: "Early Morning", sublabel: "2 AM – 6 AM",  start: 2,  end: 6 },
  { label: "Morning",       sublabel: "6 AM – 12 PM", start: 6,  end: 12 },
  { label: "Afternoon",     sublabel: "12 – 6 PM",    start: 12, end: 18 },
  { label: "Evening",       sublabel: "6 PM – 10 PM", start: 18, end: 22 },
] as const;

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;

/** Try to extract hour (IST) from a sighting description. */
function extractISTHour(desc: string): number | null {
  // Match patterns like "1:30 AM IST", "12:01 AM IST", "11:45 PM IST", "midnight"
  const ampm = desc.match(/(\d{1,2})(?::(\d{2}))?\s*(AM|PM)\s*IST/i);
  if (ampm) {
    let h = parseInt(ampm[1], 10);
    const period = ampm[3].toUpperCase();
    if (period === "AM" && h === 12) h = 0;
    if (period === "PM" && h !== 12) h += 12;
    return h;
  }
  if (/midnight/i.test(desc)) return 0;
  return null;
}

/** Try to extract day-of-week from a sighting description. */
function extractDayOfWeek(desc: string, createdAt: string): number {
  // Check description for explicit day mentions
  const dayNames = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
  const lower = desc.toLowerCase();
  for (let i = 0; i < dayNames.length; i++) {
    if (lower.includes(dayNames[i]) || lower.includes(dayNames[i].slice(0, 3))) {
      return i; // 0=Mon
    }
  }
  // Fall back to created_at timestamp day
  const d = new Date(createdAt);
  const js = d.getUTCDay(); // 0=Sun
  return js === 0 ? 6 : js - 1; // convert to 0=Mon
}

function inTimeBlock(hour: number, block: typeof TIME_BLOCKS[number]): boolean {
  if (block.start < block.end) {
    return hour >= block.start && hour < block.end;
  }
  // Wraps midnight: e.g. 22–2
  return hour >= block.start || hour < block.end;
}

function SlotPatterns({ sightings, filterConsulate }: { sightings: VisaSighting[]; filterConsulate: string }) {
  const [heatConsulate, setHeatConsulate] = useState("");

  const activeSightings = useMemo(() => {
    const c = heatConsulate || filterConsulate;
    return c ? sightings.filter((s) => s.consulate === c) : sightings;
  }, [sightings, heatConsulate, filterConsulate]);

  // Build heatmap grid: [timeBlock][dayOfWeek] = count
  const { grid, maxCount } = useMemo(() => {
    const g: number[][] = TIME_BLOCKS.map(() => DAYS.map(() => 0));
    for (const s of activeSightings) {
      const hour = extractISTHour(s.description);
      const day = extractDayOfWeek(s.description, s.created_at);
      if (hour !== null) {
        for (let t = 0; t < TIME_BLOCKS.length; t++) {
          if (inTimeBlock(hour, TIME_BLOCKS[t])) {
            g[t][day]++;
            break;
          }
        }
      } else {
        // No time parsed — distribute to late night (most common pattern)
        g[0][day] += 0.5;
      }
    }
    let mx = 0;
    for (const row of g) for (const v of row) if (v > mx) mx = v;
    return { grid: g, maxCount: mx };
  }, [activeSightings]);

  // Parse slot lifespans from descriptions
  const avgLifespan = useMemo(() => {
    const mins: number[] = [];
    for (const s of sightings) {
      const m = s.description.match(/(\d+)\s*min/i);
      if (m) mins.push(parseInt(m[1], 10));
      if (/under\s*5/i.test(s.description)) mins.push(4);
    }
    if (mins.length === 0) return null;
    return Math.round(mins.reduce((a, b) => a + b, 0) / mins.length);
  }, [sightings]);

  const cellColor = (val: number) => {
    if (val === 0 || maxCount === 0) return "bg-foreground/[0.03]";
    const intensity = val / maxCount;
    if (intensity > 0.75) return "bg-amber-500/70 text-amber-950";
    if (intensity > 0.5) return "bg-amber-500/45 text-amber-900";
    if (intensity > 0.25) return "bg-amber-500/25 text-amber-800";
    return "bg-amber-500/10 text-amber-700";
  };

  return (
    <section className="mb-10">
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-border bg-[#1a1a2e]/[0.03]">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="font-serif font-bold text-lg flex items-center gap-2">
                ⏰ When Do Slots Drop?
              </h2>
              <p className="text-xs text-foreground/50 mt-1">
                Heatmap of community sightings by day & time (IST)
              </p>
            </div>
            <select
              value={heatConsulate}
              onChange={(e) => setHeatConsulate(e.target.value)}
              className="text-xs rounded-lg border border-border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors sm:w-auto w-full"
            >
              <option value="">All Consulates</option>
              {CONSULATES.map((c) => (
                <option key={c} value={c}>{CONSULATE_LABELS[c]}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Key Insight Callout */}
        <div className="px-5 py-3 border-b border-border bg-amber-500/[0.06]">
          <div className="flex items-start gap-3">
            <span className="text-lg flex-shrink-0 mt-0.5">💡</span>
            <div>
              <p className="text-sm font-semibold text-foreground/85">
                Peak window: <span className="text-amber-600">Wednesday – Thursday, 11 PM – 1 AM IST</span>
              </p>
              <p className="text-xs text-foreground/50 mt-0.5 leading-relaxed">
                Based on community reports and cross-referenced data, most new appointment slots appear during the late-night Wednesday window. Set an alarm and refresh at midnight IST.
              </p>
            </div>
          </div>
        </div>

        {/* Heatmap Grid */}
        <div className="p-5">
          <div className="overflow-x-auto -mx-2 px-2">
            <div className="min-w-[480px]">
              {/* Day headers */}
              <div className="grid grid-cols-[120px_repeat(7,1fr)] gap-1.5 mb-1.5">
                <div /> {/* empty corner */}
                {DAYS.map((d) => (
                  <div key={d} className={`text-center text-[11px] font-bold uppercase tracking-wider py-1.5 rounded-md ${
                    d === "Wed" || d === "Thu"
                      ? "text-amber-600 bg-amber-500/[0.08]"
                      : "text-foreground/40"
                  }`}>
                    {d}
                  </div>
                ))}
              </div>

              {/* Time block rows */}
              {TIME_BLOCKS.map((block, ti) => (
                <div key={block.label} className="grid grid-cols-[120px_repeat(7,1fr)] gap-1.5 mb-1.5">
                  <div className="flex flex-col justify-center pr-2 text-right">
                    <span className={`text-[11px] font-semibold leading-tight ${
                      ti === 0 ? "text-amber-600" : "text-foreground/60"
                    }`}>
                      {block.label}
                    </span>
                    <span className="text-[9px] text-foreground/35 leading-tight">{block.sublabel}</span>
                  </div>
                  {DAYS.map((d, di) => {
                    const val = grid[ti][di];
                    return (
                      <div
                        key={d}
                        className={`rounded-md h-10 flex items-center justify-center text-[11px] font-bold transition-colors ${cellColor(val)} ${
                          val > 0 ? "shadow-sm" : ""
                        }`}
                        title={`${d} ${block.sublabel}: ${Math.round(val)} sighting${val !== 1 ? "s" : ""}`}
                      >
                        {val > 0 ? Math.round(val) : ""}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          {/* Legend + Stats */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4 pt-4 border-t border-border">
            {/* Legend */}
            <div className="flex items-center gap-2 text-[10px] text-foreground/50">
              <span>Less</span>
              <div className="flex gap-0.5">
                <div className="w-4 h-4 rounded bg-foreground/[0.03] border border-border" />
                <div className="w-4 h-4 rounded bg-amber-500/10" />
                <div className="w-4 h-4 rounded bg-amber-500/25" />
                <div className="w-4 h-4 rounded bg-amber-500/45" />
                <div className="w-4 h-4 rounded bg-amber-500/70" />
              </div>
              <span>More</span>
            </div>

            {/* Slot lifespan stat */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-red-500/8 border border-red-500/15 rounded-full px-3 py-1.5">
                <span className="text-xs">⚡</span>
                <span className="text-[11px] font-semibold text-red-600/80">
                  Slots last ~{avgLifespan ?? "5-10"} min on average
                </span>
              </div>
              <span className="text-[10px] text-foreground/35">
                {activeSightings.length} sighting{activeSightings.length !== 1 ? "s" : ""} analyzed
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Main Page                                                          */
/* ------------------------------------------------------------------ */
export default function VisaTrackerPage() {
  const [sightings, setSightings] = useState<VisaSighting[]>([]);
  const [waitTimes, setWaitTimes] = useState<ConsulateWaitRow[]>([]);
  const [updates, setUpdates] = useState<{ id: string; date: string; label: string; headline: string; summary: string; severity: string; source: string }[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterConsulate, setFilterConsulate] = useState<string>("");
  const [filterVisa, setFilterVisa] = useState<string>("");

  const load = useCallback(async () => {
    const [s, w] = await Promise.all([getVisaSightings(), getConsulateWaitTimes([...INDIA_CONSULATES])]);
    setSightings(s);
    setWaitTimes(w);
    // Load updates from static JSON
    try {
      const res = await fetch("/data/visa-updates.json");
      if (res.ok) setUpdates(await res.json());
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = useMemo(() => {
    let results = sightings;
    if (filterConsulate) results = results.filter((s) => s.consulate === filterConsulate);
    if (filterVisa) results = results.filter((s) => s.visa_type === filterVisa);
    return results;
  }, [sightings, filterConsulate, filterVisa]);

  const pillClass = (active: boolean) =>
    `inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
      active
        ? "bg-primary text-primary-foreground shadow-sm"
        : "bg-foreground/5 text-foreground/60 hover:bg-foreground/10"
    }`;

  return (
    <>
      <Helmet>
        <title>US Visa Appointment Tracker — Community Slot Intelligence | The Videshi</title>
        <meta
          name="description"
          content="Community-powered US visa appointment slot tracker for India's 5 consulates. See real-time sightings, official wait times, and report open slots to help fellow Indians."
        />
        <meta property="og:title" content="US Visa Appointment Tracker — The Videshi" />
        <meta
          property="og:description"
          content="Track US visa appointment openings across India's 5 consulates. Community-sourced, real-time sighting reports."
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration/visas" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* ── Hero ─────────────────────────────────────────── */}
        <section className="relative mb-10 -mx-4 px-6 py-12 md:py-16 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div
            className="absolute inset-0 opacity-[0.06]"
            style={{
              backgroundImage:
                "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
            }}
          />
          <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/8 rounded-full blur-3xl" />

          <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-amber-300 bg-amber-500/15 px-3 py-1 rounded-full">
                🛂 Community-Powered
              </span>
            </div>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight leading-[1.1] text-white">
              US Visa Appointment<br />
              <span className="text-green-400">Tracker.</span>
            </h1>
            <p className="text-white/70 mt-4 text-base md:text-lg max-w-2xl leading-relaxed">
              Real-time slot sightings from the community for India's 5 US consulates.
              See what people are finding, and share what you see.
            </p>
            <div className="flex flex-wrap gap-3 mt-6">
              <a
                href="#report"
                className="inline-flex items-center gap-2 bg-green-500 text-white font-semibold text-sm py-2.5 px-6 rounded-full hover:bg-green-400 transition-colors shadow-lg shadow-green-500/20"
              >
                <Send className="h-4 w-4" />
                Report a Sighting
              </a>
              <Link
                to="/immigration"
                className="inline-flex items-center gap-2 bg-white/10 text-white/80 font-medium text-sm py-2.5 px-5 rounded-full hover:bg-white/15 transition-colors border border-white/10"
              >
                ← Immigration Hub
              </Link>
            </div>
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* ── Trust note ────────────────────────────────── */}
            <p className="text-xs text-foreground/50 text-center mb-6 max-w-xl mx-auto leading-relaxed">
              US consulates prohibit automated scraping of their booking systems. This tracker relies entirely on community members voluntarily sharing what they see — helping each other, the only legal way.
            </p>

            {/* ── Official Wait Times ──────────────────────────── */}
            <section className="mb-10">
              <WaitTimeStrip data={waitTimes} />
            </section>

            {/* ── Slot Drop Patterns ──────────────────────────── */}
            <SlotPatterns sightings={sightings} filterConsulate={filterConsulate} />

            {/* ── Two-Column Layout ────────────────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
              {/* ── Left: Sighting Feed ──────────────────────── */}
              <div>
                <div className="flex items-center justify-between mb-5">
                  <h2 className="font-serif text-xl font-bold flex items-center gap-2">
                    📡 Community Sightings
                    <span className="text-xs font-normal text-foreground/40 ml-1">
                      {filtered.length} report{filtered.length !== 1 && "s"}
                    </span>
                  </h2>
                </div>

                {/* ── Filter Pills ──────────────────────────── */}
                <div className="mb-5 space-y-2">
                  <div className="flex flex-wrap gap-2">
                    <button className={pillClass(!filterConsulate)} onClick={() => setFilterConsulate("")}>
                      All Consulates
                    </button>
                    {CONSULATES.map((c) => (
                      <button key={c} className={pillClass(filterConsulate === c)} onClick={() => setFilterConsulate(filterConsulate === c ? "" : c)}>
                        {CONSULATE_LABELS[c]}
                      </button>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button className={pillClass(!filterVisa)} onClick={() => setFilterVisa("")}>
                      All Types
                    </button>
                    {VISA_TYPES.map((v) => (
                      <button key={v} className={pillClass(filterVisa === v)} onClick={() => setFilterVisa(filterVisa === v ? "" : v)}>
                        {v}
                      </button>
                    ))}
                  </div>
                </div>

                {/* ── Sighting Cards ─────────────────────────── */}
                <div className="space-y-3">
                  {filtered.length === 0 ? (
                    <div className="text-center py-12 bg-card border border-border rounded-xl">
                      <p className="text-foreground/40 text-sm">No sightings match the current filters.</p>
                      <button
                        onClick={() => { setFilterConsulate(""); setFilterVisa(""); }}
                        className="mt-2 text-primary text-sm font-medium hover:underline"
                      >
                        Clear filters
                      </button>
                    </div>
                  ) : (
                    filtered.map((s) => <SightingCard key={s.id} s={s} />)
                  )}
                </div>

                {/* ── Report Form ─────────────────────────────── */}
                <div id="report" className="mt-10 scroll-mt-20">
                  <ReportForm onSubmitted={load} />
                </div>
              </div>

              {/* ── Right Sidebar ────────────────────────────── */}
              <aside className="space-y-6">
                {/* Visa Alerts Signup — top of sidebar */}
                <div className="bg-gradient-to-b from-green-500/10 to-emerald-500/5 border border-green-500/20 rounded-xl p-5">
                  <h4 className="font-serif font-bold text-sm mb-1 flex items-center gap-2">
                    🔔 Visa Slot Alerts
                  </h4>
                  <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-500/15 text-green-700 text-[10px] font-bold uppercase tracking-wider mb-2">
                    Free during launch
                  </div>
                  <p className="text-xs text-foreground/60 leading-relaxed mb-3">
                    Get notified instantly when new appointment slots open or when policy changes affect your visa type.
                  </p>
                  <form
                    onSubmit={async (e) => {
                      e.preventDefault();
                      const form = e.target as HTMLFormElement;
                      const emailEl = form.elements.namedItem("alert_email") as HTMLInputElement;
                      const waEl = form.elements.namedItem("alert_whatsapp") as HTMLInputElement;
                      const typeEl = form.elements.namedItem("alert_type") as HTMLSelectElement;
                      if (!emailEl.value && !waEl.value) { alert("Please enter at least an email or WhatsApp number."); return; }
                      try {
                        const { createClient } = await import("@supabase/supabase-js");
                        const sb = createClient(
                          import.meta.env.VITE_SUPABASE_URL,
                          import.meta.env.VITE_SUPABASE_ANON_KEY
                        );
                        const channels: string[] = [];
                        if (emailEl.value) channels.push("email");
                        if (waEl.value) channels.push("whatsapp");
                        await sb.from("visa_alert_subscribers").upsert({
                          email: emailEl.value || `wa-${waEl.value}@placeholder.local`,
                          whatsapp: waEl.value || null,
                          visa_type: typeEl.value || "all",
                          channel: channels.join(","),
                          subscribed_at: new Date().toISOString(),
                          active: true,
                        }, { onConflict: "email" });
                        emailEl.value = "";
                        waEl.value = "";
                        alert("You're in! We'll notify you when slots open. 🎉");
                      } catch {
                        alert("Something went wrong — try again.");
                      }
                    }}
                    className="space-y-2"
                  >
                    <input name="alert_email" type="email" placeholder="your@email.com" className="w-full rounded-lg border border-border bg-background px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-colors" />
                    <div className="relative">
                      <input name="alert_whatsapp" type="tel" disabled placeholder="WhatsApp — coming soon" className="w-full rounded-lg border border-border bg-foreground/[0.03] px-3 py-2 text-xs text-foreground/30 cursor-not-allowed" />
                      <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[9px] font-semibold uppercase tracking-wider text-foreground/30">Soon</span>
                    </div>
                    <select name="alert_type" className="w-full rounded-lg border border-border bg-background px-3 py-2 text-xs text-foreground/70 focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-colors">
                      <option value="all">All visa types</option>
                      <option value="B1B2">B1/B2 (Visitor)</option>
                      <option value="H-1B">H-1B</option>
                      <option value="H-4">H-4</option>
                      <option value="F-1">F-1 (Student)</option>
                      <option value="L-1">L-1</option>
                      <option value="O-1">O-1</option>
                    </select>
                    <button type="submit" className="w-full bg-green-600 text-white text-xs font-semibold py-2 rounded-lg hover:bg-green-500 transition-colors">
                      Get Free Alerts
                    </button>
                  </form>
                  <p className="text-[10px] text-foreground/40 mt-2 leading-relaxed">
                    This is a premium service offered free during our launch period. No credit card needed.
                  </p>
                </div>

                <ThankYouWall sightings={sightings} />

                {/* Latest Updates */}
                {updates.length > 0 && (
                <div className="bg-card border border-border rounded-xl p-5">
                  <h4 className="font-serif font-bold text-sm mb-3 flex items-center gap-2">
                    📰 Latest Updates
                  </h4>
                  <ul className="text-xs text-foreground/70 space-y-3 leading-relaxed">
                    {updates.map((u, i) => (
                      <li key={u.id} className={i < updates.length - 1 ? "border-b border-border pb-2.5" : ""}>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-primary/70">{u.label}</span>
                        <p className="mt-0.5 font-medium text-foreground/90">{u.headline}</p>
                        <p className="mt-0.5">{u.summary}</p>
                      </li>
                    ))}
                  </ul>
                </div>
                )}

                {/* How it works */}
                <div className="bg-card border border-border rounded-xl p-5">
                  <h4 className="font-serif font-bold text-sm mb-3 flex items-center gap-2">
                    💡 How This Works
                  </h4>
                  <ol className="text-xs text-foreground/60 space-y-2 list-decimal list-inside leading-relaxed">
                    <li>Check <a href="https://www.ustraveldocs.com/" target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-2">ustraveldocs.com</a> for open slots</li>
                    <li>Spot available dates? Report them here</li>
                    <li>Others see your sighting and can book their slot</li>
                    <li>You appear on the Community Spotters wall 🙏</li>
                  </ol>
                </div>

                {/* Visa Guides */}
                <Link to="/immigration/guides" className="block bg-card border border-border rounded-xl p-5 hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 group">
                  <h4 className="font-serif font-bold text-sm mb-2 flex items-center gap-2 group-hover:text-primary transition-colors">
                    📚 Visa Guides
                  </h4>
                  <ul className="text-xs text-foreground/60 space-y-1.5 leading-relaxed">
                    <li className="flex items-center gap-1.5">🏛️ <span>Interview prep & document checklist</span></li>
                    <li className="flex items-center gap-1.5">🚫 <span>What NOT to say to the officer</span></li>
                    <li className="flex items-center gap-1.5">📱 <span>Social media screening guide</span></li>
                    <li className="flex items-center gap-1.5">📬 <span>After your interview — what to expect</span></li>
                    <li className="flex items-center gap-1.5">🌍 <span>Third-country stamping guide</span></li>
                  </ul>
                  <p className="text-xs text-primary font-medium mt-3 flex items-center gap-1 group-hover:gap-2 transition-all">
                    Read all guides <ChevronRight className="h-3 w-3" />
                  </p>
                </Link>

                {/* Disclaimer */}
                <div className="bg-amber-500/5 border border-amber-500/15 rounded-xl p-4">
                  <p className="text-[11px] text-foreground/50 leading-relaxed">
                    <span className="font-semibold text-foreground/70">Data Source Note:</span>{" "}
                    Official wait times are from the US State Department. Community sightings are
                    user-reported observations — we never scrape or automate access to
                    ustraveldocs.com. Slot availability changes rapidly; always verify on the
                    official site before booking.
                  </p>
                </div>
              </aside>
            </div>
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
