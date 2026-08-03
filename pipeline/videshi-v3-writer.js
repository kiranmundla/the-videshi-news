export const meta = {
  name: "videshi-v3-writer",
  description: "Write and publish V3 pipeline articles for The Videshi",
  phases: [
    { name: "write", title: "Writing articles", detail: "Reading sources and writing articles in parallel" },
    { name: "enrich", title: "Enrichment", detail: "Social embeds and image backfill" },
    { name: "storylines", title: "Storyline linking", detail: "Link articles to active storylines" },
    { name: "deploy", title: "Deploy", detail: "Rebuild feeds and push" }
  ]
};

const SKIP_INDICES = args.skipIndices || [];
const TOTAL_CANDIDATES = args.totalCandidates || 29;

phase("write");

const indices = [];
for (let i = 0; i < TOTAL_CANDIDATES; i++) {
  if (!SKIP_INDICES.includes(i)) indices.push(i);
}

log(`Processing ${indices.length} candidates (skipped ${SKIP_INDICES.length} pre-identified duplicates: indices ${SKIP_INDICES.join(',')})`);

const results = await parallel(
  indices.map(idx => () => agent(
    `You are a senior journalist writing one article for The Videshi, a professional news site for the Indian diaspora. Your task: read sources, write the article, insert it, source an image, and polish it.

CANDIDATE INDEX: ${idx} (0-indexed in /tmp/v3-candidates.json)

SETUP (run as first exec command):
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels; set +a

STEP 1 — Read candidate data:
Read /tmp/v3-candidates.json with exec, extract the candidate at array index ${idx}. Note its topic_id, title, category, source_urls, all_signals, llm_score, coverage.

STEP 2 — Dedup check:
Query recent published articles (last 3 days):
curl -sS "$SUPABASE_URL/rest/v1/p2_articles?select=headline&created_at=gte.$(date -u -d '3 days ago' +%%Y-%%m-%%dT%%H:%%M:%%SZ)&status=eq.published&limit=200" -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
If a published article covers the SAME story, return skipped=true with skip_reason. Minor entity overlap is OK — only skip true duplicates.

STEP 3 — Read source material:
Use browser_open on 2-4 of the source_urls (they may be Google News RSS URLs that redirect). Also check all_signals for additional URLs. Cross-reference multiple sources. If source_urls is empty, use browser_search with the candidate title.

STEP 4 — Write the article:
- HEADLINE: 8-14 words, clear, informative, no clickbait. For "update" coverage, lead with what's NEW.
- SUBHEADLINE: 1-2 sentence summary for display on cards (NOT the key takeaways)
- KEY TAKEAWAYS (REQUIRED): 3-4 bullet points in <div class="key-takeaways"><ul><li>...</li></ul></div> — NO heading tag inside, just the div and bullets
- BODY (500-800 words, HTML):
  * Opening paragraph: news lead, what happened
  * Context & Background with <h2> subheading
  * Impact & Analysis with <h2> subheading  
  * Diaspora Angle (when natural, NOT forced)
  * What's Next / Looking Ahead
- Use 1-2 pull quotes when strong quotes exist: <blockquote class="pull-quote"><p>"quote"</p><cite>— Name, Title</cite></blockquote>
- Write from source material ONLY. Include source citations naturally ("according to Reuters")
- NO filler: "In a significant development," "It is worth noting," "notably," "interestingly"
- Vary sentence length. Use specific numbers, dates, names.
- For markets-finance: straight financial journalism, US/global-first tone
- For entertainment: equal depth for Bollywood and Hollywood

STEP 5 — Generate slug: lowercase, hyphens, 6-10 words from headline

STEP 6 — Insert into DB:
curl -sS "$SUPABASE_URL/rest/v1/p2_articles" -X POST \\
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \\
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \\
  -H "Content-Type: application/json" \\
  -H "Prefer: return=representation" \\
  -d '<json payload>'

JSON fields: headline, subheadline, body (HTML string), slug, category, vertical (same as category), tags (string array), sources (array of source URLs used), image_url (null), image_caption (null), image_attribution (null), word_count (integer), diaspora_angle (1 sentence string), topic_id, llm_score (integer from candidate), published_at (current ISO timestamp), article_type ("breaking"), status ("published")

IMPORTANT: The body HTML must be a properly escaped JSON string. Use exec with a Python script to do the curl if the body is complex.

STEP 7 — Extract the article id (UUID) from the insert response.

STEP 8 — Source hero image:
cd ~/workspace/the-videshi-news/pipeline && python3 -u image_sourcer.py --slug <your-slug> --apply

STEP 9 — Polish article:
cd ~/workspace/the-videshi-news/pipeline && python3 -u article-polish.py --article-id <uuid>

STEP 10 — Update topic status:
curl -sS "$SUPABASE_URL/rest/v1/p2_topics?id=eq.<topic_id>" -X PATCH \\
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \\
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"status":"published","last_article_id":"<article_uuid>"}'

Return headline, slug, category, article_id. If skipped, set skipped=true with skip_reason.`,
    {
      key: `article-${idx}`,
      label: `Article ${idx + 1}`,
      timeoutMs: 600000,
      schema: {
        type: "object",
        properties: {
          headline: { type: "string" },
          slug: { type: "string" },
          category: { type: "string" },
          article_id: { type: "string" },
          skipped: { type: "boolean" },
          skip_reason: { type: "string" }
        }
      }
    }
  )),
  { concurrency: 4 }
);

