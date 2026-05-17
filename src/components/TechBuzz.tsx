import { useEffect, useRef, useState } from "react";

/* ── Types ── */
interface LatestPost {
  url: string;
  text: string;
  date: string;
  likes: number;
  retweets: number;
}

interface Leader {
  name: string;
  handle: string;
  platform: "x" | "threads";
  role: string;
  avatar: string;
  latestPost?: LatestPost;
  posts: { url: string; text?: string }[];
  category?: "tech" | "world" | "sports" | "india";
}

/* ── Platform icons ── */
function XIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

function ThreadsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.589 12c.027 3.086.718 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.361-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.96-.065-1.17.408-2.266 1.333-3.086.88-.78 2.132-1.228 3.543-1.266 1.003-.027 1.925.088 2.764.338-.02-.729-.145-1.327-.38-1.785-.312-.608-.836-.925-1.64-.995-1.136-.098-2.266.36-2.5.48l-.89-1.773c.346-.174 1.74-.82 3.569-.68 1.263.097 2.2.6 2.782 1.494.472.724.715 1.7.722 2.896v.057c0 .018 0 .036-.002.054.374.203.72.434 1.032.696 1.126.948 1.794 2.27 1.875 3.715.043.767-.09 2.04-.793 3.236-.842 1.434-2.162 2.477-3.924 3.104-1.302.463-2.783.693-4.41.683zm.884-7.69c.078 0 .158-.002.236-.007.969-.052 1.655-.387 2.098-1.026.39-.562.634-1.327.727-2.274-.624-.2-1.318-.306-2.073-.283-.99.027-1.758.298-2.285.808-.454.438-.609.955-.577 1.485.043.717.554 1.297 1.874 1.297z" />
    </svg>
  );
}

/* ── Initials avatar ── */
function InitialsAvatar({ name, bg }: { name: string; bg: string }) {
  const initials = name.split(" ").map((w) => w[0]).join("").slice(0, 2);
  return (
    <div
      style={{
        width: 44, height: 44, borderRadius: "50%",
        background: bg, display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 16, fontWeight: 700, color: "#fff", flexShrink: 0,
      }}
    >
      {initials}
    </div>
  );
}

/* ── Avatar image with fallback ── */
function AvatarImg({ leader, bg }: { leader: Leader; bg: string }) {
  const [failed, setFailed] = useState(false);

  if (!leader.avatar || failed) {
    return <InitialsAvatar name={leader.name} bg={bg} />;
  }

  return (
    <img
      src={leader.avatar}
      alt={leader.name}
      onError={() => setFailed(true)}
      style={{
        width: 44, height: 44, borderRadius: "50%",
        objectFit: "cover", flexShrink: 0,
        border: "2px solid rgba(255,255,255,0.1)",
      }}
    />
  );
}

/* ── Format engagement numbers ── */
function formatCount(n: number): string {
  if (!n) return "";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

/* ── Format relative date ── */
function timeAgo(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffHrs < 1) return "just now";
    if (diffHrs < 24) return `${diffHrs}h`;
    const diffDays = Math.floor(diffHrs / 24);
    if (diffDays < 7) return `${diffDays}d`;
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return "";
  }
}

