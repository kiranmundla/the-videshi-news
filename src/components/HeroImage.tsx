import { useState, useCallback } from "react";
import { optimizeImageUrl, IMAGE_SIZES } from "@/lib/imageUrl";

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
  onOrientationDetected?: (orientation: "landscape" | "portrait") => void;
};

export function isValidImage(src?: string | null): boolean {
  if (!src || typeof src !== "string") return false;
  if (src.trim().length === 0) return false;
  if (/hindustantimes\.com|htmedia/i.test(src)) return false;
  if (src.toLowerCase().endsWith(".svg")) return false;
  if (/Flag_of_|flag_of_|_flag\.|national.flag/i.test(src)) return false;
  if (src.includes("Flag_of_Canada")) return false;
  // Reject common low-quality image patterns
  if (/logo|icon|avatar|placeholder|default|thumbnail.*small/i.test(src)) return false;
  // Reject Wikipedia map/globe images
  if (/upload\.wikimedia.*(?:map|globe|location|locator)/i.test(src)) return false;
  // Reject very short URLs (likely broken)
  if (src.length < 20) return false;
  return true;
}

export default function HeroImage({ src, alt, className = "", loading = "lazy", fetchPriority, style, width, height, onOrientationDetected }: Props) {
  const [failed, setFailed] = useState(false);

  const handleLoad = useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
    if (!onOrientationDetected) return;
    const img = e.currentTarget;
    const ratio = img.naturalWidth / img.naturalHeight;
    onOrientationDetected(ratio > 1.2 ? "landscape" : "portrait");
  }, [onOrientationDetected]);

  if (!isValidImage(src) || failed) {
    // Return a placeholder that preserves layout space to prevent CLS
    return <div className={className} style={{ ...style, backgroundColor: '#f5f5f0' }} />;
  }
  const optimizedSrc = optimizeImageUrl(src as string, typeof width === 'number' ? width : IMAGE_SIZES.gallery);
  return (
    <img
      src={optimizedSrc}
      alt={alt}
      loading={loading}
      fetchPriority={fetchPriority}
      decoding={loading === "lazy" ? "async" : undefined}
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
      onLoad={handleLoad}
      className={className}
      style={style}
      width={width}
      height={height}
    />
  );
}
