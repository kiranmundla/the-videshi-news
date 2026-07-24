#!/usr/bin/env python3
"""
Technology writer batch — July 3, 2026 (~11:00 PT)
Inserts 3 fresh technology articles into Supabase with status="review".

Articles:
1. India's AI Job Paradox: AI hiring +16% vs IT decline
2. India AI Startup Funding Surges 317% in H1 2026
3. Fortune 500 GCC Boom in India — Crosses 2,100 Centers
"""

import json
import os
import uuid
from datetime import datetime, timezone

# ── Supabase credentials ──────────────────────────────────────────────
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# ── Article definitions ───────────────────────────────────────────────

now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ╔═══════════════════════════════════════════════════════════════╗
# ║  ARTICLE 1 — AI Job Paradox                                  ║
# ╚═══════════════════════════════════════════════════════════════╝

body_1 = """India's technology job market is splitting in two. On one side, artificial-intelligence roles are multiplying at a pace not seen since the post-pandemic hiring frenzy. On the other, thousands of conventional IT positions are quietly vanishing — and the gap is widening every quarter.

Fresh data from the Naukri JobSpeak report, published this week, shows that AI-specific job postings in India rose 16 percent year-on-year in June 2026, even as the broader information-technology sector recorded a 3 percent decline in overall hiring over the same period. The foundit Insights Tracker paints an even starker picture: India's white-collar hiring fell 5 percent month-on-month and 9 percent year-on-year in June.

The numbers tell a story the industry has been dreading. Traditional roles — manual testing, basic application maintenance, routine coding — are being compressed by automation and generative AI tools. Meanwhile, positions requiring machine-learning expertise, prompt engineering, data science and intelligent automation are commanding premium salaries and attracting bidding wars among employers.

## TCS Signals the Shift

Perhaps the most telling signal came from Tata Consultancy Services chairman N. Chandrasekaran, who told shareholders at the company's annual general meeting that TCS envisions a future where AI agents equal the number of human employees on its payroll. The statement landed like a thunderclap across Dalal Street.

TCS, India's largest IT services exporter by revenue, cut more than 12,000 jobs last July. Its net headcount declined by over 23,000 in the fiscal year ending March 2026 — the sharpest workforce reduction in the company's history. Yet in the same breath, TCS announced a global partnership with Anthropic, the maker of Claude, to equip 50,000 associates with AI tools and co-develop solutions for regulated industries including financial services, healthcare and aviation.

The paradox is clear: the company is shedding traditional workers while investing heavily in AI-native talent. And TCS is far from alone. Infosys struck a similar partnership with Anthropic in February. HCLTech invested $150 million in Sarvam AI, an Indian large-language-model startup. OpenAI has roped in both Infosys and HCLTech as enterprise distribution partners.

## GCCs: The New Talent Magnets

The brightest spot in this reconfigured landscape is India's booming Global Capability Centre ecosystem. Nearly two in three new GCC roles created in 2026 — 64 percent — now require AI, data-science or intelligent-automation skills, according to the foundit tracker.

India recorded 227,991 GCC hires in the first half of 2026, an 11 percent increase over the same period last year. The country now hosts roughly 2,120 active GCCs, and full-year hiring is projected to cross 510,000 — the first time annual GCC recruitment will breach the 5-lakh mark. GCC hiring has grown 3.4-fold since 2021, reflecting a 27.4 percent compound annual growth rate over five years.

This week, American medical-device maker Zimmer Biomet announced plans to hire 500 employees over three years for a new technology centre in Bengaluru focused on AI, robotics and surgical planning. German pharmaceutical giant Merck recently opened a 3,300-person GCC in Bengaluru's Electronic City. These are not call-centre expansions — they are R&D hubs competing for the same talent that Silicon Valley recruits.

## What This Means for the Diaspora

For the estimated 4.5 million Indian Americans, many of whom built careers in the IT services model that powered India's rise, this shift carries personal stakes. NRIs working at Tier-1 IT firms — or managing teams back home — face a clear imperative: upskill into AI or risk obsolescence.

The flip side is opportunity. GCCs are actively recruiting senior leaders with international experience, and the "reverse brain drain" that was once theoretical is becoming measurable. Diaspora professionals with domain expertise in healthcare, financial services or manufacturing — combined with AI fluency — are exactly the profiles these centres are hunting.

India's tech workforce is not shrinking. It is being remade. The question for NRIs is whether they will ride the wave or be caught beneath it.

*Sources: Reuters, The Hindu BusinessLine (foundit Insights Tracker), TechCrunch, TCS corporate filings*"""

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "India's AI Job Paradox: Hiring Surges 16% Even as IT Giants Slash Thousands",
    "subheadline": "AI roles are booming, GCCs are scaling fast, and TCS wants as many AI agents as employees. Traditional IT workers face a reckoning.",
    "slug": "india-ai-job-paradox-hiring-surges-it-giants-slash-20260703",
    "category": "technology",
    "vertical": "technology",
    "body": body_1,
    "diaspora_angle": "NRIs in IT services face an urgent reskilling imperative; GCC leadership roles offer reverse-brain-drain opportunities for diaspora professionals with AI + domain expertise.",
    "tags": ["AI hiring", "IT jobs", "TCS", "GCC India", "Anthropic Claude", "Naukri JobSpeak", "reskilling", "Indian IT sector"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "TechCrunch", "url": "https://techcrunch.com"},
        {"name": "TCS Corporate", "url": "https://www.tcs.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now_iso,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg/330px-Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg",
    "image_caption": "TCS Chairman N. Chandrasekaran at the India Economic Summit. He recently said AI agents may soon equal TCS's employee headcount.",
    "image_attribution": "World Economic Forum / Wikimedia Commons (CC BY-SA 2.0)"
})


