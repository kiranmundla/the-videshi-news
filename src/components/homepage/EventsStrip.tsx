import { useMemo } from "react";
import { Link } from "react-router-dom";
import ScrollWrap from "./ScrollWrap";
import { getDistanceMiles, formatDistance } from "@/lib/geo";

interface EventItem {
  id: string;
  title: string;
  date: string;
  time?: string;
  venue_name?: string;
  city?: string;
  state?: string;
  category?: string;
  image_url?: string;
  latitude?: number;
  longitude?: number;
}

interface Props {
  events: EventItem[];
  userLat?: number | null;
  userLng?: number | null;
  userCity?: string | null;
}

function formatEventDate(dateStr: string) {
  const d = new Date(dateStr + "T00:00:00");
  const month = d.toLocaleDateString("en-US", { month: "short" }).toUpperCase();
  const day = d.getDate();
  return { month, day };
}

export default function EventsStrip({ events, userLat, userLng, userCity }: Props) {
  const MAX_DISTANCE_MI = 100;

  const upcoming = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    const filtered = events
      .filter((e) => e.date >= today)
      .map((e) => {
        let dist: number | null = null;
        if (userLat && userLng && e.latitude && e.longitude) {
          dist = getDistanceMiles(userLat, userLng, e.latitude, e.longitude);
        }
        return { ...e, _dist: dist };
      });

    if (userLat && userLng) {
      // Only show events within MAX_DISTANCE_MI when we know the user's location
      const nearby = filtered.filter(
        (e) => e._dist !== null && e._dist <= MAX_DISTANCE_MI,
      );
      nearby.sort((a, b) => {
        if (a._dist !== null && b._dist !== null) return a._dist - b._dist;
        return a.date.localeCompare(b.date);
      });
      return nearby.slice(0, 12);
    } else {
      filtered.sort((a, b) => a.date.localeCompare(b.date));
      return filtered.slice(0, 12);
    }
  }, [events, userLat, userLng]);

  if (upcoming.length === 0) return null;

  const headerLabel = userCity ? `📅 Events near ${userCity}` : "📅 Events";

  return (
    <section className="mb-14">
      <div className="container">
        {/* Header */}
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #D4A843" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            {headerLabel}
          </h2>
          <div className="flex items-center gap-4">
            <Link
              to="/events/submit"
              className="text-[12px] font-semibold text-primary hover:text-primary/80 transition-colors whitespace-nowrap"
            >
              + Post event
            </Link>
            <Link
              to="/events"
              className="text-[13px] font-semibold text-muted-foreground hover:text-foreground transition-colors"
            >
              See all →
            </Link>
          </div>
        </div>

        {/* Mobile: scroll strip */}
        <div className="md:hidden">
          <ScrollWrap className="v2-events-scroll">
            {upcoming.map((e) => {
              const { month, day } = formatEventDate(e.date);
              return (
                <Link
                  key={e.id}
                  to={`/events/${e.slug || e.id}`}
                  className="group flex-shrink-0 bg-white rounded-xl border overflow-hidden transition-transform hover:-translate-y-0.5"
                  style={{
                    width: 240,
                    minWidth: 240,
                    borderColor: "hsl(var(--rule))",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
                  }}
                >
                  <div
                    className="flex items-center gap-3 px-4 py-3"
                    style={{ borderBottom: "1px solid hsl(var(--rule))" }}
                  >
                    <div className="text-center leading-none" style={{ minWidth: 44 }}>
                      <p className="text-[10px] font-bold tracking-[1px] uppercase" style={{ color: "#A32D2D" }}>{month}</p>
                      <p className="text-[24px] font-extrabold" style={{ color: "#0B1D3A" }}>{day}</p>
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-serif text-[14px] font-bold leading-snug line-clamp-2 group-hover:text-primary transition-colors">{e.title}</h4>
                    </div>
                  </div>
                  <div className="px-4 py-2.5">
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {[e.venue_name, e.city, e.state].filter(Boolean).join(", ")}
                    </p>
                    <div className="flex items-center justify-between mt-1">
                      {e.category && (
                        <span className="text-[10px] font-bold tracking-[1px] uppercase" style={{ color: "#D4A843" }}>{e.category}</span>
                      )}
                      {e._dist !== null && e._dist !== undefined && (
                        <span className="text-[10px] font-semibold" style={{ color: "#6B7280" }}>{formatDistance(e._dist)}</span>
                      )}
                    </div>
                  </div>
                </Link>
              );
            })}
          </ScrollWrap>
        </div>

        {/* Desktop: 4-column grid */}
        <div className="hidden md:grid grid-cols-4 gap-5">
          {upcoming.slice(0, 8).map((e) => {
            const { month, day } = formatEventDate(e.date);
            return (
              <Link
                key={e.id}
                to={`/events/${e.slug || e.id}`}
                className="group bg-white rounded-xl border overflow-hidden transition-transform hover:-translate-y-0.5"
                style={{
                  borderColor: "hsl(var(--rule))",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
                }}
              >
                <div
                  className="flex items-center gap-3 px-4 py-3"
                  style={{ borderBottom: "1px solid hsl(var(--rule))" }}
                >
                  <div className="text-center leading-none" style={{ minWidth: 44 }}>
                    <p className="text-[10px] font-bold tracking-[1px] uppercase" style={{ color: "#A32D2D" }}>{month}</p>
                    <p className="text-[24px] font-extrabold" style={{ color: "#0B1D3A" }}>{day}</p>
                  </div>
                  <div className="min-w-0">
                    <h4 className="font-serif text-[14px] font-bold leading-snug line-clamp-2 group-hover:text-primary transition-colors">{e.title}</h4>
                  </div>
                </div>
                <div className="px-4 py-2.5">
                  <p className="text-xs text-muted-foreground line-clamp-1">
                    {[e.venue_name, e.city, e.state].filter(Boolean).join(", ")}
                  </p>
                  <div className="flex items-center justify-between mt-1">
                    {e.category && (
                      <span className="text-[10px] font-bold tracking-[1px] uppercase" style={{ color: "#D4A843" }}>{e.category}</span>
                    )}
                    {e._dist !== null && e._dist !== undefined && (
                      <span className="text-[10px] font-semibold" style={{ color: "#6B7280" }}>{formatDistance(e._dist)}</span>
                    )}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
