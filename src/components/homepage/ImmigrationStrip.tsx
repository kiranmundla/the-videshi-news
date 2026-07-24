import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";
import ScrollWrap from "./ScrollWrap";

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
  if (articles.length === 0) return null;

  return (
    <section className="v2-imm-section">
      <div className="container">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <h2 className="flex items-center gap-2 text-[13px] font-bold tracking-[2px] uppercase text-white">
            <span>🛂</span> Immigration
          </h2>
          <Link
            to="/?cat=immigration"
            className="text-[13px] font-semibold transition-opacity hover:opacity-80"
            style={{ color: "#D4A843" }}
          >
            See all →
          </Link>
        </div>
        <div className="w-full h-0.5 mb-4" style={{ background: "#D4A843" }} />

        {/* Quick-access tools */}
        <div className="flex flex-wrap gap-2 mb-4">
          {[
            { to: "/immigration/green-card", icon: "📊", label: "Green Card Tracker" },
            { to: "/immigration/visas", icon: "🔍", label: "Visa Bulletin" },
            { to: "/immigration/consulate-wait-times", icon: "🏛️", label: "Wait Times" },
            { to: "/immigration/h1b", icon: "💼", label: "H-1B Hub" },
            { to: "/immigration/guides", icon: "📖", label: "Guides" },
          ].map((t) => (
            <Link
              key={t.to}
              to={t.to}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[12px] font-semibold transition-all hover:scale-[1.03]"
              style={{
                background: "rgba(212, 168, 67, 0.15)",
                color: "#D4A843",
                border: "1px solid rgba(212, 168, 67, 0.3)",
              }}
            >
              <span>{t.icon}</span> {t.label}
            </Link>
          ))}
        </div>

        {/* Cards — mobile: horizontal scroll with arrows; desktop: 4-col grid */}
        <div className="md:hidden">
          <ScrollWrap className="v2-imm-scroll" arrowVariant="dark">
            {articles.map((a) => {
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
                        focalX={a.focal_x}
                        focalY={a.focal_y}
                        className="w-full h-full object-contain group-hover:scale-[1.02] transition-transform duration-300"
                      />
                    ) : null}
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
          </ScrollWrap>
        </div>

        <div className="hidden md:grid grid-cols-4 gap-5">
          {articles.slice(0, 8).map((a) => {
            const img = isValidImage(a.hero_image_url);
            return (
              <Link
                key={a.id}
                to={`/articles/${a.slug}`}
                className="group block rounded-xl overflow-hidden"
                style={{ background: "rgba(255,255,255,0.05)" }}
              >
                <div className="w-full bg-white/[0.08] overflow-hidden" style={{ aspectRatio: "16/10" }}>
                  {img ? (
                    <HeroImage
                      src={a.hero_image_url}
                      alt={a.title}
                      loading="lazy"
                      focalX={a.focal_x}
                      focalY={a.focal_y}
                      className="w-full h-full object-contain group-hover:scale-[1.02] transition-transform duration-300"
                    />
                  ) : null}
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
