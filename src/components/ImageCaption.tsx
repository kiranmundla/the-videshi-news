type Props = {
  caption?: string | null;
  credit?: string | null;
  /** truncate caption to one line (used on small cards) */
  truncate?: boolean;
  /** larger sizing for article hero */
  size?: "sm" | "md";
  align?: "left" | "center";
};

export default function ImageCaption({
  caption,
  credit,
  truncate = false,
  size = "sm",
  align = "left",
}: Props) {
  if (!caption && !credit) return null;
  const captionSize = size === "md" ? "text-[13px]" : "text-[11px]";
  const creditSize = size === "md" ? "text-[11px]" : "text-[10px]";
  const alignCls = align === "center" ? "text-center" : "text-left";

  // Limit caption to max 10 words with ellipsis
  let displayCaption = caption ?? "";
  if (displayCaption) {
    const words = displayCaption.trim().split(/\s+/);
    if (words.length > 10) displayCaption = words.slice(0, 10).join(" ") + "…";
  }

  return (
    <figcaption className={`mt-2 leading-snug ${alignCls} max-w-full`}>
      {displayCaption && (
        <span className={`${captionSize} italic text-foreground/60 block`}>
          {displayCaption}
        </span>
      )}
      {credit && (
        <span className={`${creditSize} text-muted-foreground block`}>
          {credit}
        </span>
      )}
    </figcaption>
  );
}
