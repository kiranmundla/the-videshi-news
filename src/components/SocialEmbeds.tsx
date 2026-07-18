import { useEffect } from "react";
import { Tweet } from "react-tweet";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface SocialEmbed {
  platform: string;
  url: string;
}

interface SocialEmbedsProps {
  embeds: SocialEmbed[];
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

declare global {
  interface Window {
    instgrm?: { Embeds: { process: () => void } };
  }
}

function extractYouTubeId(url: string): string | null {
  try {
    const u = new URL(url);
    if (u.hostname === "youtu.be") {
      return u.pathname.slice(1).split("/")[0] || null;
    }
    if (u.hostname.includes("youtube.com")) {
      if (u.pathname.startsWith("/shorts/")) {
        return u.pathname.split("/shorts/")[1]?.split("/")[0] || null;
      }
      return u.searchParams.get("v") || null;
    }
    return null;
  } catch {
    return null;
  }
}

function extractTweetId(url: string): string | null {
  return url.match(/\/status\/(\d+)/)?.[1] ?? null;
}

/* ------------------------------------------------------------------ */
/*  Individual embed renderers                                         */
/* ------------------------------------------------------------------ */

function TwitterCard({ url }: { url: string }) {
  const tweetId = extractTweetId(url);
  if (!tweetId) return null;
  return (
    <div className="flex justify-center">
      <Tweet id={tweetId} />
    </div>
  );
}

function InstagramCard({ url }: { url: string }) {
  // Extract post ID and use minimal /embed/ URL (no caption, likes, or comments)
  const postId = url.match(/\/(p|reel)\/([A-Za-z0-9_-]+)/)?.[2];
  if (!postId) return null;

  const embedUrl = `https://www.instagram.com/p/${postId}/embed/`;

  return (
    <div className="flex justify-center">
      <iframe
        src={embedUrl}
        style={{ maxWidth: 540, width: "100%", minHeight: 500, border: "none", borderRadius: 8 }}
        allowTransparency
        scrolling="no"
        allowFullScreen
        title="Instagram post"
      />
    </div>
  );
}

function ThreadsCard({ url }: { url: string }) {
  useEffect(() => {
    const existing = document.querySelector('script[src="https://www.threads.com/embed.js"]');
    if (!existing) {
      const script = document.createElement("script");
      script.src = "https://www.threads.com/embed.js";
      script.async = true;
      document.body.appendChild(script);
    } else {
      // Re-process embeds if script already loaded
      setTimeout(() => {
        const iframes = document.querySelectorAll(".threads-post iframe");
        if (iframes.length === 0) {
          const s = document.createElement("script");
          s.src = "https://www.threads.com/embed.js";
          s.async = true;
          document.body.appendChild(s);
        }
      }, 500);
    }
  }, [url]);

  // Normalize to threads.com (not threads.net)
  const normalizedUrl = url.replace("://www.threads.net/", "://www.threads.com/");

  return (
    <div className="flex justify-center threads-post">
      <blockquote
        className="text-post-media"
        data-text-post-permalink={normalizedUrl}
        data-text-post-version="0"
        style={{ maxWidth: 540, width: "100%" }}
      >
        <a href={normalizedUrl}>Loading Threads post…</a>
      </blockquote>
    </div>
  );
}

function YouTubeCard({ url }: { url: string }) {
  const videoId = extractYouTubeId(url);
  if (!videoId) return null;
  return (
    <div className="relative w-full" style={{ paddingBottom: "56.25%" }}>
      <iframe
        className="absolute inset-0 w-full h-full rounded-lg"
        src={`https://www.youtube.com/embed/${videoId}?rel=0`}
        title="YouTube video"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        frameBorder="0"
      />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Platform label (small badge above each embed)                      */
/* ------------------------------------------------------------------ */

const PLATFORM_LABELS: Record<string, string> = {
  twitter: "From X",
  instagram: "From Instagram",
  threads: "From Threads",
  youtube: "Watch",
};

/* ------------------------------------------------------------------ */
/*  Main component                                                     */
/* ------------------------------------------------------------------ */

export default function SocialEmbeds({ embeds }: SocialEmbedsProps) {
  if (!embeds || embeds.length === 0) return null;

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6 my-8">
      {embeds.map((embed, i) => (
        <figure key={`${embed.platform}-${i}`} className="w-full">
          <figcaption className="text-xs text-muted-foreground mb-2 uppercase tracking-wide font-medium">
            {PLATFORM_LABELS[embed.platform] ?? embed.platform}
          </figcaption>
          {embed.platform === "twitter" && <TwitterCard url={embed.url} />}
          {embed.platform === "instagram" && <InstagramCard url={embed.url} />}
          {embed.platform === "threads" && <ThreadsCard url={embed.url} />}
          {embed.platform === "youtube" && <YouTubeCard url={embed.url} />}
        </figure>
      ))}
    </div>
  );
}
