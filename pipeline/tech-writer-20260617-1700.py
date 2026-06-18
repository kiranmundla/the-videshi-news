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

zepto_body = """Zepto wants to be the first pure quick-commerce company on an Indian stock exchange. The updated prospectus it filed with India's market regulator on June 8 makes the ambition concrete: a fresh issue of roughly ₹8,010 crore, an offer-for-sale of about 113 million shares, and a target listing as early as July. What the document does not advertise quite so loudly is the valuation. At a reported $7 billion, Zepto is asking the market to price it below rival Swiggy — and that gap, more than the headline fundraise, is the real story.

## The numbers behind the dash

Zepto's growth is not in doubt. Revenue from operations climbed nearly five-fold, from ₹4,454 crore in FY24 to ₹22,623 crore in FY26. The problem sits one line down. Losses widened almost as fast, from ₹1,249 crore to ₹5,905 crore over the same stretch. The company now runs roughly 1,139 dark stores — the small, unglamorous fulfilment warehouses that make ten-minute delivery possible — and a chunk of the IPO proceeds will go toward building more of them and paying the rent on the ones it already has.

That is the quick-commerce bargain in a sentence: spend relentlessly on density now, in the belief that India's metros will eventually deliver the order frequency that turns a dark store profitable. Zepto's founders, Aadit Palicha and Kaivalya Vohra, are not selling a single share in the offering. The exits belong to early backers — Nexus Venture Partners, US-based Contrary Capital, Dubai's Razor Capital, and Kaiser Permanente's funds — who are using the OFS to take money off the table.

## Why the valuation cut matters

By market value, Swiggy is worth about $7.8 billion and Zomato's parent, Eternal, roughly $26.9 billion. For Zepto to come to market asking for less than Swiggy is a signal that the froth of 2024, when private rounds valued the company at $5 billion and climbing, has given way to a more sober public-market reality. Bankers reading the prospectus noted something unusual: Zepto disclosed granular unit economics — including annual transacting users and customer-acquisition detail — that most Indian startups bury. That candour is a tell. A company willing to be judged on those metrics is betting the public market will reward transparency over hype.

## The diaspora angle

For the Indian-American investor, Zepto is the cleanest available wager on a behaviour that has no real US equivalent. Ten-minute grocery delivery, at scale, across dozens of Indian cities, is a uniquely Indian phenomenon — built on cheap last-mile labour, dense urban geography, and a UPI payments rail that makes a ₹150 order frictionless. An NRI in New Jersey who watches family in Mumbai order chai, vegetables, and phone chargers in the time it takes to boil water already understands the product better than most Wall Street analysts.

But understanding the product is not the same as understanding the stock. Zepto will list only on Indian exchanges, which means diaspora investors face the usual friction: a US resident generally cannot buy an Indian IPO directly without an NRE/NRO account and a portfolio investment route, and OCI-card holders have their own restrictions. The practical exposure for most NRIs comes later and indirectly — through India-focused ETFs that may eventually hold the stock, or by watching how Zepto's debut reprices Swiggy and Eternal, both already trading.

There is a sharper reason to pay attention. Zepto's listing is a referendum on whether the cash-burn model that venture capital subsidised for years can survive contact with public shareholders who want a path to profit. If Zepto lists well and holds, it validates an entire generation of Indian consumer-tech bets that diaspora money helped fund. If it stumbles, it tells every NRI angel investor still writing checks into Bengaluru startups that the era of growth-at-any-cost is genuinely over. Either way, the July tape will be worth reading.

## What's next

Watch three things. First, the final price band — if Zepto trims the $7 billion ask further before the issue opens, that is the market, not the company, setting the terms. Second, the grey-market premium in the days before listing, an imperfect but real gauge of retail appetite. Third, how Swiggy and Eternal shares move on listing day; a strong Zepto debut tends to lift the whole basket, a weak one drags it. For diaspora investors tracking India's consumer story, this is the most important IPO of the summer."""

