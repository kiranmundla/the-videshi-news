#!/usr/bin/env python3
"""NRI World writer — 2026-06-29 05:00 PT run.

Two articles:
1. Somdutta Singh wins EY Entrepreneur of the Year 2026 Southeast Award
2. Sudhanshu Priyadarshi appointed CFO & President, International at Planet Fitness
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ───────────────────────────────────────────────────────────────
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

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1 ─────────────────────────────────────────────────────────
article1_body = """\
Somdutta Singh was already used to being the only Indian woman in the room. At the EY Entrepreneur Of The Year gala in Atlanta last Thursday, she became just the third Indian woman in the programme's 41-year history to take home the Southeast award — and, at that, the youngest.

The two names before hers carry considerable weight: Kiran Mazumdar-Shaw, the biotech billionaire behind Biocon, and Falguni Nayar, the former investment banker who built Nykaa into India's beauty-commerce giant. Singh's company, Assiduus Global, operates in a less glamorous but arguably more consequential corner of commerce: the middleware that connects brands to foreign marketplaces.

## The Plumbing of Cross-Border Trade

Founded eight years ago, Assiduus is an AI-powered platform that handles the entire distribution and supply chain for brands selling across international markets — market entry, inventory planning, fulfilment, marketplace operations, and omnichannel commerce. If a mid-sized Indian consumer brand wants to sell on Amazon US, Walmart.com, or a European marketplace, Assiduus does the heavy lifting: regulatory compliance, logistics routing, demand forecasting, and pricing optimisation across borders.

The company is profitable, a rarity among cross-border logistics startups that have burned through venture capital chasing gross merchandise value. Singh, a first-generation entrepreneur, bootstrapped much of the early growth before attracting institutional backing. EY's independent panel of judges — which includes previous laureates and sitting CEOs — cited her "entrepreneurial spirit, sense of purpose, growth, and impact."

## Why the Diaspora Should Care

Cross-border commerce is the infrastructure layer beneath the diaspora's relationship with India. NRIs ordering specialty goods from Indian D2C brands, or Indian exporters trying to crack the American or European retail market, ultimately depend on exactly the kind of plumbing Assiduus provides. As India pushes to become a $1 trillion e-commerce market by 2030, the companies enabling that trade — rather than just riding it — will matter enormously.

Singh's win also signals a broader shift. Indian women founders are still vastly underrepresented in global entrepreneurship awards, and the EY programme, which spans nearly 60 countries, is as close to a consensus "who's who" as the startup world gets. Having three Indian women on that list — Mazumdar-Shaw in life sciences, Nayar in consumer tech, and now Singh in trade infrastructure — traces the expanding arc of what Indian women entrepreneurs are building.

She now enters the running for the EY Entrepreneur Of The Year national award later this year. If history is any guide, the judges will want to see evidence that her technology scales as elegantly as her ambition.

