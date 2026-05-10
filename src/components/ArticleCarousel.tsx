import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

type Slide = {
  slug: string;
  headline: string;
  image_url: string;
  category: string | null;
};

const AUTO_MS = 5000;
const MIN_SWIPE = 30;

export default function ArticleCarousel() {
  const [slides, setSlides] = useState<Slide[]>([]);
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    (supabase as any)
      .from("p2_articles")
      .select("slug, headline, image_url, category")
      .eq("status", "published")
      .not("image_url", "is", null)
      .neq("image_url", "")
      .order("score_total", { ascending: false })
      .limit(3)
      .then(({ data }: { data: Slide[] | null }) => {
        if (cancelled || !data) return;
        const valid = data.filter(
          (d) =>
            d.slug &&
            d.image_url &&
            !d.image_url.toLowerCase().endsWith(".svg") &&
            !/Flag_of_|flag_of_/i.test(d.image_url) &&
            !/hindustantimes\.com|htmedia/i.test(d.image_url)
        );
        if (valid.length < 2) return;
        setSlides(valid);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (slides.length < 2 || paused) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % slides.length);
    }, AUTO_MS);
    return () => window.clearInterval(id);
  }, [slides.length, paused]);

  if (slides.length === 0) return null;

  const total = slides.length;
  const wrap = (n: number) => ((n % total) + total) % total;
  const go = (n: number) => setIndex(wrap(n));

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };
  const onTouchMove = (e: React.TouchEvent) => setTouchEnd(e.targetTouches[0].clientX);
  const onTouchEnd = () => {
    if (touchStart == null || touchEnd == null) return;
    const d = touchStart - touchEnd;
    if (d > MIN_SWIPE) go(index + 1);
    if (d < -MIN_SWIPE) go(index - 1);
  };

  const current = slides[index];

  return (
    <section
      className="relative w-full overflow-hidden bg-muted h-[100px] md:h-[140px] my-6 select-none"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      aria-roledescription="carousel"
    >
      <div
        className="absolute inset-0 flex"
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        style={{
          width: `${total * 100}%`,
          transform: `translateX(${-index * (100 / total)}%)`,
          transition: "transform 0.4s ease-in-out",
        }}
      >
        {slides.map((s, i) => (
          <Link
            key={s.slug}
            to={`/article/${s.slug}`}
            className="relative h-full block"
            style={{ width: `${100 / total}%` }}
          >
            <img
              src={s.image_url}
              alt={s.headline}
              referrerPolicy="no-referrer"
              draggable={false}
              loading={i === 0 ? "eager" : "lazy"}
              className="absolute inset-0 w-full h-full object-cover object-[center_25%]"
            />
          </Link>
        ))}
      </div>

      <div
        className="pointer-events-none absolute inset-x-0 bottom-0 px-6 md:px-12 pt-20 pb-10 md:pb-14"
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.4) 55%, transparent 100%)",
        }}
      >
        <Link to={`/article/${current.slug}`} className="pointer-events-auto">
          <h3 className="text-white font-bold text-lg md:text-3xl leading-snug max-w-3xl drop-shadow hover:underline">
            {current.headline}
          </h3>
        </Link>
      </div>

      {total > 1 && (
        <>
          <button
            type="button"
            aria-label="Previous slide"
            onClick={() => go(index - 1)}
            className="absolute left-3 md:left-4 top-1/2 -translate-y-1/2 h-10 w-10 md:h-12 md:w-12 flex items-center justify-center rounded-full bg-black/40 text-white text-xl md:text-2xl hover:bg-black/60 transition-colors"
          >
            ‹
          </button>
          <button
            type="button"
            aria-label="Next slide"
            onClick={() => go(index + 1)}
            className="absolute right-3 md:right-4 top-1/2 -translate-y-1/2 h-10 w-10 md:h-12 md:w-12 flex items-center justify-center rounded-full bg-black/40 text-white text-xl md:text-2xl hover:bg-black/60 transition-colors"
          >
            ›
          </button>
          <div className="absolute bottom-3 md:bottom-5 left-0 right-0 flex justify-center gap-2 z-10">
            {slides.map((_, i) => (
              <button
                key={i}
                type="button"
                aria-label={`Go to slide ${i + 1}`}
                onClick={() => go(i)}
                className={`h-2.5 w-2.5 rounded-full border border-white transition-all ${
                  i === index ? "bg-white" : "bg-transparent hover:bg-white/40"
                }`}
              />
            ))}
          </div>
        </>
      )}
    </section>
  );
}
