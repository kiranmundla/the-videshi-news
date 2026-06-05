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
  return url.replace(/_normal\./, "_200x200.");
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

/* ── Verified badge (matches X's official style) ── */
function VerifiedBadge({ type }: { type?: string }) {
  const fill = type === "Government" ? "#829aab" : "#1DA1F2";
  return (
    <svg width="18" height="18" viewBox="0 0 22 22" fill="none" style={{ marginLeft: 4, flexShrink: 0 }}>
      <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.855-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.69-.13.636-.08 1.297.144 1.907-.577.27-1.067.696-1.418 1.236-.35.54-.544 1.17-.562 1.817.018.646.213 1.275.562 1.815.351.54.841.967 1.418 1.236-.224.61-.274 1.27-.144 1.907.13.635.433 1.22.878 1.69.47.443 1.055.747 1.69.878.635.13 1.294.083 1.902-.143.271.586.702 1.084 1.24 1.438.54.354 1.167.551 1.813.568.646-.017 1.276-.214 1.817-.568s.972-.852 1.245-1.438c.608.226 1.267.276 1.9.143.636-.13 1.22-.433 1.69-.878.445-.47.749-1.055.878-1.69.131-.637.08-1.297-.143-1.907.586-.27 1.078-.696 1.432-1.236.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" fill={fill} />
    </svg>
  );
}

/* ── X icon ── */
function XIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

/* ── Photo grid ── */
function PhotoGrid({ photos, tweetUrl }: { photos: { url: string; width: number; height: number }[]; tweetUrl: string }) {
  const count = photos.length;
  if (!count) return null;

  const gridStyle: React.CSSProperties =
    count === 1
      ? { gridTemplateColumns: "1fr" }
      : { gridTemplateColumns: "1fr 1fr", gridTemplateRows: count > 2 ? "1fr 1fr" : "1fr" };

  return (
    <a href={tweetUrl} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>
      <div style={{
        display: "grid", gap: 2, margin: "0 16px 12px", borderRadius: 12, overflow: "hidden",
        ...gridStyle,
      }}>
        {photos.slice(0, 4).map((p, i) => (
          <img
            key={i}
            src={p.url}
            alt=""
            loading="lazy"
            style={{
              width: "100%",
              height: count === 1 ? "auto" : "100%",
              maxHeight: count === 1 ? 320 : "none",
              objectFit: "cover",
              display: "block",
              aspectRatio: count === 1 ? undefined : "16/9",
            }}
          />
        ))}
      </div>
    </a>
  );
}

