import { useState, useRef, useEffect } from "react";
import { Tweet } from "react-tweet";
import "react-tweet/theme.css";

interface SocialEmbedProps {
  platform: "instagram" | "twitter";
  url: string;
  caption?: string;
}

function extractInstaShortcode(url: string): string | null {
  const m = url.match(/instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
  return m ? m[1] : null;
}

function extractTweetId(url: string): string | null {
  const m = url.match(/(?:twitter\.com|x\.com)\/\w+\/status\/(\d+)/);
  return m ? m[1] : null;
}

/* ------------------------------------------------------------------ */

function InstagramEmbed({ url, caption }: { url: string; caption?: string }) {
  const shortcode = extractInstaShortcode(url);
  if (!shortcode) return null;

  return (
    <figure className="my-6 flex flex-col items-center">
      <iframe
        src={`https://www.instagram.com/p/${shortcode}/embed/`}
        className="w-full max-w-[540px] rounded border-0"
        style={{ minHeight: 500 }}
        loading="lazy"
        allowTransparency
        scrolling="no"
        title="Instagram embed"
      />
      {caption && (
        <figcaption className="mt-2 text-sm text-muted-foreground text-center">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}

function TwitterEmbed({ url, caption }: { url: string; caption?: string }) {
  const tweetId = extractTweetId(url);
  if (!tweetId) return null;

  const [expanded, setExpanded] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // After mount, add a "View on 𝕏" link at the bottom if not already present
  useEffect(() => {
    if (!wrapperRef.current) return;
    // Observe for when react-tweet finishes rendering
    const observer = new MutationObserver(() => {
      const article = wrapperRef.current?.querySelector("article");
      if (article && !wrapperRef.current?.querySelector(".tweet-view-on-x")) {
        observer.disconnect();
      }
    });
    observer.observe(wrapperRef.current, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  return (
    <figure className="my-6 flex flex-col items-center">
      <div
        ref={wrapperRef}
        className={`tweet-embed-wrapper w-full max-w-[550px] ${expanded ? "tweet-expanded" : "tweet-collapsed"}`}
        data-theme="light"
      >
        <Tweet id={tweetId} />
        <div className="tweet-toggle-bar">
          <button
            onClick={() => setExpanded(!expanded)}
            className="tweet-toggle-btn"
          >
            {expanded ? "Hide text ▲" : "Show text ▼"}
          </button>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="tweet-view-x-link"
          >
            View on 𝕏 →
          </a>
        </div>
      </div>
      {caption && (
        <figcaption className="mt-2 text-sm text-muted-foreground text-center">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}

/* ------------------------------------------------------------------ */

export default function SocialEmbed({ platform, url, caption }: SocialEmbedProps) {
  if (platform === "instagram") {
    return <InstagramEmbed url={url} caption={caption} />;
  }
  if (platform === "twitter") {
    return <TwitterEmbed url={url} caption={caption} />;
  }
  return null;
}

/* ------------------------------------------------------------------ */

const INSTA_RE = /^https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel|tv)\/[A-Za-z0-9_-]+\/?$/;
const TWEET_RE = /^https?:\/\/(?:(?:www\.)?(?:twitter|x)\.com)\/\w+\/status\/\d+\/?$/;

export function detectSocialUrl(line: string): { platform: "instagram" | "twitter"; url: string } | null {
  const trimmed = line.trim();
  if (INSTA_RE.test(trimmed)) return { platform: "instagram", url: trimmed };
  if (TWEET_RE.test(trimmed)) return { platform: "twitter", url: trimmed };
  return null;
}
