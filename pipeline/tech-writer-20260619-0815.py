#!/usr/bin/env python3
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
    {
        "id": str(uuid.uuid4()),
        "headline": "The Men Who Run Microsoft and Google Just Bought a Piece of Lord's. The Buyer's List Reads Like an NRI Yearbook.",
        "subheadline": "A consortium led by Palo Alto Networks' Nikesh Arora — with Satya Nadella, Sundar Pichai and Shantanu Narayen — paid roughly £195 million for 49% of London Spirit, outbidding an IPL billionaire.",
        "slug": make_slug("london-spirit-the-hundred-nikesh-arora-nadella-pichai-narayen-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Four of the most powerful Indian-origin executives in global tech just turned their personal wealth toward cricket at Lord's — a vivid sign of where diaspora capital and cultural identity are converging.",
        "tags": ["indian-tech", "silicon-valley", "cricket", "nikesh-arora", "satya-nadella", "sundar-pichai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Cricbuzz", "url": "https://m.cricbuzz.com/cricket-news/133291/microsft-head-google-ceo-til-vc-in-consortium-that-bags-london-spirit"},
            {"name": "TechRadar", "url": "https://www.techradar.com/pro/the-ceos-of-microsoft-and-alphabet-have-bought-part-of-the-london-hundred-cricket-franchise"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/sundar-pichai-satya-nadella-and-other-tech-ceos-bid-for-london-based-cricket-team-report.html"},
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg/330px-Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Palo Alto Networks CEO Nikesh Arora, who led the consortium that bought a 49% stake in London Spirit.",
        "image_attribution": "Wikimedia Commons",
        "body": """The roster of buyers who walked away with London Spirit this week could double as a guest list for a Diwali party in Atherton. Nikesh Arora, the IIT-BHU graduate who runs Palo Alto Networks. Satya Nadella of Microsoft. Sundar Pichai of Alphabet. Shantanu Narayen of Adobe. Together with media tycoon Satyan Gajwani and Silver Lake's Egon Durban, they form an eleven-strong group that paid a valuation of roughly £295 million — about £195 million for the 49% stake the England and Wales Cricket Board put up — to co-own one of the eight franchises in The Hundred, English cricket's 100-ball competition.

That they bought the side that plays out of Lord's, the sport's spiritual home, is the part worth pausing on.

### A four-hour auction, and an IPL billionaire left behind

The consortium, formally called Cricket Investor Holdings Limited and led by Arora, was initially considered a rank outsider. It ended up staving off Sanjiv Goenka, the Kolkata industrialist who owns the Lucknow Super Giants in the IPL and the Durban Super Giants in South Africa's SA20. Goenka had pursued the Lord's-based franchise hard before giving up after an online auction that ran nearly four hours, eventually landing Manchester Originals instead for a little over £100 million — roughly half what London Spirit fetched.

The Marylebone Cricket Club, which keeps the other 51% of the franchise, welcomed the buyers warmly. "It's with great pleasure that I am able to announce that Cricket Investor Holdings Limited, a consortium led by Nikesh Arora, will be our new partner and co-owners of the London Spirit franchise," said MCC chair Mark Nicholas.

### Not the first cricket cheque these men have written

For Nadella and Narayen, this is familiar ground. Both are investors in Major League Cricket in the United States; Nadella co-owns the Seattle Orcas, and is well known for slipping cricket metaphors into Microsoft keynotes. Pichai, who grew up in Chennai watching the game, is a self-described avid fan. The diaspora's footprint in cricket ownership is now hard to miss: India's richest man, Mukesh Ambani, snapped up the stake in the other London franchise, the Oval Invincibles, and Indian-American entrepreneur Sanjay Govil took a piece of Welsh Fire.

### Why an NRI in New Jersey should care

It is tempting to read this as billionaires buying a toy. It is more interesting than that. For the Indian diaspora, the deal sits at the intersection of two things that rarely line up so neatly — the community's outsized command of global technology, and its inherited love of a sport that the homeland turned into a financial juggernaut. The men who run the companies where tens of thousands of H-1B engineers report to work are now also custodians of a slice of cricket at Lord's. The capital that the diaspora has accumulated in Silicon Valley is flowing back into the culture it came from.

There is a practical dimension too. The Hundred has drawn more than two million spectators since 2021 and is explicitly courting younger, family audiences — the exact demographic of second-generation desi families in London, Toronto and the Bay Area who grew up bilingual in cricket and Premier League football. Major League Cricket's growth in the US, backed by some of these same investors, has already given American-raised desi kids a local league to follow. A franchise at Lord's extends that bridge across the Atlantic.

### What's next

The ECB will sell its remaining teams — Trent Rockets, Northern Superchargers and Southern Braves — in the coming days, with Goenka and other IPL owners including the Ambanis, the Marans of SunRisers Hyderabad and the GMR Group of Delhi Capitals all circling. Expect more Indian and diaspora money to land. Whether these tech owners run London Spirit as a passion project or as the kind of data-driven, fan-engagement operation their day jobs would suggest is the question worth watching. Either way, the next time an NRI family in Edison or Hounslow turns on a Hundred match, the team batting at Lord's will be partly theirs."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Adobe Is Giving Its AI Away for Free. Shantanu Narayen Is Betting the Crowd Comes Back to Pay.",
        "subheadline": "On its Q2 call, Adobe paused Creative Cloud price hikes and pushed free versions of its AI tools — freemium users jumped to 90 million — and raised full-year guidance even as the strategy squeezes near-term revenue.",
        "slug": make_slug("adobe-q2-fy26-shantanu-narayen-freemium-firefly-ai-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Adobe under Indian-origin CEO Shantanu Narayen is a core holding for many NRI investors and a major employer of Indian engineers — its bet to give AI away and chase scale over margin is a wager the whole diaspora-heavy software sector is now making.",
        "tags": ["adobe", "shantanu-narayen", "ai", "firefly", "indian-tech", "markets"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/adobe-inc-adbe-accepts-a-tradeoff-to-drive-business-growth-1456789/"},
            {"name": "SQ Magazine", "url": "https://sqmagazine.co.uk/adobe-statistics/"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/news/dow-jones/adobe-ceo-to-depart-as-ai-boosts-sales-update"},
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg/330px-Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "image_caption": "Adobe chairman and CEO Shantanu Narayen, who is steering the company through its AI transition.",
        "image_attribution": "Wikimedia Commons",
        "body": """Software companies are supposed to guard their crown jewels and charge more for them every year. On its fiscal second-quarter earnings call on June 11, Adobe did close to the opposite. Chief executive Shantanu Narayen told investors the company is pausing price increases on its Creative Cloud suite and pushing free, "freemium" versions of its AI products into as many hands as possible. The early numbers are striking: freemium monthly active users climbed to more than 90 million from 50 million, and combined Acrobat and Express monthly users rose past 850 million from 700 million a year earlier.

This will dent revenue in the short run. Narayen is betting it builds a far larger base of people who eventually pay.

### The wager: scale now, margin later

The logic is the same one that built every consumer-internet giant — get the product into enough hands and a slice will convert to paying customers. For Adobe, the urgency is specific. Generative AI has made it dramatically easier to produce images, video and design without Adobe's expensive tools, and many of the buzziest new creative models come from competitors, including Google's Veo line. Rather than defend a shrinking moat with higher prices, Adobe is trying to widen the top of the funnel.

It is working well enough that management raised full-year guidance. Adobe now expects fiscal 2026 revenue of $26.5 billion to $26.6 billion, up from a prior range of $25.9 billion to $26.1 billion. Annual recurring revenue from its AI-first products, anchored by the Firefly generative suite, has more than tripled year over year off a base that crossed $250 million.

### Why this matters to the diaspora

Adobe is not an abstract ticker for the Indian community. It is run by Shantanu Narayen, the Hyderabad-born, Osmania University-trained engineer who has led the company since 2007 and is one of the most prominent Indian-origin CEOs in the world. It employs large numbers of Indian engineers across its US offices and its sizable Bengaluru and Noida operations. And it is a staple in the portfolios of NRI investors who like big, profitable software names.

For those investors, the freemium pivot is the thing to watch closely. Adobe's appeal has always been its margins — a roughly 89% gross margin and 30% net margin in 2025, far above Salesforce's. Giving products away pressures exactly that. The question is whether the 90 million freemium users become a conversion engine or a costly audience that never pays.

### The succession overhang

There is a second storyline NRI investors should not ignore. Narayen announced earlier this year that he will step down as CEO once a successor is found, moving to chair of the board. That transition lands at the worst possible moment for a clean handoff — mid-way through an AI shift that is simultaneously cannibalising Adobe's legacy stock-imagery business and powering its fastest-growing one. Analysts have flagged a "leadership vacuum premium," the discount markets apply when a seasoned operator leaves during disruption.

For the Indian-American engineer at a competitor wondering whether design software is a safe long-term career, and for the NRI investor deciding whether to hold ADBE through the transition, the same uncertainty applies. Adobe is making a credible bet that scale beats margin in the AI era. Whether Narayen's successor inherits a bigger franchise or a thinner one is the story the next several quarters will tell.

### What's next

Watch the conversion rate. Freemium user growth is easy to celebrate; turning even a modest fraction of 90 million users into paying subscribers is the harder, more important number. Watch capital spending too — Adobe rents its AI compute from Microsoft Azure and Amazon Web Services rather than building it, which keeps costs low but leaves it dependent on two companies that sell competing tools. And watch for the successor announcement, which will tell investors more about Adobe's next decade than any single quarter's revenue line."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Razorpay Just Filed Quietly for Its IPO. India's Payment Giants Are Lining Up to Cash Out — and NRIs Want In.",
        "subheadline": "The Bengaluru fintech confidentially submitted its draft prospectus to SEBI as UPI volumes hit record highs, joining a 2026 pipeline that already includes the NSE and a wave of consumer-tech listings.",
        "slug": make_slug("razorpay-confidential-ipo-sebi-india-fintech-upi-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "A generation of Indian fintech unicorns NRIs read about for years is finally heading to public markets — turning private bets into something diaspora investors can actually own, if they understand the cross-border rules.",
        "tags": ["razorpay", "fintech", "ipo", "upi", "indian-tech", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Entrackr", "url": "https://entrackr.com/news/razorpay-confidentially-files-drhp-with-sebi-for-ipo"},
            {"name": "Inc42 Indian Unicorn Tracker", "url": "https://inc42.com/features/indian-unicorn-tracker-funding-investors-revenue/"},
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935039/pexels-photo-12935039.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A customer makes a digital payment at a point-of-sale terminal, the kind of transaction Razorpay processes.",
        "image_attribution": "Pexels",
        "body": """Razorpay has quietly told India's market regulator it wants to go public. The Bengaluru payments company confidentially filed its draft red herring prospectus with SEBI this week, choosing the discreet route that lets a company begin the IPO process without immediately disclosing its financials to the public. The timing is no accident. India's digital-payment rails are running hotter than ever — PhonePe, Google Pay and Paytm all posted record UPI volumes in May — and the companies built on top of those rails are racing to list while investor appetite is strong.

Razorpay, valued at around $7.5 billion in the last private round that ranked it among India's most valuable unicorns alongside Zerodha and Lenskart, is now one of the headline names in a crowded 2026 IPO pipeline.

### A pipeline NRIs have been waiting on for years

For the diaspora, this is the moment the theory becomes tradable. NRIs have spent a decade reading about Razorpay, Zerodha, PhonePe and Meesho without any clean way to own them — these were private companies, accessible only to venture funds and a handful of well-connected angels. That wall is now coming down. India's National Stock Exchange itself finally filed to go public; Razorpay is in the queue; and the broader market saw a flurry of activity, with Meesho moving to acquire Kirana Club in a ₹202 crore deal and Ather Energy's board clearing a ₹2,500 crore raise.

The fintech logic underneath is real, not hype. UPI has become the plumbing of Indian commerce, and Razorpay sits at the merchant layer — processing payments, lending, payroll and banking services for businesses. Record UPI volumes flow, in part, through companies like it.

### The fine print that trips up diaspora investors

Here is where enthusiasm needs a cold read. Buying into an Indian IPO from abroad is not the same as clicking "buy" on a US brokerage. NRIs can invest through the NRE/NRO account framework and the portfolio investment route, but the mechanics — designated bank accounts, repatriation rules, tax treatment of capital gains, and the documentation each broker demands — are materially more involved than a domestic retail bid. The grey market, where shares trade unofficially before listing, can also send misleading signals; India's first insurtech IPO of 2026, Turtlemint, opened this week to a grey-market premium that was actually telling investors to slow down.

Confidential filing adds its own wrinkle. Because the prospectus is not yet public, the diaspora investor eyeing Razorpay has less to go on than usual — no pricing band, limited financial detail — until the company chooses to lift the veil. That argues for patience over FOMO.

### Why the structural story still favors the diaspora

Step back from the single name and the trend is clearly in the diaspora's favor. Bengaluru remains India's unicorn capital, with the city anchoring three of the four new unicorns minted in 2026, including the AI startup Sarvam. The IPO wave means the value these companies created in private markets is finally being unlocked in public ones — and unlike a decade ago, an NRI in London or San Jose can participate in that unlocking rather than watch from the sidelines.

### What's next

Watch for Razorpay to make its filing public, which will reveal the financials and a pricing range — the first real basis for a decision. Watch the NSE listing, which will be the bellwether for how much appetite the market truly has. And before placing any bid from abroad, NRIs should confirm the account structure and tax implications with their broker; the difference between a clean cross-border investment and a tangled one is almost always in the paperwork, not the pick."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)} of {len(articles)} articles inserted.")
