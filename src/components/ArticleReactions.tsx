import { useState, useEffect, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";

const REACTION_TYPES = [
  { key: "fire",  emoji: "🔥", label: "Important" },
  { key: "clap",  emoji: "👏", label: "Inspiring" },
  { key: "sad",   emoji: "😢", label: "Concerning" },
  { key: "think", emoji: "🤔", label: "Debatable" },
  { key: "fun",   emoji: "😄", label: "Fun" },
] as const;

type ReactionKey = (typeof REACTION_TYPES)[number]["key"];

/* ── Persistent anonymous visitor ID ── */
function getVisitorId(): string {
  const KEY = "videshi_visitor_id";
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(KEY, id);
  }
  return id;
}

function getLocalReactions(articleId: string): Set<ReactionKey> {
  try {
    const raw = localStorage.getItem(`reactions:${articleId}`);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

function saveLocalReaction(articleId: string, key: ReactionKey) {
  try {
    const existing = getLocalReactions(articleId);
    existing.add(key);
    localStorage.setItem(`reactions:${articleId}`, JSON.stringify([...existing]));
  } catch {}
}

interface ArticleReactionsProps {
  articleId: string;
  initialReactions?: Record<string, number>;
}

export default function ArticleReactions({ articleId, initialReactions }: ArticleReactionsProps) {
  const [counts, setCounts] = useState<Record<string, number>>(initialReactions ?? {});
  const [reacted, setReacted] = useState<Set<ReactionKey>>(new Set());
  const [animating, setAnimating] = useState<string | null>(null);

  useEffect(() => {
    setReacted(getLocalReactions(articleId));
  }, [articleId]);

  // Fetch latest counts on mount if no initial data
  useEffect(() => {
    if (initialReactions) return;
    (async () => {
      const { data } = await supabase
        .from("p2_articles")
        .select("reactions")
        .eq("id", articleId)
        .single();
      if (data?.reactions) setCounts(data.reactions as Record<string, number>);
    })();
  }, [articleId, initialReactions]);

  const handleReact = useCallback(async (key: ReactionKey) => {
    if (reacted.has(key)) return;

    // Optimistic update
    setCounts((prev) => ({ ...prev, [key]: (prev[key] ?? 0) + 1 }));
    setReacted((prev) => new Set(prev).add(key));
    saveLocalReaction(articleId, key);
    setAnimating(key);
    setTimeout(() => setAnimating(null), 600);

    // Persist with visitor ID for server-side dedup
    try {
      const visitorId = getVisitorId();
      const { data } = await supabase.rpc("increment_reaction", {
        p_article_id: articleId,
        p_reaction: key,
        p_visitor_id: visitorId,
      });
      if (data) setCounts(data as Record<string, number>);
    } catch {
      // Optimistic update stays — acceptable for reactions
    }
  }, [articleId, reacted]);

  return (
    <div className="flex flex-wrap items-center gap-2 py-5 border-t border-b" style={{ borderColor: "#E5E5E5" }}>
      <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mr-1">React</span>
      {REACTION_TYPES.map(({ key, emoji, label }) => {
        const count = counts[key] ?? 0;
        const hasReacted = reacted.has(key);
        return (
          <button
            key={key}
            onClick={() => handleReact(key)}
            disabled={hasReacted}
            title={label}
            className={`
              inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm
              transition-all duration-200 select-none
              ${hasReacted
                ? "bg-neutral-100 border border-neutral-300 opacity-80 cursor-default"
                : "bg-white border border-neutral-200 hover:border-neutral-400 hover:shadow-sm cursor-pointer active:scale-95"
              }
              ${animating === key ? "scale-110" : ""}
            `}
          >
            <span className={`text-base ${animating === key ? "animate-bounce" : ""}`}>{emoji}</span>
            {count > 0 && (
              <span className="text-xs font-medium text-muted-foreground tabular-nums">{count}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
