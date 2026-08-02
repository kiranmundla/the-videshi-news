export const meta = {
  name: "v3-batch-aug1",
  description: "Write V3 articles for The Videshi - Aug 1 batch",
  phases: ["load", "write", "enrich", "publish"]
};

phase("load");

var loadResult = await agent(
  "Read the file /tmp/v3-compact-candidates.json and return its contents. It is a JSON array of article candidate objects.",
  {
    key: "load-candidates",
    label: "Load candidates from file",
    phase: "load",
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
              llm_score: { type: "number" },
              source_urls: { type: "array", items: { type: "string" } },
              signals: { type: "array" }
            }
          }
        },
        count: { type: "number" }
      }
    }
  }
);

var candidates = loadResult.candidates;
log("Loaded " + candidates.length + " candidates");

phase("write");

function buildPrompt(c) {
  var sigs = (c.signals || []).map(function(s) {
    return '  - "' + s.title + '" (' + (s.source || "unknown") + ')';
  }).join("\n");
  var topicShort = c.topic_id.substring(0, 8);

  return 'Write ONE professional news article for The Videshi (Indian diaspora publication) and publish it to the database.\n\n' +
    'ENV SETUP (use in every exec call): set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels 2>/dev/null; set +a\n\n' +
    'CANDIDATE:\n' +
    '- topic_id: ' + c.topic_id + '\n' +
    '- title: ' + c.title + '\n' +
    '- category: ' + c.category + '\n' +
    '- coverage: ' + c.coverage + '\n' +
    '- source_urls: ' + JSON.stringify(c.source_urls) + '\n' +
    '- signals:\n' + sigs + '\n\n' +
    'STEP 1 — RESEARCH\n' +
    'Use browser_search to find 2-3 actual news articles about this topic. Read at least 2 via browser_open to get facts, quotes, numbers, and context. Cross-reference sources.\n\n' +
    'STEP 2 — WRITE THE ARTICLE\n' +
    'Write like a senior Reuters/Bloomberg journalist.\n\n' +
    'HEADLINE: 8-14 words. Clear, informative. No clickbait.\n' +
    'SUBHEADLINE: 1-2 sentence summary for card display.\n' +
    'SLUG: URL-friendly from headline (lowercase, hyphens, max 8 words).\n\n' +
    'HTML BODY (500-800 words):\n' +
    '1. Key takeaways FIRST (REQUIRED, NO heading tag inside):\n' +
    '   <div class="key-takeaways"><ul><li>Bullet 1</li><li>Bullet 2</li><li>Bullet 3</li></ul></div>\n' +
    '2. Opening paragraph — the news lead (what happened, who, why it matters)\n' +
    '3. <h2> section — Context & Background\n' +
    '4. <h2> section — Impact & Analysis\n' +
    '5. Diaspora angle paragraph (only if natural for ' + c.category + ' — never force it)\n' +
    '6. <h2> section — What\'s Next\n\n' +
    'Pull quotes (1-2 max for impactful quotes):\n' +
    '<blockquote class="pull-quote"><p>"quote text"</p><cite>— Name, Title</cite></blockquote>\n\n' +
    'WRITING RULES:\n' +
    '- Write from source material only — no fabrication\n' +
    '- Cite sources naturally: "according to Reuters", "the ministry announced"\n' +
    '- Use specific numbers, dates, names — concrete details\n' +
    '- NO filler: "In a significant development", "It is worth noting"\n' +
    '- NO qualifiers: "importantly", "notably", "interestingly"\n' +
    '- Vary sentence length. Short punchy + longer analytical.\n' +
    '- For markets-finance: straight financial journalism, no forced NRI framing\n' +
    '- For entertainment: depth, not gossip\n\n' +
    'STEP 3 — INSERT INTO DATABASE\n' +
    'Create a Python script to build the JSON (handles HTML escaping properly):\n\n' +
    'import json, subprocess, datetime\n\n' +
    'article = {\n' +
    '    "headline": "YOUR HEADLINE",\n' +
    '    "subheadline": "YOUR SUBHEADLINE",\n' +
    '    "body": YOUR_HTML_BODY_STRING,\n' +
    '    "slug": "your-slug",\n' +
    '    "category": "' + c.category + '",\n' +
    '    "vertical": "' + c.category + '",\n' +
    '    "tags": ["tag1", "tag2", "tag3"],\n' +
    '    "sources": ["source_url_1", "source_url_2"],\n' +
    '    "image_url": None,\n' +
    '    "image_caption": None,\n' +
    '    "image_attribution": None,\n' +
    '    "word_count": WORD_COUNT,\n' +
    '    "diaspora_angle": "One sentence summary",\n' +
    '    "topic_id": "' + c.topic_id + '",\n' +
    '    "llm_score": ' + c.llm_score + ',\n' +
    '    "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),\n' +
    '    "article_type": "breaking",\n' +
    '    "status": "published"\n' +
    '}\n' +
    'with open("/tmp/article_' + topicShort + '.json", "w") as f:\n' +
    '    json.dump(article, f)\n\n' +
    'Then insert via curl:\n' +
    'set -a; source ~/workspace/.env.supabase; set +a\n' +
    'curl -sS "$SUPABASE_URL/rest/v1/p2_articles" -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" -H "Content-Type: application/json" -H "Prefer: return=representation" -d @/tmp/article_' + topicShort + '.json\n\n' +
    'Extract the "id" UUID from the response.\n\n' +
    'STEP 4 — IMAGE SOURCING\n' +
    'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.pexels 2>/dev/null; set +a\n' +
    'cd ~/workspace/the-videshi-news/pipeline && python3 -u image_sourcer.py --slug YOUR_SLUG --apply\n\n' +
    'STEP 5 — POLISH\n' +
    'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a\n' +
    'cd ~/workspace/the-videshi-news/pipeline && python3 -u article-polish.py --article-id ARTICLE_UUID\n\n' +
    'STEP 6 — UPDATE TOPIC STATUS\n' +
    'set -a; source ~/workspace/.env.supabase; set +a\n' +
    'curl -sS "$SUPABASE_URL/rest/v1/p2_topics?id=eq.' + c.topic_id + '" -X PATCH -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" -H "Content-Type: application/json" -d \'{"status":"published","last_article_id":"ARTICLE_UUID"}\'\n\n' +
    'If image or polish fails, continue — the article is published and readable.\n' +
    'Return the article_id (UUID), slug, headline, and category.';
}

