import { useEffect, useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

type HeroImage = { url: string; alt: string; credit: string };

const AUTO_MS = 5000;

export default function HeroCarousel() {
  const [images, setImages] = useState<HeroImage[]>([]);
  const [index, setIndex] = useState(0);
  const touchStartX = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    supabase.functions.invoke("unsplash-hero").then(({ data }) => {
      if (cancelled) return;
      const imgs = (data as { images?: HeroImage[] } | null)?.images ?? [];
      if (imgs.length) setImages(imgs);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (images.length < 2) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % images.length);
    }, AUTO_MS);
    return () => window.clearInterval(id);
  }, [images.length]);

  if (images.length === 0) return null;

  const go = (next: number) => setIndex(((next % images.length) + images.length) % images.length);

  const onTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };
  const onTouchEnd = (e: React.TouchEvent) => {
    if (touchStartX.current == null) return;
    const dx = e.changedTouches[0].clientX - touchStartX.current;
    if (Math.abs(dx) > 40) go(index + (dx < 0 ? 1 : -1));
    touchStartX.current = null;
  };

  return (
    <div
      className="relative w-full overflow-hidden bg-muted h-[250px] md:h-[500px]"
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
      aria-roledescription="carousel"
    >
      {images.map((img, i) => (
        <img
          key={img.url}
          src={img.url}
          alt={img.alt}
          referrerPolicy="no-referrer"
          loading={i === 0 ? "eager" : "lazy"}
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ease-in-out ${
            i === index ? "opacity-100" : "opacity-0"
          }`}
        />
      ))}

      {/* bottom gradient overlay */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent" />

      {/* desktop arrows */}
      {images.length > 1 && (
        <>
          <button
            type="button"
            aria-label="Previous slide"
            onClick={() => go(index - 1)}
            className="hidden md:flex absolute left-4 top-1/2 -translate-y-1/2 h-10 w-10 items-center justify-center rounded-full bg-black/40 text-white hover:bg-black/60 transition"
          >
            ‹
          </button>
          <button
            type="button"
            aria-label="Next slide"
            onClick={() => go(index + 1)}
            className="hidden md:flex absolute right-4 top-1/2 -translate-y-1/2 h-10 w-10 items-center justify-center rounded-full bg-black/40 text-white hover:bg-black/60 transition"
          >
            ›
          </button>
        </>
      )}

      {/* mobile dots */}
      {images.length > 1 && (
        <div className="md:hidden absolute bottom-3 left-0 right-0 flex justify-center gap-2">
          {images.map((_, i) => (
            <button
              key={i}
              type="button"
              aria-label={`Go to slide ${i + 1}`}
              onClick={() => go(i)}
              className={`h-1.5 rounded-full transition-all ${
                i === index ? "w-6 bg-white" : "w-1.5 bg-white/50"
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
