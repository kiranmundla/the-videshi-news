import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  ImmigrationGuide,
  getImmigrationGuides,
  GUIDE_CATEGORIES,
  GUIDE_PLACEHOLDERS,
} from "@/lib/immigration";

/* ------------------------------------------------------------------ */
/* Immigration Guides Index Page                                      */
/* ------------------------------------------------------------------ */
export default function ImmigrationGuidesPage() {
  const [guides, setGuides] = useState<ImmigrationGuide[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState("all");

  useEffect(() => {
    getImmigrationGuides().then((data) => {
      setGuides(data);
      setLoading(false);
    });
  }, []);

  // Merge DB guides with placeholders (show "Coming Soon" for missing ones)
  const guideCards = GUIDE_PLACEHOLDERS.map((placeholder) => {
    const dbGuide = guides.find((g) => g.slug === placeholder.slug);
    return {
      ...placeholder,
      hasContent: !!dbGuide,
      readingTime: dbGuide?.reading_time_min,
      subtitle: dbGuide?.subtitle,
    };
  });

  const filtered = activeCategory === "all"
    ? guideCards
    : guideCards.filter((g) => g.category === activeCategory);

  return (
    <>
      <Helmet>
        <title>Immigration Guides — H-1B, Green Card, OCI, NRI Tax | The Videshi</title>
        <meta name="description" content="Comprehensive immigration guides for Indian Americans. H-1B visa, green card, OCI card, parent visa, NRI taxes, money transfer, and more." />
        <meta property="og:title" content="Immigration Guides | The Videshi" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration/guides" />
              <link rel="canonical" href="https://www.thevideshi.com/immigration/guides" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* Hero */}
        <section className="relative mb-8 -mx-4 px-4 py-10 md:py-14 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-3xl">
            <Link to="/immigration" className="text-xs text-amber-300/70 hover:text-amber-300 mb-3 inline-block">← Immigration Hub</Link>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              Immigration Guides
            </h1>
            <p className="text-white/60 mt-3 text-base md:text-lg">
              Comprehensive guides for every step of the Indian American immigration journey — from H-1B to citizenship.
            </p>
          </div>
        </section>

        {/* Category pills */}
        <div className="flex gap-2 overflow-x-auto scrollbar-none mb-6 -mx-1 px-1">
          <button
            onClick={() => setActiveCategory("all")}
            className={`shrink-0 px-4 py-2 text-sm font-medium rounded-full border transition-all ${
              activeCategory === "all"
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border text-foreground/70 hover:text-primary hover:border-primary/50"
            }`}
          >
            All Guides
          </button>
          {GUIDE_CATEGORIES.map((cat) => (
            <button
              key={cat.key}
              onClick={() => setActiveCategory(cat.key)}
              className={`shrink-0 px-4 py-2 text-sm font-medium rounded-full border transition-all ${
                activeCategory === cat.key
                  ? "bg-primary text-primary-foreground border-primary"
                  : "border-border text-foreground/70 hover:text-primary hover:border-primary/50"
              }`}
            >
              {cat.emoji} {cat.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* Guide grid */}
            {GUIDE_CATEGORIES.filter((cat) => activeCategory === "all" || cat.key === activeCategory).map((cat) => {
              const catGuides = filtered.filter((g) => g.category === cat.key);
              if (catGuides.length === 0) return null;
              return (
                <section key={cat.key} className="mb-10">
                  <h2 className="font-serif text-lg font-bold mb-4 flex items-center gap-2">
                    <span>{cat.emoji}</span> {cat.label}
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {catGuides.map((g) => (
                      <Link key={g.slug} to={`/immigration/guides/${g.slug}`} className="block group">
                        <div className="relative flex items-start gap-3 p-4 bg-card border border-border rounded-xl hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 h-full">
                          <span className="text-2xl flex-shrink-0 mt-0.5">{g.emoji}</span>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-sm group-hover:text-primary transition-colors">{g.title}</h3>
                            {g.subtitle && <p className="text-xs text-foreground/50 mt-0.5 line-clamp-2">{g.subtitle}</p>}
                            <div className="flex items-center gap-2 mt-2">
                              {g.hasContent ? (
                                <>
                                  {g.readingTime && (
                                    <span className="text-[10px] text-foreground/40">{g.readingTime} min read</span>
                                  )}
                                </>
                              ) : (
                                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500">
                                  Coming Soon
                                </span>
                              )}
                            </div>
                          </div>
                          <ChevronRight className="h-4 w-4 text-foreground/20 group-hover:text-primary transition-colors flex-shrink-0 mt-1" />
                        </div>
                      </Link>
                    ))}
                  </div>
                </section>
              );
            })}
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
