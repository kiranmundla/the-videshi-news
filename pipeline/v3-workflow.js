export const meta = {
  name: "v3-writer",
  description: "Write V3 articles for The Videshi in parallel",
  phases: ["write", "enrich", "publish"]
};

const candidates = [{"topic_id": "57b2ee57-1f4e-4894-aa48-cc2eef681d1b", "title": "UK inflation rate falls to 2.6% - BBC", "category": "news", "coverage": "new", "signals": [{"title": "UK inflation slows to 2.6% in June", "source": "Reuters"}, {"title": "Inflation down to 2.6% after Gulf ceasefire cooled oil price", "source": "The Times"}, {"title": "UK inflation rate falls to 2.6% - BBC", "source": "BBC"}, {"title": "UK CPI for June expected to offer respite from recent inflation spike", "source": "FXStreet"}, {"title": "BOE Preview: Hawkish Noises", "source": "Continuum Economics"}]}, {"topic_id": "0b8b3df0-7ea0-4e28-be05-8fac1da11d24", "title": "Sharad Pawar, Supriya Sule Meet PM Modi Amid Buzz Over NCP Support To NDA - NDTV", "category": "news", "coverage": "new", "signals": [{"title": "Sharad Pawar, Supriya Sule meet PM Modi in Parliament amid intensifying Delhi protests", "source": "Moneycontrol.com"}, {"title": "Sharad Pawar, Supriya Sule Meet PM Modi Amid Buzz Over NCP Support To NDA - NDTV", "source": "NDTV"}, {"title": "New Delhi: Sharad Pawar Meets PM Modi #Gallery", "source": "Social News XYZ"}, {"title": "Monsoon session: Sharad Pawar, Supriya Sule meet PM Modi in Parliament", "source": "ANI News"}, {"title": "Sharad Pawar, Supriya Sule Meet PM Modi Amid Buzz Over NCP's Merger With NDA", "source": "News18"}]}, {"topic_id": "0367dc4f-ed92-41ea-ac68-26e2e007f70e", "title": "Australia cricket star David Warner pleads guilty to drink driving - BBC", "category": "sports", "coverage": "new", "signals": [{"title": "Warner pleads guilty to drink driving", "source": "ESPN"}, {"title": "Former Australia opener David Warner pleads guilty to drink-driving, faces jail time", "source": "Rediff"}, {"title": "Former Australia opener David Warner admits to drunk-driving charge - Cricbuzz", "source": "Cricbuzz"}, {"title": "Former Australian opener Warner pleads guilty to drink-driving", "source": "Sportstar"}, {"title": "David Warner Pleads Guilty, Captaincy Future Uncertain", "source": "Cricketkeeda Sports"}]}, {"topic_id": "ef4929dc-cf91-413c-a3f7-ff9eeececba5", "title": "Man United latest: Alex Scott rejects contract as intentions made clear over \u00a336.5million star - Manchester Evening News", "category": "sports", "coverage": "new", "signals": [{"title": "Alex Scott: Bournemouth midfielder rejects new contract amid strong interest from Arsenal, Chelsea and Manchester United", "source": "Sky Sports"}, {"title": "Man United latest: Alex Scott rejects contract as intentions made clear over \u00a336.5million star - Manchester Evening News", "source": "Manchester Evening News"}, {"title": "Bournemouth reject \u00a364m bid from Chelsea for Scott", "source": "BBC"}, {"title": "With Arteta's backing... Liverpool competing strongly to snatch Chelsea, Arsenal and United's target", "source": "Goal.com"}, {"title": "Chelsea launch \u00a364m bid for another Arsenal target after confirming Morgan Rogers deal", "source": "Metro.co.uk"}]}, {"topic_id": "2076b0ed-97c2-4165-bd5d-4a8af47695c5", "title": "New Zealand just had its first bird flu case. Now its taking a rare step to protect native birds - CNN", "category": "news", "coverage": "new", "signals": [{"title": "NZ\u2019s free-range poultry in \u2018Flockdown\u2019 as hundreds of thousands of hens move indoors", "source": "Stuff"}, {"title": "Poultry Industry Steps Up Defences Following First H5 Bird Flu Detection", "source": "hospitalitybusiness.co.nz"}, {"title": "Poultry farmers \u2018laser-focused\u2019 on biosecurity, public vigilance keeps MPI busy", "source": "thepost.co.nz"}, {"title": "Newly arrived H5N1 bird flu likely to take hold in New Zealand, MPI says", "source": "RNZ"}, {"title": "New Zealand just had its first bird flu case. Now its taking a rare step to protect native birds - CNN", "source": "CNN"}]}, {"topic_id": "70745708-c10d-4426-872c-430836b9389d", "title": "Little Fire: Firefighter injured, evacuations ordered as wildfire explodes to 950 acres near Pleasanton in Alameda County - ABC7 Bay Area", "category": "news", "coverage": "new", "signals": [{"title": "\u2018Little Fire\u2019 explodes to 700 acres, forces evacuation orders in East Bay", "source": "KRON4"}, {"title": "Fast-growing wildfire south of Pleasanton prompts evacuation order in Ruby Hill", "source": "Pleasanton Weekly"}, {"title": "Little Fire: Firefighter injured, evacuations ordered as wildfire explodes to 950 acres near Pleasanton in Alameda County - ABC7 Bay Area", "source": "ABC7 Bay Area"}, {"title": "Bay Area Wildfire Prompts Evacuation Orders for Thousands of Residents", "source": "The New York Times"}, {"title": "Little Fire burning south of Pleasanton in Sunol spreads; evacuations expanded", "source": "CBS News"}]}, {"topic_id": "f714a396-f269-4bc5-bca7-bd51d529309f", "title": "Trading Plan: Will Nifty 50 defend 24,100 and Bank Nifty hold 57,600 amid likely minor pressure? - Moneycontrol.com", "category": "markets-finance", "coverage": "new", "signals": [{"title": "Nifty 50, Sensex prediction today: Check how Indian stock market is expected to trade on 22 July", "source": "livemint.com"}, {"title": "Day Trading Guide for July 22, 2026: Intraday supports, resistances for Nifty50 stocks", "source": "BusinessLine"}, {"title": "Stock Market Today: All You Need To Know Before Going Into Trade On July 22", "source": "NDTV Profit"}, {"title": "Trade Setup for July 22: Top 15 things to know before the opening bell", "source": "Moneycontrol.com"}, {"title": "Trading Plan: Will Nifty 50 defend 24,100 and Bank Nifty hold 57,600 amid likely minor pressure? - Moneycontrol.com", "source": "Moneycontrol.com"}]}, {"topic_id": "48d88b1f-6abe-4085-8ff4-69636bcbb74e", "title": "Iran Update Special Report, July 21, 2026 - Institute for the Study of War", "category": "news", "coverage": "new", "signals": [{"title": "Iran Update Evening Special Report, July 20, 2026", "source": "Critical Threats"}, {"title": "IRAN WAR WEEK 21, day #4: Same Hegseth, different day", "source": "Daily Kos"}, {"title": "Iran Shipping Update \u2013 July 20, 2026", "source": "United Against Nuclear Iran | UANI"}, {"title": "Iran Update Evening Special Report, July 19, 2026", "source": "Critical Threats"}, {"title": "Iran Update Special Report, July 21, 2026 - Institute for the Study of War", "source": "Institute for the Study of War"}]}, {"topic_id": "368cdd7c-949b-4b35-b6d3-ef1ed0c6fea1", "title": "'Play music loud to remember Ozzy' says Sharon on first anniversary of his death - BBC", "category": "entertainment", "coverage": "new", "signals": [{"title": "'Play music loud to remember Ozzy' says Sharon on first anniversary of his death - BBC", "source": "BBC"}, {"title": "Kelly Osbourne Details Her \u2018Endless Ache\u2019 of Grief After Dad Ozzy Osbourne\u2019s Death", "source": "Yahoo"}, {"title": "What Jack Osbourne Wants From Fans on Ozzy Day This Week", "source": "Loudwire"}, {"title": "Kelly Osbourne \u2018aches every single day\u2019 as she mourns father Ozzy one year after death", "source": "pagesix.com"}, {"title": "Big Rig ROCK Report 7.20", "source": "98.7 The Gator - The Palm Beaches Rock Station"}]}, {"topic_id": "5f09e781-1519-455d-9076-1888184a7337", "title": "Christopher Nolan Explains Why He Bans Ugg Boots From His Movie Sets - Just Jared", "category": "entertainment", "coverage": "new", "signals": [{"title": "Christopher Nolan Doesn\u2019t Let His Cast Wear \u2018Comfy Slippers\u2019 on Set \u2014 Here\u2019s Why", "source": "People.com"}, {"title": "Christopher Nolan Reveals Why He Bans Uggs on His Movie Sets", "source": "Yahoo"}, {"title": "\u2018The Odyssey\u2019 Stars Matt Damon and Anne Hathaway Reveal Christopher Nolan\u2019s \u2018Commandments\u2019 on Set", "source": "IMDb"}, {"title": "Christopher Nolan bans Uggs on set because they can \u2018weirdly take you out of reality\u2019", "source": "Entertainment Weekly"}, {"title": "Christopher Nolan Explains Why He Bans Ugg Boots From His Movie Sets - Just Jared", "source": "Just Jared"}]}, {"topic_id": "6aff99c7-057e-4807-979c-022019b3f79b", "title": "Russia, Latin American suppliers to rescue: India\u2019s Middle East oil imports dip in April-June on Hormuz d - The Times of India", "category": "markets-finance", "coverage": "new", "signals": [{"title": "Russia, Latin American suppliers to rescue: India\u2019s Middle East oil imports dip in April-June on Hormuz d - The Times of India", "source": "The Times of India"}, {"title": "Crude Oil Flows Show India Is Still Leaning Heavily on Russia", "source": "Investing.com"}, {"title": "Indian refiners turn to Russia, LatAm oil in June quarter, data shows", "source": "Reuters"}, {"title": "India Bought $5.14 Billion Russian Oil In June Despite Pressure. Here's Why", "source": "NDTV"}, {"title": "Indian refiners come to the rescue of Russia\u2019s oil exporters", "source": "The Economic Times"}]}, {"topic_id": "fdbae24a-6c77-45b1-929c-95fbb4547dbd", "title": "The FCC is planning to retroactively ban disguised DJI gadgets - The Verge", "category": "technology", "coverage": "new", "signals": [{"title": "FCC Catches a US Drone Vendor Lying About Possible DJI-Created Product", "source": "PCMag UK"}, {"title": "US tentatively decides to ban imports of some military-grade drones", "source": "Reuters"}, {"title": "The FCC is planning to retroactively ban disguised DJI gadgets - The Verge", "source": "The Verge"}, {"title": "FCC Targets Eight Drone Companies With Proposed Fines Over Unanswered National Security Inquiries", "source": "Dronelife"}, {"title": "US targets China in move to ban military-grade drone imports", "source": "Al Jazeera"}]}, {"topic_id": "ba5df193-0aec-4585-baff-c940de2f8b62", "title": "Real Madrid superstar congratulates Cucurella after Spain\u2019s World Cup triumph - Madrid Universal", "category": "sports", "coverage": "new", "signals": [{"title": "Real Madrid captain welcomes and congratulates World Cup winner Marc Cucurella", "source": "Yahoo Sports"}, {"title": "Real Madrid superstar congratulates Cucurella after Spain\u2019s World Cup triumph - Madrid Universal", "source": "Madrid Universal"}, {"title": "Real Madrid better hope what Marc Cucurella showed is true", "source": "The Real Champs"}, {"title": "Marc Cucurella\u2019s curls become cultural icon of World Cup 2026", "source": "MSN"}, {"title": "Two world titles in one year: Cucurella completes rare football double", "source": "BeSoccer Livescore"}]}, {"topic_id": "4beea98a-de57-41ca-a801-b1f0de4564d7", "title": "Tech Mahindra Q1 net profit rises 28.5% YoY to \u20b914.65 billion - scanx.trade", "category": "technology", "coverage": "new", "signals": [{"title": "Tech Mahindra Q1 net profit rises 28.5% YoY to \u20b914.65 billion - scanx.trade", "source": "scanx.trade"}]}, {"topic_id": "4145818e-ae6e-41cd-b420-d11950687381", "title": "Trump threatens strike on Iran's Pickaxe Mountain near Natanz", "category": "nri-world", "coverage": "update", "signals": [{"title": "Trump threatens strike on Iran's Pickaxe Mountain near Natanz", "source": null}]}, {"topic_id": "4580e297-e2dc-49ee-a4a0-eed39c55dadd", "title": "JD Vance sounds alarm on H-1B \u2018fraud\u2019: Calls for stronger American identity as Indians make up 70% of work ... - Bhaskar English", "category": "immigration", "coverage": "new", "signals": [{"title": "Australia cricket great David Warner pleads guilty to drunk-driving", "source": null}]}, {"topic_id": "a8b8f301-79c6-4598-8b15-7d89bc16b7de", "title": "Court strikes down $100,000 work visa fee in blow to Trump immigration policy - The New Voice of Ukraine", "category": "immigration", "coverage": "new", "signals": [{"title": "Indian diaspora protests in UK over police crackdown in Delhi - Kashmir Media Service", "source": "Kashmir Media Service"}, {"title": "Indian diaspora rallies across five countries in support of CJP over Neet row - Firstpost", "source": "Firstpost"}, {"title": "Barclays PB confirms Singapore non-resident Indian head - Citywire", "source": "Citywire"}]}, {"topic_id": "649e35cd-601a-4907-a0de-773ff46b00c7", "title": "\u2018Look for men in turbans\u2019: Food, first aid, refuge at Gurdwara, Sikh community help students protest at Jantar Mantar", "category": "lifestyle-health", "coverage": "new", "signals": [{"title": "\u2018Look for men in turbans\u2019: Food, first aid, refuge at Gurdwara, Sikh community help students protest at Jantar Mantar", "source": null}]}, {"topic_id": "5b0ed48b-6da6-4656-9713-837332cb291f", "title": "More young women in their 20s are getting type 2 diabetes - BBC", "category": "lifestyle-health", "coverage": "new", "signals": [{"title": "Surge in Type 2 diabetes cases among women under 40 sparks health time bomb warning", "source": "Mirror"}, {"title": "Rise in obesity triggering diabetes surge in younger women", "source": "The Times"}, {"title": "Dartmouth Health physician urges screening as Type 2 diabetes increases among younger adults", "source": "The Cabinet Press"}, {"title": "Obese young women driving rise in diabetes", "source": "The Telegraph"}, {"title": "More young women in their 20s are getting type 2 diabetes - BBC", "source": "BBC"}]}, {"topic_id": "e1d36b71-756d-4911-9484-01a2bec66cfa", "title": "\u2018You taught me how to be a mommy\u2019: Divyanka Tripathi\u2019s emotional note to Yeh Hai Mohabbatein co-star Ruha - The Times of India", "category": "entertainment", "coverage": "new", "signals": [{"title": "'You Taught Me How To Be A Mom': Divyanka Tripathi Reacts As On-Screen Daughter Ruhaanika Meets Her Twin Boys", "source": "News18"}, {"title": "\u2018You taught me how to be a mommy\u2019: Divyanka Tripathi\u2019s emotional note to Yeh Hai Mohabbatein co-star Ruha - The Times of India", "source": "The Times of India"}, {"title": "Ruhaanika Dhawan meets her 'Ishi Maa', Divyanka Tripathi and Vivek Dahiya's twins, shares adorable pics", "source": "Moneycontrol.com"}, {"title": "Ruhaanika Dhawan Meets Divyanka Tripathi And Vivek Dahiya\u2019s Twins, Says \u2018Life Has Come Full Circle\u2019", "source": "IWMBuzz"}, {"title": "'You taught me how to be a mommy': Divyanka Tripathi's heartfelt reply to Ruhaanika Dhawan meeting her twin boys", "source": "Mid-day"}]}, {"topic_id": "9786c54b-f786-4763-986d-58f7c68f6cc7", "title": "India's TCS partners with Anthropic to drive enterprise AI scaling - Reuters", "category": "technology", "coverage": "new", "signals": [{"title": "India's TCS partners with Anthropic to drive enterprise AI scaling - Reuters", "source": "Reuters"}]}, {"topic_id": "1f5b4fd0-0d93-4e86-a5cc-a5c693ba9915", "title": "Nu Skin India Partners with The Akshaya Patra Foundation to Support 700,000 Mid-Day Meals for Government and Government-Aided School Children", "category": "food", "coverage": "new", "signals": [{"title": "Nu Skin India Partners with The Akshaya Patra Foundation to Support 700,000 Mid-Day Meals for Government and Government-Aided School Children", "source": null}]}, {"topic_id": "e26ccb71-2e22-4e4f-88c3-b388b7cf2f04", "title": "Karnataka steps up drive to reduce trans fats in food supply chain; over 45 lakh litres of used cooking oil collected since 2024", "category": "food", "coverage": "new", "signals": [{"title": "Karnataka steps up drive to reduce trans fats in food supply chain; over 45 lakh litres of used cooking oil collected since 2024", "source": null}]}, {"topic_id": "9de3072c-e870-4d70-81ec-399871fc5333", "title": "The tiny Patagonian village Messi put on the map: A 70-ton steel monument is drawing football fans from a - The Times of India", "category": "travel", "coverage": "new", "signals": [{"title": "Tens of thousands of Argentine soccer fans celebrate their team\u2019s World Cup semifinal victory", "source": "The New Indian Express"}, {"title": "\u2018No-one\u2019s ever been able to stop Lionel Messi\u2019 - Why England \u2018can\u2019t complain\u2019 about painful lesson in World Cup semi-final masterclass from Argentine GOAT", "source": "Goal.com"}, {"title": "The tiny Patagonian village Messi put on the map: A 70-ton steel monument is drawing football fans from a - The Times of India", "source": "The Times of India"}]}];

