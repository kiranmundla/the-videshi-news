import { Link } from "react-router-dom";

const HUB_TILES = [
  { label: "News", to: "/", icon: "/icons/hub/news.png" },
  { label: "Directory", to: "/directory", icon: "/icons/hub/directory.png" },
  { label: "Events", to: "/events", icon: "/icons/hub/events.png" },
  { label: "Classifieds", to: "/classifieds", icon: "/icons/hub/classifieds.png" },
  { label: "Voices", to: "/stories", icon: "/icons/hub/voices.png" },
];

export default function HubStrip() {
  return (
    <nav className="v2-hub-strip">
      {HUB_TILES.map((t) => (
        <Link key={t.label} to={t.to} className="v2-hub-tile">
          <img
            src={t.icon}
            alt={t.label}
            className="v2-hub-icon"
            width={60}
            height={60}
            loading="eager"
          />
          <span className="v2-hub-label">{t.label}</span>
        </Link>
      ))}
    </nav>
  );
}
