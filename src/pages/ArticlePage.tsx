import { useEffect, useState } from "react";
import { Link, useParams, Navigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import SectionRule from "@/components/SectionRule";
import {
  Article,
  formatLongDate,
  getArticleBySlug,
  getRelatedArticles,
  readingTime,
} from "@/lib/articles";
import HeroMedia from "@/components/HeroMedia";
import PhotoScrollStrip from "@/components/PhotoScrollStrip";
import ArticleBlocks, { tryParseBlocks } from "@/components/ArticleBlocks";

/* ------------------------------------------------------------------ */
/* Gemini-style compact sources pill                                  */
/* ------------------------------------------------------------------ */
function SourcesPill({
  sources,
  domains,
}: {
  sources: { label: string; url?: string }[];
  domains: string[];
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="max-w-2xl mx-auto mt-8">
      {/* Pill trigger */}
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          padding: "6px 14px 6px 10px",
          borderRadius: "999px",
          border: "1px solid hsl(var(--border))",
          background: "hsl(var(--card))",
          cursor: "pointer",
          transition: "background 0.15s, border-color 0.15s",
          fontSize: "13px",
          color: "hsl(var(--muted-foreground))",
          fontFamily: "var(--font-sans, sans-serif)",
          fontWeight: 500,
        }}
      >
        {/* Stacked favicons */}
        <span style={{ display: "flex", alignItems: "center", marginRight: "2px" }}>
          {domains.map((d, i) => (
            <img
              key={d}
              src={`https://www.google.com/s2/favicons?domain=${d}&sz=16`}
              alt=""
              width={16}
              height={16}
              style={{
                borderRadius: "50%",
                border: "1.5px solid hsl(var(--card))",
                marginLeft: i === 0 ? 0 : "-6px",
                position: "relative",
                zIndex: domains.length - i,
                background: "hsl(var(--card))",
              }}
            />
          ))}
        </span>
        <span>
          {sources.length > domains.length && `+${sources.length - domains.length} `}
          {sources.length === 1 ? "Source" : `${sources.length} Sources`}
        </span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          style={{
            transition: "transform 0.2s",
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
          }}
        >
          <path
            d="M3 4.5L6 7.5L9 4.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Expanded sources list */}
      {open && (
        <div
          style={{
            marginTop: "8px",
            padding: "12px 16px",
            borderRadius: "12px",
            border: "1px solid hsl(var(--border))",
            background: "hsl(var(--card))",
            fontSize: "13px",
            lineHeight: "1.6",
          }}
        >
          <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
            {sources.map((s, i) => {
              const domain = s.url
                ? (() => {
                    try { return new URL(s.url).hostname.replace("www.", ""); } catch { return ""; }
                  })()
                : "";
              return (
                <li
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "4px 0",
                    color: "hsl(var(--muted-foreground))",
                  }}
                >
                  {domain ? (
                    <img
                      src={`https://www.google.com/s2/favicons?domain=${domain}&sz=16`}
                      alt=""
                      width={14}
                      height={14}
                      style={{ borderRadius: "50%", flexShrink: 0 }}
                    />
                  ) : (
                    <span style={{ width: 14, height: 14, flexShrink: 0 }} />
                  )}
                  {s.url ? (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: "hsl(var(--muted-foreground))",
                        textDecoration: "underline",
                        textUnderlineOffset: "2px",
                      }}
                    >
                      {s.label}
                    </a>
                  ) : (
                    <span>{s.label}</span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

const TRAVEL_GUIDE_REDIRECTS: Record<string, string> = {
  "rajasthan-travel-guide-diaspora": "rajasthan",
  "kerala-travel-guide-diaspora": "kerala",
  "goa-travel-guide-diaspora": "goa",
  "maldives-travel-guide-diaspora": "maldives",
  "sri-lanka-travel-guide-diaspora": "sri-lanka",
  "bali-travel-guide-diaspora": "bali",
  "london-travel-guide-diaspora": "london",
  "london-uk-travel-guide-diaspora": "london",
  "switzerland-travel-guide-diaspora": "switzerland",
  "new-zealand-travel-guide-diaspora": "new-zealand",
  "mexico-travel-guide-diaspora": "mexico",
};

export default function ArticlePage() {
  const { slug = "" } = useParams();
  const [article, setArticle] = useState<Article | null | undefined>(undefined);
  const [related, setRelated] = useState<Article[]>([]);

  useEffect(() => {
    // Redirect is handled in render, skip fetch for travel guides
    if (TRAVEL_GUIDE_REDIRECTS[slug]) return;
    let cancelled = false;
    (async () => {
      const a = await getArticleBySlug(slug);
      if (cancelled) return;
      setArticle(a ?? null);
      if (a) setRelated(await getRelatedArticles(a.slug, a.category, 3));
      window.scrollTo(0, 0);
    })();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  // Redirect travel guide articles to destination pages
  const travelDest = TRAVEL_GUIDE_REDIRECTS[slug];
  if (travelDest) {
    return <Navigate to={`/travel/${travelDest}`} replace />;
  }

  if (article === undefined) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  if (article === null) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <main className="container py-24 text-center flex-1">
          <p className="smallcaps text-primary">404</p>
          <h1 className="font-serif text-4xl mt-3">Article not found</h1>
          <Link to="/" className="inline-block mt-6 text-primary underline underline-offset-4">
            Back to homepage
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const time = readingTime(article.body);

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{article.title} — The Videshi</title>
        <meta name="description" content={article.excerpt} />
        <meta property="og:title" content={article.title} />
        <meta property="og:description" content={article.excerpt} />
        <meta property="og:type" content="article" />
        <meta property="og:image" content={article.hero_image_url} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={article.title} />
        <meta name="twitter:description" content={article.excerpt} />
        <meta name="twitter:image" content={article.hero_image_url} />
        <link rel="canonical" href={`/articles/${article.slug}`} />
      </Helmet>

      <Masthead />

      <main className="container flex-1 pt-8 md:pt-12">
        <article className="max-w-3xl mx-auto">
          <p className="smallcaps text-primary">{article.category}</p>
          <h1 className="font-serif text-[2rem] md:text-5xl lg:text-[3.5rem] leading-[1.08] mt-3 font-bold">
            {article.title}
          </h1>
          <p className="mt-5 text-lg md:text-xl text-foreground/75 font-serif italic leading-relaxed">
            {article.excerpt}
          </p>
          <div className="mt-6 flex flex-wrap gap-x-2 gap-y-1 text-xs text-muted-foreground">
            {article.author && (
              <>
                <span>By {article.author}</span>
                <span>·</span>
              </>
            )}
            <span>{formatLongDate(article.published_at)}</span>
            <span>·</span>
            <span>{time} min read</span>
          </div>
        </article>

        {article.gallery_images && article.gallery_images.length > 0 ? (
          <div className="max-w-3xl mx-auto">
            <div
              className="flex gap-3 overflow-x-auto pb-2"
              style={{ 
                scrollbarWidth: "none", 
                msOverflowStyle: "none",
                scrollSnapType: "x mandatory",
                WebkitOverflowScrolling: "touch",
                paddingLeft: "4%",
                paddingRight: "4%",
              } as React.CSSProperties}
            >
              <style>{`.article-gallery::-webkit-scrollbar { display: none; }
.article-prose table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.9rem; }
.article-prose th, .article-prose td { border: 1px solid #e5e5e5; padding: 0.5rem 0.75rem; text-align: left; }
.article-prose th { background: #f5f5f4; font-weight: 600; }
.article-prose tr:nth-child(even) { background: #fafaf9; }
.article-prose table { overflow-x: auto; display: block; }`}</style>
              {[
                ...(article.hero_image_url ? [{ src: article.hero_image_url, caption: article.image_caption || article.title }] : []),
                ...article.gallery_images
                  .filter((img) => img.url !== article.hero_image_url)
                  .map((img) => ({ src: img.url, caption: img.caption })),
              ].map((photo, i) => (
                <div
                  key={i}
                  className="flex-shrink-0 rounded-lg overflow-hidden"
                  style={{ scrollSnapAlign: "center", width: "90%" }}
                >
                  <img
                    src={photo.src}
                    alt={photo.caption || article.title}
                    loading={i === 0 ? "eager" : "lazy"}
                    style={{ display: "block", width: "100%", height: "auto", borderRadius: 8 }}
                  />
                  {photo.caption && (
                    <p className="text-xs text-muted-foreground mt-1 px-1 pb-1">{photo.caption}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : article.hero_image_url && article.hero_image_url.trim().length > 0 ? (
          <HeroMedia
            url={article.hero_image_url}
            alt={article.title}
            credit={article.image_credit ?? null}
            caption={article.image_caption ?? null}
            category={article.category}
          />
        ) : null}

        <div className="article-prose max-w-2xl mx-auto mt-12">
          {(() => {
            const blocks = tryParseBlocks(article.body);
            if (blocks) return <ArticleBlocks blocks={blocks} />;

            // Detect HTML bodies (contain <p>, <h3>, etc.) and render natively
            const isHtml = /<(?:p|h[1-6]|ul|ol|blockquote|div|figure|aside|strong|em)\b/i.test(article.body);
            if (isHtml) {
              return (
                <div
                  className="article-html"
                  dangerouslySetInnerHTML={{ __html: article.body }}
                />
              );
            }

            return (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: () => null,
                  a: ({ href, children, ...props }) => {
                    const arr = Array.isArray(children) ? children : [children];
                    const onlyImage =
                      arr.filter((c) => typeof c !== "string" || c.trim() !== "").length === 1 &&
                      arr.some(
                        (c: any) => c && typeof c === "object" && (c.type === "img" || c.props?.node?.tagName === "img")
                      );
                    if (onlyImage) return <>{children}</>;
                    return (
                      <a href={href} {...props}>
                        {children}
                      </a>
                    );
                  },
                  img: ({ src, alt }) => {
                    const norm = (u?: string) => (u ?? "").replace(/&amp;/g, "&").split("?")[0];
                    if (!src) return null;
                    if (/counter\.theconversation\.com|\/count\.gif|pixel|tracker/i.test(src)) {
                      return (
                        <img
                          src={src}
                          alt=""
                          width={1}
                          height={1}
                          aria-hidden="true"
                          referrerPolicy="no-referrer"
                          style={{ position: "absolute", width: 1, height: 1, opacity: 0, pointerEvents: "none", margin: 0 }}
                        />
                      );
                    }
                    if (article.hero_image_url && norm(src) === norm(article.hero_image_url)) {
                      return null;
                    }
                    return <img src={src} alt={alt || article.title} loading="lazy" referrerPolicy="no-referrer" />;
                  },
                }}
              >
                {article.body}
              </ReactMarkdown>
            );
          })()}
        </div>

        {article.sources && article.sources.length > 0 && (() => {
          const getDomain = (url: string) => {
            try { return new URL(url).hostname.replace("www.", ""); } catch { return ""; }
          };
          const uniqueDomains = [...new Set(article.sources.filter(s => s.url).map(s => getDomain(s.url!)))].slice(0, 3);
          return (
            <SourcesPill
              sources={article.sources}
              domains={uniqueDomains}
            />
          );
        })()}

        {related.length > 0 && (
          <section className="mt-8">
            <SectionRule label="Read More" />
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
              {related.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" />
              ))}
            </div>
          </section>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
