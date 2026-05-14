import { useEffect, useState, useCallback } from "react";

interface IndexData {
  symbol: string;
  name: string;
  flag: string;
  value: number;
  change: number;
  change_pct: number;
}

interface MarketData {
  last_updated: string;
  indices: IndexData[];
}

interface ChartPoint {
  t: string;
  v: number;
}

interface ChartData {
  charts: Record<string, Record<string, ChartPoint[]>>;
}

type Timeframe = "1D" | "1W" | "1M" | "1Y";

function formatValue(symbol: string, value: number): string {
  if (symbol === "USDINR") return value.toFixed(2);
  return value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatAxisValue(value: number): string {
  if (value >= 10000) return (value / 1000).toFixed(1) + "K";
  if (value >= 1000) return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  return value.toFixed(2);
}

function formatTimeLabel(t: string, tf: Timeframe): string {
  const d = new Date(t);
  if (tf === "1D") return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
  if (tf === "1W") return d.toLocaleDateString("en-US", { weekday: "short" });
  if (tf === "1M") return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  return d.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
}

function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

const CHART_W = 700;
const CHART_H = 200;
const PAD_L = 60;
const PAD_R = 16;
const PAD_T = 16;
const PAD_B = 28;
const PLOT_W = CHART_W - PAD_L - PAD_R;
const PLOT_H = CHART_H - PAD_T - PAD_B;

function MiniChart({ data, timeframe, color }: { data: ChartPoint[]; timeframe: Timeframe; color: string }) {
  if (!data || data.length < 2) {
    return (
      <div style={{ color: "rgba(255,255,255,0.3)", textAlign: "center", padding: 40, fontSize: 13 }}>
        No chart data available for this timeframe
      </div>
    );
  }

  const values = data.map((d) => d.v);
  const rawMin = Math.min(...values);
  const rawMax = Math.max(...values);
  const range = rawMax - rawMin || 1;
  const minVal = rawMin - range * 0.05;
  const maxVal = rawMax + range * 0.05;
  const valRange = maxVal - minVal;

  const toX = (i: number) => PAD_L + (i / (data.length - 1)) * PLOT_W;
  const toY = (v: number) => PAD_T + PLOT_H - ((v - minVal) / valRange) * PLOT_H;

  const linePoints = data.map((d, i) => `${toX(i)},${toY(d.v)}`).join(" ");
  const areaPoints = `${toX(0)},${PAD_T + PLOT_H} ${linePoints} ${toX(data.length - 1)},${PAD_T + PLOT_H}`;

  // Grid lines (4 horizontal)
  const gridCount = 4;
  const gridLines = Array.from({ length: gridCount }, (_, i) => {
    const frac = i / (gridCount - 1);
    const val = minVal + frac * valRange;
    const y = PAD_T + PLOT_H - frac * PLOT_H;
    return { y, val };
  });

  // Time labels (5 evenly spaced)
  const labelCount = 5;
  const timeLabels = Array.from({ length: labelCount }, (_, i) => {
    const idx = Math.round((i / (labelCount - 1)) * (data.length - 1));
    return { x: toX(idx), label: formatTimeLabel(data[idx].t, timeframe) };
  });

  const gradId = `grad-${timeframe}`;

  return (
    <svg
      viewBox={`0 0 ${CHART_W} ${CHART_H}`}
      style={{ width: "100%", maxWidth: CHART_W, height: "auto", display: "block" }}
    >
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.18} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>

      {/* Grid lines + Y labels */}
      {gridLines.map((g, i) => (
        <g key={i}>
          <line x1={PAD_L} y1={g.y} x2={CHART_W - PAD_R} y2={g.y} stroke="rgba(255,255,255,0.08)" strokeDasharray="4 4" />
          <text x={PAD_L - 8} y={g.y + 4} textAnchor="end" fill="rgba(255,255,255,0.35)" fontSize="10" fontFamily="system-ui">
            {formatAxisValue(g.val)}
          </text>
        </g>
      ))}

      {/* Time labels */}
      {timeLabels.map((tl, i) => (
        <text key={i} x={tl.x} y={CHART_H - 4} textAnchor="middle" fill="rgba(255,255,255,0.35)" fontSize="9" fontFamily="system-ui">
          {tl.label}
        </text>
      ))}

      {/* Area fill */}
      <polygon points={areaPoints} fill={`url(#${gradId})`} />

      {/* Line */}
      <polyline points={linePoints} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" />

      {/* Last point dot */}
      <circle cx={toX(data.length - 1)} cy={toY(data[data.length - 1].v)} r="3.5" fill={color} />
    </svg>
  );
}

