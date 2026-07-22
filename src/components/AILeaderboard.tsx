import { useEffect, useState } from "react";
import "./AILeaderboard.css";

interface AIModel {
  rank: number;
  model: string;
  model_key: string;
  company: string;
  org_key: string;
  rating: number;
  votes: number;
  change: number | null;
  license: string;
  indian_leader?: string;
}

interface AIRankings {
  updated_at: string;
  source: string;
  source_url: string;
  methodology: string;
  models: AIModel[];
}

/* ── Org logos as colored initials ── */
const ORG_COLORS: Record<string, string> = {
  anthropic: "#d97706",
  openai: "#10a37f",
  google: "#4285f4",
  meta: "#0668E1",
  moonshot: "#6366f1",
  deepseek: "#0ea5e9",
  mistral: "#ff7000",
  xai: "#1a1a1a",
};

function OrgBadge({ org }: { org: string }) {
  const bg = ORG_COLORS[org] || "#6b7280";
  const letter = org.charAt(0).toUpperCase();
  return (
    <span className="ai-lb-org-badge" style={{ background: bg }}>
      {letter}
    </span>
  );
}

/* ── Rank change indicator ── */
function RankChange({ change }: { change: number | null }) {
  if (change === null) return <span className="ai-lb-change ai-lb-new">NEW</span>;
  if (change > 0) return <span className="ai-lb-change ai-lb-up">▲{change}</span>;
  if (change < 0) return <span className="ai-lb-change ai-lb-down">▼{Math.abs(change)}</span>;
  return <span className="ai-lb-change ai-lb-same">—</span>;
}

/* ── Format vote count ── */
function fmtVotes(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

/* ── Main component ── */
export default function AILeaderboard() {
  const [data, setData] = useState<AIRankings | null>(null);

  useEffect(() => {
    fetch("/data/ai-rankings.json")
      .then((r) => r.json())
      .then(setData)
      .catch(() => {});
  }, []);

  if (!data || !data.models.length) return null;

  const updatedDate = new Date(data.updated_at + "T00:00:00Z").toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <section className="ai-lb-section">
      <div className="ai-lb-header">
        <div className="ai-lb-title-row">
          <span className="ai-lb-icon">🏆</span>
          <h2 className="ai-lb-title">AI Model Rankings</h2>
          <span className="ai-lb-subtitle">Top models by human preference</span>
        </div>
        <a
          href={data.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="ai-lb-source"
        >
          {data.source} →
        </a>
      </div>

      <div className="ai-lb-table-wrap">
        <table className="ai-lb-table">
          <thead>
            <tr>
              <th className="ai-lb-th-rank">#</th>
              <th className="ai-lb-th-model">Model</th>
              <th className="ai-lb-th-rating">Rating</th>
              <th className="ai-lb-th-votes">Votes</th>
              <th className="ai-lb-th-change">Δ</th>
            </tr>
          </thead>
          <tbody>
            {data.models.map((m) => (
              <tr key={m.model_key} className="ai-lb-row">
                <td className="ai-lb-rank">
                  {m.rank <= 3 ? (
                    <span className={`ai-lb-medal ai-lb-medal-${m.rank}`}>
                      {m.rank === 1 ? "🥇" : m.rank === 2 ? "🥈" : "🥉"}
                    </span>
                  ) : (
                    <span className="ai-lb-rank-num">{m.rank}</span>
                  )}
                </td>
                <td className="ai-lb-model-cell">
                  <OrgBadge org={m.org_key} />
                  <div className="ai-lb-model-info">
                    <span className="ai-lb-model-name">{m.model}</span>
                    <span className="ai-lb-company">{m.company}</span>
                  </div>
                </td>
                <td className="ai-lb-rating">{m.rating.toLocaleString()}</td>
                <td className="ai-lb-votes">{fmtVotes(m.votes)}</td>
                <td className="ai-lb-change-cell">
                  <RankChange change={m.change} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="ai-lb-footer">
        <span className="ai-lb-updated">Updated {updatedDate}</span>
        <span className="ai-lb-method">{data.methodology}</span>
      </div>
    </section>
  );
}
