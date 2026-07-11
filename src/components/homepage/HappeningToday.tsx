import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { DailyHappening, getTodayHappenings } from "@/lib/happenings";

export default function HappeningToday() {
  const [items, setItems] = useState<DailyHappening[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTodayHappenings().then((data) => {
      setItems(data);
      setLoading(false);
    });
  }, []);

  if (loading || items.length === 0) return null;

  return (
    <div className="v2-happening-strip">
      <div className="container">
        <div className="v2-happening-inner">
          <span className="v2-happening-badge">TODAY</span>
          <div className="v2-happening-scroll">
            {items.map((item) => {
              const content = (
                <div key={item.id} className="v2-happening-item">
                  <span className="v2-happening-emoji">{item.emoji}</span>
                  <div className="v2-happening-text">
                    <span className="v2-happening-label">{item.label}</span>
                    {item.detail && (
                      <span className="v2-happening-detail">{item.detail}</span>
                    )}
                  </div>
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
                      {content}
                    </a>
                  );
                }
                return (
                  <Link key={item.id} to={item.link} className="v2-happening-link">
                    {content}
                  </Link>
                );
              }

              return <div key={item.id}>{content}</div>;
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
