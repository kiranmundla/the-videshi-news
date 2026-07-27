import { useEffect, useState, useRef, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";

interface Comic {
  id: string;
  title: string;
  slug: string;
  image_url: string;
  caption: string;
  published_at: string;
}

export default function FridayLaughs() {
  const [comics, setComics] = useState<Comic[]>([]);
  const [selected, setSelected] = useState<Comic | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [zoomed, setZoomed] = useState(false);
  const lastTapRef = useRef(0);

  const handleImageTap = useCallback(() => {
    const now = Date.now();
    if (now - lastTapRef.current < 400) {
      setZoomed((z) => !z);
      lastTapRef.current = 0;
    } else {
      lastTapRef.current = now;
    }
  }, []);

  useEffect(() => {
    supabase
      .from("comics")
      .select("id, title, slug, image_url, caption, published_at")
      .order("published_at", { ascending: false })
      .limit(8)
      .then(({ data }) => {
        if (data && data.length > 0) {
          setComics(data as Comic[]);
          setSelected(data[0] as Comic);
        }
      });
  }, []);

  if (comics.length === 0) return null;

  return (
    <section className="container py-8 md:py-12">
      {/* Section header */}
      <div className="flex items-center gap-3 mb-6">
        <h2 className="font-serif text-2xl md:text-3xl text-foreground">Friday Laughs</h2>
        <span className="text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-100 text-amber-800">
          Comics
        </span>
      </div>

      {/* Featured comic */}
      {selected && (
        <div className="mb-6">
          <button
            onClick={() => setExpanded(true)}
            className="w-full rounded-xl overflow-hidden border border-border bg-secondary/30 cursor-zoom-in"
          >
            <img
              src={selected.image_url}
              alt={selected.title}
              className="w-full"
              loading="lazy"
            />
          </button>
          <p className="mt-3 font-serif text-lg font-semibold text-foreground">
            {selected.title}
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            {new Date(selected.published_at).toLocaleDateString("en-US", {
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </p>
        </div>
      )}

      {/* Lightbox overlay — tap to open, double-tap to zoom */}
      {expanded && selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={() => { setExpanded(false); setZoomed(false); }}
        >
          <button
            onClick={() => { setExpanded(false); setZoomed(false); }}
            className="absolute top-4 right-4 text-white text-2xl font-bold w-10 h-10 flex items-center justify-center z-50"
            aria-label="Close"
          >
            ✕
          </button>
          <div
            className={`transition-all duration-200 ${
              zoomed ? "overflow-auto max-h-[95vh] max-w-[95vw]" : "flex items-center justify-center px-4"
            }`}
            style={{ WebkitOverflowScrolling: "touch" }}
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={selected.image_url}
              alt={selected.title}
              className={`block rounded-lg shadow-2xl transition-all duration-200 ${
                zoomed ? "w-[250vw] md:w-[150vw]" : "max-w-[92vw] max-h-[80vh] object-contain"
              }`}
              onTouchStart={handleImageTap}
              onDoubleClick={() => setZoomed((z) => !z)}
            />
          </div>
        </div>
      )}

      {/* Scroll strip of past comics */}
      {comics.length > 1 && (
        <div className="flex gap-3 overflow-x-auto pb-4" style={{ WebkitOverflowScrolling: "touch" }}>
          {comics.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelected(c)}
              className={`shrink-0 rounded-lg overflow-hidden border-2 transition-all ${
                selected?.id === c.id
                  ? "border-[#D4A843] ring-2 ring-[#D4A843]/30"
                  : "border-transparent hover:border-border"
              }`}
              style={{ width: 140 }}
            >
              <img
                src={c.image_url}
                alt={c.title}
                className="w-full aspect-[16/9] object-cover"
                loading="lazy"
              />
              <p className="text-xs font-medium text-foreground px-2 py-1.5 truncate">
                {c.title}
              </p>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
