import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { getGuideBySlug, getAllGuides, type KidsGuide } from "@/lib/kidsGuides";

/* ------------------------------------------------------------------ */
/* Simple markdown renderer (handles bold, italic, links, tables,     */
/* headings, lists, and line breaks — no external dependency)          */
/* ------------------------------------------------------------------ */

function renderMarkdown(md: string): string {
  let html = md;

  // Tables
  html = html.replace(/^(\|.+\|)\n(\|[-| :]+\|)\n((?:\|.+\|\n?)*)/gm, (_m, header: string, _sep: string, body: string) => {
    const headers = header.split("|").filter((c: string) => c.trim()).map((c: string) => `<th class="px-3 py-2 text-left text-sm font-semibold text-foreground border-b border-border">${c.trim()}</th>`).join("");
    const rows = body.trim().split("\n").map((row: string) => {
      const cells = row.split("|").filter((c: string) => c.trim()).map((c: string) => `<td class="px-3 py-2 text-sm text-muted-foreground border-b border-border/50">${c.trim()}</td>`).join("");
      return `<tr class="hover:bg-muted/30">${cells}</tr>`;
    }).join("");
    return `<div class="overflow-x-auto my-4"><table class="w-full border-collapse"><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table></div>`;
  });

  // H3
  html = html.replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold text-foreground mt-6 mb-3">$1</h3>');

  // Bold + italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-[#D4A843] hover:underline">$1</a>');

  // Unordered lists
  html = html.replace(/^- (.+)$/gm, '<li class="ml-4 text-muted-foreground">$1</li>');
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, (match) => `<ul class="list-disc pl-4 space-y-1.5 my-3">${match}</ul>`);

  // Paragraphs (double newline)
  html = html.split("\n\n").map((block) => {
    const trimmed = block.trim();
    if (!trimmed) return "";
    if (trimmed.startsWith("<h3") || trimmed.startsWith("<div") || trimmed.startsWith("<ul") || trimmed.startsWith("<table")) return trimmed;
    return `<p class="text-muted-foreground leading-relaxed mb-4">${trimmed}</p>`;
  }).join("\n");

  return html;
}

/* ------------------------------------------------------------------ */
/* Component                                                          */
/* ------------------------------------------------------------------ */

export default function KidsGuidePage() {
  const { slug } = useParams<{ slug: string }>();
  const [guide, setGuide] = useState<KidsGuide | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (slug) {
      const found = getGuideBySlug(slug);
      setGuide(found || null);
    }
    setLoading(false);
    window.scrollTo(0, 0);
  }, [slug]);

  const allGuides = getAllGuides();
  const otherGuides = allGuides.filter((g) => g.slug !== slug);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Masthead />
        <CategoryPills />
        <div className="max-w-3xl mx-auto px-4 py-20 text-center">
          <div className="animate-pulse text-muted-foreground">Loading guide...</div>
        </div>
        <SiteFooter />
      </div>
    );
  }

  if (!guide) {
    return (
      <div className="min-h-screen bg-background">
        <Masthead />
        <CategoryPills />
        <div className="max-w-3xl mx-auto px-4 py-20 text-center">
          <h1 className="text-2xl font-serif font-bold text-foreground mb-4">Guide Not Found</h1>
          <p className="text-muted-foreground mb-6">We couldn't find the guide you're looking for.</p>
          <Link to="/kids" className="text-[#D4A843] hover:underline">← Back to Learn</Link>
        </div>
        <SiteFooter />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Helmet>
        <title>{guide.title} — The Videshi</title>
        <meta name="description" content={guide.summary} />
        <meta property="og:title" content={`${guide.title} — The Videshi`} />
        <meta property="og:description" content={guide.summary} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={`https://www.thevideshi.com/kids/guides/${guide.slug}`} />
        <meta property="og:site_name" content="The Videshi" />
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:title" content={`${guide.title} — The Videshi`} />
        <meta name="twitter:description" content={guide.summary} />
        <link rel="canonical" href={`https://www.thevideshi.com/kids/guides/${guide.slug}`} />
      </Helmet>

      <Masthead />
      <CategoryPills />

      {/* Breadcrumb */}
      <div className="max-w-3xl mx-auto px-4 pt-6 pb-2">
        <nav className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <Link to="/kids" className="hover:text-[#D4A843] transition-colors">Learn</Link>
          <span>›</span>
          <span className="text-foreground">Guide</span>
        </nav>
      </div>

      {/* Header */}
      <header className="max-w-3xl mx-auto px-4 pt-4 pb-8">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">{guide.icon}</span>
          <div>
            <span className="text-xs font-medium uppercase tracking-wider text-[#D4A843]">Parent's Guide</span>
            <h1 className="font-serif text-2xl sm:text-3xl font-bold text-foreground leading-tight">{guide.title}</h1>
          </div>
        </div>
        <p className="text-muted-foreground text-base sm:text-lg leading-relaxed max-w-2xl">
          {guide.summary}
        </p>
      </header>

      {/* Table of Contents */}
      <div className="max-w-3xl mx-auto px-4 mb-10">
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">In This Guide</h2>
          <ol className="space-y-1.5">
            {guide.sections.map((section, i) => (
              <li key={i}>
                <a
                  href={`#section-${i}`}
                  className="text-sm text-muted-foreground hover:text-[#D4A843] transition-colors flex items-center gap-2"
                >
                  <span className="text-xs text-muted-foreground/50 w-5 text-right">{i + 1}.</span>
                  {section.heading}
                </a>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* Guide Sections */}
      <article className="max-w-3xl mx-auto px-4 pb-12">
        {guide.sections.map((section, i) => (
          <section key={i} id={`section-${i}`} className="mb-10 scroll-mt-20">
            <h2 className="font-serif text-xl sm:text-2xl font-bold text-foreground mb-4 pb-2 border-b border-border">
              {section.heading}
            </h2>
            <div
              className="prose-custom"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(section.content) }}
            />
          </section>
        ))}
      </article>

      {/* Back to Kids & Other Guides */}
      <div className="max-w-3xl mx-auto px-4 pb-16">
        <div className="border-t border-border pt-8">
          <Link
            to="/kids"
            className="inline-flex items-center gap-2 text-sm text-[#D4A843] hover:underline mb-8"
          >
            ← Back to Learn
          </Link>

          {otherGuides.length > 0 && (
            <div>
              <h2 className="font-serif text-lg font-semibold text-foreground mb-4">More Guides</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {otherGuides.slice(0, 4).map((g) => (
                  <Link
                    key={g.slug}
                    to={`/kids/guides/${g.slug}`}
                    className="rounded-xl border border-border bg-card p-4 hover:shadow-md hover:border-[#D4A843]/50 transition-all"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl flex-shrink-0">{g.icon}</span>
                      <div>
                        <h3 className="font-serif text-sm font-semibold text-foreground leading-snug">{g.title}</h3>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{g.summary}</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <SiteFooter />
    </div>
  );
}
