import { useEffect } from "react";
import { Tweet } from "react-tweet";
import HeroImage from "@/components/HeroImage";
import ImageCaption from "@/components/ImageCaption";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface HeroMediaProps {
  url: string;
  alt: string;
  credit: string | null;
  caption: string | null;
  category: string;
}

type EmbedType = "twitter" | "instagram" | "youtube" | null;

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

declare global {
  interface Window {

    instgrm?: { Embeds: { process: () => void } };
  }
}

function detectEmbed(credit: string | null): EmbedType {
  if (!credit) return null;
  if (credit.startsWith("embed:twitter")) return "twitter";
  if (credit.startsWith("embed:instagram")) return "instagram";
  if (credit.startsWith("embed:youtube")) return "youtube";
  return null;
}

/** Parse "embed:platform | attribution" → attribution text, or null. */
function parseAttribution(credit: string | null, platform: EmbedType): string | null {
  if (!credit || !platform) return null;
  const parts = credit.split("|");
  if (parts.length < 2) return null;
  const raw = parts.slice(1).join("|").trim();
  return raw || null;
}

function formatAttribution(raw: string | null, platform: EmbedType): string | null {
  if (!raw || !platform) return null;
  switch (platform) {
    case "twitter":
      return `Via ${raw} on X`;
    case "instagram":
      return `Via ${raw} on Instagram`;
    case "youtube":
      return `Via ${raw} on YouTube`;
    default:
      return null;
  }
}

function extractYouTubeId(url: string): string | null {
  // https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID
  try {
    const u = new URL(url);
    if (u.hostname === "youtu.be") {
      return u.pathname.slice(1).split("/")[0] || null;
    }
    return u.searchParams.get("v") || null;
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------------ */
/*  Sub-components for each embed type                                 */
/* ------------------------------------------------------------------ */

function TwitterEmbed({ url, attribution }: { url: string; attribution: string | null }) {
  const tweetId = url.match(/\/status\/(\d+)/)?.[1];
  if (!tweetId) return null;

  return (
    <figure className="mt-10 w-full max-w-full md:max-w-[780px] md:mx-auto">
      <div className="flex justify-center">
        <Tweet id={tweetId} />
      </div>
      {attribution && (
        <p
          className="mt-2 text-right italic"
          style={{ fontSize: "11px", color: "#888" }}
        >
          {attribution}
        </p>
      )}
    </figure>
  );
}

function InstagramEmbed({ url, attribution }: { url: string; attribution: string | null }) {
  useEffect(() => {
    if (window.instgrm) {
      window.instgrm.Embeds.process();
      return;
    }
    const existing = document.querySelector(
      'script[src="https://www.instagram.com/embed.js"]'
    );
    if (!existing) {
      const script = document.createElement("script");
      script.src = "https://www.instagram.com/embed.js";
      script.async = true;
      document.body.appendChild(script);
    }
  }, [url]);

  return (
    <figure className="mt-10 w-full max-w-full md:max-w-[780px] md:mx-auto">
      <div className="flex justify-center">
        <blockquote
          className="instagram-media"
          data-instgrm-permalink={url}
          data-instgrm-version="14"
          style={{ maxWidth: 540, width: "100%" }}
        >
          <a href={url}>Loading Instagram post…</a>
        </blockquote>
      </div>
      {attribution && (
        <p
          className="mt-2 text-right italic"
          style={{ fontSize: "11px", color: "#888" }}
        >
          {attribution}
        </p>
      )}
    </figure>
  );
}

function YouTubeEmbed({
  url,
  alt,
  attribution,
}: {
  url: string;
  alt: string;
  attribution: string | null;
}) {
  const videoId = extractYouTubeId(url);
  if (!videoId) return null;

  return (
    <figure className="mt-10 w-full max-w-full md:max-w-[780px] md:mx-auto">
      <div className="relative w-full" style={{ paddingBottom: "56.25%" }}>
        <iframe
          className="absolute inset-0 w-full h-full rounded-lg"
          src={`https://www.youtube.com/embed/${videoId}`}
          title={alt}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          frameBorder="0"
        />
      </div>
      {attribution && (
        <p
          className="mt-2 text-right italic"
          style={{ fontSize: "11px", color: "#888" }}
        >
          {attribution}
        </p>
      )}
    </figure>
  );
}

/* ------------------------------------------------------------------ */
/*  Main component                                                     */
/* ------------------------------------------------------------------ */

export default function HeroMedia({ url, alt, credit, caption, category }: HeroMediaProps) {
  const embedType = detectEmbed(credit);
  const rawAttribution = parseAttribution(credit, embedType);
  const attribution = formatAttribution(rawAttribution, embedType);

  if (embedType === "twitter") {
    return <TwitterEmbed url={url} attribution={attribution} />;
  }

  if (embedType === "instagram") {
    return <InstagramEmbed url={url} attribution={attribution} />;
  }

  if (embedType === "youtube") {
    return <YouTubeEmbed url={url} alt={alt} attribution={attribution} />;
  }

  // Regular image (fallback) — preserves existing rendering exactly
  return (
    <figure className="mt-10 w-full max-w-full md:max-w-[780px] md:mx-auto">
      <div className="w-full max-w-full relative bg-stone-100">
        <HeroImage
          src={url}
          alt={alt}
          loading="eager"
          category={category}
          className="block w-full h-auto max-h-[80vh] object-contain"
          style={{}}
        />
      </div>
      <div className="text-center">
        <ImageCaption caption={caption} credit={null} size="md" align="center" />
      </div>
      {credit && (
        <p
          className="mt-2 text-right italic"
          style={{ fontSize: "11px", color: "#888" }}
        >
          Photo: {credit}
        </p>
      )}
    </figure>
  );
}
