import { useEffect, useState } from "react";

interface TweetEntry {
  tweet_url: string;
  handle: string;
  tweet_id: string;
  category: string;
  article_slug: string;
  article_headline: string;
}

interface SocialFeed {
  categories: Record<string, TweetEntry[]>;
}

interface TweetScrollProps {
  category: string;
  label?: string;
}

export default function TweetScroll({ category, label }: TweetScrollProps) {
  const [tweets, setTweets] = useState<TweetEntry[]>([]);

  useEffect(() => {
    fetch("/data/social-feed.json")
      .then((r) => r.json())
      .then((data: SocialFeed) => {
        const catTweets = data.categories?.[category] || [];
        setTweets(catTweets);
      })
      .catch(() => {});
  }, [category]);

  if (tweets.length === 0) return null;

  const displayLabel =
    label ||
    category.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <section className="v2-social-strip">
      <div className="container">
        {/* Header */}
        <div className="flex items-center gap-2.5 mb-4">
          <div className="v2-social-x-badge">
            <svg viewBox="0 0 24 24" width="11" height="11" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
          </div>
          <span
            className="text-[11px] font-bold tracking-[1.5px] uppercase"
            style={{ color: "#64748B" }}
          >
            What people are saying · {displayLabel}
          </span>
        </div>

        {/* Scroll strip */}
        <div className="v2-social-scroll">
          {tweets.map((t) => (
            <a
              key={t.tweet_id}
              href={t.tweet_url}
              target="_blank"
              rel="noopener noreferrer"
              className="v2-social-card group"
            >
              {/* Handle row */}
              <div className="flex items-center gap-2.5 mb-3">
                <div className="v2-social-avatar">
                  {t.handle.charAt(0).toUpperCase()}
                </div>
                <div className="min-w-0 flex-1">
                  <p
                    className="text-[13px] font-semibold truncate"
                    style={{ color: "#0B1D3A" }}
                  >
                    @{t.handle}
                  </p>
                </div>
                <svg
                  viewBox="0 0 24 24"
                  width="14"
                  height="14"
                  fill="#94A3B8"
                  className="flex-shrink-0"
                >
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </div>

              {/* Article headline as quote */}
              <blockquote
                className="font-serif text-[14px] italic leading-relaxed mb-3 pl-3"
                style={{
                  color: "#334155",
                  borderLeft: "3px solid #D4A843",
                }}
              >
                "{t.article_headline}"
              </blockquote>

              {/* Footer */}
              <div className="flex items-center gap-1.5 mt-auto pt-1">
                <span
                  className="text-[10px] font-bold tracking-[1px] uppercase group-hover:opacity-70 transition-opacity"
                  style={{ color: "#94A3B8" }}
                >
                  View on 𝕏 →
                </span>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
