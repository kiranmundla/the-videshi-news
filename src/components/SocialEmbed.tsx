import { useState, useEffect, useRef } from "react";
import { useTweet } from "react-tweet";
import { TweetPhotos, TweetVideoPlayer } from "@/components/TweetMedia";
import {
  useStaticTweet,
  type StaticTweet,
  type TweetPhoto,
  type TweetVideo,
} from "@/lib/tweetMedia";

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

/* ── Unified tweet view model ───────────────────────────────────────
   Both data sources — the static prebuild JSON (preferred, no runtime
   call) and react-tweet's runtime syndication fetch (fallback) — map
   into this shape, and both card variants render from it. Photos are
   browsed IN PLACE (strip + lightbox) and videos play via X's official
   embed on tap; see TweetMedia.tsx. */

interface TweetView {
  name: string;
  screenName: string;
  avatar: string;
  verified: boolean;
  verifiedType?: string;
  text: string;
  createdAt: string;
  favoriteCount: number;
  conversationCount: number;
  tweetUrl: string;
  photos: TweetPhoto[];
  video: TweetVideo | null;
}

function largePhotoUrl(url: string): string {
  const base = (url || "").split("?")[0];
  if (base.includes("/media/")) {
    const fmt = base.toLowerCase().endsWith(".png") ? "png" : "jpg";
    return `${base}?format=${fmt}&name=large`;
  }
  return url;
}

function runtimeToView(tweet: any): TweetView {
  const user = tweet.user;
  const video = tweet.video?.poster
    ? {
        poster: tweet.video.poster as string,
        aspect: (Array.isArray(tweet.video.aspectRatio)
          ? tweet.video.aspectRatio
          : [16, 9]) as [number, number],
        duration_ms: 0,
        type: "video",
      }
    : null;
  return {
    name: user.name,
    screenName: user.screen_name,
    avatar: hiResAvatar(user.profile_image_url_https),
    verified: !!(user.is_blue_verified || user.verified_type),
    verifiedType: user.verified_type,
    text: tweet.text ?? "",
    createdAt: tweet.created_at ?? "",
    favoriteCount: tweet.favorite_count ?? 0,
    conversationCount: tweet.conversation_count ?? 0,
    tweetUrl: `https://x.com/${user.screen_name}/status/${tweet.id_str}`,
    photos: (tweet.photos ?? []).map((p: any) => ({
      url: largePhotoUrl(p.url),
      width: p.width ?? 0,
      height: p.height ?? 0,
    })),
    video,
  };
}

function staticToView(s: StaticTweet): TweetView {
  return {
    name: s.user.name,
    screenName: s.user.screen_name,
    avatar: hiResAvatar(s.user.avatar),
    verified: s.user.verified,
    verifiedType: s.user.verified_type ?? undefined,
    text: s.text,
    createdAt: s.created_at,
    favoriteCount: s.favorite_count,
    conversationCount: s.conversation_count,
    tweetUrl: s.url,
    photos: s.photos,
    video: s.video,
  };
}

