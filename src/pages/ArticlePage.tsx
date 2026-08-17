import { useCallback, useEffect, useState } from "react";
import { Link, useParams, Navigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import SocialEmbed, { detectSocialUrl, MinimalTweetEmbed } from "@/components/SocialEmbed";
import XOfficialEmbed from "@/components/XOfficialEmbed";
import SocialPhotoStrip, { parseSocialPhotos } from "@/components/SocialPhotoStrip";
import HeroImage from "@/components/HeroImage";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import NewsletterSignup from "@/components/NewsletterSignup";
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
import SocialEmbeds from "@/components/SocialEmbeds";
import PhotoScrollStrip from "@/components/PhotoScrollStrip";
import ArticleReactions from "@/components/ArticleReactions";
import ArticleBlocks, { tryParseBlocks } from "@/components/ArticleBlocks";
import YouTubeEmbed, { extractYouTubeId } from "@/components/YouTubeEmbed";
import ChampionsTimeline from "@/components/ChampionsTimeline";

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
    <div className="max-w-4xl mx-auto mt-8">
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
      {open && (() => {
        /* Deduplicate by domain — show each site name once */
        const seen = new Set<string>();
        const dedupedSites = sources.reduce<{ domain: string; siteName: string }[]>((acc, s) => {
          const domain = s.url
            ? (() => { try { return new URL(s.url).hostname.replace("www.", ""); } catch { return ""; } })()
            : "";
          const key = domain || s.label;
          if (!seen.has(key)) {
            seen.add(key);
            /* Pretty site name: strip TLD, capitalize, handle multi-word domains */
            const siteName = domain
              ? domain.replace(/\.(com|org|net|co\.in|co\.uk|gov|gov\.in|io|xml)$/i, "")
                  .split(/[.-]/).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")
              : s.label.split("—")[0].split("–")[0].trim();
            acc.push({ domain, siteName });
          }
          return acc;
        }, []);

        return (
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
              {dedupedSites.map((s, i) => (
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
                  {s.domain ? (
                    <img
                      src={`https://www.google.com/s2/favicons?domain=${s.domain}&sz=16`}
                      alt=""
                      width={14}
                      height={14}
                      style={{ borderRadius: "50%", flexShrink: 0 }}
                    />
                  ) : (
                    <span style={{ width: 14, height: 14, flexShrink: 0 }} />
                  )}
                  <span>{s.siteName}</span>
                </li>
              ))}
            </ul>
          </div>
        );
      })()}
    </div>
  );
}

/* ── Markdown renderer that auto-detects social embed URLs ── */

const CHAMPIONS_HEADING_RE = /^##\s+Every Indian American Champion.*$/m;
const YOUTUBE_TAG_RE = /<youtube>(.*?)<\/youtube>/;

