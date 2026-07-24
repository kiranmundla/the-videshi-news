#!/usr/bin/env python3
"""Tech writer — June 30, 2026 (scheduled run)"""

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


# ---------- ARTICLE 1 ----------

article1_body = """OpenAI has appointed Prabhjeet Singh, the former President of Uber India and South Asia, as its first Managing Director for India. Singh will join the company in September, becoming the most senior OpenAI executive in a market the company now calls its second-largest in the world.

The appointment is the clearest signal yet that Sam Altman's AI juggernaut is done treating India as an afterthought. With more than 100 million weekly active ChatGPT users in the country — a number that puts India just behind the United States — OpenAI has decided it needs someone who knows how to build a business at Indian scale, not just ship a product to it.

## An Operator, Not a Researcher

Singh is not an AI researcher. He is an operator. During nearly eleven years at Uber, he built the ride-hailing company's India business from a handful of city launches into a platform spanning ride-hailing, auto-rickshaws, two-wheelers, shuttle services, electric mobility partnerships, and an integration with India's Open Network for Digital Commerce (ONDC). Before Uber, he was an Associate Partner at McKinsey & Company and worked at Lehman Brothers. He studied engineering at IIT Kharagpur and management at IIM Ahmedabad.

His mandate at OpenAI will span consumer growth, enterprise adoption, strategic partnerships, regulatory engagement, and overall business operations. He will report to Kiran Mani, the company's Managing Director for Asia Pacific, who was himself hired from JioStar just weeks ago.

## Why India, Why Now

OpenAI's India push has been building methodically. The company opened its first office in New Delhi in November 2025. Additional offices in Mumbai and Bengaluru are planned for this year. It has already forged partnerships with Reliance and Tata Group, two conglomerates that between them touch virtually every sector of the Indian economy. On the public-sector side, it has begun engaging with institutions and government bodies.

The timing is not accidental. India's AI market is rapidly becoming a three-way battlefield between OpenAI, Google (which has embedded Gemini deep into its India products), and Anthropic. Microsoft, OpenAI's largest backer, has committed $50 billion this decade to AI adoption in developing countries, with India near the top of that list. Sarvam AI, backed by the Indian government's own IndiaAI Mission, is building sovereign foundation models. The window for establishing dominance is measured in quarters, not years.

Singh's hire also comes as India's AI governance framework takes shape. MeitY's recently published India AI Governance Guidelines emphasise "Do No Harm" principles, user consent, and data transparency — a regulatory environment that will require sustained, senior engagement.

## What This Means for the Diaspora

For the tens of thousands of Indian engineers working at AI companies in the Bay Area, Seattle, and New York, this hire carries a quieter message: India is no longer just the country they left. It is an AI market that global companies are building leadership teams around. The appointment of an IIT-IIM graduate to run OpenAI's India operations — rather than parachuting in a San Francisco executive — suggests the company understands that India requires local instinct, not imported playbooks.

The enterprise implications are equally significant. Indian IT services giants — TCS, Infosys, Wipro, HCL — are scrambling to build AI capabilities even as "AI deflation" compresses their margins. OpenAI's deepening India presence could accelerate the shift from pilot projects to production-scale AI adoption, creating both opportunities and competitive pressure for companies that employ hundreds of thousands of Indian engineers.

For NRI investors, the subtext is straightforward: India's AI ecosystem is no longer speculative. When a company valued at over $300 billion assigns its most senior country leader to your home market, it is a bet worth watching."""

article1_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-27/"},
    {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/openai-names-prabhjeet-singh-managing-director-india"},
    {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/technology/openai-appoints-former-uber-india-chief-prabhjeet-singh-as-its-first-india-managing-director"},
    {"name": "afaqs!", "url": "https://www.afaqs.com/news/digital/uber-india-head-prabhjeet-singh-joins-openai-as-india-managing-director"}
])

# ---------- ARTICLE 2 ----------

