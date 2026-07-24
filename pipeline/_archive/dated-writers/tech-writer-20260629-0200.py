#!/usr/bin/env python3
"""
Videshi Technology Writer — 2026-06-29 02:00 PDT
Articles:
  1. Persistent Systems bids $1.1B for Germany's Nagarro — largest Indian IT cross-border deal
  2. India drops satcom local sourcing rule — Starlink, OneWeb clear for commercial launch
  3. The US AI export ban created a vacuum. Japan and China just filled it.
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ─────────────────────────────────────────────────────────────
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

# ═════════════════════════════════════════════════════════════════════════
# ARTICLE 1 — Persistent Systems / Nagarro acquisition
# ═════════════════════════════════════════════════════════════════════════

art1_body = """Persistent Systems, the Pune-headquartered IT services firm, has made its most ambitious move yet: a €1 billion ($1.14 billion) offer to acquire Nagarro, a German digital engineering company. If completed, the deal would rank among the largest cross-border acquisitions ever mounted by an Indian IT firm and create a combined entity with roughly $2.9 billion in annual revenue.

The market was not impressed. Persistent shares tumbled 8.1 per cent on Monday morning in Mumbai, touching their lowest level since March 2026 — the steepest single-day fall in more than a year. Investors flagged the 100 per cent premium baked into the 81-euro-per-share offer, Nagarro's comparatively slender margins, and the execution risk that comes with stitching together two mid-sized firms across continents.

## The strategic logic

On paper, the combination makes sense. Persistent, which built its reputation on product engineering for Silicon Valley software companies, gets an immediate expansion into industrials, automotive and European enterprise clients — verticals that have proven stubbornly hard for Indian firms to crack organically. Nagarro, with roughly 19,000 employees across 37 countries, would give Persistent a ready-made delivery footprint in Germany, the Nordics and the Middle East.

The deal also accelerates Persistent's shift toward what management calls "AI-led engineering." Nagarro has invested heavily in autonomous driving software, industrial IoT and generative-AI consulting for European manufacturers — capabilities that complement Persistent's existing work with US hyperscalers and SaaS vendors. Together, the firms would hold a portfolio spanning the full AI stack, from model training infrastructure to shop-floor deployment.

Nagarro's board said over the weekend that it intends to recommend the offer to shareholders.

## Why NRIs should care

For Indian tech professionals in the US and Europe, the deal crystallises a broader shift in how Indian IT is trying to grow. The old playbook — hire thousands of engineers, bid on cost arbitrage, expand headcount — is running into AI-driven compression. Accenture's guidance cut last week rattled TCS, Infosys and Wipro precisely because it exposed how quickly generative AI is shrinking delivery timelines and team sizes.

Persistent's bet is that acquiring capability is faster than building it. If the integration works, it signals a new chapter for Indian IT: growth through bold M&A rather than linear headcount addition. If it does not, a $1.1 billion write-down will serve as a cautionary tale for every mid-cap IT firm eyeing a similar leap.

