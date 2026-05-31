import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { readingTime } from "@/lib/articles";
import { isValidImage } from "@/components/HeroImage";

type EditorialArticle = {
  id: string;
  slug: string;
  headline: string;
  subheadline: string | null;
  body: string;
  category: string | null;
  image_url: string | null;
  image_caption: string | null;
  published_at: string | null;
};

const GOLD = "#d4a855";

async function fetchLatestEditorial(): Promise<EditorialArticle | null> {
  try {
    const resp = await fetch("/data/homepage-feed.json");
    if (!resp.ok) return null;
    const feed = await resp.json();
    const ed = feed.editorial;
    if (!ed) return null;
    return {
      id: ed.id,
      slug: ed.slug,
      headline: ed.title || "",
      subheadline: ed.excerpt || null,
      body: ed.body || "",
      category: ed.category || null,
      image_url: ed.hero_image_url || null,
      image_caption: ed.image_caption || null,
      published_at: ed.published_at || null,
    };
  } catch {
    return null;
  }
}

export default function EditorsDesk() {
  const [article, setArticle] = useState<EditorialArticle | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetchLatestEditorial()
      .then((a) => setArticle(a))
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  // Render nothing until loaded, and nothing if no editorial exists
  if (!loaded || !article) return null;

  const href = `/articles/${article.slug ?? article.id}`;
  const hasImage = isValidImage(article.image_url);
  const minutes = readingTime(article.body);
  const excerpt =
    article.subheadline?.trim() ||
    (article.body ?? "")
      .replace(/[#*_>`~\-\[\]{}]+/g, "")
      .trim()
      .slice(0, 200)
      .trimEnd() + "…";

  // ── With hero image: cinematic background ────────────────────────
  if (hasImage) {
    return (
      <section className="relative w-full overflow-hidden rounded-lg mb-10">
        {/* Background image */}
        <img
          src={article.image_url!}
          alt={article.headline}
          loading="eager"
          referrerPolicy="no-referrer"
          className="w-full h-auto block"
          style={{
            minHeight: "260px",
            maxHeight: "520px",
            objectFit: "cover",
            objectPosition: "center 20%",
          }}
        />

        {/* Gradient overlay */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(to top, rgba(20,20,30,0.92) 0%, rgba(20,20,30,0.6) 45%, rgba(20,20,30,0.15) 100%)",
          }}
        />

        {/* Gold top accent */}
        <div
          className="absolute top-0 inset-x-0"
          style={{ height: 3, background: GOLD }}
        />

        {/* Content */}
        <div className="absolute inset-x-0 bottom-0 px-5 md:px-12 pb-6 md:pb-10 pt-4">
          {/* Label + read time row */}
          <div className="flex items-center gap-3 mb-3 flex-wrap">
            <span
              className="inline-block px-2.5 py-1 text-[10px] font-bold tracking-[0.18em] uppercase"
              style={{
                color: "#1a1a2e",
                background: GOLD,
                borderRadius: 2,
                fontFamily: "Inter, sans-serif",
              }}
            >
              EDITOR'S DESK
            </span>
            <span
              className="text-[11px] font-medium tracking-wide"
              style={{ color: "rgba(255,255,255,0.65)", fontFamily: "Inter, sans-serif" }}
            >
              {minutes} min read
            </span>
          </div>

          <Link to={href} className="block max-w-4xl group">
            <h2
              className="font-display text-white leading-[1.12] group-hover:underline"
              style={{ fontWeight: 800, fontSize: "clamp(22px, 3.8vw, 36px)" }}
            >
              {article.headline}
            </h2>
            <p
              className="font-body-serif mt-2.5 text-sm md:text-base max-w-3xl line-clamp-2"
              style={{ color: "rgba(255,255,255,0.8)" }}
            >
              {excerpt}
            </p>
            <span
              className="inline-block mt-3 text-xs font-semibold tracking-[0.1em] uppercase group-hover:underline"
              style={{ color: GOLD, fontFamily: "Inter, sans-serif" }}
            >
              Read the full story →
            </span>
          </Link>
        </div>
      </section>
    );
  }

  // ── Without image: dark panel ──────────────────────────────────
  return (
    <section
      className="relative w-full overflow-hidden rounded-lg mb-10 px-6 md:px-12 py-8 md:py-12"
      style={{ background: "#1C1C1E" }}
    >
      {/* Gold top accent */}
      <div
        className="absolute top-0 inset-x-0"
        style={{ height: 3, background: GOLD }}
      />

      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <span
          className="inline-block px-2.5 py-1 text-[10px] font-bold tracking-[0.18em] uppercase"
          style={{
            color: "#1a1a2e",
            background: GOLD,
            borderRadius: 2,
            fontFamily: "Inter, sans-serif",
          }}
        >
          EDITOR'S DESK
        </span>
        <span
          className="text-[11px] font-medium tracking-wide"
          style={{ color: "rgba(255,255,255,0.55)", fontFamily: "Inter, sans-serif" }}
        >
          {minutes} min read
        </span>
      </div>

      <Link to={href} className="block max-w-4xl group">
        <h2
          className="font-display text-white leading-[1.12] group-hover:underline"
          style={{ fontWeight: 800, fontSize: "clamp(22px, 3.8vw, 36px)" }}
        >
          {article.headline}
        </h2>
        <p
          className="font-body-serif mt-3 text-sm md:text-base max-w-3xl line-clamp-2"
          style={{ color: "rgba(255,255,255,0.75)" }}
        >
          {excerpt}
        </p>
        <span
          className="inline-block mt-4 text-xs font-semibold tracking-[0.1em] uppercase group-hover:underline"
          style={{ color: GOLD, fontFamily: "Inter, sans-serif" }}
        >
          Read the full story →
        </span>
      </Link>
    </section>
  );
}
