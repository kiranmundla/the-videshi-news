import { useState, useEffect, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";

/* ── Types ── */
interface Poll {
  id: string;
  question: string;
  options: string[];
  votes: Record<string, number>;
  category: string | null;
  related_article_id: string | null;
  is_active: boolean;
  created_at: string;
  expires_at: string | null;
}

/* ── localStorage helpers ── */
function getVotedOption(pollId: string): number | null {
  try {
    const raw = localStorage.getItem(`poll:${pollId}`);
    return raw !== null ? parseInt(raw, 10) : null;
  } catch {
    return null;
  }
}

function saveVote(pollId: string, optionIndex: number) {
  try {
    localStorage.setItem(`poll:${pollId}`, String(optionIndex));
  } catch {
    /* localStorage full — vote still counted server-side */
  }
}

/* ── Component ── */
export default function ThePulse() {
  const [poll, setPoll] = useState<Poll | null>(null);
  const [loading, setLoading] = useState(true);
  const [votedIndex, setVotedIndex] = useState<number | null>(null);
  const [votes, setVotes] = useState<Record<string, number>>({});
  const [animating, setAnimating] = useState(false);
  const [voting, setVoting] = useState(false);

  /* ── Fetch active poll ── */
  const fetchPoll = useCallback(async () => {
    try {
      const { data, error } = await (supabase as any)
        .from("polls")
        .select("*")
        .eq("is_active", true)
        .order("created_at", { ascending: false })
        .limit(1)
        .single();

      if (error || !data) {
        setPoll(null);
        setLoading(false);
        return;
      }

      // Check if expired
      if (data.expires_at && new Date(data.expires_at) < new Date()) {
        setPoll(null);
        setLoading(false);
        return;
      }

      const pollData: Poll = {
        id: data.id,
        question: data.question,
        options: Array.isArray(data.options) ? data.options : [],
        votes: data.votes || {},
        category: data.category,
        related_article_id: data.related_article_id,
        is_active: data.is_active,
        created_at: data.created_at,
        expires_at: data.expires_at,
      };

      setPoll(pollData);
      setVotes(pollData.votes);

      // Check if already voted
      const prev = getVotedOption(pollData.id);
      if (prev !== null) {
        setVotedIndex(prev);
        // Animate bars after a tick for returning voters too
        requestAnimationFrame(() => setAnimating(true));
      }
    } catch {
      setPoll(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPoll();
  }, [fetchPoll]);

  /* ── Cast vote ── */
  const handleVote = async (optionIndex: number) => {
    if (!poll || votedIndex !== null || voting) return;
    setVoting(true);

    // Optimistic update
    const newVotes = { ...votes };
    const key = String(optionIndex);
    newVotes[key] = (newVotes[key] || 0) + 1;
    setVotes(newVotes);
    setVotedIndex(optionIndex);
    saveVote(poll.id, optionIndex);

    // Animate after a tick
    requestAnimationFrame(() => {
      setAnimating(true);
    });

    // Server-side vote
    try {
      const { data } = await (supabase as any).rpc("cast_vote", {
        p_poll_id: poll.id,
        p_option_index: key,
      });
      if (data) {
        setVotes(data);
      }
    } catch {
      /* Keep optimistic update — close enough */
    } finally {
      setVoting(false);
    }
  };

  /* ── Computed values ── */
  const totalVotes = Object.values(votes).reduce((sum, v) => sum + (v || 0), 0);

  const getPercentage = (idx: number): number => {
    const v = votes[String(idx)] || 0;
    return totalVotes > 0 ? Math.round((v / totalVotes) * 100) : 0;
  };

  const getVoteCount = (idx: number): number => votes[String(idx)] || 0;

  const leadingIndex = poll
    ? poll.options.reduce(
        (best, _, idx) => (getVoteCount(idx) > getVoteCount(best) ? idx : best),
        0
      )
    : 0;

  /* ── Don't render if no poll ── */
  if (loading || !poll) return null;

  const hasVoted = votedIndex !== null;

  return (
    <section className="mb-14">
      <div className="rounded-xl overflow-hidden border border-gray-200 bg-white shadow-sm">
        {/* Header */}
        <div
          className="px-4 py-3 flex items-center justify-between"
          style={{ background: "#0B1D3A" }}
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">📊</span>
            <span
              className="text-xs font-bold uppercase tracking-widest"
              style={{ color: "#D4A843" }}
            >
              The Pulse
            </span>
          </div>
          {totalVotes > 0 && (
            <span className="text-xs text-gray-300">
              {totalVotes.toLocaleString()} vote{totalVotes !== 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Body */}
        <div className="p-4 md:p-5">
          {/* Category tag */}
          {poll.category && (
            <span className="inline-block text-[10px] font-bold uppercase tracking-wide text-red-700 mb-2">
              {poll.category}
            </span>
          )}

          {/* Question */}
          <h3
            className="text-base md:text-lg font-bold leading-snug mb-4"
            style={{ fontFamily: "'Playfair Display', serif", color: "#1A1A1A" }}
          >
            {poll.question}
          </h3>

          {/* Options */}
          <div className="space-y-2.5">
            {poll.options.map((option, idx) => {
              const pct = getPercentage(idx);
              const isLeading = idx === leadingIndex && totalVotes > 0;
              const isSelected = votedIndex === idx;

              if (!hasVoted) {
                /* Pre-vote: clean buttons */
                return (
                  <button
                    key={idx}
                    onClick={() => handleVote(idx)}
                    disabled={voting}
                    className="w-full text-left px-4 py-2.5 rounded-lg border border-gray-200 
                      hover:border-gray-400 hover:bg-gray-50 transition-colors text-sm font-medium
                      text-gray-800 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {option}
                  </button>
                );
              }

              /* Post-vote: animated result bars */
              return (
                <div
                  key={idx}
                  className={`relative rounded-lg overflow-hidden border transition-all duration-300 ${
                    isSelected
                      ? "border-gray-400 ring-1 ring-gray-300"
                      : "border-gray-200"
                  }`}
                >
                  {/* Bar fill */}
                  <div
                    className="absolute inset-y-0 left-0 transition-all duration-[800ms] ease-out rounded-lg"
                    style={{
                      width: animating ? `${pct}%` : "0%",
                      background: isLeading
                        ? "rgba(163, 45, 45, 0.12)"
                        : "rgba(0, 0, 0, 0.05)",
                    }}
                  />

                  {/* Content */}
                  <div className="relative px-4 py-2.5 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {isSelected && (
                        <span className="text-xs">✓</span>
                      )}
                      <span
                        className={`text-sm ${
                          isLeading ? "font-bold text-gray-900" : "font-medium text-gray-700"
                        }`}
                      >
                        {option}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span
                        className={`text-sm tabular-nums ${
                          isLeading ? "font-bold" : "font-medium text-gray-500"
                        }`}
                        style={isLeading ? { color: "#A32D2D" } : undefined}
                      >
                        {pct}%
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Footer — vote count after voting */}
          {hasVoted && (
            <p className="text-xs text-gray-400 mt-3 text-center">
              {totalVotes.toLocaleString()} total vote{totalVotes !== 1 ? "s" : ""}
              {" · "}Thanks for voting!
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
