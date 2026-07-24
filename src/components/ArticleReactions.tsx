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

function getLocalReaction(articleId: string): ReactionKey | null {
  try {
    const raw = localStorage.getItem(`reaction:${articleId}`);
    return raw as ReactionKey | null;
  } catch {
    return null;
  }
}

function saveLocalReaction(articleId: string, key: ReactionKey | null) {
  try {
    if (key) {
      localStorage.setItem(`reaction:${articleId}`, key);
    } else {
      localStorage.removeItem(`reaction:${articleId}`);
    }
  } catch {}
}

interface ArticleReactionsProps {
  articleId: string;
  initialReactions?: Record<string, number>;
}

export default function ArticleReactions({ articleId, initialReactions }: ArticleReactionsProps) {
  const [counts, setCounts] = useState<Record<string, number>>(initialReactions ?? {});
  const [selected, setSelected] = useState<ReactionKey | null>(null);

  useEffect(() => {
    setSelected(getLocalReaction(articleId));
  }, [articleId]);

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
    const prev = selected;

    if (key === prev) {
      // Undo — toggle off
      setCounts((c) => ({ ...c, [key]: Math.max((c[key] ?? 0) - 1, 0) }));
      setSelected(null);
      saveLocalReaction(articleId, null);

      try {
        const { data } = await (supabase as any).rpc("set_reaction", {
          p_article_id: articleId,
          p_old_reaction: key,
        });
        if (data) setCounts(data as Record<string, number>);
      } catch {}
    } else {
      // Select new (and deselect old if any)
      setCounts((c) => {
        const next = { ...c, [key]: (c[key] ?? 0) + 1 };
        if (prev) next[prev] = Math.max((c[prev] ?? 0) - 1, 0);
        return next;
      });
      setSelected(key);
      saveLocalReaction(articleId, key);

      try {
        const { data } = await (supabase as any).rpc("set_reaction", {
          p_article_id: articleId,
          p_new_reaction: key,
          p_old_reaction: prev ?? undefined,
        });
        if (data) setCounts(data as Record<string, number>);
      } catch {}
    }
  }, [articleId, selected]);

  return (
    <div className="py-5 border-t border-b" style={{ borderColor: "#E5E5E5" }}>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mr-1">React</span>
        {REACTION_TYPES.map(({ key, emoji, label }) => {
          const count = counts[key] ?? 0;
          const isSelected = selected === key;
          return (
            <button
              key={key}
              onClick={() => handleReact(key)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm
                transition-all duration-200 select-none
                ${isSelected
                  ? "bg-neutral-100 border-2 border-neutral-400 cursor-pointer"
                  : "bg-white border border-neutral-200 hover:border-neutral-400 hover:shadow-sm cursor-pointer active:scale-95"
                }
              `}
            >
              <span className="text-base">{emoji}</span>
              <span className={`text-[11px] ${isSelected ? "font-semibold text-foreground" : "text-muted-foreground"}`}>
                {label}
              </span>
              {count > 0 && (
                <span className="text-[11px] font-medium text-muted-foreground tabular-nums">{count}</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
