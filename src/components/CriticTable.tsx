/**
 * CriticTable — The Videshi's critic-by-critic breakdown for movie reviews.
 * Shows each critic's name, publication, rating, key verdict quote, and link.
 *
 * Data comes from article.data_cards[] entries with type: "critic_table".
 * Shape:
 * {
 *   type: "critic_table",
 *   title: "What Critics Are Saying",   // optional, defaults to this
 *   critics: [
 *     {
 *       name: "Anupama Chopra",
 *       publication: "Film Companion",
 *       rating: "4/5",                          // optional
 *       verdict: "A stunning achievement...",   // key quote from the review
 *       url: "https://..."                     // optional link to full review
 *     },
 *     ...
 *   ]
 * }
 *
 * Rules: sourced data only — never invent critics, ratings, or quotes.
 * Each entry needs a name and a verdict; rating and URL are optional.
 * Returns null on missing/invalid data.
 */

export interface CriticEntry {
  name: string;
  publication?: string;
  rating?: string;
  verdict: string;
  url?: string;
}

export interface CriticTableData {
  type?: string;
  title?: string;
  critics?: CriticEntry[];
}

const NAVY = "#0B1D3A";
const GOLD = "#D4A843";

export default function CriticTable({ card }: { card: CriticTableData }) {
  if (!card) return null;

  const critics = (card.critics ?? []).filter(
    (c) => c && c.name && c.name.trim() && c.verdict && c.verdict.trim()
  );
  if (critics.length === 0) return null;

  const title = card.title || "What Critics Are Saying";

  return (
    <div
      data-testid="critic-table"
      style={{
        margin: "0 0 28px",
        borderRadius: 14,
        overflow: "hidden",
        border: `1px solid hsl(var(--rule))`,
        background: "hsl(var(--card))",
      }}
    >
      {/* Header bar */}
      <div
        style={{
          background: NAVY,
          color: "#fff",
          padding: "10px 18px",
        }}
      >
        <span
          style={{
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          ⭐ {title}
        </span>
      </div>

      {/* Critic entries */}
      <div style={{ padding: "8px 18px 14px" }}>
        {critics.map((c, i) => (
          <div
            key={c.name + i}
            style={{
              padding: "14px 0",
              borderBottom:
                i < critics.length - 1
                  ? "1px solid hsl(var(--rule) / 0.5)"
                  : "none",
            }}
          >
            {/* Name + publication + rating */}
            <div
              style={{
                display: "flex",
                alignItems: "baseline",
                justifyContent: "space-between",
                gap: 12,
                flexWrap: "wrap",
                marginBottom: 6,
              }}
            >
              <div>
                <span
                  style={{
                    fontSize: 14,
                    fontWeight: 800,
                    color: NAVY,
                  }}
                >
                  {c.name}
                </span>
                {c.publication && (
                  <span
                    style={{
                      fontSize: 12.5,
                      color: "hsl(var(--muted-foreground))",
                      marginLeft: 8,
                      fontStyle: "italic",
                    }}
                  >
                    {c.publication}
                  </span>
                )}
              </div>
              {c.rating && (
                <span
                  style={{
                    display: "inline-block",
                    fontSize: 12.5,
                    fontWeight: 800,
                    color: "#fff",
                    background: GOLD,
                    borderRadius: 4,
                    padding: "3px 9px",
                    fontVariantNumeric: "tabular-nums",
                    whiteSpace: "nowrap",
                  }}
                >
                  {c.rating}
                </span>
              )}
            </div>

            {/* Verdict quote */}
            <blockquote
              style={{
                margin: 0,
                padding: "0 0 0 12px",
                borderLeft: `3px solid ${GOLD}`,
                fontSize: 13.5,
                lineHeight: 1.55,
                color: "hsl(var(--foreground))",
                fontStyle: "italic",
              }}
            >
              “{c.verdict}”
            </blockquote>

            {/* Source link */}
            {c.url && (
              <div style={{ marginTop: 6 }}>
                <a
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: 12.5,
                    fontWeight: 700,
                    color: NAVY,
                    textDecoration: "none",
                    borderBottom: `1px solid ${GOLD}`,
                  }}
                >
                  Read full review →
                </a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