export default function MarketTicker() {
  const [data, setData] = useState<MarketData | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<Timeframe>("1M");
  const [hoveredSymbol, setHoveredSymbol] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/market-indices.json")
      .then((r) => { if (!r.ok) throw new Error("not found"); return r.json(); })
      .then((d: MarketData) => setData(d))
      .catch(() => {});
  }, []);

  const loadCharts = useCallback(() => {
    if (chartData) return;
    fetch("/data/market-charts.json")
      .then((r) => { if (!r.ok) throw new Error("not found"); return r.json(); })
      .then((d: ChartData) => setChartData(d))
      .catch(() => {});
  }, [chartData]);

  const handleClick = (symbol: string) => {
    if (selectedSymbol === symbol) {
      setSelectedSymbol(null);
    } else {
      setSelectedSymbol(symbol);
      loadCharts();
    }
  };

  if (!data || data.indices.length === 0) return null;

  const positive = "#10b981";
  const negative = "#ef4444";

  const selectedIdx = data.indices.find((idx) => idx.symbol === selectedSymbol);
  const chartPoints = chartData?.charts?.[selectedSymbol ?? ""]?.[timeframe] ?? [];
  const isUp = selectedIdx ? selectedIdx.change >= 0 : true;
  const chartColor = isUp ? positive : negative;

  // For 1D check if data goes up overall
  const chartIsUp = chartPoints.length >= 2 ? chartPoints[chartPoints.length - 1].v >= chartPoints[0].v : isUp;
  const lineColor = chartIsUp ? positive : negative;

  const timeframes: Timeframe[] = ["1D", "1W", "1M", "1Y"];

  return (
    <div style={{
      background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
      borderRadius: 8,
      marginBottom: 24,
      overflow: "hidden",
    }}>
      {/* Ticker row */}
      <div style={{
        display: "flex",
        alignItems: "center",
        overflowX: "auto",
        gap: 0,
        padding: "12px 16px",
        scrollbarWidth: "none",
        msOverflowStyle: "none" as React.CSSProperties["msOverflowStyle"],
      }} className="market-ticker-scroll">
        {/* Market label */}
        <div style={{
          flexShrink: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          paddingRight: 16,
          borderRight: "1px solid rgba(255,255,255,0.12)",
          marginRight: 8,
        }}>
          <span style={{
            fontSize: 9,
            fontWeight: 700,
            letterSpacing: "0.15em",
            color: "rgba(255,255,255,0.45)",
            textTransform: "uppercase",
          }}>MARKETS</span>
          <span style={{
            fontSize: 8,
            color: "rgba(255,255,255,0.3)",
            marginTop: 2,
          }}>{timeAgo(data.last_updated)}</span>
        </div>

        {data.indices.map((idx, i) => {
          const idxUp = idx.change >= 0;
          const color = idxUp ? positive : negative;
          const arrow = idxUp ? "▲" : "▼";
          const isSelected = selectedSymbol === idx.symbol;
          const isHovered = hoveredSymbol === idx.symbol;

          return (
            <div
              key={idx.symbol}
              onClick={() => handleClick(idx.symbol)}
              onMouseEnter={() => setHoveredSymbol(idx.symbol)}
              onMouseLeave={() => setHoveredSymbol(null)}
              style={{
                flexShrink: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                padding: "4px 14px",
                borderRight: i < data.indices.length - 1 ? "1px solid rgba(255,255,255,0.08)" : "none",
                minWidth: 120,
                cursor: "pointer",
                borderRadius: 6,
                background: isSelected
                  ? "rgba(255,255,255,0.1)"
                  : isHovered
                    ? "rgba(255,255,255,0.05)"
                    : "transparent",
                transition: "background 0.2s",
              }}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                marginBottom: 2,
              }}>
                <span style={{ fontSize: 12 }}>{idx.flag}</span>
                <span style={{
                  fontSize: 10,
                  fontWeight: 600,
                  color: "rgba(255,255,255,0.55)",
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                }}>{idx.name}</span>
              </div>
              <div style={{
                display: "flex",
                alignItems: "baseline",
                gap: 6,
              }}>
                <span style={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: "#ffffff",
                  fontVariantNumeric: "tabular-nums",
                }}>{formatValue(idx.symbol, idx.value)}</span>
                <span style={{
                  fontSize: 10,
                  fontWeight: 600,
                  color,
                  fontVariantNumeric: "tabular-nums",
                }}>{arrow} {Math.abs(idx.change_pct).toFixed(2)}%</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Expandable chart panel */}
      <div style={{
        maxHeight: selectedSymbol ? 320 : 0,
        overflow: "hidden",
        transition: "max-height 0.35s ease",
      }}>
        {selectedIdx && (
          <div style={{
            borderTop: "1px solid rgba(255,255,255,0.08)",
            padding: "16px 20px 20px",
          }}>
            {/* Header row */}
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 12,
            }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
                <span style={{
                  fontSize: 16,
                  fontWeight: 700,
                  color: "#ffffff",
                }}>{selectedIdx.flag} {selectedIdx.name}</span>
                <span style={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: "#ffffff",
                  fontVariantNumeric: "tabular-nums",
                }}>{formatValue(selectedIdx.symbol, selectedIdx.value)}</span>
                <span style={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: isUp ? positive : negative,
                }}>
                  {isUp ? "▲" : "▼"} {Math.abs(selectedIdx.change).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({Math.abs(selectedIdx.change_pct).toFixed(2)}%)
                </span>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                {/* Timeframe pills */}
                <div style={{ display: "flex", gap: 4 }}>
                  {timeframes.map((tf) => (
                    <button
                      key={tf}
                      onClick={(e) => { e.stopPropagation(); setTimeframe(tf); }}
                      style={{
                        padding: "3px 10px",
                        borderRadius: 12,
                        border: "none",
                        fontSize: 11,
                        fontWeight: 600,
                        cursor: "pointer",
                        background: timeframe === tf ? "rgba(255,255,255,0.18)" : "transparent",
                        color: timeframe === tf ? "#ffffff" : "rgba(255,255,255,0.4)",
                        transition: "all 0.2s",
                      }}
                    >
                      {tf}
                    </button>
                  ))}
                </div>

                {/* Close button */}
                <button
                  onClick={(e) => { e.stopPropagation(); setSelectedSymbol(null); }}
                  style={{
                    background: "rgba(255,255,255,0.08)",
                    border: "none",
                    color: "rgba(255,255,255,0.5)",
                    fontSize: 14,
                    cursor: "pointer",
                    borderRadius: "50%",
                    width: 24,
                    height: 24,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    lineHeight: 1,
                  }}
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Chart */}
            <MiniChart data={chartPoints} timeframe={timeframe} color={lineColor} />
          </div>
        )}
      </div>

      <style>{`
        .market-ticker-scroll::-webkit-scrollbar { display: none; }
      `}</style>
    </div>
  );
}
