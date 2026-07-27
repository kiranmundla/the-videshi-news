import { Link } from "react-router-dom";

const HUB_TILES = [
  {
    label: "News",
    to: "/",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 4h12v16H4z"/>
        <path d="M16 8h3v12H7"/>
        <line x1="7" y1="8" x2="13" y2="8"/>
        <line x1="7" y1="11" x2="13" y2="11"/>
        <line x1="7" y1="14" x2="10" y2="14"/>
      </svg>
    ),
  },
  {
    label: "Directory",
    to: "/directory",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
        <line x1="10" y1="8" x2="14" y2="8"/>
        <line x1="10" y1="10.5" x2="14" y2="10.5"/>
      </svg>
    ),
  },
  {
    label: "Events",
    to: "/events",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <line x1="3" y1="9" x2="21" y2="9"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <polygon points="12,12 13.1,14.3 15.6,14.6 13.8,16.3 14.2,18.8 12,17.6 9.8,18.8 10.2,16.3 8.4,14.6 10.9,14.3" fill="#fff" stroke="none"/>
      </svg>
    ),
  },
  {
    label: "Classifieds",
    to: "/classifieds",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>
        <circle cx="7" cy="7" r="1.5" fill="#fff"/>
        <line x1="11" y1="11" x2="15" y2="15"/>
        <line x1="11" y1="15" x2="15" y2="11"/>
      </svg>
    ),
  },
  {
    label: "Voices",
    to: "/stories",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/>
        <circle cx="8.5" cy="11.5" r="0.8" fill="#fff"/>
        <circle cx="12" cy="11.5" r="0.8" fill="#fff"/>
        <circle cx="15.5" cy="11.5" r="0.8" fill="#fff"/>
      </svg>
    ),
  },
];

export default function HubStrip() {
  /* Skip "News" on desktop — user is already on the news site */
  const desktopTiles = HUB_TILES.filter((t) => t.to !== "/");

  return (
    <>
      {/* Mobile: circular icon grid */}
      <nav className="v2-hub-strip v2-hub-strip-mobile md:hidden">
        {HUB_TILES.map((t) => (
          <Link key={t.label} to={t.to} className="v2-hub-tile">
            <div className="v2-hub-icon-wrap">
              <span className="v2-hub-dot" />
              {t.icon}
            </div>
            <span className="v2-hub-label">{t.label}</span>
          </Link>
        ))}
      </nav>

      {/* Desktop: compact text links with icons */}
      <nav className="hidden md:block" style={{ borderBottom: "1px solid hsl(var(--rule) / 0.4)" }}>
        <div className="container flex items-center gap-1 py-1.5">
          {desktopTiles.map((t, i) => (
            <Link
              key={t.label}
              to={t.to}
              className="flex items-center gap-1.5 px-3 py-1 rounded-md text-xs tracking-wide text-muted-foreground hover:text-foreground hover:bg-foreground/5 transition-colors"
            >
              <span className="w-3.5 h-3.5 opacity-60" style={{ display: "inline-flex" }}>
                {/* Re-stroke in currentColor for desktop */}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: "100%", height: "100%" }}>
                  {t.to === "/directory" && <><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><line x1="10" y1="8" x2="14" y2="8"/><line x1="10" y1="10.5" x2="14" y2="10.5"/></>}
                  {t.to === "/events" && <><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="16" y1="2" x2="16" y2="6"/></>}
                  {t.to === "/classifieds" && <><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><circle cx="7" cy="7" r="1.5" fill="currentColor"/></>}
                  {t.to === "/stories" && <><path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/></>}
                </svg>
              </span>
              <span className="smallcaps" style={{ fontSize: "0.65rem" }}>{t.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </>
  );
}
