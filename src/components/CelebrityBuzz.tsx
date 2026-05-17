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

/* ── Twitter widgets loader (shared with SocialEmbed) ── */
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

/* ── Individual embed cards ── */

function InstaCard({ post }: { post: BuzzPost }) {
  const shortcode = extractInstaShortcode(post.url);
  if (!shortcode) return null;

  return (
    <div style={{
      width: 300, flexShrink: 0, borderRadius: 6, overflow: "hidden",
      background: "#111", scrollSnapAlign: "start",
    }}>
      <div style={{
        padding: "8px 12px", display: "flex", alignItems: "center", gap: 6,
        borderBottom: "1px solid #222",
      }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: "#fff" }}>{post.celebrity}</span>
        <span style={{ fontSize: 11, color: "#888" }}>@{post.handle}</span>
      </div>
      <iframe
        src={`https://www.instagram.com/p/${shortcode}/embed/`}
        width="300"
        height="380"
        frameBorder="0"
        scrolling="no"
        loading="lazy"
        allowTransparency
        title={`${post.celebrity} Instagram post`}
        style={{ display: "block", border: "none", background: "#000" }}
      />
    </div>
  );
}

function TweetCard({ post }: { post: BuzzPost }) {
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
    <div style={{
      width: 300, flexShrink: 0, borderRadius: 6, overflow: "hidden",
      background: "#111", scrollSnapAlign: "start",
    }}>
      <div style={{
        padding: "8px 12px", display: "flex", alignItems: "center", gap: 6,
        borderBottom: "1px solid #222",
      }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: "#fff" }}>{post.celebrity}</span>
        <span style={{ fontSize: 11, color: "#888" }}>@{post.handle}</span>
      </div>
      <div ref={ref} style={{ padding: 8, maxHeight: 400, overflow: "hidden" }}>
        <blockquote className="twitter-tweet" data-dnt="true" data-theme="dark">
          <a href={tweetUrl}>{tweetUrl}</a>
        </blockquote>
      </div>
    </div>
  );
}

/* ── Main strip component ── */

export default function CelebrityBuzz() {
  const [posts, setPosts] = useState<BuzzPost[]>([]);
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

  const updateArrows = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 10);
  }, []);

  const scrollStrip = useCallback((dir: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollBy({ left: dir === "right" ? 310 : -310, behavior: "smooth" });
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
    background: "rgba(255,255,255,0.15)", backdropFilter: "blur(4px)", border: "none",
    color: "#fff", fontSize: 20, width: 40, height: 40, borderRadius: "50%",
    cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
    transition: "background 0.2s",
  };

  return (
    <section className="mt-14 mb-8">
      <div
        className="flex items-center gap-4 mb-6 pb-3"
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
        <style>{`.celeb-buzz-scroll::-webkit-scrollbar { display: none; }`}</style>

        {canScrollLeft && (
          <button
            onClick={() => scrollStrip("left")}
            aria-label="Scroll left"
            style={{ ...arrowStyle, left: 4 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.3)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.15)"; }}
          >‹</button>
        )}
        {canScrollRight && (
          <button
            onClick={() => scrollStrip("right")}
            aria-label="Scroll right"
            style={{ ...arrowStyle, right: 4 }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.3)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.15)"; }}
          >›</button>
        )}

        <div
          ref={scrollRef}
          className="celeb-buzz-scroll"
          style={{
            display: "flex", gap: 8, overflowX: "auto", overflowY: "hidden",
            WebkitOverflowScrolling: "touch", scrollbarWidth: "none",
            msOverflowStyle: "none", scrollSnapType: "x mandatory",
            paddingLeft: "4%", paddingRight: "4%", paddingBottom: 8,
          } as React.CSSProperties}
        >
          {posts.map((post, i) => (
            post.platform === "instagram"
              ? <InstaCard key={i} post={post} />
              : <TweetCard key={i} post={post} />
          ))}
        </div>
      </div>
    </section>
  );
}
