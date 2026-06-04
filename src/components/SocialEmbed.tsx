import { Tweet } from "react-tweet";
import "react-tweet/theme.css";

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
 * Extract tweet ID from a URL like
 * https://x.com/SpaceX/status/1234567890  or
 * https://twitter.com/SpaceX/status/1234567890
 */
function extractTweetId(url: string): string | null {
  const m = url.match(/(?:twitter\.com|x\.com)\/\w+\/status\/(\d+)/);
  return m ? m[1] : null;
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
  const tweetId = extractTweetId(url);
  if (!tweetId) return null;

  return (
    <figure className="my-8 flex flex-col items-center">
      <div className="w-full max-w-[550px]">
        <Tweet id={tweetId} />
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
