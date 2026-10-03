import { useState, useCallback } from "react";

type Props = {
  src?: string | null;
  alt: string;
  className?: string;
  loading?: "eager" | "lazy";
  fetchPriority?: "high" | "low" | "auto";
  category?: string;
  style?: React.CSSProperties;
  width?: number | string;
  height?: number | string;
  focalX?: number | null;
  focalY?: number | null;
  onOrientationDetected?: (orientation: "landscape" | "portrait") => void;
  zoomable?: boolean;
};

export function isValidImage(src?: string | null): boolean {
  if (!src || typeof src !== "string") return false;
  if (src.trim().length === 0) return false;
  if (/hindustantimes\.com|htmedia/i.test(src)) return false;
  if (src.toLowerCase().endsWith(".svg")) return false;
  if (/Flag_of_|flag_of_|_flag\.|national.flag/i.test(src)) return false;
  if (src.includes("Flag_of_Canada")) return false;
  if (/(?:^|[/\-_.])(?:logo|icon|avatar|placeholder|default)(?:[/\-_.\s]|$)|thumbnail.*small/i.test(src)) return false;
  if (/upload\.wikimedia.*(?:map|globe|location|locator)/i.test(src)) return false;
  if (src.length < 20) return false;
  return true;
}

export default function HeroImage({ src, alt, className = "", loading = "lazy", fetchPriority, style, width, height, focalX, focalY, onOrientationDetected, zoomable = true }: Props) {
  const [failed, setFailed] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const hasFocal = focalX != null && focalY != null && !(focalX === 0.5 && focalY === 0.5);
  const focalStyle: React.CSSProperties = hasFocal
    ? { objectPosition: `${((focalX as number) * 100).toFixed(1)}% ${((focalY as number) * 100).toFixed(1)}%` }
    : {};

  const handleLoad = useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    const ratio = img.naturalWidth / img.naturalHeight;
    const portrait = ratio < 0.87;
    if (!hasFocal && portrait && className.includes("object-cover")) {
      img.style.objectPosition = "top center";
    }
    onOrientationDetected?.(ratio > 1.2 ? "landscape" : "portrait");
  }, [onOrientationDetected, className, hasFocal]);

  if (!isValidImage(src)) return null;

  // Image URL failed to load (hotlink 403, dead CDN, etc.) — render a branded
  // tile instead of leaving the parent's empty gray frame as a dead box.
  // (2026-10-02: homepage grids showed blank gray slots for failed images.)
  if (failed) {
    return (
      <div
        className={className}
        role="img"
        aria-label={alt}
        style={{ ...style, background: "#0B1D3A", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}
      >
        <svg viewBox="0 0 40 40" style={{ width: "38%", height: "38%", opacity: 0.9 }} aria-hidden="true">
          <text x="20" y="30" textAnchor="middle" fontFamily="Georgia, 'Times New Roman', serif" fontWeight="bold" fontSize="30" fill="#D4A843">V</text>
        </svg>
      </div>
    );
  }

  return (
    <>
      <img
        src={src as string}
        alt={alt}
        loading={loading}
        fetchPriority={fetchPriority}
        decoding={loading === "lazy" ? "async" : undefined}
        referrerPolicy="no-referrer"
        onError={() => setFailed(true)}
        onLoad={handleLoad}
        className={`${className}${zoomable ? " cursor-zoom-in" : ""}`}
        style={{...focalStyle, ...style}}
        width={width}
        height={height}
        onClick={zoomable ? () => setExpanded(true) : undefined}
      />

      {/* Lightbox — same pattern as Snapshots: opaque bg, native pinch-to-zoom */}
      {zoomable && expanded && (
        <div
          style={{
            position: "fixed",
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: "rgba(0,0,0,0.95)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            animation: "snapFadeIn 0.15s ease-out",
          }}
          onClick={() => setExpanded(false)}
        >
          <style>{`@keyframes snapFadeIn { from { opacity: 0; } to { opacity: 1; } }`}</style>
          <button
            onClick={() => setExpanded(false)}
            style={{
              position: "absolute", top: 12, right: 16, zIndex: 10000,
              background: "rgba(255,255,255,0.15)", border: "none", color: "#fff",
              width: 36, height: 36, borderRadius: "50%", cursor: "pointer",
              fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center",
            }}
          >×</button>
          <div onClick={(e) => e.stopPropagation()} style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "0 20px" }}>
            <img
              src={src as string}
              alt={alt}
              draggable={false}
              referrerPolicy="no-referrer"
              style={{
                maxWidth: "calc(100vw - 40px)",
                maxHeight: "calc(100vh - 100px)",
                objectFit: "contain",
                borderRadius: "8px",
                userSelect: "none",
                WebkitUserSelect: "none",
              } as React.CSSProperties}
            />
          </div>
        </div>
      )}
    </>
  );
}
