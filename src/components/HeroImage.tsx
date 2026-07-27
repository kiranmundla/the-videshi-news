import { useState, useCallback, useRef } from "react";

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
  /** Set false to disable tap-to-expand (default true) */
  zoomable?: boolean;
};

export function isValidImage(src?: string | null): boolean {
  if (!src || typeof src !== "string") return false;
  if (src.trim().length === 0) return false;
  if (/hindustantimes\.com|htmedia/i.test(src)) return false;
  if (src.toLowerCase().endsWith(".svg")) return false;
  if (/Flag_of_|flag_of_|_flag\.|national.flag/i.test(src)) return false;
  if (src.includes("Flag_of_Canada")) return false;
  // Reject common low-quality image patterns — match as path segments (separator-bounded),
  // not as substrings, to avoid false positives like "iconic" or "semiconductor"
  if (/(?:^|[/\-_.])(?:logo|icon|avatar|placeholder|default)(?:[/\-_.\s]|$)|thumbnail.*small/i.test(src)) return false;
  // Reject Wikipedia map/globe images
  if (/upload\.wikimedia.*(?:map|globe|location|locator)/i.test(src)) return false;
  // Reject very short URLs (likely broken)
  if (src.length < 20) return false;
  return true;
}

export default function HeroImage({ src, alt, className = "", loading = "lazy", fetchPriority, style, width, height, focalX, focalY, onOrientationDetected, zoomable = true }: Props) {
  const [failed, setFailed] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [zoomed, setZoomed] = useState(false);
  const lastTapRef = useRef(0);

  // Build object-position from focal point data (pipeline-computed)
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

  const handleDoubleTap = useCallback(() => {
    const now = Date.now();
    if (now - lastTapRef.current < 400) {
      setZoomed((z) => !z);
      lastTapRef.current = 0;
    } else {
      lastTapRef.current = now;
    }
  }, []);

  if (!isValidImage(src) || failed) return null;

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

      {zoomable && expanded && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={() => { setExpanded(false); setZoomed(false); }}
        >
          <button
            onClick={() => { setExpanded(false); setZoomed(false); }}
            className="absolute top-4 right-4 text-white text-2xl font-bold w-10 h-10 flex items-center justify-center z-50"
            aria-label="Close"
          >
            ✕
          </button>
          <div
            className={`transition-all duration-200 ${
              zoomed ? "overflow-auto max-h-[95vh] max-w-[95vw]" : "flex items-center justify-center px-4"
            }`}
            style={{ WebkitOverflowScrolling: "touch" }}
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={src as string}
              alt={alt}
              className={`block rounded-lg shadow-2xl transition-all duration-200 ${
                zoomed ? "w-[250vw] md:w-[150vw]" : "max-w-[92vw] max-h-[80vh] object-contain"
              }`}
              referrerPolicy="no-referrer"
              style={{ touchAction: "none" }}
              onTouchStart={handleDoubleTap}
              onDoubleClick={() => setZoomed((z) => !z)}
            />
          </div>
        </div>
      )}
    </>
  );
}