crypto_body = """India has spent years sending crypto two contradictory signals: a punishing 30% tax on trading gains that says "go away," and a conspicuous absence of any actual ban that says "stay." This month the contradiction is finally being forced toward resolution — and the resolution looks less like a verdict on Bitcoin than a blueprint for state-controlled digital money.

## Two tracks, one direction

On the private-crypto track, Coinbase quietly switched on rupee trading in India in late May, letting users deposit and withdraw rupees through India's instant-payment rail and trade spot assets and perpetual futures. The US exchange had pulled out of India in 2023; its return, after registering with the Financial Intelligence Unit, is a bet that the country's enormous base of developers and traders is too large to ignore — even at a 30% tax rate that remains among the world's harshest. India's government, under pressure from a Supreme Court that has openly criticised the regulatory vacuum, is preparing a discussion paper drawing on IMF and Financial Stability Board frameworks.

On the public-money track, the Reserve Bank of India is moving faster and with far more conviction. Its 2025–26 annual report repositions the digital rupee, the e₹, from a retail curiosity into what the central bank frankly calls strategic infrastructure — a hedge against dependence on Western payment plumbing.

## The sovereignty play

The detail in the RBI's plans is what makes this more than a press release. Programmable welfare is already live: pilots in Gujarat, Puducherry, and Chandigarh have deployed e₹ tokens for food-subsidy distribution that can be spent only on eligible goods at approved shops, designed to stamp out the leakage that has plagued Indian welfare for decades. The central bank has signed a memorandum with Singapore's monetary authority and opened talks with the UAE's central bank to run cross-border digital-currency pilots, and it is participating in international experiments on settling foreign exchange and embedding anti-money-laundering checks directly into transactions.

Read together, the message is clear. India is not especially interested in making it easy to speculate on Bitcoin. It is intensely interested in owning the rails on which money moves — domestically through UPI and the e₹, and across borders through corridors that route around SWIFT and the dollar.

## Why the diaspora should care

This is, quietly, a remittance story — and remittances are the diaspora's most direct financial tie to India. Indians abroad send home more than $100 billion a year, and the India–UAE corridor alone moves over $20 billion. A working cross-border digital-rupee link between Mumbai and Abu Dhabi could, in time, settle those transfers faster and cheaper than the correspondent-banking chains NRIs use today, where fees and FX spreads quietly skim a few percent off every transfer.

For the diaspora's crypto holders, the picture is more cautionary. The same FIU framework that welcomed Coinbase back also tightened the screws: mandatory liveness-detection KYC, geo-tagging of users by latitude and longitude, outright prohibition of mixing services, and heightened scrutiny of peer-to-peer transfers. An NRI who casually moves crypto between an Indian exchange and a self-custody wallet should assume those transactions are now visible, logged, and taxable. The 30% gains tax and the 1% transaction levy apply regardless of where the trader sits, and India's view that crypto activity without transparency is "unacceptable" leaves little room for the grey-area behaviour many diaspora traders grew used to.

## What's next

The discussion paper is the document to watch. If it opens the floor to public comment — as reports suggest it might — diaspora industry groups and NRI investors will have a rare opening to shape the rules rather than merely react to them. The likeliest outcome is not a ban and not a free market, but a tightly regulated regime where private crypto is tolerated and taxed while the state pours its real ambition into the digital rupee. For Indians abroad, the upside lives in cheaper remittances and programmable cross-border settlement; the risk lives in assuming the old, lightly-watched ways of moving crypto across the India line still work. They increasingly do not."""

