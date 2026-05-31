import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  ImmigrationGuide,
  getGuideBySlug,
  GUIDE_PLACEHOLDERS,
  GUIDE_CATEGORIES,
} from "@/lib/immigration";

/* ------------------------------------------------------------------ */
/* Simple markdown-ish renderer (handles # headings, **, lists, paras)*/
/* ------------------------------------------------------------------ */
function renderMarkdown(md: string) {
  const lines = md.split("\n");
  const elements: JSX.Element[] = [];
  let key = 0;
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed) { i++; continue; }

    /* ---- Table detection ---- */
    if (trimmed.startsWith("|") && i + 1 < lines.length && /^\|[\s-:|]+\|$/.test(lines[i + 1]?.trim())) {
      // Collect all table rows
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i].trim());
        i++;
      }
      // Parse header
      const parseRow = (row: string) =>
        row.split("|").slice(1, -1).map((c) => c.trim());
      const headers = parseRow(tableLines[0]);
      // Skip separator (row 1), parse body rows
      const bodyRows = tableLines.slice(2).map(parseRow);

      elements.push(
        <div key={key++} className="overflow-x-auto my-4 rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-foreground/5 border-b border-border">
                {headers.map((h, hi) => (
                  <th key={hi} className="px-4 py-2.5 text-left font-semibold text-foreground/80 whitespace-nowrap"
                    dangerouslySetInnerHTML={{ __html: inlineMd(h) }}
                  />
                ))}
              </tr>
            </thead>
            <tbody>
              {bodyRows.map((row, ri) => (
                <tr key={ri} className={ri % 2 === 0 ? "" : "bg-foreground/[0.02]"}>
                  {row.map((cell, ci) => (
                    <td key={ci} className="px-4 py-2 text-foreground/70 border-t border-border/50"
                      dangerouslySetInnerHTML={{ __html: inlineMd(cell) }}
                    />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    if (trimmed.startsWith("### ")) {
      elements.push(<h3 key={key++} className="font-serif text-lg font-bold mt-6 mb-2">{trimmed.slice(4)}</h3>);
    } else if (trimmed.startsWith("## ")) {
      elements.push(<h2 key={key++} className="font-serif text-xl font-bold mt-8 mb-3">{trimmed.slice(3)}</h2>);
    } else if (trimmed.startsWith("# ")) {
      elements.push(<h1 key={key++} className="font-serif text-2xl font-bold mt-8 mb-3">{trimmed.slice(2)}</h1>);
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      elements.push(
        <li key={key++} className="text-sm text-foreground/70 leading-relaxed ml-4 list-disc"
          dangerouslySetInnerHTML={{ __html: inlineMd(trimmed.slice(2)) }}
        />
      );
    } else if (/^\d+\.\s/.test(trimmed)) {
      elements.push(
        <li key={key++} className="text-sm text-foreground/70 leading-relaxed ml-4 list-decimal"
          dangerouslySetInnerHTML={{ __html: inlineMd(trimmed.replace(/^\d+\.\s/, "")) }}
        />
      );
    } else {
      elements.push(
        <p key={key++} className="text-sm text-foreground/70 leading-relaxed mb-3"
          dangerouslySetInnerHTML={{ __html: inlineMd(trimmed) }}
        />
      );
    }
    i++;
  }
  return elements;
}

function inlineMd(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, '<code class="bg-foreground/5 px-1 py-0.5 rounded text-xs">$1</code>');
}

/* ------------------------------------------------------------------ */
/* Immigration Guide Page (individual)                                */
/* ------------------------------------------------------------------ */
export default function ImmigrationGuidePage() {
  const { slug } = useParams<{ slug: string }>();
  const [guide, setGuide] = useState<ImmigrationGuide | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  // Find placeholder info
  const placeholder = GUIDE_PLACEHOLDERS.find((g) => g.slug === slug);
  const catInfo = placeholder ? GUIDE_CATEGORIES.find((c) => c.key === placeholder.category) : null;

  useEffect(() => {
    if (!slug) return;
    getGuideBySlug(slug).then((data) => {
      setGuide(data);
      setLoading(false);
      if (!data && !placeholder) setNotFound(true);
    });
  }, [slug]);

  const title = guide?.title || placeholder?.title || "Immigration Guide";
  const description = guide?.meta_description || `${title} — comprehensive immigration guide for Indian Americans from The Videshi.`;

  return (
    <>
      <Helmet>
        <title>{title} | Immigration Guides | The Videshi</title>
        <meta name="description" content={description} />
        <meta property="og:title" content={`${title} | The Videshi`} />
        <meta property="og:url" content={`https://www.thevideshi.com/immigration/guides/${slug}`} />
        <link rel="canonical" href={`https://www.thevideshi.com/immigration/guides/${slug}`} />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* Hero */}
        <section className="relative mb-8 -mx-4 px-4 py-10 md:py-14 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-2 mb-3">
              <Link to="/immigration" className="text-xs text-amber-300/70 hover:text-amber-300">Immigration Hub</Link>
              <span className="text-amber-300/30">›</span>
              <Link to="/immigration/guides" className="text-xs text-amber-300/70 hover:text-amber-300">Guides</Link>
              {catInfo && (
                <>
                  <span className="text-amber-300/30">›</span>
                  <span className="text-xs text-amber-300/50">{catInfo.label}</span>
                </>
              )}
            </div>
            <h1 className="font-serif text-3xl md:text-4xl font-bold tracking-tight text-white flex items-center gap-3">
              {placeholder && <span className="text-3xl">{placeholder.emoji}</span>}
              {title}
            </h1>
            {guide?.subtitle && (
              <p className="text-white/60 mt-3 text-base md:text-lg">{guide.subtitle}</p>
            )}
            {guide?.reading_time_min && (
              <p className="text-white/40 mt-2 text-sm">{guide.reading_time_min} min read · Last updated {new Date(guide.last_updated).toLocaleDateString("en-US", { month: "long", year: "numeric" })}</p>
            )}
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : notFound ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-3">🔍</p>
            <p className="text-lg font-medium">Guide not found</p>
            <Link to="/immigration/guides" className="text-sm text-primary mt-2 inline-block">← Back to all guides</Link>
          </div>
        ) : guide ? (
          /* Render guide content */
          <article className="max-w-3xl mx-auto">
            <div className="prose-container">
              {renderMarkdown(guide.content)}
            </div>

            {/* Bottom nav */}
            <div className="mt-12 pt-6 border-t border-border flex items-center justify-between">
              <Link to="/immigration/guides" className="text-sm text-primary hover:text-primary/80 font-medium">
                ← All Guides
              </Link>
              <Link to="/immigration" className="text-sm text-primary hover:text-primary/80 font-medium">
                Immigration Hub →
              </Link>
            </div>
          </article>
        ) : (
          /* Coming soon */
          <div className="max-w-2xl mx-auto text-center py-16">
            <span className="text-6xl block mb-4">{placeholder?.emoji || "📝"}</span>
            <h2 className="font-serif text-2xl font-bold mb-3">{title}</h2>
            <p className="text-foreground/60 mb-6">
              This guide is currently being written by our editorial team. We're creating comprehensive, Indian-diaspora-focused content that goes beyond generic advice.
            </p>
            <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-500/10 text-amber-600 rounded-full text-sm font-semibold">
              🚧 Coming Soon
            </div>
            <div className="mt-8">
              <Link to="/immigration/guides" className="text-sm text-primary hover:text-primary/80 font-medium">
                ← Browse available guides
              </Link>
            </div>
          </div>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
