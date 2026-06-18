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

article1_body = """Tim Cook does not warn about price hikes lightly. So when Apple's outgoing chief executive told the Wall Street Journal this week that "price increases are unavoidable," he was confirming what the chip industry has been muttering for months: the AI boom has eaten the world's supply of memory, and ordinary buyers are about to pay for it.

The mechanics are brutally simple. The data centres training and running large AI models need staggering quantities of DRAM and high-bandwidth memory. Hyperscalers are locking up supply with three-to-five-year contracts and enormous cash prepayments, terms that even Apple, with its fortress balance sheet, is unwilling to match. Morgan Stanley estimates the market is running 10 to 15 percent short of demand and pencils in a 15 percent rise in US smartphone and PC prices this year. Research firm TechInsights reckons the next iPhone Pro could cost $270 more.

**The diaspora pays twice**

For Indian Americans, this is one of those rare stories where the diaspora sits on both sides of the ledger. On one side, you are the consumer. The Indian American household is, statistically, among the most device-dense in the country — multiple iPhones, MacBooks for the kids, the annual upgrade cycle. A $270 jump on a Pro, plus creeping increases on Macs and iPads, is a quiet tax on a community that buys a lot of Apple.

On the other side, you may be the beneficiary. The single largest American memory maker, Micron Technology, is run by Sanjay Mehrotra, the Kanpur-born, BITS-Pilani-and-Berkeley engineer who co-founded SanDisk before taking the helm at Micron. He has spent two years describing memory as a structurally short commodity, and the market has finally proved him right. Micron's pricing power is the flip side of Tim Cook's pain. If your retirement portfolio holds Micron — or the broader semiconductor index — the same crunch squeezing your iPhone budget is padding your 401(k).

**Why this is not a normal cycle**

Memory has always been cyclical: gluts and shortages alternate with grim reliability. What makes this different is the source of demand. Previous booms were driven by PCs or smartphones, products with predictable replacement cycles. This one is driven by AI compute, which is expanding faster than fabs can be built, and high-bandwidth memory carries fatter margins than the commodity chips that go into laptops. So manufacturers are rationally diverting capacity toward AI buyers, starving the consumer market.

That diversion has knock-on effects the industry is only starting to price in. AMD this week paid an undisclosed sum for MEXT, a memory-optimisation startup, explicitly to soften the blow of soaring memory costs — a tell that even the chip giants are scrambling. As Morgan Stanley's Shawn Kim put it, "What began as an AI infrastructure bottleneck is now spreading into hardware margins, device affordability, cloud costs, inflation, and policy."

**The India angle gets sharper**

There is a longer arc here for the diaspora to watch. Micron's new assembly-and-test plant in Sanand, Gujarat — Mehrotra's signature India bet — converts DRAM and NAND wafers into finished modules and presented its first made-in-India shipment to Dell earlier this year. It does not make wafers from scratch, so it will not single-handedly fix a global shortage. But it positions India inside the memory supply chain at precisely the moment memory became, in Arista CEO Jayshree Ullal's phrase, "the new gold."

For an NRI engineer weighing a move home, or an investor weighing an India semiconductor play, the timing matters. A community letter to Treasury and Commerce officials is already asking Washington to intervene on supply. The politics of memory — who gets it, at what price, made where — has become a live question, and Indians sit at the centre of it: as the executive selling the scarce commodity, as the engineers building India's slice of the chain, and as the consumers about to open their wallets a little wider in September.

The bottom line for the Bay Area household: budget for a pricier upgrade this year, and understand that the same force making your phone dearer is the one making chip stocks soar. Cook said Apple is "willing to use our balance sheet to help." For everyone without Apple's balance sheet, the help is going to look a lot like a higher invoice."""

