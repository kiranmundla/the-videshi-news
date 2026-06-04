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
  size: _size = "sm",
  align = "left",
}: Props) {
  const trimmed = (caption ?? "").trim();
  // Hide caption entirely if it exceeds 8 words — never truncate.
  const wordCount = trimmed ? trimmed.split(/\s+/).length : 0;
  const showCaption = trimmed.length > 0 && wordCount <= 25;

  if (!showCaption && !credit) return null;

  const alignCls = align === "center" ? "text-center" : "text-left";
  const parts: string[] = [];
  if (showCaption) parts.push(trimmed);
  if (credit) parts.push(credit);

  return (
    <figcaption
      className={`mt-2 leading-snug ${alignCls} max-w-full italic`}
      style={{ fontSize: "11px", color: "#888" }}
    >
      {parts.join(" · ")}
    </figcaption>
  );
}
