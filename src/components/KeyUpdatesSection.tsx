import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ChevronRight, ChevronDown } from "lucide-react";
import { KeyUpdate, getKeyUpdates } from "@/lib/keyUpdates";

const IMPACT_ICON: Record<string, string> = {
  high: "🔴",
  medium: "🟡",
  low: "⚪",
};

function UpdateRow({ update }: { update: KeyUpdate }) {
  const [open, setOpen] = useState(false);
  const related = update.related_articles ?? [];
  const hasRelated = related.length > 1;

  const label = (
    <span
      style={{
        fontSize: "12.5px",
        fontWeight: update.impact === "high" ? 700 : 600,
        color: "#0f172a",
        letterSpacing: "0.01em",
      }}
    >
      {update.headline}
    </span>
  );

  const date = update.event_date
    ? new Date(update.event_date + "T00:00:00").toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : null;

  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        <span style={{ fontSize: "13px", flexShrink: 0, lineHeight: 1 }}>
          {IMPACT_ICON[update.impact] || "⚪"}
        </span>
        {update.article_slug ? (
          <Link
            to={`/articles/${update.article_slug}`}
            style={{ textDecoration: "none", color: "inherit" }}
            className="v2-keydev-link"
          >
            {label}
          </Link>
        ) : (
          label
        )}
        {date && (
          <span style={{ fontSize: "12px", color: "#64748b", fontWeight: 400 }}>
            — {date}
          </span>
        )}
      </div>
      {hasRelated && (
        <button
          onClick={() => setOpen(!open)}
          style={{
            marginTop: "4px",
            marginLeft: "21px",
            display: "flex",
            alignItems: "center",
            gap: "3px",
            fontSize: "11px",
            fontWeight: 600,
            color: "#A32D2D",
            background: "none",
            border: "none",
            cursor: "pointer",
            padding: 0,
          }}
        >
          {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          {related.length} related
        </button>
      )}
      {open && hasRelated && (
        <div style={{ marginTop: "4px", marginLeft: "21px", paddingLeft: "8px", borderLeft: "2px solid #e2e8f0" }}>
          {related.map((ra, i) => (
            <Link
              key={i}
              to={`/articles/${ra.slug}`}
              style={{
                display: "block",
                fontSize: "11px",
                color: "#64748b",
                lineHeight: 1.5,
                textDecoration: "none",
                paddingTop: "2px",
              }}
              className="v2-keydev-link"
            >
              {ra.headline}
            </Link>
          ))}
        </div>
      )}
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
  const [showAll, setShowAll] = useState(false);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    getKeyUpdates(category, limit).then((data) => {
      setUpdates(data);
      setLoading(false);
    });
  }, [category, limit]);

  if (loading || updates.length === 0) return null;

  const filtered = showAll ? updates : updates.filter((u) => u.impact === "high");
  if (filtered.length === 0 && !showAll) return null;

  const hasMedium = updates.some((u) => u.impact !== "high");
  const MAX_VISIBLE = 6;
  const visible = expanded ? filtered : filtered.slice(0, MAX_VISIBLE);
  const showToggle = filtered.length > MAX_VISIBLE;

  return (
    <section
      className={className}
      style={{
        background: "#fff",
        borderBottom: "1px solid #e2e8f0",
        padding: "14px 0",
      }}
    >
      <div className="container">
        <div style={{ marginBottom: "10px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span
            style={{
              fontSize: "10px",
              fontWeight: 800,
              letterSpacing: "1.8px",
              color: "#A32D2D",
              textTransform: "uppercase" as const,
            }}
          >
            {title || "KEY DEVELOPMENTS"}
          </span>
          {hasMedium && (
            <button
              onClick={() => setShowAll(!showAll)}
              style={{
                fontSize: "11px",
                fontWeight: 600,
                color: "#A32D2D",
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: 0,
                letterSpacing: "0.02em",
              }}
            >
              {showAll ? "Major only" : "Show all"}
            </button>
          )}
        </div>
        <div style={{ display: "flex", flexDirection: "column" as const, gap: "8px" }}>
          {visible.map((update) => (
            <UpdateRow key={update.id} update={update} />
          ))}
        </div>
        {showToggle && (
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              marginTop: "8px",
              fontSize: "11px",
              fontWeight: 600,
              color: "#A32D2D",
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: 0,
              letterSpacing: "0.02em",
            }}
          >
            {expanded ? "Show less" : `+${filtered.length - MAX_VISIBLE} more`}
          </button>
        )}
      </div>
    </section>
  );
}
