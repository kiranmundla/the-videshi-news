import { useState, useEffect, useCallback, useRef } from "react";

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

let igScriptLoaded = false;
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
    s.onload = () => {
      igScriptLoaded = true;
      cb?.();
    };
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

/* ── Instagram Embed Card ── */

function InstagramEmbedCard({
  post,
  active,
  onClick,
}: {
  post: BuzzPost;
  active: boolean;
  onClick: () => void;
}) {
  const displayName = post.celebrity || post.name || post.handle;
  const sc = post.shortcode || extractInstaShortcode(post.url);
  const embedRef = useRef<HTMLDivElement>(null);
  const [processed, setProcessed] = useState(false);
  // Once activated, stay alive — never tear down
  const [everActivated, setEverActivated] = useState(false);

  useEffect(() => {
    if (active && !everActivated) setEverActivated(true);
  }, [active, everActivated]);

  // Process embed when card becomes active
  useEffect(() => {
    if (!everActivated || !sc || processed) return;
    ensureInstagramEmbed(() => {
      // Short delay to let the blockquote render in DOM
      setTimeout(() => {
        window.instgrm?.Embeds.process();
        setProcessed(true);
      }, 100);
    });
  }, [everActivated, sc, processed]);

  // Re-process if shortcode changes
  useEffect(() => {
    setProcessed(false);
  }, [sc]);

  return (
    <div
      style={{
        width: "72vw",
        maxWidth: 340,
        flexShrink: 0,
        scrollSnapAlign: "start",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          aspectRatio: "3/4",
          borderRadius: 12,
          overflow: "hidden",
          background: "#1a1a1a",
          boxShadow: "0 2px 8px rgba(0,0,0,0.10)",
        }}
      >
        {everActivated && sc ? (
          <div
            ref={embedRef}
            onClick={(e) => {
              if ((e.target as HTMLElement).tagName === "IFRAME") return;
              onClick();
            }}
            className="ig-embed-minimal"
            style={{
              position: "absolute",
              top: -54,   /* Crop Instagram header (profile pic, handle, follow) */
              left: 0,
              right: 0,
              bottom: -100, /* Extend past container to hide footer/likes/captions */
              pointerEvents: "none", /* Let clicks pass to parent */
            }}
          >
            <blockquote
              className="instagram-media"
              data-instgrm-permalink={`https://www.instagram.com/p/${sc}/`}
              data-instgrm-version="14"
              style={{
                background: "#FFF",
                border: 0,
                borderRadius: 0,
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
          /* Placeholder / fallback: show Wikipedia thumbnail or caption card */
          <FallbackCard post={post} onClick={onClick} />
        )}
      </div>

      {/* Name below card */}
      <div style={{ padding: "6px 2px 0" }}>
        <div
          style={{
            color: "#1a1a1a",
            fontSize: 13,
            fontWeight: 600,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {displayName}
        </div>
        <div style={{ color: "#888", fontSize: 11, marginTop: 1 }}>
          @{post.handle}
        </div>
      </div>
    </div>
  );
}

/* ── Static Fallback Card (Wikipedia thumbnail or caption card) ── */

function FallbackCard({
  post,
  onClick,
}: {
  post: BuzzPost;
  onClick: () => void;
}) {
  const displayName = post.celebrity || post.name || post.handle;
  const hasThumbnail = !!(post.thumbnail && post.thumbnail.length > 0);
  const [imgError, setImgError] = useState(false);

  return (
    <div
      onClick={onClick}
      style={{
        cursor: "pointer",
        width: "100%",
        aspectRatio: "3/4",
        position: "relative",
      }}
    >
      {hasThumbnail && !imgError ? (
        <img
          src={post.thumbnail}
          alt={displayName}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setImgError(true)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "top",
            display: "block",
          }}
        />
      ) : (
        /* Caption fallback */
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            padding: "24px 20px",
            background:
              "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            width: "100%",
            height: "100%",
            boxSizing: "border-box",
          }}
        >
          <div style={{ fontSize: 36, marginBottom: 12 }}>📸</div>
          <div
            style={{
              fontSize: 16,
              fontWeight: 700,
              color: "#fff",
              textAlign: "center",
              marginBottom: 8,
            }}
          >
            {displayName}
          </div>
          <div
            style={{
              fontSize: 11,
              color: "#b8860b",
              marginBottom: 12,
              fontWeight: 600,
            }}
          >
            @{post.handle}
          </div>
          {post.caption && (
            <div
              style={{
                fontSize: 12,
                color: "#ccc",
                textAlign: "center",
                lineHeight: 1.5,
                maxHeight: "50%",
                overflow: "hidden",
                display: "-webkit-box",
                WebkitLineClamp: 6,
                WebkitBoxOrient: "vertical" as const,
              }}
            >
              {post.caption}
            </div>
          )}
        </div>
      )}

      {/* Instagram badge */}
      <div
        style={{
          position: "absolute",
          top: 6,
          right: 6,
          width: 22,
          height: 22,
          borderRadius: 6,
          background:
            "linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
          zIndex: 3,
        }}
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="white"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="2" y="2" width="20" height="20" rx="5" />
          <circle cx="12" cy="12" r="5" />
          <circle cx="17.5" cy="6.5" r="1.5" fill="white" stroke="none" />
        </svg>
      </div>
    </div>
  );
}

/* ── Main component ── */

