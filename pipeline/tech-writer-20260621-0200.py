#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

razorpay_body = """Razorpay has filed confidentially for an initial public offering, and the number that matters is not the one the company wants you to look at. The Bengaluru payments firm is targeting a raise of roughly $600-700 million at a valuation of $5-6 billion. Four years ago, in the froth of 2021, private investors valued it at $7.5 billion. The IPO, in other words, is a markdown dressed up as a milestone.

That gap tells the story of an entire generation of Indian fintech — and it is a story Indian Americans have a direct stake in, whether they know it or not.

## The reverse-flip tax

Razorpay was, until recently, an American company. Like many Indian startups chasing Silicon Valley capital, it had incorporated its parent entity in the United States, where Y Combinator, Tiger Global, and Lightspeed could write checks without wrestling with Indian securities law. To list in Mumbai, it had to come home — merging its US parent into its Indian arm in a "reverse flip" that cost it around $150 million in taxes.

That single line item helps explain why Razorpay posted a consolidated net loss of ₹1,209 crore for the year ended March 2025, even as operating revenue jumped 65% to ₹3,783 crore. The business is healthier than the loss suggests; the loss is largely the price of repatriation plus a one-time ESOP charge.

For the diaspora, the reverse flip is the quiet headline. A decade of Indian founders were told to build in Delaware and raise in dollars. Now the smart money is unwinding that structure to chase Indian retail investors and Indian listing multiples. The career advice that sent thousands of NRI engineers and operators into US-domiciled Indian startups is being rewritten in real time.

## Why an NRI should read the prospectus

Razorpay processes an annualised payment volume north of $180 billion and serves a majority of India's unicorns. It is, in effect, the plumbing under India's digital economy — the layer that sits between a merchant and the UPI rails that now handle 23 billion transactions a month. An NRI who sends money home, runs a side business with Indian customers, or invests through a GIFT City brokerage is already touching infrastructure Razorpay competes to own.

The confidential filing route — which lets a company keep its financials private until just before launch — is itself a tell. It signals a firm testing investor appetite in a choppy market rather than barreling toward a fixed date. Razorpay joins Zepto, PhonePe, Groww, and a pipeline of more than 40 startups eyeing Dalal Street over the next 18 months. Collectively, 2026 could be India's largest startup-IPO year on record.

## The valuation reset is the point

The instinct is to read the cut from $7.5 billion to $5-6 billion as failure. It is closer to discipline. The 2021 cohort raised at multiples that assumed growth would never slow and capital would never get expensive. Both assumptions broke. The startups now reaching public markets are the ones that fixed unit economics, chased profitability, and accepted a humbler price tag in exchange for liquidity.

For diaspora investors, that reset cuts two ways. A lower entry valuation can mean a more honest one — less of the air that vaporised in the post-2021 correction. But it also means the easy money has already been made by the early backers cashing out in the offer-for-sale. Razorpay has raised roughly $740 million from the likes of Y Combinator, Tiger Global, Peak XV, and GIC; an IPO is partly their exit.

## What's next

Watch three things. First, the final price band when the red-herring prospectus drops — it will reveal whether public investors accept even the reset valuation. Second, the offer-for-sale split, which shows how much of the deal is fresh capital for growth versus early backers heading for the door. Third, whether GIFT City and improving NRI-investment channels make it realistic for an Indian American to actually buy in at listing, rather than watching from the sidelines as domestic institutions soak up the allocation.

Razorpay's debut will not just price one company. It will set the tone for the dozens of Indian tech names lining up behind it — and tell the diaspora whether the homecoming trade is worth making."""