# ╔═══════════════════════════════════════════════════════════════╗
# ║  ARTICLE 2 — AI Startup Funding Surges 317%                  ║
# ╚═══════════════════════════════════════════════════════════════╝

body_2 = """If 2025 was the year India's startup ecosystem rediscovered discipline, 2026 is the year it discovered a new obsession: artificial intelligence. And the funding numbers prove it.

Indian AI startups raised $676 million across 57 deals in the first half of 2026, a staggering 317 percent year-on-year jump in funding, according to a new report from Inc42. Deal volume nearly doubled, rising 90 percent over the same period. In a half-year where overall Indian startup funding actually slipped 9 percent to $5.2 billion, AI emerged as the undisputed bright spot — the sector that investors could not throw money at fast enough.

The headline deal was Sarvam AI's $234 million Series B round in June, which valued the Bengaluru-based company at $1.5 billion and made it India's newest AI unicorn. The round was led by HCLTech, which invested $150 million — a remarkable bet from an IT services firm historically focused on consulting and outsourcing. Bessemer Venture Partners, Khosla Ventures and Peak XV Partners also participated.

## Sovereign AI and the IndiaAI Mission

Sarvam's rise reflects a broader strategic shift. The company is building open-source large language models optimized for Indian languages and deploying them across banking, insurance, government services and defence. In an era of rising geopolitical tension over AI access, sovereign AI — the ability of a nation to develop and control its own AI infrastructure — has become a policy priority.

India's IndiaAI Mission, which supports compute infrastructure, indigenous model development and foundational research, has been a critical catalyst. Investors point to the government's active role in building AI compute capacity (including a 10,000-GPU cluster through partnerships with Nvidia and domestic firms) as a key confidence signal.

"First, the global AI infrastructure buildout has created real enterprise demand," said Vikram Gupta of IvyCap Ventures, in remarks captured by Inc42. "Second, investors are moving away from businesses where the moat is distribution towards companies where the moat is technology."

## Where the Smart Money Is Flowing

The AI funding surge contrasts sharply with traditional startup darlings. Fintech — long India's most-funded sector — saw investments decline 19 percent year-on-year to $1.3 billion in H1. E-commerce funding dropped 35 percent to $779 million. Even deeptech beyond AI, while growing (up 17 percent to $365 million), could not match the velocity of AI-specific deals.

Google and Accel have amplified the momentum further. Under Google's AI Futures Fund, the two firms are co-investing up to $2 million per startup in Indian AI companies through Accel's Atoms program — the first collaboration of its kind globally. Selected startups receive equity funding along with access to Google Cloud, Gemini models, DeepMind tools and hands-on mentorship. Over four years, the Atoms program has supported 40 startups that collectively raised more than $300 million in follow-on funding.

The signal is clear: global capital increasingly views India not as a cost-arbitrage destination, but as a potential AI innovation centre in its own right.

## The Diaspora Opportunity

For Indian Americans in venture capital, technology or corporate leadership, this funding explosion presents a dual opportunity. First, as investors: the AI funding gap between India and the United States means earlier-stage Indian AI companies are available at valuations far below comparable Silicon Valley firms. Sarvam's $1.5 billion valuation, for instance, is a fraction of what US AI labs command despite operating in a market of 1.4 billion potential users.

Second, as founders: Accel and Google's explicit inclusion of "Indian diaspora entrepreneurs building for global markets" in their co-investment criteria signals that the ecosystem is actively courting NRI founders who can bridge the India-US technology corridor.

The first half of 2026 was AI's breakout moment in Indian venture capital. The second half will determine whether the ecosystem can convert funding into products — and whether the diaspora will be part of that story.

*Sources: Inc42 H1 2026 Indian Startup Funding Report, TechCrunch, SiliconIndia, Google AI Futures Fund announcement*"""

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "India's AI Startup Funding Explodes 317% — Here's Where the Smart Money Is Going",
    "subheadline": "AI startups raised $676 million in the first half of 2026 while overall startup funding declined. Sarvam's unicorn round and Google-Accel co-investments mark a turning point.",
    "slug": "india-ai-startup-funding-explodes-317-percent-h1-2026-20260703",
    "category": "technology",
    "vertical": "technology",
    "body": body_2,
    "diaspora_angle": "NRI investors can access Indian AI startups at significantly lower valuations than US counterparts; Accel-Google program explicitly courts diaspora founders bridging India-US tech corridor.",
    "tags": ["AI funding", "Sarvam AI", "HCLTech", "Indian startups", "venture capital", "IndiaAI Mission", "Google Accel", "sovereign AI", "unicorn"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com"},
        {"name": "TechCrunch", "url": "https://techcrunch.com"},
        {"name": "SiliconIndia", "url": "https://www.siliconindia.com"},
        {"name": "Google AI Futures Fund", "url": "https://blog.google"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now_iso,
    "image_url": "https://images.pexels.com/photos/2599244/pexels-photo-2599244.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "India's AI startup ecosystem attracted $676 million in the first half of 2026, a 317 percent year-on-year surge driven by sovereign AI ambitions and global investor appetite.",
    "image_attribution": "Alex Knight / Pexels"
})


