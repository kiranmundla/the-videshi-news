import { useState } from "react";

type Props = {
  src?: string | null;
  alt: string;
  className?: string;
  loading?: "eager" | "lazy";
  category?: string;
};

export default function HeroImage({ src, alt, className = "", loading = "lazy", category }: Props) {
  const [failed, setFailed] = useState(false);
  const isBlocked = typeof src === "string" && /hindustantimes\.com|htmedia/i.test(src);
  const valid = typeof src === "string" && src.trim().length > 0 && !isBlocked;

  if (!valid || failed) {
    return (
      <div
        className={`bg-secondary border hairline flex items-center justify-center ${className}`}
        aria-label={alt}
        role="img"
      >
        <span className="smallcaps text-primary/70 text-xs md:text-sm px-4 text-center">
          {category || "The Videshi"}
        </span>
      </div>
    );
  }

  return (
    <img
      src={src as string}
      alt={alt}
      loading={loading}
      onError={() => setFailed(true)}
      className={className}
    />
  );
}
