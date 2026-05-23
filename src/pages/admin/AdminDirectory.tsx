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
import { DIRECTORY_CATEGORIES } from "@/lib/directory";
import MultiImageManager from "@/components/admin/MultiImageManager";

const sb = supabase as any;
const PAGE_SIZE = 25;

type DirRow = {
  id: string;
  name: string;
  category: string;
  subcategory: string | null;
  description: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip: string | null;
  image_url: string | null;
  photos: { url: string; caption?: string }[] | null;
  rating: number | null;
  review_count: number | null;
  verified: boolean;
  featured: boolean;
  slug: string;
  created_at: string;
};

export default function AdminDirectory() {
  const [rows, setRows] = useState<DirRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState("all");
  const [loading, setLoading] = useState(true);
  const [editRow, setEditRow] = useState<DirRow | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<DirRow | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    let q = sb.from("directory_listings")
      .select("id,name,category,subcategory,description,phone,email,website,address,city,state,zip,image_url,photos,rating,review_count,verified,featured,slug,created_at", { count: "exact" })
      .order("name");

    if (search) q = q.or(`name.ilike.%${search}%,city.ilike.%${search}%`);
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
    const { error } = await sb.from("directory_listings")
      .update({
        name: editRow.name,
        category: editRow.category,
        subcategory: editRow.subcategory,
        description: editRow.description,
        phone: editRow.phone,
        email: editRow.email,
        website: editRow.website,
        address: editRow.address,
        city: editRow.city,
        state: editRow.state,
        zip: editRow.zip,
        image_url: editRow.image_url,
        photos: editRow.photos ?? [],
        rating: editRow.rating,
        review_count: editRow.review_count,
        verified: editRow.verified,
        featured: editRow.featured,
      })
      .eq("id", editRow.id);
    setSaving(false);
    if (error) { toast.error(error.message); return; }
    toast.success("Listing updated");
    setEditRow(null);
    load();
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    const { error } = await sb.from("directory_listings").delete().eq("id", deleteTarget.id);
    if (error) { toast.error(error.message); return; }
    toast.success("Listing deleted");
    setDeleteTarget(null);
    load();
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!editRow || !e.target.files?.[0]) return;
    const file = e.target.files[0];
    const ext = file.name.split(".").pop()?.toLowerCase() ?? "jpg";
    const path = `directory/${editRow.slug}.${ext}`;
    const url = await uploadImage("article-images", path, file);
    if (url) { setEditRow({ ...editRow, image_url: url }); toast.success("Image uploaded"); }
    else toast.error("Upload failed");
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <AdminLayout>
      <Helmet><title>Directory · Admin · The Videshi</title></Helmet>
      <div className="flex items-center justify-between mb-4">
        <div><h1 className="text-xl font-bold">Directory Listings</h1><p className="text-sm text-muted-foreground">{total} total</p></div>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search by name or city..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} className="pl-9" />
          {search && <button className="absolute right-3 top-1/2 -translate-y-1/2" onClick={() => setSearch("")}><X className="h-4 w-4" /></button>}
        </div>
        <Select value={filterCat} onValueChange={(v) => { setFilterCat(v); setPage(0); }}>
          <SelectTrigger className="w-[200px]"><SelectValue placeholder="Category" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {DIRECTORY_CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
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
              <th className="text-left p-3 font-medium hidden md:table-cell">City</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Rating</th>
              <th className="text-left p-3 font-medium hidden lg:table-cell">Reviews</th>
              <th className="text-right p-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (<tr key={i} className="border-t border-border"><td colSpan={7} className="p-3"><div className="h-10 bg-muted/30 rounded animate-pulse" /></td></tr>))
            ) : rows.length === 0 ? (
              <tr><td colSpan={7} className="p-8 text-center text-muted-foreground">No listings found</td></tr>
            ) : rows.map((row) => (
              <tr key={row.id} className="border-t border-border hover:bg-muted/20 transition-colors">
                <td className="p-3">
                  {row.image_url ? (<img src={row.image_url} alt="" className="w-16 h-10 object-cover rounded" />) : (<div className="w-16 h-10 bg-muted rounded flex items-center justify-center"><ImageIcon className="h-4 w-4 text-muted-foreground" /></div>)}
                </td>
                <td className="p-3 max-w-xs">
                  <p className="font-medium line-clamp-1">{row.name}</p>
                  {row.verified && <Badge variant="secondary" className="text-xs mt-0.5">Verified</Badge>}
                </td>
                <td className="p-3 hidden md:table-cell"><Badge variant="secondary" className="text-xs">{row.category}</Badge></td>
                <td className="p-3 hidden md:table-cell">{row.city}{row.state ? `, ${row.state}` : ""}</td>
                <td className="p-3 hidden lg:table-cell">
                  {row.rating ? (
                    <span className="flex items-center gap-1"><Star className="h-3 w-3 text-amber-400 fill-amber-400" />{row.rating.toFixed(1)}</span>
                  ) : "—"}
                </td>
                <td className="p-3 hidden lg:table-cell text-muted-foreground">{row.review_count ?? 0}</td>
                <td className="p-3 text-right">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="icon" asChild><a href={`/directory/${row.slug}`} target="_blank" rel="noreferrer"><ExternalLink className="h-4 w-4" /></a></Button>
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
          <DialogHeader><DialogTitle>Edit Listing</DialogTitle></DialogHeader>
          {editRow && (
            <div className="space-y-4">
              <div><label className="text-sm font-medium mb-1 block">Name</label><Input value={editRow.name} onChange={(e) => setEditRow({ ...editRow, name: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Category</label>
                  <Select value={editRow.category} onValueChange={(v) => setEditRow({ ...editRow, category: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{DIRECTORY_CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div><label className="text-sm font-medium mb-1 block">Subcategory</label><Input value={editRow.subcategory ?? ""} onChange={(e) => setEditRow({ ...editRow, subcategory: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-sm font-medium mb-1 block">Phone</label><Input value={editRow.phone ?? ""} onChange={(e) => setEditRow({ ...editRow, phone: e.target.value })} /></div>
                <div><label className="text-sm font-medium mb-1 block">Email</label><Input value={editRow.email ?? ""} onChange={(e) => setEditRow({ ...editRow, email: e.target.value })} /></div>
              </div>
              <div><label className="text-sm font-medium mb-1 block">Website</label><Input value={editRow.website ?? ""} onChange={(e) => setEditRow({ ...editRow, website: e.target.value })} /></div>
              <div><label className="text-sm font-medium mb-1 block">Address</label><Input value={editRow.address ?? ""} onChange={(e) => setEditRow({ ...editRow, address: e.target.value })} /></div>
              <div className="grid grid-cols-3 gap-4">
                <div><label className="text-sm font-medium mb-1 block">City</label><Input value={editRow.city ?? ""} onChange={(e) => setEditRow({ ...editRow, city: e.target.value })} /></div>
                <div><label className="text-sm font-medium mb-1 block">State</label><Input value={editRow.state ?? ""} onChange={(e) => setEditRow({ ...editRow, state: e.target.value })} /></div>
                <div><label className="text-sm font-medium mb-1 block">ZIP</label><Input value={editRow.zip ?? ""} onChange={(e) => setEditRow({ ...editRow, zip: e.target.value })} /></div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Cover Image</label>
                <div className="flex items-start gap-4">
                  {editRow.image_url ? (<img src={editRow.image_url} alt="" className="w-32 h-20 object-cover rounded" />) : (<div className="w-32 h-20 bg-muted rounded flex items-center justify-center"><ImageIcon className="h-6 w-6 text-muted-foreground" /></div>)}
                  <div className="flex-1 space-y-2">
                    <Input type="file" accept="image/*" onChange={handleImageUpload} />
                    <Input placeholder="Or paste image URL" value={editRow.image_url ?? ""} onChange={(e) => setEditRow({ ...editRow, image_url: e.target.value })} className="text-xs" />
                  </div>
                </div>
              </div>
              <MultiImageManager
                label="Business Photos"
                images={(editRow.photos ?? []).map((v: any) => typeof v === "string" ? { url: v } : v)}
                onChange={(imgs) => setEditRow({ ...editRow, photos: imgs })}
                onUpload={async (files) => {
                  return await uploadMultipleImages("article-images", "directory", editRow.slug || editRow.id, files);
                }}
                maxImages={10}
              />
              <div><label className="text-sm font-medium mb-1 block">Description</label><Textarea value={editRow.description ?? ""} onChange={(e) => setEditRow({ ...editRow, description: e.target.value })} rows={4} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-sm font-medium mb-1 block">Rating</label><Input type="number" step="0.1" min="0" max="5" value={editRow.rating ?? ""} onChange={(e) => setEditRow({ ...editRow, rating: e.target.value ? Number(e.target.value) : null })} /></div>
                <div><label className="text-sm font-medium mb-1 block">Review Count</label><Input type="number" value={editRow.review_count ?? ""} onChange={(e) => setEditRow({ ...editRow, review_count: e.target.value ? Number(e.target.value) : null })} /></div>
              </div>
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-3">
                  <Switch checked={editRow.verified} onCheckedChange={(v) => setEditRow({ ...editRow, verified: v })} />
                  <label className="text-sm font-medium">Verified</label>
                </div>
                <div className="flex items-center gap-3">
                  <Switch checked={editRow.featured} onCheckedChange={(v) => setEditRow({ ...editRow, featured: v })} />
                  <label className="text-sm font-medium">Featured</label>
                </div>
              </div>
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
          <DialogHeader><DialogTitle>Delete Listing</DialogTitle></DialogHeader>
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
