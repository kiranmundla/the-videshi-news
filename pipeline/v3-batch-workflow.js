export const meta = {
  name: "v3-writer-batch",
  description: "Write V3 articles for The Videshi in parallel batches",
  phases: ["write", "enrich", "publish"]
};

var count = args.count;
log("Processing " + count + " articles in parallel");

phase("write");

var indices = [];
for (var i = 0; i < count; i++) {
  indices.push(i);
}

var results = await parallel(
  indices.map(function(idx) {
    return function() {
      return agent(
        "You are a senior journalist writing for The Videshi, a professional Indian diaspora news publication.\n\n" +
        "1. Read ~/workspace/the-videshi-news/pipeline/V3-WRITER-INSTRUCTIONS.md for the complete article writing process.\n" +
        "2. Read /tmp/v3-keep.json (it has a 'candidates' array). Take the candidate at array index " + idx + ".\n" +
        "3. Follow steps 3a through 3f from the instructions to research, write, and publish that ONE article.\n\n" +
        "CRITICAL REMINDERS:\n" +
        "- For research: use browser_search with keywords from the candidate title. The source_urls in the JSON are Google News redirects — do NOT try to open them. Search and read 2-3 real news articles instead.\n" +
        "- Every article MUST start with key takeaways: <div class=\"key-takeaways\"><ul><li>3-4 bullets</li></ul></div> — NO heading tag inside.\n" +
        "- Write 500-800 words in HTML. Reuters/Bloomberg quality. No filler phrases.\n" +
        "- Use <h2> subheadings for sections. Include 1-2 pull quotes for strong quotes.\n" +
        "- Image caption: exactly two factual sentences. No flowery bridging words.\n" +
        "- For DB insertion: write article JSON via Python json.dump() to a /tmp file (this handles HTML escaping). Then curl POST with -d @file.\n" +
        "- Env setup for EVERY exec call needing DB access: set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels 2>/dev/null; set +a\n" +
        "- After inserting, PATCH the p2_topics row to set status=published and last_article_id.\n\n" +
        "Return: the headline you wrote, the category, and whether the DB insert succeeded or failed (and why if failed).",
        {
          key: "art-" + idx,
          label: "Article " + idx,
          timeoutMs: 900000
        }
      );
    };
  }),
  { concurrency: 6 }
);

var completed = results.filter(function(r) { return r !== null; });
log("Write phase done: " + completed.length + "/" + count + " completed");

phase("enrich");
await agent(
  "Run enrichment scripts on recently published Videshi articles. Continue to the next script even if one fails.\n\n" +
  "Setup (run once at start):\n" +
  "set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai 2>/dev/null; source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io; source ~/workspace/.env.apify; source ~/workspace/.env.youtube; set +a\n" +
  "cd ~/workspace/the-videshi-news/pipeline\n\n" +
  "Run these in order:\n" +
  "1. timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply 2>&1\n" +
  "2. timeout 600 python3 -u enrich-articles.py --hours 3 --apply 2>&1\n" +
  "3. timeout 600 python3 -u enrich-data-cards.py --since-hours 3 --limit 10 2>&1\n" +
  "4. timeout 120 python3 -u proofread-article.py --hours 3 --apply 2>&1\n\n" +
  "Report a summary of what each script did.",
  { key: "enrich", label: "Enrich articles", timeoutMs: 1200000 }
);

phase("publish");
await agent(
  "Rebuild feeds and push to git for The Videshi:\n" +
  "1. cd ~/workspace/the-videshi-news/pipeline && python3 -u prebuild-feeds.py 2>&1\n" +
  "2. cd ~/workspace/the-videshi-news && git add -A && git commit -m 'V3 pipeline articles 2026-07-22' && git push origin main 2>&1\n" +
  "Report success or failure.",
  { key: "publish", label: "Rebuild feeds and push", timeoutMs: 300000 }
);

return "V3 pipeline complete: " + completed.length + "/" + count + " articles processed.\n\nResults:\n" + completed.map(function(r) { return typeof r === "string" ? r.substring(0, 150) : JSON.stringify(r).substring(0, 150); }).join("\n");
