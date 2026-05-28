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
}

function extractInstaShortcode(url: string): string | null {
  const m = url.match(/instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
  return m ? m[1] : null;
}

/* ── Twitter widgets loader ── */
declare global {
  interface Window {
    twttr?: { widgets: { load: (el?: HTMLElement) => void } };
  }
}

let twitterScriptLoading = false;

function ensureTwitterWidgets(cb: () => void) {
  if (window.twttr?.widgets) { cb(); return; }
  if (!twitterScriptLoading) {
    twitterScriptLoading = true;
    const s = document.createElement("script");
    s.src = "https://platform.twitter.com/widgets.js";
    s.async = true;
    s.charset = "utf-8";
    s.onload = () => cb();
    document.head.appendChild(s);
  } else {
    const iv = setInterval(() => {
      if (window.twttr?.widgets) { clearInterval(iv); cb(); }
    }, 200);
  }
}

/* ── Lightbox ── */

function BuzzLightbox({ post, images, onClose }: {
  post: BuzzPost;
  images: string[];
  onClose: () => void;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [current, setCurrent] = useState(0);
  const touchStartY = useRef<number | null>(null);
  const total = images.length;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      const el = scrollRef.current;
      if (!el) return;
      if (e.key === "ArrowRight") el.scrollBy({ left: el.clientWidth, behavior: "smooth" });
      if (e.key === "ArrowLeft") el.scrollBy({ left: -el.clientWidth, behavior: "smooth" });
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  // Track scroll position for dots
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const onScroll = () => {
      const idx = Math.round(el.scrollLeft / el.clientWidth);
      setCurrent(Math.min(idx, total - 1));
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, [total]);

  return (
    <div
      onClick={onClose}
      onTouchStart={(e) => { touchStartY.current = e.touches[0].clientY; }}
      onTouchEnd={(e) => {
        if (touchStartY.current === null) return;
        const diff = e.changedTouches[0].clientY - touchStartY.current;
        if (diff > 80) onClose();
        touchStartY.current = null;
      }}
      style={{
        position: "fixed", inset: 0, zIndex: 9999,
        background: "rgba(0,0,0,0.95)",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        animation: "buzzFadeIn 0.15s ease-out",
      }}
    >
      <style>{`@keyframes buzzFadeIn { from { opacity: 0; } to { opacity: 1; } }
        .buzz-lb-scroll::-webkit-scrollbar { display: none; }`}</style>

      <button
        onClick={onClose}
        style={{
          position: "absolute", top: 12, right: 12, zIndex: 20,
          background: "rgba(255,255,255,0.15)", border: "none", color: "#fff",
          width: 36, height: 36, borderRadius: "50%", cursor: "pointer",
          fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center",
        }}
      >×</button>

      {/* Celebrity name */}
      <div style={{ position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)", textAlign: "center", zIndex: 20 }}>
        <div style={{ color: "#fff", fontSize: 16, fontWeight: 600 }}>{post.celebrity || post.name}</div>
        {total > 1 && <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 12, marginTop: 2 }}>{current + 1} / {total}</div>}
      </div>

      {/* Scroll-snap carousel */}
      <div
        ref={scrollRef}
        className="buzz-lb-scroll"
        onClick={(e) => e.stopPropagation()}
        style={{
          display: "flex",
          overflowX: "auto",
          scrollSnapType: "x mandatory",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          width: "95vw",
          maxWidth: 600,
          borderRadius: 8,
        } as React.CSSProperties}
      >
        {images.map((img, i) => (
          <div
            key={i}
            style={{
              flex: "0 0 100%",
              scrollSnapAlign: "center",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              maxHeight: "75vh",
            }}
          >
            <img
              src={img}
              alt={`${post.celebrity || post.name} photo ${i + 1}`}
              referrerPolicy="no-referrer"
              loading={i < 2 ? "eager" : "lazy"}
              style={{
                maxWidth: "100%", maxHeight: "75vh",
                objectFit: "contain", display: "block",
              }}
            />
          </div>
        ))}
      </div>

      {/* Dots */}
      {total > 1 && (
        <div style={{ marginTop: 12, display: "flex", gap: 6, alignItems: "center" }}>
          {images.map((_, i) => (
            <div
              key={i}
              style={{
                width: i === current ? 8 : 6,
                height: i === current ? 8 : 6,
                borderRadius: "50%",
                background: i === current ? "#fff" : "rgba(255,255,255,0.3)",
                transition: "all 0.15s",
              }}
            />
          ))}
        </div>
      )}

      {/* Handle credit */}
      <a
        href={post.url}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(e) => e.stopPropagation()}
        style={{
          marginTop: 10, color: "rgba(255,255,255,0.5)", fontSize: 13,
          textDecoration: "none",
        }}
      >
        {"📷 @"}{post.handle}{" on Instagram"}
      </a>
    </div>
  );
}

