#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-29 17:00 PDT run."""

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


# ─── ARTICLE 1: London Spirit Cricket Acquisition ───────────────────────

art1_body = """Silicon Valley's biggest names have bought themselves a cricket team — and not just any team. It's the one that plays at Lord's.

A consortium of eleven tech executives, led by Palo Alto Networks chairman and CEO Nikesh Arora, outbid IPL franchise owner Sanjiv Goenka's RPSG Group in a gruelling four-hour online auction to secure a 49 per cent stake in London Spirit, one of eight franchises in England's Hundred competition. The final valuation: £295 million, or roughly $375 million. The consortium will pay £145 million for its minority share.

The investor list reads like a who's who of Indian-origin tech leadership. Alongside Arora sit Satya Nadella (Microsoft), Sundar Pichai (Alphabet), Shantanu Narayen (Adobe), and Satyan Gajwani, co-founder of Major League Cricket and vice-chairman of Times Internet. Egon Durban, co-CEO of Silver Lake Management, rounds out the publicly named members. Five more individuals in the group are yet to be disclosed.

## From Hyderabad and Chennai to Lord's

The deal is the latest — and most expensive — chapter in Indian tech capital's rapid colonisation of global cricket. Nadella and Narayen are already investors in Major League Cricket, the fledgling American T20 league. Gajwani helped found it. Now, through a holding company called Cricket Investor Holdings Limited, the same cohort is planting a flag in English cricket's most hallowed ground.

They are hardly alone. Reliance Industries, controlled by Mukesh Ambani, secured the Oval Invincibles for roughly half the Spirit's price. Sanjiv Goenka's RPSG Group picked up a 70 per cent stake in the Manchester Originals. Chennai's Sun TV Network bought the Northern Superchargers outright. The GMR Group, which co-owns the Delhi Capitals in the IPL, took 49 per cent of Southern Brave. In total, Indian or Indian-origin investors now have stakes in at least five of eight Hundred franchises.

The ECB, which initially hoped to raise £350 million from the entire process, has already crossed £300 million with four teams still to be sold. English cricket's financial future, it turns out, runs substantially through India.

## Why This Matters to Indian Americans

For NRIs in the US, the deal carries a dual significance. First, the personal: the CEOs running your employer — or competing for your talent — are spending nine-figure sums on cricket, a sport that binds the diaspora in ways few other things do. Nadella has spoken publicly about growing up watching Gavaskar bat; Pichai is a vocal cricket tragic. Their investment is both financial and cultural.

Second, the structural: cricket's centre of economic gravity has shifted irreversibly. The IPL was the first tremor. Major League Cricket was the American aftershock. London Spirit at Lord's is the proof that Indian tech wealth now sets the price in world cricket. When the Hundred's season starts on 21 July, the consortium's team will take the field at the "Home of Cricket" — owned, in part, by the men who run the internet.

The Washington Freedom, another MLC franchise, separately acquired Welsh Fire for £65 million, further cementing the American cricket ecosystem's reach into English cricket.

## What the Consortium Gets

At £295 million, Spirit's valuation is more than double its floor price and roughly twice what Reliance paid for the Invincibles. The premium reflects Lord's unique cachet. The Marylebone Cricket Club retains majority ownership and day-to-day control of the ground, but the consortium gains commercial upside in a league designed to attract younger, casual fans — the exact demographic that made the IPL a cultural phenomenon.

"Can we replicate the IPL in the UK?" Arora asked on the Sky Sports Cricket Podcast after the deal. "With all humility, some of our consortium members are the best business brains in the world."

Humility may be debatable. The ambition is not."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nadella, Pichai, and Arora Just Bought a Cricket Team at Lord's. They Paid £145 Million.",
    "subheadline": "A consortium of eleven Silicon Valley executives, most of Indian origin, outbid Sanjiv Goenka to take a 49 per cent stake in London Spirit — the most expensive franchise deal in The Hundred's history.",
    "slug": make_slug("nadella-pichai-arora-london-spirit-lords-cricket-hundred"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin tech CEOs who run America's biggest companies are now buying up global cricket franchises, with Indian or Indian-origin investors holding stakes in five of eight Hundred teams — a cultural and financial statement for the diaspora.",
    "tags": ["indian-tech-leaders", "cricket", "silicon-valley", "franchise-sports", "london-spirit", "the-hundred"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com/cricket-news/"},
        {"name": "TechRadar", "url": "https://www.techradar.com/"},
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com/"},
        {"name": "Front Office Sports", "url": "https://frontofficesports.com/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "image_caption": "Nikesh Arora, chairman and CEO of Palo Alto Networks, who led the Silicon Valley consortium's bid for London Spirit",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ─── ARTICLE 2: OpenAI Hires Prabhjeet Singh as India MD ───────────────

art2_body = """OpenAI has poached one of India's most experienced tech operators to run its fastest-growing market outside the United States.