export default function CelebrityBuzz() {
  const [posts, setPosts] = useState<BuzzPost[]>([]);
  const [visibleIdx, setVisibleIdx] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // Load posts from JSON
  useEffect(() => {
    fetch("/data/celebrity-buzz.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.posts?.length) setPosts(data.posts);
      })
      .catch(() => {});
  }, []);

  // Track which card is visible for lazy embed loading
  const updateVisibleIndex = useCallback(() => {
    const el = scrollRef.current;
    if (!el || !el.children.length) return;
    // Approximate card width from first child
    const firstChild = el.children[0] as HTMLElement;
    if (!firstChild) return;
    const cardWidth = firstChild.offsetWidth + 12; // 12 = gap
    const idx = Math.round(el.scrollLeft / cardWidth);
    setVisibleIdx(Math.max(0, Math.min(idx, posts.length - 1)));
  }, [posts.length]);

  // Scroll buttons
  const updateScrollButtons = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(
      el.scrollLeft < el.scrollWidth - el.clientWidth - 10
    );
  }, []);

  const scrollStrip = useCallback(
    (direction: "left" | "right") => {
      const el = scrollRef.current;
      if (!el) return;
      const amount = el.clientWidth * 0.75;
      el.scrollBy({
        left: direction === "right" ? amount : -amount,
        behavior: "smooth",
      });
    },
    []
  );

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;

    const onScroll = () => {
      updateScrollButtons();
      updateVisibleIndex();
    };

    updateScrollButtons();
    updateVisibleIndex();
    el.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      el.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, [posts, updateScrollButtons, updateVisibleIndex]);

  if (!posts.length) return null;

  const arrowStyle: React.CSSProperties = {
    position: "absolute",
    top: "50%",
    transform: "translateY(-50%)",
    zIndex: 10,
    background: "rgba(0,0,0,0.6)",
    backdropFilter: "blur(4px)",
    border: "none",
    color: "#fff",
    fontSize: "18px",
    width: "36px",
    height: "36px",
    borderRadius: "50%",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.2s, opacity 0.2s",
    opacity: 0.9,
  };

  return (
    <section className="mt-14 mb-8">
      {/* Style overrides for Instagram embeds inside the carousel */}
      <style>{`
        .celeb-buzz-strip::-webkit-scrollbar { display: none; }
        .celeb-buzz-strip .instagram-media {
          max-width: 100% !important;
          min-width: 100% !important;
          width: 100% !important;
          margin: 0 !important;
          border-radius: 0 !important;
          box-shadow: none !important;
        }
        .celeb-buzz-strip .instagram-media iframe {
          max-width: 100% !important;
          min-width: 100% !important;
          width: 100% !important;
          border-radius: 0 !important;
        }
        .ig-embed-minimal {
          pointer-events: none;
        }
        .ig-embed-minimal iframe {
          pointer-events: auto;
        }
      `}</style>

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

      <div style={{ position: "relative" }}>
        {/* Left arrow */}
        {canScrollLeft && (
          <button
            onClick={() => scrollStrip("left")}
            style={{ ...arrowStyle, left: 4 }}
            aria-label="Scroll left"
          >
            ‹
          </button>
        )}

        <div
          ref={scrollRef}
          className="celeb-buzz-strip"
          style={
            {
              display: "flex",
              alignItems: "flex-start",
              gap: 12,
              overflowX: "auto",
              overflowY: "hidden",
              WebkitOverflowScrolling: "touch",
              scrollbarWidth: "none",
              msOverflowStyle: "none",
              scrollSnapType: "x mandatory",
              paddingLeft: "4%",
              paddingRight: "4%",
            } as React.CSSProperties
          }
        >
          {posts.map((post, i) => {
            const sc =
              post.shortcode || extractInstaShortcode(post.url);
            const hasEmbed = !!sc;
            // Lazy load: only activate embeds within ±1 of visible
            const isNearVisible =
              i >= visibleIdx - 1 && i <= visibleIdx + 1;

            if (hasEmbed) {
              return (
                <InstagramEmbedCard
                  key={`${post.handle}-${i}`}
                  post={post}
                  active={isNearVisible}
                  onClick={() => {
                    // Open the Instagram post in a new tab
                    window.open(
                      `https://www.instagram.com/p/${sc}/`,
                      "_blank",
                      "noopener,noreferrer"
                    );
                  }}
                />
              );
            }

            // No shortcode — use fallback static card
            return (
              <div
                key={`${post.handle}-${i}`}
                style={{
                  width: "72vw",
                  maxWidth: 340,
                  flexShrink: 0,
                  scrollSnapAlign: "start",
                }}
              >
                <div
                  style={{
                    position: "relative",
                    width: "100%",
                    aspectRatio: "3/4",
                    borderRadius: 12,
                    overflow: "hidden",
                    background: "#1a1a1a",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
                  }}
                >
                  <FallbackCard
                    post={post}
                    onClick={() => {
                      window.open(
                        post.url,
                        "_blank",
                        "noopener,noreferrer"
                      );
                    }}
                  />
                </div>

                {/* Name below card */}
                <div style={{ padding: "6px 2px 0" }}>
                  <div
                    style={{
                      color: "#1a1a1a",
                      fontSize: 13,
                      fontWeight: 600,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {post.celebrity || post.name || post.handle}
                  </div>
                  <div
                    style={{ color: "#888", fontSize: 11, marginTop: 1 }}
                  >
                    @{post.handle}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right arrow */}
        {canScrollRight && (
          <button
            onClick={() => scrollStrip("right")}
            style={{ ...arrowStyle, right: 4 }}
            aria-label="Scroll right"
          >
            ›
          </button>
        )}
      </div>
    </section>
  );
}
