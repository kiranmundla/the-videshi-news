import { Fragment as FragmentRow, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, MoreHorizontal } from "lucide-react";
import { toast } from "sonner";
import { VERTICALS, VERTICAL_COLORS, URGENCY_COLORS, STATUS_COLORS, scoreColor, relTime } from "./shared";
import { adminWrite } from "@/lib/adminWrite";

const PAGE_SIZE = 20;

export default function TopicRadarPage() {
  const [filterVertical, setFilterVertical] = useState("all");
  const [filterUrgency, setFilterUrgency] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [sortBy, setSortBy] = useState<"score" | "date" | "signals">("score");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const { data: topics = [], isLoading, refetch } = useQuery({
    queryKey: ["p2_topics"],
    queryFn: async () => {
      const { data, error } = await supabase.from("p2_topics").select("*");
      if (error) throw error;
      return data;
    },
  });

  const { data: summary } = useQuery({
    queryKey: ["p2_topics-summary"],
    queryFn: async () => {
      const today = new Date(); today.setHours(0, 0, 0, 0);
      const { data } = await supabase.from("p2_topics").select("status, created_at");
      const todays = (data ?? []).filter((t: any) => new Date(t.created_at) >= today);
      const byStatus = (s: string) => (data ?? []).filter((t: any) => t.status === s).length;
      return {
        today: todays.length,
        pending: byStatus("pending"),
        review: byStatus("review"),
        published: byStatus("published"),
        rejected: byStatus("rejected"),
      };
    },
  });

  const filtered = (topics as any[]).filter((t) => {
    if (filterVertical !== "all" && t.vertical !== filterVertical) return false;
    if (filterUrgency !== "all" && t.urgency !== filterUrgency) return false;
    if (filterStatus !== "all" && t.status !== filterStatus) return false;
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "date") return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    if (sortBy === "signals") return (b.signal_count ?? 0) - (a.signal_count ?? 0);
    return (b.score_total ?? 0) - (a.score_total ?? 0);
  });

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const pageRows = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  async function reject(id: string) {
    const { error } = await adminWrite({ table: "p2_topics", op: "update", id, payload: { status: "rejected" } });
    if (error) toast.error(error);
    else { toast.success("Marked rejected"); refetch(); }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-serif text-3xl font-bold">Topic Radar</h1>
        <p className="text-sm text-muted-foreground">Ranked queue of discovered topics</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <SummaryCard label="Today" value={summary?.today ?? 0} />
        <SummaryCard label="Pending" value={summary?.pending ?? 0} />
        <SummaryCard label="In Review" value={summary?.review ?? 0} />
        <SummaryCard label="Published" value={summary?.published ?? 0} />
        <SummaryCard label="Rejected" value={summary?.rejected ?? 0} />
      </div>

      <div className="flex flex-wrap gap-2">
        <Select value={filterVertical} onValueChange={setFilterVertical}>
          <SelectTrigger className="w-[160px]"><SelectValue placeholder="Vertical" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All verticals</SelectItem>
            {VERTICALS.map(v => <SelectItem key={v} value={v}>{v}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterUrgency} onValueChange={setFilterUrgency}>
          <SelectTrigger className="w-[140px]"><SelectValue placeholder="Urgency" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All urgencies</SelectItem>
            <SelectItem value="breaking">Breaking</SelectItem>
            <SelectItem value="daily">Daily</SelectItem>
            <SelectItem value="evergreen">Evergreen</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[140px]"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {["pending","hunting","synthesizing","review","published","rejected"].map(s =>
              <SelectItem key={s} value={s}>{s}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
          <SelectTrigger className="w-[140px]"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="score">Sort: Score</SelectItem>
            <SelectItem value="date">Sort: Date</SelectItem>
            <SelectItem value="signals">Sort: Signals</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="border border-border rounded-md bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">#</TableHead>
              <TableHead className="w-16">Score</TableHead>
              <TableHead>Topic</TableHead>
              <TableHead>Vertical</TableHead>
              <TableHead>Urgency</TableHead>
              <TableHead>Signals</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && <TableRow><TableCell colSpan={9} className="text-center py-8 text-muted-foreground">Loading…</TableCell></TableRow>}
            {!isLoading && pageRows.length === 0 && (
              <TableRow><TableCell colSpan={9} className="text-center py-8 text-muted-foreground">No topics yet.</TableCell></TableRow>
            )}
            {pageRows.map((t: any, i: number) => (
              <FragmentRow key={t.id}>
                <TableRow className="cursor-pointer" onClick={() => setExpanded(expanded === t.id ? null : t.id)}>
                  <TableCell className="text-muted-foreground">{(page - 1) * PAGE_SIZE + i + 1}</TableCell>
                  <TableCell className={scoreColor(t.score_total)}>{t.score_total ?? "—"}</TableCell>
                  <TableCell className="font-medium max-w-md">{t.canonical_title}</TableCell>
                  <TableCell><Badge variant="outline" className={VERTICAL_COLORS[t.vertical] ?? ""}>{t.vertical}</Badge></TableCell>
                  <TableCell><Badge className={URGENCY_COLORS[t.urgency] ?? ""}>{t.urgency}</Badge></TableCell>
                  <TableCell>{t.signal_count}</TableCell>
                  <TableCell><Badge className={STATUS_COLORS[t.status] ?? ""}>{t.status}</Badge></TableCell>
                  <TableCell className="text-xs text-muted-foreground">{relTime(t.created_at)}</TableCell>
                  <TableCell onClick={e => e.stopPropagation()}>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild><Button size="icon" variant="ghost"><MoreHorizontal className="h-4 w-4" /></Button></DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem onClick={() => setExpanded(t.id)}>View Signals</DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setExpanded(t.id)}>View Source Hunts</DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setExpanded(t.id)}>View Article</DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive" onClick={() => reject(t.id)}>Mark Rejected</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
                {expanded === t.id && (
                  <TableRow>
                    <TableCell colSpan={9} className="bg-muted/30 p-4">
                      <ExpandedTopic topic={t} />
                    </TableCell>
                  </TableRow>
                )}
              </FragmentRow>
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

function SummaryCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-border rounded-md p-3 bg-card">
      <div className="text-xs uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="text-2xl font-serif font-bold">{value}</div>
    </div>
  );
}