space_body = """India's space programme used to be a single acronym: ISRO. This month, at the India Space Congress in Delhi and a deep-tech showcase in Nice, France, a different picture came into focus — one where the state agency is becoming a customer and a referee rather than the only player, and where a thicket of private startups is being deliberately funded to take its place at the cutting edge.

## Money follows the mission

The clearest signal came in cash. India's space regulator awarded Bengaluru-based SatSure a ₹246 million ($2.6 million) grant to build AI-powered Earth-observation models — systems that read satellite and drone imagery to track monsoons, farmland, and urban sprawl with an accuracy that global models, trained on other geographies, routinely miss. The grant is part of a broader push: India has thrown open its space sector to private firms and seeded a ₹1,000 crore fund to help startups scale.

Meanwhile, at the Bharat Innovates 2026 summit in France, IIT Madras and its startups — including rocket-maker Agnikul Cosmos and hyperloop venture TuTr — signed roughly $100 million in commercial agreements with mostly French partners. A new Bharat Innovates Fund was set up to channel patient capital into deep-tech ventures, the kind of long-horizon money that India's startup scene has historically lacked.

## From launches to layers

What ties the Earth-observation grant and the rocket startups together is a strategic word that keeps recurring in Indian policy circles: sovereignty. India does not just want to launch satellites; it wants to own the full stack — the launch vehicles, the constellations, and the AI models that turn raw imagery into decisions. SatSure's chief technology officer framed it precisely: Earth observation is shifting "from project-specific analytics to reusable intelligence infrastructure." That is the same logic driving India's semiconductor and AI ambitions, applied to orbit.

The geopolitics help. As the world grows wary of leaning on any single supplier for critical technology, a democratic, English-speaking country with low-cost engineering and a proven launch record becomes an attractive partner. The interest from France, Thailand, and Taiwan at this month's events was not ceremonial; it reflected a genuine search for alternatives to the established space powers.

## The diaspora angle

For the Indian diaspora, the space story has shifted from a source of pride to a source of opportunity. For decades, an NRI's relationship with ISRO was emotional — the Mars Orbiter, Chandrayaan-3's south-pole landing, the satisfaction of watching the home country punch above its weight on a shoestring budget. That emotional tie is now acquiring a financial dimension.

A generation of Indian space startups will need capital, and a meaningful share of it is likely to come from diaspora pockets — the NRI venture investors, the Indian-origin engineers at SpaceX and Blue Origin weighing whether to back ventures back home, the family offices looking for the next frontier after fintech and SaaS. India's largest GPU operator is already heading for a public listing, and as space startups mature, NRI-focused funds and eventually Indian IPOs will offer ways in. The deep-tech founders pitching in Nice were, in many cases, looking precisely at this audience.

There is a talent dimension too. The same Indian engineers who left for Houston, Seattle, and the Bay Area because India had no private space industry now have a reason to look back. A return-to-India calculation that once made no sense for an aerospace specialist is starting to — not for everyone, but for enough to matter. For the diaspora professional who spent a career on someone else's rockets, the idea of building India's own is no longer a fantasy.

## What's next

Watch the commercialisation pipeline. The MoUs signed in France are, for now, promises; the test is how many convert into shipped products and recurring revenue over the next year. Watch ISRO's own return-to-flight cadence, which has been quieter than usual. And watch the funding rounds — when an Indian Earth-observation or launch startup raises a large round with visible diaspora backing, that will be the clearest sign that India's space sector has graduated from national symbol to investable asset class. For Indians abroad, the sky is, for the first time, a place to put money as well as pride."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Zepto Wants to Be India's First Pure Quick-Commerce IPO. The Valuation Tells the Real Story.",
        "subheadline": "The ten-minute delivery giant filed to raise ₹8,010 crore at a reported $7 billion — below rival Swiggy. For NRI investors, July's listing is a referendum on the cash-burn era.",
        "slug": make_slug("zepto-quick-commerce-ipo-drhp-valuation-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Zepto is the cleanest available bet on a uniquely Indian behaviour NRIs watch family members do daily, and its listing will tell diaspora angel investors whether growth-at-any-cost is finally over.",
        "tags": ["zepto", "ipo", "quick-commerce", "indian-tech", "nri-investors", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint — Zepto IPO updated DRHP", "url": "https://www.livemint.com/market/ipo/zepto-ipo-quick-commerce-firm-files-updated-drhp-aims-to-raise-rs-8010-crore"},
            {"name": "Livemint — Zepto roadshow and financials", "url": "https://www.livemint.com/market/stock-market-news/zepto-roadshow-offers-clues-to-quick-commerce-next-phase"},
            {"name": "Groww — Zepto files U-DRHP with SEBI", "url": "https://groww.in/blog/zepto-files-udrhp-with-sebi"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4480794/pexels-photo-4480794.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A worker moves through a fulfilment warehouse aisle, the dark-store model that powers ten-minute delivery",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": zepto_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Done Pretending It Will Ban Crypto. It Has a Bigger Plan: Owning the Money Itself.",
        "subheadline": "Coinbase just switched on rupee trading while the RBI repositions the digital rupee as strategic infrastructure. For the diaspora, the real story is cheaper remittances — and far tighter surveillance.",
        "slug": make_slug("india-crypto-regulation-digital-rupee-coinbase-nri-remittances"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "A cross-border digital-rupee corridor could cut the cost of the $100B+ NRIs remit home each year, even as tighter KYC and geo-tagging make diaspora crypto moves fully visible and taxable.",
        "tags": ["crypto", "digital-rupee", "coinbase", "rbi", "fintech", "nri", "remittances"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Coinbase offers trading using Indian rupee", "url": "https://www.reuters.com/technology/coinbase-offers-trading-using-indian-rupee"},
            {"name": "CoinMarketCap — India's Crypto Regulation Policy", "url": "https://coinmarketcap.com/community/articles/indias-crypto-regulation-policy-coming-in-june"},
            {"name": "Mondaq — FinTales: Crypto Clampdown And Privacy Push", "url": "https://www.mondaq.com/india/fin-tech/fintales-february-2026-crypto-clampdown-and-privacy-push"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8369695/pexels-photo-8369695.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A pile of gold and silver cryptocurrency coins, the asset class India taxes heavily but has declined to ban",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": crypto_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Space Programme Is No Longer Just ISRO. For the Diaspora, That Changes the Bet.",
        "subheadline": "A wave of state grants and $100 million in deep-tech deals signed in France point to a privatised space sector — and a new reason for NRI capital and engineers to look home.",
        "slug": make_slug("india-private-space-tech-startups-earth-observation-nri-capital"),
        "category": "technology",
        "vertical": "deep-tech",
        "diaspora_angle": "India's space story is shifting from a source of NRI pride to a source of NRI opportunity, with diaspora capital and returning engineers poised to fund the next generation of launch and Earth-observation startups.",
        "tags": ["space-tech", "isro", "satsure", "agnikul", "deep-tech", "startups", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — SatSure bags $2.6M grant for Earth observation", "url": "https://www.reuters.com/technology/space/indias-satsure-bags-26-million-grant-build-ai-powered-earth-observation-models"},
            {"name": "The Hindu BusinessLine — IIT-M startups sign $100M MoUs", "url": "https://www.thehindubusinessline.com/info-tech/agnikul-hyperloop-and-other-iit-m-start-ups-sign-mous-of-100-million-at-bharat-innovates-2026"},
            {"name": "IANS Live — Space technology is one of India's strengths", "url": "https://ianslive.in/space-technology-is-one-of-indias-strengths-global-industry-leaders"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/586056/pexels-photo-586056.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A satellite glides over Earth, the kind of Earth-observation infrastructure India is funding private startups to build",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": space_body
    }
]

# word count check
for art in articles:
    wc = len(art["body"].split())
    print(f"  words={wc} | {art['slug']}")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
