import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
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

  useEffect(() => {
    getKeyUpdates(category, limit).then((data) => {
      setUpdates(data);
      setLoading(false);
    });
  }, [category, limit]);

  if (loading || updates.length === 0) return null;

  const grouped = groupByMonth(updates);
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

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        {displayGroups.map((group, gi) => (
          <div key={group.label}>
            <div className="px-4 py-2 bg-foreground/[0.03] border-b border-border">
              <span className="text-xs font-bold uppercase tracking-wider text-foreground/50">
                {group.label}
              </span>
            </div>
            <div className="divide-y divide-border">
              {group.items.map((update) => (
                <div
                  key={update.id}
                  className="group hover:bg-foreground/[0.02] transition-colors"
                >
                  {update.article_slug ? (
                    <Link
                      to={`/articles/${update.article_slug}`}
                      className="flex items-start gap-3 px-4 py-3 text-inherit no-underline"
                    >
                      <span className="text-sm mt-0.5 flex-shrink-0">
                        {IMPACT_ICON[update.impact] || "⚪"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm leading-snug ${update.impact === "high" ? "font-bold" : "font-semibold"}`}>
                          {update.headline}
                        </p>
                      </div>
                      {update.event_date && (
                        <span className="text-[10px] text-foreground/40 whitespace-nowrap mt-1 flex-shrink-0">
                          {new Date(update.event_date + "T00:00:00").toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                          })}
                        </span>
                      )}
                    </Link>
                  ) : (
                    <div className="flex items-start gap-3 px-4 py-3">
                      <span className="text-sm mt-0.5 flex-shrink-0">
                        {IMPACT_ICON[update.impact] || "⚪"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm leading-snug ${update.impact === "high" ? "font-bold" : "font-semibold"}`}>
                          {update.headline}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