function ExpandedTopic({ topic }: { topic: any }) {
  const { data: signals = [] } = useQuery({
    queryKey: ["p2_signals", topic.id],
    queryFn: async () => {
      const { data } = await supabase.from("p2_signals").select("*, p2_feed_sources(name)").eq("topic_id", topic.id);
      return data ?? [];
    },
  });
  const { data: hunts = [] } = useQuery({
    queryKey: ["p2_source_hunts", topic.id],
    queryFn: async () => {
      const { data } = await supabase.from("p2_source_hunts").select("*, p2_feed_sources(name)").eq("topic_id", topic.id);
      return data ?? [];
    },
  });
  const { data: article } = useQuery({
    queryKey: ["p2_articles", topic.id],
    queryFn: async () => {
      const { data } = await supabase.from("p2_articles").select("*").eq("topic_id", topic.id).maybeSingle();
      return data;
    },
  });

  return (
    <div className="grid md:grid-cols-2 gap-4 text-sm">
      <div className="space-y-3">
        <div>
          <div className="font-semibold mb-1">Score Breakdown</div>
          <div className="grid grid-cols-2 gap-1 text-xs">
            <div>Diaspora: <b>{topic.score_diaspora ?? "—"}</b></div>
            <div>Significance: <b>{topic.score_significance ?? "—"}</b></div>
            <div>Recency: <b>{topic.score_recency ?? "—"}</b></div>
            <div>Source Avail: <b>{topic.score_source_avail ?? "—"}</b></div>
          </div>
        </div>
        <div>
          <div className="font-semibold mb-1">Keywords</div>
          <div className="flex flex-wrap gap-1">
            {(topic.keywords ?? []).map((k: string) => <span key={k} className="text-xs px-1.5 py-0.5 rounded bg-muted">{k}</span>)}
            {(topic.keywords ?? []).length === 0 && <span className="text-xs text-muted-foreground">none</span>}
          </div>
        </div>
        <div>
          <div className="font-semibold mb-1">Signals ({signals.length})</div>
          <ul className="space-y-1 text-xs max-h-40 overflow-auto">
            {signals.map((s: any) => (
              <li key={s.id}>
                <a href={s.original_url} target="_blank" rel="noreferrer" className="hover:underline">{s.title}</a>
                <span className="text-muted-foreground"> · {s.feed_sources?.name ?? "?"}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="space-y-3">
        <div>
          <div className="font-semibold mb-1">Source Hunts ({hunts.length})</div>
          <ul className="space-y-2 text-xs max-h-60 overflow-auto">
            {hunts.map((h: any) => (
              <li key={h.id} className="border border-border rounded p-2 bg-background">
                <div className="flex justify-between">
                  <a href={h.url} target="_blank" rel="noreferrer" className="font-medium hover:underline">{h.title}</a>
                  <span className="text-muted-foreground">{h.relevance_score?.toFixed(2) ?? "—"}</span>
                </div>
                <div className="text-muted-foreground mt-1 line-clamp-2">{h.content}</div>
              </li>
            ))}
          </ul>
        </div>
        {article && (
          <div>
            <div className="font-semibold mb-1">Article</div>
            <div className="border border-border rounded p-2 bg-background text-xs">
              <div className="font-medium">{article.headline}</div>
              <div className="text-muted-foreground">{article.subheadline}</div>
              <Badge className={"mt-1 " + (STATUS_COLORS[article.status] ?? "")}>{article.status}</Badge>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
