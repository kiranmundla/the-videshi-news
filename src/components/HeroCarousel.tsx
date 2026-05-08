import { useEffect, useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

type HeroImage = { url: string; alt: string; credit: string; caption?: string; location?: string };

export default function HeroCarousel() {
  const [images, setImages] = useState<HeroImage[]>([]);
  const [index, setIndex] = useState(0);
  const dragStartX = useRef<number | null>(null);
  const dragDx = useRef(0);
  const [dragging, setDragging] = useState(false);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    let cancelled = false;
    supabase.functions.invoke("unsplash-hero").then(({ data }) => {
      if (cancelled) return;
      const imgs = (data as { images?: HeroImage[] } | null)?.images ?? [];
      if (imgs.length) setImages(imgs);
    });
    return () => { cancelled = true; };
  }, []);

  if (images.length === 0) return null;

  const total = images.length;
  const wrap = (n: number) => ((n % total) + total) % total;
  const go = (next: number) => setIndex(wrap(next));

  const onPointerDown = (e: React.PointerEvent) => {
    dragStartX.current = e.clientX;
    dragDx.current = 0;
    setDragging(true);
    (e.target as Element).setPointerCapture?.(e.pointerId);
  };
  const onPointerMove = (e: React.PointerEvent) => {
    if (dragStartX.current == null) return;
    dragDx.current = e.clientX - dragStartX.current;
    setOffset(dragDx.current);
  };
  const onPointerUp = () => {
    if (dragStartX.current == null) return;
    const dx = dragDx.current;
    if (Math.abs(dx) > 60) go(index + (dx < 0 ? 1 : -1));
    dragStartX.current = null;
    dragDx.current = 0;
    setDragging(false);
    setOffset(0);
  };

  const current = images[index];
  const prev = images[wrap(index - 1)];
  const next = images[wrap(index + 1)];
  const counter = (n: number) => String(n + 1).padStart(2, "0");

  return (
    <section className="relative w-full bg-background border-y border-border/60 py-10 md:py-16 select-none">
      {/* Editorial header */}
      <div className="container flex items-end justify-between mb-6 md:mb-10">
        <div>
          <p className="smallcaps text-primary">The Wheel</p>
          <h2 className="font-serif text-2xl md:text-4xl leading-tight mt-1">
            Dispatches in pictures
          </h2>
        </div>
        <p className="smallcaps text-foreground/60 hidden md:block">Drag · spin · explore</p>
      </div>

      {/* Stage */}
      <div
        className="relative w-full overflow-hidden"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        style={{ cursor: dragging ? "grabbing" : "grab", touchAction: "pan-y" }}
      >
        <div className="container">
          <div className="relative h-[320px] md:h-[560px] flex items-center justify-center">
            {/* Side peek — prev */}
            <div
              className="hidden md:block absolute left-0 top-1/2 -translate-y-1/2 w-[18%] h-[78%] overflow-hidden opacity-40 hover:opacity-70 transition-opacity cursor-pointer"
              onClick={() => go(index - 1)}
              style={{ transform: `translate(${offset * 0.2}px, -50%)` }}
              aria-hidden
            >
              <img src={prev.url} alt="" referrerPolicy="no-referrer"
                className="w-full h-full object-cover grayscale" />
            </div>

            {/* Side peek — next */}
            <div
              className="hidden md:block absolute right-0 top-1/2 -translate-y-1/2 w-[18%] h-[78%] overflow-hidden opacity-40 hover:opacity-70 transition-opacity cursor-pointer"
              onClick={() => go(index + 1)}
              style={{ transform: `translate(${offset * 0.2}px, -50%)` }}
              aria-hidden
            >
              <img src={next.url} alt="" referrerPolicy="no-referrer"
                className="w-full h-full object-cover grayscale" />
            </div>

            {/* Center frame */}
            <div
              className="relative w-full md:w-[60%] h-full bg-muted overflow-hidden shadow-[0_30px_80px_-20px_rgba(0,0,0,0.45)] ring-1 ring-border/40"
              style={{
                transform: `translateX(${offset}px) rotate(${offset * 0.01}deg)`,
                transition: dragging ? "none" : "transform 600ms cubic-bezier(.22,1,.36,1)",
              }}
            >
              {images.map((img, i) => (
                <img
                  key={img.url}
                  src={img.url}
                  alt={img.alt}
                  referrerPolicy="no-referrer"
                  draggable={false}
                  loading={i === 0 ? "eager" : "lazy"}
                  className={`absolute inset-0 w-full h-full object-cover transition-all duration-700 ease-[cubic-bezier(.22,1,.36,1)] ${
                    i === index ? "opacity-100 scale-100" : "opacity-0 scale-105"
                  }`}
                />
              ))}

              {/* index marker top-left */}
              <div className="absolute top-4 left-4 md:top-6 md:left-6 text-white/90 mix-blend-difference">
                <span className="font-serif text-xl md:text-3xl tracking-tight">{counter(index)}</span>
                <span className="font-serif text-xs md:text-sm opacity-70"> / {counter(total - 1)}</span>
              </div>
            </div>
          </div>

          {/* Caption — editorial layout below frame */}
          <div className="mt-6 md:mt-8 grid grid-cols-12 gap-4 md:gap-8 items-start">
            <div className="col-span-12 md:col-span-2">
              <p className="smallcaps text-foreground/60">
                {current.location || "Dispatch"}
              </p>
            </div>
            <div className="col-span-12 md:col-span-7">
              <p className="font-serif text-lg md:text-2xl leading-snug text-foreground">
                {current.caption || current.alt}
              </p>
            </div>
            <div className="col-span-12 md:col-span-3 md:text-right">
              <p className="smallcaps text-foreground/50">
                Photo · Unsplash{current.credit ? ` / ${current.credit}` : ""}
              </p>
            </div>
          </div>

          {/* Controls — thin editorial */}
          <div className="mt-6 md:mt-8 flex items-center justify-between border-t border-border/60 pt-4">
            <button
              type="button"
              onClick={() => go(index - 1)}
              className="smallcaps text-foreground/70 hover:text-primary transition flex items-center gap-2"
              aria-label="Previous"
            >
              <span className="text-xl leading-none">←</span> Prev
            </button>

            <div className="flex items-center gap-3">
              {images.map((_, i) => (
                <button
                  key={i}
                  onClick={() => go(i)}
                  aria-label={`Go to ${i + 1}`}
                  className={`h-px transition-all ${
                    i === index ? "w-10 bg-primary" : "w-5 bg-foreground/30 hover:bg-foreground/60"
                  }`}
                />
              ))}
            </div>

            <button
              type="button"
              onClick={() => go(index + 1)}
              className="smallcaps text-foreground/70 hover:text-primary transition flex items-center gap-2"
              aria-label="Next"
            >
              Next <span className="text-xl leading-none">→</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