# ╔═══════════════════════════════════════════════════════════════╗
# ║  ARTICLE 3 — GCC Boom Crosses 2,100                          ║
# ╚═══════════════════════════════════════════════════════════════╝

body_3 = """A quiet revolution is reshaping India's technology economy — and it has nothing to do with Infosys or TCS. Across Bengaluru, Hyderabad, Pune and an expanding list of Tier-2 cities, the world's largest corporations are building something far more ambitious than back offices. They are constructing the AI brains of their global operations.

India now hosts more than 2,120 Global Capability Centres, up from roughly 1,600 five years ago. In the first half of 2026 alone, these centres hired 227,991 people — an 11 percent increase over the same period last year. Full-year hiring is projected to cross 510,000, the first time annual GCC recruitment will breach the half-million mark. Revenue from India's GCCs is expected to reach $84 billion in the current financial year, according to GCC consultant ANSR, up 12 percent year-on-year.

The numbers are impressive. The nature of the hiring is transformative.

## From Cost Centre to Capability Hub

Nearly two in three new GCC roles — 64 percent — now require AI, data science or intelligent automation skills, according to the foundit Insights Tracker. Technology and software firms, together with banking and financial services companies, account for 56 percent of all GCC hiring, but the fastest growth is coming from unexpected sectors: healthcare, manufacturing and life sciences.

This week, American medical-device maker Zimmer Biomet announced it would hire 500 employees over the next three years for a newly opened technology centre in Bengaluru. The centre will focus on AI, robotics, surgical planning and R&D — work that directly feeds into the company's global product pipeline for knee, hip and shoulder replacements.

"We want to make sure that we have a centre that has all the appropriate functions running together so we can drive innovation and bring that back to our surgeons, care teams and patients," said Shaun Braun, Zimmer Biomet's Chief Information and Technology Officer.

Days earlier, German pharmaceutical giant Merck opened a 3,300-person GCC in Bengaluru's Electronic City, spanning healthcare, life sciences and electronics divisions with teams dedicated to AI, data analytics, cloud engineering, cybersecurity and digital transformation.

These are not isolated moves. Novo Nordisk, AstraZeneca and Eli Lilly already operate major India centres for clinical data analysis and drug-development research. The trend is clear: GCCs have evolved from cost-arbitrage outposts into genuine innovation engines.

## Bengaluru Leads, But Tier-2 Cities Are Rising

Bengaluru remains India's GCC capital, hosting over 2,000 centres in the broader metro area. Electronic City, in particular, has emerged as a preferred corridor — office rents there run 20 to 40 percent below prime Outer Ring Road and Whitefield locations, while the Yellow Line Metro and Elevated Expressway have dramatically improved connectivity.

But the GCC story is no longer a Bengaluru-only story. Hyderabad is rapidly emerging as a southern workspace hub, with managed-workspace provider Incuspaze recently designating the city as its strategic hub for South India as part of a ₹150-crore expansion. Pune is attracting GCCs that prioritize the city's manufacturing, BFSI and engineering talent pools. Chennai and Ahmedabad are also gaining traction.

"Companies are no longer setting up Global Capability Centres simply to reduce costs," said Tarun Sinha, CEO of foundit. "They are building them to develop the AI, engineering and product capabilities that run their global businesses. India offers the depth of talent to do this at scale, and the growing pull of Tier-2 cities shows how far that capability now extends beyond the traditional metros."

## What This Means for the Diaspora

For NRIs considering a return to India — or evaluating career moves within multinational employers — the GCC boom is reshaping the calculus. Senior leadership roles at India GCCs increasingly carry global mandates, not regional ones. A VP of Engineering at a healthcare GCC in Bengaluru may own the same product roadmap as a counterpart in Boston, at a fraction of the cost of living.

The implication extends to NRI investors and entrepreneurs as well. The commercial real-estate ecosystem supporting GCCs — Grade A office space, co-working providers, residential developments in tech corridors — represents a tangible investment opportunity tied directly to India's AI-driven economic transformation.

Half a million hires. Two thousand centres. Eighty-four billion dollars. India's GCC ecosystem has moved far beyond the back office — and the world's biggest companies are betting their AI futures on it.

*Sources: Reuters, The Hindu BusinessLine (foundit Insights Tracker), TradeBrains, ANSR, Incuspaze corporate announcements*"""

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Why Every Fortune 500 Wants an AI Hub in India: GCCs Cross 2,100 and Half a Million Hires",
    "subheadline": "Global Capability Centres are no longer back offices. With $84 billion in revenue and two-thirds of new roles requiring AI skills, India's GCCs are becoming the innovation engines of the world's biggest companies.",
    "slug": "fortune-500-ai-hub-india-gcc-cross-2100-half-million-hires-20260703",
    "category": "technology",
    "vertical": "technology",
    "body": body_3,
    "diaspora_angle": "NRI professionals can access global-mandate leadership roles at India GCCs; real-estate ecosystem around tech corridors offers investment opportunity tied to India's AI-driven economic transformation.",
    "tags": ["GCC India", "Global Capability Centres", "Bengaluru", "Zimmer Biomet", "Merck", "AI hiring", "Tier 2 cities", "reverse brain drain", "NRI careers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "TradeBrains", "url": "https://tradebrains.in"},
        {"name": "ANSR", "url": "https://ansr.com"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now_iso,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/ITPL-Whitefield-Bangalore1.jpg/1280px-ITPL-Whitefield-Bangalore1.jpg",
    "image_caption": "International Technology Park in Whitefield, Bengaluru — one of India's premier tech corridors housing major IT firms and Global Capability Centres.",
    "image_attribution": "PageImp / Wikimedia Commons (CC BY-SA 4.0)"
})


