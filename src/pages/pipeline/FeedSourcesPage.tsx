import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Copy, Plus, Trash2 } from "lucide-react";
import { VERTICALS, relTime } from "./shared";

const TYPE_VARIANT: Record<string, string> = {
  rss: "bg-emerald-100 text-emerald-900 border-emerald-200",
  scrape: "bg-yellow-100 text-yellow-900 border-yellow-200",
  api: "bg-blue-100 text-blue-900 border-blue-200",
};
const LAYER_VARIANT: Record<string, string> = {
  discovery: "bg-orange-100 text-orange-900 border-orange-200",
  primary: "bg-teal-100 text-teal-900 border-teal-200",
};

const PAGE_SIZE = 20;

export default function FeedSourcesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [filterLayer, setFilterLayer] = useState<string>("all");
  const [filterVertical, setFilterVertical] = useState<string>("all");
  const [filterTier, setFilterTier] = useState<string>("all");
  const [filterActive, setFilterActive] = useState<string>("all");
  const [page, setPage] = useState(1);

  const { data: rows = [], isLoading } = useQuery({
    queryKey: ["p2_feed_sources"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("p2_feed_sources")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  const filtered = rows.filter((r: any) => {
    if (filterLayer !== "all" && r.layer !== filterLayer) return false;
    if (filterTier !== "all" && r.tier !== filterTier) return false;
    if (filterActive !== "all" && r.is_active !== (filterActive === "active")) return false;
    if (filterVertical !== "all" && !(r.verticals ?? []).includes(filterVertical)) return false;
    return true;
  });
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageRows = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const activeCount = rows.filter((r: any) => r.is_active).length;

  async function toggleActive(row: any) {
    qc.setQueryData(["p2_feed_sources"], (old: any[] = []) =>
      old.map((r) => (r.id === row.id ? { ...r, is_active: !row.is_active } : r))
    );
    const { error } = await supabase
      .from("p2_feed_sources")
      .update({ is_active: !row.is_active })
      .eq("id", row.id);
    if (error) {
      toast.error("Failed to toggle");
      qc.invalidateQueries({ queryKey: ["p2_feed_sources"] });
    }
  }

  async function deleteRow(id: string) {
    if (!confirm("Delete this feed?")) return;
    const { error } = await supabase.from("p2_feed_sources").delete().eq("id", id);
    if (error) toast.error(error.message);
    else {
      toast.success("Deleted");
      qc.invalidateQueries({ queryKey: ["p2_feed_sources"] });
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-3xl font-bold">Feed Sources</h1>
          <p className="text-sm text-muted-foreground">
            {rows.length} total · {activeCount} active
          </p>
        </div>
        <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditing(null); }}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditing(null)}>
              <Plus className="h-4 w-4 mr-1" /> Add Feed
            </Button>
          </DialogTrigger>
          <FeedFormDialog
            row={editing}
            onSaved={() => {
              setOpen(false);
              setEditing(null);
              qc.invalidateQueries({ queryKey: ["p2_feed_sources"] });
            }}
          />
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <Select value={filterLayer} onValueChange={setFilterLayer}>
          <SelectTrigger className="w-[140px]"><SelectValue placeholder="Layer" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All layers</SelectItem>
            <SelectItem value="discovery">Discovery</SelectItem>
            <SelectItem value="primary">Primary</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterVertical} onValueChange={setFilterVertical}>
          <SelectTrigger className="w-[160px]"><SelectValue placeholder="Vertical" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All verticals</SelectItem>
            {VERTICALS.map((v) => <SelectItem key={v} value={v}>{v}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterTier} onValueChange={setFilterTier}>
          <SelectTrigger className="w-[120px]"><SelectValue placeholder="Tier" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All tiers</SelectItem>
            <SelectItem value="A">A</SelectItem>
            <SelectItem value="B">B</SelectItem>
            <SelectItem value="C">C</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterActive} onValueChange={setFilterActive}>
          <SelectTrigger className="w-[120px]"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="border border-border rounded-md bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>URL</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Layer</TableHead>
              <TableHead>Tier</TableHead>
              <TableHead>Verticals</TableHead>
              <TableHead>Active</TableHead>
              <TableHead>Last Fetched</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow><TableCell colSpan={9} className="text-center py-8 text-muted-foreground">Loading…</TableCell></TableRow>
            )}
            {!isLoading && pageRows.length === 0 && (
              <TableRow><TableCell colSpan={9} className="text-center py-8 text-muted-foreground">No feeds yet. Add one to get started.</TableCell></TableRow>
            )}
            {pageRows.map((r: any) => (
              <TableRow key={r.id}>
                <TableCell className="font-medium">{r.name}</TableCell>
                <TableCell className="max-w-[240px]">
                  <div className="flex items-center gap-1">
                    <span className="truncate text-xs text-muted-foreground">{r.url}</span>
                    <Button size="icon" variant="ghost" className="h-6 w-6 shrink-0"
                      onClick={() => { navigator.clipboard.writeText(r.url); toast.success("Copied"); }}>
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </TableCell>
                <TableCell><Badge variant="outline" className={TYPE_VARIANT[r.type] ?? ""}>{r.type}</Badge></TableCell>
                <TableCell><Badge variant="outline" className={LAYER_VARIANT[r.layer] ?? ""}>{r.layer}</Badge></TableCell>
                <TableCell><Badge variant="outline">{r.tier}</Badge></TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {(r.verticals ?? []).map((v: string) => (
                      <span key={v} className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{v}</span>
                    ))}
                  </div>
                </TableCell>
                <TableCell><Switch checked={r.is_active} onCheckedChange={() => toggleActive(r)} /></TableCell>
                <TableCell className="text-xs text-muted-foreground">{relTime(r.last_fetched_at)}</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" onClick={() => { setEditing(r); setOpen(true); }}>Edit</Button>
                    <Button size="icon" variant="ghost" onClick={() => deleteRow(r.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="flex justify-end items-center gap-2 text-sm">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Prev</Button>
          <span>Page {page} / {totalPages}</span>
          <Button variant="outline" size="sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next</Button>
        </div>
      )}
    </div>
  );
}

function FeedFormDialog({ row, onSaved }: { row: any | null; onSaved: () => void }) {
  const [name, setName] = useState(row?.name ?? "");
  const [url, setUrl] = useState(row?.url ?? "");
  const [type, setType] = useState(row?.type ?? "rss");
  const [layer, setLayer] = useState(row?.layer ?? "discovery");
  const [tier, setTier] = useState(row?.tier ?? "B");
  const [interval, setInterval] = useState<number>(row?.fetch_interval_min ?? 60);
  const [verticals, setVerticals] = useState<string[]>(row?.verticals ?? []);
  const [saving, setSaving] = useState(false);

  function toggleV(v: string) {
    setVerticals((prev) => prev.includes(v) ? prev.filter(x => x !== v) : [...prev, v]);
  }

  async function save() {
    if (!name || !url) return toast.error("Name and URL required");
    setSaving(true);
    const payload = { name, url, type, layer, tier, verticals, fetch_interval_min: interval };
    const res = row
      ? await supabase.from("p2_feed_sources").update(payload).eq("id", row.id)
      : await supabase.from("p2_feed_sources").insert(payload);
    setSaving(false);
    if (res.error) return toast.error(res.error.message);
    toast.success(row ? "Updated" : "Added");
    onSaved();
  }

  return (
    <DialogContent className="max-w-lg">
      <DialogHeader><DialogTitle>{row ? "Edit Feed" : "Add Feed"}</DialogTitle></DialogHeader>
      <div className="space-y-3">
        <div><Label>Name</Label><Input value={name} onChange={e => setName(e.target.value)} /></div>
        <div><Label>URL</Label><Input value={url} onChange={e => setUrl(e.target.value)} /></div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Type</Label>
            <Select value={type} onValueChange={setType}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="rss">RSS</SelectItem>
                <SelectItem value="scrape">Scrape</SelectItem>
                <SelectItem value="api">API</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Layer</Label>
            <Select value={layer} onValueChange={setLayer}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="discovery">Discovery</SelectItem>
                <SelectItem value="primary">Primary</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Tier</Label>
            <Select value={tier} onValueChange={setTier}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="A">A</SelectItem>
                <SelectItem value="B">B</SelectItem>
                <SelectItem value="C">C</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Interval (min)</Label>
            <Input type="number" value={interval} onChange={e => setInterval(Number(e.target.value))} />
          </div>
        </div>
        <div>
          <Label>Verticals</Label>
          <div className="flex flex-wrap gap-1.5 mt-1">
            {VERTICALS.map(v => (
              <button
                key={v}
                type="button"
                onClick={() => toggleV(v)}
                className={`text-xs px-2 py-1 rounded border ${verticals.includes(v) ? "bg-primary text-primary-foreground border-primary" : "bg-background border-border"}`}
              >{v}</button>
            ))}
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button onClick={save} disabled={saving}>{saving ? "Saving…" : "Save"}</Button>
      </DialogFooter>
    </DialogContent>
  );
}
