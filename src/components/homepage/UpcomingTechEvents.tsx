import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface TechEvent {
  id: string;
  title: string;
  date: string;
  end_date?: string;
  venue_name?: string;
  city?: string;
  state?: string;
  slug: string;
  ticket_url?: string;
}

function formatDateRange(date: string, endDate?: string): string {
  const d = new Date(date + "T00:00:00");
  const month = d.toLocaleDateString("en-US", { month: "short" });
  const day = d.getDate();
  if (!endDate) return `${month} ${day}`;
  const ed = new Date(endDate + "T00:00:00");
  if (d.getMonth() === ed.getMonth()) {
    return `${month} ${day}–${ed.getDate()}`;
  }
  const eMonth = ed.toLocaleDateString("en-US", { month: "short" });
  return `${month} ${day} – ${eMonth} ${ed.getDate()}`;
}

function daysUntil(date: string): number {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const d = new Date(date + "T00:00:00");
  return Math.ceil((d.getTime() - now.getTime()) / 86400000);
}

function urgencyLabel(days: number): string | null {
  if (days <= 0) return "NOW";
  if (days <= 7) return `${days}d away`;
  return null;
}

export default function UpcomingTechEvents() {
  const [events, setEvents] = useState<TechEvent[]>([]);

  useEffect(() => {
    fetch("/data/events.json")
      .then((r) => (r.ok ? r.json() : []))
      .then((data: TechEvent[]) => {
        const today = new Date().toISOString().slice(0, 10);
        const techEvents = data
          .filter(
            (e: any) =>
              e.category === "Technology" &&
              (e.end_date || e.date) >= today
          )
          .sort((a: TechEvent, b: TechEvent) => a.date.localeCompare(b.date))
          .slice(0, 10);
        setEvents(techEvents);
      })
      .catch(() => {});
  }, []);

  if (events.length === 0) return null;

  return (
    <div style={{
      background: "linear-gradient(135deg, #0B1D3A 0%, #132d54 100%)",
      borderRadius: 12,
      padding: "16px 0",
      marginBottom: 24,
    }}>
      <div className="container">
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          marginBottom: 12,
          paddingLeft: 4,
        }}>
          <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: 2, textTransform: "uppercase", color: "#D4A843" }}>
            Upcoming Conferences
          </span>
          <Link
            to="/events"
            style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", textDecoration: "none", marginLeft: "auto" }}
          >
            All events →
          </Link>
        </div>

        <div style={{
          display: "flex",
          gap: 10,
          overflowX: "auto",
          overflowY: "hidden",
          scrollSnapType: "x mandatory",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          paddingBottom: 2,
        }}>
          {events.map((e) => {
            const days = daysUntil(e.date);
            const urg = urgencyLabel(days);
            return (
              <Link
                key={e.id}
                to={`/events/${e.slug}`}
                style={{
                  flex: "0 0 auto",
                  width: 180,
                  minWidth: 180,
                  scrollSnapAlign: "start",
                  background: "rgba(255,255,255,0.07)",
                  borderRadius: 10,
                  padding: "12px 14px",
                  textDecoration: "none",
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                  transition: "background 0.2s",
                  border: "1px solid rgba(255,255,255,0.08)",
                }}
                onMouseEnter={(ev) => ((ev.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.12)")}
                onMouseLeave={(ev) => ((ev.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.07)")}
              >
                {/* Date + urgency */}
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#D4A843",
                    letterSpacing: 0.5,
                  }}>
                    {formatDateRange(e.date, e.end_date)}
                  </span>
                  {urg && (
                    <span style={{
                      fontSize: 9,
                      fontWeight: 700,
                      color: days <= 0 ? "#fff" : "#FF6B35",
                      background: days <= 0 ? "#e53e3e" : "rgba(255,107,53,0.15)",
                      padding: "1px 5px",
                      borderRadius: 4,
                      letterSpacing: 0.3,
                    }}>
                      {urg}
                    </span>
                  )}
                </div>

                {/* Title */}
                <span style={{
                  fontSize: 13,
                  fontWeight: 700,
                  color: "#fff",
                  lineHeight: 1.3,
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}>
                  {e.title}
                </span>

                {/* Location */}
                <span style={{
                  fontSize: 11,
                  color: "rgba(255,255,255,0.5)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}>
                  {e.city}{e.state ? `, ${e.state}` : ""}
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
