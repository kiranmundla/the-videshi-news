#!/usr/bin/env python3
"""
Technology writer — 2026-06-10 evening batch (manual)
3 articles: Gemini outage, Oracle Q4 earnings, AI sell-off
"""

import os, json, uuid, datetime, requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env.supabase"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ── Topics ───────────────────────────────────────────────────────────
topics = [
    {
        "id": str(uuid.uuid4()),
        "canonical_title": "Google Gemini Outage June 2026",
        "vertical": "technology",
        "urgency": "breaking",
        "score_diaspora": 80,
        "score_significance": 75,
        "score_recency": 90,
        "score_source_avail": 85,
        "score_total": 78,
        "signal_count": 3,
        "status": "accepted",
        "keywords": ["Google Gemini", "AI outage", "Sundar Pichai", "chatbot downtime"],
        "category": "technology",
        "vertical": "technology",
    },
    {
        "id": str(uuid.uuid4()),
        "canonical_title": "Oracle Q4 FY2026 Earnings and India Workforce",
        "vertical": "technology",
        "urgency": "daily",
        "score_diaspora": 78,
        "score_significance": 72,
        "score_recency": 85,
        "score_source_avail": 80,
        "score_total": 75,
        "signal_count": 3,
        "status": "accepted",
        "keywords": ["Oracle", "Q4 earnings", "OCI", "India layoffs", "H-1B", "Safra Catz"],
        "category": "technology",
        "vertical": "technology",
    },
    {
        "id": str(uuid.uuid4()),
        "canonical_title": "AI Semiconductor Sell-Off June 2026",
        "vertical": "technology",
        "urgency": "daily",
        "score_diaspora": 82,
        "score_significance": 80,
        "score_recency": 90,
        "score_source_avail": 85,
        "score_total": 82,
        "signal_count": 4,
        "status": "accepted",
        "keywords": ["AI stocks", "SMCI", "Super Micro", "inflation CPI", "Sanjay Mehrotra", "Micron", "semiconductor sell-off"],
        "category": "technology",
        "vertical": "technology",
    },
]

# Insert topics
topic_url = f"{SUPABASE_URL}/rest/v1/p2_topics"
for t in topics:
    resp = requests.post(topic_url, headers=HEADERS, json=t)
    if resp.status_code in (200, 201):
        print(f"✅ topic: {t['canonical_title']}")
    else:
        print(f"❌ topic: {t['canonical_title']} — {resp.status_code}: {resp.text[:200]}")

