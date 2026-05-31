import { useState, useEffect, useRef, useCallback } from "react";
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

/* ------------------------------------------------------------------ */
/* Example story prompts — inspiration cards                          */
/* ------------------------------------------------------------------ */
const EXAMPLE_PROMPTS = [
  { emoji: "🗽", text: "How I survived my H-1B transfer nightmare" },
  { emoji: "💼", text: "How I landed my first job with zero connections" },
  { emoji: "🤝", text: "The referral that changed my career — paying it forward" },
  { emoji: "🎓", text: "How I got into a top college from a small town in India" },
  { emoji: "🏠", text: "Buying our first home — what nobody tells you" },
  { emoji: "👨‍👩‍👧", text: "Raising kids who speak Telugu at home and English everywhere else" },
  { emoji: "🍛", text: "My grandmother's sambar recipe kept me sane in grad school" },
  { emoji: "✈️", text: "Why I moved back after 12 years — and what surprised me" },
  { emoji: "💪", text: "Laid off during H-1B — here's how I bounced back in 30 days" },
  { emoji: "🌱", text: "Starting a business with $500 and a prayer" },
  { emoji: "🤷", text: "The culture shock nobody warned me about" },
  { emoji: "🏥", text: "Navigating the US healthcare system as a new immigrant" },
];

/* ------------------------------------------------------------------ */
/* Story Card                                                         */
/* ------------------------------------------------------------------ */
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
        {/* Open to connect badge */}
        {story.author_linkedin && (
          <span className="absolute top-3 right-3 px-2 py-1 bg-blue-600/90 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full flex items-center gap-1">
            🤝 Open to connect
          </span>
        )}
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

