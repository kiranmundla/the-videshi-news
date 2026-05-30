import { useEffect, useState, useMemo, useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import ReactMarkdown from "react-markdown";
import type { ReactNode } from "react";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import PhotoScrollStrip from "@/components/PhotoScrollStrip";

/* ─── destination metadata ─── */
interface DestMeta {
  title: string;
  bestMonths: string;
  budget: string;
  flights: string;
  visa: string;
}

function childrenToText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(childrenToText).join("");
  if (node && typeof node === "object" && "props" in node) {
    return childrenToText((node as any).props.children);
  }
  return "";
}

const DESTINATIONS: Record<string, DestMeta> = {
  rajasthan:    { title: "Rajasthan",       bestMonths: "Oct – Mar",          budget: "$30–150/day", flights: "Delhi, Jaipur direct",       visa: "Indian passport: no visa" },
  kerala:       { title: "Kerala",          bestMonths: "Sep – Mar",          budget: "$25–120/day", flights: "Kochi, Trivandrum direct",   visa: "Indian passport: no visa" },
  goa:          { title: "Goa",             bestMonths: "Nov – Feb",          budget: "$20–100/day", flights: "Goa/Dabolim direct",         visa: "Indian passport: no visa" },
  maldives:     { title: "Maldives",        bestMonths: "Nov – Apr",          budget: "$80–500/day", flights: "Malé from Delhi, Mumbai",    visa: "Free 30-day on arrival" },
  "sri-lanka":  { title: "Sri Lanka",       bestMonths: "Dec – Mar",          budget: "$30–100/day", flights: "Colombo from Chennai, Delhi",visa: "ETA online" },
  bali:         { title: "Bali",            bestMonths: "Apr – Oct",          budget: "$30–150/day", flights: "Denpasar via Singapore/KL",  visa: "Free 30-day on arrival" },
  london:       { title: "London & UK",     bestMonths: "May – Sep",          budget: "$80–250/day", flights: "Direct from Delhi, Mumbai",  visa: "UK visa required" },
  switzerland:  { title: "Switzerland",     bestMonths: "Jun – Sep, Dec – Feb",budget: "$100–350/day",flights: "Zürich via Europe",          visa: "Schengen visa required" },
  "new-zealand":{ title: "New Zealand",     bestMonths: "Dec – Feb",          budget: "$80–200/day", flights: "Auckland via Singapore",     visa: "eVisa or NZeTA" },
  mexico:       { title: "Mexico",          bestMonths: "Nov – Apr",          budget: "$40–150/day", flights: "Mexico City direct from US", visa: "Visa-free with US visa" },
  thailand:     { title: "Thailand",        bestMonths: "Nov – Mar",          budget: "$25–120/day", flights: "Bangkok via Tokyo/Seoul",    visa: "60-day visa-free" },
  dubai:        { title: "Dubai",           bestMonths: "Nov – Mar",          budget: "$60–300/day", flights: "Emirates nonstop from US",   visa: "14-day VOA or e-visa" },
  singapore:    { title: "Singapore",       bestMonths: "Year-round",         budget: "$60–200/day", flights: "SQ nonstop from US",         visa: "Indian passport: visa required" },
  kashmir:      { title: "Kashmir",         bestMonths: "Apr – Oct",          budget: "$25–100/day", flights: "Srinagar via Delhi",         visa: "Indian passport: no visa" },
  "himachal-pradesh": { title: "Himachal Pradesh", bestMonths: "Mar – Jun, Sep – Nov", budget: "$20–80/day", flights: "Kullu/Kangra via Delhi", visa: "Indian passport: no visa" },
  vietnam:      { title: "Vietnam",         bestMonths: "Mar – May, Sep – Nov",budget: "$20–80/day", flights: "Hanoi/HCMC via Seoul/Tokyo", visa: "e-Visa ($25, 30 days)" },
  italy:        { title: "Italy",           bestMonths: "Apr – Jun, Sep – Oct",budget: "$60–200/day", flights: "Rome/Milan direct from US", visa: "Schengen visa required" },
  greece:       { title: "Greece",          bestMonths: "May – Oct",          budget: "$50–180/day", flights: "Athens via Europe",           visa: "Schengen visa required" },
  cancun:       { title: "Cancún",          bestMonths: "Dec – Apr",          budget: "$50–200/day", flights: "Direct from most US cities", visa: "Visa-free with US visa" },
  hawaii:       { title: "Hawaii",          bestMonths: "Apr – Oct",          budget: "$80–300/day", flights: "Direct from West Coast",     visa: "Domestic — no visa" },
  australia:    { title: "Australia",       bestMonths: "Sep – Nov, Mar – May",budget: "$70–250/day", flights: "Sydney nonstop from US",    visa: "e-Visa required" },
  france:       { title: "France",          bestMonths: "Apr – Jun, Sep – Oct",budget: "$70–250/day", flights: "Paris direct from US",      visa: "Schengen visa required" },
  japan:        { title: "Japan",           bestMonths: "Mar – May, Oct – Nov",budget: "$70–200/day", flights: "Tokyo nonstop from US",     visa: "Visa-free (90 days)" },
};

