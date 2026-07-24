#!/usr/bin/env python3
"""
Videshi Technology Writer — 2026-06-15 06:00 UTC
Generates 2 fresh technology articles for The Videshi.
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Sriram Krishnan Leaves White House AI Role
# ─────────────────────────────────────────────────────────────

article1_body = """Sriram Krishnan, the Chennai-born technology executive who spent the last eighteen months as the White House's senior policy adviser on artificial intelligence, will step down at the end of June. He plans to start an AI company.

The announcement, made via a post on X, marks the departure of the most senior Indian-American official shaping America's AI policy at a moment when the technology has become a frontline issue in national security, trade, and immigration.

## From Chennai to the West Wing

Krishnan's path to the White House ran through nearly every major platform in Silicon Valley. He started at Microsoft, where he worked on Windows Azure in its early days. He then held product leadership roles at Facebook, Twitter, Yahoo, and Snap before becoming a general partner at Andreessen Horowitz, the venture capital firm whose founders threw their weight behind Donald Trump's 2024 presidential campaign.

When the second Trump administration took office, Krishnan joined as AI policy adviser alongside David Sacks, the investor who served as the administration's AI and crypto czar before moving to co-chair the President's Council of Advisors on Science and Technology.

## What He Built

Krishnan's eighteen months in government were not decorative. He was instrumental in architecting the American AI Action Plan, which prioritised data centre construction over regulation and became the backbone of the administration's approach to the technology. He helped craft the National AI Policy Framework executive order and worked on what the White House called "AI acceleration partnerships" — a set of agreements designed to keep the American AI ecosystem ahead of China's.

Perhaps most consequentially, he was part of the team that brokered arrangements with Google, Microsoft, and xAI to give the federal government early access to their AI models for security assessments before public release. That framework was formalised in a June executive order requiring frontier model providers to voluntarily submit their most powerful systems for government cybersecurity testing.

He also represented American AI interests at diplomatic summits in France, India, the UK, and the Middle East.

## The Timing Matters

Krishnan's exit comes at a volatile moment for AI policy. Just days before his announcement, the US Commerce Department issued an export control directive forcing Anthropic to suspend global access to its Fable 5 and Mythos 5 models for all foreign nationals — a move that sent shockwaves through India's IT industry, where TCS had just signed a deal to equip 50,000 employees with Anthropic's tools.

The Anthropic episode demonstrated that frontier AI models are now being treated as dual-use technology, subject to the same export control logic previously reserved for advanced semiconductors. The AI policy architecture Krishnan helped build is the framework through which those decisions are made.

His departure also coincides with Trump's expressed interest in the US government acquiring equity stakes in AI companies — a proposal that could reshape the relationship between Washington and Silicon Valley.

## What Comes Next

According to AI Market Watch, Krishnan plans to launch an AI company after a brief break. The specific focus has not been disclosed, but his post hinted at "tackling some of the large challenges facing America on AI" related to energy, data centres, and delivering benefits to ordinary Americans through "institution-building efforts."

David Sacks confirmed that the administration plans to continue working with Krishnan as an outside adviser even after his formal departure.

## Why This Matters for the Diaspora

Krishnan's trajectory — from IIT-adjacent roots in Chennai to writing the rules that govern how America deploys its most powerful technology — is a particular kind of Indian-American story. It is one where technical credibility earned in the private sector converts into policy influence at the highest level.

His departure leaves a gap at the AI policy table. With the Anthropic export controls demonstrating that AI access is now a geopolitical weapon, the question of who advocates for maintaining open access — particularly for allies like India — becomes more urgent. Krishnan was one of the few people in the room who understood both the technology and the diplomatic stakes from a perspective shaped by the Indian technology ecosystem.

