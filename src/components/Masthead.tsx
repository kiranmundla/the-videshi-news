import { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { formatLongDate } from "@/lib/articles";
import { CATEGORIES } from "@/lib/categories";

/* ── Category Nav Bar ─────────────────────────────────────── */
/* Persistent nav shown below the masthead on every page.
   Becomes sticky when user scrolls past it. */

const NAV_CATEGORIES = [
  { slug: "", label: "Home", path: "/" },
  { slug: "news", label: "News", path: "/news" },
  { slug: "nri-world", label: "World", path: "/nri-world" },
  { slug: "sports", label: "Sports", path: "/sports" },
  { slug: "world-cup", label: "⚽ World Cup", path: "/world-cup" },
  { slug: "entertainment", label: "Entertainment", path: "/entertainment" },
  { slug: "technology", label: "Technology", path: "/technology" },
  { slug: "markets-finance", label: "Markets", path: "/markets-finance" },
  { slug: "lifestyle-health", label: "Lifestyle", path: "/lifestyle-health" },
  { slug: "food", label: "Food", path: "/food" },
  { slug: "immigration", label: "Immigration", path: "/immigration" },
  { slug: "travel", label: "Travel", path: "/travel" },
  { slug: "events", label: "Events", path: "/events" },
  { slug: "stories", label: "Voices", path: "/stories" },
  { slug: "cars", label: "Cars", path: "/cars" },
  { slug: "directory", label: "Directory", path: "/directory" },
  { slug: "classifieds", label: "Classifieds", path: "/classifieds" },
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
          <div className="flex items-center overflow-x-auto scrollbar-none -mx-1 px-1 gap-0">
            {NAV_CATEGORIES.map((cat) => {
              const isActive = routeSlug === cat.slug;
              return (
                <Link
                  key={cat.slug}
                  to={cat.path}
                  ref={isActive ? activeRef : undefined}
                  className={`smallcaps shrink-0 px-3 py-2.5 text-[0.7rem] tracking-[0.12em] transition-colors relative whitespace-nowrap ${
                    isActive
                      ? "text-primary font-semibold"
                      : "text-foreground/65 hover:text-foreground"
                  }`}
                >
                  {cat.label}
                  {isActive && (
                    <span className="absolute bottom-0 left-3 right-3 h-[2px] bg-primary rounded-full" />
                  )}
                </Link>
              );
            })}
          </div>
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
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const location = useLocation();

  // Close menu on navigation
  useEffect(() => {
    setMenuOpen(false);
    setSearchOpen(false);
  }, [location.pathname]);

  // Lock body scroll when menu open
  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  return (
    <>
    <header className="bg-background relative">
      <div className="container">
        <div className="flex items-end justify-between pt-8 pb-4 md:pt-10 md:pb-5">
          {/* Hamburger — mobile only */}
          <button
            className="md:hidden mr-3 self-center -ml-1"
            onClick={() => setMenuOpen(true)}
            aria-label="Open menu"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>

          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.jpg" alt="The Videshi" className="h-10 md:h-14 w-auto rounded-sm" width="56" height="56" decoding="async" />
            <h1 className="font-serif font-black tracking-tight text-foreground leading-none text-[2.25rem] md:text-[3.25rem] lg:text-[3.75rem]">
              The Videshi
            </h1>
            <p className="italic text-muted-foreground text-xs md:text-sm mt-1.5">
              News for the global Indian diaspora
            </p>
          </Link>

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
              <a href="https://threads.net/@the.videshi" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors" aria-label="Follow us on Threads">
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

        <div className="md:hidden pb-3">
          <p className="smallcaps text-muted-foreground">{today}</p>
        </div>
        <div style={{ height: "0.5px" }} className="bg-rule w-full" />
      </div>

      {/* Mobile slide-out menu */}
      {menuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={() => setMenuOpen(false)}
          />
          {/* Panel */}
          <nav className="fixed top-0 left-0 bottom-0 w-72 bg-background z-50 md:hidden overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between p-5 border-b">
              <span className="font-serif font-bold text-lg">The Videshi</span>
              <button
                onClick={() => setMenuOpen(false)}
                aria-label="Close menu"
                className="p-1"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>

            {/* Search in mobile menu */}
            <div className="p-4 border-b">
              <SearchBar onClose={() => setMenuOpen(false)} />
            </div>

            <ul className="py-2">
              <li>
                <Link
                  to="/"
                  className="block px-5 py-3 text-sm font-medium hover:bg-foreground/5 transition-colors"
                >
                  Home
                </Link>
              </li>
              {CATEGORIES.filter((c) => c.hasPipeline).map((cat) => (
                <li key={cat.slug}>
                  <Link
                    to={cat.path}
                    className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors"
                  >
                    {cat.label}
                  </Link>
                </li>
              ))}
            </ul>

            <div className="border-t py-2">
              <Link to="/immigration" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                🗽 Immigration
              </Link>
              <Link to="/travel" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                ✈️ Travel
              </Link>
              <Link to="/cars" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                🚗 Cars
              </Link>
              <Link to="/events" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                🎪 Events
              </Link>
              <Link to="/stories" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                ✍️ Diaspora Voices
              </Link>
              <Link to="/directory" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                📍 Directory
              </Link>
              <Link to="/classifieds" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                📋 Classifieds
              </Link>
              <Link to="/about" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                About
              </Link>
              <Link to="/contact" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                Contact
              </Link>
            </div>

            {/* Social links */}
            <div className="border-t px-5 py-4">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Follow Us</p>
              <div className="flex items-center gap-5">
                <a href="https://x.com/thevideshi" target="_blank" rel="noopener noreferrer" className="text-foreground/60 hover:text-foreground transition-colors" aria-label="X">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                </a>
                <a href="https://instagram.com/the.videshi" target="_blank" rel="noopener noreferrer" className="text-foreground/60 hover:text-foreground transition-colors" aria-label="Instagram">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
                  </svg>
                </a>
                <a href="https://www.facebook.com/profile.php?id=1145353431990758" target="_blank" rel="noopener noreferrer" className="text-foreground/60 hover:text-foreground transition-colors" aria-label="Facebook">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                </a>
                <a href="https://youtube.com/@the.videshi" target="_blank" rel="noopener noreferrer" className="text-foreground/60 hover:text-foreground transition-colors" aria-label="YouTube">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                    <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                </a>
                <a href="https://threads.net/@the.videshi" target="_blank" rel="noopener noreferrer" className="text-foreground/60 hover:text-foreground transition-colors" aria-label="Threads">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                    <path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.59 12c.025 3.083.718 5.496 2.057 7.164 1.432 1.784 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.348-.794-.947-1.44-1.722-1.872-.137 1.467-.544 2.632-1.228 3.469-.883 1.082-2.155 1.654-3.783 1.7-1.262-.035-2.335-.425-3.093-1.126-.797-.736-1.22-1.74-1.188-2.825.058-1.964 1.622-3.395 3.942-3.608.951-.087 1.916-.056 2.858.088-.112-.622-.336-1.1-.675-1.424-.505-.483-1.276-.73-2.29-.734h-.032c-.795.003-1.533.21-2.07.6-.416.3-.717.714-.89 1.214l-1.972-.636c.27-.776.775-1.433 1.49-1.932.937-.655 2.136-.996 3.465-1.004h.042c1.54.009 2.755.428 3.61 1.244.71.678 1.14 1.584 1.3 2.69.585.18 1.132.42 1.633.72 1.178.707 2.065 1.74 2.575 3.003.786 1.95.78 4.605-1.34 6.682-1.796 1.76-4.012 2.534-7.147 2.557z"/>
                  </svg>
                </a>
              </div>
            </div>
          </nav>
        </>
      )}
    </header>
    <CategoryNavBar />
    </>
  );
}
