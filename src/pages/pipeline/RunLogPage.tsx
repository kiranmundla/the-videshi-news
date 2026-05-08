import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import { Play } from "lucide-react";
import { relTime } from "./shared";

const PAGE_SIZE = 20;

export default function RunLogPage() {
  const { data: logs = [], isLoading } = useQuery({
    queryKey: ["pipeline_run_log"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("pipeline_run_log")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(PAGE_SIZE);
      if (error) throw error;
      return data ?? [];
    },
  });

  const { data: counts } = useQuery({
    queryKey: ["pipeline-counts"],
    queryFn: async () => {
      const today = new Date(); today.setHours(0, 0, 0, 0);
      const iso = today.toISOString();
      const [signals, topics, articles, published] = await Promise.all([
        supabase.from("raw_signals").select("*", { count: "exact", head: true }).gte("fetched_at", iso),
        supabase.from("topics").select("*", { count: "exact", head: true }).gte("created_at", iso),
        supabase.from("articles_pipeline").select("*", { count: "exact", head: true }).gte("created_at", iso),
        supabase.from("articles_pipeline").select("*", { count: "exact", head: true }).eq("status", "published").gte("published_at", iso),
      ]);
      return {
        signals: signals.count ?? 0,
        topics: topics.count ?? 0,
        articles: articles.count ?? 0,
        published: published.count ?? 0,
      };
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-3xl font-bold">Run Log</h1>
          <p className="text-sm text-muted-foreground">Pipeline activity history</p>
        </div>
        <Button onClick={() => toast.success("Pipeline triggered")}>
          <Play className="h-4 w-4 mr-1" /> Run Pipeline Now
        </Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="Signals today" value={counts?.signals ?? 0} />
        <Stat label="Topics ranked" value={counts?.topics ?? 0} />
        <Stat label="Articles synthesized" value={counts?.articles ?? 0} />
        <Stat label="Published" value={counts?.published ?? 0} />
      </div>

      <div className="border border-border rounded-md bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Stage</TableHead>
              <TableHead>Items</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Notes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && <TableRow><TableCell colSpan={5} className="text-center py-8 text-muted-foreground">Loading…</TableCell></TableRow>}
            {!isLoading && logs.length === 0 && (
              <TableRow><TableCell colSpan={5} className="text-center py-8 text-muted-foreground">No runs logged yet.</TableCell></TableRow>
            )}
            {(logs as any[]).map((l) => (
              <TableRow key={l.id}>
                <TableCell className="text-xs text-muted-foreground">{relTime(l.created_at)}</TableCell>
                <TableCell><Badge variant="outline">{l.stage}</Badge></TableCell>
                <TableCell>{l.items_processed}</TableCell>
                <TableCell>
                  <Badge className={l.status === "success" ? "bg-emerald-200 text-emerald-900" : "bg-red-200 text-red-900"}>
                    {l.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs text-muted-foreground max-w-md truncate">{l.notes}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-border rounded-md p-3 bg-card">
      <div className="text-xs uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="text-2xl font-serif font-bold">{value}</div>
    </div>
  );
}
