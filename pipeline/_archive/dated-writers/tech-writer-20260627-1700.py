#!/usr/bin/env python3
"""
Videshi Technology Writer — 2026-06-27 17:00 PDT
2 articles: Turtlemint IPO listing, MoEngage acquires Aampe
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

articles = [
    # ── Article 1: Turtlemint IPO Listing ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Biggest Insurtech IPO Lists on Monday. The Real Test Is Whether Anyone Buys Insurance Differently.",
        "subheadline": "Turtlemint's ₹883 crore debut on BSE and NSE arrives into a market where 96 per cent of Indians still lack adequate health cover — and the company's bet is that half a million human advisors, armed with AI, can close that gap faster than any app alone.",
        "slug": make_slug("turtlemint-insurtech-ipo-listing-bse-nse-india-insurance"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRI investors tracking India's insurtech sector get a rare public-market vehicle, while the platform's 'phygital' model mirrors how many diaspora families still buy insurance — through a trusted advisor, not an app.",
        "tags": ["insurtech", "ipo", "india-fintech", "turtlemint", "insurance-technology", "bse-nse"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/market/ipo/turtlemint-fintech-ipo-listing-date-on-29-june"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/markets/turtlemint-fintech-to-launch-883-crore-ipo-on-jun-19"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/turtlemint-ipo-to-open-on-june-19-price-band-set-at-144-152/"},
            {"name": "IBS Intelligence", "url": "https://ibsintelligence.com/ibsi-news/turtlemint-fintech-ipo/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Stock market trading screen displaying financial data and indices",
        "image_attribution": "Pexels",
        "body": """India's insurtech sector gets its most consequential public-market test on Monday when Turtlemint Fintech Solutions begins trading on the BSE and NSE. The Mumbai-based company, which connects insurance buyers with over five lakh advisors through an AI-powered platform, priced its shares at ₹144–152 apiece in an initial public offering that closed on 23 June.

The numbers tell a story of qualified optimism. The IPO was subscribed 1.2 times overall, with qualified institutional buyers leading at 1.59 times. Retail investors — often the loudest signal of hype — subscribed just 1.07 times, suggesting the market sees promise but not frenzy. At the upper band, the listing values Turtlemint at roughly ₹4,513 crore, or about $475 million: respectable, but hardly the runaway multiples that characterised India's 2021 IPO boom.

## The Phygital Thesis

Turtlemint's pitch is deceptively simple. Insurance in India remains staggeringly under-penetrated — total premium as a share of GDP hovers around 4 per cent, well below the global average of 7 per cent. Health insurance, despite a post-Covid bump, covers barely 4 per cent of the population adequately.

The company's answer is not a pure-play digital app. Founded in 2015 by Dhirendra Mahyavanshi and Anand Prabhudesai, Turtlemint operates what it calls a "phygital" model: its technology platform matches customers with insurance products algorithmically, but the sale is completed by human advisors who use the app as a toolkit. Think of it as Shopify for insurance agents rather than Amazon for policies.

The approach has commercial traction. Between April 2022 and December 2025, the platform facilitated the sale of over 2.18 crore insurance policies, generating premiums exceeding ₹10,066 crore. It has partnerships with more than 40 insurers — roughly 65 per cent of all life and general insurance companies in India — and has expanded into adjacent products including mutual funds, personal loans, and credit cards.

## The IPO Mechanics

The offering comprises a fresh issue of ₹660.72 crore and an offer-for-sale of 1.46 crore equity shares. Major sellers include Peak XV Partners (offloading 43.57 lakh shares), Nexus Venture Partners (27.47 lakh shares), and the founders themselves, who are each selling stakes worth approximately ₹33 crore.

Fresh proceeds will go toward strengthening the technology stack, expanding infrastructure, and supporting TIB, the company's subsidiary. With grey market premium hovering at zero in recent sessions, the listing is unlikely to deliver the kind of first-day pop that retail punters crave. But for institutional investors, the question is longer-term: can Turtlemint demonstrate that its unit economics improve as the advisor network scales?

## Why NRIs Should Watch

For diaspora investors, Turtlemint is a proxy for a structural thesis about Indian financial services. Insurance penetration in India is where banking was a decade ago — on the cusp of a digital-infrastructure-led expansion. UPI transformed payments; the question is whether a similar platform layer can transform insurance distribution.

There is a personal dimension too. Many NRI families still navigate Indian insurance through relatives or trusted advisors back home — exactly the channel Turtlemint is digitising. The company's model resonates with how insurance is actually bought in India: not through slick apps, but through conversations backed by better data.

The listing also arrives in a banner week for Indian fintech. CRED's $900 million raise from Meta and Square Yards joining the unicorn club have already put Indian financial technology back in global headlines. Turtlemint's public debut will test whether public markets are as enthusiastic as private capital.

PB Fintech, which operates Policybazaar and listed in November 2021, remains the sector's closest comparable. It took nearly three years to consistently deliver profitable quarters. Turtlemint, still loss-making at its growth stage, will face similar scrutiny — but with the advantage of entering a market that now demands profitability trajectories, not just growth narratives.

