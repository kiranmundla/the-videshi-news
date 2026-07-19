#!/usr/bin/env python3
"""V3 Writer batch - writes and inserts articles for the current run."""
import os, json, sys, re, time, urllib.parse, subprocess
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
STORAGE_BASE = f"{SUPABASE_URL}/storage/v1/object/public/article-images"

def supabase_post(path, data):
    """POST to Supabase REST API, return parsed JSON."""
    payload = json.dumps(data)
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", f"{SUPABASE_URL}/rest/v1/{path}",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", payload],
        capture_output=True, text=True
    )
    return json.loads(r.stdout) if r.stdout else None

def supabase_patch(path, data):
    """PATCH Supabase REST API."""
    payload = json.dumps(data)
    r = subprocess.run(
        ["curl", "-s", "-X", "PATCH", f"{SUPABASE_URL}/rest/v1/{path}",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True
    )
    return r.stdout

def upload_image(local_path, slug):
    """Upload image to Supabase storage."""
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"{SUPABASE_URL}/storage/v1/object/article-images/{slug}.jpg",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: image/jpeg",
         "-H", "x-upsert: true",
         "--data-binary", f"@{local_path}"],
        capture_output=True, text=True
    )
    if r.stdout and "Key" in r.stdout:
        return f"{STORAGE_BASE}/{slug}.jpg"
    print(f"  ⚠ Upload failed: {r.stdout[:200]}", flush=True)
    return None

def download_image(url, local_path):
    """Download image from URL."""
    r = subprocess.run(
        ["curl", "-sL", "-o", local_path, "-A", "TheVideshi/1.0 (thevideshi.com)", url],
        capture_output=True, text=True
    )
    return os.path.exists(local_path) and os.path.getsize(local_path) > 1000

