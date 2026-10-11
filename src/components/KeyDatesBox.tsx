/**
 * KeyDatesBox — The Videshi's key-dates card for deadline-driven stories.
 * Shows a vertical timeline of dates + events with optional source links.
 * Use for: court injunction timelines, IPO date sequences, festival calendars.
 *
 * Data comes from article.data_cards[] entries with type: "key_dates".
 * Shape:
 * {
 *   type: "key_dates",
 *   title: "Key Dates",              // optional, defaults to "Key Dates"
 *   dates: [
 *     { date: "2026-10-19", event: "Anchor investor allocation", source_url: "https://..." },
 *     { date: "2026-10-21", event: "Public issue opens" }
 *   ]
 * }
 */

export interface KeyDateItem {
  date: string;
  event: string;
  source_url?: string;
}

export interface KeyDatesBoxData {
  type?: string;
  title?: string;
  dates: KeyDateItem[];
}

const NAVY = "#0B1D3A";
const GOLD = "#D4A843";

function formatDateBadge(dateStr: string): { month: string; day: string; year: string } {
  const d = new Date(dateStr + (dateStr.includes("T") ? "" : "T12:00:00"));
  if (isNaN(d.getTime())) return { month: "", day: "?", year: "" };
  return {
    month: d.toLocaleDateString("en-US", { month: "short" }),
    day: d.toLocaleDateString("en-US", { day: "numeric" }),
    year: d.toLocaleDateString("en-US", { year: "numeric" }),
  };
}

export default function KeyDatesBox({ card }: { card: KeyDatesBoxData }) {
  if (!card || !Array.isArray(card.dates) || card.dates.length === 0) return null;
  const title = card.title || "Key Dates";

  return (
    <div
      data-testid="key-dates-box"
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
          📅 {title}
        </span>
      </div>

      {/* Timeline */}
      <div style={{ padding: "8px 18px 14px" }}>
        {card.dates.map((item, i) => {
          const badge = formatDateBadge(item.date);
          const isLast = i === card.dates.length - 1;
          return (
            <div
              key={item.date + i}
              style={{
                display: "flex",
                gap: 14,
                padding: "10px 0",
                borderBottom: isLast ? "none" : "1px solid hsl(var(--rule) / 0.5)",
              }}
            >
              {/* Date badge */}
              <div
                style={{
                  flexShrink: 0,
                  width: 56,
                  textAlign: "center",
                  borderRadius: 8,
                  background: `${GOLD}1a`,
                  border: `1px solid ${GOLD}55`,
                  padding: "6px 4px",
                  alignSelf: "flex-start",
                }}
              >
                <div
                  style={{
                    fontSize: 10.5,
                    fontWeight: 800,
                    letterSpacing: "0.06em",
                    textTransform: "uppercase",
                    color: NAVY,
                  }}
                >
                  {badge.month}
                </div>
                <div
                  style={{
                    fontSize: 20,
                    fontWeight: 800,
                    color: NAVY,
                    lineHeight: 1.1,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {badge.day}
                </div>
                {badge.year && (
                  <div
                    style={{
                      fontSize: 10,
                      fontWeight: 600,
                      color: "hsl(var(--muted-foreground))",
                    }}
                  >
                    {badge.year}
                  </div>
                )}
              </div>

              {/* Event */}
              <div
                style={{
                  flex: 1,
                  fontSize: 14,
                  lineHeight: 1.5,
                  color: "hsl(var(--foreground))",
                  paddingTop: 4,
                }}
              >
                {item.event}
                {item.source_url && (
                  <div style={{ marginTop: 4 }}>
                    <a
                      href={item.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        fontSize: 12.5,
                        fontWeight: 700,
                        color: NAVY,
                        textDecoration: "none",
                        borderBottom: `2px solid ${GOLD}`,
                        paddingBottom: 1,
                      }}
                    >
                      Source <span aria-hidden>→</span>
                    </a>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
