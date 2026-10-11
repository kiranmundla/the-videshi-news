/**
 * ChecklistCard — The Videshi's eligibility/requirements checklist card.
 * Checkbox-style items with an optional "catch" callout at the bottom.
 * Use for: program eligibility, document checklists, requirement lists.
 *
 * Data comes from article.data_cards[] entries with type: "checklist".
 * Shape:
 * {
 *   type: "checklist",
 *   title: "Eligibility Checklist",
 *   items: [
 *     { text: "Canadian PR or citizenship", note: "Required" },
 *     { text: "Complete Touchstone assessment" }
 *   ],
 *   catch_text: "Must commit to 3-year return-of-service in underserved areas."  // optional
 * }
 */

export interface ChecklistItem {
  text: string;
  note?: string;
}

export interface ChecklistCardData {
  type?: string;
  title: string;
  items: ChecklistItem[];
  catch_text?: string;
}

const NAVY = "#0B1D3A";
const GOLD = "#D4A843";

export default function ChecklistCard({ card }: { card: ChecklistCardData }) {
  if (!card || !card.title || !Array.isArray(card.items) || card.items.length === 0)
    return null;

  return (
    <div
      data-testid="checklist-card"
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
          ✅ {card.title}
        </span>
      </div>

      {/* Items */}
      <div style={{ padding: "8px 18px 6px" }}>
        {card.items.map((item, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              gap: 12,
              alignItems: "flex-start",
              padding: "10px 0",
              borderBottom:
                i < card.items.length - 1
                  ? "1px solid hsl(var(--rule) / 0.5)"
                  : "none",
            }}
          >
            {/* Checkbox */}
            <div
              style={{
                flexShrink: 0,
                width: 22,
                height: 22,
                borderRadius: 6,
                border: `2px solid ${GOLD}`,
                background: `${GOLD}1a`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginTop: 1,
              }}
            >
              <svg
                width="13"
                height="13"
                viewBox="0 0 13 13"
                fill="none"
                aria-hidden
              >
                <path
                  d="M2.5 6.8L5.3 9.5L10.5 3.5"
                  stroke={NAVY}
                  strokeWidth="2.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>

            {/* Text */}
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: "hsl(var(--foreground))",
                  lineHeight: 1.5,
                }}
              >
                {item.text}
              </div>
              {item.note && (
                <div
                  style={{
                    fontSize: 12.5,
                    color: "hsl(var(--muted-foreground))",
                    marginTop: 2,
                    lineHeight: 1.45,
                  }}
                >
                  {item.note}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Catch callout */}
      {card.catch_text && (
        <div
          style={{
            margin: "6px 18px 16px",
            padding: "10px 14px",
            borderRadius: 8,
            background: `${GOLD}1a`,
            borderLeft: `3px solid ${GOLD}`,
          }}
        >
          <span
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: NAVY,
            }}
          >
            ⚠ The catch:{' '}
          </span>
          <span
            style={{
              fontSize: 13.5,
              color: "hsl(var(--foreground))",
              lineHeight: 1.5,
            }}
          >
            {card.catch_text}
          </span>
        </div>
      )}
    </div>
  );
}
