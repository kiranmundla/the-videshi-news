import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Search, Eye, Check, X, Star, StarOff, ChevronLeft, ChevronRight } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { getCategoryLabel, getCategoryEmoji } from "@/lib/stories";

const sb = supabase as any;
const PAGE_SIZE = 20;

type StoryRow = {
  id: string;
  author_name: string;
  author_email: string;
  author_photo_url: string | null;
  author_city: string | null;
  author_linkedin: string | null;
  category: string;
  headline: string | null;
  subheadline: string | null;
  body: string | null;
  raw_story: string;
  status: string;
  featured: boolean;
  suspicion_score: number;
  reaction_count: number;
  view_count: number;
  slug: string | null;
  published_at: string | null;
  created_at: string;
};

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  pending_review: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function AdminStories() {
  const [rows, setRows] = useState<StoryRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("pending_review");
  const [loading, setLoading] = useState(true);
  const [viewRow, setViewRow] = useState<StoryRow | null>(null);
  const [rejectRow, setRejectRow] = useState<StoryRow | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [acting, setActing] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb
      .from("stories")
      .select("*", { count: "exact" })
      .order("created_at", { ascending: false });

    if (filterStatus !== "all") q = q.eq("status", filterStatus);
    if (search) q = q.or(`author_name.ilike.%${search}%,headline.ilike.%${search}%`);
    q = q.range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1);

    const { data, count, error } = await q;
    if (error) { toast.error(error.message); setLoading(false); return; }
    setRows(data ?? []);
    setTotal(count ?? 0);
    setLoading(false);
  }, [page, search, filterStatus]);

  useEffect(() => { load(); }, [load]);

  async function handleApprove(row: StoryRow) {
    setActing(true);
    const { error } = await sb
      .from("stories")
      .update({
        status: "published",
        published_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
      .eq("id", row.id);

    if (error) {
      toast.error(error.message);
    } else {
      toast.success(`"${row.headline}" published!`);
      // Send confirmation email
      try {
        await sb.functions.invoke("send-story-confirmation", {
          body: {
            headline: row.headline,
            slug: row.slug,
            email: row.author_email,
            author_name: row.author_name,
          },
        });
      } catch { /* best effort */ }
      load();
    }
    setActing(false);
    setViewRow(null);
  }

  async function handleReject() {
    if (!rejectRow) return;
    setActing(true);
    const { error } = await sb
      .from("stories")
      .update({
        status: "rejected",
        rejection_reason: rejectReason.trim() || null,
        updated_at: new Date().toISOString(),
      })
      .eq("id", rejectRow.id);

    if (error) {
      toast.error(error.message);
    } else {
      toast.success("Story rejected");
      load();
    }
    setActing(false);
    setRejectRow(null);
    setRejectReason("");
  }

  async function toggleFeatured(row: StoryRow) {
    const { error } = await sb
      .from("stories")
      .update({ featured: !row.featured, updated_at: new Date().toISOString() })
      .eq("id", row.id);

    if (error) toast.error(error.message);
    else load();
  }

  async function handleDelete(row: StoryRow) {
    if (!confirm(`Delete "${row.headline || "this story"}" permanently?`)) return;
    const { error } = await sb.from("stories").delete().eq("id", row.id);
    if (error) toast.error(error.message);
    else { toast.success("Deleted"); load(); }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <AdminLayout>
      <Helmet><title>Stories · Admin — The Videshi</title></Helmet>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold">Diaspora Voices</h1>
        <div className="flex gap-2 items-center">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              className="pl-9 w-56"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => { setFilterStatus(e.target.value); setPage(0); }}
            className="px-3 py-2 rounded-md border border-border bg-background text-sm"
          >
            <option value="all">All Statuses</option>
            <option value="pending_review">Pending Review</option>
            <option value="published">Published</option>
            <option value="rejected">Rejected</option>
            <option value="draft">Draft</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading...</div>
      ) : rows.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">No stories found</div>
      ) : (
        <div className="overflow-x-auto border border-border rounded-lg">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left p-3 font-medium">Author</th>
                <th className="text-left p-3 font-medium">Story</th>
                <th className="text-left p-3 font-medium">Category</th>
                <th className="text-left p-3 font-medium">Status</th>
                <th className="text-center p-3 font-medium">Score</th>
                <th className="text-center p-3 font-medium">❤️</th>
                <th className="text-right p-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-b border-border hover:bg-muted/20">
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      {row.author_photo_url ? (
                        <img src={row.author_photo_url} alt="" className="w-8 h-8 rounded-full object-cover" />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                          {(row.author_name || "?")[0].toUpperCase()}
                        </div>
                      )}
                      <div>
                        <p className="font-medium text-xs">{row.author_name}</p>
                        <p className="text-xs text-muted-foreground">{row.author_city || ""}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-3">
                    <p className="font-medium text-xs line-clamp-1">{row.headline || "(no headline)"}</p>
                    <p className="text-xs text-muted-foreground line-clamp-1">{row.subheadline || ""}</p>
                  </td>
                  <td className="p-3">
                    <span className="text-xs">{getCategoryEmoji(row.category)} {getCategoryLabel(row.category)}</span>
                  </td>
                  <td className="p-3">
                    <Badge className={`text-xs ${STATUS_COLORS[row.status] || ""}`}>
                      {row.status.replace("_", " ")}
                    </Badge>
                  </td>
                  <td className="p-3 text-center">
                    <span className={`text-xs font-mono ${row.suspicion_score > 70 ? "text-red-500 font-bold" : row.suspicion_score > 40 ? "text-amber-500" : "text-green-500"}`}>
                      {row.suspicion_score}
                    </span>
                  </td>
                  <td className="p-3 text-center text-xs">{row.reaction_count}</td>
                  <td className="p-3">
                    <div className="flex items-center justify-end gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setViewRow(row)} title="View">
                        <Eye className="w-3.5 h-3.5" />
                      </Button>
                      {row.status === "pending_review" && (
                        <>
                          <Button variant="ghost" size="icon" className="h-7 w-7 text-green-600" onClick={() => handleApprove(row)} disabled={acting} title="Approve">
                            <Check className="w-3.5 h-3.5" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-7 w-7 text-red-600" onClick={() => { setRejectRow(row); setRejectReason(""); }} title="Reject">
                            <X className="w-3.5 h-3.5" />
                          </Button>
                        </>
                      )}
                      {row.status === "published" && (
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => toggleFeatured(row)} title={row.featured ? "Unfeature" : "Feature"}>
                          {row.featured ? <StarOff className="w-3.5 h-3.5 text-amber-500" /> : <Star className="w-3.5 h-3.5" />}
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-muted-foreground">{total} stories total</p>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-sm">{page + 1} / {totalPages}</span>
            <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* View dialog */}
      <Dialog open={!!viewRow} onOpenChange={(o) => { if (!o) setViewRow(null); }}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{viewRow?.headline || "Story"}</DialogTitle>
          </DialogHeader>
          {viewRow && (
            <div className="space-y-4 text-sm">
              <div className="flex items-center gap-3">
                {viewRow.author_photo_url && (
                  <img src={viewRow.author_photo_url} alt="" className="w-12 h-12 rounded-full object-cover" />
                )}
                <div>
                  <p className="font-medium">{viewRow.author_name}</p>
                  <p className="text-muted-foreground">{viewRow.author_email} · {viewRow.author_city || ""}</p>
                  {viewRow.author_linkedin && (
                    <a href={viewRow.author_linkedin} target="_blank" rel="noopener noreferrer" className="text-primary text-xs underline">LinkedIn</a>
                  )}
                </div>
              </div>

              <div className="flex gap-2">
                <Badge className={STATUS_COLORS[viewRow.status] || ""}>{viewRow.status.replace("_", " ")}</Badge>
                <Badge variant="outline">{getCategoryEmoji(viewRow.category)} {getCategoryLabel(viewRow.category)}</Badge>
                <Badge variant="outline" className={viewRow.suspicion_score > 70 ? "border-red-500 text-red-500" : ""}>
                  Score: {viewRow.suspicion_score}
                </Badge>
              </div>

              {/* Raw story */}
              <div>
                <h4 className="font-semibold mb-1">Raw submission:</h4>
                <div className="bg-muted rounded-lg p-3 text-xs whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {viewRow.raw_story}
                </div>
              </div>

              {/* Polished story */}
              <div>
                <h4 className="font-semibold mb-1">AI-polished version:</h4>
                {viewRow.subheadline && <p className="italic text-muted-foreground mb-2">{viewRow.subheadline}</p>}
                <div className="bg-muted rounded-lg p-3 text-xs whitespace-pre-wrap max-h-60 overflow-y-auto">
                  {viewRow.body || "(no body)"}
                </div>
              </div>

              {viewRow.status === "pending_review" && (
                <DialogFooter className="gap-2">
                  <Button variant="outline" onClick={() => { setRejectRow(viewRow); setViewRow(null); setRejectReason(""); }}>
                    Reject
                  </Button>
                  <Button onClick={() => handleApprove(viewRow)} disabled={acting}>
                    {acting ? "Publishing..." : "✅ Approve & Publish"}
                  </Button>
                </DialogFooter>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Reject dialog */}
      <Dialog open={!!rejectRow} onOpenChange={(o) => { if (!o) { setRejectRow(null); setRejectReason(""); } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Story</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Rejecting "{rejectRow?.headline}". Optionally provide a reason (not shown publicly).
            </p>
            <Textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Reason for rejection (optional)..."
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setRejectRow(null); setRejectReason(""); }}>Cancel</Button>
            <Button variant="destructive" onClick={handleReject} disabled={acting}>
              {acting ? "Rejecting..." : "Reject"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
