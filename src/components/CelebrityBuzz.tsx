import { useState, useEffect, useCallback, useRef } from "react";

interface BuzzPost {
  platform: "instagram" | "twitter";
  url: string;
  celebrity: string;
  handle: string;
  timestamp: string;
  thumbnail?: string;
  cdn_thumbnail?: string;
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

function BuzzLightbox({ posts, index, getImageSrc, onClose, onNav }: {
  posts: BuzzPost[];
  index: number;
  getImageSrc: (i: number) => string;
  onClose: () => void;
  onNav: (i: number) => void;
}) {
  const touchStartX = useRef<number | null>(null);
  const post = posts[index];
  const imageSrc = getImageSrc(index);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") onNav((index + 1) % posts.length);
      if (e.key === "ArrowLeft") onNav((index - 1 + posts.length) % posts.length);
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose, onNav, index, posts.length]);

  return (
    <div
      onClick={onClose}
      onTouchStart={(e) => { touchStartX.current = e.touches[0].clientX; }}
      onTouchEnd={(e) => {
        if (touchStartX.current === null) return;
        const diff = e.changedTouches[0].clientX - touchStartX.current;
        if (Math.abs(diff) > 50) {
          diff < 0 ? onNav((index + 1) % posts.length) : onNav((index - 1 + posts.length) % posts.length);
        }
        touchStartX.current = null;
      }}
      style={{
        position: "fixed", inset: 0, zIndex: 9999,
        background: "rgba(0,0,0,0.95)",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        animation: "buzzFadeIn 0.15s ease-out",
      }}
    >
      <style>{`@keyframes buzzFadeIn { from { opacity: 0; } to { opacity: 1; } }`}</style>

      <button
        onClick={onClose}
        style={{
          position: "absolute", top: 12, right: 12, zIndex: 20,
          background: "rgba(255,255,255,0.15)", border: "none", color: "#fff",
          width: 36, height: 36, borderRadius: "50%", cursor: "pointer",
          fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center",
        }}
      >×</button>

      {/* Counter */}
      <div style={{ position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)", color: "rgba(255,255,255,0.5)", fontSize: 13, fontWeight: 500 }}>
        {index + 1} / {posts.length}
      </div>

      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          display: "flex", flexDirection: "column", alignItems: "center",
          maxWidth: "90vw", maxHeight: "85vh",
        }}
      >
        <img
          key={index}
          src={imageSrc}
          alt={post.celebrity}
          referrerPolicy="no-referrer"
          style={{
            maxWidth: "90vw", maxHeight: "70vh",
            borderRadius: 10, objectFit: "contain", display: "block",
          }}
        />

        <div style={{ marginTop: 12, textAlign: "center" }}>
          <div style={{ color: "#fff", fontSize: 16, fontWeight: 600 }}>
            {post.celebrity}
          </div>
          <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 13, marginTop: 2 }}>
            @{post.handle}
          </div>
        </div>

        <a
          href={post.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          style={{
            marginTop: 12, padding: "10px 24px", borderRadius: 20,
            background: "linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)",
            color: "#fff", fontSize: 14, fontWeight: 600,
            textDecoration: "none",
          }}
        >
          View on Instagram →
        </a>
      </div>
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
  const fallbackSrc = post.thumbnail || `/images/celebrity-thumbs/${post.handle}.jpg`;
  const src = dynamicSrc || fallbackSrc;

  return (
    <div
      onClick={onClick}
      style={{
        width: 160,
        flexShrink: 0,
        cursor: "pointer",
        scrollSnapAlign: "center",
      }}
    >
      {/* Image container */}
      <div style={{
        position: "relative",
        width: 160,
        height: 160,
        borderRadius: 12,
        overflow: "hidden",
        background: "#1a1a1a",
        boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
      }}>
        {/* Shimmer placeholder while loading */}
        {loading && (
          <div style={{
            position: "absolute", inset: 0, zIndex: 2,
            background: "linear-gradient(110deg, #1a1a1a 30%, #2a2a2a 50%, #1a1a1a 70%)",
            backgroundSize: "200% 100%",
            animation: "shimmer 1.5s ease-in-out infinite",
          }} />
        )}

        <img
          src={src}
          alt={post.celebrity}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={(e) => {
            const img = e.currentTarget;
            if (img.src !== window.location.origin + fallbackSrc && img.src !== fallbackSrc) {
              img.src = fallbackSrc;
            }
          }}
          style={{
            width: "100%", height: "100%",
            objectFit: "cover", display: "block",
            opacity: loading ? 0 : 1,
            transition: "opacity 0.3s ease",
          }}
        />

        {/* Instagram badge */}
        <div style={{
          position: "absolute", top: 6, right: 6,
          width: 22, height: 22, borderRadius: 6,
          background: "linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
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
          {post.celebrity}
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
        const getImgSrc = (i: number) => {
          const p = posts[i];
          const sc = extractInstaShortcode(p.url);
          return (sc ? thumbUrls[sc] : null) || p.thumbnail || `/images/celebrity-thumbs/${p.handle}.jpg`;
        };
        return (
          <BuzzLightbox
            posts={posts}
            index={selectedIndex}
            getImageSrc={getImgSrc}
            onClose={() => { setSelectedIndex(null); document.body.style.overflow = ""; }}
            onNav={(i) => setSelectedIndex(i)}
          />
        );
      })()}
    </section>
  );
}
