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

  // Load X embed script
  useEffect(() => {
    if (tweets.length === 0) return;
    const existing = document.getElementById("twitter-wjs");
    if (existing) {
      // Re-scan for new embeds
      (window as any).twttr?.widgets?.load?.();
      return;
    }
    const script = document.createElement("script");
    script.id = "twitter-wjs";
    script.src = "https://platform.twitter.com/widgets.js";
    script.async = true;
    document.body.appendChild(script);
  }, [tweets]);

  if (tweets.length === 0) return null;

  const displayLabel = label || category.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());

  return (
    <div className="mt-4 mb-2">
      <div className="flex items-center gap-2 mb-3 px-1">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" className="text-stone-400 flex-shrink-0">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
        <span className="text-[11px] font-semibold tracking-wider text-stone-400 uppercase">
          Posts · {displayLabel}
        </span>
      </div>
      <div className="v2-tweet-scroll">
        {tweets.map((t) => (
          <div key={t.tweet_id} className="v2-tweet-card">
            <blockquote className="twitter-tweet" data-dnt="true" data-theme="light" data-width="320">
              <a href={t.tweet_url}>Loading…</a>
            </blockquote>
          </div>
        ))}
      </div>
    </div>
  );
}
