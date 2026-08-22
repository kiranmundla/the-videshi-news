import { Link } from "react-router-dom";

interface InterviewArticle {
  id: string;
  slug: string;
  title: string;
  excerpt?: string;
  hero_image_url?: string;
  image_caption?: string;
  published_at?: string;
  reading_time?: number;
  tags?: string[];
}

interface Props {
  articles: InterviewArticle[];
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return "yesterday";
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export default function InterviewSpotlight({ articles }: Props) {
  if (!articles || articles.length === 0) return null;

  const lead = articles[0];

  return (
    <section className="mb-14">
      <div className="container">
        {/* Header */}
        <div
          className="flex items-center justify-between mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #D4A843" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            ✦ Exclusive Interview
          </h2>
        </div>

        {/* Featured interview card */}
        <Link
          to={`/article/${lead.slug}`}
          className="group block overflow-hidden rounded-xl border transition-shadow hover:shadow-lg"
          style={{
            borderColor: "hsl(var(--rule))",
            background: "linear-gradient(135deg, #0B1D3A 0%, #152a4a 100%)",
          }}
        >
          <div className="md:flex">
            {/* Image */}
            {lead.hero_image_url && (
              <div className="md:w-2/5 overflow-hidden">
                <img
                  src={lead.hero_image_url}
                  alt={lead.image_caption || lead.title}
                  className="w-full h-56 md:h-full object-cover object-top transition-transform duration-500 group-hover:scale-[1.03]"
                  loading="lazy"
                />
              </div>
            )}

            {/* Content */}
            <div className={`p-6 md:p-8 flex flex-col justify-center ${lead.hero_image_url ? "md:w-3/5" : "w-full"}`}>
              <span
                className="inline-block text-[10px] font-bold tracking-[2px] uppercase mb-3 px-2.5 py-1 rounded-sm w-fit"
                style={{ background: "rgba(212,168,67,0.15)", color: "#D4A843" }}
              >
                The Videshi Interview
              </span>

              <h3
                className="font-serif text-xl md:text-2xl font-bold leading-snug mb-3 group-hover:text-[#D4A843] transition-colors"
                style={{ color: "#ffffff" }}
              >
                {lead.title}
              </h3>

              {lead.excerpt && (
                <p
                  className="text-sm md:text-[15px] leading-relaxed mb-4 line-clamp-3"
                  style={{ color: "rgba(255,255,255,0.7)" }}
                >
                  {lead.excerpt}
                </p>
              )}

              <div className="flex items-center gap-3 mt-auto">
                <span
                  className="text-[12px] font-semibold tracking-wide uppercase"
                  style={{ color: "#D4A843" }}
                >
                  Read interview →
                </span>
                {lead.published_at && (
                  <span className="text-[11px]" style={{ color: "rgba(255,255,255,0.4)" }}>
                    {timeAgo(lead.published_at)}
                  </span>
                )}
                {lead.reading_time && lead.reading_time > 1 && (
                  <span className="text-[11px]" style={{ color: "rgba(255,255,255,0.4)" }}>
                    · {lead.reading_time} min read
                  </span>
                )}
              </div>
            </div>
          </div>
        </Link>

        {/* Additional interviews (if more than one) */}
        {articles.length > 1 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {articles.slice(1, 3).map((a) => (
              <Link
                key={a.id}
                to={`/article/${a.slug}`}
                className="group flex gap-4 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow"
                style={{ borderColor: "hsl(var(--rule))" }}
              >
                {a.hero_image_url && (
                  <img
                    src={a.hero_image_url}
                    alt={a.title}
                    className="w-20 h-20 rounded-lg object-cover flex-shrink-0"
                    loading="lazy"
                  />
                )}
                <div className="min-w-0">
                  <h4 className="font-serif text-sm font-bold leading-snug line-clamp-2 group-hover:text-primary transition-colors">
                    {a.title}
                  </h4>
                  {a.published_at && (
                    <span className="text-[11px] text-muted-foreground mt-1 block">
                      {timeAgo(a.published_at)}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
