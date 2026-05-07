type Props = {
  caption?: string | null;
  credit?: string | null;
  /** truncate caption to one line (used on cards) */
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
  return (
    <figcaption className={`mt-2 leading-snug ${alignCls}`}>
      {caption && (
        <span
          className={`${captionSize} italic text-foreground/60 ${truncate ? "block truncate" : ""}`}
        >
          {caption}
        </span>
      )}
      {credit && (
        <span className={`${creditSize} text-muted-foreground ${caption ? "ml-1" : ""}`}>
          {caption ? "· " : ""}
          {credit}
        </span>
      )}
    </figcaption>
  );
}
