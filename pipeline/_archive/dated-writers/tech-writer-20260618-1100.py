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
        "headline": "Wipro Built a Whole Center to Run Claude. The Company That Sold Cheap Code Is Now Selling AI to Replace It.",
        "subheadline": "The Bengaluru IT giant will certify 10,000 staff on Anthropic's models in 18 months — a defensive pivot that quietly redraws the career math for every Indian engineer who came up through the services pipeline.",
        "slug": make_slug("wipro-anthropic-claude-center-bengaluru-ai-pivot-it-jobs-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the hundreds of thousands of Indian engineers — and their relatives in the US and UK — who climbed out of the IT services pipeline that Wipro built, the company's bet on Claude is a signal that the old ladder of 'learn to code, get placed, get an H-1B' is being rebuilt around AI fluency rather than headcount.",
        "tags": ["ai", "wipro", "anthropic", "claude", "indian-it", "h1b", "bengaluru"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-wipro-opens-ai-center-anthropics-claude-bengaluru-2026-06-16/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/"},
            {"name": "CXOToday", "url": "https://www.cxotoday.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Software engineers collaborating at a technology workspace, the kind of delivery floor Wipro is retraining around Anthropic's Claude models.",
        "image_attribution": "Pexels",
        "body": """Wipro opened a building this week, and the building is the message.

On Tuesday the Bengaluru IT services giant unveiled an Applied AI Centre of Excellence dedicated entirely to Anthropic's Claude family of models, housed at its innovation hub and run under a newly created AI-Native Business and Platforms Unit. The plan attached to it is the part worth reading twice: Wipro says it will certify 10,000 frontline delivery professionals on Claude within 18 months, embed the models across its own finance, HR and sales functions, and deploy "Forward Deployed Engineers" directly inside client environments.

For a company that built its fortune on supplying large numbers of competent engineers at predictable rates, this is not a product launch. It is a hedge against its own business model.

## Context & Background

India's $315 billion IT services sector — Wipro, TCS, Infosys, HCLTech and the rest — was constructed on a simple arbitrage: deep benches of skilled engineers, billed by the hour or the seat, doing the application development, testing and maintenance that Western enterprises did not want to staff in-house. That model minted a middle class in Bengaluru, Hyderabad and Pune, and it became the on-ramp to the United States. The H-1B visa pipeline, the L-1 transfers, the cousin who "went onsite" — all of it flowed through this machine.

Generative AI attacks the machine at its foundation. When Anthropic shipped an AI coding agent earlier this year, Indian IT stocks shed billions in market value in a matter of weeks, on the straightforward fear that software that writes and maintains code makes labour-intensive delivery less valuable. The whole sector is now trying to prove it can sell the disruption rather than be flattened by it.

## Current Developments

Wipro's answer is to become a reseller and integrator of the very technology that threatens it. The CoE will build Claude-powered platforms and industry tools for mortgage, healthcare, aviation, manufacturing and consumer businesses, and feed those capabilities into Wipro's "Intelligence" stack. Chief Executive Srini Pallia framed it as "a fundamental shift in how we deliver," advancing a strategy of being "consulting-led and AI-powered."

The move follows rival TCS, which on June 11 announced its own alliance with Anthropic to drive enterprise AI adoption. Two of India's largest employers, within a week of each other, have publicly tied their futures to the same American AI lab.

Analysts are not uniformly convinced. Jefferies noted that Wipro still expects compression in services revenue to weigh on growth in coming quarters — AI may widen the addressable market through application rebuilds, but it does not obviously restore the headcount-driven growth of the past decade.

## Diaspora Impact

This is where the story stops being about a Bengaluru ribbon-cutting and starts being about families. The Indian American community is, to a remarkable degree, a services-pipeline diaspora. The engineer at a New Jersey bank, the project manager in Dallas, the consultant in the Bay Area — many of them rode this exact escalator: campus placement at an Indian IT firm, a few years of delivery work, then an onsite assignment and a visa.

Wipro's pivot is a preview of how that escalator gets rebuilt. The valuable worker is no longer the one who can write the code; it is the one certified to direct the model, validate its output, and embed it inside a client's workflow. "Forward Deployed Engineer" is a job title that did not exist on the org chart five years ago, and it is precisely the kind of higher-value, onsite role that justifies a visa in an era of $100,000 H-1B fee fights.

For Indian engineers already in the US, the lesson is to chase the certification, not the seat count. For the family back home wondering whether the IT dream still works, the honest answer is that it does — but the dream now requires fluency in a model made in San Francisco, not just a degree from an engineering college.

## What's Next

Watch whether the 10,000-certification target translates into actual client revenue when Wipro next reports earnings, and whether the FDE model produces billing rates that hold up margins. Watch, too, how many of these newly minted Claude specialists end up onsite in the US — because that number, more than any press release, will tell the diaspora whether the pipeline that built it is being upgraded or quietly retired."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Real Chip Fab Just Signed the Hardest Vendor in Tech. Now the Hard Part Begins.",
        "subheadline": "Tata Electronics has locked in ASML lithography for its $11 billion Dholera fab, with first chips due by December — a milestone that turns India's semiconductor talk into a delivery deadline.",
        "slug": make_slug("tata-electronics-asml-dholera-fab-semiconductor-mission-nri-india"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin semiconductor engineers staff the design and process teams at Micron, Intel, AMD, Applied Materials and ASML's own customers — and a working fab in Gujarat is the first credible reason in a generation for some of them to consider building chips at home instead of abroad.",
        "tags": ["semiconductor", "tata-electronics", "asml", "dholera", "india-chips", "manufacturing"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/"},
            {"name": "Press Information Bureau, Government of India", "url": "https://pib.gov.in/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31665489/pexels-photo-31665489.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A close-up of a semiconductor processor die, the class of analog and logic chips Tata's Dholera fab aims to produce.",
        "image_attribution": "Pexels",
        "body": """For two decades, "India will make its own chips" was a line in a minister's speech. This week it acquired a vendor, a node, and a deadline.

Tata Electronics has signed a Memorandum of Understanding with ASML — the Dutch company that holds an effective monopoly on advanced chip lithography — to supply the photolithography systems for its 300mm fab in Dholera, Gujarat. The $11 billion facility is India's first commercial-scale semiconductor fabrication plant, and it is now targeting initial chip production by December 2026.

When the most indispensable equipment maker in the industry agrees to ship you its machines, the project stops being aspirational. It becomes a logistics and execution problem — which, for India's chip ambitions, is enormous progress.

## Context & Background

A fab is not one factory; it is a coordinated act of global supply chains, ultra-pure chemistry, and machinery so precise that ASML's most advanced tools are among the most complex objects humans build. India has tried and failed at this before — earlier joint ventures collapsed over financing and technology access. The current push, under the India Semiconductor Mission, has been different mainly because the government put real money behind it and because Tata, a conglomerate with the balance sheet to absorb years of losses, took the lead.

The Dholera fab will produce analog and logic chips on mature 28nm-to-110nm process nodes, with a planned capacity of roughly 50,000 wafers a month. These are not the bleeding-edge 3nm chips inside the latest iPhone. They are the workhorse components that run cars, appliances, power systems and industrial electronics — a deliberately pragmatic choice, because mature nodes are where demand is durable and the technology risk is manageable.

## Current Developments

The ASML agreement slots into a fast-thickening ecosystem. Tata has separately partnered with Taiwan's Powerchip Semiconductor (PSMC) for the actual manufacturing technology transfer. Its OSAT assembly-and-test plant in Jagiroad, Assam is nearing commissioning. And Micron's $2.75 billion assembly-and-test site in Sanand has already begun commercial production, shipping its first made-in-India memory modules to Dell.

The Government of India's own filings now list a cluster of approved projects — Micron, CG Semi, Kaynes Semicon, the Hubballi components cluster and Tata's fab among them — representing roughly $17 billion in committed investment across Gujarat, Assam and beyond. The fab is the crown jewel because it is the hardest piece: front-end manufacturing, the part everyone else in the world guards jealously.

## Diaspora Impact

Here is why an NRI in San Jose should care. The global semiconductor industry runs, disproportionately, on Indian-origin talent. Walk the process-engineering floors of Micron, Intel, AMD, GlobalFoundries or Applied Materials, and you will hear Telugu, Tamil, Hindi and Gujarati. Many of these engineers left India precisely because there was no chip industry to stay for.

A functioning fab in Gujarat changes that calculus for the first time in a generation. It will not reverse the brain drain overnight — Dholera will need exactly the senior process and yield engineers who currently sit in Boise, Hillsboro and Austin. That creates a genuine, if uncomfortable, recruiting tension: India's mission needs the diaspora's expertise, and some of that expertise may decide the homecoming is finally worth it, especially as US visa politics turn hostile and $100,000 H-1B fee fights make the American path feel less secure.

For NRI investors, the fab also reshapes the India electronics thesis. A country that can fabricate its own analog and logic chips is less exposed to the US-China chip war and Taiwan Strait risk — a structural argument that runs underneath Tata, the broader Make-in-India electronics story, and the data-center buildout that Adani, Reliance and others are racing to fund.

## What's Next

The December 2026 production target is the number to watch, and the industry's track record on first-fab timelines is unforgiving — slippage is normal, not scandalous. The real test is yield: producing a wafer is one thing, producing one where most of the chips actually work is another. If Dholera hits even respectable early yields next year, the speeches finally stop being speeches. If it slips badly, the skeptics who have heard this promise before will feel vindicated. Either way, the chips — and the diaspora engineers who might come home to make them — are now on a clock."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Biggest Exchange Finally Filed to Go Public. At $57 Billion, NRIs Are About to Get a Piece of the Casino's House.",
        "subheadline": "After years of regulatory delay, the National Stock Exchange filed IPO papers this week — a once-blocked listing that hands a $2.6 billion windfall to early backers and a rare shot at owning the rails of India's markets.",
        "slug": make_slug("nse-ipo-india-national-stock-exchange-nri-investors-gift-city"),
        "category": "technology",
        "vertical": "economy",
        "diaspora_angle": "NRIs have spent years pouring money into Indian stocks through the NSE's platform; its long-delayed IPO is the first realistic chance for diaspora investors — increasingly able to buy in via GIFT City and global brokerages — to own the exchange itself rather than just trade on it.",
        "tags": ["nse", "ipo", "india-markets", "nri-investors", "fintech", "gift-city"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indias-long-delayed-nse-ipo-sets-up-26-billion-windfall-top-investors-2026-06-18/"},
            {"name": "IPO Watch", "url": "https://ipowatch.in/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stock market display board showing live price data, the kind of trading the NSE's platform processes as the world's most active derivatives exchange.",
        "image_attribution": "Pexels",
        "body": """The strange thing about the National Stock Exchange of India is that for years you could buy almost any company that trades on it — except the exchange itself. That is finally changing.

The NSE filed draft papers for an initial public offering late Wednesday, ending one of the longest-running "will they, won't they" sagas in Indian finance. The listing values the country's largest bourse — and the world's most active derivatives exchange by volume — at roughly $57 billion based on unlisted-market prices near 2,000 rupees a share. That would make it, by some measures, the world's fifth most valuable exchange operator, behind the London Stock Exchange Group and ahead of much older names.

For the investors who have waited, it is payday. For the diaspora, it is something more interesting: a chance to own the toll booth instead of just paying the toll.

## Context & Background

The NSE has wanted to go public for the better part of a decade. The hold-up was not appetite — demand has never been the problem — but a long-running regulatory and governance overhang, including a co-location scandal that tangled the exchange in investigations and kept the markets regulator SEBI from clearing a listing. Each year the IPO was "imminent," and each year it slipped.

What changed is that the legal and governance clouds cleared enough for SEBI to allow the filing. The structure is telling: this is a pure offer-for-sale, meaning existing shareholders are selling roughly 6% of the equity and the exchange itself is raising no fresh capital. The NSE does not need the money. The IPO exists to give long-trapped early investors — state-owned Indian lenders, Singapore's sovereign wealth fund, Canada's national pension manager — a way out, to the tune of a combined $2.6 billion windfall.

## Current Developments

The NSE has more than 200,000 investors in its unlisted shares already, and bankers expect the IPO to price at a 5% to 10% discount to private-market levels — around 1,900 rupees a share — to leave room for a pop without short-changing existing holders. At that price the offering itself would be worth about $3.3 billion, putting it in the same heavyweight class as Mukesh Ambani's Reliance Jio, which is expected to file its own roughly $4 billion IPO within days.

That clustering is not a coincidence. India's IPO market cooled in 2026 after a blistering 2025, pressured by Middle East conflict, tighter liquidity and foreign outflows. The biggest names — NSE, Jio, Razorpay, Turtlemint, the insurtech opening its book June 19 — are choosing this window anyway, betting that quality issuers can still command demand even when sentiment is soft.

## Diaspora Impact

NRIs are not bystanders to Indian equity markets; they are increasingly central to them. Diaspora money flows into Indian stocks through mutual funds, through PIS accounts, and now, growingly, through GIFT City — the Gujarat financial hub where Indian brokerages have just been cleared to offer US and Indian securities to global investors. Owning a slice of the NSE is, in effect, owning a slice of all of that activity: every trade, every derivative contract, every fee.

Exchanges are extraordinary businesses precisely because they are infrastructure. They take a small cut of enormous, recurring volume, with structurally high margins and a near-monopoly moat. For an NRI portfolio that already holds Infosys, HDFC and Reliance as a bet on Indian growth, the NSE is a more elegant version of the same bet — a wager not on any one company doing well, but on Indians, at home and abroad, continuing to trade.

The catch is access and valuation. Whether NRIs can participate directly in the IPO allocation depends on residency status and the specific account structures, and $57 billion is not a cheap entry point. As with any offer-for-sale, the people selling — sophisticated institutions cashing out after years — know exactly what the asset is worth.

## What's Next

Final pricing will be set after roadshows, and the gap between the unlisted-market valuation and the IPO band will reveal how much froth bankers think the current market can bear. Watch the Reliance Jio filing expected this week, too: two mega-IPOs landing together will test whether India's public markets have the depth to absorb them without one cannibalizing the other. For diaspora investors, the practical homework is simpler — confirm whether your brokerage or GIFT City account can actually get you an allocation before deciding whether the house is worth buying into."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