Prabhjeet Singh, who spent nearly eleven years at Uber — the last six as president of its India and South Asia operations — will join OpenAI in September as managing director for India. He will report to Kiran Mani, managing director for Asia Pacific, and become the company's most senior executive in the country.

The appointment is OpenAI's clearest signal yet that it views India not as an afterthought, but as a pillar of its commercial strategy. India is now OpenAI's second-largest market globally, with more than 100 million weekly ChatGPT users. It also ranks among the company's top five markets for API usage, making it critical for both consumer growth and enterprise revenue.

## The Uber Playbook, Applied to AI

Singh's mandate is broad: consumer growth, enterprise adoption, strategic partnerships, regulatory engagement, and day-to-day operations. It is, in effect, the same scope he managed at Uber, where he transformed a ride-hailing service into a multi-product mobility platform spanning Auto, Moto, Shuttle, and electric vehicle partnerships.

His career arc is a familiar one in India's tech ecosystem. An engineering degree from IIT Kharagpur. An MBA from IIM Ahmedabad. Stints at Lehman Brothers in London and McKinsey before joining Uber in 2015 as head of strategy. He rose through the ranks during the company's most turbulent years, navigating the pandemic, the competitive assault from Ola, and the regulatory maze of Indian ride-hailing. If anyone knows how to scale a foreign tech company in India, it is probably him.

## Why India Matters to OpenAI — and Vice Versa

OpenAI opened its first office in New Delhi in November 2025. It now plans to expand into Mumbai and Bengaluru during 2026. The pace is deliberate. India's AI market is growing fast, but it is also contested. Google's Gemini is aggressively priced for Indian consumers. Anthropic is pushing into enterprise accounts. And homegrown players like Sarvam AI — now valued at $1.5 billion after its HCLTech-led Series B — are building India-specific models for banking, insurance, and government services.

Singh's appointment reflects a broader industry trend: global AI companies hiring seasoned India operators rather than parachuting in expats. Meta brought in Kunal Shah to lead WhatsApp. Google's India AI leadership is deeply local. OpenAI is following the same playbook.

## What This Means for NRIs in Tech

For Indian Americans working in AI, the appointment is a data point in a larger pattern: India is no longer a cost-optimisation play for Silicon Valley. It is a product market. OpenAI needs users, developers, enterprise clients, and regulatory goodwill in India. Singh's job is to deliver all four.

For those considering a return to India — or a dual-market career — the opportunity is tangible. OpenAI's expansion will require engineers, product managers, and enterprise salespeople across three cities. The company is competing for the same talent pool as Google DeepMind's Bengaluru office, Microsoft's Hyderabad AI centre, and the wave of Indian AI startups that have raised over $1.2 billion in deep-tech funding this year alone.

