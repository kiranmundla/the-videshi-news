import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Helmet } from "react-helmet-async";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, SheetFooter,
} from "@/components/ui/sheet";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import { toast } from "sonner";
import { Plus, Trash2, Pause, Play } from "lucide-react";
import { relTime } from "@/pages/pipeline/shared";
import { adminWrite } from "@/lib/adminWrite";

const VERTICALS = [
  "politics", "economy", "tech", "immigration", "diaspora",
  "science", "culture", "sports", "world",
] as const;

const STAGE_VARIANT: Record<string, string> = {
  discovery: "bg-orange-100 text-orange-900 border-orange-200",
  primary: "bg-teal-100 text-teal-900 border-teal-200",
  image: "bg-purple-100 text-purple-900 border-purple-200",
  enrichment: "bg-blue-100 text-blue-900 border-blue-200",
  monitoring: "bg-yellow-100 text-yellow-900 border-yellow-200",
};

const TYPE_VARIANT: Record<string, string> = {
  rss: "bg-emerald-100 text-emerald-900 border-emerald-200",
  scrape: "bg-yellow-100 text-yellow-900 border-yellow-200",
  api: "bg-blue-100 text-blue-900 border-blue-200",
};

const LICENSE_VARIANT: Record<string, string> = {
  public_domain: "bg-emerald-100 text-emerald-900 border-emerald-200",
  discovery_only: "bg-red-100 text-red-900 border-red-200",
  cc_by: "bg-teal-100 text-teal-900 border-teal-200",
  press_release: "bg-blue-100 text-blue-900 border-blue-200",
  api_terms: "bg-gray-100 text-gray-900 border-gray-200",
};

const STAGES = ["discovery", "primary", "image", "enrichment", "monitoring"] as const;

