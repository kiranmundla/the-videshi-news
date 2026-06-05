import { useEffect, useRef } from "react";

interface XOfficialEmbedProps {
  url: string;
  /** When true, adds data-media-max-width="560" for video-optimized embed */
  video?: boolean;
  caption?: string;
}

declare global {
  interface Window {
    twttr?: {
      widgets: {
        load: (el?: HTMLElement) => void;
      };
    };
  }
}

/** Loads the official X widgets.js script once */
function ensureWidgetsScript(): Promise<void> {
  if (window.twttr) return Promise.resolve();
  return new Promise((resolve) => {
    const existing = document.getElementById("twitter-wjs");
    if (existing) {
      // Script tag exists but hasn't loaded yet
      existing.addEventListener("load", () => resolve());
      return;
    }
    const script = document.createElement("script");
    script.id = "twitter-wjs";
    script.src = "https://platform.x.com/widgets.js";
    script.async = true;
    script.onload = () => resolve();
    document.head.appendChild(script);
  });
}

export default function XOfficialEmbed({ url, video, caption }: XOfficialEmbedProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ensureWidgetsScript().then(() => {
      if (containerRef.current && window.twttr) {
        window.twttr.widgets.load(containerRef.current);
      }
    });
  }, [url]);

  return (
    <figure className="my-6 flex flex-col items-center x-official-embed">
      <div
        ref={containerRef}
        className="w-full"
        style={{ maxWidth: 550 }}
      >
        <blockquote
          className="twitter-tweet"
          {...(video ? { "data-media-max-width": "560" } : {})}
        >
          <a href={url}>{url}</a>
        </blockquote>
      </div>
      {caption && (
        <figcaption className="mt-2 text-sm text-muted-foreground text-center">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}
