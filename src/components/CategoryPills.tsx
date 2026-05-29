import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { CATEGORIES, getCategoryBySlug } from "@/lib/categories";

/* Standalone sections NOT on the home page — these are the only pills shown */
const SECTION_LINKS = CATEGORIES.filter((c) => !c.hasPipeline);

export default function CategoryPills() {
  const { pathname } = useLocation();
  const isHome = pathname === "/";

  const routeSlug = pathname === "/" ? "" : pathname.replace(/^\//, "").split("/")[0];
  const currentCategory = getCategoryBySlug(routeSlug);

  const scrollRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLAnchorElement>(null);

  // Auto-scroll to show the active pill when the page loads
  useEffect(() => {
    if (activeRef.current && scrollRef.current) {
      const pill = activeRef.current;
      const container = scrollRef.current;
      const pillLeft = pill.offsetLeft;
      const pillWidth = pill.offsetWidth;
      const containerWidth = container.offsetWidth;
      // Center the active pill in the scroll container
      container.scrollTo({
        left: pillLeft - containerWidth / 2 + pillWidth / 2,
        behavior: "instant",
      });
    }
  }, [routeSlug]);

  return (
    <div className="bg-background border-b hairline">
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
        <div ref={scrollRef} className="flex gap-2 overflow-x-auto py-3 -mx-1 px-1 scrollbar-none whitespace-nowrap">
          {/* Home pill */}
          <Link
            to="/"
            ref={isHome ? activeRef : undefined}
            className={`smallcaps shrink-0 px-3 py-1.5 border rounded-full transition-colors ${
              isHome
                ? "bg-primary text-primary-foreground border-primary"
                : "border-rule text-foreground/80 hover:text-primary hover:border-primary"
            }`}
          >
            Home
          </Link>

          {/* Section links: Events, Classifieds, Real Estate */}
          {SECTION_LINKS.map((section) => {
            const active = routeSlug === section.slug;
            return (
              <Link
                key={section.slug}
                to={section.path}
                ref={active ? activeRef : undefined}
                className={`smallcaps shrink-0 px-3 py-1.5 border rounded-full transition-colors ${
                  active
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-rule text-foreground/80 hover:text-primary hover:border-primary"
                }`}
              >
                {section.label}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