ather_body = """Ather Energy's stock fell more than 5% the week its board approved a ₹2,500 crore fundraise. That reaction looks backwards until you read the line CEO Tarun Mehta posted on X the same day: "We have crossed 90% utilisation, and will have to try and find ways to go above 100% in the coming weeks." Ather is not raising money because it is failing. It is raising money because it has run out of room to grow — and the market is nervous about the dilution that fixing that will require.

For the Indian American watching India's electric-vehicle story from a distance, Ather's scramble is a useful lens on a market that is finally past the hype and into the hard part.

## The mechanics of the raise

This is Ather's first major capital raise since it listed in May 2025. The board approved a two-part structure: up to ₹1,500 crore through a qualified institutional placement (QIP), and up to ₹1,000 crore through a flexible window covering preferential allotment, a rights issue, or foreign-currency convertible bonds (FCCBs). A dedicated fundraising committee has been formed, and the QIP needs shareholder approval through a postal-ballot e-vote.

The money is earmarked for research and development, marketing, and paying down borrowings. Banks including Nomura, HSBC Securities, and Axis Capital have been mentioned in early discussions. Ather is expected to launch the process as soon as July.

## Running the factory hot

The strategic story sits in that utilisation number. Ather's Hosur plant is running at 90-95% of its roughly 35,000-units-a-month capacity. A company maxing out its lines either turns away demand or builds more capacity, and Ather is choosing the latter — aggressively. It is putting more than ₹2,000 crore into a new 98-acre facility at AURIC City in Bidkin, Maharashtra, whose first phase alone is meant to add 500,000 units of annual capacity.

Behind the expansion is a bet on going down-market. Ather has mostly sold premium and mass-premium scooters. Its coming EL platform targets the ₹1-1.25 lakh bracket — the segment that accounts for nearly half of India's electric two-wheeler market and where rivals Ola Electric, TVS, and Bajaj already fight on price. Mehta has called EL the company's key growth driver for FY27 and FY28.

## Why the diaspora should care

Plenty of NRIs hold Indian equities through brokerage accounts and GIFT City channels, and Ather is now a listed name they can actually own — a rare pure-play bet on Indian EV manufacturing rather than a sprawling conglomerate. The QIP and FCCB structure is worth understanding precisely because it touches foreign capital: FCCBs let Ather raise debt denominated in dollars that converts to equity later, tapping cheaper global pools and, potentially, diaspora-linked institutional money.

There is a homecoming angle too. India's EV two-wheeler market is the kind of capital-and-engineering problem that pulls expatriate talent back — supply-chain leaders, battery engineers, and operators who cut their teeth at Tesla, Rivian, or US battery startups. Ather's expansion is a hiring signal as much as a financing one.

## The margin problem nobody escapes

The uncomfortable backdrop is cost. Lithium prices remain more than double historical levels, and battery-cell costs have climbed 30-50% in recent quarters. Every EV maker, Ather included, is absorbing that through a mix of cost-cutting and selective price hikes, and margins are expected to stay under pressure in the near term. Ather currently ranks as India's third-largest electric two-wheeler maker by Vahan registrations — strong, but not dominant, in a market where scale decides who survives.

## What's next

The immediate milestones are procedural: the shareholder e-vote on the QIP, then the pricing and investor allocation, expected to begin as early as July. After that, watch the EL platform launch and the AURIC City ramp — the two things the new capital is meant to fund. If Ather can hold its premium brand while winning the mass market without torching its margins, the dilution investors fear this week will look cheap. If it cannot, the raise will have bought time rather than growth. For diaspora investors deciding whether India's EV decade is investable, Ather is the cleanest test case on the board."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Razorpay Filed for Its IPO at a $2 Billion Discount. The Markdown Is the Story.",
        "subheadline": "India's biggest payments unicorn is going public at $5-6 billion, well below its 2021 peak — and the reverse-flip home tells the diaspora how the startup playbook has changed.",
        "slug": make_slug("razorpay-ipo-confidential-filing-valuation-reset-reverse-flip-nri-fintech"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs who send money home, run India-facing businesses, or invest via GIFT City have a direct stake in Razorpay's listing — and the reverse-flip from the US rewrites the build-in-Delaware advice that guided a generation of diaspora founders.",
        "tags": ["razorpay", "indian-tech", "fintech", "ipo", "nri-investors", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-razorpay-files-ipo-papers-confidentially-2026-06-15/"},
            {"name": "Inc42 — Indian Startup IPO Tracker 2026", "url": "https://inc42.com/features/indian-startup-ipo-tracker/"},
            {"name": "Medianama", "url": "https://www.medianama.com/2026/05/223-razorpay-shareholder-nod-ipo/"},
            {"name": "Entrackr", "url": "https://entrackr.com/news/razorpay-confidentially-files-drhp-with-sebi-for-ipo"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stock-exchange display showing live market data, as India's startups line up for a record IPO year.",
        "image_attribution": "Pexels",
        "body": razorpay_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ather's Stock Fell When It Raised ₹2,500 Crore. The CEO's One-Line Post Explains Why It Shouldn't Have.",
        "subheadline": "India's third-largest electric scooter maker is running its factory at 90% and raising capital to go mass-market — a clean test case for diaspora investors weighing India's EV decade.",
        "slug": make_slug("ather-energy-2500-crore-qip-fundraise-ev-mass-market-nri-investors"),
        "category": "technology",
        "vertical": "ev",
        "diaspora_angle": "Ather is a rare listed pure-play on Indian EV manufacturing that NRIs can actually own, and its FCCB-laced raise taps the foreign capital and returning battery talent that connect Silicon Valley to India's mobility build-out.",
        "tags": ["ather-energy", "ev", "indian-tech", "electric-vehicles", "nri-investors", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inc42 — New-Age Tech Stocks", "url": "https://inc42.com/buzz/new-age-tech-stocks-aequs-nykaa-lead-weekly-gains-ola-electric-ather-slip/"},
            {"name": "TechStory", "url": "https://techstory.in/ather-energy-board-clears-2500-crore-fundraise/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/ather-energy-eyes-fresh-fundraise-a-year-after-ipo-shares-in-focus"},
            {"name": "CEO India Magazine", "url": "https://ceoindiamagazine.com/ather-energy-board-approves-2500-crore-fundraise/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/26708106/pexels-photo-26708106.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Riders on electric scooters in a city — the mass-market segment Ather Energy's new platform is built to reach.",
        "image_attribution": "Pexels",
        "body": ather_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   {art['slug']} — {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