/* ── Thumbnail card ── */

function ThumbCard({
  post,
  dynamicSrc,
  loading,
  onClick,
}: {
  post: BuzzPost;
  dynamicSrc: string | null;
  loading: boolean;
  onClick: () => void;
}) {
  const displayName = post.celebrity || post.name || post.handle;
  const fallbackSrc = post.thumbnail || `/images/celebrity-thumbs/${post.handle}.jpg`;
  const hasThumbnail = !!(dynamicSrc || (post.thumbnail && post.thumbnail.length > 0));
  const src = dynamicSrc || fallbackSrc;

  return (
    <div
      onClick={onClick}
      style={{
        width: "72vw",
        maxWidth: 340,
        flexShrink: 0,
        cursor: "pointer",
        scrollSnapAlign: "start",
      }}
    >
      <div style={{
        position: "relative",
        width: "100%",
        aspectRatio: "3/4",
        borderRadius: 12,
        overflow: "hidden",
        background: "#1a1a1a",
        boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
      }}>
        {loading && (
          <div style={{
            position: "absolute", inset: 0, zIndex: 2,
            background: "linear-gradient(110deg, #1a1a1a 30%, #2a2a2a 50%, #1a1a1a 70%)",
            backgroundSize: "200% 100%",
            animation: "shimmer 1.5s ease-in-out infinite",
          }} />
        )}
        {hasThumbnail ? (
          <img
            src={src}
            alt={displayName}
            loading="lazy"
            referrerPolicy="no-referrer"
            onError={(e) => {
              const img = e.currentTarget;
              // On error, replace with caption card
              const parent = img.parentElement;
              if (parent) {
                img.style.display = "none";
                // Show caption overlay
                const overlay = parent.querySelector(".caption-fallback") as HTMLElement;
                if (overlay) overlay.style.display = "flex";
              }
            }}
            style={{
              width: "100%", height: "100%",
              objectFit: "cover", objectPosition: "top", display: "block",
              opacity: loading ? 0 : 1,
              transition: "opacity 0.3s ease",
            }}
          />
        ) : null}

        {/* Caption fallback card - shown when no thumbnail or image fails */}
        <div className="caption-fallback" style={{
          position: hasThumbnail ? "absolute" : "relative",
          inset: 0,
          display: hasThumbnail ? "none" : "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "24px 20px",
          background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
          width: hasThumbnail ? undefined : "100%",
          height: hasThumbnail ? undefined : "100%",
          boxSizing: "border-box",
        }}>
          <div style={{
            fontSize: 36, marginBottom: 12,
          }}>
            {post.platform === "instagram" ? "📸" : "🐦"}
          </div>
          <div style={{
            fontSize: 16, fontWeight: 700, color: "#fff",
            textAlign: "center", marginBottom: 8,
          }}>
            {displayName}
          </div>
          <div style={{
            fontSize: 11, color: "#b8860b", marginBottom: 12,
            fontWeight: 600,
          }}>
            @{post.handle}
          </div>
          {post.caption && (
            <div style={{
              fontSize: 12, color: "#ccc", textAlign: "center",
              lineHeight: 1.5, maxHeight: "50%", overflow: "hidden",
              display: "-webkit-box",
              WebkitLineClamp: 6,
              WebkitBoxOrient: "vertical" as const,
            }}>
              {post.caption}
            </div>
          )}
        </div>

        {/* Instagram badge */}
        <div style={{
          position: "absolute", top: 6, right: 6,
          width: 22, height: 22, borderRadius: 6,
          background: "linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
          zIndex: 3,
        }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="2" width="20" height="20" rx="5" />
            <circle cx="12" cy="12" r="5" />
            <circle cx="17.5" cy="6.5" r="1.5" fill="white" stroke="none" />
          </svg>
        </div>
      </div>

      {/* Name below image */}
      <div style={{ padding: "6px 2px 0" }}>
        <div style={{
          color: "#1a1a1a", fontSize: 13, fontWeight: 600,
          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
        }}>
          {displayName}
        </div>
        <div style={{
          color: "#888", fontSize: 11, marginTop: 1,
        }}>
          @{post.handle}
        </div>
      </div>
    </div>
  );
}

/* ── Main component ── */

export default function CelebrityBuzz() {
  const [posts, setPosts] = useState<BuzzPost[]>([]);
  const [thumbUrls, setThumbUrls] = useState<Record<string, string | null>>({});
  const [allImages, setAllImages] = useState<Record<string, string[]>>({});
  const [loadingThumbs, setLoadingThumbs] = useState<Set<string>>(new Set());
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // Load posts from JSON
  useEffect(() => {
    fetch("/data/celebrity-buzz.json")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => {
        if (data?.posts?.length) setPosts(data.posts);
      })
      .catch(() => {});
  }, []);

  // Dynamically fetch thumbnails via API route
  useEffect(() => {
    if (!posts.length) return;

    const fetching = new Set<string>();
    posts.forEach((post) => {
      const shortcode = extractInstaShortcode(post.url);
      if (!shortcode || post.platform !== "instagram") return;
      if (thumbUrls[shortcode] !== undefined) return; // already fetched or fetching

      fetching.add(shortcode);
    });

    if (!fetching.size) return;

    setLoadingThumbs((prev) => new Set([...prev, ...fetching]));

    fetching.forEach((shortcode) => {
      fetch(`/api/instagram-thumb?shortcode=${shortcode}`)
        .then((r) => r.ok ? r.json() : null)
        .then((data) => {
          setThumbUrls((prev) => ({ ...prev, [shortcode]: data?.url || null }));
          if (data?.images?.length) {
            setAllImages((prev) => ({ ...prev, [shortcode]: data.images }));
          }
        })
        .catch(() => {
          setThumbUrls((prev) => ({ ...prev, [shortcode]: null }));
        })
        .finally(() => {
          setLoadingThumbs((prev) => {
            const next = new Set(prev);
            next.delete(shortcode);
            return next;
          });
        });
    });
  }, [posts]); // eslint-disable-line react-hooks/exhaustive-deps

  // Scroll buttons
  const updateScrollButtons = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 10);
  }, []);

  const scrollStrip = useCallback((direction: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const amount = el.clientWidth * 0.75;
    el.scrollBy({ left: direction === "right" ? amount : -amount, behavior: "smooth" });
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateScrollButtons();
    el.addEventListener("scroll", updateScrollButtons, { passive: true });
    window.addEventListener("resize", updateScrollButtons);
    return () => {
      el.removeEventListener("scroll", updateScrollButtons);
      window.removeEventListener("resize", updateScrollButtons);
    };
  }, [posts, updateScrollButtons]);

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
      {/* Shimmer keyframes */}
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .celeb-buzz-strip::-webkit-scrollbar { display: none; }
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
        <div
          ref={scrollRef}
          className="celeb-buzz-strip"
          style={{
            display: "flex",
            gap: 12,
            overflowX: "auto",
            overflowY: "hidden",
            WebkitOverflowScrolling: "touch",
            scrollbarWidth: "none",
            msOverflowStyle: "none",
            scrollSnapType: "x mandatory",
            paddingLeft: "4%",
            paddingRight: "4%",
          } as React.CSSProperties}
        >
          {posts.map((post, i) => {
            const shortcode = extractInstaShortcode(post.url);
            const dynamicSrc = shortcode ? (thumbUrls[shortcode] ?? null) : null;
            const isLoading = shortcode ? loadingThumbs.has(shortcode) : false;

            return (
              <ThumbCard
                key={i}
                post={post}
                dynamicSrc={dynamicSrc}
                loading={isLoading}
                onClick={() => setSelectedIndex(i)}
              />
            );
          })}
        </div>
      </div>

      {selectedIndex !== null && (() => {
        const post = posts[selectedIndex];
        const sc = extractInstaShortcode(post.url);
        const imgs = sc ? (allImages[sc] || []) : [];
        // Fallback to thumbnail if API hasn't returned images yet
        const fallback = sc ? (thumbUrls[sc] || null) : null;
        const hasRealImages = imgs.length > 0 || (fallback && fallback.length > 0);
        const displayImages = imgs.length ? imgs : (fallback ? [fallback] : []);

        // If no real Instagram post images, open profile directly instead of lightbox
        if (!hasRealImages) {
          window.open(post.url, "_blank", "noopener,noreferrer");
          setSelectedIndex(null);
          return null;
        }

        return (
          <BuzzLightbox
            post={post}
            images={displayImages}
            onClose={() => { setSelectedIndex(null); document.body.style.overflow = ""; }}
          />
        );
      })()}
    </section>
  );
}
