import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Article, formatShortDate, getPublishedArticles } from "@/lib/articles";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import HeroImage from "@/components/HeroImage";

const KEY_STORAGE = "videshi-admin-key";

export default function Admin() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [adminKey, setAdminKey] = useState<string>(
    () => (typeof window !== "undefined" ? localStorage.getItem(KEY_STORAGE) ?? "" : ""),
  );
  const [pendingId, setPendingId] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    const list = await getPublishedArticles();
    list.sort(
      (a, b) =>
        Number(b.is_pinned_featured ?? false) - Number(a.is_pinned_featured ?? false) ||
        (b.featured_score ?? 0) - (a.featured_score ?? 0),
    );
    setArticles(list);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  function saveKey(k: string) {
    setAdminKey(k);
    localStorage.setItem(KEY_STORAGE, k);
  }

  async function togglePin(article: Article) {
    if (!adminKey) {
      toast.error("Enter your admin key first");
      return;
    }
    const pin = !article.is_pinned_featured;
    setPendingId(article.id);
    const { data, error } = await supabase.functions.invoke("admin-pin-article", {
      body: { id: article.id, pin, hours: 24 },
      headers: { "x-admin-key": adminKey },
    });
    setPendingId(null);
    if (error || (data as any)?.error) {
      toast.error((data as any)?.error ?? error?.message ?? "Failed");
      return;
    }
    toast.success(pin ? "Pinned for 24h" : "Unpinned");
    load();
  }

  return (
    <div className="min-h-screen container py-8">
      <Helmet><title>Admin · Featured · The Videshi</title></Helmet>
      <h1 className="font-serif text-3xl mb-2">Featured Article Admin</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Pin an article as Featured for 24 hours. Otherwise the article with the highest
        featured score wins.
      </p>

      <div className="flex gap-2 items-center mb-8 max-w-md">
        <Input
          type="password"
          placeholder="Admin key"
          value={adminKey}
          onChange={(e) => saveKey(e.target.value)}
        />
        <Button variant="outline" onClick={load}>Refresh</Button>
      </div>

      {loading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <div className="grid gap-4">
          {articles.map((a) => {
            const pinned = !!a.is_pinned_featured && !!a.pinned_until && new Date(a.pinned_until) > new Date();
            return (
              <div
                key={a.id}
                className="flex gap-4 p-4 border border-border rounded-md items-start"
              >
                <div className="w-32 h-20 flex-shrink-0 overflow-hidden rounded">
                  <HeroImage src={a.hero_image_url} alt={a.title} loading="lazy" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="smallcaps text-primary">{a.category}</span>
                    {pinned && (
                      <span className="px-2 py-0.5 text-xs rounded bg-primary text-primary-foreground">
                        PINNED until {a.pinned_until ? formatShortDate(a.pinned_until) : ""}
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">
                      score {(a.featured_score ?? 0).toFixed(1)}
                    </span>
                  </div>
                  <h2 className="font-serif text-lg leading-snug">{a.title}</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatShortDate(a.published_at)}
                  </p>
                </div>
                <Button
                  variant={pinned ? "secondary" : "default"}
                  disabled={pendingId === a.id}
                  onClick={() => togglePin(a)}
                >
                  {pendingId === a.id ? "…" : pinned ? "Unpin" : "Pin as Featured"}
                </Button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