For the roughly 300,000 Indian-origin professionals working in AI-adjacent roles across American tech companies, Krishnan's move from policy back to building also signals something about where the real leverage lies. The man who wrote the playbook apparently concluded that the next act requires building, not advising."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sriram Krishnan Wrote America's AI Playbook. Now He's Leaving the White House to Build His Own.",
    "subheadline": "The Chennai-born policy adviser shaped the AI Action Plan, brokered government access to frontier models, and navigated the Anthropic crisis. His next move is a startup.",
    "slug": make_slug("sriram-krishnan-white-house-ai-adviser-exit-startup"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "The most senior Indian-American in US AI policy is leaving at a moment when AI export controls directly threaten Indian IT firms and the 300,000 Indian-origin professionals in American tech.",
    "tags": ["ai-policy", "indian-american", "white-house", "sriram-krishnan", "silicon-valley"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/white-house-ai-policy-adviser-krishnan-leave-position-2026-06-07/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/07/sriram-krishnan-is-leaving-his-role-as-white-house-ai-advisor/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/who-is-sriram-krishnan-the-white-house-ai-adviser-set-to-step-down-in-june"},
        {"name": "AI Market Watch", "url": "https://www.ai-market-watch.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/MS200024.jpg",
    "image_caption": "Sriram Krishnan, former White House senior policy adviser on artificial intelligence",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: India's 16-EV Launch Wave
# ─────────────────────────────────────────────────────────────

article2_body = """Starting this week, India's automobile market is entering its most aggressive electrification push yet. Over the next nine months, automakers will introduce roughly sixteen electrified vehicles against just seven new internal combustion engine models — a ratio that would have been unthinkable two years ago.

The wave begins on 15 June with Mercedes-Benz India's S450e plug-in hybrid, continues with Toyota's Urban Cruiser Ebella EV and Tata Motors' Sierra EV on 30 June, and will roll through the rest of 2026 with entries from BYD, MG Motor, Honda, Hyundai, Kia, BMW, Mahindra, and Maruti Suzuki.

## Not a Niche Anymore

What makes this cycle different from previous EV pushes is its breadth. Electrification is no longer limited to the sub-₹15 lakh city car segment or the ₹2-crore luxury end. The upcoming launches span entry-level hatchbacks, family SUVs, premium crossovers, and plug-in hybrids — covering virtually every price point where Indian buyers actually spend money.

Tata Motors, which has sold over 37,000 units of the Sierra since deliveries began, is betting that the electric variant will extend that momentum. The Sierra EV, built on Tata's acti.ev+ platform, will offer both rear-wheel-drive and all-wheel-drive configurations, the latter powered by a dual-motor setup producing 396 PS. The larger 75 kWh battery pack promises a range exceeding 500 km, with DC fast charging and vehicle-to-load capability — features that let the car double as a mobile power source.

Tata is not stopping there. The Safari EV is expected during the Diwali season, giving the company eight electric models in its portfolio by year's end.

## The Plug-In Hybrid Arrives

This cycle also marks the arrival of plug-in hybrids as a serious segment in India. Four PHEVs are scheduled: the Mercedes S450e (429 HP system power, 109 km electric range), a rebadged Chery Jetour Traveller from JSW Motors, MG Motor's next PHEV, and a Kia entry. The S450e, with its 21.96 kWh battery and 60 kW DC fast charging, represents the kind of technology that lets buyers go electric for daily commutes while keeping petrol range for highway trips.

For a market where charging infrastructure remains patchy outside major metros, plug-in hybrids may be the pragmatic bridge that pure EVs alone cannot provide.

## What's Driving the Shift

Three forces are converging. First, tightening Corporate Average Fuel Economy (CAFE) norms are penalising manufacturers who rely too heavily on internal combustion. Second, battery costs have fallen sharply — Tata's acti.ev+ platform and Mahindra's INGLO architecture are both designed to bring EV price points within reach of the mass market. Third, consumer behaviour is shifting. EV penetration in India's passenger vehicle market has climbed from under 2% in 2023 to roughly 5% in the first quarter of 2026, with the trajectory steepening.

International players are watching closely. BYD, the Chinese EV giant that has upended markets from Europe to Southeast Asia, is expanding its India lineup. Maruti Suzuki, which has never sold an electric car, is preparing its first EV — a signal that even the most conservative manufacturer in India's car market considers electrification inevitable.

## The NRI Calculation

For Indian Americans tracking this from across the Pacific, the numbers are interesting on multiple levels.

Tata Motors' stock has been one of the better-performing Indian auto names this year, buoyed by the company's EV lead and the strong reception of the Sierra. Mahindra's electric SUV pipeline, anchored by the XEV 9e and BE 6, has attracted attention from institutional investors betting on India's green transition.

But the investment case goes beyond individual stocks. India's EV ecosystem — spanning battery manufacturing, charging infrastructure, and the software layer that ties it all together — is attracting the kind of capital formation that creates jobs and supply chain opportunities. The ₹31,299 crore flowing into India's semiconductor mission by FY27 is partly driven by the same logic: electrified vehicles need chips, and India wants to make them domestically.

For NRIs who visit India regularly, the shift will be visible in practical terms. Charging stations are appearing at highway rest stops and apartment complexes. Ride-hailing fleets in Bangalore, Delhi, and Mumbai are adding EVs. The experience of driving in India is, slowly but measurably, changing.

The sixteen launches arriving over the next nine months will not electrify the entire market overnight. But they represent the moment when the question shifted from "if" to "how fast" — and for every new petrol car entering the showroom, two electric ones are pulling up behind it."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Is Launching 16 Electric Vehicles in Nine Months. For Every New Petrol Car, Two EVs Are Pulling Up.",
    "subheadline": "Starting this week, Mercedes, Tata, Toyota, BYD, Mahindra, and Maruti are flooding India's market with EVs and plug-in hybrids. The ratio to new ICE models is 2:1.",
    "slug": make_slug("india-16-ev-launches-nine-months-tata-sierra-mercedes"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRI investors tracking Tata Motors and Mahindra stand to benefit from India's EV leadership, while the charging infrastructure buildout changes the experience of visiting India.",
    "tags": ["electric-vehicles", "india-ev", "tata-motors", "mahindra", "maruti-suzuki", "green-tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/indias-ev-expansion-kick-off-june-15-with-16-rollouts-vs-7-ice-models/article69691234.ece"},
        {"name": "Rushlane", "url": "https://www.rushlane.com/tata-sierra-ev-debut-june-30-awd-range-12548923.html"},
        {"name": "Gaadiwaadi", "url": "https://gaadiwaadi.com/tata-to-launch-2-new-electric-suvs-with-awd-powertrain-in-next-5-months/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/12199799/pexels-photo-12199799.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "An electric vehicle charging station in India with a user checking the app on their smartphone",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}

# ─────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
