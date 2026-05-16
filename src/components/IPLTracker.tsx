import { useEffect, useState } from "react";

/* ── Types ─────────────────────────────────────────────── */
interface Standing {
  team: string;
  short: string;
  played: number;
  won: number;
  lost: number;
  nr: number;
  nrr: string;
  points: number;
  position: number;
}

interface RecentResult {
  match?: number;
  team1: string;
  team2: string;
  score1: string;
  score2: string;
  winner: string;
  margin: string;
  date: string;
  venue?: string;
}

interface NextMatch {
  team1: string;
  team2: string;
  date: string;
  time: string;
  venue: string;
}

interface IPLData {
  season: string;
  last_updated: string;
  stage?: string;
  standings: Standing[];
  recent_results?: RecentResult[];
  next_match?: NextMatch;
  playoffs?: {
    qualifier1?: { date: string; venue: string };
    eliminator?: { date: string; venue: string };
    qualifier2?: { date: string; venue: string };
    final?: { date: string; venue: string };
  };
}

/* ── Team colours ──────────────────────────────────────── */
const TEAM_COLORS: Record<string, string> = {
  CSK: "#FFCB05",
  MI: "#004BA0",
  RCB: "#EC1C24",
  KKR: "#3A225D",
  DC: "#004C93",
  PBKS: "#ED1B24",
  RR: "#EA1A85",
  SRH: "#FF822A",
  GT: "#1C1C1C",
  LSG: "#A72056",
};

function teamColor(short: string): string {
  return TEAM_COLORS[short] || "#666";
}

/* ── Helpers ───────────────────────────────────────────── */
function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  // Handle "DD Mon" or "DD Mon YYYY" format from the pipeline (e.g. "16 May", "31 May 2026")
  const ddMon = dateStr.match(/^(\d{1,2})\s+([A-Za-z]+)(?:\s+(\d{4}))?$/);
  if (ddMon) {
    const [, day, mon] = ddMon;
    return `${mon.slice(0, 3)} ${parseInt(day, 10)}`;
  }
  // Handle ISO "YYYY-MM-DD" format
  try {
    const d = new Date(dateStr + "T00:00:00");
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
    }
  } catch { /* fall through */ }
  return dateStr;
}

function timeAgo(isoStr: string): string {
  try {
    const diff = Date.now() - new Date(isoStr).getTime();
    const hrs = Math.floor(diff / 3600000);
    if (hrs < 1) return "just now";
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  } catch {
    return "";
  }
}

