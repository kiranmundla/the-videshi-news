import { useState } from "react";
import { useTweet } from "react-tweet";

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

/* ── Helpers ── */
function hiResAvatar(url: string) {
  return url.replace(/_normal\./, "_400x400.");
}

function formatCount(n: number): string {
  if (!n) return "";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function timeAgo(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const hrs = Math.floor((now.getTime() - d.getTime()) / 3_600_000);
    if (hrs < 1) return "just now";
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    if (days < 7) return `${days}d ago`;
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return "";
  }
}

/* ── Verified badge ── */
function VerifiedBadge({ type }: { type?: string }) {
  if (type === "Government") {
    return (
      <svg width="16" height="16" viewBox="0 0 22 22" fill="none" style={{ marginLeft: 3, flexShrink: 0 }}>
        <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.855-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.69-.13.636-.08 1.297.144 1.907-.577.27-1.067.696-1.418 1.236-.35.54-.544 1.17-.562 1.817.018.646.213 1.275.562 1.815.351.54.841.967 1.418 1.236-.224.61-.274 1.27-.144 1.907.13.635.433 1.22.878 1.69.47.443 1.055.747 1.69.878.635.13 1.294.083 1.902-.143.271.586.702 1.084 1.24 1.438.54.354 1.167.551 1.813.568.646-.017 1.276-.214 1.817-.568s.972-.852 1.245-1.438c.608.226 1.267.276 1.9.143.636-.13 1.22-.433 1.69-.878.445-.47.749-1.055.878-1.69.131-.637.08-1.297-.143-1.907.586-.27 1.078-.696 1.432-1.236.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" fill="#1DA1F2" />
      </svg>
    );
  }
  return (
    <svg width="16" height="16" viewBox="0 0 22 22" fill="none" style={{ marginLeft: 3, flexShrink: 0 }}>
      <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.855-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.69-.13.636-.08 1.297.144 1.907-.577.27-1.067.696-1.418 1.236-.35.54-.544 1.17-.562 1.817.018.646.213 1.275.562 1.815.351.54.841.967 1.418 1.236-.224.61-.274 1.27-.144 1.907.13.635.433 1.22.878 1.69.47.443 1.055.747 1.69.878.635.13 1.294.083 1.902-.143.271.586.702 1.084 1.24 1.438.54.354 1.167.551 1.813.568.646-.017 1.276-.214 1.817-.568s.972-.852 1.245-1.438c.608.226 1.267.276 1.9.143.636-.13 1.22-.433 1.69-.878.445-.47.749-1.055.878-1.69.131-.637.08-1.297-.143-1.907.586-.27 1.078-.696 1.432-1.236.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" fill="#1DA1F2" />
    </svg>
  );
}

/* ── X icon ── */
function XIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

/* ── Photo grid ── */
function PhotoGrid({ photos }: { photos: { url: string; width: number; height: number }[] }) {
  const count = photos.length;
  if (!count) return null;

  const gridClass =
    count === 1
      ? "tweet-card-grid-1"
      : count === 2
      ? "tweet-card-grid-2"
      : count === 3
      ? "tweet-card-grid-3"
      : "tweet-card-grid-4";

  return (
    <div className={`tweet-card-photo-grid ${gridClass}`}>
      {photos.slice(0, 4).map((p, i) => (
        <img key={i} src={p.url} alt="" loading="lazy" />
      ))}
    </div>
  );
}

/* ── Tweet skeleton ── */
function TweetSkeleton() {
  return (
    <div className="tweet-card" style={{ minHeight: 120, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ color: "#9ca3af", fontSize: 13 }}>Loading post…</div>
    </div>
  );
}

/* ── Custom tweet card ── */
function TweetCard({ tweetId, url }: { tweetId: string; url: string }) {
  const { data: tweet, isLoading, error } = useTweet(tweetId);
  const [expanded, setExpanded] = useState(false);

  if (isLoading) return <TweetSkeleton />;
  if (error || !tweet) {
    return (
      <div className="tweet-card" style={{ padding: 16, textAlign: "center" }}>
        <a href={url} target="_blank" rel="noopener noreferrer" style={{ color: "#1DA1F2", fontSize: 13 }}>
          View post on 𝕏 →
        </a>
      </div>
    );
  }

  const user = tweet.user;
  const avatarUrl = hiResAvatar(user.profile_image_url_https);
  const tweetUrl = `https://x.com/${user.screen_name}/status/${tweet.id_str}`;
  const hasPhotos = (tweet.photos?.length ?? 0) > 0;
  const bodyText = tweet.text
    ?.replace(/https:\/\/t\.co\/\S+/g, "") // strip t.co links
    .trim();

  return (
    <div className="tweet-card">
      {/* Header */}
      <div className="tweet-card-header">
        <a href={`https://x.com/${user.screen_name}`} target="_blank" rel="noopener noreferrer">
          <img src={avatarUrl} alt={user.name} className="tweet-card-avatar" />
        </a>
        <div className="tweet-card-author">
          <div className="tweet-card-name">
            <a href={tweetUrl} target="_blank" rel="noopener noreferrer">
              <span>{user.name}</span>
            </a>
            {(user.is_blue_verified || user.verified_type) && (
              <VerifiedBadge type={user.verified_type} />
            )}
          </div>
          <div className="tweet-card-handle">
            <a href={`https://x.com/${user.screen_name}`} target="_blank" rel="noopener noreferrer">
              @{user.screen_name}
            </a>
            {tweet.created_at && (
              <span className="tweet-card-time"> · {timeAgo(tweet.created_at)}</span>
            )}
          </div>
        </div>
        <a href={tweetUrl} target="_blank" rel="noopener noreferrer" className="tweet-card-x-icon">
          <XIcon />
        </a>
      </div>

      {/* Body text (collapsible) */}
      {bodyText && expanded && (
        <p className="tweet-card-body">{bodyText}</p>
      )}

      {/* Photos */}
      {hasPhotos && <PhotoGrid photos={tweet.photos!} />}

      {/* Footer */}
      <div className="tweet-card-footer">
        <div className="tweet-card-stats">
          {tweet.favorite_count > 0 && (
            <span>❤️ {formatCount(tweet.favorite_count)}</span>
          )}
          {tweet.conversation_count > 0 && (
            <span>💬 {formatCount(tweet.conversation_count)}</span>
          )}
        </div>
        <div className="tweet-card-actions">
          {bodyText && (
            <button onClick={() => setExpanded(!expanded)} className="tweet-card-toggle">
              {expanded ? "Hide text ▲" : "Show text ▼"}
            </button>
          )}
          <a href={tweetUrl} target="_blank" rel="noopener noreferrer" className="tweet-card-view-x">
            View on 𝕏
          </a>
        </div>
      </div>
    </div>
  );
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

  return (
    <figure className="my-6 flex flex-col items-center">
      <div className="w-full max-w-[550px]">
        <TweetCard tweetId={tweetId} url={url} />
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
  if (platform === "instagram") return <InstagramEmbed url={url} caption={caption} />;
  if (platform === "twitter") return <TwitterEmbed url={url} caption={caption} />;
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
