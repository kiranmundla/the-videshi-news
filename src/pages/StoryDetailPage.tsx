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

/* Simple markdown → HTML (paragraphs, bold, italic) */
function renderMarkdown(md: string): string {
  return md
    .split(/\n\n+/)
    .map((p) => {
      let html = p
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/\n/g, "<br />");
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

    const newCount = reactionCount + 1;
    setReactionCount(newCount);
    setHasReacted(true);
    localStorage.setItem(`story-reacted-${story.id}`, "1");

    try {
      await sb
        .from("stories")
        .update({ reaction_count: newCount })
        .eq("id", story.id);
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
          <span className="inline-block px-3 py-1 bg-primary/10 text-primary text-xs font-semibold rounded-full mb-4">
            {getCategoryEmoji(story.category)} {getCategoryLabel(story.category)}
          </span>

          {/* Headline */}
          <h1 className="font-serif text-3xl md:text-4xl font-bold leading-tight mb-3">
            {story.headline}
          </h1>

          {/* Subheadline */}
          {story.subheadline && (
            <p className="text-lg text-muted-foreground italic mb-6">
              {story.subheadline}
            </p>
          )}

          {/* Author bar */}
          <div className="flex items-center gap-4 mb-8 pb-6 border-b border-border">
            {story.author_photo_url ? (
              <img
                src={story.author_photo_url}
                alt={story.author_name}
                className="w-14 h-14 rounded-full object-cover"
              />
            ) : (
              <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center text-xl font-bold text-primary">
                {(story.author_name || "?")[0].toUpperCase()}
              </div>
            )}
            <div>
              <p className="font-medium text-base">{story.author_name}</p>
              <p className="text-sm text-muted-foreground">
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
          <div className="text-center py-10 bg-muted/30 rounded-2xl border border-border">
            <p className="text-3xl mb-3">✍️</p>
            <h2 className="font-serif text-xl font-bold mb-2">Have a story to tell?</h2>
            <p className="text-muted-foreground mb-5 max-w-sm mx-auto text-sm">
              We'll help you write it. Your voice, polished into a story the whole diaspora can connect with.
            </p>
            <Link
              to="/stories/submit"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
            >
              Share Your Story
            </Link>
          </div>
        </article>
      </main>

      <SiteFooter />

      <style>{`
        .story-body p { margin-bottom: 1.25rem; line-height: 1.8; }
        .story-body p:last-child { margin-bottom: 0; }
      `}</style>
    </>
  );
}
