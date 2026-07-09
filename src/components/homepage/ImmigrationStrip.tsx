import { useState } from "react";
import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

const IMM_PILLS = ["All", "H-1B", "Green Card", "OPT", "Canada PR", "UK Visas", "Citizenship"];

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

interface Props {
  articles: Article[];
}

export default function ImmigrationStrip({ articles }: Props) {
  const [activePill, setActivePill] = useState("All");

  if (articles.length === 0) return null;

  const filtered =
    activePill === "All"
      ? articles
      : articles.filter((a) => {
          const tags = (a.tags ?? []).map((t) => t.toLowerCase());
          const title = a.title.toLowerCase();
          const needle = activePill.toLowerCase();
          return tags.some((t) => t.includes(needle)) || title.includes(needle);
        });

  const display = filtered.length > 0 ? filtered : articles;

  return (
    <section className="v2-imm-section">
      <div className="container">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <h2 className="flex items-center gap-2 text-[13px] font-bold tracking-[2px] uppercase text-white">
            <span>🛂</span> Immigration
          </h2>
          <Link
            to="/immigration"
            className="text-[13px] font-semibold transition-opacity hover:opacity-80"
            style={{ color: "#D4A843" }}
          >
            See all →
          </Link>
        </div>
        <div className="w-full h-0.5 mb-4" style={{ background: "#D4A843" }} />

        {/* Sub-pills */}
        <div className="v2-imm-pills">
          {IMM_PILLS.map((p) => (
            <button
              key={p}
              onClick={() => setActivePill(p)}
              className={`v2-imm-pill ${activePill === p ? "active" : ""}`}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Cards */}
        <div className="v2-imm-grid">
          {display.slice(0, 4).map((a) => {
            const img = isValidImage(a.hero_image_url);
            return (
              <Link
                key={a.id}
                to={`/articles/${a.slug}`}
                className="v2-imm-card group block"
              >
                <div className="w-full bg-white/[0.08] overflow-hidden" style={{ aspectRatio: "16/10" }}>
                  {img ? (
                    <HeroImage
                      src={a.hero_image_url}
                      alt={a.title}
                      loading="lazy"
                      className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-white/20 text-xs">
                      IMAGE
                    </div>
                  )}
                </div>
                <div className="p-3.5 pb-4">
                  <p
                    className="text-[10px] font-bold tracking-[1.2px] uppercase mb-2"
                    style={{ color: "#D4A843" }}
                  >
                    IMMIGRATION
                  </p>
                  <h3 className="font-serif text-[15px] font-bold leading-snug text-white line-clamp-3">
                    {a.title}
                  </h3>
                  <p className="text-xs mt-2" style={{ color: "rgba(255,255,255,0.5)" }}>
                    {(a as any).reading_time ?? 5} min read · {timeAgo(a.published_at)}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
