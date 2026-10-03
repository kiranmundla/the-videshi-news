import { useState, useEffect } from "react";

/* ── Star Buzz strip ──────────────────────────────
   Celebrity social posts from /data/star-buzz.json
   (prebuilt from the X embed cache). Renders nothing
   when empty. */

interface BuzzPost {
  id: string;
  handle: string;
  text: string;
  photo: string | null;
  has_video: boolean;
  url: string;
  likes: number;
  views: number;
  created_at: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return `${n}`;
}

export default function StarBuzzStrip() {
  const [posts, setPosts] = useState<BuzzPost[]>([]);

  useEffect(() => {
    fetch("/data/star-buzz.json")
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then((d) => {
        if (d?.posts?.length) setPosts(d.posts.slice(0, 10));
      })
      .catch(() => {});
  }, []);

  if (posts.length === 0) return null;

  return (
    <section className="mb-14">
      <div className="container">
        <div
          className="flex items-center mb-5 pb-2.5"
          style={{ borderBottom: "3px solid #D4A843" }}
        >
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            Star Buzz
          </h2>
          <span className="ml-3 text-[11px] text-foreground/50">
            What the stars are posting
          </span>
        </div>
        <div className="flex gap-5 overflow-x-auto pb-2 -mx-1 px-1">
          {posts.map((p) => (
            <a
              key={p.id}
              href={p.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group shrink-0 w-60 md:w-64 rounded-xl border border-rule overflow-hidden bg-card hover:shadow-lg transition-shadow"
            >
              {p.photo && (
                <div className="relative w-full aspect-[4/3] overflow-hidden bg-muted">
                  <img
                    src={p.photo}
                    alt=""
                    loading="lazy"
                    className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
                  />
                  {p.has_video && (
                    <span className="absolute bottom-2 right-2 text-[10px] font-bold uppercase tracking-wide text-white bg-black/60 rounded px-2 py-0.5">
                      Video
                    </span>
                  )}
                </div>
              )}
              <div className="p-3.5">
                <div className="flex items-center gap-1.5 text-[11px] text-foreground/50 mb-1.5">
                  <span className="font-bold text-foreground/80">@{p.handle}</span>
                  <span>·</span>
                  <span>{timeAgo(p.created_at)}</span>
                </div>
                <p className="text-[0.85rem] leading-snug line-clamp-3 text-foreground/90">
                  {p.text}
                </p>
                <div className="flex items-center gap-4 mt-2.5 text-[11px] text-foreground/45">
                  <span>♥ {formatCount(p.likes)}</span>
                  {p.views > 0 && <span>👁 {formatCount(p.views)}</span>}
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
