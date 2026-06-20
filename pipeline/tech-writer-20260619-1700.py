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

jio_body = """India's biggest company is finally putting a price tag on the business that rewired how 1.4 billion people get online. On Friday, at Reliance Industries' annual shareholder meeting, Mukesh Ambani confirmed that the board of Jio Platforms has approved a draft prospectus for an initial public offering, with papers due to be filed with the Securities and Exchange Board of India that same day.

The numbers are the kind that move an entire market. Jio is targeting roughly 360 billion rupees — about $3.8 billion — by issuing up to 270 million new shares, equal to roughly 2.9% of the company. If it lands at that size, it would be the largest IPO in Indian history, edging past the National Stock Exchange's own newly filed offering.

**What sits inside the box**

Jio Platforms is not just a telecom operator. It houses Reliance Jio Infocomm, which serves around 500 million subscribers and carries about 60% of India's mobile data traffic, making it the world's second-largest carrier by users after China Mobile. Bolted onto that are cloud, enterprise networking, and a growing stack of AI ambitions. Ambani framed the listing in nation-building terms: a chance to "demonstrate to the world that India can build technology companies of global scale."

There is also a succession subtext. Ambani said his children — Akash, Isha, and Anant — will lead the IPO process, a public signal about who steers the empire next.

**Why an NRI should read past the headline**

For the Indian diaspora, this is the rare megacap listing that arrives with familiar foreign names already on the cap table. When Jio raised capital in 2020, it pulled in Meta and Google, which today hold roughly 10% and 7.7% respectively, alongside Vista Equity Partners. An NRI investor in New Jersey or the Bay Area effectively already has indirect Jio exposure through any S&P 500 index fund holding those two American giants. A direct listing changes the calculus — it offers a cleaner, India-rupee-denominated way to own the asset, but it also comes wrapped in rupee risk and India market-timing risk.

And the timing is awkward. The benchmark Sensex is down nearly 10% this year, dragged by weaker risk appetite, stretched valuations, and the fallout from Middle East conflict on a country that imports most of its oil and gas from the Gulf. Listing activity has been subdued precisely because sentiment is soft. Jio is large enough to defy that gravity, but NRIs weighing a GIFT City or NRE-account route into the offering should treat the macro backdrop as a real variable, not a footnote.

**The bigger pattern**

Jio's filing lands in the same week as the NSE's $57-billion IPO papers and Razorpay's confidential filing. India's biggest private technology assets are queuing for public markets all at once, after years of regulatory delay. For diaspora investors who have watched from the sidelines as Indian unicorns stayed private, the gate is opening — and Jio is the marquee name walking through it first.

The prospectus is only the starting gun. Pricing, the regulatory review, and roadshows will determine whether this becomes the blockbuster Ambani is promising or a casualty of a jittery market. Either way, the diaspora now has a front-row decision to make."""