Monday's listing price will be the first verdict. The more consequential one comes in the quarters ahead."""
    },

    # ── Article 2: MoEngage Acquires Aampe ──
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian SaaS Company Just Bought a San Francisco AI Startup. The Direction of That Deal Says Everything.",
        "subheadline": "MoEngage's acquisition of Aampe — and its simultaneous reverse merger to shift domicile back to India — signals that the country's enterprise software companies are done being the outsourced back office. They want to own the product.",
        "slug": make_slug("moengage-acquires-aampe-india-saas-ai-acquisition-reverse-merger"),
        "category": "technology",
        "vertical": "enterprise-saas",
        "diaspora_angle": "Indian-origin SaaS founders who once flipped their companies to US holding structures are now re-domiciling to India — a reversal that has implications for NRI investors, employees, and the broader narrative of where enterprise value gets built.",
        "tags": ["saas", "ai", "moengage", "aampe", "india-acquisition", "enterprise-tech", "agentic-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/moengage-acquires-san-francisco-ai-startup-aampe"},
            {"name": "Indian Startup News", "url": "https://indianstartupnews.com/news/moengage-acquires-aampe-ai-startup"},
            {"name": "Morningstar / PR Newswire", "url": "https://www.morningstar.com/news/pr-newswire/20260624dc05442/moengage-acquires-aampe"},
            {"name": "BestMediaInfo", "url": "https://bestmediainfo.com/2026/06/moengage-acquires-aampe"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Software developers collaborating in a modern tech office workspace",
        "image_attribution": "Pexels",
        "body": """For most of the last two decades, the script for ambitious Indian enterprise software companies has been predictable: build in Bengaluru, flip your holding company to Delaware, raise Silicon Valley money, and eventually sell to a larger American acquirer. MoEngage just tore up that script — twice in the same week.

The Bengaluru- and San Francisco-headquartered customer engagement platform announced last week that it has acquired Aampe, a San Francisco-based AI infrastructure startup that builds autonomous decisioning agents for individual users. The deal terms were not disclosed. And in a separate but symbolically linked move, MoEngage received approval from India's National Company Law Tribunal (NCLT) for a reverse merger to shift its domicile from the United States back to India.

Together, the two announcements mark a notable inflection point for India's enterprise SaaS sector. An Indian company is not being acquired by an American one. It is acquiring an American one. And it is re-domiciling to India while doing it.

## What MoEngage Bought

Aampe, founded in 2020 by Paul Meinshausen, Schaun Wheeler, and Sami Abboud, has built what it describes as a per-user AI agent system. Where most marketing automation platforms segment audiences into broad cohorts — "users who abandoned carts," "high-value customers in the Northeast" — Aampe assigns an individual reinforcement-learning agent to each user. That agent decides, autonomously and continuously, which message to send, when to send it, how often, and through which channel.

"We built Aampe on one conviction: one agent per user, not one model per segment," Meinshausen said in a statement. "A per-user agent builds a persistent, compounding model of each individual — their rhythm, their content preferences, what actually moves them to act."

For MoEngage, which already serves over 1,350 global consumer brands — including Flipkart, Swiggy, Domino's, Coca-Cola, and SoundCloud — through its Merlin AI platform, the acquisition fills a specific gap. Merlin AI helps marketers build campaigns and surface insights. Aampe adds the real-time decisioning layer that operates at the individual level, learning from every interaction rather than resetting with each new campaign.

"Every marketer wants to show up at the right moment, with the right message, for every individual user," said Raviteja Dodda, MoEngage's co-founder and CEO. "The challenge has never been ambition — it's been infrastructure."

Aampe's founding team will join MoEngage to lead what the company calls its "Agentic Decisioning" unit. Existing Aampe customers will continue to be served without disruption.

## The Reverse Merger Signal

The domicile shift is arguably the more consequential development. MoEngage, founded in 2014 by Dodda and Yashwant Kumar, was originally incorporated in the US — a common structure for Indian SaaS companies seeking American venture capital and enterprise customers. The NCLT-approved reverse merger brings the parent entity back to India.

The move follows a broader trend. Razorpay, PhonePe, and Meesho have all executed similar reverse flips in recent years, driven by a combination of factors: India's growing domestic capital markets, the prospect of Indian IPOs, and a regulatory environment that increasingly favours locally domiciled technology companies.

For MoEngage specifically, the reverse merger likely sets the stage for a future Indian public listing. The company is also reportedly evaluating further acquisitions in the US and Europe to expand its product capabilities and geographic reach.

## What This Means for the Diaspora

For Indian-origin engineers and product managers in the Bay Area, MoEngage's moves offer an interesting counter-narrative to the standard career trajectory. The assumption has long been that serious enterprise software gets built in San Francisco and sold globally. Indian companies either serve as outsourced development partners or, at best, build products that compete at lower price points.

MoEngage's acquisition of an American AI startup — and its decision to domicile in India while doing so — suggests the hierarchy is shifting. India's SaaS ecosystem generated over $14 billion in revenue in 2025, according to industry estimates, and companies like Freshworks, Zoho, and Postman have demonstrated that globally competitive products can be built and led from India.

The Aampe deal is small in absolute terms. But in directional terms, it is significant. Indian enterprise software companies are no longer content to be acquisition targets. They are becoming acquirers — and they are doing it on their own terms, from their own soil."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