article2_body = """India's semiconductor ambitions have collided with a war thousands of kilometres away. The West Asia conflict — which shut the Strait of Hormuz and disrupted energy infrastructure across the Gulf — is now delaying several of the country's marquee chip projects, including Tata Electronics' showcase fabrication plant in Dholera, Gujarat.

The delays are not caused by sanctions or trade restrictions. They are caused by chemistry.

## The Materials Problem

Semiconductor manufacturing demands an exotic cocktail of ultra-high-purity gases, chemicals, and metals. Many of them originate in or transit through West Asia. Qatar, which supplies roughly 30 percent of the world's helium — a gas essential to cooling processes in chip fabrication — was forced to halt production of liquefied natural gas early in the conflict after Iranian attacks struck Ras Laffan, its principal industrial hub. Since helium is a byproduct of LNG production, its supply dropped immediately.

Bromine, concentrated in the Dead Sea region shared by Israel and Jordan, is critical to semiconductor packaging and specialised etching chemicals. Sulphur and sulphuric acid, used in wafer cleaning and etching, are also at risk: approximately 40 percent of global sulphur exports pass through the Strait of Hormuz. When the strait closed, logistics routes were severed and spot prices for several of these materials more than doubled.

India's greenfield semiconductor projects are particularly exposed. Established chip makers like TSMC and Samsung maintain diverse, long-term supplier contracts and extensive on-site inventories built over decades. A new fab under construction in Gujarat has none of those buffers.

## Tata's Dholera Dilemma

Tata Electronics' Dholera fab — India's flagship semiconductor facility, being built in partnership with Taiwan's PSMC — is "expected to be hit the worst owing to the sheer size and scale of the project," according to people familiar with the matter. The company was airlifting materials to keep construction on schedule, but this is "not viable in the long run because it cannot cater to the large volumes needed for such a project and is prohibitively expensive."

The impact extends beyond Tata. Assembly and test facilities being built by CG Semi and Micron in India are also facing disruptions. Industry experts estimate that project timelines have been pushed back by six to twelve months, with significant cost overruns.

Not everyone agrees the damage is severe. Some sources say Tata Electronics activated a strong business continuity plan, established alternate sourcing, and received government support. "No significant delays to the timelines are expected due to the conflict," one person said. The truth likely lies somewhere in between.

## The Contrast With Established Players

The Wall Street Journal recently reported that global chip makers — TSMC, Samsung, Intel — barely flinched during the helium shortage. They had long-term contracts with suppliers of critical gases, extensive storage caverns, and years of supply-chain diversification. Air Liquide recently inked a deal with SK Hynix, while Samsung tapped Air Products for industrial gases.

India, by contrast, is trying to build a semiconductor ecosystem from scratch. Its 12 approved projects under the India Semiconductor Mission represent investments of nearly ₹1.64 lakh crore (approximately $19 billion), but the ecosystem lacks the deep supplier relationships, redundant logistics, and buffer stocks that insulate mature chip-making nations from exactly this kind of shock.

Rising crude oil prices have compounded the pressure. Semiconductor fabs are among the world's most energy-intensive facilities, and analysts estimate the conflict has already raised energy costs for fabs by 20 to 30 percent and pushed petrochemical input expenses up by 8 to 10 percent.

## The NRI Calculation

For the growing number of Indian-American semiconductor engineers weighing return-to-India opportunities — whether at Tata's Dholera fab, Micron's Gujarat assembly plant, or one of the design startups emerging from the India Semiconductor Mission — these delays add a practical variable to an already complex calculation.

The jobs will still materialise, but they may arrive later than promised. More importantly, the episode exposes a structural vulnerability: India's chip dreams are hostage to supply chains it does not yet control. South Korea invests $576 billion in chips; India invests $19 billion. That gap was already a concern. The West Asia conflict has made it tangible."""

article2_sources = json.dumps([
    {"name": "The Economic Times (via NewsPoint)", "url": "https://www.newspointapp.com/west-asia-conflict-may-delay-indias-chip-projects/"},
    {"name": "The Wall Street Journal", "url": "https://www.wsj.com/articles/middle-east-helium-supply-shock-chip-makers"},
    {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/electronics-semicon-supply-chain-navigate-west-asia-tensions/article69320187.ece"},
    {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/west-asia-crisis-a-war-far-from-fabs-is-rattling-the-chip-supply-chain/"}
])


# ---------- INSERT ----------

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI Poached Uber India's Boss to Run Its Second-Largest Market. He Starts in September.",
        "subheadline": "Prabhjeet Singh — IIT Kharagpur, IIM Ahmedabad, eleven years building Uber's India business — will become OpenAI's most senior executive in a country with 100 million weekly ChatGPT users.",
        "slug": make_slug("openai-prabhjeet-singh-india-md-uber-chatgpt"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "An IIT-IIM alumnus leading OpenAI in India signals the country is no longer just a talent pipeline — it is a market global AI companies are building C-suite leadership around.",
        "tags": ["openai", "india-ai", "chatgpt", "indian-tech-leaders", "uber"],
        "urgency": "high",
        "sources": article1_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
        "image_caption": "OpenAI CEO Sam Altman at the White House in February 2025",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A War 5,000 Miles Away Is Slowing India's Chip Dreams. Tata's Dholera Fab Is Hit Hardest.",
        "subheadline": "The West Asia conflict has disrupted supplies of helium, bromine, and sulphur — exotic materials that India's greenfield semiconductor fabs need and cannot yet source independently.",
        "slug": make_slug("india-semiconductor-delays-west-asia-tata-dholera"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI semiconductor engineers eyeing return-to-India roles at Tata or Micron face a new variable: project timelines pushed back 6-12 months as supply chains India doesn't control buckle under geopolitical stress.",
        "tags": ["semiconductor", "india-chips", "tata-electronics", "supply-chain", "west-asia"],
        "urgency": "medium",
        "sources": article2_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Silicon_wafer_researcher.jpg/1280px-Silicon_wafer_researcher.jpg",
        "image_caption": "A researcher handles a silicon wafer inside a semiconductor fabrication facility",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
