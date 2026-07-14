import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Check, X, Clock, ChevronLeft, ChevronRight, ExternalLink } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

const sb = supabase as any;
const PAGE_SIZE = 20;

type Recommendation = {
  id: string;
  business_name: string;
  category: string;
  city: string;
  state: string;
  phone: string | null;
  website: string | null;
  description: string | null;
  recommender_name: string | null;
  recommender_email: string | null;
  reason: string | null;
  status: string;
  created_at: string;
  reviewed_at: string | null;
  notes: string | null;
};

function statusBadge(status: string) {
  switch (status) {
    case "pending":
      return <Badge variant="secondary" className="bg-amber-500/15 text-amber-400 border-amber-500/30"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
    case "approved":
      return <Badge variant="secondary" className="bg-green-500/15 text-green-400 border-green-500/30"><Check className="h-3 w-3 mr-1" />Approved</Badge>;
    case "rejected":
      return <Badge variant="secondary" className="bg-red-500/15 text-red-400 border-red-500/30"><X className="h-3 w-3 mr-1" />Rejected</Badge>;
    default:
      return <Badge variant="secondary">{status}</Badge>;
  }
}

function generateSlug(name: string): string {
  const cleaned = name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+$/, "")
    .slice(0, 60)
    .replace(/-+$/, "");
  const suffix = Math.random().toString(36).slice(2, 8);
  return `${cleaned}-${suffix}`;
}

