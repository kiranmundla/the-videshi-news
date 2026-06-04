import { useRef } from "react";

export interface SocialPhoto {
  src: string;
  alt?: string;
}

interface SocialPhotoStripProps {
  images: SocialPhoto[];
  via: string;
  platform: "x" | "instagram" | "threads";
  postUrl?: string;
}

const platformLabel: Record<string, string> = {
  x: "𝕏",
  instagram: "Instagram",
  threads: "Threads",
};

export default function SocialPhotoStrip({ images, via, platform, postUrl }: SocialPhotoStripProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  if (!images || images.length === 0) return null;

  const attrText = `${via} on ${platformLabel[platform] || platform}`;
  const singleImage = images.length === 1;

  return (
    <figure className="my-6">
      <style>{`.social-photo-scroll::-webkit-scrollbar { display: none; }`}</style>

      {singleImage ? (
        <div
          style={{
            borderRadius: "10px",
            overflow: "hidden",
            background: "#111",
          }}
        >
          <img
            src={images[0].src}
            alt={images[0].alt || attrText}
            loading="lazy"
            draggable={false}
            style={{
              width: "100%",
              display: "block",
              borderRadius: "10px",
            }}
          />
        </div>
      ) : (
        <div
          ref={scrollRef}
          className="social-photo-scroll"
          style={{
            display: "flex",
            gap: "8px",
            overflowX: "auto",
            overflowY: "hidden",
            WebkitOverflowScrolling: "touch",
            scrollSnapType: "x mandatory",
            scrollbarWidth: "none",
            msOverflowStyle: "none",
          } as React.CSSProperties}
        >
          {images.map((img, i) => (
            <div
              key={i}
              style={{
                minWidth: images.length === 2 ? "calc(50% - 4px)" : "80%",
                flexShrink: 0,
                borderRadius: "10px",
                overflow: "hidden",
                scrollSnapAlign: "start",
                background: "#111",
              }}
            >
              <img
                src={img.src}
                alt={img.alt || `${attrText} photo ${i + 1}`}
                loading={i < 3 ? "eager" : "lazy"}
                draggable={false}
                style={{
                  width: "100%",
                  display: "block",
                  borderRadius: "10px",
                }}
              />
            </div>
          ))}
        </div>
      )}

      {/* Attribution */}
      <figcaption
        style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          marginTop: "8px",
          paddingLeft: "2px",
        }}
      >
        <span style={{ fontSize: "12px", color: "hsl(var(--muted-foreground))", fontFamily: "var(--font-sans, sans-serif)" }}>
          📸{" "}
          {postUrl ? (
            <a
              href={postUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "hsl(var(--muted-foreground))", textDecoration: "underline", textUnderlineOffset: "2px" }}
            >
              {attrText}
            </a>
          ) : (
            attrText
          )}
        </span>
        {!singleImage && images.length <= 8 && (
          <span style={{ display: "flex", gap: "4px", marginLeft: "auto", paddingRight: "2px" }}>
            {images.map((_, i) => (
              <span key={i} style={{
                width: "5px", height: "5px", borderRadius: "50%",
                background: "hsl(var(--muted-foreground))",
                opacity: 0.4,
              }} />
            ))}
          </span>
        )}
      </figcaption>
    </figure>
  );
}

/** Parse a social-photos HTML comment block */
export function parseSocialPhotos(comment: string): {
  images: SocialPhoto[];
  via: string;
  platform: "x" | "instagram" | "threads";
  postUrl?: string;
} | null {
  try {
    const jsonStr = comment.replace(/^<!--\s*social-photos\s*\n?/, "").replace(/\n?\s*-->$/, "").trim();
    const data = JSON.parse(jsonStr);
    if (!data.images || !Array.isArray(data.images) || data.images.length === 0) return null;
    return {
      images: data.images.map((src: string) => ({ src })),
      via: data.via || "Unknown",
      platform: data.platform || "x",
      postUrl: data.post_url,
    };
  } catch {
    return null;
  }
}