ctrls_body = """A Canadian pension fund just made one of the clearest bets yet that India's artificial-intelligence build-out is real, present, and hungry for concrete and electricity. On June 17, the Canada Pension Plan Investment Board said it would commit up to 70 billion rupees — about C$1 billion — to CtrlS Datacenters, a Hyderabad-based operator that most consumers have never heard of but that quietly underpins a chunk of India's cloud economy.

The structure is telling. CPP Investments will spend 40 billion rupees (C$588 million) to buy an 8.2% stake in CtrlS at a pre-money valuation of roughly 44,914 crore rupees, or about $4.75 billion. Separately, it has committed up to 30 billion rupees (C$441 million) to a joint venture with CtrlS to build hyperscale data-center campuses across India, with CPP holding 48% and CtrlS 52%.

**Why a pension fund cares about server racks**

The demand signals are not subtle. CtrlS founder Sridhar Pinnapureddy put it bluntly: "India's AI moment is not on the horizon, it is already here." His company operates 370 megawatts of active capacity today and is targeting 4 gigawatts — a more than tenfold expansion. For context, JLL pegged India's total active data-center capacity at 1.12 GW as of mid-2024. CtrlS alone wants to dwarf that.

The money is chasing a market that consulting firm IMARC projects will nearly double to $13.11 billion by 2034, driven by cloud adoption, digitalization, and AI workloads. American hyperscalers — Amazon, Microsoft, and Google — are pouring capital into Indian regions, and New Delhi is actively courting the investment.

**The diaspora angle: where your cloud actually lives**

For Indian Americans, this story matters on two levels. First, professionally: a generation of NRI engineers works on cloud and AI infrastructure at AWS, Azure, and GCP, and India is fast becoming one of the most important regions those platforms serve. The buildout means more capacity provisioned closer to Indian users — lower latency for the apps the diaspora uses to stay connected to home, and a deeper engineering footprint that often routes through teams in Hyderabad and Bengaluru.

Second, as investors. CtrlS is private, so there is no ticker to buy today. But the CPP deal is a roadmap. It validates Indian data-center operators as institutional-grade assets, the kind that eventually reach public markets or feed into infrastructure funds that NRIs can access. CPP, which already holds ₹1.85 trillion ($19.6 billion) in Indian investments, is not a tourist here.

**A familiar trade-off**

The risk is the same one haunting AI infrastructure everywhere: capacity is being built on the assumption that demand keeps climbing. If the AI boom cools, India could end up with expensive, half-used campuses. But CPP's willingness to anchor both equity and a development JV suggests the smart money sees the demand as durable, not speculative.

For the diaspora, the takeaway is concrete: the physical backbone of India's digital economy is being financed by global capital, built by Indian operators, and increasingly designed by engineers who look a lot like the readers of this page."""

