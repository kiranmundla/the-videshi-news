import { Link } from "react-router-dom";
import type { EventItem } from "@/lib/events";
import { formatEventDate } from "@/lib/events";
import { formatDistance } from "@/lib/geo";

/* Shared event card — used by EventsPage and YourHubPage.
   Extracted verbatim from EventsPage.tsx so the hub is a personalized
   *view* into existing content, not a new content format. */

const CAT_EMOJI: Record<string, string> = {
  Cultural: "🎭",
  Music: "🎵",
  Food: "🍛",
  Sports: "🏅",
  Community: "🤝",
  Festival: "🪔",
  Comedy: "😂",
  Dance: "💃",
  Religious: "🙏",
  Education: "🎓",
  Competition: "🏆",
  Entertainment: "🎶",
  Technology: "🚀",
  Shopping: "🛍️",
  Spiritual: "🧘",
  Other: "📌",
};

const CAT_FALLBACK_IMG: Record<string, string> = {
  Cultural: "/images/events/cultural.jpg",
  Music: "/images/events/music.jpg",
  Food: "/images/events/food.jpg",
  Sports: "/images/events/sports.jpg",
  Community: "/images/events/community.jpg",
  Festival: "/images/events/festival.jpg",
  Comedy: "/images/events/comedy.jpg",
  Dance: "/images/events/dance.jpg",
  Religious: "/images/events/religious.jpg",
  Education: "/images/events/education.jpg",
  Competition: "/images/events/competition.jpg",
  Entertainment: "/images/events/entertainment.jpg",
  Technology: "/images/events/technology.jpg",
  Shopping: "/images/events/cultural.jpg",
  Spiritual: "/images/events/religious.jpg",
  Other: "/images/events/other.jpg",
};

function categoryFallbackImg(category?: string | null): string {
  return CAT_FALLBACK_IMG[category || "Other"] || CAT_FALLBACK_IMG["Other"];
}

const CAT_BADGE_COLORS: Record<string, string> = {
  Cultural: "bg-purple-100 text-purple-700",
  Music: "bg-pink-100 text-pink-700",
  Food: "bg-amber-100 text-amber-700",
  Sports: "bg-green-100 text-green-700",
  Community: "bg-blue-100 text-blue-700",
  Festival: "bg-orange-100 text-orange-700",
  Comedy: "bg-yellow-100 text-yellow-700",
  Dance: "bg-fuchsia-100 text-fuchsia-700",
  Religious: "bg-indigo-100 text-indigo-700",
  Education: "bg-teal-100 text-teal-700",
  Competition: "bg-emerald-100 text-emerald-700",
  Entertainment: "bg-pink-100 text-pink-700",
  Technology: "bg-cyan-100 text-cyan-700",
  Shopping: "bg-rose-100 text-rose-700",
  Spiritual: "bg-violet-100 text-violet-700",
  Other: "bg-gray-100 text-gray-700",
};

function CategoryBadge({ category }: { category: string | null }) {
  const cat = category || "Other";
  const color = CAT_BADGE_COLORS[cat] || CAT_BADGE_COLORS.Other;
  const emoji = CAT_EMOJI[cat] || "📌";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {emoji} {cat}
    </span>
  );
}

/** Decode common HTML entities scrapers leave behind */
export function decodeHTMLEntities(text: string): string {
  const el = document.createElement("textarea");
  el.innerHTML = text;
  return el.value;
}

export default function EventCard({ event, distance }: { event: EventItem; distance?: number }) {
  const dateStr = formatEventDate(event.date, event.end_date);
  const location = [event.venue_name, event.city, event.state]
    .filter(Boolean)
    .join(", ");

  const card = (
    <article className="group flex flex-col sm:flex-row bg-card border border-border rounded-lg overflow-hidden hover:border-primary/40 transition-colors w-full box-border" style={{ wordBreak: "break-word" }}>
      {/* Image */}
      {event.image_url ? (
        <div className="w-full sm:w-56 sm:min-w-[14rem] sm:h-auto overflow-hidden flex-shrink-0">
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-auto max-h-64 sm:max-h-none sm:h-full object-contain sm:object-cover bg-muted/10 group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        </div>
      ) : (
        <div className="w-full sm:w-56 sm:min-w-[14rem] sm:h-auto overflow-hidden flex-shrink-0">
          <img
            src={categoryFallbackImg(event.category)}
            alt={event.category || "Event"}
            className="w-full h-auto max-h-64 sm:max-h-none sm:h-full object-cover bg-muted/10 group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        </div>
      )}

      {/* Content */}
      <div className="flex-1 p-4 sm:py-4 sm:pr-4 sm:pl-4 flex flex-col justify-between min-w-0 overflow-hidden">
        <div>
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <CategoryBadge category={event.category} />
            {distance != null && distance < 9999 && (
              <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-orange-600/20 text-orange-300">
                📍 {formatDistance(distance)}
              </span>
            )}
            {event.audience && (
              <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-700">
                👤 {event.audience}
              </span>
            )}
            {event.price_range && (
              <span className="text-xs text-muted-foreground font-medium">
                {event.price_range}
              </span>
            )}
          </div>
          <h3 className="font-serif text-lg font-semibold text-foreground leading-snug mb-1 line-clamp-2 group-hover:text-primary transition-colors">
            {decodeHTMLEntities(event.title)}
          </h3>
          {event.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
              {event.description}
            </p>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground mt-auto pt-2">
          <span className="text-primary font-semibold whitespace-nowrap">
            📅 {dateStr}
            {event.time && ` · ${event.time}`}
          </span>
          {location && (
            <span className="truncate">📍 {location}</span>
          )}
          {event.organizer && (
            <span className="truncate opacity-70">by {event.organizer}</span>
          )}
        </div>
      </div>
    </article>
  );

  const eventSlug = event.slug || event.id;

  return (
    <Link to={`/events/${eventSlug}`} className="block no-underline">
      {card}
    </Link>
  );
}
