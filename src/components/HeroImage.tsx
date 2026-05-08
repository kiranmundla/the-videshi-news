import { useState } from "react";

type Props = {
  src?: string | null;
  alt: string;
  className?: string;
  loading?: "eager" | "lazy";
  category?: string;
};

// Map categories to design-token-based gradient classes for consistent theming
const categoryStyles: Record<string, string> = {
  India: "from-primary/20 via-primary/10 to-secondary",
  "NRI Affairs": "from-accent/30 via-accent/10 to-secondary",
  "US-India": "from-primary/25 via-accent/10 to-secondary",
  Business: "from-secondary via-muted to-primary/10",
  Culture: "from-accent/25 via-primary/10 to-secondary",
  Voices: "from-primary/15 via-secondary to-accent/15",
  Politics: "from-primary/30 via-secondary to-muted",
  Opinion: "from-accent/20 via-secondary to-primary/10",
};

function gradientFor(category?: string) {
  if (category && categoryStyles[category]) return categoryStyles[category];
  // Deterministic fallback based on category string
  const palettes = Object.values(categoryStyles);
  if (!category) return "from-secondary via-muted to-secondary";
  let h = 0;
  for (let i = 0; i < category.length; i++) h = (h * 31 + category.charCodeAt(i)) >>> 0;
  return palettes[h % palettes.length];
}

export default function HeroImage({ src, alt, className = "", loading = "lazy", category }: Props) {
  const [failed, setFailed] = useState(false);
  const isBlocked = typeof src === "string" && /hindustantimes\.com|htmedia/i.test(src);
  const valid = typeof src === "string" && src.trim().length > 0 && !isBlocked;

  if (!valid || failed) {
    const gradient = gradientFor(category);
    return (
      <div
        className={`relative bg-gradient-to-br ${gradient} border hairline overflow-hidden flex items-center justify-center ${className}`}
        aria-label={alt}
        role="img"
      >
        {/* Decorative hairline frame */}
        <div className="absolute inset-3 border hairline pointer-events-none" aria-hidden="true" />
        <div className="relative text-center px-4">
          <p className="smallcaps text-primary text-[0.65rem] md:text-xs tracking-[0.2em]">
            {category || "The Videshi"}
          </p>
          <p className="mt-1 font-serif italic text-foreground/60 text-[0.7rem] md:text-sm">
            The Videshi
          </p>
        </div>
      </div>
    );
  }

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
