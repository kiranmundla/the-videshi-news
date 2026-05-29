/**
 * Extracts a YouTube video ID from various URL formats.
 * Supports youtube.com/watch?v=, youtu.be/, youtube.com/embed/, youtube.com/shorts/
 */
export function extractYouTubeId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?.*v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/shorts\/)([A-Za-z0-9_-]{11})/,
  ];
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  return null;
}

interface Props {
  url: string;
}

export default function YouTubeEmbed({ url }: Props) {
  const videoId = extractYouTubeId(url);
  if (!videoId) return null;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: 720,
        margin: "1.5rem auto",
        borderRadius: 12,
        overflow: "hidden",
        boxShadow: "0 4px 20px rgba(0,0,0,0.12)",
        background: "#000",
      }}
    >
      <div
        style={{
          position: "relative",
          paddingBottom: "56.25%", // 16:9
          height: 0,
        }}
      >
        <iframe
          src={`https://www.youtube.com/embed/${videoId}?rel=0`}
          title="YouTube video"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            border: "none",
          }}
        />
      </div>
    </div>
  );
}