log(`Processing ${candidates.length} articles`);

phase("write");

const buildPrompt = (c) => {
  const sigs = (c.signals || []).map(s => `  - "${s.title}" (${s.source || "unknown"})`).join("
");
  const topicShort = c.topic_id.substring(0, 8);
  return `Write ONE professional news article for The Videshi (Indian diaspora news publication) and insert it into the database.

## Setup (include in EVERY exec call needing env vars)
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels 2>/dev/null; set +a

## Candidate
- topic_id: ${c.topic_id}
- title: ${c.title}
- category: ${c.category}
- coverage: ${c.coverage}
- signals:
${sigs}

## Step 1 — Research
Use browser_search with key terms from the title to find 2-3 actual news articles. Read at least 2 via browser_open. Cross-reference facts. Never fabricate.

## Step 2 — Write Article (500-800 words, HTML)
HEADLINE: 8-14 words, clear, informative.${c.coverage === "update" ? " Lead with what is NEW." : ""}
SUBHEADLINE: 1-2 sentence summary.

BODY (HTML string):
1. Key takeaways FIRST (REQUIRED, NO heading tag):
   <div class="key-takeaways"><ul><li>3-4 bullets</li></ul></div>
2. Opening paragraph (news lead)
3. <h2>Context & Background</h2>
4. <h2>Impact & Analysis</h2>
5. Diaspora angle (only if natural)
6. <h2>What’s Next</h2>

Use 1-2 pull quotes: <blockquote class="pull-quote"><p>"quote"</p><cite>— Name, Title</cite></blockquote>

RULES: Source material only. Cite naturally. NO filler ("In a significant development"). Vary sentence length. Specific numbers/dates/names.

## Step 3 — Hero Image
Try in order (use URL directly, do NOT download/upload):
1. og:image from source articles: curl -sL "<url>" | grep -oP 'property="og:image" content="\K[^"]+' | head -1
2. Person images table: curl -s "\/rest/v1/person_images?person_name_lower=eq.<name>&order=use_count.asc&limit=1" -H "apikey: " -H "Authorization: Bearer "
3. Wikipedia: curl -s "https://en.wikipedia.org/api/rest_v1/page/summary/<Name>" -H "User-Agent: TheVideshi/1.0"
4. Pexels (last resort): curl -s "https://api.pexels.com/v1/search?query=<terms>&per_page=3" -H "Authorization: "

Caption: Two factual sentences. NO flowery bridging.

## Step 4 — Insert via Python + curl
Write a Python script that creates the article JSON and saves to /tmp/article_${topicShort}.json:
- Fields: headline, subheadline, body (HTML), slug (from headline, lowercase hyphens), category ("${c.category}"), vertical ("${c.category}"), tags (array), sources (array of URLs), image_url, image_caption, image_attribution, word_count, diaspora_angle (1 sentence), topic_id ("${c.topic_id}"), published_at (UTC ISO now), article_type ("breaking"), status ("published")
- Use json.dump() to handle HTML escaping properly

Then insert:
set -a; source ~/workspace/.env.supabase; set +a
curl -s -X POST "\/rest/v1/p2_articles" -H "apikey: " -H "Authorization: Bearer " -H "Content-Type: application/json" -H "Prefer: return=representation" -d @/tmp/article_${topicShort}.json

## Step 5 — Update topic
set -a; source ~/workspace/.env.supabase; set +a
curl -s -X PATCH "\/rest/v1/p2_topics?id=eq.${c.topic_id}" -H "apikey: " -H "Authorization: Bearer " -H "Content-Type: application/json" -d '{"status":"published","last_article_id":"<ID>"}'

Return JSON: {"headline":"...", "slug":"...", "article_id":"...", "status":"success or failed", "reason":"..."}`;
};

const results = await parallel(
  candidates.map((c, i) => () => agent(buildPrompt(c), {
    key: `art-${i}`,
    label: `${c.category}: ${c.title.substring(0, 45)}`,
    timeoutMs: 900000,
    schema: {
      type: "object",
      properties: {
        headline: { type: "string" },
        slug: { type: "string" },
        article_id: { type: "string" },
        status: { type: "string" },
        reason: { type: "string" }
      },
      required: ["headline", "status"]
    }
  })),
  { concurrency: 6 }
);

const successful = results.filter(r => r !== null && r.status === "success");
const failed = results.filter(r => r !== null && r.status !== "success");
const nulled = results.filter(r => r === null);
log(`Write phase: ${successful.length} success, ${failed.length} failed, ${nulled.length} null`);

phase("enrich");
await agent(`Run enrichment on recently published Videshi articles. Continue even if individual scripts fail.

Setup:
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai 2>/dev/null; source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io; source ~/workspace/.env.apify; source ~/workspace/.env.youtube; set +a
cd ~/workspace/the-videshi-news/pipeline

Run in order:
1. timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply 2>&1
2. timeout 600 python3 -u enrich-articles.py --hours 3 --apply 2>&1
3. timeout 600 python3 -u enrich-data-cards.py --since-hours 3 --limit 10 2>&1
4. timeout 120 python3 -u proofread-article.py --hours 3 --apply 2>&1

Report summary of each.`, {
  key: "enrich",
  label: "Enrich articles",
  timeoutMs: 1200000
});

phase("publish");
await agent(`Rebuild feeds and push to git:
cd ~/workspace/the-videshi-news/pipeline && python3 -u prebuild-feeds.py 2>&1
cd ~/workspace/the-videshi-news && git add -A && git commit -m "V3 pipeline articles 6-07-22" && git push origin main 2>&1
Report success/failure.`, {
  key: "publish",
  label: "Rebuild feeds and push",
  timeoutMs: 300000
});

const headlinesByCategory = {};
successful.forEach(r => {
  const cat = candidates[results.indexOf(r)]?.category || "unknown";
  if (!headlinesByCategory[cat]) headlinesByCategory[cat] = [];
  headlinesByCategory[cat].push(r.headline);
});

return {
  message: `V3 pipeline complete: ${successful.length}/${candidates.length} articles published`,
  articles_by_category: headlinesByCategory,
  failed: failed.map(r => `${r.headline}: ${r.reason || "unknown"}`),
  timed_out: nulled.length
};