/* ── Custom tweet card — matches X's embed layout with enhancements ── */
function TweetCard({ tweetId, url }: { tweetId: string; url: string }) {
  const { data: tweet, isLoading, error } = useTweet(tweetId);
  const [expanded, setExpanded] = useState(false);

  if (isLoading) {
    return (
      <div style={{
        background: "#fff", border: "1px solid #e1e8ed", borderTop: "3px solid #1DA1F2",
        borderRadius: 14, padding: 32, textAlign: "center", color: "#9ca3af", fontSize: 13,
      }}>
        Loading post…
      </div>
    );
  }

  if (error || !tweet) {
    return (
      <div style={{
        background: "#fff", border: "1px solid #e1e8ed", borderRadius: 14, padding: 20, textAlign: "center",
      }}>
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
  const bodyText = tweet.text?.replace(/https:\/\/t\.co\/\S+/g, "").trim();

  return (
    <div style={{
      background: "#fff",
      border: "1px solid #e1e8ed",
      borderTop: "3px solid #1DA1F2",
      borderRadius: 14,
      overflow: "hidden",
      boxShadow: "0 1px 8px rgba(0,0,0,0.06)",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    }}>
      {/* Header — matches X embed: avatar | name+handle | X icon */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "14px 16px 10px" }}>
        <a href={`https://x.com/${user.screen_name}`} target="_blank" rel="noopener noreferrer"
           style={{ flexShrink: 0 }}>
          <img
            src={avatarUrl}
            alt={user.name}
            width={48}
            height={48}
            style={{
              width: 48, height: 48, minWidth: 48, minHeight: 48, maxWidth: 48, maxHeight: 48,
              borderRadius: "50%", objectFit: "cover",
              border: "1px solid rgba(0,0,0,0.08)",
            }}
          />
        </a>
        <div style={{ flex: 1, minWidth: 0, overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <a href={tweetUrl} target="_blank" rel="noopener noreferrer"
               style={{ color: "#0f1419", textDecoration: "none", fontWeight: 700, fontSize: 15, lineHeight: 1.3 }}>
              {user.name}
            </a>
            {(user.is_blue_verified || user.verified_type) && (
              <VerifiedBadge type={user.verified_type} />
            )}
          </div>
          <div style={{ color: "#536471", fontSize: 14, lineHeight: 1.3, display: "flex", alignItems: "center", gap: 2 }}>
            <a href={`https://x.com/${user.screen_name}`} target="_blank" rel="noopener noreferrer"
               style={{ color: "inherit", textDecoration: "none" }}>
              @{user.screen_name}
            </a>
            <span style={{ color: "#536471" }}> · </span>
            <a href={tweetUrl} target="_blank" rel="noopener noreferrer"
               style={{ color: "#1DA1F2", textDecoration: "none", fontWeight: 500, fontSize: 14 }}>
              Follow
            </a>
          </div>
        </div>
        <a href={tweetUrl} target="_blank" rel="noopener noreferrer"
           style={{ color: "#0f1419", flexShrink: 0, marginLeft: "auto" }}>
          <XIcon />
        </a>
      </div>

      {/* Body text (collapsible) */}
      {bodyText && expanded && (
        <p style={{
          padding: "0 16px 10px", fontSize: 15, lineHeight: 1.55, color: "#0f1419",
          margin: 0, whiteSpace: "pre-wrap", wordWrap: "break-word",
        }}>
          {bodyText}
        </p>
      )}

      {/* Photos */}
      {hasPhotos && <PhotoGrid photos={tweet.photos!} tweetUrl={tweetUrl} />}

      {/* Footer with stats + actions */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "8px 16px 12px", borderTop: "1px solid #f0f0f0",
        background: "linear-gradient(to bottom, #fafbfc, #f5f7f9)",
      }}>
        <div style={{ display: "flex", gap: 14, fontSize: 13, color: "#536471" }}>
          {tweet.favorite_count > 0 && <span>❤️ {formatCount(tweet.favorite_count)}</span>}
          {tweet.conversation_count > 0 && <span>💬 {formatCount(tweet.conversation_count)}</span>}
          {tweet.created_at && (
            <span style={{ color: "#8899a6" }}>{timeAgo(tweet.created_at)}</span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {bodyText && (
            <button
              onClick={() => setExpanded(!expanded)}
              style={{
                background: "none", border: "none", color: "#536471", cursor: "pointer",
                fontSize: 12, padding: "4px 8px", fontFamily: "inherit", borderRadius: 6,
              }}
              onMouseOver={(e) => { e.currentTarget.style.color = "#1DA1F2"; e.currentTarget.style.background = "rgba(29,155,240,0.08)"; }}
              onMouseOut={(e) => { e.currentTarget.style.color = "#536471"; e.currentTarget.style.background = "none"; }}
            >
              {expanded ? "Hide text ▲" : "Show text ▼"}
            </button>
          )}
          <a
            href={tweetUrl} target="_blank" rel="noopener noreferrer"
            style={{
              display: "inline-flex", alignItems: "center", color: "#fff", textDecoration: "none",
              fontWeight: 600, fontSize: 12, background: "#0f1419", padding: "6px 16px",
              borderRadius: 20, transition: "background 0.15s",
            }}
            onMouseOver={(e) => (e.currentTarget.style.background = "#333")}
            onMouseOut={(e) => (e.currentTarget.style.background = "#0f1419")}
          >
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
