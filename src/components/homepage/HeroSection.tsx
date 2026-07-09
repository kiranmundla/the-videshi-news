import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

const CATEGORY_COLORS: Record<string, string> = {
  immigration: "#D4A843",
  technology: "#4527A0",
  entertainment: "#AD1457",
  "markets-finance": "#E65100",
  sports: "#2E7D32",
  "nri-world": "#1565C0",
  news: "#C62828",
};

function catColor(cat?: string) {
  return CATEGORY_COLORS[cat?.toLowerCase() ?? ""] ?? "#C62828";
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

interface Props {
  lead: Article | null;
  side: Article[];
}

export default function HeroSection({ lead, side }: Props) {
  if (!lead) return null;

  const hasImage = isValidImage(lead.hero_image_url);
  const rt = (lead as any).reading_time ?? 5;

  return (
    <section className="pt-8 md:pt-10">
      <div className="container">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-7">
          {/* Lead article */}
          <Link to={`/articles/${lead.slug}`} className="group block">
            {hasImage && (
              <div className="w-full aspect-[16/10] bg-stone-100 overflow-hidden rounded-lg mb-4">
                <HeroImage
                  src={lead.hero_image_url}
                  alt={lead.title}
                  loading="eager"
                  fetchPriority="high"
                  className="w-full h-full object-cover group-hover:scale-[1.01] transition-transform duration-500"
                  width="800"
                  height="500"
                  style={{ objectPosition: "center 20%" }}
                />
              </div>
            )}
            <p
              className="text-[11px] font-bold tracking-[1.2px] uppercase mb-1.5"
              style={{ color: catColor(lead.category) }}
            >
              {lead.category?.replace("-", " ")}
            </p>
            <h1
              className="font-serif font-extrabold leading-[1.2] mb-2.5 group-hover:text-primary transition-colors"
              style={{ fontSize: "clamp(22px, 3vw, 32px)", color: "#0B1D3A" }}
            >
              {lead.title}
            </h1>
            {lead.excerpt && (
              <p className="text-base text-foreground/65 leading-relaxed line-clamp-2 mb-2">
                {lead.excerpt}
              </p>
            )}
            <p className="text-xs text-muted-foreground">
              {lead.author ? `By ${lead.author} · ` : ""}
              {rt} min read · {timeAgo(lead.published_at)}
            </p>
          </Link>

          {/* Side articles */}
          <div className="flex flex-col gap-4">
            {side.slice(0, 3).map((a) => {
              const img = isValidImage(a.hero_image_url);
              return (
                <Link
                  key={a.id}
                  to={`/articles/${a.slug}`}
                  className="group flex gap-3.5 pb-4 border-b last:border-b-0 last:pb-0 transition-transform hover:translate-x-0.5"
                  style={{ borderColor: "hsl(var(--rule))" }}
                >
                  {img && (
                    <div className="w-[120px] min-w-[120px] aspect-[4/3] bg-stone-100 rounded overflow-hidden">
                      <HeroImage
                        src={a.hero_image_url}
                        alt={a.title}
                        loading="lazy"
                        className="w-full h-full object-cover"
                        width="120"
                        height="90"
                      />
                    </div>
                  )}
                  <div className="min-w-0">
                    <p
                      className="text-[10px] font-bold tracking-[1.2px] uppercase mb-1"
                      style={{ color: catColor(a.category) }}
                    >
                      {a.category?.replace("-", " ")}
                    </p>
                    <h3 className="font-serif text-base font-bold leading-snug group-hover:text-primary transition-colors line-clamp-3">
                      {a.title}
                    </h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      {timeAgo(a.published_at)}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
