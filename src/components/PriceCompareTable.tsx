/**
 * PriceCompareTable — The Videshi's cost-comparison table card.
 * Clean table with an optional highlighted row (the best option).
 * Use for: savings breakdowns, service comparisons, cost tables.
 *
 * Data comes from article.data_cards[] entries with type: "price_compare".
 * Shape:
 * {
 *   type: "price_compare",
 *   title: "Savings Breakdown",
 *   headers: ["Item", "Regular", "Student Fare"],
 *   rows: [
 *     ["Base fare", "$1,200", "$1,080"],
 *     ["Change fee", "$150", "Free"]
 *   ],
 *   highlight_row: 2   // optional, 0-based index of row to highlight
 * }
 */

export interface PriceCompareTableData {
  type?: string;
  title: string;
  headers: string[];
  rows: string[][];
  highlight_row?: number;
}

const NAVY = "#0B1D3A";
const GOLD = "#D4A843";

export default function PriceCompareTable({ card }: { card: PriceCompareTableData }) {
  if (
    !card ||
    !card.title ||
    !Array.isArray(card.headers) ||
    card.headers.length === 0 ||
    !Array.isArray(card.rows) ||
    card.rows.length === 0
  )
    return null;

  return (
    <div
      data-testid="price-compare-table"
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
          💰 {card.title}
        </span>
      </div>

      {/* Table */}
      <div style={{ overflowX: "auto", padding: "6px 10px 10px" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: 13.5,
            minWidth: 320,
          }}
        >
          <thead>
            <tr>
              {card.headers.map((h, i) => (
                <th
                  key={i}
                  style={{
                    textAlign: i === 0 ? "left" : "right",
                    padding: "10px 10px 8px",
                    fontSize: 11.5,
                    fontWeight: 800,
                    letterSpacing: "0.05em",
                    textTransform: "uppercase",
                    color: "hsl(var(--muted-foreground))",
                    borderBottom: `2px solid ${NAVY}33`,
                    whiteSpace: "nowrap",
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {card.rows.map((row, ri) => {
              const highlighted = card.highlight_row === ri;
              return (
                <tr
                  key={ri}
                  style={{
                    background: highlighted ? `${GOLD}1a` : "transparent",
                  }}
                >
                  {card.headers.map((_, ci) => {
                    const cell = row[ci] ?? "";
                    const isFirst = ci === 0;
                    return (
                      <td
                        key={ci}
                        style={{
                          textAlign: isFirst ? "left" : "right",
                          padding: "9px 10px",
                          fontWeight: isFirst
                            ? 600
                            : highlighted
                              ? 800
                              : 500,
                          color: highlighted && !isFirst
                            ? NAVY
                            : "hsl(var(--foreground))",
                          borderBottom:
                            ri < card.rows.length - 1
                              ? "1px solid hsl(var(--rule) / 0.5)"
                              : "none",
                          fontVariantNumeric: "tabular-nums",
                          whiteSpace: isFirst ? "normal" : "nowrap",
                          borderLeft: highlighted
                            ? `3px solid ${GOLD}`
                            : "3px solid transparent",
                        }}
                      >
                        {highlighted && isFirst && (
                          <span
                            style={{
                              fontSize: 10,
                              fontWeight: 800,
                              letterSpacing: "0.06em",
                              textTransform: "uppercase",
                              color: NAVY,
                              background: GOLD,
                              borderRadius: 4,
                              padding: "1px 6px",
                              marginRight: 8,
                              verticalAlign: "1px",
                            }}
                          >
                            Best
                          </span>
                        )}
                        {cell}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
