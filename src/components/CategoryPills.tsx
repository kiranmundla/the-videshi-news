import { Link, useLocation, useNavigate } from "react-router-dom";
import { CATEGORIES } from "@/lib/categories";

export default function CategoryPills() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isHome = pathname === "/";
  const items = [
    { slug: "all", label: "All", path: "/" },
    ...CATEGORIES.map((c) => ({ slug: c.slug, label: c.label, path: c.path })),
  ];

  const handleClick = (e: React.MouseEvent, slug: string, path: string) => {
    if (isHome && slug !== "all") {
      e.preventDefault();
      const el = document.getElementById(`section-${slug}`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        navigate(path);
      }
    }
  };

  return (
    <div className="bg-background border-b hairline md:hidden">
      <div className="container">
        <div className="flex gap-2 overflow-x-auto py-3 -mx-1 px-1 scrollbar-none whitespace-nowrap">
          {items.map((it) => {
            const active = it.path === "/" ? pathname === "/" : pathname === it.path;
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
