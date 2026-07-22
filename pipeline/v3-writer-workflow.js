export const meta = { 
  name: "v3-article-batch", 
  description: "Write V3 pipeline articles in parallel for The Videshi", 
  phases: ["write"] 
};

const candidates = args.candidates;
log("Starting batch write for " + candidates.length + " articles");

phase("write");

function buildPrompt(c) {
  var signalSummary = c.all_signals.map(function(s) { return s.title + " (" + s.source + ")"; }).join("\n  ");
  var sourceUrls = c.source_urls.slice(0, 4).join("\n  ");

  return "You are a senior journalist writing ONE article for The Videshi, a professional news publication for the Indian diaspora. Write like Reuters/Bloomberg quality. Follow every instruction below precisely.\n\n" +
    "CANDIDATE:\n" +
    "- Title: " + c.title + "\n" +
    "- Topic ID: " + c.topic_id + "\n" +
    "- Category: " + c.category + "\n" +
    "- Coverage: " + c.coverage + "\n" +
    "- Source Signals:\n  " + signalSummary + "\n" +
    "- Source URLs (Google News redirects):\n  " + sourceUrls + "\n\n" +
    "STEP 1: RESEARCH\n" +
    "Use browser_search to find 2-3 actual news articles about this topic. Search for the core subject. Also try browser_open on 1-2 source URLs above (Google News redirects that resolve to articles). Cross-reference multiple sources. Extract key facts, quotes, numbers, and dates.\n\n" +
    "STEP 2: WRITE ARTICLE\n" +
    "Generate ALL of the following:\n\n" +
    "HEADLINE: 8-14 words, clear, informative, no clickbait. For updates, lead with what's NEW.\n\n" +
    "SUBHEADLINE: 1-2 sentence summary for display below headline on cards. NOT the key takeaways.\n\n" +
    "KEY TAKEAWAYS (in the body HTML, at the very top before anything else):\n" +
    "Format: <div class=\"key-takeaways\"><ul><li>Point 1</li><li>Point 2</li><li>Point 3</li></ul></div>\n" +
    "3-4 bullet points summarizing essential facts. NO heading tag inside. Just the div with ul/li.\n\n" +
    "BODY: 500-800 words, HTML format with <h2> subheadings:\n" +
    "1. Opening paragraph: the news lead. What happened, who involved, why it matters. No fluff.\n" +
    "2. Context & Background: what led to this, the history a smart reader needs.\n" +
    "3. Impact & Analysis: what this means going forward, who benefits, who's affected.\n" +
    "4. Diaspora Angle (ONLY when natural, never forced): how it affects Indians abroad.\n" +
    "5. What's Next: what to watch for, upcoming decisions, timeline.\n\n" +
    "WRITING RULES:\n" +
    "- Write from source material ONLY. No fabrication.\n" +
    "- Include source citations naturally: 'according to Reuters,' 'the ministry announced'\n" +
    "- Use 1-2 pull quotes when strong quotes exist: <blockquote class=\"pull-quote\"><p>\"quote\"</p><cite>\\u2014 Name, Title</cite></blockquote>\n" +
    "- NO generic filler: 'In a significant development,' 'It is worth noting,' 'interestingly'\n" +
    "- Vary sentence length. Short punchy sentences mixed with longer analytical ones.\n" +
    "- Use specific numbers, dates, names. Concrete details.\n" +
    "- NEVER repeat the same pull quote.\n\n" +
    "STEP 3: HERO IMAGE\n" +
    "Find a hero image. Try in this order:\n" +
    "1. Check og:image meta tags from the source article pages you read in Step 1. Look for lines containing 'og:image' in browser_open output.\n" +
    "2. For person-focused articles, try Wikipedia REST API via exec:\n" +
    "   curl -sL -H 'User-Agent: TheVideshi/1.0 (thevideshi.com)' 'https://en.wikipedia.org/api/rest_v1/page/summary/ENCODED_NAME'\n" +
    "   Use originalimage.source or thumbnail.source from the JSON response.\n" +
    "3. For topic images, try Pexels via exec:\n" +
    "   set -a; source ~/workspace/.env.pexels; set +a\n" +
    "   curl -s 'https://api.pexels.com/v1/search?query=TOPIC&per_page=3' -H \"Authorization: $PEXELS_API_KEY\"\n" +
    "   Use src.original from the first result.\n" +
    "Use the image URL directly (do NOT download or upload).\n" +
    "Image caption: Two factual sentences. First: what the image shows. Second: the news context. NO flowery language, no 'symbolizing,' 'reflecting,' etc.\n" +
    "Image attribution: source name (e.g., 'Reuters via Washington Post', 'Wikipedia', 'Pexels/photographer')\n\n" +
    "STEP 4: INSERT INTO DATABASE\n" +
    "Run this command to insert the article:\n\n" +
    "set -a; source ~/workspace/.env.supabase; set +a\n\n" +
    "Create a JSON payload with ALL these fields:\n" +
    "- headline (string)\n" +
    "- subheadline (string, 1-2 sentences)\n" +
    "- body (string, the full HTML including key-takeaways div at top)\n" +
    "- slug (string, URL-friendly from headline, lowercase-hyphens-only, no special chars, max 80 chars)\n" +
    "- category (string, exactly: " + c.category + ")\n" +
    "- vertical (string, same as category: " + c.category + ")\n" +
    "- tags (JSON array of 3-5 relevant tags)\n" +
    "- sources (JSON array of source URLs you used)\n" +
    "- image_url (string)\n" +
    "- image_caption (string)\n" +
    "- image_attribution (string)\n" +
    "- word_count (integer)\n" +
    "- diaspora_angle (string, 1 sentence)\n" +
    "- topic_id (string, exactly: " + c.topic_id + ")\n" +
    "- published_at (string, use current ISO timestamp)\n" +
    "- article_type (string, 'breaking')\n" +
    "- status (string, 'published')\n\n" +
    "Write the JSON payload to a temp file, then use curl:\n" +
    "cat /tmp/article_SLUG.json | curl -s -X POST \"$SUPABASE_URL/rest/v1/p2_articles\" \\\n" +
    "  -H \"apikey: $SUPABASE_SERVICE_ROLE_KEY\" \\\n" +
    "  -H \"Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY\" \\\n" +
    "  -H \"Content-Type: application/json\" \\\n" +
    "  -H \"Prefer: return=representation\" \\\n" +
    "  -d @-\n\n" +
    "The response will include an 'id' field - this is the article_id.\n\n" +
    "STEP 5: UPDATE TOPIC STATUS\n" +
    "After successful insert, update the topic:\n" +
    "curl -s -X PATCH \"$SUPABASE_URL/rest/v1/p2_topics?id=eq." + c.topic_id + "\" \\\n" +
    "  -H \"apikey: $SUPABASE_SERVICE_ROLE_KEY\" \\\n" +
    "  -H \"Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY\" \\\n" +
    "  -H \"Content-Type: application/json\" \\\n" +
    "  -d '{\"status\": \"published\", \"last_article_id\": \"ARTICLE_ID_HERE\"}'\n\n" +
    "Return result JSON with: headline, slug, category ('" + c.category + "'), and article_id from the insert response.";
}

var articleResults = await parallel(
  candidates.map(function(c, i) {
    return async function() {
      return await agent(buildPrompt(c), {
        key: "article-" + i + "-" + c.category,
        label: "Writing: " + c.title.slice(0, 60),
        timeoutMs: 600000,
        schema: {
          type: "object",
          properties: {
            headline: { type: "string" },
            slug: { type: "string" },
            category: { type: "string" },
            article_id: { type: "string" },
            error: { type: "string" }
          },
          required: ["headline"]
        }
      });
    };
  }),
  { concurrency: 4 }
);

var successful = articleResults.filter(function(r) { return r && r.article_id; });
var failed = articleResults.filter(function(r) { return r && !r.article_id; });
var dropped = articleResults.filter(function(r) { return r === null; });

log("Articles written: " + successful.length + "/" + candidates.length);
if (failed.length > 0) {
  log("Failed: " + failed.map(function(f) { return f.headline || f.error || "unknown"; }).join(", "));
}
if (dropped.length > 0) {
  log("Dropped (null): " + dropped.length);
}

return {
  message: "Wrote " + successful.length + " articles for The Videshi",
  articles: successful,
  failed: failed.length > 0 ? failed : undefined
};