/* ── Dark tweet card (markdown-body articles) ── */
function TweetCard({ view }: { view: TweetView }) {
  const [expanded, setExpanded] = useState(false);
  const { tweetUrl } = view;
  const hasPhotos = view.photos.length > 0;
  const hasVideo = !!view.video;
  const hasMedia = hasPhotos || hasVideo;
  const bodyText = view.text?.replace(/https:\/\/t\.co\/\S+/g, "").trim();

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
        <a href={`https://x.com/${view.screenName}`} target="_blank" rel="noopener noreferrer"
           style={{ flexShrink: 0 }}>
          <img
            src={view.avatar}
            alt={view.name}
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
              {view.name}
            </a>
            {view.verified && <VerifiedBadge type={view.verifiedType} />}
          </div>
          <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 14, lineHeight: 1.3, display: "flex", alignItems: "center", gap: 2 }}>
            <a href={`https://x.com/${view.screenName}`} target="_blank" rel="noopener noreferrer"
               style={{ color: "rgba(255,255,255,0.5)", textDecoration: "none" }}>
              @{view.screenName}
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

      {/* Photos — in place: strip + lightbox, no tap-out */}
      {hasPhotos && (
        <div style={{ margin: "0 16px 12px", borderRadius: 12, overflow: "hidden" }}>
          <TweetPhotos
            photos={view.photos}
            tweetUrl={tweetUrl}
            authorLabel={`@${view.screenName} on X`}
            dark
          />
        </div>
      )}

      {/* Video — poster + play; tap swaps in the official X embed in
          place. Renders alongside photos too: X allows mixed-media
          tweets (photos + one video in a single post). */}
      {hasVideo && (
        <div style={{ margin: "0 16px 12px", borderRadius: 12, overflow: "hidden" }}>
          <TweetVideoPlayer url={tweetUrl} video={view.video!} dark />
        </div>
      )}

      {/* Text — always visible when no media, collapsible when media present */}
      {bodyText && (
        <div style={{ padding: "0 16px" }}>
          {(!hasMedia || expanded) && (
            <p style={{
              fontSize: 15, lineHeight: 1.55, color: "rgba(255,255,255,0.85)",
              margin: "0 0 8px", whiteSpace: "pre-wrap", wordWrap: "break-word",
            }}>
              {bodyText}
            </p>
          )}
          {hasMedia && (
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
          {view.favoriteCount > 0 && <span>❤️ {formatCount(view.favoriteCount)}</span>}
          {view.conversationCount > 0 && <span>💬 {formatCount(view.conversationCount)}</span>}
          {view.createdAt && (
            <span style={{ color: "rgba(255,255,255,0.3)" }}>{timeAgo(view.createdAt)}</span>
          )}
        </div>
        <a
          href={tweetUrl}
          target="_blank" rel="noopener noreferrer"
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

function RuntimeTweetCard({ tweetId, url }: { tweetId: string; url: string }) {
  const { data: tweet, isLoading, error } = useTweet(tweetId);

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

  return <TweetCard view={runtimeToView(tweet)} />;
}

/** Static-first: render from /data/tweet-media.json when the prebuild
    covered this tweet; otherwise the runtime syndication fetch. */
function TweetCardRouter({ tweetId, url }: { tweetId: string; url: string }) {
  const entry = useStaticTweet(tweetId);
  if (entry === undefined) {
    return (
      <div style={{
        background: "#0f0f0f", border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 14, padding: 32, textAlign: "center", color: "rgba(255,255,255,0.4)", fontSize: 13,
      }}>
        Loading post…
      </div>
    );
  }
  if (entry) return <TweetCard view={staticToView(entry)} />;
  return <RuntimeTweetCard tweetId={tweetId} url={url} />;
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
      <div style={{ maxWidth: 540, width: '100%', borderRadius: 8, position: 'relative', overflow: 'hidden' }}>
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
            marginBottom: -56,
          }}
        />
      </div>
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
        <TweetCardRouter tweetId={tweetId} url={url} />
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

/* ── Minimal inline tweet card for article bodies (HTML-body path) ── */

function MinimalTweetCard({ view }: { view: TweetView }) {
  const { tweetUrl } = view;
  const bodyText = view.text?.replace(/https:\/\/t\.co\/\S+/g, "").trim();
  const photos = view.photos;
  const hasVideo = !!view.video;

  return (
    <div style={{ margin: "24px auto", maxWidth: 480 }}>
      <div
        style={{
          display: "block", borderRadius: 10,
          border: "1px solid #e0ddd8", background: "#faf9f7",
          overflow: "hidden",
        }}
      >
        <a
          href={tweetUrl}
          target="_blank"
          rel="noopener noreferrer"
          style={{ display: "block", textDecoration: "none", color: "#333" }}
        >
          <div style={{ padding: "16px 18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: bodyText ? 8 : 0 }}>
              <svg viewBox="0 0 24 24" width="16" height="16" style={{ flexShrink: 0 }}>
                <path fill="#000" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{view.name}</span>
              {view.verified && (
                <svg viewBox="0 0 22 22" width="14" height="14" style={{ flexShrink: 0 }}>
                  <path fill="#1d9bf0" d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.855-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.607-.274 1.264-.144 1.897.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" />
                </svg>
              )}
              <span style={{ color: "#888", fontSize: 13 }}>@{view.screenName}</span>
            </div>
            {bodyText && (
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.55, color: "#444" }}>
                {bodyText.length > 200 ? bodyText.slice(0, 200) + "…" : bodyText}
              </p>
            )}
          </div>
        </a>
        {/* Photos — in place: strip + lightbox, no tap-out */}
        {photos.length > 0 && (
          <TweetPhotos
            photos={photos}
            tweetUrl={tweetUrl}
            authorLabel={`@${view.screenName} on X`}
          />
        )}
        {/* Video — poster + play; tap swaps in the official X embed in
            place. Also renders with photos (X mixed-media tweets). */}
        {hasVideo && (
          <TweetVideoPlayer url={tweetUrl} video={view.video!} />
        )}
        <a href={tweetUrl} target="_blank" rel="noopener noreferrer" style={{ display: "block", textDecoration: "none" }}>
          <div style={{ padding: "10px 18px 14px", fontSize: 13, color: "#1d9bf0", fontWeight: 500 }}>
            View on X →
          </div>
        </a>
      </div>
    </div>
  );
}

function MinimalTweetFallback({ url, handle, loading }: { url: string; handle: string; loading?: boolean }) {
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
          {loading ? "Loading…" : "View on X →"}
        </span>
      </a>
    </div>
  );
}

function RuntimeMinimalTweetEmbed({ url, tweetId, handle }: { url: string; tweetId: string; handle: string }) {
  const { data: tweet, isLoading, error } = useTweet(tweetId);

  if (isLoading || error || !tweet) {
    return <MinimalTweetFallback url={url} handle={handle} loading={isLoading} />;
  }

  return <MinimalTweetCard view={runtimeToView(tweet)} />;
}

export function MinimalTweetEmbed({ url }: { url: string }) {
  const tweetId = extractTweetId(url);
  const handle = url.match(/(?:twitter\.com|x\.com)\/(\w+)\//)?.[1] ?? "";
  const entry = useStaticTweet(tweetId);

  if (!tweetId) return null;

  if (entry === undefined) {
    return <MinimalTweetFallback url={url} handle={handle} loading />;
  }
  if (entry) return <MinimalTweetCard view={staticToView(entry)} />;
  return <RuntimeMinimalTweetEmbed url={url} tweetId={tweetId} handle={handle} />;
}
