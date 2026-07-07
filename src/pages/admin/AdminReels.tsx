import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { ExternalLink, Play, Image as ImageIcon } from "lucide-react";
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
type FilterType = typeof FILTERS[number];

export default function AdminReels() {
  const [rows, setRows] = useState<ReelRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterType>("all");

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb
      .from("prebuilt_reels")
      .select(
        "id,article_id,article_slug,headline,video_url,status,qa_score,qa_passed,carousel_images,yt_video_id,yt_posted_at,ig_posted_at,threads_posted_at,x_posted_at,created_at"
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

  const fmtDate = (d: string | null) =>
    d ? new Date(d).toLocaleDateString() : "—";

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

      {/* Table */}
      <div className="border border-border rounded-lg overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left p-3 font-medium">Headline</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">Status</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">QA</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Platforms</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Date</th>
              <th className="text-left p-3 font-medium hidden xl:table-cell">Images</th>
              <th className="text-right p-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} className="border-t border-border">
                  <td colSpan={7} className="p-3">
                    <div className="h-10 bg-muted/30 rounded animate-pulse" />
                  </td>
                </tr>
              ))
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-muted-foreground">
                  No reels found
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr
                  key={row.id}
                  className="border-t border-border hover:bg-muted/20 transition-colors"
                >
                  <td className="p-3 max-w-xs">
                    <p className="font-medium line-clamp-2">{row.headline}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 truncate">
                      {row.article_slug}
                    </p>
                  </td>
                  <td className="p-3 hidden md:table-cell">
                    <Badge
                      variant={row.status === "ready" ? "default" : "outline"}
                      className="text-xs"
                    >
                      {row.status}
                    </Badge>
                  </td>
                  <td className="p-3 hidden md:table-cell">
                    {row.qa_passed != null && (
                      <Badge
                        className={`text-xs ${
                          row.qa_passed
                            ? "bg-green-500/15 text-green-400 border-green-500/30"
                            : "bg-red-500/15 text-red-400 border-red-500/30"
                        }`}
                        variant="outline"
                      >
                        {row.qa_passed ? "✓" : "✗"}{" "}
                        {row.qa_score != null ? `${row.qa_score}/10` : ""}
                      </Badge>
                    )}
                  </td>
                  <td className="p-3 hidden lg:table-cell">
                    <div className="flex gap-1 flex-wrap">
                      {row.yt_posted_at && (
                        <Badge
                          variant="outline"
                          className="text-xs bg-red-500/10 text-red-400 border-red-500/30"
                        >
                          YT
                        </Badge>
                      )}
                      {row.ig_posted_at && (
                        <Badge
                          variant="outline"
                          className="text-xs bg-pink-500/10 text-pink-400 border-pink-500/30"
                        >
                          IG
                        </Badge>
                      )}
                      {row.threads_posted_at && (
                        <Badge
                          variant="outline"
                          className="text-xs bg-purple-500/10 text-purple-400 border-purple-500/30"
                        >
                          Threads
                        </Badge>
                      )}
                      {row.x_posted_at && (
                        <Badge
                          variant="outline"
                          className="text-xs bg-blue-500/10 text-blue-400 border-blue-500/30"
                        >
                          X
                        </Badge>
                      )}
                      {!row.yt_posted_at &&
                        !row.ig_posted_at &&
                        !row.threads_posted_at &&
                        !row.x_posted_at && (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                    </div>
                  </td>
                  <td className="p-3 hidden lg:table-cell text-muted-foreground">
                    {fmtDate(row.created_at)}
                  </td>
                  <td className="p-3 hidden xl:table-cell">
                    {row.carousel_images && row.carousel_images.length > 0 ? (
                      <div className="flex gap-1">
                        {row.carousel_images.slice(0, 3).map((url, i) => (
                          <img
                            key={i}
                            src={url}
                            alt=""
                            className="w-8 h-8 object-cover rounded"
                          />
                        ))}
                        {row.carousel_images.length > 3 && (
                          <span className="text-xs text-muted-foreground self-center ml-1">
                            +{row.carousel_images.length - 3}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </td>
                  <td className="p-3 text-right">
                    <div className="flex justify-end gap-1">
                      {row.video_url && (
                        <Button variant="ghost" size="icon" asChild>
                          <a
                            href={row.video_url}
                            target="_blank"
                            rel="noreferrer"
                            title="Watch video"
                          >
                            <Play className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                      {row.yt_video_id && (
                        <Button variant="ghost" size="icon" asChild>
                          <a
                            href={`https://youtube.com/shorts/${row.yt_video_id}`}
                            target="_blank"
                            rel="noreferrer"
                            title="View on YouTube"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  );
}