article2_body = """When India opened its space sector to private companies, the obvious bets were the rocket startups — Skyroot, Agnikul, the firms that put hardware on a launch pad. The quieter, and arguably smarter, bet is on what happens after the satellite is up. This week the Indian space regulator put money behind exactly that, handing Bengaluru-based SatSure Analytics a 246-million-rupee ($2.6 million) grant to build AI-powered Earth-observation models tailored to India.

It is a small cheque by Silicon Valley standards. But it signals something the diaspora should be tracking closely: India is trying to build sovereign AI not just in chatbots and language models, but in the unglamorous, high-value layer of geospatial intelligence — the data that tells you where the monsoon will hit, how a crop is faring, where a city is sprawling.

**Why "sovereign" is the operative word**

SatSure's pitch is that global Earth-observation models, trained largely on Western geographies, struggle with Indian conditions: the monsoon's peculiarities, smallholder agricultural patchworks, dense and chaotic urban growth. The grant funds large Earth-observation models built on satellite and drone data specific to India, to improve accuracy over those one-size-fits-all global systems.

"Earth observation is moving from project-specific analytics to reusable intelligence infrastructure," said co-founder and CTO Rashmit Singh Sukhmani. Translated: instead of building a bespoke model every time someone wants to monitor a dam or insure a harvest, India wants a reusable foundation layer it owns outright. The grant also backs SatSure's role in India's planned commercial satellite constellation.

**The diaspora connection runs deep**

This is not a niche story for Indian Americans. A striking share of the global space-and-geospatial workforce is Indian — at NASA's JPL, at NOAA, at the Earth-observation arms of Planet Labs, Maxar, and the climate-tech startups raising money across California. For those professionals, India's private space push is the first credible "come home, or come invest" pitch in their own field. For decades, an ambitious Indian remote-sensing scientist had exactly one employer back home: ISRO, the state agency. Now there is an ecosystem.

The money is starting to follow. India launched a 10-billion-rupee fund to help space startups scale, and the sector has drawn private capital from names that NRI investors recognise. SatSure itself sits at the intersection of three things the diaspora cares about — space, AI, and climate resilience — which makes it a useful proxy for the whole category.

**Why agriculture and finance, not defence, is the tell**

The most revealing part of SatSure's plan is where the data goes: monsoon patterns, agricultural landscapes, urban expansion, deployed into infrastructure and finance. This is Earth observation as a commercial input, not a national-security curiosity. Crop-yield models feed agricultural lending and insurance. Urban-growth data feeds infrastructure planning and real-estate underwriting. These are exactly the sectors where an NRI with capital, or a returning professional with domain expertise, can plug in.

It also reflects a broader pattern in India's tech policy: build the public-good infrastructure layer, then let private players commercialise on top. It worked with UPI in payments and Aadhaar in identity. Geospatial intelligence is the same playbook applied to the physical world — and the diaspora has watched the earlier versions mint companies.

**The realistic frame**

A $2.6 million grant will not, on its own, build a sovereign Earth-observation stack. The hard parts — compute, a steady satellite data pipeline, talent that can be lured back from Western labs — remain expensive and unsolved. India's space-tech scene is still early, and most of these startups are years from meaningful revenue.

But the direction is unmistakable. Governments worldwide are pouring money into domestic AI and geospatial systems to cut dependence on foreign technology, and India is determined not to be a customer in a field where it has the raw talent to be a supplier. For the Indian American watching from a satellite-imaging lab in California, the question is shifting from whether India's private space sector is real to whether it is time to get involved while it is still early."""

