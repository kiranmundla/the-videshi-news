// One-time: rehost all external article images into Supabase Storage.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

async function uploadToStorage(
  supabase: ReturnType<typeof createClient>,
  sourceUrl: string,
  articleId: string,
): Promise<string | null> {
  const r = await fetch(sourceUrl, {
    headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" },
  });
  if (!r.ok) {
    console.error(`download failed ${r.status} for ${sourceUrl}`);
    return null;
  }
  const buf = await r.arrayBuffer();
  const contentType = r.headers.get("content-type") || "image/jpeg";
  const ext = contentType.includes("png") ? "png" : contentType.includes("webp") ? "webp" : "jpg";
  const filename = `${articleId}-${Date.now()}.${ext}`;
  const { error } = await supabase.storage
    .from("article-images")
    .upload(filename, buf, { contentType, cacheControl: "31536000", upsert: false });
  if (error) {
    console.error("storage upload error", error);
    return null;
  }
  const { data: { publicUrl } } = supabase.storage
    .from("article-images")
    .getPublicUrl(filename);
  return publicUrl;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

  const { data: articles, error } = await supabase
    .from("articles")
    .select("id, title, image_url")
    .eq("is_published", true)
    .not("image_url", "is", null);

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const external = (articles ?? []).filter(
    (a) => a.image_url && !a.image_url.includes("supabase"),
  );

  let rehosted = 0;
  let failed = 0;
  const errors: { id: string; title: string; reason: string }[] = [];

  for (const a of external) {
    try {
      console.log(`→ rehosting ${a.title}`);
      const newUrl = await uploadToStorage(supabase, a.image_url!, a.id);
      if (!newUrl) {
        failed++;
        errors.push({ id: a.id, title: a.title, reason: "upload returned null" });
        continue;
      }
      const { error: updErr } = await supabase
        .from("articles")
        .update({ image_url: newUrl })
        .eq("id", a.id);
      if (updErr) {
        failed++;
        errors.push({ id: a.id, title: a.title, reason: updErr.message });
        continue;
      }
      rehosted++;
      console.log(`✓ ${a.title}`);
    } catch (e) {
      failed++;
      const msg = e instanceof Error ? e.message : String(e);
      errors.push({ id: a.id, title: a.title, reason: msg });
      console.error(`✗ ${a.title}: ${msg}`);
    }
  }

  return new Response(
    JSON.stringify({ total: external.length, rehosted, failed, errors }),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
