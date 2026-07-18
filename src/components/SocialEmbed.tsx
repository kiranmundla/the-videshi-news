import { useState, useEffect, useRef } from "react";
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
              maxHeight: count === 1 ? 400 : "none",
              objectFit: "cover",
              display: "block",
              aspectRatio: count === 1 ? undefined : "4/3",
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
        background: "#0f0f0f", border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 14, padding: 32, textAlign: "center", color: "rgba(255,255,255,0.4)", fontSize: 13,
      }}>
        Loading post…
      </div>
    );
  }

  if (error || !tweet) {
    return (
      <div style={{
        background: "#0f0f0f", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: 20, textAlign: "center",
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
      background: "#0f0f0f",
      borderRadius: 14,
      overflow: "hidden",
      border: "1px solid rgba(255,255,255,0.08)",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    }}>
      {/* Header — matches X embed: avatar | name+handle | X icon */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "14px 16px 6px" }}>
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
              border: "2px solid rgba(255,255,255,0.12)",
            }}
          />
        </a>
        <div style={{ flex: 1, minWidth: 0, overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <a href={tweetUrl} target="_blank" rel="noopener noreferrer"
               style={{ color: "#fff", textDecoration: "none", fontWeight: 700, fontSize: 15, lineHeight: 1.3 }}>
              {user.name}
            </a>
            {(user.is_blue_verified || user.verified_type) && (
              <VerifiedBadge type={user.verified_type} />
            )}
          </div>
          <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 14, lineHeight: 1.3, display: "flex", alignItems: "center", gap: 2 }}>
            <a href={`https://x.com/${user.screen_name}`} target="_blank" rel="noopener noreferrer"
               style={{ color: "rgba(255,255,255,0.5)", textDecoration: "none" }}>
              @{user.screen_name}
            </a>
            <span style={{ color: "rgba(255,255,255,0.35)" }}> · </span>
            <a href={tweetUrl} target="_blank" rel="noopener noreferrer"
               style={{ color: "#1DA1F2", textDecoration: "none", fontWeight: 500, fontSize: 14 }}>
              Follow
            </a>
          </div>
        </div>
        <a href={tweetUrl} target="_blank" rel="noopener noreferrer"
           style={{ color: "rgba(255,255,255,0.7)", flexShrink: 0, marginLeft: "auto" }}>
          <XIcon />
        </a>
      </div>

      {/* Photos */}
      {hasPhotos && <PhotoGrid photos={tweet.photos!} tweetUrl={tweetUrl} />}

      {/* Text — always visible when no photos, collapsible when photos present */}
      {bodyText && (
        <div style={{ padding: "0 16px" }}>
          {(!hasPhotos || expanded) && (
            <p style={{
              fontSize: 15, lineHeight: 1.55, color: "rgba(255,255,255,0.85)",
              margin: "0 0 8px", whiteSpace: "pre-wrap", wordWrap: "break-word",
            }}>
              {bodyText}
            </p>
          )}
          {hasPhotos && (
            <button
              onClick={() => setExpanded(!expanded)}
              style={{
                background: "none", border: "none", color: "#1DA1F2", cursor: "pointer",
                fontSize: 13, padding: "2px 0 8px", fontFamily: "inherit", fontWeight: 500,
              }}
            >
              {expanded ? "Hide text ▲" : "Show text ▼"}
            </button>
          )}
        </div>
      )}

      {/* Footer with stats + View on X */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "8px 16px 12px", borderTop: "1px solid rgba(255,255,255,0.08)",
      }}>
        <div style={{ display: "flex", gap: 14, fontSize: 13, color: "rgba(255,255,255,0.4)" }}>
          {tweet.favorite_count > 0 && <span>❤️ {formatCount(tweet.favorite_count)}</span>}
          {tweet.conversation_count > 0 && <span>💬 {formatCount(tweet.conversation_count)}</span>}
          {tweet.created_at && (
            <span style={{ color: "rgba(255,255,255,0.3)" }}>{timeAgo(tweet.created_at)}</span>
          )}
        </div>
        <a
          href={tweetUrl} target="_blank" rel="noopener noreferrer"
          style={{
            display: "inline-flex", alignItems: "center", color: "#fff", textDecoration: "none",
            fontWeight: 600, fontSize: 12, background: "rgba(255,255,255,0.12)", padding: "6px 16px",
            borderRadius: 20, transition: "background 0.15s",
          }}
          onMouseOver={(e) => (e.currentTarget.style.background = "#333")}
          onMouseOut={(e) => (e.currentTarget.style.background = "#0f1419")}
        >
          View on 𝕏
        </a>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */

