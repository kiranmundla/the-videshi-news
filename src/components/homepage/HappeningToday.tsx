import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { DailyHappening, getTodayHappenings, buildDetail } from "@/lib/happenings";

export default function HappeningToday() {
  const [items, setItems] = useState<DailyHappening[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    getTodayHappenings().then((data) => {
      setItems(data);
      setLoading(false);
    });
  }, []);

  if (loading || items.length === 0) return null;

  const MAX_VISIBLE = 4;
  const showToggle = items.length > MAX_VISIBLE;
  const visible = expanded ? items : items.slice(0, MAX_VISIBLE);

  return (
    <div className="v2-happening-strip">
      <div className="container">
        <div className="v2-happening-header">
          <span className="v2-happening-badge">HAPPENING TODAY</span>
        </div>
        <div className="v2-happening-list">
          {visible.map((item) => {
            const detail = buildDetail(item);
            const row = (
              <div className="v2-happening-row">
                <span className="v2-happening-emoji">{item.emoji}</span>
                <span className="v2-happening-label">{item.label}</span>
                {detail && (
                  <span className="v2-happening-detail">— {detail}</span>
                )}
              </div>
            );

            if (item.link) {
              const isExternal = item.link.startsWith("http");
              if (isExternal) {
                return (
                  <a
                    key={item.id}
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="v2-happening-link"
                  >
                    {row}
                  </a>
                );
              }
              return (
                <Link key={item.id} to={item.link} className="v2-happening-link">
                  {row}
                </Link>
              );
            }

            return <div key={item.id}>{row}</div>;
          })}
        </div>
        {showToggle && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="v2-happening-toggle"
          >
            {expanded ? "Show less" : `+${items.length - MAX_VISIBLE} more`}
          </button>
        )}
      </div>
    </div>
  );
}