function MarkdownWithEmbeds({
  body,
  heroImageUrl,
  title,
}: {
  body: string;
  heroImageUrl?: string;
  title: string;
}) {
  // Pre-process: strip the champions table section (component renders it)
  let processedBody = body;
  if (CHAMPIONS_HEADING_RE.test(processedBody)) {
    // Remove from the heading through the stat line + footnote
    processedBody = processedBody.replace(
      /## Every Indian American Champion[^\n]*\n[\s\S]*?\*\*31 Indian American champions\.[^\n]*\n?/,
      "<!-- champions-timeline -->\n"
    );
    // Also remove the ★ footnote line if still present
    processedBody = processedBody.replace(
      /★ = Co-champion[^\n]*\n?/,
      ""
    );
  }

  // Split body into chunks: lines that are bare social URLs become embed
  // blocks; <youtube> tags become YouTube embeds; the champions-timeline
  // marker becomes its own chunk; everything else passes to ReactMarkdown.
  const lines = processedBody.split("\n");
  const chunks: any[] = [];
  let mdBuf: string[] = [];

  const flush = () => {
    if (mdBuf.length) {
      const text = mdBuf.join("\n");
      // Check for <youtube> tags inside the markdown buffer
      if (YOUTUBE_TAG_RE.test(text)) {
        // Split around <youtube> tags
        const parts = text.split(/(<youtube>.*?<\/youtube>)/g);
        for (const part of parts) {
          const ytMatch = part.match(/<youtube>(.*?)<\/youtube>/);
          if (ytMatch && extractYouTubeId(ytMatch[1])) {
            chunks.push({ kind: "youtube", url: ytMatch[1] });
          } else if (part.trim()) {
            chunks.push({ kind: "md", text: part });
          }
        }
      } else {
        chunks.push({ kind: "md", text });
      }
      mdBuf = [];
    }
  };

  let socialPhotosBuf: string[] | null = null;

  for (const line of lines) {
    // Accumulate <!-- social-photos ... --> blocks
    if (line.trim().startsWith("<!-- social-photos")) {
      flush();
      // Check if single-line (unlikely but handle it)
      if (line.trim().endsWith("-->")) {
        const sp = parseSocialPhotos(line.trim());
        if (sp) chunks.push({ kind: "social-photos", ...sp });
      } else {
        socialPhotosBuf = [line];
      }
      continue;
    }
    if (socialPhotosBuf !== null) {
      socialPhotosBuf.push(line);
      if (line.trim().endsWith("-->")) {
        const block = socialPhotosBuf.join("\n");
        const sp = parseSocialPhotos(block);
        if (sp) chunks.push({ kind: "social-photos", ...sp });
        socialPhotosBuf = null;
      }
      continue;
    }

    if (line.trim() === "<!-- champions-timeline -->") {
      flush();
      chunks.push({ kind: "champions-timeline" });
      continue;
    }
    const embed = detectSocialUrl(line);
    // Official X embed: x-official:URL or x-video:URL
    const xOfficialMatch = line.trim().match(/^x-(official|video):(.+)$/);
    if (xOfficialMatch) {
      flush();
      chunks.push({ kind: "x-official", url: xOfficialMatch[2].trim(), video: xOfficialMatch[1] === "video" });
    } else if (embed) {
      flush();
      chunks.push({ kind: "embed", ...embed });
    } else {
      mdBuf.push(line);
    }
  }
  flush();

  const norm = (u?: string) => (u ?? "").replace(/&amp;/g, "&").split("?")[0];

  const mdComponents = {
    h1: () => null as any,
    a: ({ href, children, ...props }: any) => {
      const arr = Array.isArray(children) ? children : [children];
      const onlyImage =
        arr.filter((c: any) => typeof c !== "string" || c.trim() !== "").length === 1 &&
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
    img: ({ src, alt }: any) => {
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
      if (heroImageUrl && norm(src) === norm(heroImageUrl)) {
        return null;
      }
      return <HeroImage src={src} alt={alt || title} loading="lazy" className="w-full rounded-lg" />;
    },
  };

  return (
    <>
      {(chunks as any[]).map((chunk, i) =>
        chunk.kind === "social-photos" ? (
          <SocialPhotoStrip key={i} images={chunk.images} via={chunk.via} platform={chunk.platform} postUrl={chunk.postUrl} />
        ) : chunk.kind === "embed" ? (
          <SocialEmbed key={i} platform={chunk.platform} url={chunk.url} />
        ) : chunk.kind === "x-official" ? (
          <XOfficialEmbed key={i} url={chunk.url} video={chunk.video} />
        ) : chunk.kind === "youtube" ? (
          <YouTubeEmbed key={i} url={chunk.url} />
        ) : chunk.kind === "champions-timeline" ? (
          <ChampionsTimeline key={i} />
        ) : (
          <ReactMarkdown key={i} remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]} components={mdComponents}>
            {chunk.text}
          </ReactMarkdown>
        )
      )}
    </>
  );
}

