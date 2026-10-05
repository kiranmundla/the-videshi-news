import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { DESTINATIONS } from "@/lib/travel";
import { getImmigrationGuides, type ImmigrationGuide } from "@/lib/immigration";

type Tab = "destinations" | "guides" | "trackers";

/* Deterministic gradient per destination key (no images needed) */
const GRADIENTS = [
  "from-orange-400 to-pink-600",
  "from-teal-400 to-blue-600",
  "from-amber-400 to-orange-600",
  "from-cyan-400 to-teal-600",
  "from-indigo-400 to-purple-600",
  "from-emerald-400 to-green-600",
  "from-rose-400 to-red-600",
  "from-sky-400 to-indigo-600",
];
function gradientFor(key: string) {
  let h = 0;
  for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) >>> 0;
  return GRADIENTS[h % GRADIENTS.length];
}

const TRACKERS = [
  { label: "Visa Bulletin", desc: "Monthly cutoff dates", to: "/immigration" },
  { label: "Green Card Tracker", desc: "Wait times by category", to: "/immigration" },
  { label: "H-1B Hub", desc: "Lottery & stamping", to: "/immigration" },
  { label: "Remittance", desc: "Dollar to rupee", to: "/markets-finance" },
];

export default function ExploreHub() {
  const [tab, setTab] = useState<Tab>("destinations");
  const [guides, setGuides] = useState<ImmigrationGuide[]>([]);

  useEffect(() => {
    if (tab === "guides" && guides.length === 0) {
      getImmigrationGuides().then(setGuides).catch(() => {});
    }
  }, [tab, guides.length]);

  const tabs: { key: Tab; label: string }[] = [
    { key: "destinations", label: "Destinations" },
    { key: "guides", label: "Visa Guides" },
    { key: "trackers", label: "Trackers" },
  ];

  return (
    <section className="mb-14">
      <div className="container">
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #D4A843" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            Explore
          </h2>
          <span className="text-[11px] text-muted-foreground">
            Plan your next move
          </span>
        </div>

        <div className="flex gap-2 mb-5" role="tablist" aria-label="Explore sections">
          {tabs.map((t) => (
            <button
              key={t.key}
              role="tab"
              aria-selected={tab === t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-colors border ${
                tab === t.key
                  ? "bg-[#0B1D3A] text-white border-[#0B1D3A]"
                  : "bg-transparent text-muted-foreground border-border hover:border-[#0B1D3A]/40"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === "destinations" && (
          <div className="flex gap-5 overflow-x-auto pb-2 -mx-1 px-1">
            {DESTINATIONS.slice(0, 12).map((d) => (
              <Link
                key={d.key}
                to={`/travel/${d.key}`}
                className="group shrink-0 w-40 md:w-44"
              >
                <div className={`relative w-40 md:w-44 aspect-[4/3] rounded-lg overflow-hidden bg-gradient-to-br ${gradientFor(d.key)}`}>
                  <img
                    src={d.image}
                    alt={d.label}
                    loading="lazy"
                    className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-transparent to-transparent pointer-events-none" />
                  <span className="absolute bottom-2 left-2 right-2 text-white text-sm font-bold drop-shadow leading-tight">
                    {d.label}
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground mt-1.5">
                  {d.bestMonths} · {d.budget}
                </p>
              </Link>
            ))}
            <Link
              to="/travel"
              className="group shrink-0 w-40 md:w-44 flex flex-col items-center justify-center aspect-[4/3] rounded-lg border border-dashed border-[#0B1D3A]/30 hover:border-[#D4A843] transition-colors"
            >
              <span className="text-sm font-bold" style={{ color: "#0B1D3A" }}>
                + {DESTINATIONS.length - 12} more
              </span>
              <span className="text-[11px] text-muted-foreground">View all →</span>
            </Link>
          </div>
        )}

        {tab === "guides" && (
          <div>
            {guides.length === 0 ? (
              <div className="flex gap-5 overflow-x-auto pb-2">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="shrink-0 w-56 h-24 rounded-lg bg-muted animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="flex gap-5 overflow-x-auto pb-2 -mx-1 px-1">
                {guides.slice(0, 10).map((g) => (
                  <Link
                    key={g.slug}
                    to={`/immigration/guides/${g.slug}`}
                    className="group shrink-0 w-56 rounded-lg border border-border p-3 hover:border-[#D4A843] transition-colors bg-card"
                  >
                    <p className="text-[10px] uppercase tracking-wider text-[#A32D2F] font-semibold truncate">{g.category}</p>
                    <p className="font-serif text-[0.95rem] font-bold mt-0.5 line-clamp-2 leading-snug group-hover:text-primary transition-colors">{g.title}</p>
                    {g.reading_time_min ? (
                      <p className="text-[11px] text-muted-foreground mt-1">{g.reading_time_min} min read</p>
                    ) : null}
                  </Link>
                ))}
                <Link
                  to="/immigration/guides"
                  className="shrink-0 w-40 rounded-lg border border-dashed border-[#0B1D3A]/30 hover:border-[#D4A843] transition-colors flex flex-col items-center justify-center p-3"
                >
                  <span className="text-sm font-bold" style={{ color: "#0B1D3A" }}>All {guides.length} guides</span>
                  <span className="text-[11px] text-muted-foreground">View all →</span>
                </Link>
              </div>
            )}
          </div>
        )}

        {tab === "trackers" && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {TRACKERS.map((t) => (
              <Link
                key={t.label}
                to={t.to}
                className="rounded-lg border border-border p-3 hover:border-[#D4A843] transition-colors bg-card group"
              >
                <p className="font-serif font-bold text-[0.95rem] group-hover:text-primary transition-colors" style={{ color: "#0B1D3A" }}>{t.label}</p>
                <p className="text-[11px] text-muted-foreground mt-0.5">{t.desc}</p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
