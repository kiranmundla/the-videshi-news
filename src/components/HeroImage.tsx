import { useState, useCallback, useRef, useEffect } from "react";

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
  if (/(?:^|[/\-_.])(?:logo|icon|avatar|placeholder|default)(?:[/\-_.\s]|$)|thumbnail.*small/i.test(src)) return false;
  if (/upload\.wikimedia.*(?:map|globe|location|locator)/i.test(src)) return false;
  if (src.length < 20) return false;
  return true;
}

export default function HeroImage({ src, alt, className = "", loading = "lazy", fetchPriority, style, width, height, focalX, focalY, onOrientationDetected, zoomable = true }: Props) {
  const [failed, setFailed] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [zoomed, setZoomed] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const lastTapRef = useRef(0);

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

  // Native touchstart listener for double-tap zoom
  useEffect(() => {
    const img = imgRef.current;
    if (!img || !expanded) return;

    const handler = (e: TouchEvent) => {
      e.preventDefault();
      const now = Date.now();
      if (now - lastTapRef.current < 400) {
        setZoomed((z) => !z);
        lastTapRef.current = 0;
      } else {
        lastTapRef.current = now;
      }
    };

    img.addEventListener("touchstart", handler, { passive: false });
    return () => img.removeEventListener("touchstart", handler);
  }, [expanded, zoomed]);

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
          className="fixed inset-0 z-50 flex flex-col bg-black/70 backdrop-blur-sm"
          onClick={() => { setExpanded(false); setZoomed(false); }}
        >
          {/* Top bar */}
          <div className="flex items-center justify-between px-4 py-3 shrink-0" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setZoomed((z) => !z)}
              className="text-white text-sm font-semibold px-3 py-1.5 rounded-full bg-white/20 active:bg-white/30"
            >
              {zoomed ? "Zoom Out" : "Zoom In"}
            </button>
            <button
              onClick={() => { setExpanded(false); setZoomed(false); }}
              className="text-white text-2xl font-bold w-10 h-10 flex items-center justify-center"
              aria-label="Close"
            >
              ✕
            </button>
          </div>

          {/* Image area */}
          <div
            className="flex-1 overflow-auto"
            style={{ WebkitOverflowScrolling: "touch" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className={zoomed ? "" : "h-full flex items-center justify-center px-4"}>
              <img
                ref={imgRef}
                src={src as string}
                alt={alt}
                className={`block rounded-lg shadow-2xl transition-all duration-200 ${
                  zoomed ? "w-[250vw] md:w-[150vw]" : "max-w-[92vw] max-h-[80vh] object-contain"
                }`}
                referrerPolicy="no-referrer"
                style={{ touchAction: "none" }}
                onDoubleClick={() => setZoomed((z) => !z)}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
