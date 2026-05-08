import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { CATEGORIES, getCategoryBySlug } from "@/lib/categories";

export default function CategoryPills() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isHome = pathname === "/";
  const items = [
    { slug: "all", label: "All", path: "/" },
    ...CATEGORIES.map((c) => ({ slug: c.slug, label: c.label, path: c.path })),
  ];

  // Active category from current route (e.g. "/sports" → "sports")
  const routeSlug = pathname === "/" ? "all" : pathname.replace(/^\//, "").split("/")[0];
  const currentCategory = getCategoryBySlug(routeSlug);

  // Scroll-spy: track active section on home
  const [spySlug, setSpySlug] = useState<string>("all");

  useEffect(() => {
    if (!isHome) return;
    setSpySlug("all");
    const sectionIds = items
      .filter((i) => i.slug !== "all")
      .map((i) => `section-${i.slug}`);

    const onScroll = () => {
      // If near top, ALL is active
      if (window.scrollY < 200) {
        setSpySlug("all");
        return;
      }
      const offset = 140; // sticky-bar offset
      let current = "all";
      for (const id of sectionIds) {
        const el = document.getElementById(id);
        if (!el) continue;
        const top = el.getBoundingClientRect().top;
        if (top - offset <= 0) current = id.replace("section-", "");
      }
      setSpySlug(current);
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [isHome, pathname]);

  const handleClick = (e: React.MouseEvent, slug: string, path: string) => {
    if (isHome && slug !== "all") {
      e.preventDefault();
      const el = document.getElementById(`section-${slug}`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        navigate(path);
      }
    } else if (isHome && slug === "all") {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <div className="bg-background border-b hairline md:hidden">
      <div className="container">
        {!isHome && currentCategory && (
          <div className="flex items-center justify-between pt-2.5 pb-1">
            <nav aria-label="Breadcrumb" className="smallcaps text-foreground/60 text-xs flex items-center gap-1">
              <Link to="/" className="hover:text-primary">Home</Link>
              <ChevronRight className="h-3 w-3" />
              <span className="text-foreground/80">{currentCategory.label}</span>
            </nav>
            <Link
              to="/"
              className="smallcaps text-xs flex items-center gap-1 text-foreground/70 hover:text-primary"
            >
              <ChevronLeft className="h-3 w-3" />
              Home
            </Link>
          </div>
        )}
        <div className="flex gap-2 overflow-x-auto py-3 -mx-1 px-1 scrollbar-none whitespace-nowrap">
          {items.map((it) => {
            const active = isHome ? spySlug === it.slug : routeSlug === it.slug;
            return (
              <Link
                key={it.slug}
                to={it.path}
                onClick={(e) => handleClick(e, it.slug, it.path)}
                className={`smallcaps shrink-0 px-3 py-1.5 border rounded-full transition-colors ${
                  active
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-rule text-foreground/80 hover:text-primary hover:border-primary"
                }`}
              >
                {it.label}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