const DEST_KEYS = Object.keys(DESTINATIONS);

interface GalleryPhoto { src: string; caption: string; }
interface GalleryData { [key: string]: { photos: GalleryPhoto[]; experiences?: Record<string, GalleryPhoto[]> } }

function extractSections(body: string): { id: string; label: string }[] {
  const re = /^## (.+)$/gm;
  const out: { id: string; label: string }[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(body)) !== null) {
    const label = m[1].trim();
    const id = label.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    out.push({ id, label });
  }
  return out;
}

export default function TravelDestination() {
  const { destination = "" } = useParams();
  const meta = DESTINATIONS[destination];

  const [body, setBody] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [galleryPhotos, setGalleryPhotos] = useState<GalleryPhoto[]>([]);
  const [experiencePhotos, setExperiencePhotos] = useState<Record<string, GalleryPhoto[]>>({});
  const [fullscreenIdx, setFullscreenIdx] = useState<number | null>(null);
  const [fullscreenPhotos, setFullscreenPhotos] = useState<GalleryPhoto[]>([]);

  useEffect(() => {
    if (!meta) { setLoading(false); return; }
    setLoading(true);
    fetch(`/data/travel-guides/${destination}.md`)
      .then((r) => r.ok ? r.text() : null)
      .then((text) => setBody(text))
      .catch(() => setBody(null))
      .finally(() => setLoading(false));
  }, [meta, destination]);

  useEffect(() => {
    if (!destination) return;
    fetch("/data/travel-galleries.json")
      .then((r) => r.ok ? r.json() : {})
      .then((data: GalleryData) => {
        const d = data[destination];
        setGalleryPhotos(d?.photos ?? []);
        setExperiencePhotos(d?.experiences ?? {});
      })
      .catch(() => { setGalleryPhotos([]); setExperiencePhotos({}); });
  }, [destination]);

  const openFullscreen = useCallback((photos: GalleryPhoto[], idx: number) => {
    setFullscreenPhotos(photos);
    setFullscreenIdx(idx);
  }, []);
  const fsNext = useCallback(() => {
    setFullscreenIdx((i) => i !== null ? (i + 1) % fullscreenPhotos.length : null);
  }, [fullscreenPhotos.length]);
  const fsPrev = useCallback(() => {
    setFullscreenIdx((i) => i !== null ? (i - 1 + fullscreenPhotos.length) % fullscreenPhotos.length : null);
  }, [fullscreenPhotos.length]);
  const fsClose = useCallback(() => { setFullscreenIdx(null); setFullscreenPhotos([]); }, []);

  useEffect(() => {
    if (fullscreenIdx === null) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") fsClose();
      else if (e.key === "ArrowRight") fsNext();
      else if (e.key === "ArrowLeft") fsPrev();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [fullscreenIdx, fsClose, fsNext, fsPrev]);

  const sections = useMemo(() => (body ? extractSections(body) : []), [body]);

  const otherDestinations = useMemo(() => {
    return DEST_KEYS.filter((k) => k !== destination).sort(() => Math.random() - 0.5).slice(0, 3);
  }, [destination]);

  /* ─── 404 ─── */
  if (!meta && !loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <main className="container flex-1 flex items-center justify-center py-20">
          <div className="text-center">
            <h2 className="font-serif text-3xl mb-4">Destination not found</h2>
            <Link to="/travel" className="text-red-700 underline">← Back to Travel</Link>
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  if (loading || !meta) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <main className="container flex-1 flex items-center justify-center py-20 text-muted-foreground">
          Loading…
        </main>
        <SiteFooter />
      </div>
    );
  }

  const heroUrl = galleryPhotos.length > 0 ? galleryPhotos[0].src : "";

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{meta.title} Travel Guide — The Videshi</title>
        <meta name="description" content={`Complete diaspora travel guide to ${meta.title}. Best months, budget tips, visa info, and more.`} />
      </Helmet>

      <Masthead />

      {/* ─── Destination pills nav ─── */}
      <div className="bg-stone-50 border-b border-stone-200">
        <div className="container overflow-x-auto" style={{ WebkitOverflowScrolling: "touch" }}>
          <div className="flex gap-2 py-3 whitespace-nowrap">
            <Link to="/travel" className="px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider border border-stone-300 text-stone-500 no-underline hover:bg-stone-100 transition-colors">
              All
            </Link>
            {DEST_KEYS.map((key) => {
              const active = key === destination;
              return (
                <Link key={key} to={`/travel/${key}`}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider no-underline transition-all border ${
                    active
                      ? "bg-stone-900 text-white border-stone-900"
                      : "text-stone-500 border-stone-300 hover:bg-stone-100"
                  }`}
                >
                  {DESTINATIONS[key].title}
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* ─── Breadcrumb ─── */}
      <div className="container pt-3.5">
        <nav className="text-xs text-stone-400 uppercase tracking-wide">
          <Link to="/" className="text-stone-400 no-underline hover:text-stone-600">Home</Link>
          <span className="mx-1.5">›</span>
          <Link to="/travel" className="text-stone-400 no-underline hover:text-stone-600">Travel</Link>
          <span className="mx-1.5">›</span>
          <span className="text-stone-700">{meta.title}</span>
        </nav>
      </div>

      {/* ─── Hero ─── */}
      <div className="container mt-4">
        <div className="relative w-full h-[280px] md:h-[420px] overflow-hidden rounded-lg bg-stone-900">
          {heroUrl && (
            <img src={heroUrl} alt={meta.title} className="w-full h-full object-cover block opacity-85" />
          )}
          <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.1) 100%)" }} />
          <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10">
            <p className="text-white/70 text-xs tracking-widest uppercase mb-2 font-semibold">Diaspora Travel Guide</p>
            <h1 className="font-serif text-3xl md:text-5xl font-black text-white leading-tight m-0">{meta.title}</h1>
          </div>
        </div>
      </div>

      {/* ─── Quick Facts Bar ─── */}
      <div className="container">
        <div className="flex flex-wrap bg-stone-100 rounded-b-lg overflow-hidden">
          {[
            { icon: "🗓", label: "Best Months", value: meta.bestMonths },
            { icon: "💰", label: "Budget", value: meta.budget },
            { icon: "✈️", label: "Flights", value: meta.flights },
            { icon: "🛂", label: "Visa", value: meta.visa },
          ].map((fact, i) => (
            <div key={i} className="flex-1 min-w-[140px] px-5 py-4" style={{ borderRight: i < 3 ? "1px solid #e5e5e0" : "none" }}>
              <div className="text-[11px] text-stone-400 uppercase tracking-wider font-semibold mb-1">{fact.icon} {fact.label}</div>
              <div className="text-sm text-stone-700 font-medium">{fact.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ─── Photo Gallery Strip ─── */}
      {galleryPhotos.length > 0 && (
        <div className="container mt-5">
          <PhotoScrollStrip photos={galleryPhotos} onPhotoClick={openFullscreen} />
        </div>
      )}

      {/* ─── Fullscreen Gallery Viewer ─── */}
      {fullscreenIdx !== null && fullscreenPhotos[fullscreenIdx] && (() => {
        let touchStartX = 0;
        return (
          <>
          <style>{`@keyframes lbFadeIn { from { opacity: 0; } to { opacity: 1; } }`}</style>
          <div onClick={(e) => { if (e.target === e.currentTarget) fsClose(); }}
            className="fixed inset-0 z-[9999] bg-black/95 flex flex-col items-center justify-center"
            style={{ animation: "lbFadeIn 0.15s ease-out" }}>
            <button onClick={fsClose} className="absolute top-4 right-5 bg-transparent border-none text-white text-3xl cursor-pointer z-10">✕</button>
            <div className="absolute top-5 left-1/2 -translate-x-1/2 text-white/70 text-sm font-medium">
              {fullscreenIdx + 1} / {fullscreenPhotos.length}
            </div>
            <button onClick={(e) => { e.stopPropagation(); fsPrev(); }}
              className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/15 border-none text-white text-[28px] w-12 h-12 rounded-full cursor-pointer hover:bg-white/25 transition-colors hidden md:flex items-center justify-center">‹</button>
            <div
              onTouchStart={(e) => { touchStartX = e.touches[0].clientX; }}
              onTouchEnd={(e) => { const diff = e.changedTouches[0].clientX - touchStartX; if (Math.abs(diff) > 50) { diff < 0 ? fsNext() : fsPrev(); } }}
              className="max-w-[90vw] max-h-[75vh]"
            >
              <img src={fullscreenPhotos[fullscreenIdx].src} alt={fullscreenPhotos[fullscreenIdx].caption}
                className="max-w-[90vw] max-h-[75vh] object-contain rounded" />
            </div>
            <button onClick={(e) => { e.stopPropagation(); fsNext(); }}
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/15 border-none text-white text-[28px] w-12 h-12 rounded-full cursor-pointer hover:bg-white/25 transition-colors hidden md:flex items-center justify-center">›</button>
            <div className="mt-4 text-white/85 text-[15px] font-medium text-center max-w-[80vw]">{fullscreenPhotos[fullscreenIdx].caption}</div>
          </div>
          </>
        );
      })()}

      {/* ─── Main content + sidebar ─── */}
      <div className="container mt-8 flex gap-10 items-start">

        {/* Article content */}
        <article className="flex-1 min-w-0 max-w-[780px] overflow-x-hidden">
          {body ? (
            <div className="prose-article" style={{ fontFamily: "Georgia, serif", fontSize: 17, lineHeight: 1.8, color: "#222" }}>
              <ReactMarkdown
                components={{
                  h1: ({ children }) => <h1 className="font-serif text-[32px] font-extrabold mt-8 mb-4 text-stone-900 leading-tight">{children}</h1>,
                  h2: ({ children }) => {
                    const text = childrenToText(children);
                    const id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
                    return <h2 id={id} className="font-serif text-[26px] font-bold mt-9 mb-3.5 text-stone-900 leading-snug border-b border-stone-200 pb-2">{children}</h2>;
                  },
                  h3: ({ children }) => <h3 className="font-serif text-xl font-semibold mt-7 mb-2.5 text-stone-800">{children}</h3>,
                  p: ({ children }) => {
                    const text = childrenToText(children);
                    const expMatch = text.match(/^\*?\*?\d+\.\s*([^*—–]+)/);
                    let matchedKey = "";
                    if (expMatch && Object.keys(experiencePhotos).length > 0) {
                      const expName = expMatch[1].trim().replace(/,$/, "");
                      matchedKey = Object.keys(experiencePhotos).find((k) =>
                        expName.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(expName.toLowerCase().split(",")[0].trim())
                      ) || "";
                    }
                    const expPhotos = matchedKey ? experiencePhotos[matchedKey] : null;
                    return (
                      <>
                        <p className="mb-4" style={{ lineHeight: 1.8 }}>{children}</p>
                        {expPhotos && expPhotos.length > 0 && (
                          <div className="mb-5">
                            <PhotoScrollStrip photos={expPhotos} itemWidth={220} itemHeight={140} onPhotoClick={openFullscreen} />
                          </div>
                        )}
                      </>
                    );
                  },
                  ul: ({ children }) => <ul className="mb-4 pl-6">{children}</ul>,
                  ol: ({ children }) => <ol className="mb-4 pl-6">{children}</ol>,
                  li: ({ children }) => <li className="mb-2" style={{ lineHeight: 1.7 }}>{children}</li>,
                  strong: ({ children }) => <strong className="font-bold text-stone-900">{children}</strong>,
                  blockquote: ({ children }) => <blockquote className="border-l-[3px] border-red-700 pl-4 my-5 text-stone-500 italic">{children}</blockquote>,
                  a: ({ href, children }) => <a href={href || "#"} target="_blank" rel="noopener noreferrer" className="text-red-700 underline">{children}</a>,
                }}
              >
                {body}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-stone-400 italic">Guide content is being prepared…</p>
          )}
        </article>

        {/* Sidebar — hidden on mobile */}
        <aside className="hidden lg:block w-[300px] flex-shrink-0 sticky top-6">
          {sections.length > 0 && (
            <div className="mb-7 bg-stone-50 rounded-lg p-5 border border-stone-200">
              <h3 className="font-serif text-sm font-bold mb-3 text-stone-700 uppercase tracking-wider">In This Guide</h3>
              {sections.map((s) => (
                <a key={s.id} href={`#${s.id}`}
                  className="block py-1.5 text-sm text-stone-500 no-underline border-b border-stone-100 hover:text-red-700 transition-colors">
                  {s.label}
                </a>
              ))}
            </div>
          )}

          <div className="mb-7 bg-stone-50 rounded-lg p-5 border border-stone-200">
            <h3 className="font-serif text-sm font-bold mb-3.5 text-stone-700 uppercase tracking-wider">At a Glance</h3>
            {[
              { label: "Best Months", value: meta.bestMonths },
              { label: "Daily Budget", value: meta.budget },
              { label: "Flights", value: meta.flights },
              { label: "Visa", value: meta.visa },
            ].map((row, i) => (
              <div key={i} className="mb-3">
                <div className="text-[11px] text-stone-400 uppercase tracking-wider font-semibold">{row.label}</div>
                <div className="text-sm text-stone-700 mt-0.5">{row.value}</div>
              </div>
            ))}
          </div>

          <div className="mb-7 rounded-lg p-10 border-2 border-dashed border-stone-200 text-center">
            <p className="text-stone-300 text-xs uppercase tracking-widest m-0">Advertisement</p>
          </div>

          {otherDestinations.length > 0 && (
            <div className="mb-7">
              <h3 className="font-serif text-sm font-bold mb-3.5 text-stone-700 uppercase tracking-wider">More Destinations</h3>
              {otherDestinations.map((k) => (
                <Link key={k} to={`/travel/${k}`} className="block mb-3.5 no-underline">
                  <span className="font-serif text-sm font-semibold text-stone-700 hover:text-red-700 transition-colors">{DESTINATIONS[k].title}</span>
                </Link>
              ))}
            </div>
          )}
        </aside>
      </div>

      {/* ─── Related Destinations ─── */}
      {otherDestinations.length > 0 && (
        <div className="container mt-12 pb-10">
          <div className="border-t border-stone-200 pt-7">
            <h2 className="font-serif text-[22px] font-bold mb-5 text-stone-800">Explore More Destinations</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {otherDestinations.map((k) => {
                const destMeta = DESTINATIONS[k];
                return (
                  <Link key={k} to={`/travel/${k}`}
                    className="no-underline rounded-lg overflow-hidden border border-stone-200 hover:shadow-lg transition-shadow">
                    <div className="relative h-[100px] overflow-hidden bg-stone-900 flex items-center justify-center">
                      <span className="font-serif text-2xl font-extrabold text-white">{destMeta.title}</span>
                    </div>
                    <div className="px-3.5 py-3">
                      <p className="text-xs text-stone-400 m-0 tracking-wide">🗓 {destMeta.bestMonths} · 💰 {destMeta.budget}</p>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      )}

      <div className="flex-1" />
      <SiteFooter />
    </div>
  );
}