/* ------------------------------------------------------------------ */
/* Main Page                                                          */
/* ------------------------------------------------------------------ */
export default function StoriesPage() {
  const [stories, setStories] = useState<Story[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("all");
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounce search input
  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedSearch(value);
      setPage(0);
    }, 300);
  }, []);

  useEffect(() => {
    setPage(0);
  }, [category]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchStories({
      category: category === "all" ? undefined : category,
      search: debouncedSearch || undefined,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    }).then(({ stories: s, total: t }) => {
      if (cancelled) return;
      setStories(s);
      setTotal(t);
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, [category, page, debouncedSearch]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <>
      <Helmet>
        <title>Diaspora Voices — Real Stories from the Indian Diaspora | The Videshi</title>
        <meta
          name="description"
          content="Community stories from the Indian diaspora. Share your journey, help someone a few steps behind you, and learn from those who've been there. Immigration, careers, family, food, and everything in between."
        />
              <link rel="canonical" href="https://www.thevideshi.com/stories" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-8 md:py-12">
        {/* ============================================================ */}
        {/* Hero — Community framing                                     */}
        {/* ============================================================ */}
        <div className="text-center max-w-3xl mx-auto mb-6">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
            Diaspora Voices
          </h1>
          <p className="text-muted-foreground text-lg leading-relaxed mb-3">
            Every diaspora journey has a story worth sharing. A visa nightmare someone else is going through right now. A career hack that could change someone's trajectory. A recipe that tastes like home.
          </p>
          <p className="text-foreground font-medium text-base leading-relaxed">
            Share yours — help someone who's a few steps behind you on the same path.
          </p>
          <p className="text-sm text-muted-foreground mt-3 italic">
            Include your LinkedIn — the community might just reach out with a referral, an introduction, or advice.
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

        {/* ============================================================ */}
        {/* Example story prompts — inspiration scroll                   */}
        {/* ============================================================ */}
        <div className="mb-10">
          <p className="text-center text-sm text-muted-foreground mb-4 font-medium">
            Not sure what to write about? Here are some ideas from people like you:
          </p>
          <div className="relative">
            <div className="flex gap-3 overflow-x-auto pb-3 scrollbar-hide snap-x snap-mandatory -mx-4 px-4 md:mx-0 md:px-0 md:flex-wrap md:justify-center">
              {EXAMPLE_PROMPTS.map((p, i) => (
                <Link
                  key={i}
                  to="/stories/submit"
                  className="snap-start flex-shrink-0 flex items-start gap-2.5 px-4 py-3 bg-muted/60 hover:bg-muted rounded-xl border border-border hover:border-primary/30 transition-all duration-200 max-w-[260px] md:max-w-[280px] group"
                >
                  <span className="text-lg flex-shrink-0 mt-0.5">{p.emoji}</span>
                  <span className="text-sm text-foreground/80 group-hover:text-foreground leading-snug" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>
                    "{p.text}"
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* Search bar                                                   */}
        {/* ============================================================ */}
        <div className="max-w-xl mx-auto mb-6">
          <div className="relative">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
            <input
              type="text"
              placeholder="Search stories — try 'H-1B', 'referral', 'Bay Area', 'food'..."
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="w-full pl-10 pr-10 py-3 rounded-xl border border-border bg-background text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
            />
            {search && (
              <button
                onClick={() => { setSearch(""); setDebouncedSearch(""); setPage(0); }}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Clear search"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
          {debouncedSearch && !loading && (
            <p className="text-xs text-muted-foreground mt-2 text-center">
              {total === 0
                ? `No stories found for "${debouncedSearch}"`
                : `${total} ${total === 1 ? "story" : "stories"} found for "${debouncedSearch}"`}
            </p>
          )}
        </div>

        {/* ============================================================ */}
        {/* Category filter pills                                        */}
        {/* ============================================================ */}
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

        {/* ============================================================ */}
        {/* Stories grid                                                  */}
        {/* ============================================================ */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-muted rounded-xl animate-pulse aspect-[3/4]" />
            ))}
          </div>
        ) : stories.length === 0 && !debouncedSearch ? (
          <div className="text-center py-20">
            <p className="text-5xl mb-4">📝</p>
            <h2 className="text-lg font-semibold tracking-tight mb-2">No stories yet</h2>
            <p className="text-muted-foreground mb-2">
              Be the first to share your story with the diaspora community.
            </p>
            <p className="text-sm text-muted-foreground mb-6">
              Your experience could be the exact thing someone else needs to hear right now.
            </p>
            <Link
              to="/stories/submit"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
            >
              Share Your Story
            </Link>
          </div>
        ) : stories.length === 0 && debouncedSearch ? (
          <div className="text-center py-16">
            <p className="text-4xl mb-3">🔍</p>
            <h2 className="text-base font-semibold tracking-tight mb-2">No matches for "{debouncedSearch}"</h2>
            <p className="text-muted-foreground text-sm mb-4">
              Try different keywords, or be the first to share a story about this topic.
            </p>
            <Link
              to="/stories/submit"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
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

        {/* ============================================================ */}
        {/* Bottom CTA — Community framing                               */}
        {/* ============================================================ */}
        <div className="mt-16 text-center py-12 px-6 bg-muted/30 rounded-2xl border border-border">
          <p className="text-3xl mb-3">🤝</p>
          <h2 className="text-lg md:text-xl font-semibold tracking-tight mb-4">Your experience is someone else's roadmap</h2>
          <p className="text-muted-foreground mb-3 max-w-lg mx-auto leading-relaxed">
            Every story you share helps someone who's a few steps behind you. A first-gen student figuring out college apps. A new H-1B holder who doesn't know what to expect. A parent wondering if anyone else is raising kids between two cultures.
          </p>
          <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto italic">
            Include your LinkedIn — you never know who might reach out with the exact opportunity or advice you need.
          </p>
          <Link
            to="/stories/submit"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4 12.5-12.5z" />
            </svg>
            Share Your Story
          </Link>
        </div>
      </main>

      <SiteFooter />

      <style>{`
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </>
  );
}
