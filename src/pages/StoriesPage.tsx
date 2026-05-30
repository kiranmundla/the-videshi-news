import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  fetchStories,
  formatStoryDate,
  getCategoryLabel,
  getCategoryEmoji,
  STORY_CATEGORIES,
  type Story,
} from "@/lib/stories";

const PAGE_SIZE = 12;

const FILTER_CATS = [
  { value: "all", label: "All Stories" },
  ...STORY_CATEGORIES.map((c) => ({ value: c.value, label: c.label })),
];

function StoryCard({ story }: { story: Story }) {
  return (
    <Link
      to={`/stories/${story.slug}`}
      className="group block bg-card rounded-xl overflow-hidden border border-border hover:border-primary/30 hover:shadow-lg transition-all duration-200"
    >
      {/* Author photo */}
      <div className="relative aspect-[4/3] bg-muted overflow-hidden">
        {story.author_photo_url ? (
          <img
            src={story.author_photo_url}
            alt={story.author_name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-900/20 dark:to-orange-900/20">
            <span className="text-5xl">{getCategoryEmoji(story.category)}</span>
          </div>
        )}
        {/* Category badge */}
        <span className="absolute top-3 left-3 px-2.5 py-1 bg-background/90 backdrop-blur-sm text-xs font-medium rounded-full border border-border">
          {getCategoryEmoji(story.category)} {getCategoryLabel(story.category)}
        </span>
      </div>

      {/* Content */}
      <div className="p-5">
        <h3 className="font-serif font-bold text-lg leading-snug group-hover:text-primary transition-colors line-clamp-2 mb-2">
          {story.headline || "Untitled Story"}
        </h3>
        {story.subheadline && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {story.subheadline}
          </p>
        )}
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          {/* Small circular author photo */}
          {story.author_photo_url ? (
            <img
              src={story.author_photo_url}
              alt=""
              className="w-6 h-6 rounded-full object-cover"
            />
          ) : (
            <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
              {(story.author_name || "?")[0].toUpperCase()}
            </div>
          )}
          <span className="font-medium text-foreground">{story.author_name}</span>
          {story.author_city && (
            <>
              <span className="text-muted-foreground/40">·</span>
              <span>{story.author_city}</span>
            </>
          )}
        </div>
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
          <span className="text-xs text-muted-foreground">
            {story.published_at ? formatStoryDate(story.published_at) : ""}
          </span>
          {story.reaction_count > 0 && (
            <span className="text-xs text-muted-foreground flex items-center gap-1">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5 text-red-500">
                <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
              </svg>
              {story.reaction_count}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

export default function StoriesPage() {
  const [stories, setStories] = useState<Story[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("all");
  const [page, setPage] = useState(0);

  useEffect(() => {
    setPage(0);
  }, [category]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchStories({
      category: category === "all" ? undefined : category,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    }).then(({ stories: s, total: t }) => {
      if (cancelled) return;
      setStories(s);
      setTotal(t);
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, [category, page]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <>
      <Helmet>
        <title>Diaspora Voices — Real Stories from the Indian Diaspora | The Videshi</title>
        <meta
          name="description"
          content="Real stories from the Indian diaspora, in their own words. Immigration journeys, career wins, family moments, and the shared experience of building a life abroad."
        />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-8 md:py-12">
        {/* Hero */}
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h1 className="font-serif text-3xl md:text-4xl font-bold mb-3">
            Diaspora Voices
          </h1>
          <p className="text-muted-foreground text-lg leading-relaxed">
            Real stories from the Indian diaspora, in their own words. Immigration journeys, career pivots, family moments, and everything in between.
          </p>
          <Link
            to="/stories/submit"
            className="inline-flex items-center gap-2 mt-6 px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4 12.5-12.5z" />
            </svg>
            Share Your Story
          </Link>
        </div>

        {/* Category filter */}
        <div className="flex flex-wrap gap-2 justify-center mb-8">
          {FILTER_CATS.map((c) => (
            <button
              key={c.value}
              onClick={() => setCategory(c.value)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                category === c.value
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted hover:bg-muted/80 text-foreground"
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>

        {/* Stories grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-muted rounded-xl animate-pulse aspect-[3/4]" />
            ))}
          </div>
        ) : stories.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-5xl mb-4">📝</p>
            <h2 className="font-serif text-xl font-bold mb-2">No stories yet</h2>
            <p className="text-muted-foreground mb-6">
              Be the first to share your story with the diaspora community.
            </p>
            <Link
              to="/stories/submit"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
            >
              Share Your Story
            </Link>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {stories.map((story) => (
                <StoryCard key={story.id} story={story} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-4 mt-10">
                <button
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="px-4 py-2 text-sm font-medium rounded-lg border border-border disabled:opacity-40 hover:bg-muted transition-colors"
                >
                  ← Previous
                </button>
                <span className="text-sm text-muted-foreground">
                  Page {page + 1} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                  className="px-4 py-2 text-sm font-medium rounded-lg border border-border disabled:opacity-40 hover:bg-muted transition-colors"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}

        {/* Bottom CTA */}
        {stories.length > 0 && (
          <div className="mt-16 text-center py-12 bg-muted/30 rounded-2xl border border-border">
            <p className="text-3xl mb-3">✍️</p>
            <h2 className="font-serif text-xl font-bold mb-2">Your story matters</h2>
            <p className="text-muted-foreground mb-5 max-w-md mx-auto">
              Whether it's about immigration, career, family, or finding home — we want to hear it. We'll help you tell it beautifully.
            </p>
            <Link
              to="/stories/submit"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
            >
              Share Your Story
            </Link>
          </div>
        )}
      </main>

      <SiteFooter />
    </>
  );
}
