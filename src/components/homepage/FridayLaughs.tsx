import { useEffect, useState } from "react";
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
      <div className="flex items-center gap-3 mb-6">
        <h2 className="font-serif text-2xl md:text-3xl text-foreground">Friday Laughs</h2>
        <span className="text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-100 text-amber-800">
          Comics
        </span>
      </div>

      {selected && (
        <div className="mb-6">
          <button
            onClick={() => setExpanded(true)}
            className="w-full rounded-xl overflow-hidden border border-border bg-secondary/30 cursor-zoom-in"
          >
            <img src={selected.image_url} alt={selected.title} className="w-full" loading="lazy" />
          </button>
          <p className="mt-3 font-serif text-lg font-semibold text-foreground">{selected.title}</p>
          <p className="text-sm text-muted-foreground mt-1">
            {new Date(selected.published_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
          </p>
        </div>
      )}

      {/* Lightbox — same pattern as Snapshots: opaque bg, native pinch-to-zoom */}
      {expanded && selected && (
        <div
          style={{
            position: "fixed",
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: "rgba(0,0,0,0.95)",
            zIndex: 9999,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            animation: "snapFadeIn 0.15s ease-out",
          }}
          onClick={() => setExpanded(false)}
        >
          <style>{`@keyframes snapFadeIn { from { opacity: 0; } to { opacity: 1; } }`}</style>
          <button
            onClick={() => setExpanded(false)}
            style={{
              position: "absolute", top: 12, right: 16, zIndex: 10000,
              background: "rgba(255,255,255,0.15)", border: "none", color: "#fff",
              width: 36, height: 36, borderRadius: "50%", cursor: "pointer",
              fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center",
            }}
          >×</button>
          <div onClick={(e) => e.stopPropagation()} style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "0 20px" }}>
            <img
              src={selected.image_url}
              alt={selected.title}
              draggable={false}
              style={{
                maxWidth: "calc(100vw - 40px)",
                maxHeight: "calc(100vh - 100px)",
                objectFit: "contain",
                borderRadius: "8px",
                userSelect: "none",
                WebkitUserSelect: "none",
              } as React.CSSProperties}
            />
          </div>
          <p style={{
            color: "#fff", fontSize: "14px", fontWeight: 600,
            fontFamily: "var(--font-sans, sans-serif)",
            textAlign: "center", padding: "12px 20px 0", margin: 0,
          }}>
            {selected.title}
          </p>
        </div>
      )}

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
              <img src={c.image_url} alt={c.title} className="w-full aspect-[16/9] object-cover" loading="lazy" />
              <p className="text-xs font-medium text-foreground px-2 py-1.5 truncate">{c.title}</p>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
