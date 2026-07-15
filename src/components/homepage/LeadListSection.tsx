import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

interface Props {
  title: string;
  borderColor: string;
  categorySlug: string;
  articles: Article[];
  listCount?: number;
}

function adaptiveImageStyle(
  imgW?: number | null,
  imgH?: number | null,
): { aspectRatio: string; useContain: boolean } {
  if (!imgW || !imgH || imgW <= 0 || imgH <= 0) {
    return { aspectRatio: "3/2", useContain: false };
  }
  const natural = imgW / imgH;
  const isPortrait = natural < 0.9;
  if (isPortrait) {
    return { aspectRatio: "4/3", useContain: true };
  }
  const clamped = Math.min(Math.max(natural, 1.0), 2.0);
  return { aspectRatio: `${clamped.toFixed(3)}`, useContain: false };
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

export default function LeadListSection({ title, borderColor, categorySlug, articles, listCount = 3 }: Props) {
  if (articles.length === 0) return null;

  const [lead, ...rest] = articles;
  const list = rest.slice(0, listCount);
  const hasMore = rest.length > listCount;
  const hasLeadImage = isValidImage(lead.hero_image_url);
  const rt = (lead as any).reading_time ?? 5;
  const { aspectRatio: leadRatio, useContain: leadContain } = adaptiveImageStyle(lead.img_w, lead.img_h);

  return (
    <section className="mb-14">
      <div className="container">
        {/* Section header */}
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: `3px solid ${borderColor}` }}
        >
          <h2 className="text-[13px] font-bold tracking-[2px] uppercase" style={{ color: "#0B1D3A" }}>
            {title}
          </h2>
          <Link
            to={`/?cat=${categorySlug}`}
            className="text-[13px] font-semibold text-muted-foreground hover:text-foreground transition-colors"
          >
            See all →
          </Link>
        </div>

        {/* Lead + list grid */}
        <div className="grid grid-cols-1 md:grid-cols-[3fr_2fr] gap-8 items-start">
          {/* Lead card */}
          <Link to={`/articles/${lead.slug}`} className="group block">
            {hasLeadImage && (
              <div
                className={`w-full bg-stone-200 overflow-hidden rounded-lg mb-3.5 ${leadContain ? "flex items-center justify-center" : ""}`}
                style={{ aspectRatio: leadRatio, maxHeight: "500px" }}
              >
                <HeroImage
                  src={lead.hero_image_url}
                  alt={lead.title}
                  loading="lazy"
                  focalX={leadContain ? undefined : lead.focal_x}
                  focalY={leadContain ? undefined : lead.focal_y}
                  className={`${leadContain ? "max-w-full max-h-full w-auto h-auto" : "w-full h-full object-cover"} group-hover:scale-[1.01] transition-transform duration-500`}
                />
              </div>
            )}
            <p
              className="text-[11px] font-bold tracking-[1.2px] uppercase mb-1.5"
              style={{ color: borderColor }}
            >
              {lead.category?.replace("-", " ")}
            </p>
            <h3 className="font-serif text-[22px] font-extrabold leading-[1.25] mb-2 group-hover:text-primary transition-colors">
              {lead.title}
            </h3>
            {lead.excerpt && (
              <p className="text-sm text-muted-foreground leading-relaxed line-clamp-2 mb-1.5">
                {lead.excerpt}
              </p>
            )}
            <p className="text-xs text-muted-foreground">
              {rt} min read · {timeAgo(lead.published_at)}
            </p>
          </Link>

          {/* List stack */}
          <div className="flex flex-col">
            {list.map((a, i) => {
              const img = isValidImage(a.hero_image_url);
              return (
                <Link
                  key={a.id}
                  to={`/articles/${a.slug}`}
                  className="group flex gap-3.5 py-3.5 border-b last:border-b-0 hover:bg-stone-50 transition-colors rounded"
                  style={{ borderColor: "hsl(var(--rule))" }}
                >
                  {img && (
                    <div className="w-[72px] min-w-[72px] h-[72px] bg-stone-100 rounded overflow-hidden">
                      <HeroImage
                        src={a.hero_image_url}
                        alt={a.title}
                        loading="lazy"
                        focalX={a.focal_x}
                        focalY={a.focal_y}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-[10px] font-bold tracking-[1.2px] uppercase mb-1"
                      style={{ color: borderColor }}
                    >
                      {a.category?.replace("-", " ")}
                    </p>
                    <h4 className="font-serif text-[15px] font-bold leading-snug group-hover:text-primary transition-colors line-clamp-2">
                      {a.title}
                    </h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      {timeAgo(a.published_at)}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* View all link at bottom */}
        <div className="text-center mt-6">
          <Link
            to={`/?cat=${categorySlug}`}
            className="inline-block text-[13px] font-semibold tracking-wide uppercase hover:opacity-80 transition-opacity"
            style={{ color: borderColor }}
          >
            View all {title} →
          </Link>
        </div>
      </div>
    </section>
  );
}
