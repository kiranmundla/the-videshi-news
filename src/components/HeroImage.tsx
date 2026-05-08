import { useState } from "react";

type Props = {
  src?: string | null;
  alt: string;
  className?: string;
  loading?: "eager" | "lazy";
  category?: string;
};

const BLOCKED_RE = /hindustantimes\.com|htmedia/i;

export function isValidImage(src?: string | null): boolean {
  return typeof src === "string" && src.trim().length > 0 && !BLOCKED_RE.test(src);
}

export default function HeroImage({ src, alt, className = "", loading = "lazy" }: Props) {
  const [failed, setFailed] = useState(false);
  if (!isValidImage(src) || failed) return null;
  return (
    <img
      src={src as string}
      alt={alt}
      loading={loading}
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
      className={className}
    />
  );
}
