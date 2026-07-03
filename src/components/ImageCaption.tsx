type Props = {
  caption?: string | null;
  credit?: string | null;
  /** @deprecated kept for backwards compatibility — no longer truncates */
  truncate?: boolean;
  size?: "sm" | "md";
  align?: "left" | "center";
};

export default function ImageCaption({
  caption,
  credit,
  size = "sm",
  align = "left",
}: Props) {
  const trimmed = (caption ?? "").trim();
  const wordCount = trimmed ? trimmed.split(/\s+/).length : 0;
  const showCaption = trimmed.length > 0 && wordCount <= 25;

  if (!showCaption && !credit) return null;

  const alignCls = align === "center" ? "text-center" : "text-left";
  const fontSize = size === "md" ? "13px" : "12px";

  return (
    <figcaption
      className={`mt-2 leading-snug ${alignCls} max-w-full`}
      style={{ fontSize, color: "#555" }}
    >
      {showCaption && <span className="italic">{trimmed}</span>}
      {showCaption && credit && <span> · </span>}
      {credit && <span style={{ color: "#888" }}>{credit}</span>}
    </figcaption>
  );
}