bigbasket_body = """The company that taught India to order groceries online is handing the keys to an outsider for the first time in its 15-year history — and the move says more about the brutal economics of 10-minute delivery than about any one executive.

On June 16, BigBasket, owned by Tata Digital, named Amit Nanda as its chief executive, replacing co-founder Hari Menon, who steps back into a mentorship and board role. Nanda arrives after more than 11 years at Amazon India, most recently running Selling Partner Services, the unit overseeing the country's vast third-party marketplace. Before Amazon, he logged time at Hindustan Unilever and Citibank. His mandate is narrow and urgent: make BigBasket competitive in quick commerce before the window closes.

**The numbers behind the reshuffle**

BigBasket pioneered online grocery in India, but it is losing the speed race. According to Tata Sons' FY25 annual report, the consumer-facing business saw operating revenue slip 2.7% to ₹7,673 crore while losses ballooned 46% to ₹1,850 crore. That is the financial signature of a company spending heavily just to stay in a fight it no longer leads.

The fight is for India's quick-commerce market, which has exploded into an $11.5 billion business in roughly five years. The leaders now are Eternal's Blinkit, Swiggy's Instamart, and Zepto — the 10-minute upstarts — alongside Amazon's Now, Flipkart's Minutes, and Reliance's JioMart. BigBasket, once the category's grandfather, is scrambling to roll out 10-minute delivery nationwide. The Nanda hire follows other recent moves: Seshu Kumar Tirumala was elevated to COO and Arpit Jaiswal brought in as chief growth officer.

**Why the diaspora should pay attention**

For NRIs, BigBasket is more than a stock-watch item — it is often the literal pipeline that keeps a parent in Pune or Hyderabad supplied. Diaspora children routinely place BigBasket orders from abroad for aging family members in India, and the reliability of that service is a quiet daily concern. A leadership shake-up at the top of the company, plus the squeeze from faster rivals, is a signal worth tracking for anyone who manages a household remotely.

There is an investment dimension too. BigBasket sits inside Tata Digital, and Tata has signaled it may eventually list parts of its consumer-internet portfolio. For NRI investors who like the Tata brand's stability, BigBasket's turnaround — or failure to turn around — will shape the valuation of any future offering. A former Amazon operator at the helm is a bet that disciplined marketplace logistics, not just cash-burning expansion, can rescue margins.

**The Amazon playbook meets the Tata balance sheet**

Nanda's career is essentially a masterclass in marketplace operations and private-label scaling — exactly the muscles BigBasket needs as it leans on its own brands to protect margins against the discount wars. Whether that translates in the frantic, sub-10-minute world of dark stores and gig riders is the open question. India's quick-commerce shakeout has already minted winners and is starting to expose the losers. For the diaspora watching from afar, BigBasket's next year will reveal whether a category pioneer can be retrofitted for a race it didn't design."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Ambani Just Priced India's Biggest IPO Ever. Two American Tech Giants Are Already Inside Jio.",
        "subheadline": "Reliance filed Jio Platforms' draft prospectus Friday, targeting a record $3.8 billion — and NRIs holding any S&P 500 fund already own a sliver of it through Meta and Google.",
        "slug": make_slug("jio-platforms-ipo-ambani-reliance-record-listing-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Jio's record IPO is the cleanest direct route yet for NRIs to own India's largest digital business — but it arrives in a soft Sensex with rupee and timing risk to weigh.",
        "tags": ["jio", "reliance", "ipo", "ambani", "indian-tech", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/ambanis-jio-platforms-eyes-record-38-billion-indian-ipo-sources-say-2026-06-19/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/reliances-jio-platforms-to-seek-india-listing"},
            {"name": "Financial Times (via Reuters)", "url": "https://www.reuters.com/business/ambanis-jio-set-file-india-ipo-within-days-ft-reports-2026-06-17/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stock exchange display board tracking equity prices, as India's largest IPOs line up for listing",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": jio_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Canadian Pension Fund Just Bet $1 Billion on India's AI Plumbing. The Diaspora Builds Both Ends of It.",
        "subheadline": "CPP Investments is backing Hyderabad's CtrlS Datacenters to scale tenfold — a sign global capital sees India's AI demand as real, not speculative.",
        "slug": make_slug("ctrls-datacenters-cpp-investments-india-ai-data-center-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's AI infrastructure is being financed by global pension capital and built by Indian operators, with much of the cloud engineering routed through NRI-heavy teams in Hyderabad and Bengaluru.",
        "tags": ["data-centers", "ai-infrastructure", "ctrls", "cpp-investments", "indian-tech", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/cpp-investments-invest-740-million-indias-ctrls-datacenters-2026-06-17/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/ctrls-bags-7000-cr-commitment-from-cpp-investments/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/ctrls-raises-7000-crore-at-4-8-billion-valuation-to-chase-indias-ai-data-centre-boom"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Rows of servers inside a data center, the physical backbone of India's expanding AI economy",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": ctrls_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "BigBasket Just Hired an Amazon Veteran to Save It. The Company That Invented Indian Grocery Is Now the Underdog.",
        "subheadline": "Tata handed the CEO job to ex-Amazon executive Amit Nanda as losses widened 46% and 10-minute rivals Blinkit, Zepto and Instamart pulled ahead.",
        "slug": make_slug("bigbasket-amit-nanda-ceo-amazon-tata-quick-commerce-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "BigBasket is the pipeline many NRIs use to supply aging parents in India, so a leadership shake-up amid the quick-commerce squeeze is a daily-life signal as much as an investing one.",
        "tags": ["bigbasket", "quick-commerce", "tata", "amazon", "indian-tech", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/retail-consumer/indias-bigbasket-names-former-amazon-veteran-amit-nanda-ceo-2026-06-16/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/tata-hands-bigbasket-reins-to-former-amazon-executive-amit-nanda/"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/hari-menon-steps-down-bigbasket-ceo-amit-nanda"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7843985/pexels-photo-7843985.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Packed grocery delivery orders ready for dispatch, as India's quick-commerce race intensifies",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": bigbasket_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] words={wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