article3_body = """For the Indian American who grew up visiting relatives in Mumbai or Bengaluru, the rooftop is a familiar feature of every house — the place for water tanks, drying laundry, the occasional terrace party. SolarSquare wants to make it a power plant. This week the Mumbai-based residential solar company raised $53 million in a Series C round led by B Capital, pushing its total funding past $100 million and putting a serious bet behind a simple idea: India's homeowners are ready to generate their own electricity.

It is a clean-energy story, but for the diaspora it doubles as a window into how the India most NRIs remember — unreliable power, diesel backup generators, the summer load-shedding ritual — is being quietly rewired.

**Why a rooftop company raised $53 million**

SolarSquare, founded in 2015 by Neeraj Jain, Nikhil Nahar, and Shreya Mishra, sells end-to-end rooftop solar to homeowners: consultation, system design, installation, financing, and ongoing maintenance. The pitch to the Indian household is straightforward economics. Grid power is getting pricier, panel costs have collapsed, and government subsidy schemes now defray a chunk of the upfront cost. For a middle-class family in a tier-one or tier-two city, the payback period has fallen into a range that makes the decision rational rather than aspirational.

The investor roster tells its own story. Beyond lead B Capital, the round drew Lightspeed, Elevation Capital, Lowercarbon Capital, Good Capital, and — notably for the diaspora — Rainmatter, the climate fund backed by Zerodha, the brokerage that has become a touchstone for India's retail-investing class. When the people who built India's stock-trading boom start funding rooftops, it is worth paying attention.

**The diaspora angle: you might be the customer's landlord**

Here is the connection most NRIs miss. A large share of the diaspora owns property in India — the family home in the hometown, an apartment held as an investment, the house the parents still live in. Every one of those is a candidate rooftop. For an NRI funding a parent's household from abroad, residential solar is a way to permanently cut a recurring bill and add value to an asset, all without setting foot on site, since companies like SolarSquare now handle the entire journey end to end.

There is an investment angle too. India's residential solar market is still a sliver of its potential — the country has pushed hard on utility-scale solar farms but barely scratched the rooftop opportunity. The government's flagship rooftop subsidy programme has set ambitious household-installation targets, and companies racing to capture that demand are exactly the kind of climate-infrastructure play that NRI investors, increasingly able to access Indian markets, have been looking for.

**Part of a bigger clean-energy churn**

SolarSquare's raise lands amid a broader sorting in India's clean-energy and mobility sector. The same week saw Exponent Energy pull in roughly $24 million in a round that drew Hitachi's first India investment, even as electric-scooter pioneer Ola Electric's troubles served as a cautionary tale that being first is not the same as being durable. The lesson investors seem to be internalising: in Indian clean tech, boring and well-executed beats flashy and fast.

That is a useful frame for the diaspora reader weighing where to put attention. Rooftop solar is not a moonshot. It is plumbing — unsexy, capital-intensive, dependent on installation logistics and financing more than on breakthrough technology. But it maps onto a real, recurring household pain that every NRI with family in India understands viscerally.

**The honest caveat**

Rooftop adoption in India still faces friction: financing access for lower-income households, the quality and reliability of installers, and the patchwork of state-level net-metering rules that determine how much a homeowner actually saves. A $53 million round does not erase those. SolarSquare will have to prove it can scale installation quality, not just sales.

Still, the trajectory is the point. The India of the diaspora's memory ran on an unreliable grid and a noisy backup generator. The India taking shape may run, increasingly, on the roof of the family home — and the capital building it is flowing from funds the diaspora already knows."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Tim Cook Says Your Next iPhone Costs More. Blame the AI Memory Crunch — and Thank an Indian CEO for It.",
        "subheadline": "The same shortage driving Apple's price hikes is minting profits for Micron's Sanjay Mehrotra. The diaspora sits on both sides of the trade.",
        "slug": make_slug("apple-price-hike-memory-chip-crunch-micron-sanjay-mehrotra-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian American households buy a lot of Apple gear and will feel the price hikes, while the global memory crunch driving them is enriching Micron's Indian-origin CEO Sanjay Mehrotra and pulling India deeper into the chip supply chain.",
        "tags": ["semiconductors", "apple", "micron", "memory-chips", "indian-tech", "ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/apple-memory-chip-prices-tim-cook"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-raise-prices-due-memory-chip-shortage-ceo-tells-wsj-2026-06-18/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/amd-mext-memory-stock"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/17/apple-confirms-price-increases-ram-shortage/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron Technology chairman, president and CEO Sanjay Mehrotra, the Indian-origin chip executive whose memory business is benefiting from the AI-driven shortage",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Funded an AI That Watches the Country From Orbit. For the Diaspora, It's a New Kind of Homecoming.",
        "subheadline": "A $2.6 million grant to Bengaluru's SatSure signals India's push for sovereign Earth-observation AI — and a first real career pitch to diaspora space scientists.",
        "slug": make_slug("satsure-earth-observation-sovereign-ai-india-space-tech-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "A large share of the global space and geospatial workforce is Indian; India's private space push and its bet on sovereign Earth-observation AI is the first credible come-home-or-invest pitch in their own field.",
        "tags": ["space-tech", "indian-startups", "ai", "earth-observation", "sovereign-ai", "isro"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-satsure-bags-26-million-grant-build-ai-powered-earth-observation-models-2026-06-11/"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/startup-news-updates-daily-roundup-june-16-2026"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/586056/pexels-photo-586056.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A satellite in orbit over Earth, the kind of platform feeding the Earth-observation AI models India is now funding",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "SolarSquare Raised $53 Million to Put Power Plants on India's Rooftops. NRIs Already Own a Lot of Those Roofs.",
        "subheadline": "The Mumbai startup's Series C is a bet that India's homeowners are done with load-shedding — and a quiet opportunity for the diaspora that owns property back home.",
        "slug": make_slug("solarsquare-53-million-rooftop-solar-india-nri-property-clean-energy"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Many NRIs own property in India — the family home or an investment flat — making them direct candidates for rooftop solar, while the sector is becoming a climate-infrastructure investment play backed by funds the diaspora already knows.",
        "tags": ["clean-energy", "indian-startups", "solar", "climate-tech", "nri-investors", "venture-capital"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/startup-news-updates-daily-roundup-june-16-2026"},
            {"name": "LinkedIn — Startup & VC Report India", "url": "https://www.linkedin.com/pulse/startup-venture-capital-report-usa-canada-india-june-8-14-2026"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9875679/pexels-photo-9875679.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Solar panels installed on a residential rooftop, the market SolarSquare is racing to capture across Indian cities",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
