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
        "headline": "Micron Reports Wednesday. For Sanjay Mehrotra, the Hard Part Isn't the Number — It's What Comes After.",
        "subheadline": "Profit is set to grow nearly tenfold on the AI memory boom. The Indian-origin CEO's real test is convincing Wall Street a 300% stock run still has room.",
        "slug": make_slug("micron-q3-earnings-sanjay-mehrotra-hbm-ai-memory-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Micron is one of the largest employers of Indian-origin chip engineers in the US and is building a major assembly plant in Gujarat — its earnings shape both NRI portfolios and the India fab story.",
        "tags": ["micron", "semiconductors", "ai", "indian-tech", "earnings"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/micron-q3-earnings-2026"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/microns-earnings-are-a-must-watch-market-event"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/wall-street-investors-micron-earnings"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron Technology chief executive Sanjay Mehrotra, who leads the memory chipmaker into its closely watched fiscal third-quarter results.",
        "image_attribution": "Wikimedia Commons",
        "body": """When Micron Technology posts its fiscal third-quarter results after the close on Wednesday, the headline number will read like a typo. Analysts expect roughly $35 billion in revenue, up close to 275% from a year ago, and adjusted earnings near $20 a share — a jump of more than 900%. The company's own guidance points the same way, with a record gross margin around 81%. For a maker of commodity memory chips, that is not a good quarter. It is a different industry.

The man steering it is Sanjay Mehrotra, the Kanpur-born, BITS-Pilani-and-Berkeley-trained engineer who co-founded SanDisk before taking over Micron in 2017. He has spent most of his tenure managing the brutal cyclicality of memory — the business that booms when everyone needs chips and collapses when they all build capacity at once. The current cycle has handed him the best hand of his career. The question Wall Street will press on the call is whether he is holding it well, or whether the table is about to turn.

**Why memory became the new gold**

For two decades, DRAM and NAND flash were the unglamorous plumbing of computing: essential, cheap and ruthlessly competitive. Artificial intelligence rewrote that. Training and running large models requires enormous quantities of high-bandwidth memory, or HBM, the stacked DRAM that sits beside Nvidia's accelerators. Supply is tight, prices are soaring, and Micron — one of only three serious players alongside Samsung and SK Hynix — is selling close to everything it can make.

Micron's stock has risen nearly 300% in 2026, pushing its market value past $1.2 trillion. FactSet now expects Micron and Nvidia together to be the two largest contributors to S&P 500 earnings growth this quarter; strip them out and the index's growth rate roughly halves. That concentration is precisely why a memory company's results have become a market-wide event.

**The diaspora stake**

For the Indian diaspora, Micron is not an abstraction. It is one of the larger employers of Indian-origin semiconductor engineers in the United States, with design and engineering talent clustered in Boise, Austin and the Bay Area. An NRI working a memory-design or process role has watched the value of vested stock balloon this year — and is now reading the same analyst notes warning that the run may have priced in perfection.

There is a second, longer thread. Micron is building a chip assembly and test facility in Sanand, Gujarat, its single biggest bet on Indian soil and the anchor tenant of the country's semiconductor mission. A blow-out quarter and confident guidance make it easier to justify pouring capital into India; a stumble, or a cautious outlook on 2027 pricing, could slow the pace. For Indian professionals weighing a move home to a Micron India role, Wednesday's tone matters as much as the number.

**What could go wrong**

The bear case is not that earnings disappoint — almost no one expects that. It is that they merely meet a bar that has been raised impossibly high. With the stock up threefold, several analysts warn the report is a "tough earnings test," where a strong beat is the price of admission and anything short of a dramatic one could trigger a sell-off. SK Hynix's plan to expand memory output over the next five years is a reminder that the thing that always ends a memory boom is the industry's own appetite for new capacity.

Mehrotra has lived through enough of these cycles to know the script. The art on Wednesday will be in the guidance: signalling enough confidence to keep the AI narrative alive, while avoiding the kind of triumphalism that invites the next glut. He has been careful so far, framing the surge as demand-led rather than a sugar high.

**What to watch**

Three things will tell the story. First, HBM commentary — order books, capacity additions and any pricing colour for 2027. Second, the gross-margin trajectory, the cleanest read on how much pricing power Micron still holds. Third, anything Mehrotra says about India and US capacity expansion, which translates directly into jobs and the diaspora's return-migration math.

The number on Wednesday will be spectacular. Whether the stock — and the engineers whose net worth rides on it — celebrate or wince will come down to the sentences Mehrotra says next."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Now Makes Most of Its US iPhones in India. The Plumbing Underneath Is Starting to Creak.",
        "subheadline": "Tata and Foxconn plants have made India the assembly hub for Apple's American market. A pollution notice at a Tata parts plant is a reminder of how fast it was all built.",
        "slug": make_slug("apple-india-iphone-manufacturing-tata-foxconn-supply-chain-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India becoming Apple's manufacturing base reshapes the diaspora narrative from back-office coders to hardware builders — and the iPhone an NRI buys in New Jersey was likely assembled near Chennai or Bengaluru.",
        "tags": ["apple", "iphone", "india-manufacturing", "tata", "foxconn"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/indian-officials-survey-farms-tata-iphone-plant"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/apple-iphone-17-india-five-factories"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/foxconn-devanahalli-iphone-shipments"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4211136/pexels-photo-4211136.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Smartphone circuit boards on a production line; Apple now assembles most US-bound iPhones at plants run by Tata and Foxconn in India.",
        "image_attribution": "Pexels",
        "body": """A decade ago, the sentence "your iPhone was made in India" would have sounded like a misprint. Today it is the base case. Apple's chief executive Tim Cook has told investors that most iPhones sold in the United States in the June quarter were assembled in India, and the company is now producing all four of its newest models there ahead of launch — the first time every variant ships from Indian lines at debut.

The machinery behind that shift is two names: Tata Electronics, the Indian conglomerate that has become an unlikely iPhone maker, and Foxconn, the Taiwanese contract giant whose new $2.6 billion plant near Bengaluru airport has come online. Together with three other facilities, they have turned India into the assembly hub for Apple's most important market. Bloomberg has reported that Tata's plants alone could account for as much as half of India's iPhone output within two years.

For the Indian diaspora, this is a quiet reordering of an old story. The familiar diaspora identity in American tech is the software engineer — the H-1B coder at Google, the product manager at Microsoft. The iPhone build-out adds a different chapter: India as a place that makes the hardware, not just writes the code that runs on it. The phone an NRI buys at an Apple Store in Edison or Sunnyvale was, with rising probability, assembled near Chennai or Bengaluru by workers earning their place in a global supply chain that used to run almost entirely through Shenzhen.

**Why Apple moved, and moved fast**

The proximate cause is tariffs. President Trump's levies on Chinese imports — at times exceeding 100% — turned Apple's two-decade dependence on China from an efficiency into a liability. The company began assembling iPhones in India in 2017 with older, cheaper models, expanded to flagships in 2023, and has since compressed years of planned diversification into a sprint. Reaching its target meant roughly doubling Indian output, from about 40 million units a year toward more than 80 million.

That speed is the achievement and the risk. Building a world-class electronics supply chain is not only about final assembly; it is about the thousands of components, the water and power, the environmental permits and the trained workforce that sit beneath the headline factories.

**The creak in the system**

This month offered a glimpse of the strain. Indian officials surveyed farmland around a Tata iPhone parts plant after a state pollution board found the facility had discharged wastewater into a harvesting pond that overflowed and contaminated groundwater in adjacent agricultural land. It is a containable problem — but it lands on a record that already includes a 2024 fire at Tata's Hosur plant that briefly halted component production, and a 2023 fire at a former supplier's plant that shut output for days. A 2024 Reuters investigation also found a major Apple supplier had excluded married women from assembly jobs at an Indian plant, a labour-practices question the industry is still answering.

None of these is fatal. All of them are the predictable growing pains of standing up heavy manufacturing at extraordinary speed. The lesson, for anyone tracking India's industrial ambitions, is that "Make in India" is no longer a slogan competing for attention — it is an operating reality now being judged on the unglamorous metrics of effluent management, fire safety and labour standards.

**What it means for the diaspora investor and worker**

For NRI investors, the India manufacturing story is increasingly inseparable from the Apple thesis itself. A supply chain that survives tariff shocks is worth a premium; one that wobbles on environmental or labour failures invites the kind of scrutiny that slows expansion. For the smaller cohort of diaspora professionals in operations, supply-chain and manufacturing engineering, India's hardware build-out is opening a category of senior roles that barely existed there five years ago.

The iPhone in an American pocket has quietly become a product of Indian industry. The next phase is less about whether India can assemble the phone — it clearly can — and more about whether it can do so to the standards a $3 trillion company, and its diaspora customers, expect."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Took 120 of Its Hardest Startups to France. The Pitch Wasn't Software — It Was Rockets and Chips.",
        "subheadline": "At Bharat Innovates 2026 in Nice, Modi and Macron put India's deep-tech founders in front of global capital. The subtext: stop seeing India as the world's back office.",
        "slug": make_slug("bharat-innovates-2026-nice-deep-tech-startups-modi-macron-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRI investors and would-be returnees, Bharat Innovates signals a shift from consumer-app bets to hard-science startups — the kind of long-horizon companies diaspora capital and expertise are well placed to back.",
        "tags": ["deep-tech", "startups", "bharat-innovates", "india-france", "venture-capital"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/news/pm-modi-macron-bharat-innovates-2026-nice"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/bharat-innovates-2026-deep-tech-startups-nice"},
            {"name": "IANS / The Indian Eye", "url": "https://theindianeye.com/india-contributor-solutions-modi-bharat-innovates"}
        ]),
        "score_total": 71,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
        "image_caption": "Prime Minister Narendra Modi, who jointly inaugurated the Bharat Innovates 2026 deep-tech conclave with French President Emmanuel Macron in Nice.",
        "image_attribution": "Wikimedia Commons",
        "body": """The Indian startup story the world knows is a consumer one: a food-delivery app, a payments wallet, a quick-commerce network promising groceries in ten minutes. At Bharat Innovates 2026 in Nice, India tried to tell a different story. The 120 companies it flew to the French Riviera this month were not building apps. They were building hydrogen cylinders, small satellite launchers, AI diagnostics, quantum-safe security and iron-air batteries.

Prime Minister Narendra Modi and French President Emmanuel Macron jointly inaugurated the three-day conclave, part of the India-France Year of Innovation, and the framing was deliberate. "India should not be seen as a mere back office for the world's software," runs the pitch behind the event — India as a builder of frontier technology in its own right. Modi told the gathering that India is "emerging as a contributor of solutions to the world," and Macron singled out the space sector, invoking Chandrayaan-3's south-pole Moon landing as proof of capability.

**Why deep tech, and why now**

The cohort was chosen from nearly 3,000 applicants, and its shape is revealing. Space and defence was the single largest group with 22 startups, followed by healthcare and medtech with 20, then energy and climate with 16, advanced computing with 13 and biotechnology with 11. Familiar names — electric two-wheeler maker Ather Energy, drone firm ideaForge, AI-diagnostics company Qure.ai, sovereign-AI builder Sarvam AI and small-launch-vehicle company Agnikul Cosmos — sat beside far earlier-stage ventures working on brain-mapping platforms and green propulsion.

The timing reflects a real shift in Indian capital. Deep-tech funding reached roughly $1.1 billion by the start of June, already about 80% of the prior full year, according to Tracxn. Crucially, cheque sizes are growing: investors who once treated hard science as an experiment are now writing Series A rounds north of $20 million, betting that government incentives, defence spending and the semiconductor mission can produce globally competitive companies. The India Deep Tech Alliance has earmarked over $1 billion specifically for AI startups.

Deep tech does not move at the speed of a consumer app. A chip design or a satellite payload can take years to commercialise, and that long horizon has historically starved such ventures of patient money. The whole point of Bharat Innovates is to introduce those founders to the kind of capital — and global partners — willing to wait.

**The diaspora angle**

This is where the Indian diaspora becomes more than spectators. The profile of a deep-tech investor — comfortable with long timelines, technically literate, globally networked — describes a great many NRIs in Silicon Valley, London and Singapore. For diaspora venture capital, Bharat Innovates is effectively a curated deal pipeline of India's hardest startups, vetted by the government and presented on a European stage rather than buried in a Bengaluru pitch deck.

There is also a talent dimension. Many of these companies need exactly the expertise the diaspora has spent two decades accumulating at Nvidia, SpaceX, Moderna and the AI labs — chip architects, propulsion engineers, regulatory specialists. A semiconductor or aerospace professional weighing a return to India now has more to come home to than a services job; there is a frontier-tech ecosystem taking shape, with capital starting to flow toward it.

**The caution**

Showcases are easy; outcomes are hard. India has staged investor events before, and the gap between a warm reception in Nice and signed term sheets is wide. Deep tech is unforgiving — most hard-science startups fail, and the ones that succeed often need a decade and several rounds of believers. The Bengaluru run-up event in May drew 90-plus investors managing over $85 billion, but interest is not commitment.

Still, the direction is unmistakable. India is no longer content to be the place where the world's code is written cheaply. It wants to be where some of the world's hardest engineering gets built — and it is asking its diaspora, with its capital and its expertise, to help fund the bet. For NRIs who have spent careers building someone else's frontier technology, the invitation to build India's own is the most interesting thing on offer in a long time."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
