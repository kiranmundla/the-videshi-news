import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

type HeroImage = {
  url: string;
  alt: string;
  credit: string;
  caption?: string;
  location?: string;
};

const AUTO_MS = 6000;
const MIN_SWIPE_DISTANCE = 30;

export default function HeroCarousel() {
  const [images, setImages] = useState<HeroImage[]>([]);
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    // Always fetch fresh from carousel_images (no client cache).
    const today = new Date().toISOString().slice(0, 10);
    supabase
      .from("carousel_images")
      .select("image_url,caption,credit,location")
      .eq("date", today)
      .order("position", { ascending: true })
      .then(({ data }) => {
        if (cancelled || !data) return;
        const imgs: HeroImage[] = data.map((r: any) => ({
          url: r.image_url,
          alt: r.caption ?? "",
          credit: r.credit ?? "",
          caption: r.caption ?? "",
          location: r.location ?? "",
        }));
        if (imgs.length) setImages(imgs);
      });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (images.length < 2 || paused) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % images.length);
    }, AUTO_MS);
    return () => window.clearInterval(id);
  }, [images.length, paused]);

  if (images.length === 0) return null;

  const total = images.length;
  const wrap = (n: number) => ((n % total) + total) % total;
  const go = (n: number) => setIndex(wrap(n));
  const goNext = () => go(index + 1);
  const goPrev = () => go(index - 1);

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (touchStart == null || touchEnd == null) return;
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > MIN_SWIPE_DISTANCE;
    const isRightSwipe = distance < -MIN_SWIPE_DISTANCE;
    if (isLeftSwipe) goNext();
    if (isRightSwipe) goPrev();
  };

  const current = images[index];

  return (
    <section
      className="relative w-full overflow-hidden bg-muted h-[280px] md:h-[560px] group select-none"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      aria-roledescription="carousel"
    >
      <div
        className="absolute inset-0 flex touch-pan-y"
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        style={{
          width: `${total * 100}%`,
          transform: `translateX(${-index * (100 / total)}%)`,
          transition: "transform 0.4s ease-in-out",
        }}
      >
        {images.map((img, i) => (
          <div key={img.url} className="relative h-full" style={{ width: `${100 / total}%` }}>
            <img
              src={img.url}
              alt={img.alt}
              referrerPolicy="no-referrer"
              draggable={false}
              loading={i === 0 ? "eager" : "lazy"}
              fetchPriority={i === 0 ? "high" : undefined}
              decoding={i === 0 ? undefined : "async"}
              className="absolute inset-0 w-full h-full object-cover pointer-events-none"
              width="800"
              height="450"
            />
          </div>
        ))}
      </div>

      {/* Caption overlay */}
      <div
        className="pointer-events-none absolute inset-x-0 bottom-0 px-6 md:px-12 pt-20 pb-10 md:pb-14"
        style={{ background: "linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.35) 55%, transparent 100%)" }}
      >
        <p className="text-white font-bold text-base md:text-2xl leading-snug max-w-3xl drop-shadow">
          {current.location ? `${current.location} · ` : ""}
          {current.caption || current.alt}
        </p>
        <p className="text-white/70 text-xs md:text-sm mt-1.5">
          Photo{current.credit ? `: ${current.credit} / Unsplash` : ": Unsplash"}
        </p>
      </div>

      {/* Arrow buttons — always visible, semi-transparent */}
      {total > 1 && (
        <>
          <button
            type="button"
            aria-label="Previous slide"
            onClick={goPrev}
            className="absolute left-3 md:left-4 top-1/2 -translate-y-1/2 h-10 w-10 md:h-12 md:w-12 flex items-center justify-center rounded-full bg-black/40 text-white text-xl md:text-2xl hover:bg-black/60 transition-colors"
          >
            ‹
          </button>
          <button
            type="button"
            aria-label="Next slide"
            onClick={goNext}
            className="absolute right-3 md:right-4 top-1/2 -translate-y-1/2 h-10 w-10 md:h-12 md:w-12 flex items-center justify-center rounded-full bg-black/40 text-white text-xl md:text-2xl hover:bg-black/60 transition-colors"
          >
            ›
          </button>
        </>
      )}

      {/* Dot indicators */}
      {total > 1 && (
        <div className="absolute bottom-3 md:bottom-5 left-0 right-0 flex justify-center gap-2 z-10">
          {images.map((_, i) => (
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
      )}
    </section>
  );
}
