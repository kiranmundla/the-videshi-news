// Ingest articles from The Conversation India Atom feed into the `articles` table.
// Public endpoint (verify_jwt = false). Uses the service role key to bypass RLS.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";
import { XMLParser } from "npm:fast-xml-parser@4.5.0";
import TurndownService from "npm:turndown@7.2.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const FEED_URL =
  "https://theconversation.com/topics/india-1429/articles.atom";

const turndown = new TurndownService({
  headingStyle: "atx",
  codeBlockStyle: "fenced",
  bulletListMarker: "-",
});
// Preserve ![alt](url) markdown image syntax
turndown.addRule("img", {
  filter: "img",
  replacement: (_c, node) => {
    const el = node as unknown as { getAttribute(n: string): string | null };
    const src = el.getAttribute("src") || "";
    const alt = el.getAttribute("alt") || "";
    return src ? `\n\n![${alt}](${src})\n\n` : "";
  },
});

function slugify(title: string): string {
  return title
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 80);
}

async function shortHash(input: string): Promise<string> {
  const buf = await crypto.subtle.digest(
    "SHA-1",
    new TextEncoder().encode(input),
  );
  return Array.from(new Uint8Array(buf))
    .slice(0, 3)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function firstImageUrl(html: string): string | null {
  const re = /<img[^>]+src=["']([^"']+)["']/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) {
    const url = m[1];
    // Skip tracking pixels and counters
    if (/counter\.|\/count\.gif|pixel|tracking|1x1|\.gif(\?|$)/i.test(url)) continue;
    return url;
  }
  return null;
}

function buildExcerpt(markdown: string): string {
  const para = markdown
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .find(
      (p) =>
        p &&
        !p.startsWith("#") &&
        !p.startsWith("![") &&
        !p.startsWith(">"),
    );
  const text = (para ?? "").replace(/[*_`>#-]+/g, "").replace(/\s+/g, " ").trim();
  return text.length > 200 ? text.slice(0, 197).trimEnd() + "..." : text;
}

function asArray<T>(v: T | T[] | undefined | null): T[] {
  if (v == null) return [];
  return Array.isArray(v) ? v : [v];
}

function pickLink(entry: Record<string, unknown>): string | null {
  const links = asArray(entry.link as unknown);
  for (const l of links) {
    if (typeof l === "string") return l;
    if (l && typeof l === "object") {
      const obj = l as Record<string, string>;
      const rel = obj["@_rel"];
      if (!rel || rel === "alternate") return obj["@_href"] || null;
    }
  }
  return null;
}

function pickAuthor(entry: Record<string, unknown>): string | null {
  const dc = entry["dc:creator"];
  if (typeof dc === "string" && dc.trim()) return dc.trim();
  const author = entry.author as
    | { name?: string }
    | { name?: string }[]
    | undefined;
  const a = Array.isArray(author) ? author[0] : author;
  return a?.name?.trim() || null;
}

function pickContent(entry: Record<string, unknown>): string {
  const c = entry.content as
    | string
    | { "#text"?: string; "@_type"?: string }
    | undefined;
  if (typeof c === "string") return c;
  return c?.["#text"] ?? "";
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const errors: string[] = [];
  let ingested = 0;
  let skipped = 0;

  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const res = await fetch(FEED_URL, {
      headers: { "User-Agent": "Videshi-Ingest/1.0 (+supabase-edge)" },
    });
    if (!res.ok) {
      return new Response(
        JSON.stringify({ error: `Feed fetch failed: ${res.status}` }),
        {
          status: 502,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }
    const xml = await res.text();

    const parser = new XMLParser({
      ignoreAttributes: false,
      attributeNamePrefix: "@_",
      trimValues: true,
    });
    const parsed = parser.parse(xml);
    const entries = asArray<Record<string, unknown>>(parsed?.feed?.entry);

    for (const entry of entries) {
      try {
        const title = (entry.title as string | { "#text"?: string }) ?? "";
        const titleStr =
          typeof title === "string" ? title : (title["#text"] ?? "");
        const sourceUrl = pickLink(entry);
        if (!titleStr || !sourceUrl) {
          errors.push(`Skipping entry with missing title/url`);
          continue;
        }

        // Dedup by source_url
        const { data: existing, error: dupErr } = await supabase
          .from("articles")
          .select("id")
          .eq("source_url", sourceUrl)
          .maybeSingle();
        if (dupErr) throw dupErr;
        if (existing) {
          skipped++;
          continue;
        }

        const html = pickContent(entry);
        const heroImage = firstImageUrl(html);
        const markdown = turndown.turndown(html || "");
        const excerpt = buildExcerpt(markdown);

        const publishedAt =
          (entry.updated as string) ||
          (entry.published as string) ||
          new Date().toISOString();

        // Slug with collision-resistant suffix
        let slug = slugify(titleStr);
        if (!slug) slug = (await shortHash(sourceUrl)).slice(0, 6);
        const { data: slugHit } = await supabase
          .from("articles")
          .select("id")
          .eq("slug", slug)
          .maybeSingle();
        if (slugHit) {
          slug = `${slug}-${await shortHash(sourceUrl)}`;
        }

        const author = pickAuthor(entry);
        const sources = JSON.stringify([
          {
            name: "The Conversation India",
            url: sourceUrl,
            author: author ?? undefined,
            license: "CC BY-ND 4.0",
          },
        ]);

        const { error: insertErr } = await supabase.from("articles").insert({
          title: titleStr,
          slug,
          body: markdown,
          excerpt,
          category: "india",
          hero_image_url: heroImage,
          status: "draft",
          published_at: publishedAt,
          source_url: sourceUrl,
          sources,
        });
        if (insertErr) throw insertErr;
        ingested++;
      } catch (e) {
        errors.push(e instanceof Error ? e.message : String(e));
      }
    }

    return new Response(
      JSON.stringify({ ingested, skipped, errors }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (e) {
    return new Response(
      JSON.stringify({
        error: e instanceof Error ? e.message : String(e),
        ingested,
        skipped,
        errors,
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  }
});
