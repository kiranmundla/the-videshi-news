#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "India's Quietest AI Investor Just Showed Its Hand: Rs 1,003 Crore Across 54 Startups",
        "subheadline": "Info Edge, the firm behind Naukri and an early Zomato backer, carved out its AI and deeptech bets as a separate book for the first time — and was unusually frank about how few have paid off yet.",
        "slug": make_slug("info-edge-ai-deeptech-1003-crore-54-startups-naukri-redstart"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs who treat Info Edge as a proxy for India's internet economy, the disclosure is a rare honest map of where smart Indian capital is betting on AI — and a reminder that the deeptech wave is still years from returns.",
        "tags": ["ai", "deeptech", "indian-tech", "venture-capital", "info-edge"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/info-edge-ai-deeptech-startup-investments-1003-crore"},
            {"name": "StartupTalky", "url": "https://startuptalky.com/news/daily-indian-funding-roundup-key-news-june-23-2026-square-yards-enters-unicorn-club/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7495291/pexels-photo-7495291.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Founders at work in a startup office, the kind of early-stage company Info Edge's deeptech funds back",
        "image_attribution": "Pexels",
        "body": """India's most-watched internet investor spent the last decade letting its results do the talking. Last week it decided to talk.

In a letter to shareholders filed with the National Stock Exchange and the BSE on June 22nd, Info Edge — the Noida company best known for the jobs portal Naukri and as an early backer of Zomato's parent, Eternal — broke out its artificial-intelligence and deeptech investments as a standalone book for the first time. The number: Rs 1,003 crore, roughly $120 million, deployed across 54 startups since 2020. For a firm that usually discloses as little as the rules allow, the gesture was its own kind of signal.

## What the book actually holds

Info Edge runs its startup investing through three vehicles: Redstart Labs, the deeptech-focused Capital 2B, and a trio of Info Edge Ventures funds. The company says it began writing AI and deeptech cheques around 2020 — into robotics, biotech and space tech — well before the global AI frenzy turned those themes into a consensus trade. That timing is the boast buried in the filing: it was early when being early was lonely.

What sets the disclosure apart is its candour about the scoreboard. Rather than dressing up a young portfolio with paper markups, Info Edge was blunt that most of these bets are still in their infancy and that returns, if they come, are years away. In a market where every fund manager now claims an "AI thesis," a public admission that the early scorecard is thin counts as something close to honesty.

## Why a separate book, and why now

Carving the AI and deeptech holdings out of the larger consumer-technology portfolio does two things. It lets shareholders value the speculative, long-horizon bets separately from the cash-generating core — Naukri, the property portal 99acres, the matrimony site Jeevansathi. And it plants a flag: Info Edge wants to be read as a deeptech investor, not merely an internet-classifieds business that got lucky with Zomato and the insurance aggregator PB Fintech.

The move also lands in a week when sovereign AI and deeptech were the loudest themes in Indian venture capital. Sarvam, the language-model startup, became a unicorn days earlier on a $234 million round led by HCLTech. AI-networking firm Upscale AI hit a $2 billion valuation. Against that backdrop, a respected public-market name putting a formal figure on its decade-old deeptech conviction reads as validation that the category has graduated from fringe to mainstream.

## Why an NRI should read past the headline

For the Indian diaspora, Info Edge is more than a stock — it is a barometer. Many NRIs hold it directly or through India-focused funds precisely because it offers exposure to the country's internet economy in one ticker. When such a firm reorganises its reporting to spotlight AI and deeptech, it is telling its shareholders where it expects the next decade of value to come from.

There is a sharper lesson for the Bay Area engineer or the New Jersey founder watching India's startup scene for a re-entry point. Info Edge's willingness to say plainly that the bets have not yet paid is a useful corrective to the hype reaching the diaspora through WhatsApp forwards and LinkedIn victory laps. India's deeptech ambition is real and well-capitalised, but it is also early, illiquid and unproven. The same patient money that waited years for Zomato to mature is now waiting on robotics and space — and even the people writing the cheques are telling you not to expect quick wins.

## What's next

Expect more Indian investors to follow Info Edge in separating their AI books, if only because public markets are starting to reward the disclosure. The harder question is whether the 54 companies in this portfolio produce a breakout that justifies the patience. For now, Info Edge has done something rare in a frothy market: shown its hand, and admitted the cards are still being dealt."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Bengaluru Startup Wants to Build India's Largest Security Operations Centre. Bessemer Just Bet $15 Million on It.",
        "subheadline": "Mitigata raised a Series B less than a year after its last round, betting that AI-driven attacks and a chronic talent shortage have created a 'perfect storm' for Indian enterprises.",
        "slug": make_slug("mitigata-15-million-series-b-bessemer-cyber-resilience-india"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs increasingly hold accounts, run businesses and store data with Indian banks and firms — the institutions Mitigata is racing to protect — making India's cyber-resilience build-out a direct concern for the diaspora, not a distant domestic story.",
        "tags": ["cybersecurity", "indian-tech", "startup-funding", "ai", "bessemer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/mitigata-raises-15-million-in-series-b-led-by-bessemer-venture-partners"},
            {"name": "Indian Startup News", "url": "https://indianstartupnews.com/funding/cybersecurity-startup-mitigata-raises-15-million-to-expand-ai-led-security-platform-12064400"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3949101/pexels-photo-3949101.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A security operations workstation, the kind of monitoring infrastructure cyber-resilience firms run around the clock",
        "image_attribution": "Pexels",
        "body": """The timing was hard to miss. In the same week that a ransomware gang claimed it had lifted Apple and Tesla files from a Tata Electronics plant in India, a Bengaluru startup that sells protection against exactly that kind of disaster closed a fresh round of funding.

Mitigata, a four-year-old cyber-resilience firm, raised about $15 million in a Series B round led by Bessemer Venture Partners, with existing backers Nexus Venture Partners, Titan Capital and WEH Ventures returning. It comes less than a year after the company's $5.9 million Series A in August 2025 — a quick follow-on that says as much about investor anxiety over Indian cybersecurity as it does about Mitigata itself.

## Not a vendor, a full-stack bet

Founded in 2021 by Mohit Anand, Sarthak Dubey, Mayank Morya and Akshit Kaushik, Mitigata pitches itself as a "cyber-resilience" platform rather than a conventional security vendor. The distinction matters to its business model. Instead of selling a single tool, it bundles threat monitoring, risk intelligence, compliance automation, digital forensics, incident response and — unusually — cyber insurance into one system, operating as an insurance intermediary so it can sell both the defence and the financial backstop.

Its product suite leans heavily on AI: Gordon AI, a security co-pilot for detection and response; RELIQ, a proprietary cyber-risk assessment engine; Dranta, a privacy and consent tool; and a consumer-facing exposure monitor. The platform integrates with the heavyweights — Palo Alto Networks, CrowdStrike, SentinelOne — positioning itself as connective tissue rather than a rip-and-replace.

The numbers it claims are growing fast. Mitigata says it serves more than 800 organisations across banking, healthcare, manufacturing, technology and e-commerce, has triaged over a million security incidents in recent months, and is growing at 12-to-15 times year-on-year off a small base.

## The 'perfect storm' thesis

Bessemer's logic is straightforward. "The accelerating number of AI-driven malicious attacks, combined with a severe shortage of cybersecurity talent, has resulted in a perfect storm for Indian enterprises," said partner Pankaj Mitra. India's rapid digitisation — UPI, Aadhaar-linked services, a banking system that runs increasingly online — has expanded the attack surface faster than the country can train people to defend it.

Mitigata plans to spend the money scaling its Security Operations Centre, which it wants to grow into India's largest, doubling headcount across product and engineering, and expanding abroad — starting with the Middle East and North Africa, then Southeast Asia, with "some bit of US exposure" to follow. The founders frame the ambition in national terms, talking about building "sovereign, indigenous AI security infrastructure" from India for the world.

## Why this lands for the diaspora

It is tempting for an NRI to file Indian cybersecurity under "domestic news." That would be a mistake. The diaspora is deeply wired into the institutions Mitigata protects: NRE and NRO bank accounts, family businesses back home, property transactions, health records at Indian hospitals, money moving across borders through Indian fintech rails. When a Tata plant gets breached or an Indian bank's systems are probed, the blast radius reaches Edison and Fremont and Wembley.

There is a professional angle, too. India's cybersecurity talent gap is the mirror image of the diaspora's success story — many of the country's best security engineers left for jobs at American firms. A funded, ambitious local champion like Mitigata, explicitly hiring across AI and engineering, is part of the slow reverse pull that gives India-curious NRI technologists somewhere to land if they want to go home.

## What's next

The cyber-insurance angle is the one to watch. If Mitigata can prove that bundling coverage with active defence lowers actual losses, it has a model that travels well beyond India — into precisely the Gulf and Southeast Asian markets it is targeting. The breach headlines that made this round look prescient are not going away. Neither, increasingly, are the companies built to answer them."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Has a New Real-Estate Unicorn. The Twist Is How It Got There — and Who's Buying.",
        "subheadline": "Square Yards crossed a $1 billion valuation on a Rs 900 crore debt-and-equity round, riding a property platform built in no small part on the wallets of non-resident Indians.",
        "slug": make_slug("square-yards-unicorn-95-million-proptech-nri-real-estate"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Square Yards built its business partly by selling Indian property to NRIs — so its rise to unicorn status is, in a literal sense, a story about where the diaspora's money has been going.",
        "tags": ["proptech", "indian-tech", "startup-funding", "real-estate", "nri-investing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "StartupTalky", "url": "https://startuptalky.com/news/daily-indian-funding-roundup-key-news-june-23-2026-square-yards-enters-unicorn-club/"},
            {"name": "Inc42", "url": "https://inc42.com/startups/indian-startup-ipo-tracker-2026/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5674684/pexels-photo-5674684.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Modern residential apartment towers of the kind sold on India's online property platforms",
        "image_attribution": "Pexels",
        "body": """Most of India's unicorns arrive on a wave of venture froth — a giant equity cheque from a Silicon Valley fund, a valuation that defies the income statement. Square Yards got there a different way, and the difference is the story.

The Gurugram-based real-estate and mortgage platform crossed a $1 billion valuation this week after raising Rs 900 crore — about $95 million — in a round anchored not by a marquee VC but by EAAA Alternatives, a credit manager, with the global corporate-credit firm Muzinich & Co also participating. The structure was a mix of debt and equity, not a pure equity raise. In a market still nursing a hangover from over-funded, cash-burning startups, becoming a unicorn substantially on credit is itself a statement.

## A unicorn with a P&L

The numbers underneath are unusually grown-up for the club Square Yards just joined. Founded by Tanuj Shori and Kanika Gupta, the company reported FY26 revenue of Rs 2,086 crore, up 48% year-on-year, with EBITDA jumping 3.7 times to Rs 176 crore. That is a business throwing off operating profit, not just gross merchandise value — a rarity among Indian proptech names, a category that has produced more cautionary tales than success stories. The company says it plans to raise a further $50-60 million over the next quarter as it lines up a public listing.

## The diaspora is the business model

Here is what makes Square Yards a technology story with the diaspora at its centre rather than its margins: the company built much of its early distribution by selling Indian real estate to non-resident Indians. Its platform, with offices stretching across the Gulf, North America and beyond, was designed around a recurring diaspora behaviour — the NRI who wants to own a flat in Gurugram, Bengaluru or Mumbai but cannot walk a site, vet a builder or chase paperwork from 8,000 miles away.

Square Yards turned that friction into a funnel: virtual tours, digital transactions, mortgage facilitation and post-sale management aimed squarely at buyers who are not in the country. Its move into mortgages and financial services deepened the hook, capturing not just the sale but the financing around it. So when the company crosses a billion-dollar valuation, it is in a real sense monetising a decade of diaspora money flowing back into Indian property.

## Why this matters now

For NRIs, the rise of a credible, profitable, soon-to-be-public platform changes the calculus of buying property back home. The traditional NRI real-estate experience has been a minefield of unreliable brokers, opaque pricing and distant relatives roped in to supervise. A scaled, regulated, listed platform — with the disclosure obligations that an IPO brings — offers something the diaspora has long wanted: a more trustworthy intermediary for one of the largest financial decisions many NRIs make.

There is a caveat worth stating plainly. A slicker platform does not change the underlying risks of Indian real estate — liquidity, regulatory shifts, currency exposure on rupee-denominated assets for someone earning in dollars or pounds. Square Yards makes the transaction smoother; it does not make the asset class safe. The diaspora buyer still has to do the hard thinking about whether an apartment in India belongs in a portfolio built around a life abroad.

## What's next

The planned IPO is the event to watch. A successful listing would give NRIs a way to invest in the diaspora-property trend without buying a single flat — owning the platform rather than the asset. It would also be a test of whether public markets reward a proptech company that grew the unfashionable way: slowly, profitably, and on the strength of customers scattered across the very diaspora now being asked to buy the stock."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
