import { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { formatLongDate } from "@/lib/articles";
import { CATEGORIES } from "@/lib/categories";
import "@/components/homepage/homepage-v2.css";

/* ── Category Nav Bar ─────────────────────────────────────── */
/* Persistent nav shown below the masthead on every page.
   Becomes sticky when user scrolls past it. */

/* Row 1 — editorial content categories (scrollable, homepage only via HomeCategoryNav) */
const NAV_CATEGORIES = [
  { slug: "", label: "Home", path: "/" },
  { slug: "news", label: "India", path: "/news" },
  { slug: "nri-world", label: "World", path: "/nri-world" },
  { slug: "immigration", label: "Immigration", path: "/immigration" },
  { slug: "technology", label: "Technology", path: "/technology" },
  { slug: "sports", label: "Sports", path: "/sports" },
  { slug: "markets-finance", label: "Markets", path: "/markets-finance" },
  { slug: "entertainment", label: "Entertainment", path: "/entertainment" },
  { slug: "lifestyle-health", label: "Lifestyle", path: "/lifestyle-health" },
  { slug: "travel", label: "Travel", path: "/travel" },
  { slug: "food", label: "Food", path: "/food" },
  { slug: "cars", label: "Cars", path: "/cars" },
];

/* Hub navigation — compact icons for non-homepage pages */
const HUB_NAV = [
  {
    slug: "", label: "News", path: "/",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 16, height: 16 }}><path d="M4 4h12v16H4z"/><path d="M16 8h3v12H7"/><line x1="7" y1="8" x2="13" y2="8"/><line x1="7" y1="11" x2="13" y2="11"/><line x1="7" y1="14" x2="10" y2="14"/></svg>,
  },
  {
    slug: "directory", label: "Directory", path: "/directory",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 16, height: 16 }}><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><line x1="10" y1="8" x2="14" y2="8"/><line x1="10" y1="10.5" x2="14" y2="10.5"/></svg>,
  },
  {
    slug: "events", label: "Events", path: "/events",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 16, height: 16 }}><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="16" y1="2" x2="16" y2="6"/></svg>,
  },
  {
    slug: "classifieds", label: "Classifieds", path: "/classifieds",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 16, height: 16 }}><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><circle cx="7" cy="7" r="1.5" fill="currentColor"/></svg>,
  },
  {
    slug: "stories", label: "Voices", path: "/stories",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 16, height: 16 }}><path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/></svg>,
  },
  {
    slug: "kids", label: "Learn", path: "/kids",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 16, height: 16 }}><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c0 1.66 2.69 3 6 3s6-1.34 6-3v-5"/></svg>,
  },
];

/* Row 2 — feature / community sections (fixed, no scroll) */
const NAV_SECTIONS = [
  { slug: "events", label: "Events", path: "/events" },
  { slug: "directory", label: "Directory", path: "/directory" },
  { slug: "classifieds", label: "Classifieds", path: "/classifieds" },
  { slug: "stories", label: "Voices", path: "/stories" },
  { slug: "kids", label: "Learn", path: "/kids" },
];

/* CTA links in Row 2 (right-aligned) */
const NAV_CTAS = [
  // Removed — each section page (events, classifieds) has its own + Post button
];

/* Row 3 — live happenings (conditional, only renders when non-empty) */
const LIVE_HAPPENINGS = [
  { slug: "world-cup", label: "FIFA World Cup", path: "/world-cup", icon: "⚽" },
  // { slug: "ipl", label: "IPL 2026", path: "/sports", icon: "🏏" },
  // { slug: "elections", label: "Elections", path: "/news", icon: "🗳️" },
];