/* ── Component ─────────────────────────────────────────── */
export default function IPLTracker() {
  const [data, setData] = useState<IPLData | null>(null);
  const [tab, setTab] = useState<"table" | "results">("table");

  useEffect(() => {
    fetch("/data/ipl-standings.json")
      .then((r) => {
        if (!r.ok) throw new Error("not found");
        return r.json();
      })
      .then((d: IPLData) => {
        if (d && d.standings && d.standings.length > 0) setData(d);
      })
      .catch(() => {
        /* silently don't render */
      });
  }, []);

  if (!data) return null;

  const playoffLine = 4;
  return (
    <section
      style={{
        margin: "0 0 2rem",
        border: "1px solid #e5e5e5",
        borderRadius: 8,
        overflow: "hidden",
        background: "#fff",
      }}
    >
      {/* Header */}
      <div
        style={{
          background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
          padding: "12px 20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 8,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 20 }}>🏏</span>
          <div>
            <div
              style={{
                color: "#fff",
                fontFamily: "'Playfair Display', Georgia, serif",
                fontSize: 16,
                fontWeight: 700,
                letterSpacing: "0.02em",
              }}
            >
              {data.season}
            </div>
            {data.stage && (
              <div style={{ color: "rgba(255,255,255,0.6)", fontSize: 10, marginTop: 1 }}>
                {data.stage}
              </div>
            )}
          </div>
        </div>
        <div style={{ color: "rgba(255,255,255,0.45)", fontSize: 10 }}>
          Updated {timeAgo(data.last_updated)}
        </div>
      </div>

      {/* Next match banner */}
      {data.next_match && (
        <div
          style={{
            background: "#f8f5f0",
            padding: "8px 20px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 6,
            borderBottom: "1px solid #e5e5e5",
            fontSize: 13,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                fontSize: 9,
                fontWeight: 700,
                letterSpacing: "0.1em",
                color: "#fff",
                background: "#c0392b",
                padding: "2px 6px",
                borderRadius: 3,
                textTransform: "uppercase",
              }}
            >
              Next
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: teamColor(data.next_match.team1),
                  display: "inline-block",
                  flexShrink: 0,
                }}
              />
              <strong>{data.next_match.team1}</strong>
              <span style={{ color: "#999" }}>vs</span>
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: teamColor(data.next_match.team2),
                  display: "inline-block",
                  flexShrink: 0,
                }}
              />
              <strong>{data.next_match.team2}</strong>
            </span>
          </div>
          <div style={{ color: "#888", fontSize: 11 }}>
            {formatDate(data.next_match.date)} · {data.next_match.time}
            {data.next_match.venue && (
              <span style={{ color: "#aaa" }}> · {data.next_match.venue.split(",")[0]}</span>
            )}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div
        style={{
          display: "flex",
          borderBottom: "1px solid #e5e5e5",
        }}
      >
        {(["table", "results"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              flex: 1,
              padding: "8px 0",
              fontSize: 10,
              fontWeight: 600,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              background: "transparent",
              border: "none",
              borderBottom: tab === t ? "2px solid #1a1a2e" : "2px solid transparent",
              color: tab === t ? "#1a1a2e" : "#999",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            {t === "table" ? "Points Table" : "Recent Results"}
          </button>
        ))}
      </div>

      {/* Points Table */}
      {tab === "table" && (
        <div style={{ maxHeight: 220, overflowY: "auto", WebkitOverflowScrolling: "touch" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: 13,
              fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: "1px solid #e5e5e5",
                  color: "#999",
                  fontSize: 10,
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                }}
              >
                <th style={{ padding: "7px 12px", textAlign: "left" }}>#</th>
                <th style={{ padding: "7px 6px", textAlign: "left" }}>Team</th>
                <th style={{ padding: "7px 6px", textAlign: "center" }}>P</th>
                <th style={{ padding: "7px 6px", textAlign: "center" }}>W</th>
                <th style={{ padding: "7px 6px", textAlign: "center" }}>L</th>
                <th style={{ padding: "7px 6px", textAlign: "center" }}>Pts</th>
                <th style={{ padding: "7px 12px", textAlign: "right" }}>NRR</th>
              </tr>
            </thead>
            <tbody>
              {data.standings.map((s, i) => {
                const inPlayoff = i < playoffLine;
                return (
                  <tr
                    key={s.short}
                    style={{
                      borderBottom:
                        i === playoffLine - 1
                          ? "2px dashed #c0392b"
                          : "1px solid #f0f0f0",
                      background: inPlayoff ? "rgba(39, 174, 96, 0.04)" : "transparent",
                    }}
                  >
                    <td
                      style={{
                        padding: "7px 12px",
                        color: "#bbb",
                        fontSize: 11,
                        fontWeight: 500,
                      }}
                    >
                      {i + 1}
                    </td>
                    <td style={{ padding: "7px 6px" }}>
                      <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span
                          style={{
                            width: 10,
                            height: 10,
                            borderRadius: "50%",
                            background: teamColor(s.short),
                            display: "inline-block",
                            flexShrink: 0,
                          }}
                        />
                        <span style={{ fontWeight: 600, fontSize: 13 }}>{s.short}</span>
                      </span>
                    </td>
                    <td style={{ padding: "7px 6px", textAlign: "center", color: "#666" }}>
                      {s.played}
                    </td>
                    <td
                      style={{
                        padding: "7px 6px",
                        textAlign: "center",
                        fontWeight: 600,
                        color: "#2d3436",
                      }}
                    >
                      {s.won}
                    </td>
                    <td style={{ padding: "7px 6px", textAlign: "center", color: "#999" }}>
                      {s.lost}
                    </td>
                    <td
                      style={{
                        padding: "7px 6px",
                        textAlign: "center",
                        fontWeight: 700,
                        fontSize: 14,
                        color: inPlayoff ? "#27ae60" : "#2d3436",
                      }}
                    >
                      {s.points}
                    </td>
                    <td
                      style={{
                        padding: "7px 12px",
                        textAlign: "right",
                        fontSize: 12,
                        fontFamily: "'SF Mono', 'Fira Code', monospace",
                        color: s.nrr.startsWith("-") ? "#c0392b" : "#27ae60",
                      }}
                    >
                      {s.nrr}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Recent Results */}
      {tab === "results" && data.recent_results && (
        <div style={{ padding: "4px 0" }}>
          {data.recent_results.slice(0, 3).map((r, i) => {
            const isWinner1 = r.winner === r.team1;
            const isWinner2 = r.winner === r.team2;
            return (
              <div
                key={i}
                style={{
                  padding: "10px 20px",
                  borderBottom:
                    i < Math.min((data.recent_results?.length ?? 0), 3) - 1
                      ? "1px solid #f0f0f0"
                      : "none",
                  display: "flex",
                  flexDirection: "column",
                  gap: 3,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 8,
                  }}
                >
                  <div style={{ display: "flex", flexDirection: "column", gap: 2, flex: 1 }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        fontSize: 13,
                      }}
                    >
                      <span
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          background: teamColor(r.team1),
                          display: "inline-block",
                          flexShrink: 0,
                        }}
                      />
                      <span
                        style={{
                          fontWeight: isWinner1 ? 700 : 400,
                          color: isWinner1 ? "#2d3436" : "#999",
                          minWidth: 36,
                        }}
                      >
                        {r.team1}
                      </span>
                      <span style={{ color: "#bbb", fontSize: 12, fontFamily: "monospace" }}>
                        {r.score1}
                      </span>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        fontSize: 13,
                      }}
                    >
                      <span
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          background: teamColor(r.team2),
                          display: "inline-block",
                          flexShrink: 0,
                        }}
                      />
                      <span
                        style={{
                          fontWeight: isWinner2 ? 700 : 400,
                          color: isWinner2 ? "#2d3436" : "#999",
                          minWidth: 36,
                        }}
                      >
                        {r.team2}
                      </span>
                      <span style={{ color: "#bbb", fontSize: 12, fontFamily: "monospace" }}>
                        {r.score2}
                      </span>
                    </div>
                  </div>

                  <div style={{ textAlign: "right", flexShrink: 0 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: "#2d3436" }}>
                      {r.winner} won
                    </div>
                    <div style={{ fontSize: 10, color: "#999" }}>by {r.margin}</div>
                  </div>
                </div>

                <div style={{ fontSize: 10, color: "#bbb", marginLeft: 16 }}>
                  {formatDate(r.date)}
                  {r.venue && <span> · {r.venue}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Playoffs info */}
      {data.playoffs?.final && (
        <div
          style={{
            padding: "8px 20px",
            background: "#f8f5f0",
            borderTop: "1px solid #e5e5e5",
            fontSize: 11,
            color: "#888",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <span style={{ fontWeight: 600 }}>Final:</span>
          {formatDate(data.playoffs.final.date)} · {data.playoffs.final.venue}
        </div>
      )}
    </section>
  );
}
