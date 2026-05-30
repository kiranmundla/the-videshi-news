import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { useParams, Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  fetchStoryBySlug,
  formatStoryDate,
  getCategoryLabel,
  getCategoryEmoji,
  type Story,
} from "@/lib/stories";
import { supabase } from "@/integrations/supabase/client";

const sb = supabase as any;

/* Enhanced markdown → HTML for personal essays */
function renderMarkdown(md: string): string {
  const paragraphs = md.split(/\n\n+/);
  return paragraphs
    .map((p, i) => {
      let html = p
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/\n/g, "<br />");

      // First paragraph gets a drop cap
      if (i === 0 && html.length > 20) {
        const first = html.charAt(0);
        const rest = html.slice(1);
        return `<p class="story-first-p"><span class="story-dropcap">${first}</span>${rest}</p>`;
      }

      // Short paragraphs (< 80 chars, no HTML tags) become pull quotes
      const stripped = html.replace(/<[^>]+>/g, "");
      if (stripped.length < 80 && stripped.length > 15 && !html.includes("<strong") && !html.includes("<em") && (stripped.endsWith(".") || stripped.endsWith("?"))) {
        // Only do this occasionally — check if it feels like a standalone thought
        const words = stripped.split(" ");
        if (words.length >= 4 && words.length <= 18 && i > 2 && i < paragraphs.length - 2) {
          return `<blockquote class="story-pullquote">${stripped}</blockquote>`;
        }
      }

      return `<p>${html}</p>`;
    })
    .join("");
}