function CategoryNavBar() {
  const { pathname } = useLocation();
  const navRef = useRef<HTMLDivElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const [stuck, setStuck] = useState(false);
  const activeRef = useRef<HTMLAnchorElement>(null);

  // Determine active slug from path
  const routeSlug = pathname === "/" ? "" : pathname.replace(/^\//, "").split("/")[0];

  // Intersection observer for sticky state
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;
    const obs = new IntersectionObserver(
      ([e]) => setStuck(!e.isIntersecting),
      { threshold: 0 }
    );
    obs.observe(sentinel);
    return () => obs.disconnect();
  }, []);

  // Auto-scroll to active pill on mount / route change
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({
        inline: "center",
        block: "nearest",
        behavior: "instant",
      });
    }
  }, [routeSlug]);

  return (
    <>
      {/* Sentinel — when it scrolls out of view, nav becomes sticky */}
      <div ref={sentinelRef} className="h-0" />
      <nav
        ref={navRef}
        className={`bg-background/95 backdrop-blur-sm border-b transition-shadow z-30 ${
          stuck ? "fixed top-0 left-0 right-0 shadow-sm" : ""
        }`}
        style={{ borderColor: "hsl(var(--rule))" }}
      >
        <div className="container">
          {routeSlug !== "" && (
          <div className="v2-home-cat-nav" style={{ padding: "0 4px" }}>
            <div className="v2-home-cat-nav-inner">
              {NAV_CATEGORIES.map((item) => {
                const isActive = routeSlug === item.slug;
                return (
                  <Link
                    key={item.slug}
                    to={item.path}
                    ref={isActive ? activeRef : undefined}
                    className={`v2-home-cat-pill${isActive ? " active" : ""}`}
                  >
                    {item.label}
                  </Link>
                );
              })}
              {/* Hub section links removed — HubStrip tiles render on desktop now */}
            </div>
          </div>
          )}

          {/* Row 2 — feature sections (hidden everywhere, hub icons replace it) */}
          {false && (
          <div className="flex items-center overflow-x-auto scrollbar-none -mx-1 px-1 gap-0 border-t" style={{ borderColor: "hsl(var(--rule) / 0.4)" }}>
            {NAV_SECTIONS.map((sec) => {
              const isActive = routeSlug === sec.slug;
              return (
                <Link
                  key={sec.slug}
                  to={sec.path}
                  ref={isActive ? activeRef : undefined}
                  className={`flex items-center gap-1 shrink-0 px-3 py-2 text-[0.65rem] tracking-[0.1em] transition-colors relative whitespace-nowrap ${
                    isActive
                      ? "text-primary font-semibold"
                      : "text-foreground/55 hover:text-foreground"
                  }`}
                >
                  <span className="smallcaps">{sec.label}</span>
                  {isActive && (
                    <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full" />
                  )}
                </Link>
              );
            })}
            {/* CTA links */}
            <div className="ml-auto flex items-center gap-0 shrink-0">
              {NAV_CTAS.map((cta) => (
                <Link
                  key={cta.path}
                  to={cta.path}
                  className="shrink-0 px-3 py-1.5 text-[0.6rem] tracking-[0.08em] font-semibold text-primary hover:text-primary/80 transition-colors whitespace-nowrap"
                >
                  {cta.label}
                </Link>
              ))}
            </div>
          </div>
          )}

          {/* Row 3 — live happenings (homepage only, rendered as LiveStrip in IndexV2) */}
          {false && LIVE_HAPPENINGS.length > 0 && (
            <div
              className="flex items-center overflow-x-auto scrollbar-none gap-0 px-1 v2-live-strip"
              style={{ background: "linear-gradient(135deg, #0B1D3A, #132d54)" }}
            >
              <span className="shrink-0 flex items-center gap-1 pl-3 pr-1 py-1.5 text-[0.6rem] tracking-[0.08em] text-red-400 font-semibold uppercase">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
                </span>
                Live
              </span>
              {LIVE_HAPPENINGS.map((h) => {
                const isActive = routeSlug === h.slug;
                return (
                  <Link
                    key={h.slug}
                    to={h.path}
                    ref={isActive ? activeRef : undefined}
                    className={`flex items-center gap-1 shrink-0 px-3 py-1.5 text-[0.65rem] tracking-[0.1em] transition-colors relative whitespace-nowrap ${
                      isActive
                        ? "text-amber-300 font-semibold"
                        : "text-white/70 hover:text-white"
                    }`}
                  >
                    <span className="text-[0.7rem]">{h.icon}</span>
                    <span className="smallcaps">{h.label}</span>
                    {isActive && (
                      <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-amber-400 rounded-full" />
                    )}
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </nav>
      {/* Spacer when stuck to prevent content jump */}
      {stuck && <div style={{ height: navRef.current?.offsetHeight || 40 }} />}
    </>
  );
}

function SearchBar({ onClose }: { onClose?: () => void }) {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
    onClose?.();
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search articles…"
        className="flex-1 px-3 py-2 rounded-md border border-foreground/20 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
        autoFocus
      />
      <button
        type="submit"
        className="px-3 py-2 rounded-md bg-foreground text-background text-sm font-medium hover:bg-foreground/90 transition-colors"
      >
        Search
      </button>
    </form>
  );
}

export default function Masthead() {
  const today = formatLongDate(new Date().toISOString());
  const [searchOpen, setSearchOpen] = useState(false);
  const location = useLocation();

  // Close search on navigation
  useEffect(() => {
    setSearchOpen(false);
  }, [location.pathname]);

  return (
    <>
    <header className="bg-background relative">
      <div className="container">
        <div className="flex items-end justify-between pt-8 pb-4 md:pt-10 md:pb-5">
          <Link to="/" onClick={() => { window.dispatchEvent(new Event('videshi-go-home')); window.scrollTo(0, 0); }} className="flex items-center gap-3">
            <img src="/logo.jpg" alt="The Videshi" className="h-14 md:h-16 w-auto rounded-sm" width="64" height="64" decoding="async" />
            <div className="flex flex-col">
              <h1 className="font-serif font-black tracking-tight text-foreground leading-none text-[2rem] md:text-[3.25rem] lg:text-[3.75rem] whitespace-nowrap">
                The Videshi
              </h1>
              <p className="italic text-muted-foreground text-[0.7rem] md:text-sm mt-0.5">
                News for the global Indian diaspora
              </p>
            </div>
          </Link>

          {/* Mobile search icon */}
          <button
            className="md:hidden p-1.5 rounded-full hover:bg-foreground/5 transition-colors self-center"
            onClick={() => setSearchOpen(!searchOpen)}
            aria-label="Toggle search"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </button>

          <div className="hidden md:flex items-center gap-4 text-right">
            <div className="flex items-center gap-3 mr-2">
              <a href="https://x.com/thevideshi" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors" aria-label="Follow us on X">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </a>
              <a href="https://instagram.com/the.videshi" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors" aria-label="Follow us on Instagram">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
                </svg>
              </a>
              <a href="https://www.facebook.com/profile.php?id=1145353431990758" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors" aria-label="Follow us on Facebook">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a href="https://youtube.com/@the.videshi" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors" aria-label="Follow us on YouTube">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>
              <a href="https://threads.com/@the.videshi" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors" aria-label="Follow us on Threads">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.59 12c.025 3.083.718 5.496 2.057 7.164 1.432 1.784 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.348-.794-.947-1.44-1.722-1.872-.137 1.467-.544 2.632-1.228 3.469-.883 1.082-2.155 1.654-3.783 1.7-1.262-.035-2.335-.425-3.093-1.126-.797-.736-1.22-1.74-1.188-2.825.058-1.964 1.622-3.395 3.942-3.608.951-.087 1.916-.056 2.858.088-.112-.622-.336-1.1-.675-1.424-.505-.483-1.276-.73-2.29-.734h-.032c-.795.003-1.533.21-2.07.6-.416.3-.717.714-.89 1.214l-1.972-.636c.27-.776.775-1.433 1.49-1.932.937-.655 2.136-.996 3.465-1.004h.042c1.54.009 2.755.428 3.61 1.244.71.678 1.14 1.584 1.3 2.69.585.18 1.132.42 1.633.72 1.178.707 2.065 1.74 2.575 3.003.786 1.95.78 4.605-1.34 6.682-1.796 1.76-4.012 2.534-7.147 2.557z"/>
                </svg>
              </a>
            </div>
            <p className="smallcaps text-muted-foreground">{today}</p>
            {/* Desktop search toggle */}
            <button
              onClick={() => setSearchOpen(!searchOpen)}
              aria-label="Toggle search"
              className="p-1.5 rounded-full hover:bg-foreground/5 transition-colors"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </button>
          </div>
        </div>

        {/* Desktop search bar */}
        {searchOpen && (
          <div className="hidden md:block pb-4 max-w-xl ml-auto">
            <SearchBar onClose={() => setSearchOpen(false)} />
          </div>
        )}

        {/* Mobile search bar */}
        {searchOpen && (
          <div className="md:hidden pb-3 px-1">
            <SearchBar onClose={() => setSearchOpen(false)} />
          </div>
        )}

        <div className="md:hidden pb-3">
          <p className="smallcaps text-muted-foreground">{today}</p>
        </div>
        <div style={{ height: "0.5px" }} className="bg-rule w-full" />
      </div>

      {/* Mobile slide-out menu */}
    </header>
    <CategoryNavBar />
    </>
  );
}
