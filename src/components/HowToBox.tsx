/**
 * HowToBox — The Videshi's step-by-step how-to card.
 * Numbered steps with optional detail text and links.
 * Use for: "How NRIs can apply for Jio IPO", "FHA loan eligibility by visa status".
 *
 * Data comes from article.data_cards[] entries with type: "how_to".
 * Shape:
 * {
 *   type: "how_to",
 *   title: "How NRIs Can Apply for the Jio IPO",
 *   steps: [
 *     { step: "Open an NRE/NRO demat account", detail: "Needed for IPO bidding...", link: "https://...", link_text: "SEBI guide" },
 *     { step: "Apply via ASBA", detail: "..." }
 *   ]
 * }
 */

export interface HowToStep {
  step: string;
  detail?: string;
  link?: string;
  link_text?: string;
}

export interface HowToBoxData {
  type?: string;
  title: string;
  steps: HowToStep[];
}

const NAVY = "#0B1D3A";
const GOLD = "#D4A843";

export default function HowToBox({ card }: { card: HowToBoxData }) {
  if (!card || !card.title || !Array.isArray(card.steps) || card.steps.length === 0)
    return null;

  return (
    <div
      data-testid="how-to-box"
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
          📋 {card.title}
        </span>
      </div>

      {/* Steps */}
      <div style={{ padding: "8px 18px 14px" }}>
        {card.steps.map((s, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              gap: 14,
              padding: "12px 0",
              borderBottom:
                i < card.steps.length - 1
                  ? "1px solid hsl(var(--rule) / 0.5)"
                  : "none",
            }}
          >
            {/* Step number */}
            <div
              style={{
                flexShrink: 0,
                width: 30,
                height: 30,
                borderRadius: "50%",
                background: NAVY,
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 13.5,
                fontWeight: 800,
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {i + 1}
            </div>

            {/* Step content */}
            <div style={{ flex: 1, paddingTop: 2 }}>
              <div
                style={{
                  fontSize: 14.5,
                  fontWeight: 700,
                  color: "hsl(var(--foreground))",
                  lineHeight: 1.45,
                }}
              >
                {s.step}
              </div>
              {s.detail && (
                <div
                  style={{
                    fontSize: 13.5,
                    color: "hsl(var(--muted-foreground))",
                    lineHeight: 1.55,
                    marginTop: 4,
                  }}
                >
                  {s.detail}
                </div>
              )}
              {s.link && (
                <div style={{ marginTop: 6 }}>
                  <a
                    href={s.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      fontSize: 13,
                      fontWeight: 700,
                      color: NAVY,
                      textDecoration: "none",
                      borderBottom: `2px solid ${GOLD}`,
                      paddingBottom: 1,
                    }}
                  >
                    {s.link_text || "Learn more"} <span aria-hidden>→</span>
                  </a>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