function slugify(s: string) {
  return s.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export default function SourcesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [stage, setStage] = useState("all");
  const [type, setType] = useState("all");
  const [vertical, setVertical] = useState("all");
  const [status, setStatus] = useState("all");
  const [search, setSearch] = useState("");

  const { data: rows = [], isLoading } = useQuery({
    queryKey: ["videshi_sources"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("videshi_sources")
        .select("*")
        .order("priority", { ascending: true });
      if (error) throw error;
      return data ?? [];
    },
  });

  const counts = useMemo(() => {
    const c = { active: 0, discovery: 0, primary: 0, image: 0, enrichment: 0, monitoring: 0 };
    for (const r of rows as any[]) {
      if (r.is_active) c.active++;
      if (r.pipeline_stage in c) (c as any)[r.pipeline_stage]++;
    }
    return c;
  }, [rows]);

  const types = useMemo(
    () => Array.from(new Set((rows as any[]).map(r => r.source_type))).sort(),
    [rows],
  );

  const filtered = (rows as any[]).filter(r => {
    if (stage !== "all" && r.pipeline_stage !== stage) return false;
    if (type !== "all" && r.source_type !== type) return false;
    if (vertical !== "all" && !(r.verticals ?? []).includes(vertical)) return false;
    if (status !== "all" && r.is_active !== (status === "active")) return false;
    if (search && !r.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  async function toggleActive(row: any) {
    qc.setQueryData(["videshi_sources"], (old: any[] = []) =>
      old.map(r => r.id === row.id ? { ...r, is_active: !row.is_active } : r));
    const { error } = await adminWrite({
      table: "videshi_sources", op: "update", id: row.id,
      payload: { is_active: !row.is_active },
    });
    if (error) {
      toast.error(error);
      qc.invalidateQueries({ queryKey: ["videshi_sources"] });
    }
  }

  async function deleteRow(id: string) {
    if (!confirm("Delete this source? This cannot be undone.")) return;
    const { error } = await adminWrite({ table: "videshi_sources", op: "delete", id });
    if (error) toast.error(error);
    else {
      toast.success("Deleted");
      qc.invalidateQueries({ queryKey: ["videshi_sources"] });
    }
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <Helmet><title>Source Registry · Admin</title></Helmet>

      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-serif text-3xl font-bold">Source Registry</h1>
          <div className="flex flex-wrap gap-1.5 mt-2 text-xs">
            <Badge variant="outline">{counts.active} active</Badge>
            <Badge variant="outline" className={STAGE_VARIANT.discovery}>{counts.discovery} discovery</Badge>
            <Badge variant="outline" className={STAGE_VARIANT.primary}>{counts.primary} primary</Badge>
            <Badge variant="outline" className={STAGE_VARIANT.image}>{counts.image} image</Badge>
            <Badge variant="outline" className={STAGE_VARIANT.enrichment}>{counts.enrichment} enrichment</Badge>
            <Badge variant="outline" className={STAGE_VARIANT.monitoring}>{counts.monitoring} monitoring</Badge>
          </div>
        </div>
        <Sheet open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditing(null); }}>
          <SheetTrigger asChild>
            <Button onClick={() => setEditing(null)}>
              <Plus className="h-4 w-4 mr-1" /> Add Source
            </Button>
          </SheetTrigger>
          <SourceFormSheet row={editing} onSaved={() => {
            setOpen(false); setEditing(null);
            qc.invalidateQueries({ queryKey: ["videshi_sources"] });
          }} />
        </Sheet>
      </div>

      <Tabs defaultValue="registry">
        <TabsList>
          <TabsTrigger value="registry">Registry</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="registry" className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            <Select value={stage} onValueChange={setStage}>
              <SelectTrigger className="w-[150px]"><SelectValue placeholder="Stage" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All stages</SelectItem>
                {STAGES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={type} onValueChange={setType}>
              <SelectTrigger className="w-[150px]"><SelectValue placeholder="Type" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All types</SelectItem>
                {types.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={vertical} onValueChange={setVertical}>
              <SelectTrigger className="w-[160px]"><SelectValue placeholder="Vertical" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All verticals</SelectItem>
                {VERTICALS.map(v => <SelectItem key={v} value={v}>{v}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-[130px]"><SelectValue placeholder="Status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
              </SelectContent>
            </Select>
            <Input
              className="w-[220px]"
              placeholder="Search by name…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          <div className="border border-border rounded-md bg-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Slug</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Verticals</TableHead>
                  <TableHead>Pri</TableHead>
                  <TableHead>License</TableHead>
                  <TableHead>Active</TableHead>
                  <TableHead>Last Fetched</TableHead>
                  <TableHead>Errors</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading && (
                  <TableRow><TableCell colSpan={11} className="text-center py-8 text-muted-foreground">Loading…</TableCell></TableRow>
                )}
                {!isLoading && filtered.length === 0 && (
                  <TableRow><TableCell colSpan={11} className="text-center py-8 text-muted-foreground">No sources match filters.</TableCell></TableRow>
                )}
                {filtered.map((r: any) => {
                  const verts = r.verticals ?? [];
                  return (
                    <TableRow key={r.id}>
                      <TableCell className="font-medium">{r.name}</TableCell>
                      <TableCell className="font-mono text-[11px] text-muted-foreground">{r.slug}</TableCell>
                      <TableCell><Badge variant="outline" className={TYPE_VARIANT[r.source_type] ?? ""}>{r.source_type}</Badge></TableCell>
                      <TableCell><Badge variant="outline" className={STAGE_VARIANT[r.pipeline_stage] ?? ""}>{r.pipeline_stage}</Badge></TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {verts.slice(0, 3).map((v: string) => (
                            <span key={v} className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{v}</span>
                          ))}
                          {verts.length > 3 && <span className="text-[10px] text-muted-foreground">+{verts.length - 3}</span>}
                        </div>
                      </TableCell>
                      <TableCell className="tabular-nums text-sm">{r.priority}</TableCell>
                      <TableCell>
                        {r.license_type
                          ? <Badge variant="outline" className={LICENSE_VARIANT[r.license_type] ?? ""}>{r.license_type}</Badge>
                          : <span className="text-xs text-muted-foreground">—</span>}
                      </TableCell>
                      <TableCell><Switch checked={r.is_active} onCheckedChange={() => toggleActive(r)} /></TableCell>
                      <TableCell className="text-xs text-muted-foreground">{relTime(r.last_fetched_at)}</TableCell>
                      <TableCell className={`text-sm tabular-nums ${r.consecutive_errors > 0 ? "text-destructive font-bold" : "text-muted-foreground"}`}>
                        {r.consecutive_errors ?? 0}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button size="sm" variant="ghost" onClick={() => { setEditing(r); setOpen(true); }}>Edit</Button>
                          <Button size="icon" variant="ghost" title={r.is_active ? "Pause" : "Resume"} onClick={() => toggleActive(r)}>
                            {r.is_active ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                          </Button>
                          <Button size="icon" variant="ghost" onClick={() => deleteRow(r.id)}>
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <PerformanceTab sources={rows as any[]} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ───────────────────── Performance Tab ─────────────────────
function PerformanceTab({ sources }: { sources: any[] }) {
  const { data: logs = [] } = useQuery({
    queryKey: ["videshi_source_logs_7d"],
    queryFn: async () => {
      const since = new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString();
      const { data, error } = await supabase
        .from("videshi_source_logs")
        .select("*")
        .gte("fetched_at", since)
        .limit(1000);
      if (error) throw error;
      return data ?? [];
    },
  });

  const stats = useMemo(() => {
    const map = new Map<string, {
      name: string; fetched: number; accepted: number;
      errors: number; total: number; durationSum: number; durationCount: number;
    }>();
    const idToName = new Map(sources.map(s => [s.id, s.name]));
    for (const l of logs as any[]) {
      const name = idToName.get(l.source_id) ?? "(deleted)";
      const cur = map.get(l.source_id) ?? {
        name, fetched: 0, accepted: 0, errors: 0, total: 0, durationSum: 0, durationCount: 0,
      };
      cur.fetched += l.items_fetched ?? 0;
      cur.accepted += l.items_accepted ?? 0;
      cur.total += 1;
      if (l.status === "error") cur.errors += 1;
      if (l.duration_ms != null) { cur.durationSum += l.duration_ms; cur.durationCount += 1; }
      map.set(l.source_id, cur);
    }
    return Array.from(map.values()).map(s => ({
      ...s,
      acceptRate: s.fetched ? Math.round((s.accepted / s.fetched) * 100) : 0,
      errorRate: s.total ? Math.round((s.errors / s.total) * 100) : 0,
      avgMs: s.durationCount ? Math.round(s.durationSum / s.durationCount) : 0,
    })).sort((a, b) => b.fetched - a.fetched);
  }, [logs, sources]);

  if (stats.length === 0) {
    return <p className="text-sm text-muted-foreground py-8 text-center">No fetch logs in the last 7 days yet.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="border border-border rounded-md bg-card p-4">
        <h3 className="font-semibold mb-3">Items fetched per source (last 7 days)</h3>
        <ResponsiveContainer width="100%" height={Math.max(220, stats.length * 28)}>
          <BarChart data={stats} layout="vertical" margin={{ left: 80, right: 24 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="fetched" fill="hsl(var(--primary))" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="border border-border rounded-md bg-card overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Source</TableHead>
              <TableHead className="text-right">Runs</TableHead>
              <TableHead className="text-right">Fetched</TableHead>
              <TableHead className="text-right">Accepted</TableHead>
              <TableHead className="text-right">Accept %</TableHead>
              <TableHead className="text-right">Error %</TableHead>
              <TableHead className="text-right">Avg duration</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {stats.map(s => (
              <TableRow key={s.name}>
                <TableCell className="font-medium">{s.name}</TableCell>
                <TableCell className="text-right tabular-nums">{s.total}</TableCell>
                <TableCell className="text-right tabular-nums">{s.fetched}</TableCell>
                <TableCell className="text-right tabular-nums">{s.accepted}</TableCell>
                <TableCell className="text-right tabular-nums">{s.acceptRate}%</TableCell>
                <TableCell className={`text-right tabular-nums ${s.errorRate > 20 ? "text-destructive font-semibold" : ""}`}>{s.errorRate}%</TableCell>
                <TableCell className="text-right tabular-nums">{s.avgMs}ms</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

// ───────────────────── Form Sheet ─────────────────────
function SourceFormSheet({ row, onSaved }: { row: any | null; onSaved: () => void }) {
  const [name, setName] = useState(row?.name ?? "");
  const [slug, setSlug] = useState(row?.slug ?? "");
  const [slugTouched, setSlugTouched] = useState(!!row);
  const [description, setDescription] = useState(row?.description ?? "");
  const [sourceType, setSourceType] = useState(row?.source_type ?? "rss");
  const [pipelineStage, setPipelineStage] = useState(row?.pipeline_stage ?? "discovery");
  const [verticals, setVerticals] = useState<string[]>(row?.verticals ?? []);
  const [skipVerticals, setSkipVerticals] = useState<string[]>(row?.skip_verticals ?? []);
  const [categories, setCategories] = useState<string>((row?.categories ?? []).join(", "));
  const [endpointUrl, setEndpointUrl] = useState(row?.endpoint_url ?? "");
  const [apiKeySecret, setApiKeySecret] = useState(row?.api_key_secret ?? "");
  const [requiresProxy, setRequiresProxy] = useState(!!row?.requires_proxy);
  const [proxyType, setProxyType] = useState(row?.proxy_type ?? "");
  const [priority, setPriority] = useState<number>(row?.priority ?? 50);
  const [interval, setInterval] = useState<number>(row?.fetch_interval_min ?? 60);
  const [maxItems, setMaxItems] = useState<number>(row?.max_items ?? 20);
  const [licenseType, setLicenseType] = useState(row?.license_type ?? "");
  const [requiresAttribution, setRequiresAttribution] = useState(!!row?.requires_attribution);
  const [attributionText, setAttributionText] = useState(row?.attribution_text ?? "");
  const [notes, setNotes] = useState(row?.notes ?? "");
  const [isActive, setIsActive] = useState(row?.is_active ?? true);
  const [saving, setSaving] = useState(false);

  function onName(v: string) {
    setName(v);
    if (!slugTouched) setSlug(slugify(v));
  }

  function toggle(arr: string[], setArr: (a: string[]) => void, v: string) {
    setArr(arr.includes(v) ? arr.filter(x => x !== v) : [...arr, v]);
  }

  async function save() {
    if (!name.trim() || !slug.trim()) return toast.error("Name and slug required");
    setSaving(true);
    const payload: any = {
      name, slug, description: description || null,
      source_type: sourceType, pipeline_stage: pipelineStage,
      verticals, skip_verticals: skipVerticals,
      categories: categories.split(",").map(s => s.trim()).filter(Boolean),
      endpoint_url: endpointUrl || null,
      api_key_secret: apiKeySecret || null,
      requires_proxy: requiresProxy, proxy_type: proxyType || null,
      priority, fetch_interval_min: interval, max_items: maxItems,
      license_type: licenseType || null,
      requires_attribution: requiresAttribution,
      attribution_text: attributionText || null,
      notes: notes || null,
      is_active: isActive,
    };
    const res = row
      ? await adminWrite({ table: "videshi_sources", op: "update", id: row.id, payload })
      : await adminWrite({ table: "videshi_sources", op: "insert", payload });
    setSaving(false);
    if (res.error) return toast.error(res.error);
    toast.success(row ? "Updated" : "Added");
    onSaved();
  }

  function VerticalsField({ value, onChange, label }: { value: string[]; onChange: (a: string[]) => void; label: string }) {
    return (
      <div>
        <Label>{label}</Label>
        <div className="flex flex-wrap gap-1.5 mt-1">
          {VERTICALS.map(v => (
            <button
              key={v}
              type="button"
              onClick={() => toggle(value, onChange, v)}
              className={`text-xs px-2 py-1 rounded border ${value.includes(v) ? "bg-primary text-primary-foreground border-primary" : "bg-background border-border"}`}
            >{v}</button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <SheetContent className="w-full sm:max-w-xl overflow-y-auto">
      <SheetHeader><SheetTitle>{row ? "Edit Source" : "Add Source"}</SheetTitle></SheetHeader>

      <div className="space-y-6 py-4">
        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Identity</h3>
          <div><Label>Name</Label><Input value={name} onChange={e => onName(e.target.value)} /></div>
          <div>
            <Label>Slug</Label>
            <Input value={slug} onChange={e => { setSlug(e.target.value); setSlugTouched(true); }} className="font-mono text-sm" />
          </div>
          <div><Label>Description</Label><Textarea rows={2} value={description} onChange={e => setDescription(e.target.value)} /></div>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Type</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Source type</Label>
              <Input value={sourceType} onChange={e => setSourceType(e.target.value)} placeholder="rss / scrape / api / img_unsplash" />
            </div>
            <div>
              <Label>Pipeline stage</Label>
              <Select value={pipelineStage} onValueChange={setPipelineStage}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {STAGES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Targeting</h3>
          <VerticalsField value={verticals} onChange={setVerticals} label="Good for verticals" />
          <VerticalsField value={skipVerticals} onChange={setSkipVerticals} label="Skip for verticals" />
          <div><Label>Categories (comma-separated)</Label><Input value={categories} onChange={e => setCategories(e.target.value)} /></div>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Access</h3>
          <div><Label>Endpoint URL</Label><Input value={endpointUrl} onChange={e => setEndpointUrl(e.target.value)} /></div>
          <div><Label>API key secret name</Label><Input value={apiKeySecret} onChange={e => setApiKeySecret(e.target.value)} placeholder="UNSPLASH_ACCESS_KEY" /></div>
          <div className="flex items-center gap-3">
            <Switch checked={requiresProxy} onCheckedChange={setRequiresProxy} />
            <Label>Requires proxy</Label>
          </div>
          {requiresProxy && (
            <div><Label>Proxy type</Label><Input value={proxyType} onChange={e => setProxyType(e.target.value)} /></div>
          )}
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Operations</h3>
          <div className="grid grid-cols-3 gap-3">
            <div><Label>Priority</Label><Input type="number" value={priority} onChange={e => setPriority(Number(e.target.value))} /></div>
            <div><Label>Interval (min)</Label><Input type="number" value={interval} onChange={e => setInterval(Number(e.target.value))} /></div>
            <div><Label>Max items</Label><Input type="number" value={maxItems} onChange={e => setMaxItems(Number(e.target.value))} /></div>
          </div>
          <div className="flex items-center gap-3">
            <Switch checked={isActive} onCheckedChange={setIsActive} />
            <Label>Active</Label>
          </div>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Legal</h3>
          <div>
            <Label>License type</Label>
            <Select value={licenseType || "none"} onValueChange={v => setLicenseType(v === "none" ? "" : v)}>
              <SelectTrigger><SelectValue placeholder="Select…" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">—</SelectItem>
                <SelectItem value="public_domain">public_domain</SelectItem>
                <SelectItem value="cc_by">cc_by</SelectItem>
                <SelectItem value="press_release">press_release</SelectItem>
                <SelectItem value="discovery_only">discovery_only</SelectItem>
                <SelectItem value="api_terms">api_terms</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-3">
            <Switch checked={requiresAttribution} onCheckedChange={setRequiresAttribution} />
            <Label>Requires attribution</Label>
          </div>
          {requiresAttribution && (
            <div><Label>Attribution text</Label><Input value={attributionText} onChange={e => setAttributionText(e.target.value)} /></div>
          )}
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Notes</h3>
          <Textarea rows={3} value={notes} onChange={e => setNotes(e.target.value)} />
        </section>
      </div>

      <SheetFooter>
        <Button onClick={save} disabled={saving}>{saving ? "Saving…" : "Save"}</Button>
      </SheetFooter>
    </SheetContent>
  );
}
