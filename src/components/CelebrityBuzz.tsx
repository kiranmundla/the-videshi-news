import { useState, useEffect, useCallback, useRef } from "react";

interface BuzzPost {
  platform: "instagram" | "twitter";
  url: string;
  celebrity: string;
  handle: string;
  timestamp: string;
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

/* ── Compact strip card (thumbnail) ── */

function InstaThumb({ post, onClick }: { post: BuzzPost; onClick: () => void }) {
  const shortcode = extractInstaShortcode(post.url);
  if (!shortcode) return null;

  return (
    <div
      onClick={onClick}
      style={{
        width: 280, flexShrink: 0, overflow: "hidden",
        background: "#000", scrollSnapAlign: "center",
        cursor: "pointer", maxHeight: 380,
      }}
    >
      <iframe
        src={`https://www.instagram.com/p/${shortcode}/embed/`}
        width="280"
        height="500"
        frameBorder="0"
        scrolling="no"
        loading="lazy"
        allowTransparency
        title={`${post.celebrity} Instagram post`}
        style={{ display: "block", border: "none", background: "#000", pointerEvents: "none", marginBottom: -60 }}
      />
    </div>
  );
}

function TweetThumb({ post, onClick }: { post: BuzzPost; onClick: () => void }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ensureTwitterWidgets(() => {
      if (ref.current) window.twttr?.widgets.load(ref.current);
    });
  }, [post.url]);

  const tweetUrl = post.url
    .replace(/^https?:\/\/(mobile\.)?twitter\.com/, "https://x.com")
    .split("?")[0];

  return (
    <div
      onClick={onClick}
      style={{
        width: 280, flexShrink: 0, overflow: "hidden",
        background: "#000", scrollSnapAlign: "center",
        cursor: "pointer",
      }}
    >
      <div ref={ref} style={{ padding: 8, maxHeight: 360, overflow: "hidden", pointerEvents: "none" }}>
        <blockquote className="twitter-tweet" data-dnt="true" data-theme="dark">
          <a href={tweetUrl}>{tweetUrl}</a>
        </blockquote>
      </div>
    </div>
  );
}

/* ── Lightbox modal ── */

function LightboxSlide({ post }: { post: BuzzPost }) {
  const shortcode = post.platform === "instagram" ? extractInstaShortcode(post.url) : null;
  const tweetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (post.platform === "twitter") {
      ensureTwitterWidgets(() => {
        if (tweetRef.current) window.twttr?.widgets.load(tweetRef.current);
      });
    }
  }, [post]);

  const tweetUrl = post.url
    .replace(/^https?:\/\/(mobile\.)?twitter\.com/, "https://x.com")
    .split("?")[0];

  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    }}>
      <div style={{
        width: "min(90vw, 480px)", maxHeight: "85vh",
        borderRadius: 12, overflow: "hidden", background: "#000",
      }}>
        {post.platform === "instagram" && shortcode ? (
          <div style={{ overflow: "hidden", maxHeight: "calc(85vh - 50px)" }}>
            <iframe
              src={`https://www.instagram.com/p/${shortcode}/embed/captioned/`}
              width="100%"
              height="800"
              frameBorder="0"
              scrolling="no"
              allowTransparency
              title={`${post.celebrity} Instagram post`}
              style={{ display: "block", border: "none", background: "#000", marginBottom: -80 }}
            />
          </div>
        ) : (
          <div ref={tweetRef} style={{ padding: 16, maxHeight: "70vh", overflow: "auto" }}>
            <blockquote className="twitter-tweet" data-dnt="true" data-theme="dark">
              <a href={tweetUrl}>{tweetUrl}</a>
            </blockquote>
          </div>
        )}
        <a
          href={post.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "block", textAlign: "center", padding: "12px 16px",
            color: "#3897f0", fontSize: 14, fontWeight: 600,
            textDecoration: "none", borderTop: "1px solid #222",
          }}
        >
          View on {post.platform === "instagram" ? "Instagram" : "X"} →
        </a>
      </div>
    </div>
  );
}

