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
          <div className="mt-6 flex flex-wrap gap-x-2 gap-y-1 text-xs text-muted-foreground items-center">
            {article.author && (
              <>
                <span>By {article.author}</span>
                <span>·</span>
              </>
            )}
            <span>{formatLongDate(article.published_at)}</span>
            <span>·</span>
            <span>{time} min read</span>
            <span className="ml-auto flex gap-1.5">
              <a
                href={`https://api.whatsapp.com/send?text=${encodeURIComponent(article.title + ' — The Videshi\n' + window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#25D366]/10 text-[#25D366] hover:bg-[#25D366]/20 transition-colors"
                aria-label="Share on WhatsApp"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
              </a>
              <a
                href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(article.title + ' — The Videshi')}&url=${encodeURIComponent(window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-foreground/5 text-foreground/60 hover:bg-foreground/10 transition-colors"
                aria-label="Share on X"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              </a>
              <a
                href={`https://www.threads.net/intent/post?text=${encodeURIComponent(article.title + ' — The Videshi ' + window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-foreground/5 text-foreground/60 hover:bg-foreground/10 transition-colors"
                aria-label="Share on Threads"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.59 12c.025 3.083.717 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.361-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.96-.065-1.17.408-2.266 1.33-3.084.88-.783 2.15-1.263 3.578-1.352 1.072-.067 2.073.039 2.99.272-.065-1.183-.477-2.075-1.233-2.606-.81-.57-1.947-.83-3.378-.777l-.12-.002c-1.182.05-2.094.376-2.713.97-.655.63-.99 1.49-.997 2.554l-2.12-.02c.01-1.57.56-2.876 1.59-3.766.952-.82 2.258-1.287 3.787-1.355l.163-.004c1.856-.064 3.43.322 4.604 1.148 1.254.882 1.936 2.243 2.04 4.047.518.2.998.467 1.436.808 1.082.845 1.8 2.06 2.134 3.61.44 2.04-.03 4.333-1.822 6.093-1.872 1.838-4.162 2.628-7.376 2.652z"/></svg>
              </a>
              <button
                onClick={() => { navigator.clipboard.writeText(window.location.href); }}
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-foreground/5 text-foreground/60 hover:bg-foreground/10 transition-colors"
                aria-label="Copy link"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
              </button>
            </span>
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
