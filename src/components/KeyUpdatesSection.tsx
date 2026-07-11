import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ChevronRight, ChevronDown } from "lucide-react";
import { KeyUpdate, getKeyUpdates } from "@/lib/keyUpdates";

const IMPACT_ICON: Record<string, string> = {
  high: "🔴",
  medium: "🟡",
  low: "⚪",
};

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function groupByMonth(updates: KeyUpdate[]): { label: string; items: KeyUpdate[] }[] {
  const groups: Record<string, KeyUpdate[]> = {};
  for (const u of updates) {
    const d = u.event_date ? new Date(u.event_date + "T00:00:00") : new Date(u.created_at);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(u);
  }
  return Object.entries(groups)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([key, items]) => {
      const [y, m] = key.split("-").map(Number);
      return { label: `${MONTH_NAMES[m - 1]} ${y}`, items };
    });
}

function UpdateRow({ update }: { update: KeyUpdate }) {
  const [open, setOpen] = useState(false);
  const related = update.related_articles ?? [];
  const hasRelated = related.length > 1;

  return (
    <div className="group hover:bg-foreground/[0.02] transition-colors">
      <div className="flex items-start gap-3 px-4 py-3">
        <span className="text-sm mt-0.5 flex-shrink-0">
          {IMPACT_ICON[update.impact] || "⚪"}
        </span>
        <div className="flex-1 min-w-0">
          {update.article_slug ? (
            <Link
              to={`/articles/${update.article_slug}`}
              className="text-inherit no-underline"
            >
              <p className={`text-sm leading-snug ${update.impact === "high" ? "font-bold" : "font-semibold"}`}>
                {update.headline}
              </p>
            </Link>
          ) : (
            <p className={`text-sm leading-snug ${update.impact === "high" ? "font-bold" : "font-semibold"}`}>
              {update.headline}
            </p>
          )}
          {hasRelated && (
            <button
              onClick={() => setOpen(!open)}
              className="mt-1 flex items-center gap-1 text-xs text-foreground/40 hover:text-foreground/60 transition-colors"
            >
              {open ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronRight className="h-3 w-3" />
              )}
              {related.length} related articles
            </button>
          )}
          {open && hasRelated && (
            <div className="mt-2 pl-1 space-y-1 border-l-2 border-foreground/10">
              {related.map((ra, i) => (
                <Link
                  key={i}
                  to={`/articles/${ra.slug}`}
                  className="block pl-3 text-xs text-foreground/60 hover:text-foreground/80 leading-snug no-underline"
                >
                  {ra.headline}
                </Link>
              ))}
            </div>
          )}
        </div>
        {update.event_date && (
          <span className="text-[10px] text-foreground/40 whitespace-nowrap mt-1 flex-shrink-0">
            {new Date(update.event_date + "T00:00:00").toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
            })}
          </span>
        )}
      </div>
    </div>
  );
}

interface KeyUpdatesProps {
  category: string;
  title?: string;
  limit?: number;
  className?: string;
}

export default function KeyUpdatesSection({ category, title, limit = 15, className = "" }: KeyUpdatesProps) {
  const [updates, setUpdates] = useState<KeyUpdate[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    getKeyUpdates(category, limit).then((data) => {
      setUpdates(data);
      setLoading(false);
    });
  }, [category, limit]);

  if (loading || updates.length === 0) return null;

  const filtered = showAll ? updates : updates.filter((u) => u.impact === "high");
  if (filtered.length === 0 && !showAll) {
    return null;
  }
  const hasMedium = updates.some((u) => u.impact !== "high");
  const grouped = groupByMonth(filtered);
  const displayGroups = expanded ? grouped : grouped.slice(0, 1);
  const hasMore = grouped.length > 1;

  return (
    <section className={className}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-lg">⚡</span>
          <h2 className="font-serif text-xl font-bold">
            {title || "Key Developments"}
          </h2>
        </div>
        <div className="flex items-center gap-3">
          {hasMedium && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="text-sm text-foreground/50 hover:text-foreground/70 font-medium"
            >
              {showAll ? "Major only" : "Show all"}
            </button>
          )}
          {hasMore && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-sm text-primary hover:text-primary/80 font-medium flex items-center gap-1"
            >
              {expanded ? "Show less" : `All months`}
              <ChevronRight className={`h-4 w-4 transition-transform ${expanded ? "rotate-90" : ""}`} />
            </button>
          )}
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        {displayGroups.map((group) => (
          <div key={group.label}>
            <div className="px-4 py-2 bg-foreground/[0.03] border-b border-border">
              <span className="text-xs font-bold uppercase tracking-wider text-foreground/50">
                {group.label}
              </span>
            </div>
            <div className="divide-y divide-border">
              {group.items.map((update) => (
                <UpdateRow key={update.id} update={update} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
