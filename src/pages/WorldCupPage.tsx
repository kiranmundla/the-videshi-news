import { useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";

/* ── Types ── */
interface Team {
  name: string; code: string; flag: string; rank: number;
  p: number; w: number; d: number; l: number; gf: number; ga: number; pts: number;
}
interface Match {
  id: number; group: string; date: string; time: string; tz: string;
  home: string; away: string; venue: string; city: string;
  status: string; score: string | null; home_code: string; away_code: string;
}
interface Highlight {
  platform: string; url: string; account: string; caption: string; date: string;
}
interface NRIVenue {
  venue: string; city: string; matches: number; note: string;
}
interface WCData {
  tournament: string; last_updated: string; stage: string; hosts: string;
  dates: Record<string, string>;
  groups: Record<string, Team[]>;
  matches: Match[];
  knockout: Record<string, any>;
  highlights: Highlight[];
  tv: { english: string; spanish: string };
  nri_watch: { headline: string; description: string; key_venues_near_desi_hubs: NRIVenue[] };
  final_venue: string;
}

type Tab = "schedule" | "groups" | "highlights" | "nri";

/* ── Flag lookup for team codes ── */
const FLAGS: Record<string, string> = {};

/* ── Helpers ── */
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

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

function groupMatchesByDate(matches: Match[]): Record<string, Match[]> {
  const grouped: Record<string, Match[]> = {};
  for (const m of matches) {
    if (!grouped[m.date]) grouped[m.date] = [];
    grouped[m.date].push(m);
  }
  return grouped;
}

/* ── Styles ── */
const COLORS = {
  darkGreen: "#0a3d2e",
  green: "#1a6b4a",
  gold: "#c9a84c",
  lightGold: "#f5e6b8",
  darkBg: "#0d1117",
  cardBg: "#161b22",
  white: "#ffffff",
  muted: "#8b949e",
  border: "#21262d",
  live: "#e74c3c",
};

export default function WorldCupPage() {
  const [data, setData] = useState<WCData | null>(null);
  const [tab, setTab] = useState<Tab>("schedule");
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/data/worldcup.json")
      .then(r => r.json())
      .then(d => {
        setData(d);
        // Build flags lookup
        for (const teams of Object.values(d.groups)) {
          for (const t of teams as Team[]) FLAGS[t.code] = t.flag;
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="min-h-screen flex flex-col">
      <Masthead />
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
        <div style={{ width: 32, height: 32, border: `3px solid ${COLORS.gold}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  );

  if (!data) return null;

  const now = new Date();
  const byDate = groupMatchesByDate(data.matches);
  const dates = Object.keys(byDate).sort();

  // Find today or next match day
  const todayStr = now.toISOString().split("T")[0];
  const todayIdx = dates.findIndex(d => d >= todayStr);
  const startIdx = todayIdx >= 0 ? todayIdx : 0;

  const tabs: { key: Tab; label: string; icon: string }[] = [
    { key: "schedule", label: "Schedule", icon: "📅" },
    { key: "groups", label: "Groups", icon: "🏆" },
    { key: "highlights", label: "Highlights", icon: "🎬" },
    { key: "nri", label: "NRI Guide", icon: "🇮🇳" },
  ];

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "#fafafa" }}>
      <Helmet>
        <title>FIFA World Cup 2026 — The Videshi</title>
        <meta name="description" content="Complete FIFA World Cup 2026 coverage: live scores, group standings, match schedule, highlight videos, and an NRI guide to attending matches across the US, Canada & Mexico." />
        <link rel="canonical" href="https://www.thevideshi.com/world-cup" />
      </Helmet>
      <Masthead />

      {/* ── Hero Banner ── */}
      <div style={{
        background: `linear-gradient(135deg, ${COLORS.darkGreen} 0%, ${COLORS.darkBg} 100%)`,
        padding: "40px 20px 32px",
        textAlign: "center",
        position: "relative",
        overflow: "hidden",
      }}>
        {/* Subtle pattern overlay */}
        <div style={{
          position: "absolute", inset: 0, opacity: 0.05,
          backgroundImage: "repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,0.1) 35px, rgba(255,255,255,0.1) 70px)",
        }} />
        <div style={{ position: "relative", zIndex: 1, maxWidth: 800, margin: "0 auto" }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>⚽</div>
          <h1 style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: "clamp(28px, 5vw, 44px)",
            fontWeight: 800,
            color: COLORS.white,
            margin: "0 0 8px",
            letterSpacing: "-0.02em",
          }}>
            FIFA World Cup 2026
          </h1>
          <p style={{
            fontSize: "clamp(14px, 2.5vw, 18px)",
            color: COLORS.gold,
            fontWeight: 600,
            margin: "0 0 16px",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}>
            {data.hosts} · {data.dates.start.split("-").slice(1).join("/")} – {data.dates.end.split("-").slice(1).join("/")}
          </p>
          <div style={{
            display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 16,
            fontSize: 13, color: COLORS.lightGold,
          }}>
            <span>🏟️ 16 Venues</span>
            <span>🌍 48 Teams</span>
            <span>⚽ 104 Matches</span>
            <span>📺 {data.tv.english.split("(")[0].trim()}</span>
          </div>
          <p style={{
            fontSize: 13, color: COLORS.gold, marginTop: 12,
            fontStyle: "italic", opacity: 0.9,
          }}>
            {data.stage}
          </p>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div style={{
        position: "sticky", top: 40, zIndex: 20,
        background: "#fff", borderBottom: `1px solid ${COLORS.border}`,
        display: "flex", justifyContent: "center", gap: 0,
        overflowX: "auto", WebkitOverflowScrolling: "touch",
      }}>
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            style={{
              padding: "12px 20px",
              fontSize: 14,
              fontWeight: tab === t.key ? 700 : 500,
              color: tab === t.key ? COLORS.darkGreen : COLORS.muted,
              background: "none",
              border: "none",
              borderBottom: tab === t.key ? `3px solid ${COLORS.gold}` : "3px solid transparent",
              cursor: "pointer",
              whiteSpace: "nowrap",
              transition: "all 0.2s",
            }}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      <main style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px", width: "100%" }}>

        {/* ═══ SCHEDULE TAB ═══ */}
        {tab === "schedule" && (
          <div>
            {dates.slice(Math.max(0, startIdx - 1)).map(date => {
              const matches = byDate[date];
              const isToday = date === todayStr;
              const isPast = date < todayStr;
              return (
                <div key={date} style={{ marginBottom: 28 }}>
                  <h2 style={{
                    fontFamily: "'Playfair Display', Georgia, serif",
                    fontSize: 18, fontWeight: 700,
                    color: isToday ? COLORS.darkGreen : "#2d3436",
                    margin: "0 0 12px",
                    display: "flex", alignItems: "center", gap: 8,
                  }}>
                    {isToday && <span style={{
                      background: COLORS.live, color: "#fff", fontSize: 10,
                      padding: "2px 8px", borderRadius: 4, fontWeight: 700,
                      fontFamily: "system-ui",
                    }}>TODAY</span>}
                    {formatDate(date)}
                  </h2>
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {matches.map(m => (
                      <MatchCard key={m.id} match={m} isPast={isPast} isToday={isToday} />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ═══ GROUPS TAB ═══ */}
        {tab === "groups" && (
          <div>
            {/* Group selector pills */}
            <div style={{
              display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 20, justifyContent: "center",
            }}>
              <button
                onClick={() => setSelectedGroup(null)}
                style={{
                  padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600,
                  border: `1px solid ${selectedGroup === null ? COLORS.gold : "#ddd"}`,
                  background: selectedGroup === null ? COLORS.gold : "#fff",
                  color: selectedGroup === null ? "#fff" : "#555",
                  cursor: "pointer",
                }}
              >All Groups</button>
              {Object.keys(data.groups).map(g => (
                <button
                  key={g}
                  onClick={() => setSelectedGroup(g)}
                  style={{
                    padding: "6px 12px", borderRadius: 20, fontSize: 13, fontWeight: 600,
                    border: `1px solid ${selectedGroup === g ? COLORS.gold : "#ddd"}`,
                    background: selectedGroup === g ? COLORS.gold : "#fff",
                    color: selectedGroup === g ? "#fff" : "#555",
                    cursor: "pointer", minWidth: 36,
                  }}
                >{g}</button>
              ))}
            </div>

            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
              gap: 16,
            }}>
              {Object.entries(data.groups)
                .filter(([g]) => !selectedGroup || g === selectedGroup)
                .map(([group, teams]) => (
                  <GroupTable key={group} group={group} teams={teams} />
                ))}
            </div>
          </div>
        )}

        {/* ═══ HIGHLIGHTS TAB ═══ */}
        {tab === "highlights" && (
          <div>
            <p style={{ color: COLORS.muted, fontSize: 14, marginBottom: 20, textAlign: "center" }}>
              Official highlights from @fifaworldcup and country football accounts
            </p>
            {data.highlights.length === 0 ? (
              <div style={{ textAlign: "center", padding: 40, color: COLORS.muted }}>
                <p style={{ fontSize: 48, marginBottom: 12 }}>⚽</p>
                <p>Highlights will appear here as matches are played.</p>
              </div>
            ) : (
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
                gap: 16,
              }}>
                {data.highlights.map((h, i) => (
                  <HighlightCard key={i} highlight={h} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ═══ NRI GUIDE TAB ═══ */}
        {tab === "nri" && (
          <div>
            <div style={{
              background: `linear-gradient(135deg, ${COLORS.darkGreen}, #1a4a3a)`,
              borderRadius: 16, padding: "32px 24px", marginBottom: 24, color: "#fff",
            }}>
              <h2 style={{
                fontFamily: "'Playfair Display', Georgia, serif",
                fontSize: 28, fontWeight: 700, margin: "0 0 12px",
                color: COLORS.lightGold,
              }}>
                🇮🇳 {data.nri_watch.headline}
              </h2>
              <p style={{ fontSize: 15, lineHeight: 1.7, color: "rgba(255,255,255,0.85)", margin: 0 }}>
                {data.nri_watch.description}
              </p>
            </div>

            <h3 style={{
              fontFamily: "'Playfair Display', Georgia, serif",
              fontSize: 20, fontWeight: 700, marginBottom: 16,
            }}>
              🏟️ Venues Near Major Desi Communities
            </h3>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
              gap: 12,
            }}>
              {data.nri_watch.key_venues_near_desi_hubs.map((v, i) => (
                <div key={i} style={{
                  background: "#fff", border: "1px solid #e5e5e5", borderRadius: 12,
                  padding: 16, transition: "box-shadow 0.2s",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <h4 style={{ fontSize: 15, fontWeight: 700, margin: "0 0 4px", color: COLORS.darkGreen }}>
                        {v.venue}
                      </h4>
                      <p style={{ fontSize: 13, color: COLORS.muted, margin: 0 }}>{v.city}</p>
                    </div>
                    <span style={{
                      background: COLORS.lightGold, color: COLORS.darkGreen,
                      padding: "3px 10px", borderRadius: 12, fontSize: 12, fontWeight: 700,
                    }}>
                      {v.matches} matches
                    </span>
                  </div>
                  <p style={{ fontSize: 13, color: "#555", margin: "8px 0 0", lineHeight: 1.5 }}>
                    {v.note}
                  </p>
                </div>
              ))}
            </div>

            <div style={{
              marginTop: 24, padding: 20, background: "#fff",
              border: "1px solid #e5e5e5", borderRadius: 12,
            }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 8px" }}>📺 How to Watch</h3>
              <p style={{ fontSize: 14, color: "#555", margin: "0 0 4px" }}>
                <strong>English:</strong> {data.tv.english}
              </p>
              <p style={{ fontSize: 14, color: "#555", margin: 0 }}>
                <strong>Español:</strong> {data.tv.spanish}
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Updated timestamp */}
      <div style={{ textAlign: "center", padding: "8px 0 24px", fontSize: 11, color: COLORS.muted }}>
        Last updated: {new Date(data.last_updated).toLocaleString()} · Data refreshes automatically
      </div>

      <SiteFooter />
    </div>
  );
}

/* ── Match Card ── */
function MatchCard({ match, isPast, isToday }: { match: Match; isPast: boolean; isToday: boolean }) {
  const isFinished = match.status === "FT";
  const scores = match.score?.split("-").map(s => s.trim()) ?? [];
  const homeFlag = FLAGS[match.home_code] || "";
  const awayFlag = FLAGS[match.away_code] || "";

  // Convert ET to PDT for display
  const pdtTime = etToPdt(match.time);

  return (
    <div style={{
      background: "#fff",
      border: `1px solid ${isToday ? COLORS.gold + "66" : "#e5e5e5"}`,
      borderRadius: 12,
      padding: "12px 16px",
      display: "flex",
      alignItems: "center",
      gap: 12,
      boxShadow: isToday ? `0 0 0 1px ${COLORS.gold}33` : "none",
    }}>
      {/* Group badge */}
      <div style={{
        width: 36, height: 36, borderRadius: 8,
        background: COLORS.darkGreen, color: COLORS.gold,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 13, fontWeight: 800, flexShrink: 0,
      }}>
        {match.group}
      </div>

      {/* Teams & score */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
              <span style={{ fontSize: 16 }}>{homeFlag}</span>
              <span style={{
                fontSize: 14, fontWeight: isFinished && scores[0] > scores[1] ? 700 : 500,
                color: isFinished && scores[0] < scores[1] ? COLORS.muted : "#2d3436",
                overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
              }}>{match.home}</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 16 }}>{awayFlag}</span>
              <span style={{
                fontSize: 14, fontWeight: isFinished && scores[1] > scores[0] ? 700 : 500,
                color: isFinished && scores[1] < scores[0] ? COLORS.muted : "#2d3436",
                overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
              }}>{match.away}</span>
            </div>
          </div>

          {/* Score or time */}
          <div style={{ textAlign: "center", flexShrink: 0, minWidth: 60 }}>
            {isFinished ? (
              <>
                <div style={{
                  fontSize: 20, fontWeight: 800, color: COLORS.darkGreen,
                  fontFamily: "'SF Mono', monospace",
                }}>
                  {match.score}
                </div>
                <div style={{ fontSize: 10, color: COLORS.muted, fontWeight: 600 }}>FT</div>
              </>
            ) : (
              <>
                <div style={{ fontSize: 15, fontWeight: 700, color: COLORS.darkGreen }}>
                  {formatMatchTime(pdtTime)}
                </div>
                <div style={{ fontSize: 10, color: COLORS.muted }}>PDT</div>
              </>
            )}
          </div>
        </div>
        <div style={{ fontSize: 11, color: COLORS.muted, marginTop: 4 }}>
          📍 {match.venue}, {match.city}
        </div>
      </div>
    </div>
  );
}

/* ── Group Table ── */
function GroupTable({ group, teams }: { group: string; teams: Team[] }) {
  const sorted = [...teams].sort((a, b) => {
    if (b.pts !== a.pts) return b.pts - a.pts;
    const gdA = a.gf - a.ga, gdB = b.gf - b.ga;
    if (gdB !== gdA) return gdB - gdA;
    return b.gf - a.gf;
  });

  return (
    <div style={{
      background: "#fff", border: "1px solid #e5e5e5", borderRadius: 12,
      overflow: "hidden",
    }}>
      <div style={{
        background: COLORS.darkGreen, padding: "10px 16px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <span style={{ color: COLORS.gold, fontSize: 15, fontWeight: 800 }}>
          Group {group}
        </span>
        <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 11 }}>
          {sorted.map(t => t.flag).join(" ")}
        </span>
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #eee" }}>
            <th style={{ padding: "8px 12px", textAlign: "left", fontWeight: 600, color: COLORS.muted, fontSize: 11 }}>Team</th>
            <th style={{ padding: "8px 6px", textAlign: "center", fontWeight: 600, color: COLORS.muted, fontSize: 11 }}>P</th>
            <th style={{ padding: "8px 6px", textAlign: "center", fontWeight: 600, color: COLORS.muted, fontSize: 11 }}>W</th>
            <th style={{ padding: "8px 6px", textAlign: "center", fontWeight: 600, color: COLORS.muted, fontSize: 11 }}>D</th>
            <th style={{ padding: "8px 6px", textAlign: "center", fontWeight: 600, color: COLORS.muted, fontSize: 11 }}>L</th>
            <th style={{ padding: "8px 6px", textAlign: "center", fontWeight: 600, color: COLORS.muted, fontSize: 11 }}>GD</th>
            <th style={{ padding: "8px 12px", textAlign: "center", fontWeight: 600, color: COLORS.muted, fontSize: 11 }}>Pts</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((t, i) => {
            const qualifies = i < 2;
            return (
              <tr key={t.code} style={{
                borderBottom: i < sorted.length - 1 ? "1px solid #f0f0f0" : "none",
                background: qualifies && t.pts > 0 ? "#f0faf5" : "transparent",
              }}>
                <td style={{ padding: "8px 12px" }}>
                  <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 16 }}>{t.flag}</span>
                    <span style={{ fontWeight: 600 }}>{t.name}</span>
                    <span style={{ fontSize: 10, color: COLORS.muted }}>#{t.rank}</span>
                  </span>
                </td>
                <td style={{ padding: "8px 6px", textAlign: "center", color: "#666" }}>{t.p}</td>
                <td style={{ padding: "8px 6px", textAlign: "center", fontWeight: 600 }}>{t.w}</td>
                <td style={{ padding: "8px 6px", textAlign: "center", color: "#666" }}>{t.d}</td>
                <td style={{ padding: "8px 6px", textAlign: "center", color: "#999" }}>{t.l}</td>
                <td style={{ padding: "8px 6px", textAlign: "center", color: (t.gf - t.ga) > 0 ? "#27ae60" : (t.gf - t.ga) < 0 ? "#c0392b" : "#666", fontWeight: 600 }}>
                  {(t.gf - t.ga) > 0 ? "+" : ""}{t.gf - t.ga}
                </td>
                <td style={{
                  padding: "8px 12px", textAlign: "center",
                  fontWeight: 800, fontSize: 15,
                  color: t.pts > 0 ? COLORS.darkGreen : "#999",
                }}>{t.pts}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/* ── Highlight Card — native embeds for Instagram/Threads, link cards for others ── */
function HighlightCard({ highlight }: { highlight: Highlight }) {
  const isInstagram = highlight.platform === "instagram";
  const isThreads = highlight.platform === "threads";

  if (isInstagram || isThreads) {
    return <SocialEmbed highlight={highlight} />;
  }

  // Fallback card for YouTube, Twitter, etc.
  const platformIcon = highlight.platform === "youtube" ? "▶️" : "🐦";
  const platformLabel = highlight.platform.charAt(0).toUpperCase() + highlight.platform.slice(1);

  return (
    <a
      href={highlight.url}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        background: "#fff", border: "1px solid #e5e5e5", borderRadius: 12,
        padding: 16, textDecoration: "none", color: "inherit",
        display: "block", transition: "box-shadow 0.2s, transform 0.2s",
      }}
      onMouseEnter={e => { (e.currentTarget as HTMLElement).style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)"; }}
      onMouseLeave={e => { (e.currentTarget as HTMLElement).style.boxShadow = "none"; }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontSize: 18 }}>{platformIcon}</span>
        <span style={{ fontSize: 13, fontWeight: 600, color: COLORS.darkGreen }}>{platformLabel}</span>
        <span style={{ fontSize: 12, color: COLORS.muted, marginLeft: "auto" }}>{highlight.account}</span>
      </div>
      <p style={{ fontSize: 14, color: "#2d3436", margin: "0 0 8px", lineHeight: 1.5, fontWeight: 500 }}>
        {highlight.caption}
      </p>
      <div style={{ fontSize: 11, color: COLORS.muted }}>
        {formatDate(highlight.date)} · Tap to watch →
      </div>
    </a>
  );
}

/* ── Native Instagram / Threads embed ── */
function SocialEmbed({ highlight }: { highlight: Highlight }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    // Load Instagram embed script if not already present
    const scriptId = "instagram-embed-js";
    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = "https://www.instagram.com/embed.js";
      script.async = true;
      script.onload = () => {
        if ((window as any).instgrm?.Embeds) {
          (window as any).instgrm.Embeds.process();
        }
        setLoaded(true);
      };
      document.body.appendChild(script);
    } else {
      // Script already loaded, just process this new embed
      setTimeout(() => {
        if ((window as any).instgrm?.Embeds) {
          (window as any).instgrm.Embeds.process();
        }
        setLoaded(true);
      }, 100);
    }
  }, []);

  // Re-process whenever component mounts (e.g. tab switch)
  useEffect(() => {
    if (loaded && (window as any).instgrm?.Embeds) {
      const timer = setTimeout(() => {
        (window as any).instgrm.Embeds.process(containerRef.current);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [loaded]);

  // Clean permalink — ensure it ends with /
  const permalink = highlight.url.endsWith("/") ? highlight.url : highlight.url + "/";

  return (
    <div ref={containerRef} style={{ minHeight: 400 }}>
      <blockquote
        className="instagram-media"
        data-instgrm-permalink={permalink}
        data-instgrm-version="14"
        data-instgrm-captioned=""
        style={{
          background: "#FFF",
          border: 0,
          borderRadius: 12,
          boxShadow: "0 0 1px 0 rgba(0,0,0,0.5), 0 1px 10px 0 rgba(0,0,0,0.15)",
          margin: "0 auto",
          maxWidth: 540,
          minWidth: 280,
          padding: 0,
          width: "100%",
        }}
      >
        <div style={{ padding: 16 }}>
          <a
            href={permalink}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: COLORS.darkGreen,
              fontWeight: 600,
              fontSize: 14,
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span style={{ fontSize: 18 }}>{highlight.platform === "instagram" ? "📸" : "🧵"}</span>
            {highlight.caption}
          </a>
          <p style={{ color: COLORS.muted, fontSize: 12, marginTop: 8 }}>
            {highlight.account} · {formatDate(highlight.date)}
          </p>
        </div>
      </blockquote>
    </div>
  );
}