const published = [];
const skippedByAgent = [];
const failed = [];

for (let i = 0; i < results.length; i++) {
  const r = results[i];
  if (!r) {
    failed.push({ index: indices[i], reason: "agent returned null" });
  } else if (r.skipped) {
    skippedByAgent.push(r);
  } else if (r.article_id) {
    published.push(r);
  } else {
    failed.push({ index: indices[i], headline: r.headline, reason: "no article_id" });
  }
}

log(`Write phase: ${published.length} published, ${skippedByAgent.length} skipped by agent, ${failed.length} failed`);

if (published.length === 0) {
  return {
    message: "No articles published — all candidates were skipped or failed.",
    skipped_dupes: SKIP_INDICES.map(i => `Candidate ${i + 1}`),
    skipped_by_agents: skippedByAgent,
    failed: failed
  };
}

// Phase 2: Enrichment
phase("enrich");

const enrichResult = await agent(
  `Run enrichment scripts for recently published Videshi articles.

ENV setup:
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai; source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io; source ~/workspace/.env.apify; source ~/workspace/.env.youtube; set +a

cd ~/workspace/the-videshi-news/pipeline

Run these three commands in order:
1. timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply
2. timeout 600 python3 -u enrich-articles.py --hours 3 --apply
3. python3 -u image_sourcer.py --backfill --hours 3 --apply

Report a brief summary of what each script did (articles enriched, embeds added, images found).`,
  {
    key: "enrichment",
    label: "Enrichment pipeline",
    timeoutMs: 900000
  }
);

log(`Enrichment complete`);

// Phase 3: Storyline linking
phase("storylines");

const articleListStr = published.map(p => `- ${p.article_id}: "${p.headline}" [${p.category}]`).join('\n');

const storylineResult = await agent(
  `Link newly published articles to active developing stories in the storylines table.

ENV setup:
set -a; source ~/workspace/.env.supabase; set +a

1. Fetch active storylines:
curl -sS "$SUPABASE_URL/rest/v1/storylines?select=id,title,slug,status,article_count&status=in.(active,emerging)" \\
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \\
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"

2. Review each article below and determine if it belongs to an active storyline based on topic match:

${articleListStr}

3. For each match:
- Check if already linked: GET /rest/v1/storyline_articles?storyline_id=eq.<sid>&article_id=eq.<aid>
- If not linked, insert: POST /rest/v1/storyline_articles with {"storyline_id":"...","article_id":"..."}
- Update storyline: PATCH /rest/v1/storylines?id=eq.<sid> with updated article_count (increment by 1), last_article_at (now ISO), status "active"

Report which articles were linked to which storylines, or if none matched.`,
  {
    key: "storylines",
    label: "Storyline linking",
    timeoutMs: 300000
  }
);

log(`Storyline linking complete`);

// Phase 4: Deploy
phase("deploy");

await agent(
  `Rebuild The Videshi feeds and deploy to production.

set -a; source ~/workspace/.env.supabase; set +a

cd ~/workspace/the-videshi-news/pipeline
python3 -u prebuild-feeds.py

cd ~/workspace/the-videshi-news
git add -A public/data/
git commit -m "V3 pipeline articles $(date +%%Y-%%m-%%d)"
git push origin main

Report the git push result.`,
  {
    key: "deploy",
    label: "Rebuild and deploy",
    timeoutMs: 300000
  }
);

return {
  message: `V3 pipeline complete. Published ${published.length} articles.`,
  published: published.map(p => ({ headline: p.headline, category: p.category, slug: p.slug })),
  skipped_pre: SKIP_INDICES.map(i => `Candidate ${i + 1}`),
  skipped_by_agents: skippedByAgent.map(s => ({ headline: s.headline || "unknown", reason: s.skip_reason || "unknown" })),
  failed: failed
};