The AI boom, in other words, is not just an American story. India is becoming a front line — and OpenAI just put its most experienced general in charge."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Hired Uber India's Boss to Run Its Second-Largest Market",
    "subheadline": "Prabhjeet Singh, an IIT Kharagpur and IIM Ahmedabad alumnus who spent eleven years at Uber, will lead OpenAI's India operations as the company expands to Mumbai and Bengaluru.",
    "slug": make_slug("openai-prabhjeet-singh-india-md-uber-chatgpt"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India is now OpenAI's second-largest market with 100M+ weekly ChatGPT users — NRIs in AI face new career opportunities as the company opens offices in Mumbai and Bengaluru, competing for the same talent pool as Google DeepMind and Microsoft.",
    "tags": ["openai", "india-ai", "chatgpt", "uber", "silicon-valley", "ai-hiring"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16323438/pexels-photo-16323438.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Professionals collaborating in a modern tech office — the kind of talent OpenAI is hiring across three Indian cities",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ─── ARTICLE 3: Apple Price Hikes in India ──────────────────────────────

art3_body = """The AI boom just reached your desk — literally.

On 25 June, Apple raised the price of MacBooks and iPads across its India lineup by 14 to 42 per cent, with the steepest single increase a ₹70,000 jump on the MacBook Pro. The company did something it almost never does: it blamed the cost of someone else's business. The "rapid expansion of AI data centres," Apple said, had created "an extraordinary surge in demand for memory and storage" that it could no longer absorb.

Apple's shares fell more than 6 per cent on the news, their worst single-day drop since April 2025. Dell declined over 8 per cent. The consumer hardware industry, it turns out, is an accidental casualty of the AI arms race.

## The Numbers

The price hikes are not subtle. The base MacBook Air (M5, 13-inch) jumped from ₹1,19,900 to ₹1,49,900 — a 25 per cent increase. The MacBook Pro (M5, 14-inch) went from ₹1,69,900 to ₹2,39,900, a 41 per cent hike of ₹70,000. Even the entry-level MacBook Neo rose ₹10,000 to ₹79,900. The iPad Air (11-inch, M4) climbed 38 per cent, from ₹64,900 to ₹89,900.

India received the steepest increases of any major market. Analysts point to a compounding effect: global component costs rising in dollars, the rupee's depreciation against the dollar, India's import duties on electronics, and 18 per cent GST on laptops. A ₹2,39,900 MacBook Pro is already a three-month salary for many Indian IT professionals. For students and small businesses, the devices have crossed from expensive to aspirational.

## Why AI Is to Blame

The root cause is straightforward supply-and-demand economics. Samsung, SK Hynix, and Micron — the three companies that control nearly all of the world's DRAM and NAND flash memory — have been diverting manufacturing capacity toward high-bandwidth memory (HBM) for AI data centres. HBM commands significantly higher margins than the conventional DRAM that goes into laptops and phones.

The numbers are striking. Amazon, Alphabet, Microsoft, Oracle, and Meta are projected to spend roughly $1.6 trillion in combined capital expenditure over the next two fiscal years, with around 60 per cent flowing into compute hardware. That demand has vacuumed up memory supply, creating shortages and price spikes for everyone else. Apple CEO Tim Cook warned in January that rising memory costs had "started to pressure profitability," but said the company would try to shield consumers. That shield has now broken.

Apple is reportedly lobbying the Trump administration for approval to source DRAM from Chinese manufacturer CXMT — a move that would diversify its supply chain but risks political blowback in both Washington and New Delhi, where semiconductor self-reliance is a stated national priority.

## What This Means for Indian Tech Workers

The impact falls disproportionately on India's tech workforce. MacBooks are the default machine for developers, designers, and product managers across Bengaluru, Hyderabad, and Pune. Companies that provide laptops absorb the cost increase — but startups, freelancers, and the millions of Indian tech workers who buy their own equipment are now looking at significantly higher bills.

For NRIs who routinely buy Apple devices during India trips to take advantage of lower pre-hike prices, that arbitrage has narrowed sharply. In some configurations, Indian prices now exceed US prices after accounting for exchange rates.

The broader lesson is uncomfortable: the AI revolution is not free. Its infrastructure demands are reshaping supply chains, raising costs, and forcing trade-offs that reach far beyond the data centre. The next time an AI company announces a $10 billion cloud investment, remember that the bill lands, eventually, on someone's desk.

In India, it just landed on ₹2,39,900 worth of aluminium and Retina display."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The AI Boom Just Made Your MacBook 42% More Expensive. India Got the Worst of It.",
    "subheadline": "Apple raised MacBook and iPad prices by up to ₹70,000 in India — the steepest hikes of any market — as AI data centres vacuum up the world's memory chip supply.",
    "slug": make_slug("apple-macbook-ipad-india-price-hike-ai-memory-shortage"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian tech workers who buy their own laptops face steep cost increases, while NRIs lose the pricing arbitrage that made India trips a chance to buy Apple devices at a discount — a direct consequence of the AI infrastructure boom.",
    "tags": ["apple", "macbook", "india-tech", "ai-infrastructure", "semiconductor", "consumer-tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://www.theindianeye.com/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
        {"name": "StartupTalky", "url": "https://startuptalky.com/"},
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/306198/pexels-photo-306198.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A MacBook Air keyboard — Apple's laptops in India now cost up to 42 per cent more due to AI-driven memory shortages",
    "image_attribution": "Pexels",
    "body": art3_body,
}


# ─── INSERT ─────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
