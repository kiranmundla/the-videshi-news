import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

/* ── "Story so far" context block for article pages ─────────────────────────
   Shown on articles that belong to an active/emerging developing storyline.
   Gives readers the narrative context: what the story is, the latest
   developments, and a link to the full timeline. Auto-generated from the
   storyline's linked articles — no manual curation needed.
*/

interface TimelineEntry {
  id: string;
  headline: string;
  slug: string;
  published_at: string | null;
}

interface StorylineInfo {
  id: string;
  title: string;
  slug: string;
  status: string;
  article_count: number;
  entries: TimelineEntry[];
}

function formatDateShort(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export default function StorySoFar({ articleId }: { articleId: string }) {
  const [storylines, setStorylines] = useState<StorylineInfo[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!articleId) return;
    let cancelled = false;

    (supabase as any)
      .from("storyline_articles")
      .select("storyline_id, storylines(id, title, slug, status, article_count)")
      .eq("article_id", articleId)
      .then(async ({ data: links }: { data: any[] | null }) => {
        if (cancelled) return;
        // Only surface live narratives — active or emerging.
        const live = (links || [])
          .map((l: any) => l.storylines)
          .filter((s: any) => s && (s.status === "active" || s.status === "emerging"));
        if (live.length === 0) {
          setLoaded(true);
          return;
        }

        // Fetch the 3 most recent entries per storyline for context.
        const enriched: StorylineInfo[] = [];
        for (const s of live.slice(0, 2)) {
          const { data: entries }: { data: any[] | null } = await (supabase as any)
            .from("storyline_articles")
            .select("article_id, p2_articles(id, headline, slug, published_at)")
            .eq("storyline_id", s.id)
            .order("added_at", { ascending: false })
            .limit(4);
          const timeline = (entries || [])
            .map((e: any) => e.p2_articles)
            .filter((a: any) => a && a.id !== articleId)
            .slice(0, 3)
            .map((a: any) => ({
              id: a.id,
              headline: a.headline,
              slug: a.slug,
              published_at: a.published_at,
            }));
          enriched.push({ ...s, entries: timeline });
        }
        if (!cancelled) {
          setStorylines(enriched);
          setLoaded(true);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [articleId]);

  if (!loaded || storylines.length === 0) return null;

  return (
    <div
      className="my-6 rounded-lg border border-border bg-card overflow-hidden"
      data-testid="story-so-far"
    >
      {storylines.map((s, si) => (
        <div key={s.id} className={si > 0 ? "border-t border-border" : ""}>
          <div className="px-4 pt-4 pb-1 flex items-center gap-2">
            <span
              className="inline-block w-2 h-2 rounded-full animate-pulse"
              style={{ backgroundColor: "#A32D2F" }}
              aria-hidden
            />
            <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
              Developing story · The story so far
            </span>
          </div>
          <div className="px-4 pb-1">
            <Link
              to={`/developing/${s.slug}`}
              className="text-[15px] font-bold leading-snug hover:underline"
              style={{ color: "#0B1D3A" }}
            >
              {s.title}
            </Link>
          </div>
          {s.entries.length > 0 && (
            <ul className="px-4 py-2 space-y-2">
              {s.entries.map((e) => (
                <li key={e.id} className="text-[13px] leading-snug">
                  <span className="text-muted-foreground text-[11px] font-medium mr-2">
                    {formatDateShort(e.published_at)}
                  </span>
                  <Link
                    to={`/articles/${e.slug}`}
                    className="hover:underline text-foreground/90"
                  >
                    {e.headline}
                  </Link>
                </li>
              ))}
            </ul>
          )}
          <div className="px-4 pb-4 pt-1">
            <Link
              to={`/developing/${s.slug}`}
              className="text-[13px] font-semibold hover:underline"
              style={{ color: "#A32D2F" }}
            >
              See full timeline ({s.article_count} article{s.article_count === 1 ? "" : "s"}) →
            </Link>
          </div>
        </div>
      ))}
    </div>
  );
}
