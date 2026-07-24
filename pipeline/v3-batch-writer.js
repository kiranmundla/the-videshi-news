export const meta = { name: "v3-batch-writer", description: "Write V3 articles for The Videshi in parallel batches", phases: ["load-candidates", "write-articles", "post-processing"] };

const ENV_SETUP = "set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels 2>/dev/null; set +a";

// Phase 1: Load candidate list from file
phase("load-candidates");

const loadResult = await agent(
  "Read the file at ~/workspace/the-videshi-news/pipeline/v3-batch-candidates.json using the read tool. Return the full JSON array as the 'candidates' field. Each element has: topic_id, title, category, coverage, source_urls (array), and optionally merge_topic_ids (array).",
  {
    key: "load-candidates",
    label: "Loading candidate list",
    timeoutMs: 60000,
    schema: {
      type: "object",
      properties: {
        candidates: {
          type: "array",
          items: {
            type: "object",
            properties: {
              topic_id: { type: "string" },
              title: { type: "string" },
              category: { type: "string" },
              coverage: { type: "string" },
              source_urls: { type: "array", items: { type: "string" } },
              merge_topic_ids: { type: "array", items: { type: "string" } }
            },
            required: ["topic_id", "title", "category"]
          }
        }
      },
      required: ["candidates"]
    }
  }
);

const candidates = loadResult.candidates;
log("Loaded " + candidates.length + " candidates");

// Phase 2: Write articles in parallel
phase("write-articles");

const buildPrompt = (c, idx) => {
  const mergeNote = c.merge_topic_ids
    ? "\n- MERGED TOPICS: This article combines two related topics. After inserting, update BOTH topic IDs: " + JSON.stringify(c.merge_topic_ids)
    : "";
  const updateNote = c.coverage === "update"
    ? "\n- This is an UPDATE. Frame as a new development. Reference that prior coverage exists."
    : "";

  return "You are a senior journalist writing ONE article for The Videshi, a professional Indian diaspora news publication.\n\n" +
    "FIRST: Read ~/workspace/the-videshi-news/pipeline/V3-WRITER-INSTRUCTIONS.md section '3c' for the writing standard. Follow it EXACTLY.\n\n" +
    "CANDIDATE:\n" +
    "- Topic ID: " + c.topic_id + "\n" +
    "- Title: " + c.title + "\n" +
    "- Category: " + c.category + "\n" +
    "- Coverage: " + c.coverage + "\n" +
    "- Source URLs: " + JSON.stringify(c.source_urls) +
    mergeNote + updateNote + "\n\n" +
    "PROCESS:\n\n" +
    "STEP 1 - RESEARCH:\n" +
    "Open 2-3 source URLs with browser_open. These are Google News RSS redirect URLs - browser_open will follow the redirect. If browser_open fails or returns unhelpful content, use browser_search to find the topic.\n\n" +
    "STEP 2 - WRITE THE ARTICLE:\n" +
    "- HEADLINE: 8-14 words, clear, informative, active voice, NO clickbait\n" +
    "- SUBHEADLINE: 1-2 sentences for article cards\n" +
    "- KEY TAKEAWAYS in this EXACT HTML (NO heading tag inside):\n" +
    '  <div class="key-takeaways"><ul><li>Bullet 1</li><li>Bullet 2</li><li>Bullet 3</li></ul></div>\n' +
    "- BODY: 500-800 words HTML with <h2> subheadings:\n" +
    "  a) News lead - what happened\n" +
    "  b) Context & Background\n" +
    "  c) Impact & Analysis\n" +
    "  d) Diaspora angle (natural, not forced)\n" +
    "  e) Looking Ahead\n" +
    "- PULL QUOTES (1-2 max, only with strong quotes):\n" +
    '  <blockquote class="pull-quote"><p>"Quote."</p><cite>\\u2014 Name, Title</cite></blockquote>\n' +
    "- NO filler: 'In a significant development,' 'It is worth noting'\n" +
    "- Cite sources naturally: 'according to Reuters,' 'Bloomberg reported'\n" +
    "- Use specific numbers, dates, names. Write ONLY from source material.\n\n" +
    "STEP 3 - GENERATE SLUG: From headline, lowercase, hyphens, no special chars, max 80 chars.\n\n" +
    "STEP 4 - INSERT ARTICLE:\n" +
    "Write a Python script to /tmp/insert-" + c.topic_id.substring(0, 8) + ".py that:\n" +
    "1. Constructs the article JSON payload with ALL required fields:\n" +
    "   headline, subheadline, body, slug, category ('" + c.category + "'), vertical ('" + c.category + "'),\n" +
    "   tags (JSON array of 3-5 tags), sources (array of source URLs used),\n" +
    "   image_url (null), image_caption (null), image_attribution (null),\n" +
    "   word_count (int), diaspora_angle (1 sentence string),\n" +
    "   topic_id ('" + c.topic_id + "'), llm_score (5),\n" +
    "   published_at (current ISO timestamp with timezone), article_type ('breaking'), status ('published')\n" +
    "2. POSTs to $SUPABASE_URL/rest/v1/p2_articles using subprocess.run with curl (NOT urllib)\n" +
    "   Headers: apikey, Authorization Bearer, Content-Type application/json, Prefer return=representation\n" +
    "3. Prints the article ID and slug from the response\n\n" +
    "Run it: " + ENV_SETUP + " && python3 -u /tmp/insert-" + c.topic_id.substring(0, 8) + ".py\n\n" +
    "STEP 5 - IMAGE SOURCING:\n" +
    ENV_SETUP + "\n" +
    "cd ~/workspace/the-videshi-news/pipeline && python3 -u image_sourcer.py --slug YOUR_SLUG --apply\n\n" +
    "STEP 6 - UPDATE TOPIC:\n" +
    ENV_SETUP + "\n" +
    'curl -s -X PATCH "$SUPABASE_URL/rest/v1/p2_topics?id=eq.' + c.topic_id + '" ' +
    '-H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" ' +
    '-H "Content-Type: application/json" -d \'{"status":"published","last_article_id":"ARTICLE_ID"}\'\n' +
    (c.merge_topic_ids ? "\nAlso PATCH the merged topic: " + c.merge_topic_ids[1] + " with same data.\n" : "") +
    "\nReturn your result with: headline, slug, category, article_id, status ('published' or 'failed').";
};