export default function AdminRecommendations() {
  const [rows, setRows] = useState<Recommendation[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [filterStatus, setFilterStatus] = useState<string>("pending");
  const [loading, setLoading] = useState(true);
  const [detailRow, setDetailRow] = useState<Recommendation | null>(null);
  const [processing, setProcessing] = useState(false);
  const [adminNotes, setAdminNotes] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb
      .from("directory_recommendations")
      .select("*", { count: "exact" })
      .order("created_at", { ascending: false });

    if (filterStatus !== "all") q = q.eq("status", filterStatus);
    q = q.range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1);

    const { data, count, error } = await q;
    if (error) {
      toast.error(error.message);
      setLoading(false);
      return;
    }
    setRows(data ?? []);
    setTotal(count ?? 0);
    setLoading(false);
  }, [page, filterStatus]);

  useEffect(() => {
    load();
  }, [load]);

  const handleApprove = async (row: Recommendation) => {
    setProcessing(true);

    // 1. Create directory listing from recommendation
    const slug = generateSlug(row.business_name);
    const { error: insertError } = await sb.from("directory_listings").insert([
      {
        name: row.business_name,
        category: row.category,
        city: row.city,
        state: row.state,
        phone: row.phone || null,
        website: row.website || null,
        ai_description: row.description || null,
        source: "community",
        verified: false,
        featured: false,
        slug,
      },
    ]);

    if (insertError) {
      toast.error("Failed to create listing: " + insertError.message);
      setProcessing(false);
      return;
    }

    // 2. Update recommendation status
    const { error: updateError } = await sb
      .from("directory_recommendations")
      .update({
        status: "approved",
        reviewed_at: new Date().toISOString(),
        notes: adminNotes.trim() || null,
      })
      .eq("id", row.id);

    if (updateError) {
      toast.error("Listing created but failed to update recommendation status");
    } else {
      toast.success(`Approved! "${row.business_name}" added to directory.`);
    }

    setProcessing(false);
    setDetailRow(null);
    setAdminNotes("");
    load();
  };

  const handleReject = async (row: Recommendation) => {
    setProcessing(true);

    const { error } = await sb
      .from("directory_recommendations")
      .update({
        status: "rejected",
        reviewed_at: new Date().toISOString(),
        notes: adminNotes.trim() || null,
      })
      .eq("id", row.id);

    setProcessing(false);

    if (error) {
      toast.error("Failed to reject: " + error.message);
      return;
    }

    toast.success("Recommendation rejected.");
    setDetailRow(null);
    setAdminNotes("");
    load();
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const pendingCount = rows.filter((r) => r.status === "pending").length;

  return (
    <AdminLayout>
      <Helmet>
        <title>Recommendations · Admin · The Videshi</title>
      </Helmet>

      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold">Directory Recommendations</h1>
          <p className="text-sm text-muted-foreground">{total} total</p>
        </div>
      </div>

      {/* Status filter tabs */}
      <div className="flex gap-1 mb-4 border-b border-border">
        {[
          { value: "pending", label: "Pending" },
          { value: "approved", label: "Approved" },
          { value: "rejected", label: "Rejected" },
          { value: "all", label: "All" },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => {
              setFilterStatus(tab.value);
              setPage(0);
            }}
            className={`px-4 py-2 text-sm font-medium transition-colors relative ${
              filterStatus === tab.value
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground/70"
            }`}
          >
            {tab.label}
            {filterStatus === tab.value && (
              <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="border border-border rounded-lg overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left p-3 font-medium">Business</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">Category</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">Location</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Recommended By</th>
              <th className="text-left p-3 font-medium">Status</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Date</th>
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
                  {filterStatus === "pending"
                    ? "No pending recommendations 🎉"
                    : "No recommendations found"}
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr
                  key={row.id}
                  className="border-t border-border hover:bg-muted/20 transition-colors cursor-pointer"
                  onClick={() => {
                    setDetailRow(row);
                    setAdminNotes(row.notes || "");
                  }}
                >
                  <td className="p-3">
                    <p className="font-medium line-clamp-1">{row.business_name}</p>
                    {row.reason && (
                      <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                        "{row.reason}"
                      </p>
                    )}
                  </td>
                  <td className="p-3 hidden md:table-cell">
                    <Badge variant="secondary" className="text-xs">
                      {row.category}
                    </Badge>
                  </td>
                  <td className="p-3 hidden md:table-cell text-muted-foreground">
                    {row.city}, {row.state}
                  </td>
                  <td className="p-3 hidden lg:table-cell text-muted-foreground">
                    {row.recommender_name || "Anonymous"}
                  </td>
                  <td className="p-3">{statusBadge(row.status)}</td>
                  <td className="p-3 hidden lg:table-cell text-muted-foreground text-xs">
                    {new Date(row.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-3 text-right">
                    {row.status === "pending" && (
                      <div className="flex justify-end gap-1" onClick={(e) => e.stopPropagation()}>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-green-400 hover:text-green-300 hover:bg-green-500/10"
                          onClick={() => {
                            setDetailRow(row);
                            setAdminNotes("");
                          }}
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                          onClick={() => {
                            setDetailRow(row);
                            setAdminNotes("");
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-muted-foreground">
            Page {page + 1} of {totalPages}
          </p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(page - 1)}>
              <ChevronLeft className="h-4 w-4 mr-1" /> Prev
            </Button>
            <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}>
              Next <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Detail / Review Dialog */}
      <Dialog open={!!detailRow} onOpenChange={(open) => !open && setDetailRow(null)}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Review Recommendation</DialogTitle>
          </DialogHeader>
          {detailRow && (
            <div className="space-y-4">
              {/* Business info */}
              <div className="bg-muted/30 rounded-lg p-4 space-y-2">
                <h3 className="font-semibold text-lg">{detailRow.business_name}</h3>
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="secondary">{detailRow.category}</Badge>
                  {statusBadge(detailRow.status)}
                </div>
                <p className="text-sm text-muted-foreground">
                  📍 {detailRow.city}, {detailRow.state}
                </p>
                {detailRow.phone && (
                  <p className="text-sm text-muted-foreground">📞 {detailRow.phone}</p>
                )}
                {detailRow.website && (
                  <p className="text-sm flex items-center gap-1">
                    <ExternalLink className="h-3 w-3" />
                    <a
                      href={detailRow.website}
                      target="_blank"
                      rel="noreferrer"
                      className="text-primary hover:underline text-sm"
                    >
                      {detailRow.website}
                    </a>
                  </p>
                )}
                {detailRow.description && (
                  <p className="text-sm text-foreground/80 mt-2">{detailRow.description}</p>
                )}
              </div>

              {/* Recommender info */}
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Recommended by
                </p>
                <p className="text-sm">
                  {detailRow.recommender_name || "Anonymous"}
                  {detailRow.recommender_email && (
                    <span className="text-muted-foreground ml-2">({detailRow.recommender_email})</span>
                  )}
                </p>
                {detailRow.reason && (
                  <p className="text-sm text-foreground/80 italic">"{detailRow.reason}"</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Submitted {new Date(detailRow.created_at).toLocaleString()}
                </p>
              </div>

              {/* Admin notes */}
              {detailRow.status === "pending" && (
                <div>
                  <label className="text-sm font-medium mb-1 block">Admin Notes (optional)</label>
                  <Textarea
                    value={adminNotes}
                    onChange={(e) => setAdminNotes(e.target.value)}
                    placeholder="Internal notes..."
                    rows={2}
                  />
                </div>
              )}

              {/* Existing notes for already-reviewed */}
              {detailRow.status !== "pending" && detailRow.notes && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                    Admin Notes
                  </p>
                  <p className="text-sm text-foreground/80">{detailRow.notes}</p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            {detailRow?.status === "pending" ? (
              <div className="flex w-full gap-2">
                <Button
                  variant="outline"
                  onClick={() => setDetailRow(null)}
                  className="flex-1"
                  disabled={processing}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => detailRow && handleReject(detailRow)}
                  className="flex-1"
                  disabled={processing}
                >
                  {processing ? "…" : "Reject"}
                </Button>
                <Button
                  onClick={() => detailRow && handleApprove(detailRow)}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                  disabled={processing}
                >
                  {processing ? "…" : "Approve & Add"}
                </Button>
              </div>
            ) : (
              <Button variant="outline" onClick={() => setDetailRow(null)}>
                Close
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
