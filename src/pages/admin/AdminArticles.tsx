import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Search, X, Trash2, Edit, ChevronLeft, ChevronRight, Image as ImageIcon, ExternalLink } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { uploadImage, makeStoragePath } from "@/lib/adminUpload";

const sb = supabase as any;
const PAGE_SIZE = 25;

const CATEGORIES = [
  "news", "entertainment", "lifestyle", "sports", "health",
  "business", "technology", "opinion", "culture",
];

type ArticleRow = {
  id: string;
  headline: string;
  subheadline: string | null;
  body: string;
  vertical: string;
  category: string | null;
  status: string;
  image_url: string | null;
  slug: string | null;
  published_at: string | null;
  created_at: string;
};

export default function AdminArticles() {
  const [rows, setRows] = useState<ArticleRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [loading, setLoading] = useState(true);
  const [editRow, setEditRow] = useState<ArticleRow | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<ArticleRow | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb.from("p2_articles")
      .select("id,headline,subheadline,body,vertical,category,status,image_url,slug,published_at,created_at", { count: "exact" })
      .order("published_at", { ascending: false, nullsFirst: false });

    if (search) q = q.ilike("headline", `%${search}%`);
    if (filterCat !== "all") q = q.eq("category", filterCat);
    if (filterStatus !== "all") q = q.eq("status", filterStatus);

    q = q.range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1);

    const { data, count, error } = await q;
    if (error) { toast.error(error.message); setLoading(false); return; }
    setRows(data ?? []);
    setTotal(count ?? 0);
    setLoading(false);
  }, [page, search, filterCat, filterStatus]);

  useEffect(() => { load(); }, [load]);

  async function handleSave() {
    if (!editRow) return;
    setSaving(true);
    const { error } = await sb.from("p2_articles")
      .update({
        headline: editRow.headline,
        subheadline: editRow.subheadline,
        body: editRow.body,
        category: editRow.category,
        status: editRow.status,
        image_url: editRow.image_url,
      })
      .eq("id", editRow.id);
    setSaving(false);
    if (error) { toast.error(error.message); return; }
    toast.success("Article updated");
    setEditRow(null);
    load();
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    const { error } = await sb.from("p2_articles").delete().eq("id", deleteTarget.id);
    if (error) { toast.error(error.message); return; }
    toast.success("Article deleted");
    setDeleteTarget(null);
    load();
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!editRow || !e.target.files?.[0]) return;
    const file = e.target.files[0];
    const path = makeStoragePath("articles", editRow.slug || editRow.id, file);
    const url = await uploadImage("article-images", path, file);
    if (url) {
      setEditRow({ ...editRow, image_url: url });
      toast.success("Image uploaded");
    } else {
      toast.error("Upload failed");
    }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const fmtDate = (d: string | null) => d ? new Date(d).toLocaleDateString() : "—";

  return (
    <AdminLayout>
      <Helmet><title>Articles · Admin · The Videshi</title></Helmet>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-bold">Articles</h1>
          <p className="text-sm text-muted-foreground">{total} total</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by title..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            className="pl-9"
          />
          {search && (
            <button className="absolute right-3 top-1/2 -translate-y-1/2" onClick={() => setSearch("")}>
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          )}
        </div>
        <Select value={filterCat} onValueChange={(v) => { setFilterCat(v); setPage(0); }}>
          <SelectTrigger className="w-[160px]"><SelectValue placeholder="Category" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={(v) => { setFilterStatus(v); setPage(0); }}>
          <SelectTrigger className="w-[140px]"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="published">Published</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <div className="border border-border rounded-lg overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left p-3 font-medium">Image</th>
              <th className="text-left p-3 font-medium">Title</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">Category</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">Status</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Published</th>
              <th className="text-right p-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} className="border-t border-border"><td colSpan={6} className="p-3"><div className="h-10 bg-muted/30 rounded animate-pulse" /></td></tr>
              ))
            ) : rows.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-muted-foreground">No articles found</td></tr>
            ) : rows.map((row) => (
              <tr key={row.id} className="border-t border-border hover:bg-muted/20 transition-colors">
                <td className="p-3">
                  {row.image_url ? (
                    <img src={row.image_url} alt="" className="w-16 h-10 object-cover rounded" />
                  ) : (
                    <div className="w-16 h-10 bg-muted rounded flex items-center justify-center">
                      <ImageIcon className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </td>
                <td className="p-3 max-w-xs">
                  <p className="font-medium line-clamp-2">{row.headline}</p>
                </td>
                <td className="p-3 hidden md:table-cell">
                  <Badge variant="secondary" className="text-xs">{row.category || row.vertical}</Badge>
                </td>
                <td className="p-3 hidden md:table-cell">
                  <Badge variant={row.status === "published" ? "default" : "outline"} className="text-xs">
                    {row.status}
                  </Badge>
                </td>
                <td className="p-3 hidden lg:table-cell text-muted-foreground">{fmtDate(row.published_at)}</td>
                <td className="p-3 text-right">
                  <div className="flex justify-end gap-1">
                    {row.slug && (
                      <Button variant="ghost" size="icon" asChild>
                        <a href={`/articles/${row.slug}`} target="_blank" rel="noreferrer"><ExternalLink className="h-4 w-4" /></a>
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" onClick={() => setEditRow({ ...row })}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row)} className="text-red-400 hover:text-red-300">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
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

      {/* Edit Dialog */}
      <Dialog open={!!editRow} onOpenChange={(open) => !open && setEditRow(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Article</DialogTitle>
          </DialogHeader>
          {editRow && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Title</label>
                <Input
                  value={editRow.headline}
                  onChange={(e) => setEditRow({ ...editRow, headline: e.target.value })}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Subtitle</label>
                <Input
                  value={editRow.subheadline ?? ""}
                  onChange={(e) => setEditRow({ ...editRow, subheadline: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Category</label>
                  <Select value={editRow.category ?? ""} onValueChange={(v) => setEditRow({ ...editRow, category: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Status</label>
                  <Select value={editRow.status} onValueChange={(v) => setEditRow({ ...editRow, status: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="published">Published</SelectItem>
                      <SelectItem value="draft">Draft</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Hero Image</label>
                <div className="flex items-start gap-4">
                  {editRow.image_url ? (
                    <img src={editRow.image_url} alt="" className="w-32 h-20 object-cover rounded" />
                  ) : (
                    <div className="w-32 h-20 bg-muted rounded flex items-center justify-center">
                      <ImageIcon className="h-6 w-6 text-muted-foreground" />
                    </div>
                  )}
                  <div className="flex-1 space-y-2">
                    <Input type="file" accept="image/*" onChange={handleImageUpload} />
                    <Input
                      placeholder="Or paste image URL"
                      value={editRow.image_url ?? ""}
                      onChange={(e) => setEditRow({ ...editRow, image_url: e.target.value })}
                      className="text-xs"
                    />
                  </div>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Body</label>
                <Textarea
                  value={editRow.body}
                  onChange={(e) => setEditRow({ ...editRow, body: e.target.value })}
                  rows={12}
                  className="font-mono text-xs"
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditRow(null)}>Cancel</Button>
            <Button onClick={handleSave} disabled={saving}>{saving ? "Saving…" : "Save Changes"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Article</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Are you sure you want to delete "<strong>{deleteTarget?.headline}</strong>"? This cannot be undone.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDelete}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
