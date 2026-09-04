/**
 * MovieRatingsCard — The Videshi's editorial ratings scorecard.
 * Shows overall star rating + category breakdowns, synthesized from critic reviews.
 * Used on both the movie detail page and review article page.
 */

interface MovieRatingsCardProps {
  starRating: number;
  categoryRatings?: Record<string, number>;
  ratingConsensus?: string | null;
}

const CATEGORY_LABELS: Record<string, string> = {
  acting: "Acting",
  direction: "Direction",
  story: "Story",
  music: "Music",
  visuals: "Visuals",
};

function Stars({ rating, size = 16 }: { rating: number; size?: number }) {
  const stars = [];
  for (let i = 1; i <= 5; i++) {
    if (rating >= i) {
      stars.push(
        <span key={i} style={{ color: "#D4A843", fontSize: size }}>
          ★
        </span>
      );
    } else if (rating >= i - 0.5) {
      stars.push(
        <span
          key={i}
          style={{
            position: "relative",
            display: "inline-block",
            fontSize: size,
          }}
        >
          <span style={{ color: "#ddd" }}>★</span>
          <span
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              overflow: "hidden",
              width: "50%",
              color: "#D4A843",
            }}
          >
            ★
          </span>
        </span>
      );
    } else {
      stars.push(
        <span key={i} style={{ color: "#ddd", fontSize: size }}>
          ★
        </span>
      );
    }
  }
  return <>{stars}</>;
}

export default function MovieRatingsCard({
  starRating,
  categoryRatings,
  ratingConsensus,
}: MovieRatingsCardProps) {
  return (
    <div
      style={{
        marginBottom: 24,
        padding: "20px 20px 16px",
        background: "hsl(var(--muted) / 0.3)",
        borderRadius: 12,
        border: "1px solid hsl(var(--rule))",
      }}
    >
      {/* Overall rating */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginBottom: categoryRatings && Object.keys(categoryRatings).length > 0 ? 16 : 0,
        }}
      >
        <span
          style={{
            fontSize: 36,
            fontWeight: 800,
            color: "#D4A843",
            fontFamily: "var(--font-serif, 'Playfair Display', serif)",
            lineHeight: 1,
          }}
        >
          {starRating}
        </span>
        <div>
          <div style={{ display: "flex", gap: 2 }}>
            <Stars rating={starRating} size={20} />
          </div>
          <span
            style={{
              fontSize: 11,
              color: "#888",
              fontWeight: 600,
              letterSpacing: "0.05em",
            }}
          >
            THE VIDESHI RATING
          </span>
        </div>
      </div>

      {/* Category ratings */}
      {categoryRatings && Object.keys(categoryRatings).length > 0 && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "8px 20px",
          }}
        >
          {Object.entries(categoryRatings).map(([cat, rating]) => (
            <div
              key={cat}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <span style={{ fontSize: 12, color: "#666", fontWeight: 600 }}>
                {CATEGORY_LABELS[cat] || cat}
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <div style={{ display: "flex", gap: 1 }}>
                  <Stars rating={rating} size={12} />
                </div>
                <span
                  style={{
                    fontSize: 11,
                    color: "#999",
                    fontWeight: 600,
                    minWidth: 20,
                    textAlign: "right",
                  }}
                >
                  {rating}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Consensus line */}
      {ratingConsensus && (
        <div
          style={{
            marginTop: 12,
            paddingTop: 10,
            borderTop: "1px solid hsl(var(--rule) / 0.5)",
            fontSize: 12,
            color: "#888",
            fontStyle: "italic",
          }}
        >
          {ratingConsensus}
        </div>
      )}
    </div>
  );
}