function InstagramEmbed({ url, caption }: { url: string; caption?: string }) {
  const shortcode = extractInstaShortcode(url);
  if (!shortcode) return null;

  // Determine the correct permalink path based on the original URL
  const isReel = /\/reel\//.test(url);
  const isTv = /\/tv\//.test(url);
  const pathType = isReel ? "reel" : isTv ? "tv" : "p";
  const permalink = `https://www.instagram.com/${pathType}/${shortcode}/`;

  // Use Instagram's official embed method (blockquote + embed.js)
  // which auto-sizes the embed correctly — same approach as CelebrityBuzz/HeroMedia
  const ref = useRef<HTMLDivElement>(null);
  const [loaded, setLoaded] = useState(false);
  const [timedOut, setTimedOut] = useState(false);

  useEffect(() => {
    // Watch for embed.js replacing the blockquote with an iframe
    const observer = new MutationObserver(() => {
      if (ref.current?.querySelector("iframe")) {
        setLoaded(true);
        observer.disconnect();
      }
    });
    if (ref.current) {
      observer.observe(ref.current, { childList: true, subtree: true });
    }

    const w = window as unknown as { instgrm?: { Embeds: { process: (el?: HTMLElement) => void } } };
    if (w.instgrm?.Embeds) {
      w.instgrm.Embeds.process(ref.current || undefined);
    } else if (!document.querySelector('script[src="https://www.instagram.com/embed.js"]')) {
      const script = document.createElement("script");
      script.src = "https://www.instagram.com/embed.js";
      script.async = true;
      script.onload = () => {
        (window as any).instgrm?.Embeds?.process(ref.current || undefined);
      };
      document.body.appendChild(script);
    }

    // Fallback: if embed doesn't render within 5s, show a link instead
    const timeout = setTimeout(() => {
      if (!ref.current?.querySelector("iframe")) {
        setTimedOut(true);
      }
    }, 5000);

    return () => {
      observer.disconnect();
      clearTimeout(timeout);
    };
  }, [shortcode]);

  // If embed.js failed, show a compact fallback link instead of blank space
  if (timedOut && !loaded) {
    return (
      <figure className="my-6 flex flex-col items-center">
        <a
          href={permalink}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-sm"
          style={{ maxWidth: 540, width: "100%" }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.5"/></svg>
          <span>View on Instagram</span>
        </a>
        {caption && (
          <figcaption className="mt-2 text-sm text-muted-foreground text-center">
            {caption}
          </figcaption>
        )}
      </figure>
    );
  }

  return (
    <figure className="my-6 flex flex-col items-center" ref={ref}>
      <blockquote
        className="instagram-media"
        data-instgrm-permalink={permalink}
        data-instgrm-version="14"
        style={{
          background: "#FFF",
          border: 0,
          borderRadius: 3,
          margin: "0 auto",
          maxWidth: 540,
          width: "100%",
          minWidth: 326,
          padding: 0,
        }}
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

/* ── Minimal inline tweet card for article bodies ── */

export function MinimalTweetEmbed({ url }: { url: string }) {
  const tweetId = extractTweetId(url);
  const handle = url.match(/(?:twitter\.com|x\.com)\/(\w+)\//)?.[1] ?? "";

  if (!tweetId) return null;

  const { data: tweet, isLoading, error } = useTweet(tweetId);

  /* Loading / error fallback — just a styled link */
  if (isLoading || error || !tweet) {
    return (
      <div style={{ margin: "24px auto", maxWidth: 480 }}>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "14px 18px", borderRadius: 10,
            border: "1px solid #e0ddd8", background: "#faf9f7",
            textDecoration: "none", color: "#333",
          }}
        >
          <svg viewBox="0 0 24 24" width="18" height="18" style={{ flexShrink: 0 }}>
            <path fill="#000" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
          <span style={{ flex: 1, fontSize: 14, color: "#555" }}>
            {handle ? `@${handle}` : "Post"}
          </span>
          <span style={{ fontSize: 13, color: "#1d9bf0", fontWeight: 500 }}>
            {isLoading ? "Loading…" : "View on X →"}
          </span>
        </a>
      </div>
    );
  }

  const user = tweet.user;
  const bodyText = tweet.text?.replace(/https:\/\/t\.co\/\S+/g, "").trim();
  const tweetUrl = `https://x.com/${user.screen_name}/status/${tweet.id_str}`;

  return (
    <div style={{ margin: "24px auto", maxWidth: 480 }}>
      <a
        href={tweetUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: "block", padding: "16px 18px", borderRadius: 10,
          border: "1px solid #e0ddd8", background: "#faf9f7",
          textDecoration: "none", color: "#333",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: bodyText ? 8 : 0 }}>
          <svg viewBox="0 0 24 24" width="16" height="16" style={{ flexShrink: 0 }}>
            <path fill="#000" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
          <span style={{ fontWeight: 600, fontSize: 14 }}>{user.name}</span>
          {(user.is_blue_verified || user.verified_type) && (
            <svg viewBox="0 0 22 22" width="14" height="14" style={{ flexShrink: 0 }}>
              <path fill="#1d9bf0" d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.855-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.607-.274 1.264-.144 1.897.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" />
            </svg>
          )}
          <span style={{ color: "#888", fontSize: 13 }}>@{user.screen_name}</span>
        </div>
        {bodyText && (
          <p style={{ margin: 0, fontSize: 14, lineHeight: 1.55, color: "#444" }}>
            {bodyText.length > 200 ? bodyText.slice(0, 200) + "…" : bodyText}
          </p>
        )}
        <div style={{ marginTop: 10, fontSize: 13, color: "#1d9bf0", fontWeight: 500 }}>
          View on X →
        </div>
      </a>
    </div>
  );
}
