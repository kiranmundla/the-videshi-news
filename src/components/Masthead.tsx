import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { formatLongDate } from "@/lib/articles";
import { CATEGORIES } from "@/lib/categories";

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
            <img src="/logo.jpg" alt="The Videshi" className="h-10 md:h-14 w-auto rounded-sm" />
            <h1 className="font-serif font-black tracking-tight text-foreground leading-none text-[2.25rem] md:text-[3.25rem] lg:text-[3.75rem]">
              The Videshi
            </h1>
            <p className="italic text-muted-foreground text-xs md:text-sm mt-1.5">
              News for the global Indian diaspora
            </p>
          </Link>

          <div className="hidden md:flex items-center gap-4 text-right">
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
              <Link to="/travel" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                ✈️ Travel
              </Link>
              <Link to="/immigration" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                🗽 Immigration
              </Link>
              <Link to="/events" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                🎪 Events
              </Link>
              <Link to="/classifieds" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                📋 Classifieds
              </Link>
              <Link to="/cars" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                🚗 Cars
              </Link>
              <Link to="/about" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                About
              </Link>
              <Link to="/contact" className="block px-5 py-3 text-sm hover:bg-foreground/5 transition-colors">
                Contact
              </Link>
            </div>
          </nav>
        </>
      )}
    </header>
  );
}