const COLORS = ["#1DA1F2", "#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

/* ── Main component ── */
export default function TechBuzz({ category = "tech" }: { category?: "tech" | "world" | "sports" | "india" }) {
  const [leaders, setLeaders] = useState<Leader[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load leader data
  useEffect(() => {
    fetch("/data/tech-buzz.json")
      .then((r) => r.json())
      .then((d) => setLeaders((d.leaders || []).filter((l: Leader) => !l.category || l.category === category)))
      .catch(() => {});
  }, []);

  if (!leaders.length) return null;

  return (
    <section className="mt-8 mb-4">
      <div className="flex items-center gap-2 mb-3 px-4 md:px-0">
        <span style={{ fontSize: 18 }}>⚡</span>
        {category === "tech" ? (
          <>
            <h2 className="font-serif text-lg font-bold tracking-tight">Tech Pulse</h2>
            <span className="text-xs text-muted-foreground ml-1">What tech leaders are saying</span>
          </>
        ) : category === "india" ? (
          <>
            <h2 className="font-serif text-lg font-bold tracking-tight">India Pulse</h2>
            <span className="text-xs text-muted-foreground ml-1">What India's leaders are saying</span>
          </>
        ) : category === "sports" ? (
          <>
            <h2 className="font-serif text-lg font-bold tracking-tight">Sports Pulse</h2>
            <span className="text-xs text-muted-foreground ml-1">What sports stars are saying</span>
          </>
        ) : (
          <>
            <h2 className="font-serif text-lg font-bold tracking-tight">Power Pulse</h2>
            <span className="text-xs text-muted-foreground ml-1">What world leaders are saying</span>
          </>
        )}
      </div>

      <style>{`.tech-buzz-scroll::-webkit-scrollbar { display: none; }`}</style>

      <div
        ref={scrollRef}
        className="tech-buzz-scroll flex gap-3 overflow-x-auto px-4 md:px-0 pb-2"
        style={{
          scrollSnapType: "x mandatory",
          scrollBehavior: "smooth",
          msOverflowStyle: "none",
          scrollbarWidth: "none",
        }}
      >
        {leaders.map((leader, i) => {
          const profileUrl = leader.platform === "x"
            ? `https://x.com/${leader.handle}`
            : `https://www.threads.net/@${leader.handle}`;
          const postUrl = leader.latestPost?.url || leader.posts[0]?.url || profileUrl;
          const postText = leader.latestPost?.text || leader.posts[0]?.text || "";
          const hasPost = !!postText;

          return (
            <a
              key={leader.handle}
              href={postUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-shrink-0 no-underline"
              style={{
                width: "min(300px, 80vw)",
                scrollSnapAlign: "start",
              }}
            >
              <div
                style={{
                  background: "#0f0f0f",
                  borderRadius: 14,
                  padding: "16px 16px 14px",
                  height: "100%",
                  minHeight: 160,
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                  border: "1px solid rgba(255,255,255,0.08)",
                  transition: "border-color 0.2s",
                }}
              >
                {/* Header: avatar + name + platform */}
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <AvatarImg leader={leader} bg={COLORS[i % COLORS.length]} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ color: "#fff", fontWeight: 700, fontSize: 14, lineHeight: 1.2 }}>
                      {leader.name}
                    </div>
                    <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                      <span>@{leader.handle}</span>
                      <span style={{ opacity: 0.6 }}>
                        {leader.platform === "x" ? <XIcon /> : <ThreadsIcon />}
                      </span>
                      {leader.latestPost?.date && (
                        <span style={{ marginLeft: 2, opacity: 0.6 }}>
                          · {timeAgo(leader.latestPost.date)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Post text or role */}
                <div style={{
                  color: hasPost ? "rgba(255,255,255,0.85)" : "rgba(255,255,255,0.4)",
                  fontSize: 13,
                  lineHeight: 1.5,
                  flex: 1,
                  overflow: "hidden",
                  display: "-webkit-box",
                  WebkitLineClamp: 8,
                  WebkitBoxOrient: "vertical",
                }}>
                  {hasPost ? postText : leader.role}
                </div>

                {/* Footer: engagement + link */}
                <div style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  fontSize: 12,
                }}>
                  {/* Engagement counts */}
                  {leader.latestPost && (leader.latestPost.likes > 0 || leader.latestPost.retweets > 0) ? (
                    <div style={{ display: "flex", gap: 10, color: "rgba(255,255,255,0.35)" }}>
                      {leader.latestPost.retweets > 0 && (
                        <span>🔁 {formatCount(leader.latestPost.retweets)}</span>
                      )}
                      {leader.latestPost.likes > 0 && (
                        <span>❤️ {formatCount(leader.latestPost.likes)}</span>
                      )}
                    </div>
                  ) : <div />}

                  <div style={{
                    color: leader.platform === "x" ? "#1DA1F2" : "#000",
                    fontWeight: 600,
                    display: "flex", alignItems: "center", gap: 4,
                  }}>
                    {leader.platform === "x" ? <XIcon /> : <ThreadsIcon />}
                    <span style={{ color: "rgba(255,255,255,0.35)" }}>
                      View on {leader.platform === "x" ? "X" : "Threads"}
                    </span>
                  </div>
                </div>
              </div>
            </a>
          );
        })}
      </div>
    </section>
  );
}
