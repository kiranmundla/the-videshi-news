import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { ExternalLink, Play, Copy, Check, ChevronDown, ChevronUp } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

const sb = supabase as any;

type ReelRow = {
  id: string;
  article_id: string;
  article_slug: string;
  headline: string;
  video_url: string | null;
  caption: string | null;
  status: string;
  qa_score: number | null;
  qa_passed: boolean | null;
  carousel_images: string[] | null;
  yt_video_id: string | null;
  yt_posted_at: string | null;
  ig_posted_at: string | null;
  threads_posted_at: string | null;
  x_posted_at: string | null;
  created_at: string;
};

const FILTERS = ["all", "ready", "pending"] as const;
type FilterType = (typeof FILTERS)[number];

function buildYTCaption(row: ReelRow): string {
  return [
    row.headline,
    "",
    `📰 https://www.thevideshi.com/articles/${row.article_slug}`,
    "",
    "TheVideshi.com",
    "Subscribe to @the.videshi for more",
    "#IndianDiaspora #NRI #TheVideshi #Shorts",
  ].join("\n");
}

function ReelCard({ row }: { row: ReelRow }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const fmtDate = (d: string | null) =>
    d ? new Date(d).toLocaleDateString() : "—";

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(buildYTCaption(row));
    setCopied(true);
    toast.success("Copied for YouTube!");
    setTimeout(() => setCopied(false), 2000);
  };

  const hasImages = row.carousel_images && row.carousel_images.length > 0;

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      {/* Main row */}
      <div
        className="flex items-center gap-3 p-3 hover:bg-muted/20 transition-colors cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        {hasImages ? (
          <img
            src={row.carousel_images![0]}
            alt=""
            className="w-12 h-12 object-cover rounded flex-shrink-0"
          />
        ) : (
          <div className="w-12 h-12 bg-muted/30 rounded flex-shrink-0 flex items-center justify-center text-muted-foreground text-xs">
            —
          </div>
        )}

        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm line-clamp-1">{row.headline}</p>
          <div className="flex gap-2 mt-1 flex-wrap">
            <Badge
              variant={row.status === "ready" ? "default" : "outline"}
              className="text-xs"
            >
              {row.status}
            </Badge>
            {row.qa_passed != null && (
              <Badge
                className={`text-xs ${
                  row.qa_passed
                    ? "bg-green-500/15 text-green-600 border-green-500/30"
                    : "bg-red-500/15 text-red-600 border-red-500/30"
                }`}
                variant="outline"
              >
                {row.qa_passed ? "✓" : "✗"} {row.qa_score != null ? `${row.qa_score}/10` : ""}
              </Badge>
            )}
            {row.yt_posted_at && (
              <Badge variant="outline" className="text-xs bg-red-500/10 text-red-600 border-red-500/30">YT</Badge>
            )}
            {row.ig_posted_at && (
              <Badge variant="outline" className="text-xs bg-pink-500/10 text-pink-600 border-pink-500/30">IG</Badge>
            )}
            {row.threads_posted_at && (
              <Badge variant="outline" className="text-xs bg-purple-500/10 text-purple-600 border-purple-500/30">Threads</Badge>
            )}
            {row.x_posted_at && (
              <Badge variant="outline" className="text-xs bg-blue-500/10 text-blue-600 border-blue-500/30">X</Badge>
            )}
          </div>
        </div>

        <span className="text-xs text-muted-foreground hidden md:block">{fmtDate(row.created_at)}</span>
        <div className="flex gap-1 items-center">
          {row.video_url && (
            <Button variant="ghost" size="icon" asChild onClick={(e: React.MouseEvent) => e.stopPropagation()}>
              <a href={row.video_url} target="_blank" rel="noreferrer" title="Watch video">
                <Play className="h-4 w-4" />
              </a>
            </Button>
          )}
          {row.yt_video_id && (
            <Button variant="ghost" size="icon" asChild onClick={(e: React.MouseEvent) => e.stopPropagation()}>
              <a href={`https://youtube.com/shorts/${row.yt_video_id}`} target="_blank" rel="noreferrer" title="YouTube">
                <ExternalLink className="h-4 w-4" />
              </a>
            </Button>
          )}
          {expanded ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
        </div>
      </div>

      {/* Expanded detail panel */}
      {expanded && (
        <div className="border-t border-border bg-muted/10 p-4 space-y-4">
          {/* Carousel images — larger grid for saving */}
          {hasImages && (
            <div>
              <p className="text-sm font-medium mb-2">
                Carousel Images{" "}
                <span className="text-muted-foreground font-normal">(tap to open full size)</span>
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                {row.carousel_images!.map((url, i) => (
                  <a key={i} href={url} target="_blank" rel="noreferrer" className="block">
                    <img
                      src={url}
                      alt={`Scene ${i + 1}`}
                      className="w-full aspect-[4/5] object-cover rounded-lg border border-border hover:border-foreground/30 transition-colors"
                    />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex flex-wrap gap-2 items-center">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className={copied ? "bg-green-500/15 text-green-600 border-green-500/30" : ""}
            >
              {copied ? (
                <><Check className="h-4 w-4 mr-1" /> Copied!</>
              ) : (
                <><Copy className="h-4 w-4 mr-1" /> Copy for YouTube</>
              )}
            </Button>
            <Button variant="outline" size="sm" asChild>
              <a href="https://studio.youtube.com/" target="_blank" rel="noreferrer">
                Open YouTube Studio ↗
              </a>
            </Button>
            {row.video_url && (
              <Button variant="outline" size="sm" asChild>
                <a href={row.video_url} target="_blank" rel="noreferrer">
                  Download Video ↗
                </a>
              </Button>
            )}
            <a
              href={`https://www.thevideshi.com/articles/${row.article_slug}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-muted-foreground hover:text-foreground underline ml-auto"
            >
              View Article ↗
            </a>
          </div>

          {/* Caption preview */}
          <div>
            <p className="text-sm font-medium mb-1">YouTube Caption Preview</p>
            <pre className="text-xs bg-background border border-border rounded-lg p-3 whitespace-pre-wrap break-words max-h-40 overflow-auto">
              {buildYTCaption(row)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AdminReels() {
  const [rows, setRows] = useState<ReelRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterType>("all");

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb
      .from("prebuilt_reels")
      .select(
        "id,article_id,article_slug,headline,video_url,caption,status,qa_score,qa_passed,carousel_images,yt_video_id,yt_posted_at,ig_posted_at,threads_posted_at,x_posted_at,created_at"
      )
      .order("created_at", { ascending: false })
      .limit(30);

    if (filter !== "all") {
      q = q.eq("status", filter);
    }

    const { data, error } = await q;
    if (error) {
      toast.error(error.message);
      setLoading(false);
      return;
    }
    setRows(data ?? []);
    setLoading(false);
  }, [filter]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <AdminLayout>
      <Helmet>
        <title>Reels | Videshi CMS</title>
      </Helmet>

      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-bold">Reels</h1>
          <p className="text-sm text-muted-foreground">{rows.length} reels</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-4">
        {FILTERS.map((f) => (
          <Button
            key={f}
            variant={filter === f ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </Button>
        ))}
      </div>

      {/* Reel cards */}
      <div className="space-y-2">
        {loading ? (
          [...Array(5)].map((_, i) => (
            <div key={i} className="border border-border rounded-lg p-4">
              <div className="h-12 bg-muted/30 rounded animate-pulse" />
            </div>
          ))
        ) : rows.length === 0 ? (
          <div className="border border-border rounded-lg p-8 text-center text-muted-foreground">
            No reels found
          </div>
        ) : (
          rows.map((row) => <ReelCard key={row.id} row={row} />)
        )}
      </div>
    </AdminLayout>
  );
}
