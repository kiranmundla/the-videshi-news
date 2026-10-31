import { useEffect, useState } from "react";

/* ── Static tweet media ─────────────────────────────────────────────
   /data/tweet-media.json is built by pipeline/prebuild-feeds.py (see
   pipeline/tweet_media.py) from X's syndication endpoint: for every
   tweet referenced by a recently rebuilt article it carries the author,
   text, EVERY photo at the largest served size, and the video poster +
   aspect. Article pages render from this static data when present —
   no runtime API call — and fall back to react-tweet's runtime fetch
   for tweets the prebuild hasn't covered yet (older articles). */

export interface TweetPhoto {
  url: string;
  width: number;
  height: number;
}

export interface TweetVideo {
  poster: string;
  aspect: [number, number];
  duration_ms: number;
  type: string;
}

export interface StaticTweet {
  id: string;
  url: string;
  text: string;
  created_at: string;
  favorite_count: number;
  conversation_count: number;
  user: {
    name: string;
    screen_name: string;
    avatar: string;
    verified: boolean;
    verified_type?: string | null;
  };
  photos: TweetPhoto[];
  video: TweetVideo | null;
  media_count: number;
}

type TweetMediaMap = Record<string, StaticTweet>;

let cached: TweetMediaMap | null = null;
let inflight: Promise<TweetMediaMap> | null = null;

export function loadTweetMedia(): Promise<TweetMediaMap> {
  if (cached) return Promise.resolve(cached);
  if (!inflight) {
    inflight = fetch("/data/tweet-media.json")
      .then((r) => (r.ok ? r.json() : {}))
      .then((data) => {
        cached = (data ?? {}) as TweetMediaMap;
        return cached;
      })
      .catch(() => {
        cached = {};
        return cached;
      });
  }
  return inflight;
}

/**
 * Returns the static entry for a tweet:
 *  - undefined → still loading (caller should show a placeholder)
 *  - null      → not in the static data (caller falls back to runtime)
 *  - entry     → render from static data, no runtime fetch
 */
export function useStaticTweet(
  tweetId: string | null,
): StaticTweet | null | undefined {
  const [entry, setEntry] = useState<StaticTweet | null | undefined>(
    () =>
      tweetId && cached ? (cached[tweetId] ?? null) : undefined,
  );

  useEffect(() => {
    if (!tweetId) {
      setEntry(null);
      return;
    }
    if (cached) {
      setEntry(cached[tweetId] ?? null);
      return;
    }
    let cancelled = false;
    loadTweetMedia().then((map) => {
      if (!cancelled) setEntry(map[tweetId] ?? null);
    });
    return () => {
      cancelled = true;
    };
  }, [tweetId]);

  return entry;
}
