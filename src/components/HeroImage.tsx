import { useState } from "react";

type Props = {
  src?: string | null;
  alt: string;
  className?: string;
  loading?: "eager" | "lazy";
  category?: string;
};

export function isValidImage(src?: string | null): boolean {
  if (!src || typeof src !== "string") return false;
  if (src.trim().length === 0) return false;
  if (/hindustantimes\.com|htmedia/i.test(src)) return false;
  if (src.toLowerCase().endsWith(".svg")) return false;
  if (/Flag_of_|flag_of_|_flag\.|national.flag/i.test(src)) return false;
  if (src.includes("Flag_of_Canada")) return false;
  return true;
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
