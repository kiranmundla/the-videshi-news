import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Search, X, Trash2, Edit, ChevronLeft, ChevronRight, Image as ImageIcon, Ban, ExternalLink } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { CLASSIFIED_CATEGORIES } from "@/lib/classifieds";
import { uploadMultipleImages } from "@/lib/adminUpload";
import MultiImageManager from "@/components/admin/MultiImageManager";

const sb = supabase as any;
const PAGE_SIZE = 25;

type ClassifiedRow = {
  id: string;
  title: string;
  description: string | null;
  category: string;
  subcategory: string | null;
  price: string | null;
  city: string | null;
  state: string | null;
  contact_email: string | null;
  status: string;
  source: string | null;
  slug: string;
  image_url: string | null;
  photos: string[];
  created_at: string;
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-900/40 text-green-300",
  expired: "bg-red-900/40 text-red-300",
  flagged: "bg-yellow-900/40 text-yellow-300",
};

export default function AdminClassifieds() {
  const [rows, setRows] = useState<ClassifiedRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [loading, setLoading] = useState(true);
  const [editRow, setEditRow] = useState<ClassifiedRow | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<ClassifiedRow | null>(null);

  const categories = [...CLASSIFIED_CATEGORIES];

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb.from("classifieds")
      .select("id,title,description,category,subcategory,price,city,state,contact_email,status,source,slug,image_url,photos,created_at", { count: "exact" })
      .order("created_at", { ascending: false });

    if (search) q = q.ilike("title", `%${search}%`);
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
    const { error } = await sb.from("classifieds")
      .update({
        title: editRow.title,
        description: editRow.description,
        category: editRow.category,
        subcategory: editRow.subcategory,
        price: editRow.price,
        city: editRow.city,
        state: editRow.state,
        status: editRow.status,
      })
      .eq("id", editRow.id);
    setSaving(false);
    if (error) { toast.error(error.message); return; }
    toast.success("Classified updated");
    setEditRow(null);
    load();
  }

  async function handleTakeDown(row: ClassifiedRow) {
    const { error } = await sb.from("classifieds").update({ status: "expired" }).eq("id", row.id);
    if (error) { toast.error(error.message); return; }
    toast.success("Listing taken down");
    load();
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    const { error } = await sb.from("classifieds").delete().eq("id", deleteTarget.id);
    if (error) { toast.error(error.message); return; }
    toast.success("Classified deleted");
    setDeleteTarget(null);
    load();
  }

  const fmtDate = (d: string) => new Date(d).toLocaleDateString();
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <AdminLayout>
      <Helmet><title>Classifieds · Admin · The Videshi</title></Helmet>
      <div className="flex items-center justify-between mb-4">
        <div><h1 className="text-xl font-bold">Classifieds</h1><p className="text-sm text-muted-foreground">{total} total</p></div>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search classifieds..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} className="pl-9" />
          {search && <button className="absolute right-3 top-1/2 -translate-y-1/2" onClick={() => setSearch("")}><X className="h-4 w-4" /></button>}
        </div>
        <Select value={filterCat} onValueChange={(v) => { setFilterCat(v); setPage(0); }}>
          <SelectTrigger className="w-[160px]"><SelectValue placeholder="Category" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {categories.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={(v) => { setFilterStatus(v); setPage(0); }}>
          <SelectTrigger className="w-[140px]"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="expired">Expired</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="border border-border rounded-lg overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left p-3 font-medium">Title</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">Category</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">City</th>
              <th className="text-left p-3 font-medium">Status</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Source</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Created</th>
              <th className="text-right p-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (<tr key={i} className="border-t border-border"><td colSpan={7} className="p-3"><div className="h-10 bg-muted/30 rounded animate-pulse" /></td></tr>))
            ) : rows.length === 0 ? (
              <tr><td colSpan={7} className="p-8 text-center text-muted-foreground">No classifieds found</td></tr>
            ) : rows.map((row) => (
              <tr key={row.id} className="border-t border-border hover:bg-muted/20 transition-colors">
                <td className="p-3 max-w-xs"><p className="font-medium line-clamp-2">{row.title}</p></td>
                <td className="p-3 hidden md:table-cell"><Badge variant="secondary" className="text-xs">{row.category}</Badge></td>
                <td className="p-3 hidden md:table-cell">{row.city}{row.state ? `, ${row.state}` : ""}</td>
                <td className="p-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[row.status] ?? "bg-muted text-muted-foreground"}`}>
                    {row.status}
                  </span>
                </td>
                <td className="p-3 hidden lg:table-cell"><Badge variant="outline" className="text-xs">{row.source ?? "user"}</Badge></td>
                <td className="p-3 hidden lg:table-cell text-muted-foreground">{fmtDate(row.created_at)}</td>
                <td className="p-3 text-right">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="icon" asChild>
                      <a href={`/classifieds/${row.slug}`} target="_blank" rel="noreferrer"><ExternalLink className="h-4 w-4" /></a>
                    </Button>
                    {row.status === "active" && (
                      <Button variant="ghost" size="icon" onClick={() => handleTakeDown(row)} title="Take down" className="text-yellow-400 hover:text-yellow-300">
                        <Ban className="h-4 w-4" />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" onClick={() => setEditRow({ ...row })}><Edit className="h-4 w-4" /></Button>
                    <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row)} className="text-red-400 hover:text-red-300"><Trash2 className="h-4 w-4" /></Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-muted-foreground">Page {page + 1} of {totalPages}</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(page - 1)}><ChevronLeft className="h-4 w-4 mr-1" /> Prev</Button>
            <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}>Next <ChevronRight className="h-4 w-4 ml-1" /></Button>
          </div>
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!editRow} onOpenChange={(open) => !open && setEditRow(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle>Edit Classified</DialogTitle></DialogHeader>
          {editRow && (
            <div className="space-y-4">
              <div><label className="text-sm font-medium mb-1 block">Title</label><Input value={editRow.title} onChange={(e) => setEditRow({ ...editRow, title: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Category</label>
                  <Select value={editRow.category} onValueChange={(v) => setEditRow({ ...editRow, category: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{categories.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Status</label>
                  <Select value={editRow.status} onValueChange={(v) => setEditRow({ ...editRow, status: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="expired">Expired</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-sm font-medium mb-1 block">City</label><Input value={editRow.city ?? ""} onChange={(e) => setEditRow({ ...editRow, city: e.target.value })} /></div>
                <div><label className="text-sm font-medium mb-1 block">State</label><Input value={editRow.state ?? ""} onChange={(e) => setEditRow({ ...editRow, state: e.target.value })} /></div>
              </div>
              <div><label className="text-sm font-medium mb-1 block">Price</label><Input value={editRow.price ?? ""} onChange={(e) => setEditRow({ ...editRow, price: e.target.value })} /></div>
              <div><label className="text-sm font-medium mb-1 block">Description</label><Textarea value={editRow.description ?? ""} onChange={(e) => setEditRow({ ...editRow, description: e.target.value })} rows={6} /></div>
              <MultiImageManager
                label="Photos"
                images={(editRow.photos ?? []).map((p: any) => typeof p === "string" ? { url: p } : p)}
                onChange={(imgs) => setEditRow({ ...editRow, photos: imgs.map((i: any) => i.url || i), image_url: imgs[0]?.url ?? editRow.image_url })}
                onUpload={async (files) => {
                  return await uploadMultipleImages("article-images", "classifieds", editRow.slug || editRow.id, files);
                }}
                maxImages={10}
              />
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditRow(null)}>Cancel</Button>
            <Button onClick={handleSave} disabled={saving}>{saving ? "Saving…" : "Save Changes"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Delete Classified</DialogTitle></DialogHeader>
          <p className="text-sm text-muted-foreground">Delete "<strong>{deleteTarget?.title}</strong>"? This cannot be undone.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDelete}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
