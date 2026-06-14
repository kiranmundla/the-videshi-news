import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

/* ── Types ── */
interface Team { name: string; code: string; flag: string; rank: number; p: number; w: number; d: number; l: number; gf: number; ga: number; pts: number; }
interface Match { id: number; group: string; date: string; time: string; tz: string; home: string; away: string; venue: string; city: string; status: string; score: string | null; home_code: string; away_code: string; }
interface WCData { tournament: string; last_updated: string; stage: string; groups: Record<string, Team[]>; matches: Match[]; dates: Record<string, string>; }

type Tab = "upcoming" | "results";

const FLAGS: Record<string, string> = {};

function etToPdt(time: string): string {
  const [h, m] = time.split(":").map(Number);
  const pdt = ((h - 3) + 24) % 24;
  return `${pdt}:${m.toString().padStart(2, "0")}`;
}

function formatMatchTime(time: string): string {
  const [h, m] = time.split(":").map(Number);
  const suffix = h >= 12 ? "PM" : "AM";
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${h12}:${m.toString().padStart(2, "0")} ${suffix}`;
}

function formatShortDate(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export default function WorldCupTracker() {
  const [data, setData] = useState<WCData | null>(null);
  const [tab, setTab] = useState<Tab>("upcoming");

  useEffect(() => {
    fetch("/data/worldcup.json")
      .then(r => r.json())
      .then(d => {
        setData(d);
        for (const teams of Object.values(d.groups)) {
          for (const t of teams as Team[]) FLAGS[t.code] = t.flag;
        }
        // Default to results tab if we have completed matches
        const hasResults = d.matches.some((m: Match) => m.status === "FT");
        if (hasResults) setTab("results");
      })
      .catch(() => {});
  }, []);

  if (!data) return null;

  const completed = data.matches.filter(m => m.status === "FT").reverse();
  const upcoming = data.matches.filter(m => m.status === "scheduled").slice(0, 4);

  return (
    <section style={{
      background: "#fff",
      border: "1px solid #e5e5e5",
      borderRadius: 16,
      overflow: "hidden",
      marginBottom: 24,
      boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
    }}>
      {/* Header */}
      <Link to="/world-cup" style={{ textDecoration: "none" }}>
        <div style={{
          background: "linear-gradient(135deg, #0a3d2e 0%, #0d1117 100%)",
          padding: "12px 20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 20 }}>⚽</span>
            <div>
              <div style={{
                fontSize: 15, fontWeight: 800, color: "#fff",
                fontFamily: "'Playfair Display', Georgia, serif",
              }}>
                FIFA World Cup 2026
              </div>
              <div style={{ fontSize: 11, color: "#c9a84c", fontWeight: 500 }}>
                {data.stage}
              </div>
            </div>
          </div>
          <span style={{ fontSize: 12, color: "#c9a84c", fontWeight: 600 }}>
            View All →
          </span>
        </div>
      </Link>

      {/* Tabs */}
      <div style={{ display: "flex", borderBottom: "1px solid #eee" }}>
        {(["results", "upcoming"] as Tab[]).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              flex: 1, padding: "8px 0",
              fontSize: 12, fontWeight: tab === t ? 700 : 500,
              color: tab === t ? "#0a3d2e" : "#999",
              background: "none", border: "none",
              borderBottom: tab === t ? "2px solid #c9a84c" : "2px solid transparent",
              cursor: "pointer", textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            {t === "results" ? "Results" : "Upcoming"}
          </button>
        ))}
      </div>

      {/* Match list */}
      <div style={{ padding: "4px 0" }}>
        {tab === "results" && completed.length === 0 && (
          <div style={{ padding: 16, textAlign: "center", color: "#999", fontSize: 13 }}>
            No results yet. The tournament has just begun!
          </div>
        )}

        {(tab === "results" ? completed.slice(0, 4) : upcoming).map((m, i, arr) => {
          const scores = m.score?.split("-").map(s => s.trim()) ?? [];
          const pdtTime = etToPdt(m.time);
          // Link finished matches to their individual recap article
          const homeSlug = m.home.toLowerCase().replace(/ /g, "-").replace(/&/g, "and");
          const awaySlug = m.away.toLowerCase().replace(/ /g, "-").replace(/&/g, "and");
          const linkTo = m.status === "FT"
            ? `/articles/world-cup-2026-${homeSlug}-vs-${awaySlug}-${m.date}`
            : "/world-cup?tab=schedule";
          return (
            <Link key={m.id} to={linkTo} style={{ textDecoration: "none", color: "inherit" }}>
            <div style={{
              padding: "10px 20px",
              borderBottom: i < arr.length - 1 ? "1px solid #f0f0f0" : "none",
              display: "flex", alignItems: "center", gap: 10,
              cursor: "pointer",
              transition: "background 0.15s",
            }}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "#f8f5f0"; }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "transparent"; }}
            >
              {/* Group badge */}
              <div style={{
                width: 28, height: 28, borderRadius: 6,
                background: "#0a3d2e", color: "#c9a84c",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 11, fontWeight: 800, flexShrink: 0,
              }}>
                {m.group}
              </div>

              {/* Teams */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 1 }}>
                  <span style={{ fontSize: 14 }}>{FLAGS[m.home_code] || ""}</span>
                  <span style={{
                    fontSize: 13,
                    fontWeight: m.status === "FT" && scores[0] > scores[1] ? 700 : 500,
                    color: m.status === "FT" && scores[0] < scores[1] ? "#bbb" : "#2d3436",
                  }}>{m.home}</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ fontSize: 14 }}>{FLAGS[m.away_code] || ""}</span>
                  <span style={{
                    fontSize: 13,
                    fontWeight: m.status === "FT" && scores[1] > scores[0] ? 700 : 500,
                    color: m.status === "FT" && scores[1] < scores[0] ? "#bbb" : "#2d3436",
                  }}>{m.away}</span>
                </div>
              </div>

              {/* Score / Time */}
              <div style={{ textAlign: "center", flexShrink: 0, minWidth: 50 }}>
                {m.status === "FT" ? (
                  <>
                    <div style={{ fontSize: 17, fontWeight: 800, color: "#0a3d2e", fontFamily: "monospace" }}>
                      {m.score}
                    </div>
                    <div style={{ fontSize: 9, color: "#999", fontWeight: 600 }}>FT</div>
                  </>
                ) : (
                  <>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#0a3d2e" }}>
                      {formatMatchTime(pdtTime)}
                    </div>
                    <div style={{ fontSize: 9, color: "#999" }}>
                      {formatShortDate(m.date)}
                    </div>
                  </>
                )}
              </div>
            </div>
            </Link>
          );
        })}
      </div>

      {/* Footer link */}
      <Link to="/world-cup" style={{ textDecoration: "none" }}>
        <div style={{
          padding: "8px 20px",
          background: "#f8f5f0",
          borderTop: "1px solid #eee",
          fontSize: 12, color: "#c9a84c", fontWeight: 600,
          textAlign: "center",
        }}>
          Full Schedule, Groups & Highlights →
        </div>
      </Link>
    </section>
  );
}
