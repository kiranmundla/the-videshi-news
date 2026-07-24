#!/usr/bin/env python3
"""Videshi Tech Writer – 2026-06-27 05:00 PDT batch"""

import json, os, uuid, re, requests, urllib.parse
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


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


# ─────────────────────────────────────────────
# ARTICLE 1: SK Hynix Dethroned Samsung
# ─────────────────────────────────────────────

art1_body = """SK Hynix Inc. has done what would have seemed absurd five years ago. On June 22, the memory chipmaker overtook Samsung Electronics to become South Korea's most valuable listed company — the first change at the top of the Kospi in more than a quarter-century. Samsung had held that throne since 2000.

The numbers tell one of the most dramatic corporate turnarounds in Asian tech history. SK Hynix's market capitalisation hit 2,080 trillion won ($1.35 trillion), edging past Samsung's 2,067 trillion won (excluding preferred shares). Its stock has rallied more than 340% this year alone, powered by a single product category that barely existed in its current form three years ago: high-bandwidth memory chips for artificial intelligence.

## The HBM Advantage

What catapulted SK Hynix from a mid-tier commodity chipmaker to a trillion-dollar colossus is its stranglehold on HBM — the stacked memory chips that sit inside every Nvidia AI accelerator and Google TPU. The company has secured roughly two-thirds of Nvidia's initial orders for its next-generation HBM4 chips, according to industry sources. It also supplies HBM3E to Microsoft for its Maia 200 custom AI chip.

"The emergence of customised AI memory fundamentally changed the industry's economics and allowed SK Hynix to establish itself as the market leader," said Kim Sunwoo, a senior analyst at Meritz Securities.

Samsung, which also makes logic chips, consumer electronics and smartphones, has struggled to keep pace in the AI memory race. Its HBM3E chips reportedly failed Nvidia's quality tests earlier this year, costing it crucial supply contracts.

## Wall Street Is Next

SK Hynix is not content with Seoul. The company has tentatively set July 10 for an American depositary receipt listing on the Nasdaq, from which it aims to raise up to $29 billion — a move that would make it one of the largest ADR debuts in history. It is also planning a $66 billion shareholder return programme over the coming years.

The Nasdaq listing will give American retail and institutional investors direct access to the chip stock, bypassing the Korean won and Seoul trading hours. SK Hynix shares currently trade at a discount to U.S.-listed peers like Micron Technology, partly because of South Korea's so-called "Korea discount" — a mix of governance concerns, geopolitical risk and limited foreign access to its equity markets.

The broader Korean market is reflecting the AI-driven mania. The Kospi index surpassed 9,000 points for the first time this month, though analysts warn the rally is narrow: chip stocks are driving the index higher while most other sectors stagnate.

## What This Means for the Diaspora

For NRI investors and Indian semiconductor professionals, SK Hynix's ascent is more than a Korean equity story. It is a live demonstration of how the AI memory supply chain reshapes corporate value.

India has its own memory chapter being written. Micron Technology is building its first semiconductor assembly and test facility in Sanand, Gujarat — a $2.75 billion investment backed by the India Semiconductor Mission. While India is years away from fabricating memory chips, the packaging and testing expertise gained at Sanand feeds directly into the HBM supply chain that is making SK Hynix a trillion-dollar company.

The memory crunch has already hit Indian-American consumers. Apple raised MacBook and iPad prices this month, citing memory shortages driven by AI data centre buildouts. Microsoft's Xbox consoles jumped $150. The same HBM chips enriching SK Hynix's shareholders are thinning the DRAM supply available for consumer devices.

For the Indian engineer at Nvidia designing the next GPU that consumes these very chips, or the NRI investor weighing whether to buy SK Hynix's Nasdaq ADR on July 10, the message is the same: memory is no longer a commodity. It is the chokepoint of the AI economy, and the companies that control it are being valued accordingly."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "SK Hynix Dethroned Samsung After 25 Years. Now It Wants $29 Billion From Wall Street.",
    "subheadline": "The memory chipmaker that nearly went bankrupt in 2002 is now South Korea's most valuable company, planning a Nasdaq ADR listing on July 10 that could be one of the largest in history.",
    "slug": make_slug("sk-hynix-samsung-dethroned-nasdaq-adr-hbm-ai-memory"),
    "category": "technology",
    "vertical": "semiconductors",
    "diaspora_angle": "NRI investors get direct Nasdaq access to the AI memory boom on July 10; Micron's Gujarat fab feeds the same HBM supply chain; memory shortages are already raising Apple and Xbox prices for Indian-American consumers.",
    "tags": ["semiconductors", "sk-hynix", "samsung", "ai-chips", "hbm", "nvidia", "nasdaq", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/sk-hynix-overtakes-samsung-become-koreas-most-valuable-company-2026-06-22/"},
        {"name": "KED Global", "url": "http://www.kedglobal.com/korean-chipmakers/newsView/ked202606220007"},
        {"name": "KED Global", "url": "http://www.kedglobal.com/korean-chipmakers/newsView/ked202606240008"},
        {"name": "Sensor Tower via TechCrunch", "url": "https://techcrunch.com/2026/06/16/chatgpts-market-share-slips-below-50-for-first-time/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg",
    "image_caption": "Close-up of tower servers in a data center with blue and red lighting",
    "image_attribution": "Pexels",
    "body": art1_body
}


# ─────────────────────────────────────────────
# ARTICLE 2: ChatGPT's Market Share Below 50%
# ─────────────────────────────────────────────

art2_body = """For three and a half years, ChatGPT was the AI assistant. Not the best, not the cheapest — just the default, the way Google was for search or Excel was for spreadsheets. That era is over.

