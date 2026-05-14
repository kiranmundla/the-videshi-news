import { useEffect, useState } from "react";

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

function formatValue(symbol: string, value: number): string {
  if (symbol === "USDINR") return value.toFixed(2);
  if (symbol === "GOLD" || symbol === "SILVER") return value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
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

export default function MarketTicker() {
  const [data, setData] = useState<MarketData | null>(null);

  useEffect(() => {
    fetch("/data/market-indices.json")
      .then((r) => { if (!r.ok) throw new Error("not found"); return r.json(); })
      .then((d: MarketData) => setData(d))
      .catch(() => {});
  }, []);

  if (!data || data.indices.length === 0) return null;

  const positive = "#10b981";
  const negative = "#ef4444";

  return (
    <div style={{
      background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
      borderRadius: 8,
      padding: "12px 0",
      marginBottom: 24,
      overflow: "hidden",
    }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        overflowX: "auto",
        gap: 0,
        paddingLeft: 16,
        paddingRight: 16,
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
          const isUp = idx.change >= 0;
          const color = isUp ? positive : negative;
          const arrow = isUp ? "▲" : "▼";

          return (
            <div key={idx.symbol} style={{
              flexShrink: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              padding: "4px 14px",
              borderRight: i < data.indices.length - 1 ? "1px solid rgba(255,255,255,0.08)" : "none",
              minWidth: 120,
            }}>
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

      {/* Hide scrollbar via inline style workaround */}
      <style>{`
        .market-ticker-scroll::-webkit-scrollbar { display: none; }
      `}</style>
    </div>
  );
}
