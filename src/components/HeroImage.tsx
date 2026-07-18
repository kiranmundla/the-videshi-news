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

export default function HeroImage({ src, alt, className = "", loading = "lazy", fetchPriority, style, width, height, focalX, focalY, onOrientationDetected }: Props) {
  const [failed, setFailed] = useState(false);

  // Build object-position from focal point data (pipeline-computed)
  const hasFocal = focalX != null && focalY != null && !(focalX === 0.5 && focalY === 0.5);
  const focalStyle: React.CSSProperties = hasFocal
    ? { objectPosition: `${((focalX as number) * 100).toFixed(1)}% ${((focalY as number) * 100).toFixed(1)}%` }
    : {};

  const handleLoad = useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    const ratio = img.naturalWidth / img.naturalHeight;
    const portrait = ratio < 0.87;
    // For portrait images without pipeline focal data, shift to top so faces aren't cropped.
    if (!hasFocal && portrait && className.includes("object-cover")) {
      img.style.objectPosition = "top center";
    }
    onOrientationDetected?.(ratio > 1.2 ? "landscape" : "portrait");
  }, [onOrientationDetected, className, hasFocal]);

  if (!isValidImage(src) || failed) return null;

  return (
    <img
      src={src as string}
      alt={alt}
      loading={loading}
      fetchPriority={fetchPriority}
      decoding={loading === "lazy" ? "async" : undefined}
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
      onLoad={handleLoad}
      className={className}
      style={{...focalStyle, ...style}}
      width={width}
      height={height}
    />
  );
}