According to Sensor Tower's State of AI 2026 report, ChatGPT's share of the global AI assistant market dropped below 50% for the first time in May, falling to 46.4%. Google's Gemini climbed to 27.7%. Anthropic's Claude reached 10.3%, up from roughly 3% just five months earlier.

Here is the paradox: ChatGPT did not shrink. It reached 1.1 billion monthly users in May — the fastest any mobile app has reached that milestone, faster than TikTok, faster than Instagram. At the exact moment it became the biggest app of all time, it became a minority player in its own category.

## Gemini's Quiet Invasion

The biggest winner is Gemini, which hit 662 million monthly users — and its growth has almost nothing to do with people deliberately choosing it. Google has quietly embedded Gemini into Android, Gmail, Chrome and Search. No download required. No signup friction. If you own an Android phone — and about 3.6 billion people do — Gemini is already there, answering queries in your search bar and drafting emails in your inbox.

For Sundar Pichai, the Indian-born CEO of Alphabet, this represents the payoff of a strategy that looked uncertain a year ago. Google's initial AI rollout was marred by embarrassing hallucinations and a rushed Bard launch that wiped $100 billion off Alphabet's market cap in a single day. The pivot to Gemini, tightly integrated across Google's dominant consumer products, has turned distribution into a weapon no standalone app can match.

Gemini added 129 million monthly users in five months. That is not virality. That is infrastructure.

## Claude's Trust Premium

Anthropic's Claude had the most improbable surge. Its user base quadrupled in five months, jumping from about 60 million in December to 245 million by May. The catalyst was not a product launch but a controversy: OpenAI's deal with the U.S. Department of Defence in February triggered a measurable spike in ChatGPT uninstalls. Claude, which had publicly refused to allow its models for mass surveillance or autonomous weapons, became the beneficiary of a values-driven migration.

In the United States, Claude's market share rose from 5% in December to 14% in May. Thirteen percent of its users are paying for a subscription — the highest conversion rate of any AI assistant, a metric that matters enormously for a company raising capital at a $61.5 billion valuation.

## The Indian Numbers

Asia recorded the first decline in AI app downloads — down 3.3% in Q1 2026 — with dips in both China and India. Despite leading globally in total downloads, Asia trails North America and Europe in per-user spending. For AI companies, that gap is both a ceiling and an opportunity: the next billion users will likely come from India, but monetising them requires a fundamentally different pricing model.

For Indian engineers and product managers in Silicon Valley, the fragmenting market has practical consequences. Teams building on ChatGPT's API are now hedging with Gemini and Claude integrations. The monoculture is giving way to a multi-model stack, which means more work, more testing — and more leverage for the developers doing the integrating.

OpenAI has responded by experimenting with advertising. By May, about 17% of ChatGPT's daily users were seeing ads, with software and shopping as the largest advertiser categories. Amazon, notably, has blocked ChatGPT's web crawlers, leading to stagnant referral traffic from the platform — while Walmart has embraced the channel.