UBS analysts flagged the "excessive valuations" given Nagarro's relatively low growth profile. BofA maintained an "underperform" rating, calling the integration a key risk to monitor. For NRI investors holding Persistent — or Indian IT stocks generally — the next two quarters will reveal whether this was vision or hubris."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Persistent Systems Just Bet $1.1 Billion That Indian IT Can Buy Its Way Into Europe",
    "subheadline": "The Pune-based firm's offer for Germany's Nagarro is among the largest cross-border deals in Indian tech history. Investors have questions.",
    "slug": make_slug("persistent-systems-nagarro-acquisition-billion-indian-it"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "The deal signals a new M&A-driven growth model for Indian IT, directly relevant to NRI investors and tech professionals watching the sector's AI-era transformation.",
    "tags": ["indian-it", "mergers-acquisitions", "persistent-systems", "nagarro", "ai-engineering", "europe"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "UBS Research Note", "url": "https://www.ubs.com/"},
        {"name": "Bank of America Research", "url": "https://www.bankofamerica.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7989239/pexels-photo-7989239.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A business deal being sealed over laptops and documents in a corporate office",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}

# ═════════════════════════════════════════════════════════════════════════
# ARTICLE 2 — India drops satcom local sourcing rule
# ═════════════════════════════════════════════════════════════════════════

art2_body = """For years, the biggest question surrounding India's satellite broadband market was not whether Starlink, OneWeb and Amazon would enter. It was under what conditions they would be allowed to operate. This week, New Delhi answered — and the conditions just got considerably easier.

The Centre has notified the Telecommunications (Authorisation for Provision of Principal Telecommunication Services) Rules, 2026, completing India's transition from a decades-old licensing regime to a modern authorisation framework. Buried in the fine print: the final rules omit a draft proposal that would have required satellite operators to source at least 20 per cent of their ground-segment equipment from Indian manufacturers within five years of launching commercial services.

The removal clears one of the last significant regulatory hurdles for Elon Musk's Starlink, Bharti-backed Eutelsat OneWeb and Amazon's Project Kuiper, all of which have been circling the Indian market for years.

## Why the rule was dropped

The math was simple. India does not yet manufacture the specialised user terminals, LEO gateways and phased-array antennas that satellite broadband requires at commercial scale. Enforcing a 20 per cent local sourcing mandate would have either delayed satellite internet rollout by years or forced operators into hollow compliance — packaging unrelated infrastructure costs to meet the letter of the law.

"The removal of the requirement removes a major commercial hurdle and signals India's intent to attract global satellite operators," said Utkarsh Sinha, managing director at Bexley Advisors.

New Delhi is betting that India's sheer market size — 1.4 billion potential users, hundreds of millions in underserved rural areas — will eventually pull manufacturing investment without a mandate. The approach mirrors what worked with smartphone assembly: build demand first, and the factories follow.

The government has, however, retained significant sovereign controls. Gateway infrastructure must pass through Indian-controlled ground stations. The Centre retains the power to issue directions, suspend or revoke authorisations, and security norms for satellite providers have been tightened under the new rules.

## What this means for the diaspora

For NRIs with family in rural India — and there are millions — satellite broadband could be transformative. Terrestrial fibre remains patchy outside major metros, and 4G coverage in remote districts is unreliable. LEO satellite constellations promise broadband-class speeds anywhere with a clear view of the sky, from a village in Bihar to a farm in Rajasthan.

The investment angle is equally compelling. Bharti Airtel, which backs Eutelsat OneWeb, stands to gain from an accelerated Indian rollout. Tata Group, already invested in satellite communications through Nelco, is positioning for the same market. For NRI investors who remember the mobile revolution that took India from 10 million to a billion connections in 15 years, the satellite broadband opportunity carries echoes of that same trajectory — but compressed into a fraction of the time.

Starlink has already secured key regulatory approvals and is awaiting spectrum allocation. The race to wire India from space is officially on."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Dropped the Rule That Was Keeping Starlink Out. The Satellite Race Is On.",
    "subheadline": "New Delhi's decision to scrap a 20 per cent local sourcing mandate clears the path for Starlink, OneWeb and Amazon Kuiper to bring broadband to 1.4 billion people.",
    "slug": make_slug("india-drops-satcom-local-sourcing-starlink-oneweb-kuiper"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "For NRIs with family in underserved rural India, satellite broadband could deliver reliable internet where fibre and 4G never reached — and Bharti-backed OneWeb makes it an investable thesis.",
    "tags": ["starlink", "satellite-broadband", "india-telecom", "space-tech", "bharti-airtel", "amazon-kuiper"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/buzz/india-drops-20-local-sourcing-rule-for-satcom-applicants/"},
        {"name": "Communications Today", "url": "https://communicationstoday.co.in/"},
        {"name": "Lapaas Voice", "url": "https://voice.lapaas.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Starlink_Rocket_Launch_6-71_%288825933%29.jpg/1280px-Starlink_Rocket_Launch_6-71_%288825933%29.jpg",
    "image_caption": "A SpaceX Starlink rocket launch carrying satellite broadband payloads into orbit",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ═════════════════════════════════════════════════════════════════════════
# ARTICLE 3 — Asian AI alternatives fill the Anthropic vacuum
# ═════════════════════════════════════════════════════════════════════════

art3_body = """Two weeks after the Trump administration ordered Anthropic to suspend global access to its most powerful AI models, the vacuum is filling faster than Washington probably anticipated — and not with American alternatives.

In a single week, three Asian AI players launched products explicitly positioned against Anthropic's embargoed models. Tokyo-based Sakana AI unveiled Fugu, a multi-model orchestration system that routes tasks across a pool of available models to match the performance of frontier systems without requiring any single restricted model. China's cybersecurity giant 360 Security introduced Tulongfeng, an automated vulnerability discovery tool it says rivals Anthropic's Mythos in offensive security. And Zhipu AI, the Beijing startup now valued at $128 billion after a parabolic post-IPO rally, released GLM-5.2 — an open-weight model that scores within a percentage point of Anthropic's Opus 4.8 on agentic coding benchmarks, at roughly one-sixth the cost.

Their collective message is blunt: if American export controls make frontier AI unreliable, the rest of the world will build around it.

## The architectural divergence

What makes Sakana's approach particularly interesting is that Fugu is not a model in the traditional sense. It is an orchestration layer — a system that decomposes complex tasks, identifies which available model handles each subtask best, and assembles the results. On SWE-Bench Pro, a rigorous software engineering benchmark, Fugu Ultra scored 73.7 per cent, outperforming several Western frontier models that cost orders of magnitude more to train.

"Delivering frontier capability without the risk of export controls," Sakana's website advertises, with the subtlety of a billboard. Co-founded in 2023 by former Google researchers including Transformer co-author Llion Jones, the company insists the timing was "entirely coincidental." The market does not seem to care about the distinction.

Zhipu's GLM-5.2, meanwhile, takes the brute-force approach: a massive open-weight model that anyone can download, run on their own servers and modify without supervision. Its strength in coding and agentic tasks makes it directly competitive for the enterprise workloads that drive most frontier-model revenue — and its open architecture means no government can unplug it overnight.

## Where India stands

For India's technology ecosystem, the implications are uncomfortable. The country has no sovereign frontier model at production scale. BharatGen and Param-2 are promising government-backed initiatives, but they are not yet competitive with models from OpenAI, Anthropic or even Zhipu. India's rapidly growing AI startup ecosystem — Sarvam AI, Krutrim, the nascent BharatGPT effort — is building on top of American and, increasingly, Chinese foundation models.

The Anthropic export ban showed that access to those models can be withdrawn overnight. India's diplomatic intervention helped — MeitY Secretary S. Krishnan secured conversations with US officials about long-term access guarantees — but diplomatic assurances are not the same as sovereign capability.

For Indian developers and enterprises, the practical takeaway is diversification. Building critical AI infrastructure on a single provider's API is now a measurable risk. The Sakana model — orchestration across multiple providers, so no single point of failure — may be the most prudent architecture for any Indian company deploying frontier AI at scale.

For NRI engineers at American AI labs, the geopolitical dimension adds another layer. The export controls that restrict Anthropic's models also shape who gets to work on them. Foreign-national employees at Anthropic were temporarily locked out of their own company's products. In an industry where Indian-origin researchers hold senior positions at every major lab, the line between national security and talent policy is getting uncomfortably thin."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "America Banned Its Best AI Models. Japan and China Built Replacements in Two Weeks.",
    "subheadline": "Sakana AI, Zhipu and 360 Security have launched Anthropic alternatives that sidestep US export controls. India, with no sovereign frontier model, is taking notes.",
    "slug": make_slug("asian-ai-alternatives-anthropic-ban-sakana-zhipu-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian developers and enterprises dependent on US AI models face overnight access risk; NRI engineers at American AI labs are caught between export controls and their own careers.",
    "tags": ["ai", "export-controls", "anthropic", "sakana-ai", "zhipu", "sovereign-ai", "india-ai", "geopolitics"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/28/asian-ai-startups-launch-mythos-like-models-as-anthropics-export-ban-drags-on/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/"},
        {"name": "CNN", "url": "https://www.cnn.com/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Server racks and fibre-optic cabling inside a modern data centre",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ═════════════════════════════════════════════════════════════════════════
# Insert all articles
# ═════════════════════════════════════════════════════════════════════════

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
