import { useState, useEffect, useRef } from "react";

interface BuzzPost {
  platform: "instagram" | "twitter";
  url: string;
  celebrity?: string;
  name?: string;
  handle: string;
  timestamp: string;
  thumbnail?: string;
  cdn_thumbnail?: string;
  caption?: string;
  media_type?: string;
  shortcode?: string;
}

function extractInstaShortcode(url: string): string | null {
  const m = url.match(/instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
  return m ? m[1] : null;
}

/* ── Instagram embed.js loader ── */
declare global {
  interface Window {
    instgrm?: { Embeds: { process: () => void } };
  }
}

let igScriptLoading = false;

function ensureInstagramEmbed(cb?: () => void) {
  if (window.instgrm?.Embeds) {
    cb?.();
    return;
  }
  if (!igScriptLoading) {
    igScriptLoading = true;
    const s = document.createElement("script");
    s.src = "https://www.instagram.com/embed.js";
    s.async = true;
    s.onload = () => cb?.();
    document.head.appendChild(s);
  } else {
    const iv = setInterval(() => {
      if (window.instgrm?.Embeds) {
        clearInterval(iv);
        cb?.();
      }
    }, 200);
  }
}

/* ── Main component ── */

export default function CelebrityBuzz() {
  const [posts, setPosts] = useState<BuzzPost[]>([]);
  const [activeIdx, setActiveIdx] = useState(0);
  const [processed, setProcessed] = useState<Set<number>>(new Set());
  const embedRef = useRef<HTMLDivElement>(null);
  const avatarStripRef = useRef<HTMLDivElement>(null);

  // Load posts
  useEffect(() => {
    fetch("/data/celebrity-buzz.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.posts?.length) setPosts(data.posts);
      })
      .catch(() => {});
  }, []);

  // Process embed when active celebrity changes
  useEffect(() => {
    if (!posts.length) return;
    const post = posts[activeIdx];
    const sc = post?.shortcode || extractInstaShortcode(post?.url || "");
    if (!sc || processed.has(activeIdx)) return;

    ensureInstagramEmbed(() => {
      setTimeout(() => {
        window.instgrm?.Embeds.process();
        setProcessed((prev) => new Set(prev).add(activeIdx));
      }, 150);
    });
  }, [activeIdx, posts, processed]);

  // Scroll active avatar into view
  useEffect(() => {
    const strip = avatarStripRef.current;
    if (!strip) return;
    const child = strip.children[activeIdx] as HTMLElement;
    if (!child) return;
    const stripRect = strip.getBoundingClientRect();
    const childRect = child.getBoundingClientRect();
    if (childRect.left < stripRect.left || childRect.right > stripRect.right) {
      child.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
  }, [activeIdx]);

  if (!posts.length) return null;

  const post = posts[activeIdx];
  const displayName = post.celebrity || post.name || post.handle;
  const sc = post.shortcode || extractInstaShortcode(post.url);

  return (
    <section className="mt-14 mb-8">
      <style>{`
        .celeb-avatar-strip::-webkit-scrollbar { display: none; }
        .celeb-embed-container .instagram-media {
          max-width: 100% !important;
          min-width: 100% !important;
          width: 100% !important;
          margin: 0 !important;
          border-radius: 12px !important;
          box-shadow: none !important;
          border: none !important;
        }
        .celeb-embed-container .instagram-media iframe {
          max-width: 100% !important;
          min-width: 100% !important;
          width: 100% !important;
          border-radius: 12px !important;
        }
      `}</style>

      {/* Header */}
      <div
        className="flex items-center gap-4 mb-4 pb-3"
        style={{ borderBottom: "1px solid hsl(var(--rule))" }}
      >
        <span
          className="font-bold uppercase"
          style={{ fontSize: 11, letterSpacing: "0.12em", color: "#888" }}
        >
          ✨ Celebrity Buzz
        </span>
      </div>

      {/* Main embed area — one celebrity at a time */}
      <div className="celeb-embed-container" style={{ marginBottom: 12 }}>
        {sc ? (
          <div ref={embedRef} key={`embed-${activeIdx}`}>
            <blockquote
              className="instagram-media"
              data-instgrm-permalink={`https://www.instagram.com/p/${sc}/`}
              data-instgrm-version="14"
              data-instgrm-captioned
              style={{
                background: "#FFF",
                border: 0,
                borderRadius: 12,
                boxShadow: "none",
                margin: 0,
                maxWidth: "100%",
                minWidth: "100%",
                padding: 0,
                width: "100%",
              }}
            />
          </div>
        ) : (
          /* Fallback: Wikipedia thumbnail card */
          <div
            style={{
              position: "relative",
              width: "100%",
              aspectRatio: "3/4",
              maxHeight: 500,
              borderRadius: 12,
              overflow: "hidden",
              background: "#1a1a1a",
              boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
              cursor: "pointer",
            }}
            onClick={() => window.open(post.url, "_blank", "noopener,noreferrer")}
          >
            {post.thumbnail ? (
              <img
                src={post.thumbnail}
                alt={displayName}
                referrerPolicy="no-referrer"
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  objectPosition: "top",
                  display: "block",
                }}
              />
            ) : (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center",
                  width: "100%",
                  height: "100%",
                  padding: 24,
                  boxSizing: "border-box",
                  background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
                }}
              >
                <div style={{ fontSize: 36, marginBottom: 12 }}>📸</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", textAlign: "center" }}>
                  {displayName}
                </div>
                <div style={{ fontSize: 11, color: "#b8860b", fontWeight: 600, marginTop: 6 }}>
                  @{post.handle}
                </div>
                {post.caption && (
                  <div style={{
                    fontSize: 12, color: "#ccc", textAlign: "center",
                    marginTop: 12, lineHeight: 1.5, maxHeight: 100,
                    overflow: "hidden", display: "-webkit-box",
                    WebkitLineClamp: 4, WebkitBoxOrient: "vertical" as const,
                  }}>
                    {post.caption}
                  </div>
                )}
              </div>
            )}

            {/* IG badge */}
            <div style={{
              position: "absolute", top: 8, right: 8,
              width: 24, height: 24, borderRadius: 7,
              background: "linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 1px 4px rgba(0,0,0,0.3)", zIndex: 3,
            }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white"
                strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" />
                <circle cx="12" cy="12" r="5" />
                <circle cx="17.5" cy="6.5" r="1.5" fill="white" stroke="none" />
              </svg>
            </div>
          </div>
        )}

        {/* Celebrity name below embed */}
        <div style={{ padding: "8px 2px 0" }}>
          <div style={{ color: "#1a1a1a", fontSize: 15, fontWeight: 700 }}>
            {displayName}
          </div>
          <div style={{ color: "#888", fontSize: 12, marginTop: 2 }}>
            @{post.handle}
          </div>
        </div>
      </div>

      {/* Bottom avatar strip — scroll to switch celebrities */}
      <div
        ref={avatarStripRef}
        className="celeb-avatar-strip"
        style={{
          display: "flex",
          gap: 8,
          overflowX: "auto",
          overflowY: "hidden",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          paddingBottom: 4,
          paddingTop: 8,
          borderTop: "1px solid hsl(var(--rule))",
        } as React.CSSProperties}
      >
        {posts.map((p, i) => {
          const isActive = i === activeIdx;
          const name = p.celebrity || p.name || p.handle;
          return (
            <button
              key={`avatar-${i}`}
              onClick={() => setActiveIdx(i)}
              style={{
                flexShrink: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 4,
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: "4px 4px",
                opacity: isActive ? 1 : 0.5,
                transition: "opacity 0.2s, transform 0.2s",
                transform: isActive ? "scale(1.05)" : "scale(1)",
              }}
              aria-label={name}
            >
              {/* Avatar circle */}
              <div style={{
                width: 48,
                height: 48,
                borderRadius: "50%",
                overflow: "hidden",
                border: isActive
                  ? "2.5px solid #b8860b"
                  : "2px solid transparent",
                background: "#eee",
                flexShrink: 0,
              }}>
                {p.thumbnail ? (
                  <img
                    src={p.thumbnail}
                    alt={name}
                    referrerPolicy="no-referrer"
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      objectPosition: "top",
                      display: "block",
                    }}
                  />
                ) : (
                  <div style={{
                    width: "100%", height: "100%",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    background: "linear-gradient(135deg, #1a1a2e, #0f3460)",
                    color: "#fff", fontSize: 16, fontWeight: 700,
                  }}>
                    {name.charAt(0)}
                  </div>
                )}
              </div>
              {/* Name label */}
              <div style={{
                fontSize: 9,
                fontWeight: isActive ? 700 : 500,
                color: isActive ? "#1a1a1a" : "#888",
                maxWidth: 56,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
                textAlign: "center",
                lineHeight: 1.2,
              }}>
                {name.split(" ")[0]}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
