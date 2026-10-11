/**
 * MatchScorecard — The Videshi's match summary card for sports articles.
 * Shows teams/scores, result, top performers, and a link to the full scorecard.
 * Designed generically: works for cricket now, extensible to football etc.
 *
 * Data comes from article.data_cards[] entries with type: "match_scorecard".
 * Shape:
 * {
 *   type: "match_scorecard",
 *   sport: "cricket",            // "cricket" | "football" | ...
 *   format: "T20I",              // match format / competition
 *   venue: "JSCA Stadium, Ranchi",
 *   date: "2026-10-10",
 *   teams: [
 *     { name: "West Indies", short: "WI", score: "252/4", overs: "18.3" },
 *     { name: "India", short: "IND", score: "249/5", overs: "20" }
 *   ],
 *   result: "West Indies won by 6 wickets",
 *   series_status: "Series leveled 1-1",   // optional
 *   top_performers: [                        // optional, max 3 shown
 *     { name: "Shai Hope", team: "WI", stat: "102* (45)" },
 *     { name: "Mayank Yadav", team: "IND", stat: "3/38" }
 *   ],
 *   scorecard_url: "https://www.espncricinfo.com/..."  // optional
 * }
 */

export interface ScorecardTeam {
  name: string;
  short: string;
  score: string;
  overs?: string;
}

export interface ScorecardPerformer {
  name: string;
  team?: string;
  stat: string;
}

export interface MatchScorecardData {
  type?: string;
  sport?: string;
  format?: string;
  venue?: string;
  date?: string;
  teams: ScorecardTeam[];
  result?: string;
  series_status?: string;
  top_performers?: ScorecardPerformer[];
  scorecard_url?: string;
}

const NAVY = "#0B1D3A";
const GOLD = "#D4A843";

function formatCardDate(dateStr?: string): string | null {
  if (!dateStr) return null;
  const d = new Date(dateStr + (dateStr.includes("T") ? "" : "T12:00:00"));
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function MatchScorecard({ card }: { card: MatchScorecardData }) {
  if (!card || !Array.isArray(card.teams) || card.teams.length === 0) return null;

  const meta = [card.format, card.venue, formatCardDate(card.date)]
    .filter(Boolean)
    .join("  •  ");
  const performers = (card.top_performers ?? []).slice(0, 3);

  return (
    <div
      data-testid="match-scorecard"
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
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
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
          🏏 Match Scorecard
        </span>
        {meta && (
          <span
            style={{
              fontSize: 11.5,
              color: "rgba(255,255,255,0.75)",
              textAlign: "right",
              lineHeight: 1.4,
            }}
          >
            {meta}
          </span>
        )}
      </div>

      {/* Scores */}
      <div style={{ padding: "16px 18px 6px" }}>
        {card.teams.map((t, i) => (
          <div
            key={t.short || i}
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
              gap: 12,
              padding: "7px 0",
              borderBottom:
                i < card.teams.length - 1
                  ? "1px solid hsl(var(--rule) / 0.5)"
                  : "none",
            }}
          >
            <span
              style={{
                fontSize: 15,
                fontWeight: 700,
                color: "hsl(var(--foreground))",
              }}
            >
              <span
                style={{
                  display: "inline-block",
                  minWidth: 40,
                  fontSize: 12,
                  fontWeight: 800,
                  color: "#fff",
                  background: NAVY,
                  borderRadius: 4,
                  padding: "2px 6px",
                  marginRight: 8,
                  textAlign: "center",
                  verticalAlign: "1px",
                }}
              >
                {t.short}
              </span>
              {t.name}
            </span>
            <span
              style={{
                fontSize: 16,
                fontWeight: 800,
                fontVariantNumeric: "tabular-nums",
                color: "hsl(var(--foreground))",
                whiteSpace: "nowrap",
              }}
            >
              {t.score}
              {t.overs && (
                <span
                  style={{
                    fontSize: 12.5,
                    fontWeight: 500,
                    color: "hsl(var(--muted-foreground))",
                    marginLeft: 6,
                  }}
                >
                  ({t.overs} ov)
                </span>
              )}
            </span>
          </div>
        ))}
      </div>

      {/* Result line */}
      {card.result && (
        <div
          style={{
            padding: "10px 18px",
            background: `${GOLD}1a`,
            borderTop: `1px solid ${GOLD}55`,
            borderBottom: `1px solid ${GOLD}55`,
          }}
        >
          <div
            style={{
              fontSize: 14,
              fontWeight: 700,
              color: NAVY,
              lineHeight: 1.45,
            }}
          >
            {card.result}
          </div>
          {card.series_status && (
            <div
              style={{
                fontSize: 12.5,
                color: "hsl(var(--muted-foreground))",
                marginTop: 2,
              }}
            >
              {card.series_status}
            </div>
          )}
        </div>
      )}

      {/* Top performers */}
      {performers.length > 0 && (
        <div style={{ padding: "12px 18px 4px" }}>
          <div
            style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: "0.07em",
              textTransform: "uppercase",
              color: "hsl(var(--muted-foreground))",
              marginBottom: 8,
            }}
          >
            Top Performers
          </div>
          {performers.map((p, i) => (
            <div
              key={p.name + i}
              style={{
                display: "flex",
                alignItems: "baseline",
                justifyContent: "space-between",
                gap: 10,
                padding: "5px 0",
                fontSize: 13.5,
              }}
            >
              <span style={{ color: "hsl(var(--foreground))", fontWeight: 600 }}>
                {p.name}
                {p.team && (
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: "hsl(var(--muted-foreground))",
                      marginLeft: 6,
                    }}
                  >
                    {p.team}
                  </span>
                )}
              </span>
              <span
                style={{
                  fontWeight: 700,
                  fontVariantNumeric: "tabular-nums",
                  color: NAVY,
                  whiteSpace: "nowrap",
                }}
              >
                {p.stat}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Full scorecard link */}
      {card.scorecard_url && (
        <div style={{ padding: "10px 18px 16px" }}>
          <a
            href={card.scorecard_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              fontSize: 13.5,
              fontWeight: 700,
              color: NAVY,
              textDecoration: "none",
              borderBottom: `2px solid ${GOLD}`,
              paddingBottom: 1,
            }}
          >
            Full scorecard on ESPNcricinfo
            <span aria-hidden>→</span>
          </a>
        </div>
      )}
    </div>
  );
}
