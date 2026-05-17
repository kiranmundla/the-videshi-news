import { useState, useEffect, useCallback, useRef } from "react";

interface BuzzPost {
  platform: "instagram" | "twitter";
  url: string;
  celebrity: string;
  handle: string;
  timestamp: string;
  thumbnail?: string;
  cdn_thumbnail?: string;
  thumbnail_url?: string;
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

function BuzzLightbox({ post, onClose }: {
  post: BuzzPost;
  onClose: () => void;
}) {
  const tweetRef = useRef<HTMLDivElement>(null);

  // Escape to close
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  // Load Twitter widgets when showing a tweet
  useEffect(() => {
    if (post.platform === "twitter") {
      ensureTwitterWidgets(() => {
        if (tweetRef.current) window.twttr?.widgets.load(tweetRef.current);
      });
    }
  }, [post]);

  const shortcode = post.platform === "instagram" ? extractInstaShortcode(post.url) : null;
  const tweetUrl = post.url
    .replace(/^https?:\/\/(mobile\.)?twitter\.com/, "https://x.com")
    .split("?")[0];

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed", inset: 0, zIndex: 9999,
        background: "rgba(0,0,0,0.92)", backdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}
    >
      {/* Close button */}
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
      <div style={{
        position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)",
        zIndex: 20, color: "#fff", fontSize: 14, fontWeight: 600, opacity: 0.9,
      }}>
        {post.celebrity}
      </div>

      {/* Embed card */}
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(90vw, 480px)", maxHeight: "80vh",
          borderRadius: 12, overflow: "hidden", background: "#000",
          position: "relative",
        }}
      >
        {post.platform === "instagram" && shortcode ? (
          <div style={{ position: "relative", overflow: "hidden", maxHeight: "calc(80vh - 50px)" }}>
            <iframe
              src={`https://www.instagram.com/p/${shortcode}/embed/`}
              width="100%"
              height="800"
              frameBorder="0"
              scrolling="no"
              allowTransparency
              title={`${post.celebrity} Instagram post`}
              style={{ display: "block", border: "none", background: "#000", marginBottom: -80 }}
            />
            {/* Interaction blocker — prevents all taps going to Instagram */}
            <div style={{
              position: "absolute", inset: 0, zIndex: 5,
              cursor: "default",
            }} />
          </div>
        ) : (
          <div style={{ position: "relative" }}>
            <div ref={tweetRef} style={{ padding: 16, maxHeight: "70vh", overflow: "auto" }}>
              <blockquote className="twitter-tweet" data-dnt="true" data-theme="dark">
                <a href={tweetUrl}>{tweetUrl}</a>
              </blockquote>
            </div>
            {/* Interaction blocker */}
            <div style={{
              position: "absolute", inset: 0, zIndex: 5,
              cursor: "default",
            }} />
          </div>
        )}

        {/* Our controlled link — only way to reach Instagram */}
        <a
          href={post.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "block", textAlign: "center", padding: "12px 16px",
            color: "#3897f0", fontSize: 14, fontWeight: 600,
            textDecoration: "none", borderTop: "1px solid #222",
            position: "relative", zIndex: 10,
          }}
        >
          View on {post.platform === "instagram" ? "Instagram" : "X"} →
        </a>
      </div>
    </div>
  );
}

/* ── Main component — Photo scroll strip ── */

export default function CelebrityBuzz() {
  const [posts, setPosts] = useState<BuzzPost[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  useEffect(() => {
    fetch("/data/celebrity-buzz.json")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => {
        if (data?.posts?.length) setPosts(data.posts);
      })
      .catch(() => {});
  }, []);

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
        <style>{`.celeb-buzz-strip::-webkit-scrollbar { display: none; }`}</style>

        {canScrollLeft && (
          <button
            onClick={() => scrollStrip("left")}
            aria-label="Scroll left"
            style={{ ...arrowStyle, left: 4 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.85)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.6)"; }}
          >‹</button>
        )}

        {canScrollRight && (
          <button
            onClick={() => scrollStrip("right")}
            aria-label="Scroll right"
            style={{ ...arrowStyle, right: 4 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.85)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.6)"; }}
          >›</button>
        )}

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
            const fallbackSrc = post.thumbnail || `/images/celebrity-thumbs/${post.handle}.jpg`;
            return (
              <div
                key={i}
                onClick={() => setSelectedIndex(i)}
                style={{
                  position: "relative",
                  width: 220,
                  height: 280,
                  borderRadius: 10,
                  overflow: "hidden",
                  flexShrink: 0,
                  background: "#1a1a1a",
                  cursor: "pointer",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
                  scrollSnapAlign: "center",
                }}
              >
                <img
                  src={post.cdn_thumbnail || fallbackSrc}
                  alt={post.celebrity}
                  loading="lazy"
                  referrerPolicy="no-referrer"
                  crossOrigin="anonymous"
                  onError={(e) => {
                    const img = e.currentTarget;
                    if (img.src !== fallbackSrc) {
                      img.src = fallbackSrc;
                    }
                  }}
                  style={{
                    width: "100%", height: "100%",
                    objectFit: "cover", display: "block",
                  }}
                />
                <div style={{
                  position: "absolute", bottom: 0, left: 0, right: 0,
                  padding: "28px 12px 10px",
                  background: "linear-gradient(transparent, rgba(0,0,0,0.75))",
                }}>
                  <div style={{
                    color: "#fff", fontSize: 13, fontWeight: 600,
                    textShadow: "0 1px 3px rgba(0,0,0,0.5)",
                  }}>
                    {post.celebrity}
                  </div>
                  <div style={{
                    color: "rgba(255,255,255,0.7)", fontSize: 11, marginTop: 2,
                  }}>
                    @{post.handle}
                  </div>
                </div>
                {/* Instagram icon badge */}
                <div style={{
                  position: "absolute", top: 8, right: 8,
                  width: 24, height: 24, borderRadius: 6,
                  background: "linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
                }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="2" width="20" height="20" rx="5" />
                    <circle cx="12" cy="12" r="5" />
                    <circle cx="17.5" cy="6.5" r="1.5" fill="white" stroke="none" />
                  </svg>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Lightbox */}
      {selectedIndex !== null && (
        <BuzzLightbox
          post={posts[selectedIndex]}
          onClose={() => setSelectedIndex(null)}
        />
      )}
    </section>
  );
}
