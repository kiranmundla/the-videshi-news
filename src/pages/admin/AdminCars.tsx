import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Search, X, Trash2, Edit, ChevronLeft, ChevronRight, Image as ImageIcon, Star, ExternalLink } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { uploadImage, uploadMultipleImages } from "@/lib/adminUpload";
import { CAR_CATEGORIES } from "@/lib/cars";
import MultiImageManager from "@/components/admin/MultiImageManager";

const sb = supabase as any;
const PAGE_SIZE = 25;

type CarRow = {
  id: string;
  name: string;
  brand: string;
  model: string;
  slug: string;
  category: string;
  body_type: string | null;
  fuel_type: string | null;
  year: number;
  msrp_low: number | null;
  msrp_high: number | null;
  mpg: string | null;
  seating: number | null;
  nri_take: string | null;
  pros: string[] | null;
  cons: string[] | null;
  image_url: string | null;
  images: { url: string; caption?: string }[] | null;
  is_our_pick: boolean;
  lease_monthly: number | null;
  lease_due_at_signing: number | null;
};

export default function AdminCars() {
  const [rows, setRows] = useState<CarRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState("all");
  const [loading, setLoading] = useState(true);
  const [editRow, setEditRow] = useState<CarRow | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<CarRow | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb.from("cars")
      .select("id,name,brand,model,slug,category,body_type,fuel_type,year,msrp_low,msrp_high,mpg,seating,nri_take,pros,cons,image_url,images,is_our_pick,lease_monthly,lease_due_at_signing", { count: "exact" })
      .order("name");

    if (search) q = q.ilike("name", `%${search}%`);
    if (filterCat !== "all") q = q.eq("category", filterCat);
    q = q.range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1);

    const { data, count, error } = await q;
    if (error) { toast.error(error.message); setLoading(false); return; }
    setRows(data ?? []);
    setTotal(count ?? 0);
    setLoading(false);
  }, [page, search, filterCat]);

  useEffect(() => { load(); }, [load]);

  async function handleSave() {
    if (!editRow) return;
    setSaving(true);
    const { error } = await sb.from("cars")
      .update({
        name: editRow.name,
        brand: editRow.brand,
        model: editRow.model,
        category: editRow.category,
        body_type: editRow.body_type,
        fuel_type: editRow.fuel_type,
        year: editRow.year,
        msrp_low: editRow.msrp_low,
        msrp_high: editRow.msrp_high,
        mpg: editRow.mpg,
        seating: editRow.seating,
        nri_take: editRow.nri_take,
        pros: editRow.pros,
        cons: editRow.cons,
        image_url: editRow.image_url,
        images: editRow.images ?? [],
        is_our_pick: editRow.is_our_pick,
        lease_monthly: editRow.lease_monthly,
        lease_due_at_signing: editRow.lease_due_at_signing,
      })
      .eq("id", editRow.id);
    setSaving(false);
    if (error) { toast.error(error.message); return; }
    toast.success("Car updated");
    setEditRow(null);
    load();
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    const { error } = await sb.from("cars").delete().eq("id", deleteTarget.id);
    if (error) { toast.error(error.message); return; }
    toast.success("Car deleted");
    setDeleteTarget(null);
    load();
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!editRow || !e.target.files?.[0]) return;
    const file = e.target.files[0];
    const ext = file.name.split(".").pop()?.toLowerCase() ?? "jpg";
    const path = `cars/${editRow.slug}.${ext}`;
    const url = await uploadImage("article-images", path, file);
    if (url) {
      setEditRow({ ...editRow, image_url: url });
      toast.success("Image uploaded");
    } else {
      toast.error("Upload failed");
    }
  }

  const fmtPrice = (n: number | null) => n ? `$${n.toLocaleString()}` : "—";
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <AdminLayout>
      <Helmet><title>Cars · Admin · The Videshi</title></Helmet>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold">Cars</h1>
          <p className="text-sm text-muted-foreground">{total} total</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search cars..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} className="pl-9" />
          {search && <button className="absolute right-3 top-1/2 -translate-y-1/2" onClick={() => setSearch("")}><X className="h-4 w-4" /></button>}
        </div>
        <Select value={filterCat} onValueChange={(v) => { setFilterCat(v); setPage(0); }}>
          <SelectTrigger className="w-[150px]"><SelectValue placeholder="Category" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {CAR_CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <div className="border border-border rounded-lg overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left p-3 font-medium">Image</th>
              <th className="text-left p-3 font-medium">Name</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">Category</th>
              <th className="text-left p-3 font-medium hidden md:table-cell">MSRP</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Pick</th>
              <th className="text-right p-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} className="border-t border-border"><td colSpan={6} className="p-3"><div className="h-10 bg-muted/30 rounded animate-pulse" /></td></tr>
              ))
            ) : rows.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-muted-foreground">No cars found</td></tr>
            ) : rows.map((row) => (
              <tr key={row.id} className="border-t border-border hover:bg-muted/20 transition-colors">
                <td className="p-3">
                  {row.image_url ? (
                    <img src={row.image_url} alt="" className="w-20 h-12 object-contain rounded bg-muted/30" />
                  ) : (
                    <div className="w-20 h-12 bg-muted rounded flex items-center justify-center"><ImageIcon className="h-4 w-4 text-muted-foreground" /></div>
                  )}
                </td>
                <td className="p-3"><p className="font-medium">{row.name}</p></td>
                <td className="p-3 hidden md:table-cell"><Badge variant="secondary" className="text-xs">{row.category}</Badge></td>
                <td className="p-3 hidden md:table-cell text-muted-foreground">{fmtPrice(row.msrp_low)} – {fmtPrice(row.msrp_high)}</td>
                <td className="p-3 hidden lg:table-cell">
                  {row.is_our_pick && <Star className="h-4 w-4 text-amber-400 fill-amber-400" />}
                </td>
                <td className="p-3 text-right">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="icon" asChild>
                      <a href={`/cars/${row.slug}`} target="_blank" rel="noreferrer"><ExternalLink className="h-4 w-4" /></a>
                    </Button>
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
          <DialogHeader><DialogTitle>Edit Car</DialogTitle></DialogHeader>
          {editRow && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-sm font-medium mb-1 block">Name</label><Input value={editRow.name} onChange={(e) => setEditRow({ ...editRow, name: e.target.value })} /></div>
                <div><label className="text-sm font-medium mb-1 block">Brand</label><Input value={editRow.brand} onChange={(e) => setEditRow({ ...editRow, brand: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div><label className="text-sm font-medium mb-1 block">Model</label><Input value={editRow.model} onChange={(e) => setEditRow({ ...editRow, model: e.target.value })} /></div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Category</label>
                  <Select value={editRow.category} onValueChange={(v) => setEditRow({ ...editRow, category: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{CAR_CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div><label className="text-sm font-medium mb-1 block">Year</label><Input type="number" value={editRow.year} onChange={(e) => setEditRow({ ...editRow, year: Number(e.target.value) })} /></div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div><label className="text-sm font-medium mb-1 block">MSRP Low</label><Input type="number" value={editRow.msrp_low ?? ""} onChange={(e) => setEditRow({ ...editRow, msrp_low: e.target.value ? Number(e.target.value) : null })} /></div>
                <div><label className="text-sm font-medium mb-1 block">MSRP High</label><Input type="number" value={editRow.msrp_high ?? ""} onChange={(e) => setEditRow({ ...editRow, msrp_high: e.target.value ? Number(e.target.value) : null })} /></div>
                <div><label className="text-sm font-medium mb-1 block">MPG</label><Input value={editRow.mpg ?? ""} onChange={(e) => setEditRow({ ...editRow, mpg: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div><label className="text-sm font-medium mb-1 block">Seating</label><Input type="number" value={editRow.seating ?? ""} onChange={(e) => setEditRow({ ...editRow, seating: e.target.value ? Number(e.target.value) : null })} /></div>
                <div><label className="text-sm font-medium mb-1 block">Lease $/mo</label><Input type="number" value={editRow.lease_monthly ?? ""} onChange={(e) => setEditRow({ ...editRow, lease_monthly: e.target.value ? Number(e.target.value) : null })} /></div>
                <div><label className="text-sm font-medium mb-1 block">Due at signing</label><Input type="number" value={editRow.lease_due_at_signing ?? ""} onChange={(e) => setEditRow({ ...editRow, lease_due_at_signing: e.target.value ? Number(e.target.value) : null })} /></div>
              </div>
              <MultiImageManager
                label="Car Images (first = hero)"
                images={(() => {
                  const list: { url: string; caption?: string }[] = [];
                  if (editRow.image_url) list.push({ url: editRow.image_url, caption: "Hero" });
                  if (editRow.images) {
                    for (const img of editRow.images) {
                      if (img.url !== editRow.image_url) list.push(img);
                    }
                  }
                  return list;
                })()}
                onChange={(imgs) => {
                  setEditRow({
                    ...editRow,
                    image_url: imgs[0]?.url ?? null,
                    images: imgs,
                  });
                }}
                onUpload={async (files) => {
                  return await uploadMultipleImages("article-images", "cars", editRow.slug, files);
                }}
                maxImages={10}
              />
              <div>
                <label className="text-sm font-medium mb-1 block">NRI Take</label>
                <Textarea value={editRow.nri_take ?? ""} onChange={(e) => setEditRow({ ...editRow, nri_take: e.target.value })} rows={3} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Pros (one per line)</label>
                  <Textarea value={(editRow.pros ?? []).join("\n")} onChange={(e) => setEditRow({ ...editRow, pros: e.target.value.split("\n").filter(Boolean) })} rows={4} />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Cons (one per line)</label>
                  <Textarea value={(editRow.cons ?? []).join("\n")} onChange={(e) => setEditRow({ ...editRow, cons: e.target.value.split("\n").filter(Boolean) })} rows={4} />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Switch checked={editRow.is_our_pick} onCheckedChange={(v) => setEditRow({ ...editRow, is_our_pick: v })} />
                <label className="text-sm font-medium">Our Pick</label>
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
          <DialogHeader><DialogTitle>Delete Car</DialogTitle></DialogHeader>
          <p className="text-sm text-muted-foreground">Delete "<strong>{deleteTarget?.name}</strong>"? This cannot be undone.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDelete}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