function BuzzLightbox({ posts, startIndex, onClose }: { posts: BuzzPost[]; startIndex: number; onClose: () => void }) {
  const [current, setCurrent] = useState(startIndex);
  const count = posts.length;

  const goNext = useCallback(() => setCurrent((i) => Math.min(i + 1, count - 1)), [count]);
  const goPrev = useCallback(() => setCurrent((i) => Math.max(i - 1, 0)), []);

  // Escape to close, arrow keys to navigate
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") goNext();
      if (e.key === "ArrowLeft") goPrev();
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose, goNext, goPrev]);

  const post = posts[current];

  const arrowStyle: React.CSSProperties = {
    position: "absolute", top: "50%", transform: "translateY(-50%)", zIndex: 20,
    background: "rgba(255,255,255,0.2)", backdropFilter: "blur(4px)", border: "none",
    color: "#fff", fontSize: 24, width: 44, height: 44, borderRadius: "50%",
    cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
    transition: "background 0.2s",
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed", inset: 0, zIndex: 9999,
        background: "rgba(0,0,0,0.9)", backdropFilter: "blur(8px)",
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
        zIndex: 20, color: "#fff", fontSize: 14, fontWeight: 600,
        textAlign: "center", opacity: 0.9,
      }}>
        {post.celebrity}
      </div>

      {/* Prev arrow */}
      {current > 0 && (
        <button
          onClick={(e) => { e.stopPropagation(); goPrev(); }}
          style={{ ...arrowStyle, left: 8 }}
          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.35)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.2)"; }}
        >‹</button>
      )}

      {/* Next arrow */}
      {current < count - 1 && (
        <button
          onClick={(e) => { e.stopPropagation(); goNext(); }}
          style={{ ...arrowStyle, right: 8 }}
          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.35)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.2)"; }}
        >›</button>
      )}

      {/* Dot indicators */}
      <div style={{
        position: "absolute", bottom: 16, left: "50%", transform: "translateX(-50%)",
        zIndex: 20, display: "flex", gap: 6,
      }}>
        {posts.map((_, i) => (
          <button
            key={i}
            onClick={(e) => { e.stopPropagation(); setCurrent(i); }}
            style={{
              width: 7, height: 7, borderRadius: "50%", border: "none", padding: 0,
              background: i === current ? "#fff" : "rgba(255,255,255,0.3)",
              transition: "background 0.2s", cursor: "pointer",
            }}
          />
        ))}
      </div>

      {/* Current post */}
      <div onClick={(e) => e.stopPropagation()}>
        <LightboxSlide post={post} />
      </div>
    </div>
  );
}

/* ── Main strip ── */

export default function CelebrityBuzz() {
  const [posts, setPosts] = useState<BuzzPost[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  useEffect(() => {
    fetch("/data/celebrity-buzz.json")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => {
        if (data?.posts?.length) setPosts(data.posts);
      })
      .catch(() => {});
  }, []);

  const updateArrows = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 10);
  }, []);

  const scrollStrip = useCallback((dir: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollBy({ left: dir === "right" ? el.clientWidth * 0.75 : -el.clientWidth * 0.75, behavior: "smooth" });
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateArrows();
    el.addEventListener("scroll", updateArrows, { passive: true });
    window.addEventListener("resize", updateArrows);
    return () => {
      el.removeEventListener("scroll", updateArrows);
      window.removeEventListener("resize", updateArrows);
    };
  }, [posts, updateArrows]);

  if (!posts.length) return null;

  const arrowStyle: React.CSSProperties = {
    position: "absolute", top: "50%", transform: "translateY(-50%)", zIndex: 10,
    background: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)", border: "none",
    color: "#fff", fontSize: 20, width: 36, height: 36, borderRadius: "50%",
    cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
    transition: "background 0.2s",
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

      <div style={{ position: "relative", borderRadius: 8, overflow: "hidden" }}>
        <style>{`.celeb-buzz-scroll::-webkit-scrollbar { display: none; }`}</style>

        {canScrollLeft && (
          <button
            onClick={() => scrollStrip("left")}
            aria-label="Scroll left"
            style={{ ...arrowStyle, left: 6 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.75)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.5)"; }}
          >‹</button>
        )}
        {canScrollRight && (
          <button
            onClick={() => scrollStrip("right")}
            aria-label="Scroll right"
            style={{ ...arrowStyle, right: 6 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.75)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.5)"; }}
          >›</button>
        )}

        <div
          ref={scrollRef}
          className="celeb-buzz-scroll"
          style={{
            display: "flex", gap: 2, overflowX: "auto", overflowY: "hidden",
            WebkitOverflowScrolling: "touch", scrollbarWidth: "none",
            msOverflowStyle: "none", scrollSnapType: "x mandatory",
          } as React.CSSProperties}
        >
          {posts.map((post, i) => (
            post.platform === "instagram"
              ? <InstaThumb key={i} post={post} onClick={() => setSelectedIndex(i)} />
              : <TweetThumb key={i} post={post} onClick={() => setSelectedIndex(i)} />
          ))}
        </div>
      </div>

      {/* Lightbox */}
      {selectedIndex !== null && (
        <BuzzLightbox posts={posts} startIndex={selectedIndex} onClose={() => setSelectedIndex(null)} />
      )}
    </section>
  );
}