export default function StoryDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(true);
  const [reactionCount, setReactionCount] = useState(0);
  const [hasReacted, setHasReacted] = useState(false);
  const [reacting, setReacting] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!slug) return;
    fetchStoryBySlug(slug).then((s) => {
      setStory(s);
      setReactionCount(s?.reaction_count ?? 0);
      setLoading(false);

      // Check localStorage for prior reaction
      const reacted = localStorage.getItem(`story-reacted-${s?.id}`);
      if (reacted) setHasReacted(true);
    });
  }, [slug]);

  async function handleReaction() {
    if (!story || hasReacted || reacting) return;
    setReacting(true);

    const oldCount = reactionCount;
    const newCount = oldCount + 1;
    setReactionCount(newCount);
    setHasReacted(true);
    localStorage.setItem(`story-reacted-${story.id}`, "1");

    try {
      // Optimistic locking: only update if reaction_count hasn't changed
      const { data, error } = await sb
        .from("stories")
        .update({ reaction_count: newCount })
        .eq("id", story.id)
        .eq("reaction_count", oldCount)
        .select("reaction_count")
        .single();

      if (error || !data) {
        // Conflict — re-read and retry once
        const { data: fresh } = await sb
          .from("stories")
          .select("reaction_count")
          .eq("id", story.id)
          .single();
        if (fresh) {
          const retryCount = (fresh.reaction_count || 0) + 1;
          await sb
            .from("stories")
            .update({ reaction_count: retryCount })
            .eq("id", story.id)
            .eq("reaction_count", fresh.reaction_count);
          setReactionCount(retryCount);
        }
      }
    } catch {
      // Optimistic — don't revert
    }
    setReacting(false);
  }

  function handleCopyLink() {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function shareWhatsApp() {
    const text = `${story?.headline} — a real story from the Indian diaspora on The Videshi\n${window.location.href}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank");
  }

  function shareX() {
    const text = `"${story?.headline}" — real stories from the Indian diaspora on @thevideshi`;
    window.open(
      `https://x.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(window.location.href)}`,
      "_blank"
    );
  }

  if (loading) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <main className="container py-16">
          <div className="max-w-2xl mx-auto">
            <div className="h-8 w-2/3 bg-muted rounded animate-pulse mb-4" />
            <div className="h-4 w-1/3 bg-muted rounded animate-pulse mb-8" />
            <div className="space-y-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-4 bg-muted rounded animate-pulse" style={{ width: `${70 + Math.random() * 30}%` }} />
              ))}
            </div>
          </div>
        </main>
        <SiteFooter />
      </>
    );
  }

  if (!story) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <main className="container py-20 text-center">
          <p className="text-5xl mb-4">🔍</p>
          <h1 className="font-serif text-2xl font-bold mb-2">Story not found</h1>
          <p className="text-muted-foreground mb-6">This story may have been removed or isn't published yet.</p>
          <Link to="/stories" className="text-primary underline">Browse all stories</Link>
        </main>
        <SiteFooter />
      </>
    );
  }

  const storyUrl = `https://thevideshi.com/stories/${story.slug}`;

  return (
    <>
      <Helmet>
        <title>{story.headline || "A Diaspora Story"} | Diaspora Voices — The Videshi</title>
        <meta name="description" content={story.subheadline || `A personal story from ${story.author_name} on The Videshi`} />
        <meta property="og:title" content={story.headline || "A Diaspora Story"} />
        <meta property="og:description" content={story.subheadline || `Read ${story.author_name}'s story`} />
        {story.author_photo_url && <meta property="og:image" content={story.author_photo_url} />}
        <meta property="og:url" content={storyUrl} />
        <meta name="twitter:card" content="summary_large_image" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-8 md:py-12">
        <article className="max-w-2xl mx-auto">
          {/* Breadcrumb */}
          <div className="mb-6">
            <Link to="/stories" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              ← Diaspora Voices
            </Link>
          </div>

          {/* Category badge */}
          <div className="flex items-center gap-2 mb-5 flex-wrap">
            <span className="inline-block px-3 py-1 bg-primary/10 text-primary text-xs font-semibold rounded-full tracking-wide uppercase">
              {getCategoryEmoji(story.category)} {getCategoryLabel(story.category)}
            </span>
            {story.author_linkedin && (
              <span className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-semibold rounded-full">
                🤝 Open to connect
              </span>
            )}
          </div>

          {/* Headline */}
          <h1 className="text-2xl md:text-[1.75rem] font-bold leading-snug mb-4 tracking-tight" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>
            {story.headline}
          </h1>

          {/* Subheadline */}
          {story.subheadline && (
            <p className="text-base md:text-[1.05rem] text-muted-foreground leading-relaxed mb-6" style={{ fontFamily: "'Newsreader', Georgia, serif", fontStyle: "italic" }}>
              {story.subheadline}
            </p>
          )}

          {/* Reading time */}
          <p className="text-xs text-muted-foreground uppercase tracking-widest mb-6">
            {Math.max(3, Math.ceil((story.body || "").split(/\s+/).length / 230))} min read
          </p>

          {/* Author bar */}
          <div className="flex items-center gap-3 mb-8 pb-6 border-b border-border">
            {story.author_photo_url ? (
              <img
                src={story.author_photo_url}
                alt={story.author_name}
                className="w-11 h-11 rounded-full object-cover"
              />
            ) : (
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-amber-100 to-orange-100 flex items-center justify-center text-base font-semibold text-amber-800">
                {(story.author_name || "?")[0].toUpperCase()}
              </div>
            )}
            <div>
              <p className="font-semibold text-sm">{story.author_name}</p>
              <p className="text-xs text-muted-foreground">
                {story.author_city && `${story.author_city} · `}
                {story.published_at && formatStoryDate(story.published_at)}
              </p>
            </div>
          </div>

          {/* Body */}
          <div
            className="prose prose-lg dark:prose-invert max-w-none mb-10 story-body"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(story.body || "") }}
          />

          {/* ============================================================ */}
          {/* LinkedIn connect CTA (if author shared their LinkedIn)       */}
          {/* ============================================================ */}
          {story.author_linkedin && (
            <div className="mb-10 p-6 bg-blue-50 dark:bg-blue-950/20 rounded-2xl border border-blue-200 dark:border-blue-800">
              <div className="flex items-start gap-4">
                {story.author_photo_url ? (
                  <img
                    src={story.author_photo_url}
                    alt={story.author_name}
                    className="w-12 h-12 rounded-full object-cover flex-shrink-0"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center text-lg font-bold text-blue-700 dark:text-blue-300 flex-shrink-0">
                    {(story.author_name || "?")[0].toUpperCase()}
                  </div>
                )}
                <div className="flex-1">
                  <h3 className="font-semibold text-base mb-1">
                    Connect with {story.author_name}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                    {story.author_name} shared their story to help the community. If you can help with a referral, advice, or just want to connect — reach out.
                  </p>
                  <a
                    href={story.author_linkedin.startsWith("http") ? story.author_linkedin : `https://linkedin.com/in/${story.author_linkedin}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                    View LinkedIn Profile →
                  </a>
                </div>
              </div>
            </div>
          )}

          {/* Reaction + Share bar */}
          <div className="flex items-center justify-between py-6 border-t border-b border-border mb-10">
            {/* Love reaction */}
            <button
              onClick={handleReaction}
              disabled={hasReacted}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-full border transition-all ${
                hasReacted
                  ? "border-red-200 bg-red-50 dark:bg-red-950/20 dark:border-red-800 text-red-600"
                  : "border-border hover:border-red-300 hover:bg-red-50 dark:hover:bg-red-950/20"
              }`}
            >
              <svg viewBox="0 0 24 24" fill={hasReacted ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" className={`w-5 h-5 ${hasReacted ? "text-red-500" : "text-muted-foreground"}`}>
                <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
              </svg>
              <span className="text-sm font-medium">
                {reactionCount > 0 ? reactionCount : ""} {hasReacted ? "Loved" : "Love this"}
              </span>
            </button>

            {/* Share buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={shareWhatsApp}
                className="p-2.5 rounded-full border border-border hover:bg-muted transition-colors"
                title="Share on WhatsApp"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-green-600">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
              </button>
              <button
                onClick={shareX}
                className="p-2.5 rounded-full border border-border hover:bg-muted transition-colors"
                title="Share on X"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </button>
              <button
                onClick={handleCopyLink}
                className="p-2.5 rounded-full border border-border hover:bg-muted transition-colors"
                title="Copy link"
              >
                {copied ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-green-500">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                    <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* CTA */}
          <div className="text-center py-8 px-6 bg-gradient-to-b from-amber-50/50 to-orange-50/50 rounded-2xl border border-amber-100">
            <h2 className="text-lg font-semibold mb-2 tracking-tight" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>Your story could be next</h2>
            <p className="text-muted-foreground mb-5 max-w-md mx-auto text-sm leading-relaxed">
              Whether it's a visa struggle, a career breakthrough, or finding home in a new country — the diaspora learns from each other.
            </p>
            <Link
              to="/stories/submit"
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors text-sm"
            >
              Share Your Story →
            </Link>
          </div>
        </article>
      </main>

      <SiteFooter />

      <style>{`
        /* Story body — editorial essay feel */
        .story-body {
          font-family: 'Newsreader', 'Source Serif 4', Georgia, serif;
          font-size: 1.1rem;
          line-height: 1.9;
          color: hsl(var(--foreground) / 0.88);
        }
        .story-body p {
          margin-bottom: 1.6rem;
        }
        .story-body p:last-child { margin-bottom: 0; }

        /* Drop cap on first paragraph */
        .story-body .story-first-p {
          margin-bottom: 1.6rem;
        }
        .story-body .story-dropcap {
          float: left;
          font-family: 'Playfair Display', Georgia, serif;
          font-size: 3.8rem;
          line-height: 0.75;
          font-weight: 700;
          padding-right: 0.12em;
          padding-top: 0.08em;
          color: hsl(var(--foreground));
        }

        /* Pull quotes — standout single-line thoughts */
        .story-body .story-pullquote {
          border-left: none;
          border-top: 1px solid hsl(var(--foreground) / 0.12);
          border-bottom: 1px solid hsl(var(--foreground) / 0.12);
          margin: 2.5rem auto;
          padding: 1.5rem 0;
          font-family: 'Playfair Display', Georgia, serif;
          font-style: italic;
          font-size: 1.35rem;
          line-height: 1.5;
          text-align: center;
          color: hsl(var(--foreground) / 0.75);
          max-width: 85%;
        }

        /* Bold text stands out */
        .story-body strong {
          font-weight: 600;
          color: hsl(var(--foreground));
        }

        /* Italic for internal thoughts */
        .story-body em {
          font-style: italic;
          color: hsl(var(--foreground) / 0.8);
        }

        @media (min-width: 768px) {
          .story-body { font-size: 1.15rem; }
          .story-body .story-dropcap { font-size: 4.5rem; }
        }
      `}</style>
    </>
  );
}