/* ── Known travel-guide article slugs → /travel/:destination ────── */
const TRAVEL_GUIDE_REDIRECTS: Record<string, string> = {
  // Original guides
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
  // Added May 2026
  "thailand-travel-guide-diaspora": "thailand",
  "dubai-travel-guide-diaspora": "dubai",
  "singapore-travel-guide-diaspora": "singapore",
  "kashmir-travel-guide-diaspora": "kashmir",
  "himachal-pradesh-travel-guide-diaspora": "himachal-pradesh",
  "vietnam-travel-guide-diaspora": "vietnam",
  "italy-travel-guide-diaspora": "italy",
  "greece-travel-guide-diaspora": "greece",
  "cancun-travel-guide-diaspora": "cancun",
  "hawaii-travel-guide-diaspora": "hawaii",
  "australia-travel-guide-diaspora": "australia",
  "france-travel-guide-diaspora": "france",
  "japan-travel-guide-diaspora": "japan",
};

export default function ArticlePage() {
  const { slug = "" } = useParams();
  const [article, setArticle] = useState<Article | null | undefined>(undefined);
  const [related, setRelated] = useState<Article[]>([]);
  const [fsIdx, setFsIdx] = useState<number | null>(null);
  const [fsPhotos, setFsPhotos] = useState<{src: string; caption: string}[]>([]);

  const openFullscreen = useCallback((photos: {src: string; caption: string}[], idx: number) => {
    setFsPhotos(photos);
    setFsIdx(idx);
  }, []);
  const fsNext = useCallback(() => {
    setFsIdx((i) => i !== null ? (i + 1) % fsPhotos.length : null);
  }, [fsPhotos.length]);
  const fsPrev = useCallback(() => {
    setFsIdx((i) => i !== null ? (i - 1 + fsPhotos.length) % fsPhotos.length : null);
  }, [fsPhotos.length]);
  const fsClose = useCallback(() => { setFsIdx(null); setFsPhotos([]); }, []);

  // Lock body scroll when fullscreen lightbox is open
  useEffect(() => {
    if (fsIdx !== null) {
      document.body.style.overflow = "hidden";
      return () => { document.body.style.overflow = ""; };
    }
  }, [fsIdx !== null]);

  useEffect(() => {
    if (fsIdx === null) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") fsClose();
      else if (e.key === "ArrowRight") fsNext();
      else if (e.key === "ArrowLeft") fsPrev();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [fsIdx, fsClose, fsNext, fsPrev]);

  useEffect(() => {
    // Redirect is handled in render, skip fetch for travel guides
    if (TRAVEL_GUIDE_REDIRECTS[slug]) return;
    let cancelled = false;

    // Reset state when slug changes
    setArticle(undefined);
    setRelated([]);

    // Fallback: original Supabase fetch
    const fetchFromSupabase = async () => {
      const a = await getArticleBySlug(slug);
      if (cancelled) return;
      setArticle(a ?? null);
      if (a) setRelated(await getRelatedArticles(a.slug, a.category, 3));
      window.scrollTo(0, 0);
    };

    // Race static JSON vs Supabase — show whichever arrives first,
    // but always prefer Supabase data (always fresh after admin edits)
    let shown = false;

    const fromStatic = fetch(`/data/articles/${slug}.json`)
      .then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then(async (a) => {
        if (cancelled || shown) return;
        shown = true;
        setArticle(a);
        try {
          const rel = await getRelatedArticles(a.slug, a.category, 3);
          if (!cancelled) setRelated(rel);
        } catch {}
        window.scrollTo(0, 0);
      })
      .catch(() => {});

    const fromLive = getArticleBySlug(slug).then(async (a) => {
      if (cancelled) return;
      if (!a) {
        // Supabase returned nothing — don't set shown, let fallback handle it
        return;
      }
      shown = true;
      setArticle(a);
      try {
        const rel = await getRelatedArticles(a.slug, a.category, 3);
        if (!cancelled) setRelated(rel);
      } catch {}
      window.scrollTo(0, 0);
    }).catch(() => {});

    // If both fail, fall back
    Promise.allSettled([fromStatic, fromLive]).then(() => {
      if (!shown && !cancelled) fetchFromSupabase().catch(() => {
        if (!cancelled) setArticle(null);
      });
    });

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
        <meta property="article:published_time" content={article.published_at || ""} />
        <meta property="article:section" content={article.category || "News"} />
        {article.tags?.map((tag, i) => (
          <meta key={i} property="article:tag" content={tag} />
        ))}
        <link rel="canonical" href={`https://www.thevideshi.com/articles/${article.slug}`} />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            headline: article.title,
            ...(article.excerpt ? { description: article.excerpt } : {}),
            ...(article.published_at ? { datePublished: article.published_at } : {}),
            ...(article.published_at ? { dateModified: article.updated_at || article.published_at } : {}),
            ...(article.hero_image_url ? { image: article.hero_image_url } : {}),
            ...(article.category ? { articleSection: article.category } : {}),
            url: `https://www.thevideshi.com/articles/${article.slug}`,
            mainEntityOfPage: {
              "@type": "WebPage",
              "@id": `https://www.thevideshi.com/articles/${article.slug}`
            },
            inLanguage: "en",
            isAccessibleForFree: true,
            author: { "@type": "Organization", name: "The Videshi" },
            publisher: {
              "@type": "Organization",
              name: "The Videshi",
              url: "https://www.thevideshi.com",
              logo: {
                "@type": "ImageObject",
                url: "https://www.thevideshi.com/logo.jpg"
              }
            },
          })}
        </script>
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: "https://www.thevideshi.com" },
              ...(article.category ? [{ "@type": "ListItem", position: 2, name: article.category, item: `https://www.thevideshi.com/${article.category.toLowerCase().replace(/\s+&\s+/g, "-").replace(/\s+/g, "-")}` }] : []),
              { "@type": "ListItem", position: article.category ? 3 : 2, name: article.title },
            ],
          })}
        </script>
      </Helmet>

      <Masthead />

      <main className="container flex-1 pt-8 md:pt-12">
        <article className="max-w-4xl mx-auto">
          <p className="smallcaps text-primary">{article.category}</p>
          <h1 className="font-serif text-[2rem] md:text-5xl lg:text-[3.5rem] leading-[1.08] mt-3 font-bold">
            {article.title}
          </h1>
          <p className="mt-5 text-lg md:text-xl text-foreground/75 font-serif italic leading-relaxed">
            {article.excerpt}
          </p>
          <div className="mt-6 flex flex-wrap gap-x-2 gap-y-1 text-xs text-muted-foreground items-center">
            <span>{formatLongDate(article.published_at)}</span>
            <span>·</span>
            <span>{time} min read</span>
            <span className="ml-auto flex gap-1.5">
              <a
                href={`https://api.whatsapp.com/send?text=${encodeURIComponent(window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#25D366]/10 text-[#25D366] hover:bg-[#25D366]/20 transition-colors"
                aria-label="Share on WhatsApp"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
              </a>
              <a
                href={`https://x.com/intent/post?text=${encodeURIComponent(article.title + ' — The Videshi ' + window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-foreground/5 text-foreground/60 hover:bg-foreground/10 transition-colors"
                aria-label="Share on X"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              </a>
              <a
                href={`https://www.threads.com/intent/post?text=${encodeURIComponent(article.title + ' — The Videshi ' + window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-foreground/5 text-foreground/60 hover:bg-foreground/10 transition-colors"
                aria-label="Share on Threads"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.59 12c.025 3.083.717 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.361-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.96-.065-1.17.408-2.266 1.33-3.084.88-.783 2.15-1.263 3.578-1.352 1.072-.067 2.073.039 2.99.272-.065-1.183-.477-2.075-1.233-2.606-.81-.57-1.947-.83-3.378-.777l-.12-.002c-1.182.05-2.094.376-2.713.97-.655.63-.99 1.49-.997 2.554l-2.12-.02c.01-1.57.56-2.876 1.59-3.766.952-.82 2.258-1.287 3.787-1.355l.163-.004c1.856-.064 3.43.322 4.604 1.148 1.254.882 1.936 2.243 2.04 4.047.518.2.998.467 1.436.808 1.082.845 1.8 2.06 2.134 3.61.44 2.04-.03 4.333-1.822 6.093-1.872 1.838-4.162 2.628-7.376 2.652z"/></svg>
              </a>
              <button
                onClick={(e) => {
                  navigator.clipboard.writeText(window.location.href);
                  const btn = e.currentTarget;
                  btn.classList.add('text-green-600');
                  const orig = btn.innerHTML;
                  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-3.5 h-3.5"><path d="M20 6L9 17l-5-5"/></svg>';
                  setTimeout(() => { btn.innerHTML = orig; btn.classList.remove('text-green-600'); }, 1500);
                }}
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-foreground/5 text-foreground/60 hover:bg-foreground/10 transition-colors"
                aria-label="Copy link"
                title="Copy link"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
              </button>
            </span>
          </div>
        </article>

        {article.gallery_images && article.gallery_images.length > 0 ? (
          <div className="max-w-4xl mx-auto">
            <style>{`.article-prose table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.9rem; }
.article-prose th, .article-prose td { border: 1px solid #e5e5e5; padding: 0.5rem 0.75rem; text-align: left; }
.article-prose th { background: #f5f5f4; font-weight: 600; }
.article-prose tr:nth-child(even) { background: #fafaf9; }
.article-prose table { overflow-x: auto; display: block; }`}</style>
            <PhotoScrollStrip
              photos={[
                ...(article.hero_image_url ? [{ src: article.hero_image_url, caption: article.image_caption || article.image_attribution || "" }] : []),
                ...article.gallery_images
                  .filter((img: { url: string }) => img.url !== article.hero_image_url)
                  .map((img: { url: string; caption: string }) => ({ src: img.url, caption: img.caption })),
              ]}
              itemWidth={500}
              itemHeight={320}
              objectFit="contain"
              onPhotoClick={openFullscreen}
            />
          </div>
        ) : article.hero_image_url && article.hero_image_url.trim().length > 0 ? (
          <HeroMedia
            url={article.hero_image_url}
            alt={article.title}
            credit={article.image_attribution ?? null}
            caption={article.image_caption ?? null}
            category={article.category}
          />
        ) : null}

        <div className="article-prose max-w-4xl mx-auto mt-12">
          {(() => {
            const blocks = tryParseBlocks(article.body);
            if (blocks) return <ArticleBlocks blocks={blocks} />;

            // Detect HTML bodies (start with HTML block tags) and render natively
            const isHtml = /^\s*<(?:!--|(?:p|h[1-6]|div|section|article)\b)/i.test(article.body);
            if (isHtml) {
              let processedHtml = article.body;

              // Transform <youtube> tags into responsive iframe embeds
              processedHtml = processedHtml.replace(
                /<youtube>(.*?)<\/youtube>/g,
                (_: string, url: string) => {
                  const m = url.match(/(?:youtube\.com\/watch\?.*v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/shorts\/)([A-Za-z0-9_-]{11})/);
                  if (!m) return url;
                  return `<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin:28px 0;border-radius:12px"><iframe src="https://www.youtube.com/embed/${m[1]}?rel=0" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0" allowfullscreen></iframe></div>`;
                }
              );

              // Transform markdown headings ## / ### into <h2> / <h3>
              processedHtml = processedHtml.replace(
                /^(#{2,3})\s+(.+)$/gm,
                (_: string, hashes: string, text: string) => {
                  const level = hashes.length;
                  return `<h${level}>${text.trim()}</h${level}>`;
                }
              );

              // Pre-process: ensure bare social-embed URLs are isolated between
              // double-newlines so the paragraph splitter treats them as separate chunks.
              processedHtml = processedHtml.replace(
                /(\n?)(\s*)(https?:\/\/(?:(?:www\.)?(?:twitter|x)\.com\/\w+\/status\/\d+|(?:www\.)?instagram\.com\/(?:p|reel)\/[\w-]+)\/?)\s*(\n?)/g,
                '\n\n$3\n\n'
              );

              // Wrap plain-text blocks in <p> tags so spacing renders correctly.
              // Split by double-newlines, leave HTML block elements alone, wrap the rest.
              const paraChunks = processedHtml.split(/\n\n+/);
              processedHtml = paraChunks.map((chunk: string) => {
                const trimmed = chunk.trim();
                if (!trimmed) return '';
                // Already an HTML block element — leave as-is
                if (/^\s*<(?:div|h[1-6]|figure|blockquote|ul|ol|table|section|article|aside|nav|header|footer|iframe|style|p[\s>])/i.test(trimmed)) {
                  return trimmed;
                }
                // Bare social-embed URL — leave unwrapped so detectSocialUrl can match it
                if (/^https?:\/\/(?:(?:www\.)?(?:twitter|x)\.com\/\w+\/status\/\d+|(?:www\.)?instagram\.com\/(?:p|reel)\/[\w-]+)\/?$/.test(trimmed)) {
                  return trimmed;
                }
                // Plain text — wrap in <p>
                return `<p>${trimmed}</p>`;
              }).filter(Boolean).join('\n\n');

              // Transform markdown images ![alt](url) into HTML img tags
              processedHtml = processedHtml.replace(
                /!\[([^\]]*)\]\((https?:\/\/[^)]+)\)/g,
                (_: string, alt: string, url: string) => {
                  return `<figure style="margin:28px auto;text-align:center"><img src="${url}" alt="${alt}" style="max-width:100%;border-radius:8px" loading="lazy"><figcaption style="font-size:0.85rem;color:#666;margin-top:8px">${alt}</figcaption></figure>`;
                }
              );

              // Transform markdown blockquotes > **"text"** into pull-quote blockquotes
              processedHtml = processedHtml.replace(
                /^>\s*\*\*"([^"]+)"\*\*\s*$/gm,
                (_: string, quote: string) => {
                  return `<blockquote class="pull-quote"><p>"${quote}"</p></blockquote>`;
                }
              );

              // Detect bare social-embed URLs in the HTML body and render
              // them as React components (same logic as MarkdownWithEmbeds).
              const htmlLines = processedHtml.split("\n");
              const htmlChunks: Array<{ kind: "html"; html: string } | { kind: "embed"; platform: "instagram" | "twitter"; url: string }> = [];
              let htmlBuf: string[] = [];
              const flushHtml = () => {
                if (htmlBuf.length) {
                  htmlChunks.push({ kind: "html", html: htmlBuf.join("\n") });
                  htmlBuf = [];
                }
              };
              for (const line of htmlLines) {
                const embed = detectSocialUrl(line);
                if (embed) {
                  flushHtml();
                  htmlChunks.push({ kind: "embed", ...embed });
                } else {
                  htmlBuf.push(line);
                }
              }
              flushHtml();

              // Also insert social_embeds from the JSON field mid-article
              const socialEmbeds = article.social_embeds ?? [];
              if (socialEmbeds.length > 0 && htmlChunks.every(c => c.kind === "html")) {
                // No inline embeds found — insert social_embeds at a split point
                const fullHtml = processedHtml;
                const h2Matches = [...fullHtml.matchAll(/<h2[\s>]/gi)];
                let splitIdx = -1;
                if (h2Matches.length >= 2) {
                  splitIdx = h2Matches[1].index!;
                } else {
                  const paraBreaks = [...fullHtml.matchAll(/<\/p>/gi)];
                  const target = Math.max(1, Math.floor(paraBreaks.length / 3));
                  if (paraBreaks.length >= 3 && paraBreaks[target]) {
                    splitIdx = paraBreaks[target].index! + paraBreaks[target][0].length;
                  }
                }

                if (splitIdx > 0) {
                  const firstHalf = fullHtml.slice(0, splitIdx);
                  const secondHalf = fullHtml.slice(splitIdx);
                  return (
                    <>
                      <div className="article-html" dangerouslySetInnerHTML={{ __html: firstHalf }} />
                      <SocialEmbeds embeds={socialEmbeds} />
                      <div className="article-html" dangerouslySetInnerHTML={{ __html: secondHalf }} />
                    </>
                  );
                }
              }

              return (
                <>
                  {htmlChunks.map((chunk, i) =>
                    chunk.kind === "embed" && chunk.platform === "twitter" ? (
                      <MinimalTweetEmbed key={i} url={chunk.url} />
                    ) : chunk.kind === "embed" ? (
                      <SocialEmbed key={i} platform={chunk.platform} url={chunk.url} />
                    ) : (
                      <div key={i} className="article-html" dangerouslySetInnerHTML={{ __html: chunk.html }} />
                    )
                  )}
                  {socialEmbeds.length > 0 && <SocialEmbeds embeds={socialEmbeds} />}
                </>
              );
            }

            return (
              <>
                <MarkdownWithEmbeds
                  body={article.body}
                  heroImageUrl={article.hero_image_url}
                  title={article.title}
                />
                {(article.social_embeds ?? []).length > 0 && (
                  <SocialEmbeds embeds={article.social_embeds!} />
                )}
              </>
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

        {["immigration", "nri-world", "lifestyle-health", "news"].includes(article.category) && (
          <section className="my-10 mx-auto max-w-4xl">
            <a
              href="/stories/submit"
              className="block rounded-xl border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-6 text-center transition hover:shadow-md hover:border-amber-300"
            >
              <p className="text-2xl mb-2">✍️</p>
              <p className="font-semibold text-gray-900 text-lg">Your Diaspora Story Matters</p>
              <p className="text-gray-600 mt-1 text-sm leading-relaxed">
                Whether it's a visa struggle, a career breakthrough, finding community abroad, or building something back home — the diaspora learns from each other. Share your experience.
              </p>
              <span className="inline-block mt-3 text-sm font-medium text-amber-700 hover:text-amber-900">
                Share Your Story on Voices →
              </span>
            </a>
          </section>
        )}

        {/* Emoji reactions */}
        <ArticleReactions articleId={article.id} initialReactions={article.reactions as Record<string, number> | undefined} />

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

        <NewsletterSignup variant="inline" />
      </main>

      <SiteFooter />

      {fsIdx !== null && fsPhotos.length > 0 && (() => {
        return (
          <>
          <style>{`@keyframes lbFadeIn { from { opacity: 0; } to { opacity: 1; } }
.fs-scroll::-webkit-scrollbar { display: none; }`}</style>
          <div
            className="fixed inset-0 z-[9999] bg-black flex flex-col"
            style={{ animation: "lbFadeIn 0.15s ease-out" }}>
            <button onClick={fsClose} className="absolute top-4 right-5 bg-transparent border-none text-white text-3xl cursor-pointer z-10">✕</button>
            <div className="absolute top-5 left-1/2 -translate-x-1/2 text-white/70 text-sm font-medium z-10">
              {fsIdx + 1} / {fsPhotos.length}
            </div>
            <div
              ref={(el) => {
                if (el) {
                  // Scroll to initial index
                  el.scrollLeft = fsIdx * el.clientWidth;
                  // Track scroll position to update counter
                  const onScroll = () => {
                    const idx = Math.round(el.scrollLeft / el.clientWidth);
                    setFsIdx(Math.min(idx, fsPhotos.length - 1));
                  };
                  el.onscroll = onScroll;
                }
              }}
              className="fs-scroll flex-1 flex overflow-x-auto overflow-y-hidden"
              style={{ scrollSnapType: "x mandatory", scrollBehavior: "smooth" }}
            >
              {fsPhotos.map((photo, i) => (
                <div
                  key={i}
                  className="flex-shrink-0 w-screen h-full flex flex-col items-center justify-center"
                  style={{ scrollSnapAlign: "start" }}
                  onClick={(e) => { if (e.target === e.currentTarget) fsClose(); }}
                >
                  <img src={photo.src} alt={photo.caption}
                    className="max-w-[90vw] max-h-[75vh] object-contain rounded" />
                  {photo.caption && (
                    <div className="mt-4 text-white/85 text-[15px] font-medium text-center max-w-[80vw]">{photo.caption}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
          </>
        );
      })()}
    </div>
  );
}