The AI race has not produced a winner. It has produced a marketplace. And in a marketplace, distribution, trust and pricing matter more than benchmark scores. Pichai has the first. Anthropic has the second. Sam Altman is betting on the third. For the Indian engineers building across all three, the fragmentation is less a problem than a professional moat."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "ChatGPT Just Lost Its Majority. Pichai's Gemini and an Anthropic Revolt Are Why.",
    "subheadline": "OpenAI's chatbot fell below 50% market share for the first time as Sundar Pichai's Gemini quietly reached 662 million users and Claude quadrupled on a wave of trust-driven migration.",
    "slug": make_slug("chatgpt-market-share-below-50-gemini-claude-pichai"),
    "category": "technology",
    "vertical": "ai",
    "diaspora_angle": "Sundar Pichai's Gemini is the biggest winner in the AI assistant race; Indian engineers in Silicon Valley are building multi-model stacks across ChatGPT, Gemini and Claude; India's download decline signals monetisation challenges ahead.",
    "tags": ["ai", "chatgpt", "gemini", "claude", "sundar-pichai", "openai", "anthropic", "silicon-valley"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/16/chatgpts-market-share-slips-below-50-for-first-time/"},
        {"name": "Sensor Tower State of AI 2026 (via LinkedIn)", "url": "https://www.linkedin.com/pulse/chatgpt-just-fell-below-50-market-share-heres-what-tells-us-future/"},
        {"name": "Fast Company", "url": "https://www.fastcompany.com/91356041/chatgpt-loses-ground-gemini-claude-falling-below-50-percent"},
        {"name": "Apptopia", "url": "https://apptopia.com/blog/gen-ai-chatbots-april-2026-apptopia-data-brief"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google, whose Gemini AI assistant has reached 662 million monthly users",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ─────────────────────────────────────────────
# ARTICLE 3: Five Eyes AI Cyberattack Warning
# ─────────────────────────────────────────────

art3_body = """The intelligence agencies of the United States, United Kingdom, Canada, Australia and New Zealand — collectively known as the Five Eyes — do not issue joint warnings casually. When they do, the language tends toward bureaucratic caution. Not this time.

In a three-page statement released on June 22, the Five Eyes declared that frontier AI models "are anticipated to exceed current industry expectations, fundamentally transforming both offensive and defensive cyber capabilities." Their timeline: "not years, it is months."

The warning names no specific threat actor, but points to a convergence of capabilities that security professionals have been dreading. AI models can now scan vast networks for vulnerabilities faster than any human team, generate realistic phishing emails customised to individual targets and automate the reconnaissance work that used to take weeks. Acting CISA Director Nick Andersen put it bluntly: "Adversaries are already using AI to move faster and more effectively. Defenders must do the same."

## The Models Behind the Worry

The concern is not hypothetical. It stems in part from demonstrations by models such as Anthropic's Mythos and OpenAI's GPT-5.5-Cyber, which have shown the ability to identify and exploit software vulnerabilities at a speed that renders traditional patch-and-respond cycles inadequate.

Earlier this month, Anthropic was forced to disable a version of Mythos after the U.S. government ordered it to suspend access for foreign nationals over national security concerns. Around the same time, CISA reduced the deadline for government agencies to patch critical vulnerabilities from weeks to three days, citing AI threats.

Representative Andrew Garbarino, who chairs the House Homeland Security Committee, framed the warning in geopolitical terms: "China is just months, if not now weeks, away from achieving frontier AI capabilities comparable to those of the United States."

The Five Eyes statement identifies three specific weaknesses that AI will exploit first: weak identity controls, unpatched legacy systems and systems exposed to the internet unnecessarily. Its advice is, in some ways, basic — patch faster, retire old software, test incident plans. But basic controls still fail at scale, which is precisely the point.

## India's Cybersecurity Moment

For India's technology sector, the Five Eyes warning validates a strategic bet that its largest IT services firms have been making for the past three years. TCS, Infosys, Wipro and HCL Tech have all expanded their managed security services divisions, and cybersecurity is now one of the fastest-growing verticals across Indian IT.

The numbers support the pivot. India's cybersecurity market is projected to reach $6.8 billion by 2028, according to the Data Security Council of India. CERT-In, the country's Computer Emergency Response Team, handled more than 15 lakh (1.5 million) cybersecurity incidents in 2025 — a 20% increase over the previous year. The sheer volume of attacks on Indian digital infrastructure, from UPI payment systems to Aadhaar databases, has turned cybersecurity from a compliance checkbox into an operational necessity.

For Indian-American professionals, the implications run in two directions. Those working at U.S. tech firms face an AI-accelerated threat landscape where security teams need to move faster than ever. Those considering a return to India — or building cross-border consulting practices — find a domestic market where demand for cybersecurity expertise is outpacing supply by a factor of three, according to NASSCOM estimates.

Palo Alto Networks, led by Indian-origin CEO Nikesh Arora, has seen demand for its AI-powered security platform surge as enterprises scramble to implement the very defences the Five Eyes recommends. But the Indian IT services firms may have a structural advantage: they already sit inside the networks of Fortune 500 companies, running infrastructure, managing identities and monitoring endpoints.

## A New Kind of Arms Race

The Five Eyes statement closes with a stark message: "Cyber resilience is no longer merely a technical safeguard but a prerequisite for operational survival." It urges organisations to use AI defensively — to find vulnerabilities sooner, monitor for unusual behaviour and respond faster.

What goes unsaid is that the same AI models powering defence will also power attack. The asymmetry that has long favoured attackers — they need to find one weakness, while defenders must protect everything — is about to be amplified by machines that never sleep and never forget a configuration error.

For the Indian diaspora in tech, that asymmetry is both a threat and a career tailwind. The world needs more cybersecurity professionals. India produces more of them, per capita, than almost anywhere else. The Five Eyes just announced, in three pages of measured prose, that the demand is about to get much louder."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Five Eyes Says AI Cyberattacks Are Months Away. India's IT Sector Is Already Selling the Shield.",
    "subheadline": "The intelligence alliance warned that frontier AI models will transform cyber warfare within months. For TCS, Infosys and a generation of Indian security professionals, the timing could not be better.",
    "slug": make_slug("five-eyes-ai-cyberattack-warning-india-it-cybersecurity"),
    "category": "technology",
    "vertical": "cybersecurity",
    "diaspora_angle": "Indian IT services firms like TCS, Infosys and Wipro are pivoting hard into cybersecurity as demand surges; India's domestic cyber market is growing at 20%+ annually; Indian-American security professionals face both a threat landscape and a career tailwind.",
    "tags": ["cybersecurity", "five-eyes", "ai-threats", "india-it", "tcs", "infosys", "nikesh-arora", "cert-in"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/five-eyes-intelligence-alliance-warns-that-new-ai-models-pose-urgent-cyber-risk-2026-06-23/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/23/world/ai-five-eyes-warning-cyber-threat-intl-hnk/"},
        {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/news-five-eyes-ai-cyberattacks/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/23/business/ai-could-fuel-severe-cyberattacks-against-governments-businesses-within-months-five-eyes-spy-agencies-warn/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5380603/pexels-photo-5380603.jpeg",
    "image_caption": "Hacker working at a computer terminal, illustrating the AI-accelerated cyber threat landscape",
    "image_attribution": "Pexels",
    "body": art3_body
}


# ─────────────────────────────────────────────
# Validate and insert
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

# Validate before inserting
for art in articles:
    h = art["headline"]
    assert 20 <= len(h) <= 200, f"Headline length {len(h)} out of range: {h[:50]}"
    assert len(art["subheadline"]) >= 15, f"Subheadline too short for {h[:50]}"
    assert len(art["body"].split()) >= 400, f"Body too short for {h[:50]}: {len(art['body'].split())} words"
    assert art["category"] == "technology", f"Wrong category for {h[:50]}"
    assert art["status"] == "review", f"Wrong status for {h[:50]}"
    assert art.get("is_editorial") == False, f"is_editorial must be False for {h[:50]}"
    assert art["image_url"].startswith("https://"), f"Image URL invalid for {h[:50]}"
    assert art.get("image_caption"), f"Missing image_caption for {h[:50]}"
    assert art.get("image_attribution"), f"Missing image_attribution for {h[:50]}"
    assert art.get("vertical"), f"Missing vertical for {h[:50]}"
    assert art.get("diaspora_angle"), f"Missing diaspora_angle for {h[:50]}"
    sources = json.loads(art["sources"])
    assert len(sources) >= 2, f"Need ≥2 sources for {h[:50]}"
    print(f"✓ Validated: {h[:80]}... ({len(art['body'].split())} words)")

print()

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