*Sources: EINPresswire, EY Entrepreneur Of The Year programme*
"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "She Built the Middleware That Moves Indian Brands Across Borders. EY Just Noticed.",
    "subheadline": "Somdutta Singh becomes the third and youngest Indian woman to win an EY Entrepreneur Of The Year award, after Kiran Mazumdar-Shaw and Falguni Nayar.",
    "slug": make_slug("somdutta-singh-ey-entrepreneur-year-southeast-assiduus-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Singh's cross-border commerce platform is the infrastructure layer NRIs and Indian exporters depend on. Her recognition at a global entrepreneurship award elevates the visibility of Indian women founders in the diaspora business landscape.",
    "tags": ["nri", "diaspora", "entrepreneur", "business", "ey-award", "indian-women"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "EINPresswire", "url": "https://www.einpresswire.com/article/922370510/somdutta-singh-founder-ceo-of-assiduus-global-becomes-the-3rd-indian-woman-to-win-ey-entrepreneur-of-the-year-award"},
        {"name": "NRI ConnectMyIndia", "url": "https://nri.connectmyindia.com/"},
        {"name": "EY Entrepreneur Of The Year Programme", "url": "https://www.ey.com/en_us/entrepreneur-of-the-year"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1427541/pexels-photo-1427541.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Shipping containers at a busy international port, symbolising the cross-border commerce infrastructure Singh's company powers",
    "image_attribution": "Pexels",
    "body": article1_body,
}


# ── Article 2 ─────────────────────────────────────────────────────────
article2_body = """\
When Planet Fitness announced last Wednesday that Sudhanshu Priyadarshi would serve as its new Chief Financial Officer *and* President of International, the press release ticked the usual boxes: 25 years of experience, global consumer brands, strategic vision. What it didn't dwell on is the trajectory that brought a graduate of India's National Law School to the C-suite of America's largest gym chain by membership.

## From Bengaluru's Law School to Hampton, New Hampshire

Priyadarshi's résumé reads like a case study in the Indian executive diaspora's quiet march through American corporate hierarchies. After earning a master's in business law from the National Law School of India University in Bengaluru, he pursued business administration at Georgia Southern University and later studied public policy and artificial intelligence at Singapore's Lee Kuan Yew School. The education is deliberately eclectic — law, business, policy, tech — and mirrors a career that has zigzagged across industries and continents.

He spent formative years at PepsiCo, where he worked across the company's sprawling operations. He moved through Walmart's global business, then to Flexport (the freight-forwarding startup that briefly became Silicon Valley's logistics darling), and on to Vista Outdoor, the ammunition-and-outdoors conglomerate. Most recently, he held the dual CFO and President, International role at Keurig Dr Pepper, overseeing finance, IT, and global operations for the beverage giant.

## The Planet Fitness Bet

Planet Fitness is not a luxury play. It is the Judgement Free Zone — the gym chain built on $10 monthly memberships, free pizza Mondays, and the deliberate absence of grunting bodybuilders. With more members than any other fitness brand in the world and a franchise-heavy model, it is essentially a consumer-finance operation wrapped in purple and yellow spandex. Priyadarshi's job is twofold: tighten the financial machinery at home and take the brand global.

The international piece is where his Indian and multi-continental experience matters most. Planet Fitness has roughly 2,700 locations, the vast majority in the United States. The company has signalled ambitions to expand into new geographies, and it needs someone who has actually managed businesses in 80-plus countries — which Priyadarshi has, across North America, Europe, Asia-Pacific, and Africa.

## The Broader Pattern

Priyadarshi's appointment adds to a conspicuous trend: Indian-origin executives landing top operational roles at major American consumer brands. Satya Nadella at Microsoft, Laxman Narasimhan at Starbucks (until recently), and Leena Nair at Chanel are the boldface names. But the pipeline runs deeper — through CFO suites, division presidencies, and chief strategy offices that rarely make headlines but quietly shape how these companies run.

For the diaspora, the significance is partly aspirational and partly practical. Every Indian-origin executive who reaches the C-suite of a publicly traded American company normalises a path that, a generation ago, topped out at middle management. And for Planet Fitness members who happen to be NRIs: yes, the person minding the books also studied at NLS Bengaluru. Small world, big gym.

*Sources: Planet Fitness Inc. (PR Newswire), NRI ConnectMyIndia, TradingView*
"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "An Indian Law Graduate Just Became CFO of America's Biggest Gym Chain. He Also Runs Its Global Expansion.",
    "subheadline": "Planet Fitness appoints Sudhanshu Priyadarshi — a National Law School alumnus who has steered finances at Keurig, PepsiCo, and Walmart — as CFO and President, International.",
    "slug": make_slug("sudhanshu-priyadarshi-planet-fitness-cfo-indian-american-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Priyadarshi's appointment at Planet Fitness extends the growing pattern of Indian-origin executives reaching the C-suite of major American consumer brands, normalising a career trajectory that was rare a generation ago.",
    "tags": ["nri", "diaspora", "corporate-leadership", "indian-american", "planet-fitness"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Planet Fitness / PR Newswire", "url": "https://www.prnewswire.com/news-releases/planet-fitness-appoints-sudhanshu-priyadarshi-as-chief-financial-officer-and-president-international-302461853.html"},
        {"name": "NRI ConnectMyIndia", "url": "https://nri.connectmyindia.com/chicago/news/article/indian-american-sudhanshu-priyadarshi-appointed-cfo-and-international-president-at-planet-fitness-3833/"},
        {"name": "TradingView", "url": "https://www.tradingview.com/news/prnewswire:2025062518451510:0/"}
    ]),
    "score_total": 70,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Planet_Fitness_Ypsilanti_Twp.JPG/1280px-Planet_Fitness_Ypsilanti_Twp.JPG",
    "image_caption": "A Planet Fitness location in Ypsilanti Township, Michigan — part of the chain's 2,700-strong network that Priyadarshi now helps steer",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ── Insert ────────────────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