# ── Insert into Supabase ──────────────────────────────────────────────
import subprocess

print(f"\n{'='*60}")
print(f"  Technology Writer — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  Inserting {len(articles)} articles into Supabase")
print(f"{'='*60}\n")

success = 0
for i, art in enumerate(articles, 1):
    payload = json.dumps(art)
    result = subprocess.run(
        [
            "curl", "-sS", "-X", "POST",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload
        ],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"  [{i}] ✗ CURL ERROR: {result.stderr}")
        continue

    resp = result.stdout
    try:
        data = json.loads(resp)
        if isinstance(data, list) and len(data) > 0:
            print(f"  [{i}] ✓ {art['headline'][:70]}...")
            print(f"      slug: {art['slug']}")
            print(f"      id:   {art['id']}")
            success += 1
        elif isinstance(data, dict) and "message" in data:
            print(f"  [{i}] ✗ API ERROR: {data['message']}")
            if "details" in data:
                print(f"      Details: {data['details']}")
        else:
            print(f"  [{i}] ? Unexpected response: {resp[:200]}")
    except json.JSONDecodeError:
        print(f"  [{i}] ✗ Non-JSON response: {resp[:200]}")

print(f"\n{'='*60}")
print(f"  DONE — {success}/{len(articles)} articles inserted (status=review)")
print(f"{'='*60}\n")
