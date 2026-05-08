import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { VERTICAL_COLORS, URGENCY_COLORS, scoreColor, relTime } from "./shared";

export default function ReviewQueuePage() {
  const qc = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: articles = [], isLoading } = useQuery({
    queryKey: ["pipeline-review"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("articles_pipeline")
        .select("*, topics(score_total, signal_count, urgency, vertical)")
        .eq("status", "review")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data ?? [];
    },
  });

  useEffect(() => {
    if (!selectedId && articles.length > 0) setSelectedId(articles[0].id);
  }, [articles, selectedId]);

  const selected = (articles as any[]).find((a) => a.id === selectedId) ?? null;

  if (!isLoading && articles.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="font-serif text-3xl font-bold">Review Queue</h1>
        <div className="border border-border rounded-md p-12 bg-card text-center text-muted-foreground">
          Pipeline is clear — no articles awaiting review.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="font-serif text-3xl font-bold">Review Queue</h1>
      <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-4">
        <div className="space-y-2 max-h-[80vh] overflow-auto pr-1">
          {(articles as any[]).map((a) => {
            const urgency = a.urgency ?? a.topics?.urgency ?? "daily";
            const border = urgency === "breaking" ? "border-l-red-600" : urgency === "daily" ? "border-l-yellow-400" : "border-l-gray-300";
            return (
              <button
                key={a.id}
                onClick={() => setSelectedId(a.id)}
                className={`w-full text-left border border-border border-l-4 ${border} rounded-md p-3 bg-card hover:bg-muted/40 transition ${selectedId === a.id ? "ring-2 ring-primary" : ""}`}
              >
                <div className="font-serif font-semibold text-sm line-clamp-2">{a.headline}</div>
                <div className="flex flex-wrap items-center gap-1.5 mt-2">
                  <Badge variant="outline" className={VERTICAL_COLORS[a.vertical] ?? ""}>{a.vertical}</Badge>
                  <Badge className={URGENCY_COLORS[urgency] ?? ""}>{urgency}</Badge>
                  {a.topics?.score_total != null && <span className={"text-xs " + scoreColor(a.topics.score_total)}>{a.topics.score_total}</span>}
                  <span className="text-xs text-muted-foreground">· {a.topics?.signal_count ?? 0} signals</span>
                </div>
                <div className="text-[11px] text-muted-foreground mt-1">{relTime(a.created_at)}</div>
              </button>
            );
          })}
        </div>

        {selected && <ArticleDetail article={selected} onSaved={() => qc.invalidateQueries({ queryKey: ["pipeline-review"] })} />}
      </div>
    </div>
  );
}

function ArticleDetail({ article, onSaved }: { article: any; onSaved: () => void }) {
  const [headline, setHeadline] = useState(article.headline ?? "");
  const [subheadline, setSubheadline] = useState(article.subheadline ?? "");
  const [body, setBody] = useState(article.body ?? "");
  const [diaspora, setDiaspora] = useState(article.diaspora_angle ?? "");
  const [tags, setTags] = useState<string[]>(article.tags ?? []);
  const [tagInput, setTagInput] = useState("");
  const [sendBeehiiv, setSendBeehiiv] = useState(false);
  const [showBeehiiv, setShowBeehiiv] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setHeadline(article.headline ?? "");
    setSubheadline(article.subheadline ?? "");
    setBody(article.body ?? "");
    setDiaspora(article.diaspora_angle ?? "");
    setTags(article.tags ?? []);
    setShowBeehiiv(false);
    setSendBeehiiv(false);
  }, [article.id]);

  const wordCount = body.trim().split(/\s+/).filter(Boolean).length;

  async function save(extra: Record<string, any> = {}, msg = "Saved") {
    setSaving(true);
    const { error } = await supabase
      .from("articles_pipeline")
      .update({ headline, subheadline, body, diaspora_angle: diaspora, tags, word_count: wordCount, ...extra })
      .eq("id", article.id);
    setSaving(false);
    if (error) toast.error(error.message);
    else { toast.success(msg); onSaved(); }
  }

  function addTag() {
    const t = tagInput.trim();
    if (!t) return;
    if (!tags.includes(t)) setTags([...tags, t]);
    setTagInput("");
  }

  return (
    <div className="border border-border rounded-md bg-card p-5 space-y-4">
      <Input className="font-serif text-2xl font-bold h-auto py-2" value={headline} onChange={e => setHeadline(e.target.value)} />
      <Input className="text-base" value={subheadline} onChange={e => setSubheadline(e.target.value)} placeholder="Subheadline" />

      <div>
        <Label className="text-xs">Body ({wordCount} words)</Label>
        <Textarea value={body} onChange={e => setBody(e.target.value)} className="min-h-[300px] article-prose" />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded p-3">
        <Label className="text-xs text-blue-900">Diaspora Angle</Label>
        <Textarea value={diaspora} onChange={e => setDiaspora(e.target.value)} className="bg-white" />
      </div>

      <div>
        <Label className="text-xs">Tags</Label>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {tags.map(t => (
            <Badge key={t} variant="secondary" className="cursor-pointer" onClick={() => setTags(tags.filter(x => x !== t))}>
              {t} ×
            </Badge>
          ))}
        </div>
        <Input
          value={tagInput}
          onChange={e => setTagInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); addTag(); } }}
          placeholder="Add tag, press Enter"
        />
      </div>

      <div>
        <Label className="text-xs">Sources</Label>
        <ul className="text-xs space-y-1">
          {(article.sources ?? []).map((s: any, i: number) => (
            <li key={i}>
              <a href={typeof s === "string" ? s : s.url} target="_blank" rel="noreferrer" className="text-primary hover:underline">
                {typeof s === "string" ? s : (s.title ?? s.url)}
              </a>
            </li>
          ))}
          {(article.sources ?? []).length === 0 && <li className="text-muted-foreground">none</li>}
        </ul>
      </div>

      {showBeehiiv && (
        <div className="flex items-center gap-2 border border-border rounded p-2">
          <Switch checked={sendBeehiiv} onCheckedChange={setSendBeehiiv} id="bh" />
          <Label htmlFor="bh" className="text-sm">Send to Beehiiv on publish</Label>
        </div>
      )}

      <div className="flex gap-2 border-t border-border pt-3">
        <Button
          onClick={async () => {
            await save({ status: "published", published_at: new Date().toISOString(), reviewed_at: new Date().toISOString() }, "Published");
            setShowBeehiiv(true);
            if (sendBeehiiv) toast.success("Queued for Beehiiv");
          }}
          disabled={saving}
        >Approve & Publish</Button>
        <Button variant="outline" onClick={() => save({}, "Edits saved")} disabled={saving}>Save Edits</Button>
        <Button variant="destructive" onClick={() => save({ status: "rejected", reviewed_at: new Date().toISOString() }, "Rejected")} disabled={saving}>Reject</Button>
      </div>
    </div>
  );
}
