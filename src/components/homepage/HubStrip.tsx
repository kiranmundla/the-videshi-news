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
  {
    label: "Learn",
    to: "/kids",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
        <path d="M6 12v5c0 1.66 2.69 3 6 3s6-1.34 6-3v-5"/>
      </svg>
    ),
  },
];

export default function HubStrip() {
  return (
    <nav className="v2-hub-strip">
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
  );
}
