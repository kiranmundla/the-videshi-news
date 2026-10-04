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
    <section className="mb-10">
      <div className="container">
        <div
          className="rounded-2xl overflow-hidden border border-[#0B1D3A]/10"
          style={{ background: "linear-gradient(135deg, #0B1D3A 0%, #132E57 100%)" }}
        >
          <div className="p-5 md:p-6">
            <p className="text-[11px] uppercase tracking-[0.2em] text-[#D4A843] font-semibold mb-1">
              Explore
            </p>
            <h2 className="text-xl md:text-2xl font-bold text-white mb-4">
              Plan your next move
            </h2>

            <div className="flex gap-2 mb-4" role="tablist" aria-label="Explore sections">
              {tabs.map((t) => (
                <button
                  key={t.key}
                  role="tab"
                  aria-selected={tab === t.key}
                  onClick={() => setTab(t.key)}
                  className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-colors ${
                    tab === t.key
                      ? "bg-[#D4A843] text-[#0B1D3A]"
                      : "bg-white/10 text-white/70 hover:bg-white/15"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {tab === "destinations" && (
              <div>
                <div className="flex gap-3 overflow-x-auto pb-1 -mx-5 px-5 md:mx-0 md:px-0" style={{ scrollbarWidth: "none" }}>
                  {DESTINATIONS.slice(0, 12).map((d) => (
                    <Link
                      key={d.key}
                      to={`/travel/${d.key}`}
                      className="shrink-0 w-36 rounded-xl overflow-hidden bg-white/5 border border-white/10 hover:border-[#D4A843]/50 transition-colors"
                    >
                      <div className={`h-20 bg-gradient-to-br ${gradientFor(d.key)} flex items-end p-2`}>
                        <span className="text-white text-xs font-bold drop-shadow">{d.label}</span>
                      </div>
                      <div className="p-2">
                        <p className="text-[11px] text-white/50 truncate">{d.bestMonths} · {d.budget}</p>
                      </div>
                    </Link>
                  ))}
                  <Link
                    to="/travel"
                    className="shrink-0 w-36 rounded-xl overflow-hidden bg-[#D4A843]/10 border border-[#D4A843]/30 flex flex-col items-center justify-center gap-1 p-2"
                  >
                    <span className="text-[#D4A843] text-sm font-bold">+ {DESTINATIONS.length - 12} more</span>
                    <span className="text-[11px] text-white/50">View all →</span>
                  </Link>
                </div>
              </div>
            )}

            {tab === "guides" && (
              <div>
                {guides.length === 0 ? (
                  <div className="flex gap-3 overflow-x-auto pb-1">
                    {[0, 1, 2].map((i) => (
                      <div key={i} className="shrink-0 w-56 h-24 rounded-xl bg-white/5 border border-white/10 animate-pulse" />
                    ))}
                  </div>
                ) : (
                  <div className="flex gap-3 overflow-x-auto pb-1 -mx-5 px-5 md:mx-0 md:px-0" style={{ scrollbarWidth: "none" }}>
                    {guides.slice(0, 10).map((g) => (
                      <Link
                        key={g.slug}
                        to={`/immigration/guides/${g.slug}`}
                        className="shrink-0 w-56 rounded-xl bg-white/5 border border-white/10 p-3 hover:border-[#D4A843]/50 transition-colors"
                      >
                        <p className="text-[10px] uppercase tracking-wider text-[#D4A843] font-semibold truncate">{g.category}</p>
                        <p className="text-sm font-bold text-white mt-0.5 line-clamp-2">{g.title}</p>
                        {g.reading_time_min ? (
                          <p className="text-[11px] text-white/40 mt-1">{g.reading_time_min} min read</p>
                        ) : null}
                      </Link>
                    ))}
                    <Link
                      to="/immigration/guides"
                      className="shrink-0 w-40 rounded-xl bg-[#D4A843]/10 border border-[#D4A843]/30 flex flex-col items-center justify-center gap-1 p-3"
                    >
                      <span className="text-[#D4A843] text-sm font-bold">All {guides.length} guides</span>
                      <span className="text-[11px] text-white/50">View all →</span>
                    </Link>
                  </div>
                )}
              </div>
            )}

            {tab === "trackers" && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {TRACKERS.map((t) => (
                  <Link
                    key={t.label}
                    to={t.to}
                    className="rounded-xl bg-white/5 border border-white/10 p-3 hover:border-[#D4A843]/50 transition-colors"
                  >
                    <p className="text-sm font-bold text-white">{t.label}</p>
                    <p className="text-[11px] text-white/40 mt-0.5">{t.desc}</p>
                  </Link>
                ))}
              </div>
            )}
          </div>
          <div className="h-1" style={{ background: "linear-gradient(90deg, #D4A843, #A32D2F)" }} />
        </div>
      </div>
    </section>
  );
}