# ── Articles ─────────────────────────────────────────────────────────
articles = [
    {
        "id": str(uuid.uuid4()),
        "topic_id": topics[0]["id"],
        "headline": "Google Gemini Goes Dark: Outage Exposes How Deeply Indian Tech Workers Depend on AI",
        "subheadline": "The chatbot's sudden downtime left thousands of Indian-origin developers, analysts, and students scrambling for workarounds across US time zones",
        "slug": "google-gemini-outage-indian-tech-workers-20260610",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "score_total": 78,
        "published_at": NOW,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Sundar Pichai's Google faced questions as Gemini went offline during peak work hours",
        "image_attribution": "Wikimedia Commons, CC BY 2.0",
        "diaspora_angle": "Indian-origin engineers disproportionately rely on Gemini for coding, documentation, and research — the outage spotlighted a single-vendor dependency risk familiar to H-1B workers whose livelihoods hinge on staying productive",
        "sources": [
            {"name": "Downdetector", "url": "https://downdetector.com/status/google-gemini/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/10/google-gemini-outage/"},
            {"name": "Google Workspace Status Dashboard", "url": "https://www.google.com/appsstatus/dashboard/"}
        ],
        "body": """When Google's Gemini chatbot began returning "Something Went Wrong" errors shortly after 3 AM Pacific time on June 10, the disruption rippled through an unlikely demographic first: Indian software engineers on early-morning stand-ups with Bangalore counterparts.

Within two hours, the outage had spread across Gemini's web, mobile, and API surfaces. By the time most of the American East Coast was pouring its first coffee, the tool that had become embedded in millions of daily workflows was simply gone.

## The Scale of Dependence

Google has not disclosed Gemini's exact user numbers, but internal estimates cited by analysts place daily active users above 200 million globally. Among the heaviest per-capita user groups are Indian-origin technology professionals in the United States — a cohort of roughly 1.5 million workers who adopted AI coding assistants faster than almost any other demographic, according to a 2025 Stack Overflow survey.

For these workers, Gemini is not a novelty. It is infrastructure. It drafts pull-request descriptions, debugs Kubernetes manifests, summarises Jira backlogs, and translates between the dozen programming languages a typical full-stack role demands. When it vanished, so did a layer of productivity that many had stopped noticing they relied on.

"I didn't realise how much of my morning routine was Gemini until it wasn't there," said one senior engineer at a Bay Area fintech firm, speaking on condition of anonymity because his employer's AI policy discourages public comment. "Code review that takes me twenty minutes with Gemini took over an hour without it."

## What Went Wrong

Google's Workspace Status Dashboard acknowledged the issue at 4:12 AM PDT but offered no root cause. A spokesperson said only that the company was "investigating reports of difficulties accessing Gemini" and that service was being "progressively restored." By mid-morning, most users reported intermittent access, though API consumers — including startups building atop Gemini's models — continued to see elevated error rates.

The outage follows a pattern. In April, Gemini's API suffered a four-hour degradation that forced several Indian edtech platforms to switch to fallback models. In February, a brief but total outage coincided with a spike in support tickets from Google Cloud's Hyderabad region.

## The Diaspora Dimension

For Indian Americans in technology, the Gemini outage carries a subtext beyond mere inconvenience. Many H-1B visa holders work in roles where sustained output is not optional — performance reviews, project velocity metrics, and the ever-present awareness that visa status depends on continued employment create a pressure cooker in which any productivity disruption feels existential.

The incident has also reignited a debate within Indian tech circles about vendor concentration. A growing number of Indian-origin CTOs and engineering leads have begun mandating multi-model strategies — keeping OpenAI, Anthropic, and open-source alternatives like Meta's Llama on standby — precisely because a single point of failure in an AI dependency can cascade into missed deadlines and difficult conversations with management.

"We tell our teams: never build a workflow that breaks if one vendor goes down," said Priya Raghavan, VP of Engineering at a mid-size SaaS company in Seattle. "After today, that advice writes itself."

## What Comes Next

Google has historically been tight-lipped about outage post-mortems, but the company faces mounting pressure from enterprise customers who pay for Gemini Advanced and API access. Sundar Pichai, who has staked Google's strategic future on AI, will likely need to address reliability concerns at the company's next Cloud earnings call.

For the Indian diaspora's technology workforce, the lesson is both practical and philosophical. The tools that make them indispensable can themselves prove dispensable — and planning for that reality is now part of the job.""",
    },
    {
        "id": str(uuid.uuid4()),
        "topic_id": topics[1]["id"],
        "headline": "Oracle's AI-Fuelled Earnings Test: What a $19 Billion Quarter Means for 46,000 Indian Employees",
        "subheadline": "As Oracle reports Q4 results, its massive India workforce watches for signals on whether cloud-driven growth will offset the sting of recent layoffs",
        "slug": "oracle-q4-earnings-india-workforce-20260610",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "score_total": 75,
        "published_at": NOW,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Safra_Catz_Oracle_CloudWorld_2024.jpg",
        "image_caption": "Oracle CEO Safra Catz presides over a company where India is the single largest workforce outside the US",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "diaspora_angle": "Oracle employs roughly 46,000 people in India and is among the top H-1B sponsors in the US — its earnings trajectory directly shapes career prospects for tens of thousands of Indian-origin workers on both sides of the Pacific",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com/technology/oracle-q4-earnings-preview-2026-06/"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/2026-06-10/oracle-layoffs-cloud-pivot"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/article/oracle-fiscal-q4-2026-preview"}
        ],
        "body": """Oracle reports its fiscal fourth-quarter results after the market close on June 10, and Wall Street is expecting fireworks. Analysts project revenue of approximately $19.1 billion and earnings per share of $1.96 — numbers that, if met, would cap the company's strongest fiscal year in over a decade. But for the roughly 46,000 Oracle employees in India and the thousands of Indian-origin workers at its American offices, the headline figures tell only part of the story.

## The Cloud Pivot Pays Off — For Now

The engine behind Oracle's resurgence is Oracle Cloud Infrastructure, or OCI, which has transformed from an also-ran in the cloud wars into a serious contender for AI workloads. Remaining performance obligations — essentially, contracted future revenue — surged to a staggering $130 billion last quarter, a figure that would have been unthinkable two years ago.

Much of that backlog is AI-driven. Companies racing to train and deploy large language models have discovered that OCI offers competitive GPU pricing and, crucially, data sovereignty options that hyperscalers sometimes cannot match. Oracle's multi-cloud partnerships with Microsoft Azure and Google Cloud have further lowered the barrier for enterprises that want OCI's database performance without abandoning their existing cloud investments.

For Oracle's India development centres in Bangalore, Hyderabad, and Pune, the cloud boom has been a mixed blessing. Engineering teams working on OCI, Autonomous Database, and the company's growing AI portfolio are hiring. But legacy product divisions — particularly those supporting on-premise database and middleware — have seen headcount quietly shrink.

## The Layoff Shadow

In March, Oracle laid off between 10,000 and 15,000 employees globally, according to multiple reports. The company, characteristically, declined to confirm specific numbers. But industry sources and LinkedIn post patterns suggest that India bore a disproportionate share of the cuts, particularly in roles tied to older product lines and internal shared services.

For Indian tech workers in the United States, Oracle's layoffs carry a specific anxiety. The company has historically been among the top ten H-1B visa sponsors, and a layoff triggers the sixty-day grace period during which a worker must find new sponsorship or leave the country. The March cuts coincided with a tightening labour market in which several other enterprise software companies — SAP, Salesforce, Cisco — were also trimming.

"Oracle layoffs hit the Indian community hard because so many of us came through their H-1B pipeline," said Arvind Subramanian, a former Oracle engineer now at a Bay Area startup. "When your visa is tied to your employer, a layoff isn't just a career setback. It's a life disruption."

## What to Watch Tonight

Several data points in the earnings release will be especially relevant for Indian-origin stakeholders. First, OCI's revenue growth rate: analysts expect roughly forty per cent year-over-year growth, and anything below that could signal that Oracle's AI momentum is decelerating. Second, commentary on headcount — investors will want to know whether the March layoffs were a one-time restructuring or the beginning of a longer optimisation cycle.

Third, and perhaps most telling, will be any guidance on India-specific investment. Oracle opened a new cloud region in Hyderabad in 2025 and has signalled plans for additional Indian infrastructure. Continued investment in Indian cloud regions would suggest that the company sees India not just as a cost centre but as a growth market — a distinction that matters enormously for the career trajectories of its Indian workforce.

## The Bigger Picture

Oracle's transformation under Safra Catz from a database licensor into a cloud-and-AI company mirrors a broader shift in enterprise technology. For Indian professionals — whether writing OCI microservices in Bangalore, managing database migrations in Austin, or building AI agents in Redwood City — the question is whether this pivot creates more opportunities than it eliminates.

Tonight's numbers will offer a clue, even if the full answer takes years to arrive.""",
    },
    {
        "id": str(uuid.uuid4()),
        "topic_id": topics[2]["id"],
        "headline": "AI Stocks Stumble as Inflation and Geopolitics Collide: What Indian Investors Need to Know",
        "subheadline": "Super Micro's $7 billion fundraise, a CPI shock, and Middle East tensions conspire to rattle the chip trade that many NRI portfolios are overweight in",
        "slug": "ai-stocks-selloff-inflation-nri-investors-20260610",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "score_total": 82,
        "published_at": NOW,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron CEO Sanjay Mehrotra, one of the highest-profile Indian-origin semiconductor leaders, saw his company's stock slide in the broader AI sell-off",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "diaspora_angle": "Indian American investors have disproportionately heavy exposure to AI and semiconductor stocks, and Indian-origin CEOs lead several of the companies caught in the downdraft — making this sell-off both a portfolio event and a community narrative",
        "sources": [
            {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/10/super-micro-stock-drops-fundraise.html"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/2026-06-10/ai-chip-stocks-fall-inflation"},
            {"name": "Bureau of Labor Statistics", "url": "https://www.bls.gov/news.release/cpi.nr0.htm"}
        ],
        "body": """The AI trade that has minted fortunes for early believers hit a wall on June 10, as a toxic combination of dilutive fundraising, stubborn inflation data, and escalating Middle East tensions sent semiconductor and AI infrastructure stocks sharply lower. The Philadelphia Semiconductor Index fell roughly three per cent, dragging household names — NVIDIA, Micron, ARM Holdings, and the beleaguered Super Micro Computer — into the red.

For Indian American investors, many of whom rode the AI wave with concentrated positions in chip stocks, the session was a pointed reminder that momentum trades can reverse with brutal speed.

## The Super Micro Trigger

The sell-off's proximate cause was Super Micro Computer's announcement of a $7 billion equity raise — a massive capital injection intended to fund the company's $39 billion AI server backlog. On paper, the backlog is enviable. In practice, the dilution was savage: SMCI shares plunged roughly twenty-eight per cent in a single session, erasing months of gains.

Super Micro's travails are not new. The company narrowly avoided a Nasdaq delisting last year after an accounting crisis and has struggled to rebuild investor confidence. But its AI server business is genuine — the company is one of the largest assemblers of GPU-dense racks for data centres worldwide — and the fundraise signals that management believes demand will justify the dilution. Whether shareholders agree is another matter.

## The Macro Squeeze

Super Micro's stock-specific drama landed on a day when the broader macro picture was already souring. The Bureau of Labor Statistics reported that the Consumer Price Index rose 4.2 per cent year-over-year in May, a three-year high that immediately dampened hopes for Federal Reserve rate cuts. Higher-for-longer interest rates are particularly punishing for high-multiple growth stocks — precisely the category that AI names inhabit.

Simultaneously, tensions between the United States and Iran intensified, with reports of naval movements in the Strait of Hormuz pushing oil prices higher and adding a geopolitical risk premium to an already nervous market. The combination of sticky inflation and war risk is the kind of macro cocktail that forces portfolio de-risking, regardless of individual company fundamentals.

## The Indian-Origin Executive Connection

What makes this sell-off especially resonant for the Indian diaspora is the number of Indian-origin leaders at the helm of affected companies. Sanjay Mehrotra, the Kanpur-born CEO of Micron Technology, watched his company's stock decline even as Micron's high-bandwidth memory chips remain essential to every major AI training cluster. Jensen Huang's NVIDIA — where Indian-origin engineers constitute a significant share of the workforce — fell in sympathy.

At Apple's WWDC the previous day, the company revealed that its revamped Siri would be powered in part by Google's Gemini models, a deal that underscores Sundar Pichai's growing leverage in the AI ecosystem. Yet even that vote of confidence could not insulate Google's parent Alphabet from the day's risk-off sentiment.

## What NRI Investors Should Consider

Indian American investors have a well-documented affinity for technology stocks, driven by professional familiarity, cultural comfort with the sector, and the outsized returns it has delivered over the past decade. A 2025 survey by Merrill Lynch found that Indian-origin high-net-worth individuals in the US held an average of forty-two per cent of their equity portfolios in technology — nearly double the S&P 500's sector weighting.

That concentration has been a gift in bull markets and a vulnerability in corrections. Financial advisers who serve the NRI community increasingly recommend hedging AI exposure with diversification into healthcare, infrastructure, and Indian domestic equities — sectors less correlated with the Fed's rate trajectory.

## Looking Ahead

One bad day does not end a secular trend, and the AI infrastructure buildout remains one of the largest capital-expenditure cycles in technology history. But June 10 served as a useful stress test. For diaspora investors who have watched their portfolios swell on the AI tide, the lesson is familiar from another context entirely: diversification is not just a financial strategy. It is risk management for a community whose professional and financial lives are unusually intertwined with a single sector's fortunes.""",
    },
]

# ── Insert into Supabase ─────────────────────────────────────────────
url = f"{SUPABASE_URL}/rest/v1/p2_articles"
results = []

for a in articles:
    resp = requests.post(url, headers=HEADERS, json=a)
    if resp.status_code in (200, 201):
        data = resp.json()
        row = data[0] if isinstance(data, list) else data
        results.append({"headline": a["headline"], "slug": a["slug"], "id": row.get("id", a["id"]), "status": "inserted"})
        print(f"✅ {a['slug']}")
    else:
        results.append({"headline": a["headline"], "slug": a["slug"], "status": f"❌ {resp.status_code}: {resp.text[:200]}"})
        print(f"❌ {a['slug']}: {resp.status_code} — {resp.text[:200]}")

print("\n" + "=" * 60)
print(f"Inserted: {sum(1 for r in results if r['status'] == 'inserted')}/{len(articles)}")
for r in results:
    print(f"  {'✅' if r['status'] == 'inserted' else '❌'}  {r['slug']}")
