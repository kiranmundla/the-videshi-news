import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Copy, ExternalLink, Check, Image as ImageIcon } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

const sb = supabase as any;

type ArticleRow = {
  id: string;
  slug: string;
  headline: string;
  subheadline: string | null;
  category: string | null;
  image_url: string | null;
  published_at: string | null;
  tweeted_at: string | null;
};

const CATEGORY_EMOJI: Record<string, string> = {
  news: "📰",
  immigration: "🛂",
  entertainment: "🎬",
  technology: "💻",
  "markets-finance": "📊",
  sports: "🏏",
  "nri-world": "🌏",
  "lifestyle-health": "🧘",
  food: "🍛",
  travel: "✈️",
};

function getEmoji(cat: string | null): string {
  if (!cat) return "📰";
  return CATEGORY_EMOJI[cat] || "📰";
}

function buildTweetText(
  headline: string,
  category: string | null,
  subheadline: string | null,
  slug: string
): string {
  const emoji = getEmoji(category);
  const catLabel = category
    ? category
        .split("-")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ")
    : "News";

  let text = headline + "\n\n" + emoji + " " + catLabel;

  if (subheadline) {
    text += "\n\n" + subheadline;
  }

  text +=
    "\n\n📰 https://www.thevideshi.com/articles/" +
    slug +
    "\n\nTheVideshi.com\nFollow @thevideshi for more\n#IndianDiaspora #NRI #TheVideshi";

  return text;
}

type FilterType = "all" | "not-posted";

export default function AdminPostToX() {
  const [rows, setRows] = useState<ArticleRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterType>("not-posted");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [markingId, setMarkingId] = useState<string | null>(null);
  const [markedId, setMarkedId] = useState<string | null>(null);
  // Track locally-marked articles so UI updates without refetch
  const [localMarked, setLocalMarked] = useState<Set<string>>(new Set());

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb
      .from("p2_articles")
      .select(
        "id,slug,headline,subheadline,category,image_url,published_at,tweeted_at"
      )
      .eq("status", "published")
      .order("published_at", { ascending: false, nullsFirst: false })
      .limit(30);

    if (filter === "not-posted") {
      q = q.is("tweeted_at", null);
    }

    const { data, error } = await q;
    if (error) {
      toast.error(error.message);
      setLoading(false);
      return;
    }
    setRows(data ?? []);
    setLocalMarked(new Set());
    setLoading(false);
  }, [filter]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleCopy(row: ArticleRow) {
    const text = buildTweetText(
      row.headline,
      row.category,
      row.subheadline,
      row.slug
    );
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(row.id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      toast.error("Failed to copy");
    }
  }

  function handleOpenX(row: ArticleRow) {
    const text = buildTweetText(
      row.headline,
      row.category,
      row.subheadline,
      row.slug
    );
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
      "_blank"
    );
  }

  async function handleMarkPosted(row: ArticleRow) {
    setMarkingId(row.id);
    const { error } = await sb
      .from("p2_articles")
      .update({ tweeted_at: new Date().toISOString() })
      .eq("id", row.id);
    setMarkingId(null);

    if (error) {
      toast.error(error.message);
      return;
    }

    setLocalMarked((prev) => new Set(prev).add(row.id));
    setMarkedId(row.id);
    toast.success("Marked as posted");
    setTimeout(() => setMarkedId(null), 2000);
  }

  const isPosted = (row: ArticleRow) =>
    !!row.tweeted_at || localMarked.has(row.id);

  const fmtDate = (d: string | null) =>
    d ? new Date(d).toLocaleDateString() : "—";

  return (
    <AdminLayout>
      <Helmet>
        <title>Post to X | Videshi CMS</title>
      </Helmet>

      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-bold">Post to X</h1>
          <p className="text-sm text-muted-foreground">
            {rows.length} articles
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-4">
        <Button
          variant={filter === "not-posted" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("not-posted")}
        >
          Not Posted
        </Button>
        <Button
          variant={filter === "all" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("all")}
        >
          All
        </Button>
      </div>

      {/* Cards */}
      <div className="space-y-3">
        {loading ? (
          [...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-24 bg-muted/30 rounded-lg animate-pulse"
            />
          ))
        ) : rows.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            {filter === "not-posted"
              ? "All articles have been posted! 🎉"
              : "No articles found"}
          </div>
        ) : (
          rows.map((row) => {
            const posted = isPosted(row);
            return (
              <div
                key={row.id}
                className="border border-border rounded-lg p-4 bg-card hover:bg-muted/10 transition-colors"
              >
                <div className="flex gap-4">
                  {/* Hero image */}
                  <div className="flex-shrink-0">
                    {row.image_url ? (
                      <img
                        src={row.image_url}
                        alt=""
                        className="w-20 h-14 object-cover rounded"
                      />
                    ) : (
                      <div className="w-20 h-14 bg-muted rounded flex items-center justify-center">
                        <ImageIcon className="h-5 w-5 text-muted-foreground" />
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h3 className="font-medium text-sm line-clamp-2">
                        {row.headline}
                      </h3>
                      <Badge
                        variant="outline"
                        className={`text-xs flex-shrink-0 ${
                          posted
                            ? "bg-green-500/15 text-green-400 border-green-500/30"
                            : "bg-amber-500/15 text-amber-400 border-amber-500/30"
                        }`}
                      >
                        {posted ? "Posted" : "Not posted"}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                      <span>
                        {getEmoji(row.category)}{" "}
                        {row.category
                          ? row.category
                              .split("-")
                              .map(
                                (w) =>
                                  w.charAt(0).toUpperCase() + w.slice(1)
                              )
                              .join(" ")
                          : "News"}
                      </span>
                      <span>·</span>
                      <span>{fmtDate(row.published_at)}</span>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs"
                        onClick={() => handleCopy(row)}
                      >
                        {copiedId === row.id ? (
                          <>
                            <Check className="h-3 w-3 mr-1" /> Copied ✓
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3 mr-1" /> Copy All
                          </>
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs"
                        onClick={() => handleOpenX(row)}
                      >
                        Open X
                      </Button>
                      {!posted && (
                        <Button
                          variant="outline"
                          size="sm"
                          className={`h-7 text-xs ${
                            markedId === row.id
                              ? "bg-green-500/15 text-green-400 border-green-500/30"
                              : "text-green-400 border-green-500/30 hover:bg-green-500/10"
                          }`}
                          disabled={markingId === row.id}
                          onClick={() => handleMarkPosted(row)}
                        >
                          {markingId === row.id
                            ? "Marking…"
                            : markedId === row.id
                            ? "Marked ✓"
                            : "✓ Mark as Posted"}
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs"
                        asChild
                      >
                        <a
                          href={`https://www.thevideshi.com/articles/${row.slug}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          View Article{" "}
                          <ExternalLink className="h-3 w-3 ml-1" />
                        </a>
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </AdminLayout>
  );
}