const results = await parallel(
  candidates.map((c, i) => {
    return async () => {
      const result = await agent(buildPrompt(c, i), {
        key: "article-" + i + "-" + c.category.replace(/[^a-z]/g, ""),
        label: "Writing: " + c.title.substring(0, 50),
        timeoutMs: 600000,
        schema: {
          type: "object",
          properties: {
            headline: { type: "string" },
            slug: { type: "string" },
            category: { type: "string" },
            article_id: { type: "string" },
            status: { type: "string" }
          },
          required: ["headline", "category", "status"]
        }
      });
      log("Article " + i + " [" + c.category + "]: " + (result ? result.headline : "FAILED") + " - " + (result ? result.status : "null"));
      return result;
    };
  }),
  { concurrency: 4 }
);

const published = results.filter(function(r) { return r && r.status === "published"; });
const failed = results.filter(function(r) { return !r || r.status === "failed"; });

log("Phase 2 complete. Published: " + published.length + ", Failed: " + failed.length);

// Phase 3: Post-processing
phase("post-processing");

const enrichResult = await agent(
  "Run the post-publish enrichment pipeline for The Videshi. Execute these commands in order using exec:\n\n" +
  "1. Source env vars:\n" +
  "set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai; " +
  "source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io 2>/dev/null; " +
  "source ~/workspace/.env.apify 2>/dev/null; source ~/workspace/.env.youtube 2>/dev/null; set +a\n\n" +
  "2. cd ~/workspace/the-videshi-news/pipeline\n\n" +
  "3. Run enrichments:\n" +
  "   timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply 2>&1\n" +
  "   timeout 600 python3 -u enrich-articles.py --hours 3 --apply 2>&1\n" +
  "   timeout 600 python3 -u enrich-data-cards.py --since-hours 3 --limit 10 2>&1\n\n" +
  "4. Image backfill:\n" +
  "   python3 -u image_sourcer.py --backfill --hours 3 --apply 2>&1\n\n" +
  "5. Proofread:\n" +
  "   timeout 120 python3 -u proofread-article.py --hours 3 --apply 2>&1\n\n" +
  "6. Rebuild feeds:\n" +
  "   python3 -u prebuild-feeds.py 2>&1\n\n" +
  "7. Git commit and push:\n" +
  "   cd ~/workspace/the-videshi-news && git add -A && git commit -m 'V3 pipeline articles 2026-07-24' && git push origin main 2>&1\n\n" +
  "Report what each step accomplished (articles enriched, images found, etc.).",
  {
    key: "enrichment",
    label: "Post-publish enrichment and feed rebuild",
    timeoutMs: 900000,
    schema: {
      type: "object",
      properties: {
        summary: { type: "string" },
        enriched_count: { type: "number" },
        images_found: { type: "number" },
        git_pushed: { type: "boolean" }
      },
      required: ["summary"]
    }
  }
);

log("Enrichment: " + (enrichResult ? enrichResult.summary : "unknown"));

const headlines = published.map(function(a) { return "[" + a.category + "] " + a.headline; });

return "V3 Pipeline Complete: " + published.length + " articles published, " + failed.length + " failed.\n\n" +
  "Headlines:\n" + headlines.map(function(h) { return "- " + h; }).join("\n") +
  "\n\nEnrichment: " + (enrichResult ? enrichResult.summary : "completed");
