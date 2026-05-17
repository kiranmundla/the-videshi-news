import { useEffect, useRef, useState } from "react";

interface SocialEmbedProps {
  platform: "instagram" | "twitter";
  url: string;
  caption?: string;
}

/**
 * Extract Instagram shortcode from a URL like
 * https://www.instagram.com/p/ABC123/  or  /reel/ABC123/
 */
function extractInstaShortcode(url: string): string | null {
  const m = url.match(/instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
  return m ? m[1] : null;
}

/**
 * Normalise a tweet URL so it always uses x.com and strips query params.
 */
function normaliseTweetUrl(url: string): string {
  return url
    .replace(/^https?:\/\/(mobile\.)?twitter\.com/, "https://x.com")
    .split("?")[0];
}

/* ------------------------------------------------------------------ */

declare global {
  interface Window {
    twttr?: { widgets: { load: (el?: HTMLElement) => void } };
  }
}

let twitterScriptLoading = false;

function ensureTwitterWidgets(cb: () => void) {
  if (window.twttr?.widgets) {
    cb();
    return;
  }
  if (!twitterScriptLoading) {
    twitterScriptLoading = true;
    const s = document.createElement("script");
    s.src = "https://platform.twitter.com/widgets.js";
    s.async = true;
    s.charset = "utf-8";
    s.onload = () => cb();
    document.head.appendChild(s);
  } else {
    // Script is loading — poll until ready
    const iv = setInterval(() => {
      if (window.twttr?.widgets) {
        clearInterval(iv);
        cb();
      }
    }, 200);
  }
}

/* ------------------------------------------------------------------ */

function InstagramEmbed({ url, caption }: { url: string; caption?: string }) {
  const shortcode = extractInstaShortcode(url);
  if (!shortcode) return null;

  return (
    <figure className="my-8 flex flex-col items-center">
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
  const ref = useRef<HTMLDivElement>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    ensureTwitterWidgets(() => {
      if (ref.current) {
        window.twttr?.widgets.load(ref.current);
        setLoaded(true);
      }
    });
  }, [url]);

  const tweetUrl = normaliseTweetUrl(url);

  return (
    <figure className="my-8 flex flex-col items-center">
      <div ref={ref} className="w-full max-w-[550px]">
        <blockquote className="twitter-tweet" data-dnt="true">
          <a href={tweetUrl}>{tweetUrl}</a>
        </blockquote>
        {!loaded && (
          <div className="animate-pulse h-48 bg-secondary/40 rounded flex items-center justify-center text-muted-foreground text-sm">
            Loading post…
          </div>
        )}
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

/** Regex patterns to detect bare social URLs on their own line. */
const INSTA_RE = /^https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel|tv)\/[A-Za-z0-9_-]+\/?$/;
const TWEET_RE = /^https?:\/\/(?:(?:www\.)?(?:twitter|x)\.com)\/\w+\/status\/\d+\/?$/;

/**
 * Given a line of text, returns embed props if it's a bare social URL,
 * or null if it's just normal text.
 */
export function detectSocialUrl(line: string): { platform: "instagram" | "twitter"; url: string } | null {
  const trimmed = line.trim();
  if (INSTA_RE.test(trimmed)) return { platform: "instagram", url: trimmed };
  if (TWEET_RE.test(trimmed)) return { platform: "twitter", url: trimmed };
  return null;
}
