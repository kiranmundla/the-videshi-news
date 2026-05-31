import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";
import { optimizeImageUrl, IMAGE_SIZES } from "@/lib/imageUrl";

function getImageOrientation(url: string | null | undefined): 'landscape' | 'portrait' | null {
  if (!url) return null;
  try {
    const params = new URL(url).searchParams;
    const w = parseInt(params.get('w') || '');
    const h = parseInt(params.get('h') || '');
    if (w > 0 && h > 0) {
      return (w / h) > 1.2 ? 'landscape' : 'portrait';
    }
  } catch {}
  return null;
}

export default function EventCluster({
  label,
  items,
}: {
  label: string;
  items: Article[];
}) {
  if (items.length < 2) return null;
  const [lead, ...rest] = items;
  const sub = rest.slice(0, 2);
  const leadHasImg = isValidImage(lead.hero_image_url);

  return (
    <section
      className="border-l-4 mb-8 px-5 md:px-7 py-5 md:py-6"
      style={{ background: "#FFF8F7", borderLeftColor: "hsl(var(--primary))" }}
    >
      <p
        className="font-bold mb-4"
        style={{
          color: "hsl(var(--primary))",
          fontSize: 11,
          letterSpacing: "0.15em",
          textTransform: "uppercase",
        }}
      >
        {label}
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-7">
        <Link to={`/articles/${lead.slug}`} className="group block">
          {leadHasImg && (
            <div className={`w-full overflow-hidden mb-3 bg-muted ${getImageOrientation(lead.hero_image_url) === 'portrait' ? 'max-w-[200px] aspect-[3/4]' : 'aspect-[16/9]'}`}>
              <img
                src={optimizeImageUrl(lead.hero_image_url, IMAGE_SIZES.card)}
                alt={lead.title}
                loading="lazy"
                referrerPolicy="no-referrer"
                className="w-full h-full object-cover"
                style={{ objectPosition: "center" }}
              />
            </div>
          )}
          <h3
            className="font-display font-bold text-[20px] md:text-[26px] leading-snug text-foreground group-hover:text-primary transition-colors"
            style={{ fontWeight: 800 }}
          >
            {lead.title}
          </h3>
          {lead.excerpt && (
            <p className="font-body-serif mt-2 text-foreground/75 text-sm line-clamp-2">
              {lead.excerpt}
            </p>
          )}
        </Link>
        <div className="flex flex-col gap-4">
          {sub.map((a) => (
            <Link
              key={a.id}
              to={`/articles/${a.slug}`}
              className="group block border-t border-rule/60 pt-3 first:border-t-0 first:pt-0"
            >
              <h4
                className="font-display font-bold text-[16px] md:text-[18px] leading-snug text-foreground group-hover:text-primary transition-colors"
                style={{ fontWeight: 700 }}
              >
                {a.title}
              </h4>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
