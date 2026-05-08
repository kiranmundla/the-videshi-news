import { useEffect, useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

type HeroImage = {
  url: string;
  alt: string;
  credit: string;
  caption?: string;
  location?: string;
};

const AUTO_MS = 6000;
const SWIPE_THRESHOLD = 50;

export default function HeroCarousel() {
  const [images, setImages] = useState<HeroImage[]>([]);
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const [dragDx, setDragDx] = useState(0);
  const dragStartX = useRef<number | null>(null);
  const dragging = useRef(false);

  useEffect(() => {
    let cancelled = false;
    supabase.functions.invoke("unsplash-hero").then(({ data }) => {
      if (cancelled) return;
      const imgs = (data as { images?: HeroImage[] } | null)?.images ?? [];
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

  const startDrag = (x: number) => {
    dragStartX.current = x;
    dragging.current = true;
    setPaused(true);
  };
  const moveDrag = (x: number) => {
    if (!dragging.current || dragStartX.current == null) return;
    setDragDx(x - dragStartX.current);
  };
  const endDrag = () => {
    if (!dragging.current) return;
    const dx = dragDx;
    if (Math.abs(dx) > SWIPE_THRESHOLD) go(index + (dx < 0 ? 1 : -1));
    dragStartX.current = null;
    dragging.current = false;
    setDragDx(0);
    setTimeout(() => setPaused(false), 800);
  };

  const current = images[index];

  return (
    <section
      className="relative w-full overflow-hidden bg-muted h-[280px] md:h-[560px] group select-none"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => { endDrag(); setPaused(false); }}
      onTouchStart={(e) => startDrag(e.touches[0].clientX)}
      onTouchMove={(e) => moveDrag(e.touches[0].clientX)}
      onTouchEnd={endDrag}
      onMouseDown={(e) => startDrag(e.clientX)}
      onMouseMove={(e) => moveDrag(e.clientX)}
      onMouseUp={endDrag}
      aria-roledescription="carousel"
      style={{ cursor: dragging.current ? "grabbing" : "grab" }}
    >
      {/* Slides — translate track */}
      <div
        className="absolute inset-0 flex"
        style={{
          width: `${total * 100}%`,
          transform: `translateX(calc(${-index * (100 / total)}% + ${dragDx}px))`,
          transition: dragging.current ? "none" : "transform 0.4s ease-in-out",
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
              className="absolute inset-0 w-full h-full object-cover pointer-events-none"
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

      {/* Hover arrows (desktop only) */}
      {total > 1 && (
        <>
          <button
            type="button"
            aria-label="Previous slide"
            onClick={() => go(index - 1)}
            className="hidden md:flex absolute left-4 top-1/2 -translate-y-1/2 h-12 w-12 items-center justify-center rounded-full bg-black/30 text-white text-2xl opacity-0 group-hover:opacity-100 hover:bg-black/60 transition-opacity duration-300"
          >
            ‹
          </button>
          <button
            type="button"
            aria-label="Next slide"
            onClick={() => go(index + 1)}
            className="hidden md:flex absolute right-4 top-1/2 -translate-y-1/2 h-12 w-12 items-center justify-center rounded-full bg-black/30 text-white text-2xl opacity-0 group-hover:opacity-100 hover:bg-black/60 transition-opacity duration-300"
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