var writeResults = await parallel(
  candidates.map(function(c, i) {
    return function() {
      return agent(buildPrompt(c), {
        key: "art-" + i,
        label: c.category + ": " + c.title.substring(0, 45),
        phase: "write",
        timeoutMs: 720000,
        schema: {
          type: "object",
          properties: {
            article_id: { type: "string" },
            slug: { type: "string" },
            headline: { type: "string" },
            category: { type: "string" },
            error: { type: "string" }
          },
          required: ["headline"]
        }
      });
    };
  }),
  { concurrency: 5 }
);

var published = writeResults.filter(function(r) { return r !== null && r.article_id; });
var failed = writeResults.filter(function(r) { return r === null || !r.article_id; });
log("Write phase: " + published.length + " published, " + failed.length + " failed/null");

phase("enrich");

var pubInfo = JSON.stringify(published.map(function(p) {
  return { headline: p.headline, article_id: p.article_id, slug: p.slug, category: p.category };
}));

await agent(
  'Run post-processing for The Videshi. Continue even if individual scripts fail.\n\n' +
  'Published articles:\n' + pubInfo + '\n\n' +
  '1. Social enrichment:\n' +
  'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai 2>/dev/null; source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io; source ~/workspace/.env.apify; source ~/workspace/.env.youtube; set +a\n' +
  'cd ~/workspace/the-videshi-news/pipeline\n' +
  'timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply\n' +
  'timeout 600 python3 -u enrich-articles.py --hours 3 --apply\n\n' +
  '2. Image backfill:\n' +
  'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.pexels 2>/dev/null; set +a\n' +
  'cd ~/workspace/the-videshi-news/pipeline\n' +
  'python3 -u image_sourcer.py --backfill --hours 3 --apply\n\n' +
  '3. Storyline linking:\n' +
  'set -a; source ~/workspace/.env.supabase; set +a\n' +
  'curl -sS "$SUPABASE_URL/rest/v1/storylines?select=id,title,slug,status,article_count&status=in.(active,emerging)" -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"\n' +
  'For each published article, if it matches an active storyline, insert into storyline_articles and update the storyline article_count and last_article_at.\n\n' +
  'Report enrichment summary and storyline links.',
  {
    key: "enrich",
    label: "Enrichment + storylines",
    phase: "enrich",
    timeoutMs: 900000
  }
);

phase("publish");

await agent(
  'Rebuild feeds and deploy:\n' +
  'cd ~/workspace/the-videshi-news\n' +
  'set -a; source ~/workspace/.env.supabase; set +a\n' +
  'python3 -u pipeline/prebuild-feeds.py\n' +
  'git add -A public/data/ && git commit -m "feeds: v3 writer aug-1" && git push origin main\n' +
  'Report success or failure.',
  {
    key: "deploy",
    label: "Rebuild feeds + deploy",
    phase: "publish",
    timeoutMs: 300000
  }
);

return {
  message: "V3 pipeline: " + published.length + "/" + candidates.length + " articles published",
  articles: published.map(function(r) { return { headline: r.headline, category: r.category, slug: r.slug }; }),
  failed_count: failed.length
};