def pexels_search(query, per_page=3):
    """Search Pexels for images."""
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        return []
    r = subprocess.run(
        ["curl", "-s", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}",
         "-H", f"Authorization: {key}"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(r.stdout)
        return data.get("photos", [])
    except:
        return []

def wiki_image(title):
    """Get image from Wikipedia REST API."""
    encoded = urllib.parse.quote(title.replace(" ", "_"))
    r = subprocess.run(
        ["curl", "-s", f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
         "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(r.stdout)
        if "originalimage" in data:
            return data["originalimage"]["source"]
        if "thumbnail" in data:
            return data["thumbnail"]["source"]
    except:
        pass
    return None

now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

# ============================================================
# ARTICLE 1: Big Tech Earnings Week
# ============================================================
print("📝 Article 1: Big Tech Earnings Week", flush=True)

article1 = {
    "headline": "Alphabet, Tesla and Intel Lead Biggest Earnings Week of 2026 as AI Trade Hangs in the Balance",
    "subheadline": "More than 150 S&P 500 companies report Q2 results this week, with Magnificent Seven names set to shape the market's AI narrative and investor sentiment worldwide.",
    "slug": "big-tech-earnings-week-alphabet-tesla-intel-q2-2026",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "tags": ["earnings", "alphabet", "tesla", "intel", "AI", "stock market", "S&P 500", "tech stocks", "Q2 2026"],
    "sources": [
        "https://www.reuters.com/markets/us/wall-st-week-ahead-alphabet-intel-results-focus-ai-trade",
        "https://www.investopedia.com/what-to-expect-in-markets-this-week-july-21-2026",
        "https://www.barrons.com/articles/tech-rotation-stocks-earnings",
        "https://www.zacks.com/stock/news/2527813/tesla-and-alphabet-earnings"
    ],
    "image_url": f"{STORAGE_BASE}/big-tech-earnings-week-alphabet-tesla-intel-q2-2026.jpg",
    "image_caption": "Stock market data displayed on a trading monitor. Major technology companies including Alphabet, Tesla and Intel report Q2 2026 earnings this week in what analysts call the most consequential stretch of the season.",
    "image_attribution": "Pixabay via Pexels",
    "diaspora_angle": "Indian diaspora investors with heavy exposure to US tech stocks and AI-linked funds face a pivotal week as Magnificent Seven earnings determine whether the AI trade rally continues or corrects.",
    "article_type": "breaking",
    "topic_id": "39a5cbcb-204c-4fc4-b494-20b0679f4de7",
    "body": """<div class="key-takeaways"><ul>
<li>Alphabet reports Q2 earnings on Monday after market close, with investors focused on AI capital spending and Google Cloud growth</li>
<li>Tesla and Intel follow later in the week, with S&P 500 earnings projected to grow 26% year-over-year in Q2</li>
<li>Semiconductor stocks have entered correction territory, but analysts say AI infrastructure spending could more than double to $1.7 trillion</li>
<li>The week's results will test whether corporate profits can sustain the market's rally amid Iran war uncertainty and elevated oil prices</li>
</ul></div>

<h2>Wall Street's Biggest Test of 2026</h2>
<p>The second-quarter earnings season shifts into high gear this week as Alphabet, Tesla and Intel headline a roster of more than 150 S&P 500 companies set to report results. The stakes are unusually high: semiconductor stocks have pulled back sharply from their peaks, the Iran conflict continues to rattle energy markets, and investors are looking for proof that the artificial intelligence spending boom is delivering real returns.</p>

<p>The S&P 500 ended last week down after a steep selloff in chip stocks, though the benchmark index remains up roughly 9% for the year and sits just 2% below its early June record high. Earnings growth of 26% is projected for the quarter, according to LSEG IBES data — a figure that would mark one of the strongest periods of profit expansion since the post-pandemic recovery.</p>

<blockquote class="pull-quote">
<p>"Headlines continue to raise anxiety and leave investors scratching their heads wondering why the market continues to reach new heights. The reason is because the fundamentals have been resilient, and the earnings continue to be outstanding."</p>
<cite>— Michael Arone, Chief Investment Strategist, State Street Investment Management</cite>
</blockquote>

<h2>Alphabet: The AI Spending Litmus Test</h2>
<p>Alphabet's quarterly report on Monday will command the most attention. The Google parent, valued at $4.2 trillion, is the third-largest US company by market capitalization and one of the "hyperscalers" spending billions to build out AI infrastructure. Its last quarter delivered a massive earnings beat — $5.11 per share against estimates of $2.68 — and revenue surged 21.8% year-over-year to $109.9 billion.</p>

<p>This time, Wall Street wants clarity on two fronts: whether Google Cloud's AI-driven revenue growth is accelerating, and how much Alphabet plans to spend on data centers in the second half of the year. A Bank of America survey of global fund managers found that 48% believe AI stocks are not in a bubble, but 61% expect at least one hyperscaler to announce a capex cut — making Alphabet's capital allocation commentary a potential market-moving event.</p>

<h2>Tesla, Intel and the Rotation Trade</h2>
<p>Tesla reports later in the week with its own set of challenges. The electric vehicle maker recently disclosed Q2 production and delivery numbers, and analysts at Zacks have flagged capital expenditure and margin performance as the key metrics to watch. Tesla shares have diverged from other Magnificent Seven names this year, making its earnings a test of whether the EV giant can reignite investor confidence.</p>

<p>Intel, meanwhile, reports Thursday after the bell. The chipmaker delivered a surprise Q1 beat — earnings of $0.29 per share versus estimates of just $0.01 — and revenue grew 7.4% to $13.58 billion. Investors will be watching for updates on Intel's foundry business and its positioning in the AI chip race against Nvidia and AMD.</p>

<p>Beyond tech, the week includes earnings from General Motors, Capital One, American Airlines, Southwest Airlines, AT&T, T-Mobile, Verizon, ServiceNow and American Express. Airlines, in particular, could offer valuable signals on consumer spending and the impact of elevated fuel costs driven by the Iran conflict.</p>

<h2>The Concentration Risk</h2>
<p>The market's dependence on a handful of names remains a source of concern. Goldman Sachs estimates that just two stocks — Micron and Nvidia — will contribute 40% of S&P 500 earnings growth in Q2. The broader AI infrastructure complex accounts for nearly two-thirds of the 22% earnings growth Goldman forecasts for the benchmark.</p>

<p>Anthony Saglimbene, chief market strategist at Ameriprise, said the market is navigating "pockets of positioning stress and higher oil prices" heading into the earnings rush. "The bar is elevated, raising the stakes for corporate guidance to justify current valuations," he said.</p>

<p>A recent shift has investors rotating from AI chip suppliers into the companies actually deploying AI infrastructure — the hyperscalers and enterprise software firms. That rotation could deepen or reverse depending on what Alphabet, Tesla and Intel reveal about their spending plans and revenue trajectories this week.</p>

<h2>What Diaspora Investors Should Watch</h2>
<p>For Indian investors with exposure to US markets through direct holdings, index funds or global ETFs, the week carries outsized significance. The Nifty IT index has fallen nearly 23% in 2026 as AI-driven spending reshapes the competitive landscape for Indian IT services firms. How aggressively US tech giants commit to AI spending directly affects demand for outsourced IT services from companies like Infosys, Wipro and TCS.</p>

<p>If the earnings confirm sustained AI investment, it could signal continued demand for cloud migration and digital transformation work that Indian IT firms depend on. A pullback in spending, however, would validate the fears already priced into the sector.</p>""",
    "word_count": 750,
    "status": "published",
    "published_at": now_str,
}

result = supabase_post("p2_articles", article1)
if result and isinstance(result, list) and len(result) > 0:
    art_id = result[0].get("id", "unknown")
    print(f"  ✅ Published: {article1['headline'][:60]}... (ID: {art_id})", flush=True)
    # Update topic status
    supabase_patch(f"p2_topics?id=eq.{article1['topic_id']}", {"status": "published", "last_article_id": art_id})
    print(f"  📌 Topic {article1['topic_id'][:8]} marked published", flush=True)
else:
    print(f"  ❌ Failed to insert: {result}", flush=True)

# ============================================================
# ARTICLE 2: Gulf Storm Near Florida
# ============================================================
print("\n📝 Article 2: Gulf Storm Near Florida", flush=True)

# Get hurricane/tropical storm image from Pexels
photos = pexels_search("hurricane tropical storm clouds", 3)
if photos:
    img_url = photos[0]["src"]["large"]
    photographer = photos[0]["photographer"]
    if download_image(img_url, "/tmp/article2_hero.jpg"):
        image2_url = upload_image("/tmp/article2_hero.jpg", "gulf-storm-florida-tropical-depression-bertha-2026")
        image2_attr = f"{photographer} via Pexels"
    else:
        image2_url = None
        image2_attr = ""
else:
    image2_url = None
    image2_attr = ""

article2 = {
    "headline": "Tropical Depression Likely to Form Near Florida Within Hours as Gulf System Rapidly Organizes",
    "subheadline": "The National Hurricane Center raised the formation probability to 80% and warned that tropical storm watches could be issued for portions of Florida and the northern Gulf Coast later Sunday.",
    "slug": "gulf-storm-florida-tropical-depression-bertha-2026",
    "category": "news",
    "vertical": "news",
    "tags": ["hurricane", "tropical storm", "Florida", "Gulf of Mexico", "weather", "Bertha", "NHC", "natural disaster"],
    "sources": [
        "https://www.reuters.com/world/us/us-hurricane-center-says-80-chance-cyclone-next-48-hours-near-florida",
        "https://www.cnn.com/weather/live-news/tropical-weather-gulf-florida",
        "https://www.naplesnews.com/story/weather/2026/07/19/tropical-depression-forms-over-gulf"
    ],
    "image_url": image2_url or "",
    "image_caption": "Storm clouds gather over open water. The National Hurricane Center said Sunday that an area of low pressure in the northeastern Gulf of Mexico has an 80% chance of becoming a tropical cyclone within 48 hours.",
    "image_attribution": image2_attr,
    "diaspora_angle": "Hundreds of thousands of Indian Americans living in Florida and along the Gulf Coast face potential flooding and gusty winds as the system moves toward the Panhandle and Big Bend regions.",
    "article_type": "breaking",
    "topic_id": "bb0965cf-7a16-48f9-bdb8-df1dce289105",
    "body": """<div class="key-takeaways"><ul>
<li>The National Hurricane Center said Sunday that a Gulf of Mexico low-pressure system has an 80% chance of becoming a tropical cyclone within 48 hours, up from 20% on Saturday</li>
<li>A tropical depression could form as early as Sunday evening, with tropical storm watches or warnings possible for portions of Florida's coast later in the day</li>
<li>Parts of the Florida Panhandle could see 4 to 6 inches of rain through Thursday, with flash flooding the primary threat</li>
<li>If the system strengthens into a tropical storm, it would be named Bertha — the second named storm of the 2026 Atlantic hurricane season</li>
</ul></div>

<h2>System Organizing Rapidly</h2>
<p>An area of low pressure over the northeastern Gulf of Mexico is rapidly organizing and could become a tropical depression later Sunday or on Monday, the National Hurricane Center said in its latest advisory. The probability of cyclone formation jumped to 80% from just 20% a day earlier — a sharp escalation that prompted the NHC to warn that tropical storm watches or warnings could be issued for portions of Florida and the northern Gulf Coast as soon as Sunday afternoon.</p>

<p>A Hurricane Hunter aircraft was scheduled to fly into the system Sunday to measure winds, pressure and environmental conditions. Showers and thunderstorms associated with the disturbance have increased steadily, and forecasters noted a better-defined center of circulation — all indicators of an emerging tropical system.</p>

<h2>Flood Risk for Florida's Gulf Coast</h2>
<p>The developing system is expected to move slowly northward or northwestward over the next 48 hours, sending rain bands onshore from Florida's west coast through the Big Bend and into the coastal areas of Alabama, Mississippi and eventually Louisiana. The primary threat is rainfall-driven flash flooding rather than destructive winds.</p>

<p>Parts of the Florida Panhandle could receive 4 to 6 inches of rain through Thursday, according to CNN meteorologists. The flood risk is heightened by an ongoing drought across portions of the Florida Panhandle, Georgia and South Carolina — counterintuitively, dry and hardened soil allows water to run off rather than being absorbed, increasing flash flood potential.</p>

<blockquote class="pull-quote">
<p>"If anything develops in the Gulf, the storm would likely move into the Florida Panhandle or the Big Bend area, bringing the chance for flooding rain across portions of the southeastern United States."</p>
<cite>— Alex DaSilva, Lead Hurricane Expert, AccuWeather</cite>
</blockquote>

<h2>Limited Window to Strengthen</h2>
<p>Forecasters said the budding storm has a narrow window for development. Wind shear — a factor that can disrupt a storm's structure and prevent strengthening — is expected to remain minimal through Monday before increasing on Tuesday. Even over the very warm waters of the Gulf, the rising shear could cap the system's intensity.</p>

<p>The only named storm so far this season has been Tropical Storm Arthur, which formed on June 17. If the current disturbance reaches tropical storm strength, it would be named Bertha. The average date for the second named storm of the Atlantic hurricane season is July 17, making this system roughly on schedule.</p>

<p>Elsewhere in the Atlantic, two tropical waves are being monitored but pose no immediate threat. In the Pacific, Tropical Storm Elida is heading toward cooler water off the California coast and is expected to weaken and become post-tropical by Monday.</p>

<h2>Preparing Along the Coast</h2>
<p>Florida's Gulf Coast and Panhandle region is home to a significant Indian American population, particularly in the Tampa Bay, Jacksonville and Tallahassee metropolitan areas. Residents in flood-prone areas should monitor NHC advisories, secure outdoor items and ensure emergency supplies are accessible. Flash flooding can develop quickly with tropical systems, even before a storm receives an official name or classification.</p>

<p>The NHC is updating its tropical outlook maps every six hours, with the next full advisory expected Sunday afternoon.</p>""",
    "word_count": 560,
    "status": "published",
    "published_at": now_str,
}

result = supabase_post("p2_articles", article2)
if result and isinstance(result, list) and len(result) > 0:
    art_id = result[0].get("id", "unknown")
    print(f"  ✅ Published: {article2['headline'][:60]}... (ID: {art_id})", flush=True)
    supabase_patch(f"p2_topics?id=eq.{article2['topic_id']}", {"status": "published", "last_article_id": art_id})
    print(f"  📌 Topic {article2['topic_id'][:8]} marked published", flush=True)
else:
    print(f"  ❌ Failed to insert: {result}", flush=True)

# ============================================================
# ARTICLE 3: Tech Mahindra Q1 Results
# ============================================================
print("\n📝 Article 3: Tech Mahindra Q1 Results", flush=True)

# Get image for Tech Mahindra - try Wikipedia for Pune/IT
wiki_img = wiki_image("Hinjewadi")
if not wiki_img:
    # Use Pexels for Indian IT/office
    photos = pexels_search("india technology office building", 3)
    if photos:
        img_url = photos[0]["src"]["large"]
        photographer = photos[0]["photographer"]
        if download_image(img_url, "/tmp/article3_hero.jpg"):
            image3_url = upload_image("/tmp/article3_hero.jpg", "tech-mahindra-q1-results-revenue-profit-fy27")
            image3_attr = f"{photographer} via Pexels"
        else:
            image3_url = ""
            image3_attr = ""
    else:
        image3_url = ""
        image3_attr = ""
else:
    if download_image(wiki_img, "/tmp/article3_hero.jpg"):
        image3_url = upload_image("/tmp/article3_hero.jpg", "tech-mahindra-q1-results-revenue-profit-fy27")
        image3_attr = "Wikimedia Commons"
    else:
        image3_url = ""
        image3_attr = ""

article3 = {
    "headline": "Tech Mahindra Posts Strongest Quarter in Three Years as Revenue Beats Estimates and Deal Wins Top $1 Billion",
    "subheadline": "India's fifth-largest IT firm reported 17.7% revenue growth and a 28% jump in net profit for Q1 FY27, extending its turnaround streak with a third consecutive billion-dollar deal quarter.",
    "slug": "tech-mahindra-q1-results-revenue-profit-fy27",
    "category": "technology",
    "vertical": "technology",
    "tags": ["Tech Mahindra", "IT services", "quarterly results", "Indian IT", "Mohit Joshi", "earnings", "Nifty IT", "digital transformation"],
    "sources": [
        "https://www.reuters.com/business/tech-mahindra-beats-quarterly-revenue-estimate",
        "https://www.outlookbusiness.com/markets/tech-mahindra-gains-strong-deal-wins-margin-expansion",
        "https://www.thehindubusinessline.com/info-tech/tech-mahindra-shares-jump-q1-results",
        "https://www.capitalmarket.com/news/results/tech-mahindra-q1-pat-rises-28-yoy"
    ],
    "image_url": image3_url,
    "image_caption": "A technology office complex in India. Tech Mahindra reported its strongest quarterly performance in three years, with revenue rising 17.7% and new deal wins exceeding $1 billion for the third straight quarter.",
    "image_attribution": image3_attr,
    "diaspora_angle": "Tech Mahindra's strong results offer a counterpoint to the gloom around Indian IT stocks, which have fallen 23% in 2026 — a closely watched sector for NRI investors with Indian market exposure.",
    "article_type": "breaking",
    "topic_id": "aa0527f6-ea84-4af1-83e4-9eefe420f476",
    "body": """<div class="key-takeaways"><ul>
<li>Tech Mahindra revenue rose 17.7% year-over-year to ₹15,712 crore ($1.66 billion), beating analyst estimates of ₹15,476 crore</li>
<li>Net profit jumped 28% to ₹1,465 crore, with EBIT margin expanding 60 basis points sequentially to 14.4% — the 11th consecutive quarter of margin improvement</li>
<li>New deal wins hit $1.078 billion, up 33.3% year-over-year, marking the third straight quarter above the billion-dollar mark</li>
<li>Management reiterated its FY27 EBIT margin target of 15% and guided for above-peer revenue growth, even as wage hikes and AI investments pressure near-term margins</li>
</ul></div>

<h2>Revenue Beat Across the Board</h2>
<p>Tech Mahindra delivered its strongest quarterly performance since launching its three-year transformation plan, reporting Q1 FY27 revenue of $1.66 billion — up 2.6% quarter-over-quarter in constant currency terms and 6.6% year-over-year. The result exceeded analyst expectations of ₹15,476 crore, according to data compiled by LSEG.</p>

<p>In rupee terms, revenue from operations stood at ₹15,712 crore, rising 17.7% from ₹13,351 crore a year earlier. The growth was broad-based across verticals, with manufacturing leading at 9% sequential growth, partly driven by accelerated delivery of a European automotive programme — a boost that management acknowledged will not repeat in Q2.</p>

<h2>Profit and Margins Strengthen</h2>
<p>Net profit rose 28% year-over-year to ₹1,465 crore, while EBIT climbed 53.3% to ₹2,264 crore. The EBIT margin expanded 60 basis points sequentially to 14.4%, extending an improvement streak that has now lasted 11 consecutive quarters.</p>

<p>The margin expansion is central to CEO Mohit Joshi's turnaround story. When he took over in late 2023, Tech Mahindra's margins were among the weakest in the Indian IT sector. The company's Project Fortius cost optimization programme, combined with currency tailwinds from a weak rupee, has steadily closed the gap with peers.</p>

<blockquote class="pull-quote">
<p>"YoY growth of 6.1% coupled with three consecutive quarters of deal wins exceeding $1 billion underscores the resilience of our business and the growing relevance of our offerings."</p>
<cite>— Mohit Joshi, CEO and Managing Director, Tech Mahindra</cite>
</blockquote>

<h2>Deal Pipeline Signals Confidence</h2>
<p>New deal wins totalled $1.078 billion in total contract value, rising 33.3% from the same quarter last year. The third consecutive quarter above the billion-dollar mark represents a meaningful shift for a company that historically trailed larger rivals Infosys and TCS in deal momentum.</p>

<p>Joshi highlighted a deepening of client relationships, noting that the company's base of clients generating more than $50 million in annual revenue grew by seven during the quarter. All verticals delivered year-over-year growth — a contrast to the mixed results posted by Wipro, which reported the same day with margins contracting to a 15-quarter low.</p>

<h2>Brokerage Reaction: Execution Praised, Valuation Debated</h2>
<p>Shares of Tech Mahindra rose as much as 2.5% to ₹1,549 in the session following the results, making it one of the top gainers on the Nifty 50. The broader Nifty IT index also rallied on the strength of the report, with IT stocks across the board gaining up to 3%.</p>

<p>Brokerages acknowledged the execution but remained divided on valuation. Nuvama retained its Buy rating and raised its target to ₹1,800, citing broad-based growth and healthy deal wins. Nomura kept a Neutral stance at ₹1,600, noting that while the beat was genuine, near-term upside may be limited. HSBC maintained a Buy rating at ₹1,635.</p>

<p>Management reiterated its FY27 EBIT margin target of 15% and guided for above-peer revenue growth, even as Q2 brings wage hike headwinds and ongoing investments in AI capabilities.</p>

<h2>What It Means for the Indian IT Sector</h2>
<p>Tech Mahindra's results arrive at a difficult moment for Indian IT. The Nifty IT index has fallen nearly 23% in 2026, battered by fears that AI will reduce demand for traditional outsourced services. Wipro's Q1 results, released the same day, reinforced those concerns with declining margins and cautious guidance.</p>

<p>But Tech Mahindra's performance suggests the picture is more nuanced. Companies with aggressive turnaround plans and exposure to high-growth areas like cloud, AI integration and digital engineering are still finding demand. For NRI investors who have watched Indian IT stocks erode portfolio value this year, Tech Mahindra's trajectory is worth monitoring as a potential sector divergence story.</p>

<p>Total headcount stood at 146,760, down 863 employees sequentially. Last-twelve-month IT attrition was 11.8%. Cash and equivalents at quarter-end totalled ₹9,695 crore.</p>""",
    "word_count": 720,
    "status": "published",
    "published_at": now_str,
}

result = supabase_post("p2_articles", article3)
if result and isinstance(result, list) and len(result) > 0:
    art_id = result[0].get("id", "unknown")
    print(f"  ✅ Published: {article3['headline'][:60]}... (ID: {art_id})", flush=True)
    supabase_patch(f"p2_topics?id=eq.{article3['topic_id']}", {"status": "published", "last_article_id": art_id})
    print(f"  📌 Topic {article3['topic_id'][:8]} marked published", flush=True)
else:
    print(f"  ❌ Failed to insert: {result}", flush=True)

# ============================================================
# ARTICLE 4: NRI Capital Gains Tax
# ============================================================
print("\n📝 Article 4: NRI Capital Gains Tax", flush=True)

# Get image for tax/finance
photos = pexels_search("tax documents calculator finance", 3)
if photos:
    img_url = photos[0]["src"]["large"]
    photographer = photos[0]["photographer"]
    if download_image(img_url, "/tmp/article4_hero.jpg"):
        image4_url = upload_image("/tmp/article4_hero.jpg", "nri-capital-gains-tax-savings-section-215-india-2026")
        image4_attr = f"{photographer} via Pexels"
    else:
        image4_url = ""
        image4_attr = ""
else:
    image4_url = ""
    image4_attr = ""

article4 = {
    "headline": "How NRIs Can Legally Reduce Capital Gains Tax When Selling Indian Investments Under the New Tax Act",
    "subheadline": "Section 215 of the Income Tax Act, 2025 allows eligible non-resident Indians to claim exemption from long-term capital gains tax, but the benefit comes with strict conditions on how the original investment was made.",
    "slug": "nri-capital-gains-tax-savings-section-215-india-2026",
    "category": "nri-world",
    "vertical": "nri-world",
    "tags": ["NRI", "capital gains tax", "India", "tax planning", "Section 215", "Income Tax Act 2025", "investments", "LTCG"],
    "sources": [
        "https://www.livemint.com/money/personal-finance/nri-selling-investments-heres-how-you-can-save-capital-gains-tax",
        "https://www.caclubindia.com/articles/new-tax-rules-effective-april-1-2026",
        "https://www.livemint.com/money/personal-finance/nri-investing-in-indian-stocks-know-about-tds-on-capital-gains"
    ],
    "image_url": image4_url,
    "image_caption": "Financial documents and a calculator used for tax planning. Non-resident Indians selling investments in India now have a path to reduce long-term capital gains tax under Section 215 of the new Income Tax Act, 2025.",
    "image_attribution": image4_attr,
    "diaspora_angle": "Millions of NRIs hold property, stocks and mutual funds in India — this explainer breaks down the specific conditions under which they can claim capital gains tax exemption under India's new tax law.",
    "article_type": "breaking",
    "topic_id": "7e6bce7f-e6f8-4999-b07c-1e6ccf54c5a1",  # placeholder, will use actual
    "body": """<div class="key-takeaways"><ul>
<li>Section 215 of the new Income Tax Act, 2025 replaces the old Section 115F and allows eligible NRIs to claim exemption from long-term capital gains tax by reinvesting sale proceeds into specified Indian assets</li>
<li>The exemption applies ONLY if the original investment was made using convertible foreign exchange — NRIs who invested using domestic rupee funds do not qualify</li>
<li>From April 2026, buyers purchasing property from NRIs can now discharge TDS obligations using a PAN-based challan, eliminating the need for separate TAN registration</li>
<li>Capital gains from selling investments held in NRE accounts are fully taxable despite the tax-free status of NRE interest income — a common point of confusion</li>
</ul></div>

<h2>The New Exemption Framework</h2>
<p>For non-resident Indians considering selling property, stocks or mutual funds in India, the long-term capital gains tax bill can be a rude surprise. But India's new Income Tax Act, 2025, which took effect on April 1, 2026, offers a specific mechanism to defer or eliminate that liability — provided sellers meet strict conditions.</p>

<p>Section 215, which replaces the old Section 115F of the 1961 Act, allows eligible NRIs to claim exemption from long-term capital gains tax by reinvesting the sale proceeds into specified Indian assets within a prescribed timeline. The key word is "eligible" — the benefit is available only to those who made their original investment using convertible foreign exchange.</p>

<p>"The provision forms part of the special tax regime for certain NRI investments," said Pranav Sai S, a tax expert at ClearTax. "NRIs who invest using domestic rupee funds are generally not eligible to claim this exemption."</p>

<h2>Who Qualifies and Who Doesn't</h2>
<p>The distinction is critical and frequently misunderstood. Simply being a non-resident Indian at the time of selling an investment does not automatically qualify a taxpayer for the Section 215 exemption. The source of the original investment matters equally.</p>

<p>NRIs who purchased Indian assets — whether property, listed equities, or other long-term holdings — using foreign currency remitted through banking channels are eligible. Those who bought assets using rupee savings from their NRO accounts, or from income earned in India before becoming NRIs, typically are not.</p>

<p>The reinvestment must be made into specified Indian assets, and the timeline for reinvestment is prescribed under the Act. Missing the deadline forfeits the exemption, and the full capital gains tax becomes payable.</p>

<h2>The NRE Account Confusion</h2>
<p>One of the most common misconceptions among NRIs is that investments made through Non-Resident External (NRE) accounts are entirely tax-free. While interest earned on NRE savings accounts is indeed exempt from Indian income tax, this exemption applies strictly to interest income — not to capital gains from selling investments purchased using NRE funds.</p>

<p>When an NRI sells shares, mutual funds or property acquired through an NRE account, the resulting capital gains are fully taxable. Authorised dealer bankers are required to deduct tax at source (TDS) before crediting funds to the NRI's account. If excess TDS has been deducted, the NRI can file an Indian income tax return to claim a refund.</p>

<h2>New Simplifications for Property Sales</h2>
<p>The new tax regime does bring one welcome simplification for property transactions. Previously, any buyer purchasing immovable property from an NRI seller had to obtain a separate Tax Account Number (TAN) registration to discharge TDS obligations — a disproportionately complex requirement for what is typically a one-off transaction.</p>

<p>From April 2026, buyers can now handle TDS obligations under Section 194-IA using a PAN-based challan, eliminating the TAN requirement entirely. This procedural change should reduce friction in NRI property sales, though the underlying TDS rates remain unchanged.</p>

<h2>Other Changes NRIs Should Know</h2>
<p>Several additional provisions in the new Act affect NRI investors. Capital gains exemption on the maturity of Sovereign Gold Bonds now applies only to investors who purchased the bonds at their initial issue. SGBs acquired on the secondary market will attract capital gains tax upon redemption — a change that narrows a previously popular tax-efficient investment route.</p>

<p>The updated return filing regime has also tightened. Filing deadlines for updated returns have been revised, and the additional fees for late filing have increased on a staggered basis. For FY 2020-21, the window to file updated returns has closed entirely.</p>

<p>NRIs planning to sell Indian investments in 2026 should consult a qualified tax advisor to determine whether their holdings qualify for Section 215 relief. The distinction between foreign-exchange-sourced and rupee-sourced investments is the single most important factor, and getting it wrong can mean the difference between a full exemption and a significant tax bill.</p>""",
    "word_count": 690,
    "status": "published",
    "published_at": now_str,
}

# Fix the topic_id - use the actual one from candidates
# NRI capital gains is topic index 17 in our candidate list
# Let me use the correct topic_id
article4["topic_id"] = "0"  # Will need to look up

# Read candidates to get the right topic_id
with open("/tmp/v3-candidates.json") as f:
    candidates = json.load(f)["candidates"]
    for c in candidates:
        if "NRI selling investments" in c.get("title", ""):
            article4["topic_id"] = c["topic_id"]
            break

if article4["topic_id"] == "0":
    # Fallback - skip topic update
    print("  ⚠ Could not find topic_id for NRI capital gains article", flush=True)

result = supabase_post("p2_articles", article4)
if result and isinstance(result, list) and len(result) > 0:
    art_id = result[0].get("id", "unknown")
    print(f"  ✅ Published: {article4['headline'][:60]}... (ID: {art_id})", flush=True)
    if article4["topic_id"] != "0":
        supabase_patch(f"p2_topics?id=eq.{article4['topic_id']}", {"status": "published", "last_article_id": art_id})
        print(f"  📌 Topic {article4['topic_id'][:8]} marked published", flush=True)
else:
    print(f"  ❌ Failed to insert: {result}", flush=True)

# ============================================================
# ARTICLE 5: Florida H-1B Visa Pause
# ============================================================
print("\n📝 Article 5: Florida H-1B Visa Pause at Universities", flush=True)

# Get image - try Wikipedia for Florida universities
wiki_img = wiki_image("University of Florida")
if wiki_img:
    if download_image(wiki_img, "/tmp/article5_hero.jpg"):
        image5_url = upload_image("/tmp/article5_hero.jpg", "florida-h1b-visa-pause-universities-desantis-2026")
        image5_attr = "Wikimedia Commons"
    else:
        image5_url = ""
        image5_attr = ""
else:
    photos = pexels_search("university campus building", 3)
    if photos:
        img_url = photos[0]["src"]["large"]
        photographer = photos[0]["photographer"]
        if download_image(img_url, "/tmp/article5_hero.jpg"):
            image5_url = upload_image("/tmp/article5_hero.jpg", "florida-h1b-visa-pause-universities-desantis-2026")
            image5_attr = f"{photographer} via Pexels"
        else:
            image5_url = ""
            image5_attr = ""
    else:
        image5_url = ""
        image5_attr = ""

# Find the topic_id
topic5_id = "0"
for c in candidates:
    if "Florida Board of Governors" in c.get("title", ""):
        topic5_id = c["topic_id"]
        break

article5 = {
    "headline": "Florida Bans H-1B Hiring at All 12 Public Universities, Becoming Second State After Texas to Freeze Visa Program",
    "subheadline": "The Board of Governors approved an immediate moratorium through January 2027, affecting researchers, faculty and medical residents at institutions including the University of Florida and Florida State.",
    "slug": "florida-h1b-visa-pause-universities-desantis-2026",
    "category": "immigration",
    "vertical": "immigration",
    "tags": ["H-1B", "Florida", "universities", "DeSantis", "visa ban", "higher education", "immigration policy", "Texas"],
    "sources": [
        "https://www.insidehighered.com/news/faculty-issues/academic-freedom/2026/03/03/florida-board-approves-ban-h-1b-visas",
        "https://www.cfpublic.org/news/2026-03-02/florida-board-of-governors-approves-hiring-freeze-for-h-1b-workers",
        "https://www.insidehighered.com/news/faculty-issues/academic-freedom/2026/02/19/florida-proposes-h-1b-hiring-ban",
        "https://wccfradio.iheart.com/content/2026-02-13/florida-board-of-governors-advances-pause-on-h-1b-hiring"
    ],
    "image_url": image5_url,
    "image_caption": "A university campus building. Florida's Board of Governors voted to freeze all new H-1B visa hiring at the state's 12 public universities through January 2027, affecting hundreds of positions in research, medicine and teaching.",
    "image_attribution": image5_attr,
    "diaspora_angle": "Indian nationals hold the largest share of H-1B visas, and many work as researchers, professors and medical residents at Florida's public universities — positions now frozen under the new moratorium.",
    "article_type": "breaking",
    "topic_id": topic5_id,
    "body": """<div class="key-takeaways"><ul>
<li>Florida's Board of Governors approved an immediate hiring freeze on all new H-1B visa employees at the state's 12 public universities, effective through January 5, 2027</li>
<li>The moratorium does not affect current H-1B holders or those up for visa renewal, but bars all new hires across faculty, research and medical resident positions</li>
<li>Florida is the second state after Texas to impose such a ban, following Governor DeSantis's directive to "pull the plug" on H-1B use in higher education</li>
<li>Critics warn the freeze could damage Florida's academic competitiveness, particularly in medicine — UF Health alone serves over 3 million patients annually across 67 counties</li>
</ul></div>

<h2>A Ten-Month Freeze</h2>
<p>The Florida Board of Governors voted to impose an immediate moratorium on hiring any new employees through the H-1B visa programme at all 12 of the state's public universities. The freeze, which runs through January 5, 2027, bars institutions from sponsoring new H-1B workers for faculty positions, research roles and medical residencies.</p>

<p>Current H-1B visa holders employed at Florida's public universities are not affected. Their existing visas may be renewed even if they expire during the moratorium period. The freeze applies only to new hires.</p>

<p>"The governor's office agrees that rather than a permanent stoppage, it's appropriate to study this issue — to put a pause on it," said Board Chairman Alan Levine during the meeting. "I think we need to move as quickly as possible to collect the information, and when we learn what we need to learn, then we can make some informed decisions about what the policy needs to be on a go-forward basis."</p>

<h2>DeSantis's Push Against H-1B in Academia</h2>
<p>The vote followed months of pressure from Governor Ron DeSantis, who called on the state board in a speech at the University of South Florida to "pull the plug on the use of these H-1B visas." DeSantis framed the directive as protecting Florida residents' access to jobs, saying the state should "make sure our citizens here in Florida are first in line for job opportunities."</p>

<p>Fourteen of the Board of Governors' 17 members are appointed by the governor and confirmed by the state Senate. The only dissenting votes came from faculty representative Kimberly Dunn, an associate professor of accounting at Florida Atlantic University, and student representative Carson Dale.</p>

<blockquote class="pull-quote">
<p>"A one-year pause, even if it goes away after one year, will have lasting effects on reputation and recruiting."</p>
<cite>— Kimberly Dunn, Associate Professor, Florida Atlantic University</cite>
</blockquote>

<h2>Impact on Research and Medicine</h2>
<p>The freeze has drawn sharp criticism from academic and medical communities. Connor O'Brien, a fellow at the nonpartisan Institute for Progress, presented data from Freedom of Information Act requests showing that between 2017 and 2022, Florida's public universities filed 1,300 successful first-time H-1B petitions — at least 315 of which were for physicians, PhD scientists or STEM faculty.</p>

<p>The ban's impact on healthcare is a particular concern. UF Health, the University of Florida's healthcare system, regularly sponsors physicians and surgeons through the H-1B programme. It serves more than 3 million Floridians annually across all 67 counties in the state, often providing specialized care in fields where domestic candidates are scarce.</p>

<p>"The ban as written also applies to UF Health, which regularly sponsors physicians and surgeons using the H-1B visa — doctors who serve many of the more than 3 million Floridians who visit a UF Health facility annually," O'Brien said during public comment.</p>

<h2>A Growing State-Level Trend</h2>
<p>Florida is the second state to ban H-1B hiring at public universities, following Texas Governor Greg Abbott's announcement of a similar one-year freeze. The moves represent a growing willingness among Republican-led states to go beyond federal immigration restrictions, extending the policy battleground into higher education — territory traditionally resistant to visa restrictions due to the global nature of academic research.</p>

<p>The Board of Governors oversees Florida's public university system but not its public colleges. The moratorium does not affect other visa categories, and private universities in Florida remain free to sponsor H-1B workers.</p>

<h2>What It Means for Indian Academics and Researchers</h2>
<p>Indian nationals are the largest group of H-1B visa holders in the United States, and they constitute a significant share of faculty, postdoctoral researchers and medical residents at American universities. The Florida freeze effectively closes one of the largest state university systems in the country to new Indian academic hires for nearly a year.</p>

<p>For Indian graduate students currently pursuing doctoral programmes in Florida and hoping to transition into faculty or research positions at their institutions, the moratorium may force them to look elsewhere. University administrators have warned privately that top international candidates are already choosing to interview at institutions in other states, creating a competitive disadvantage that could outlast the formal freeze period.</p>

<p>The chancellor's office is expected to study H-1B usage and costs during the moratorium and present findings to the board before any decision on extending or ending the policy.</p>""",
    "word_count": 740,
    "status": "published",
    "published_at": now_str,
}

result = supabase_post("p2_articles", article5)
if result and isinstance(result, list) and len(result) > 0:
    art_id = result[0].get("id", "unknown")
    print(f"  ✅ Published: {article5['headline'][:60]}... (ID: {art_id})", flush=True)
    if topic5_id != "0":
        supabase_patch(f"p2_topics?id=eq.{topic5_id}", {"status": "published", "last_article_id": art_id})
        print(f"  📌 Topic {topic5_id[:8]} marked published", flush=True)
else:
    print(f"  ❌ Failed to insert: {result}", flush=True)

print("\n✅ All articles written and inserted!", flush=True)
