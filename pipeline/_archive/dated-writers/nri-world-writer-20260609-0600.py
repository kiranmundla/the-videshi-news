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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian-Owned Businesses in Britain Just Hit a Record. The Numbers Are Staggering.",
        "subheadline": "A 60 per cent surge in a single year has pushed the count past 1,900 firms, £105 billion in turnover, and 200,000 jobs — making India the most consequential foreign investor Britain didn't see coming.",
        "slug": make_slug("indian-owned-businesses-uk-record-1912-firms-105-billion"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian-origin entrepreneurs and conglomerates are no longer peripheral players in Britain's economy — they are structural pillars, employing hundreds of thousands and paying hundreds of millions in tax, reshaping the NRI community's economic identity abroad.",
        "tags": ["nri", "diaspora", "uk", "business", "tata", "investment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Samaj Weekly UK", "url": "https://samajweekly.com/indias-footprint-in-britain-according-to-grant-thornton-india-meets-britain-tracker-2026/"},
            {"name": "Asian Voice", "url": "https://asian-voice.com/"},
            {"name": "Grant Thornton India Meets Britain Tracker", "url": "https://www.grantthornton.co.uk/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18729251/pexels-photo-18729251.jpeg",
        "image_caption": "The Gherkin and surrounding skyscrapers in London's financial district",
        "image_attribution": "Pexels",
        "body": """The annual stock-take of Indian capital in Britain has landed, and it reads less like an investment report than a census of a parallel economy.

The Grant Thornton India Meets Britain Tracker 2026, released in partnership with the Confederation of Indian Industry and India Global Forum, counts 1,912 Indian-owned companies now operating in the United Kingdom — up from 1,197 just a year earlier. That is a jump of nearly 60 per cent, the largest single-year increase the tracker has ever recorded.

Together, these firms generate a combined turnover exceeding £105.8 billion, employ more than 203,000 people across England, Scotland, and Wales, and paid £378 million in corporation tax in the latest filing year, up from £277 million the year before. One in four of the companies on the tracker is a new entrant, suggesting the pipeline of Indian businesses flowing into Britain shows no signs of narrowing.

## The Tata Factor — and Beyond

The headline employer remains Jaguar Land Rover, owned by Tata Motors, with more than 44,000 staff. Tata Steel adds another 19,600 workers, many of them in plants across Wales and northern England that sustain entire communities. In total, 16 Indian-owned companies each employ more than 1,000 people in Britain.

But the story extends well beyond the Tata empire. Technology firms, pharmaceutical companies, and fintech startups from India are setting up shop in London, Manchester, and Birmingham at an accelerating clip. The tracker identified technology and telecoms as the most represented sectors, followed by engineering and manufacturing.

India's High Commissioner to the UK put it plainly: these companies are "not only expanding their commercial footprint" but "generating employment and contributing to the UK tax take, directly supporting growth and public services."

## Why Britain, and Why Now

Several forces are converging. The UK's post-Brexit trade posture has pushed it to court Indian capital more aggressively, with ongoing negotiations around a Free Trade Agreement that both governments hope will lower tariffs on goods, ease services access, and open professional mobility pathways.

For Indian conglomerates, Britain offers something the European Union no longer does after Brexit: a single English-speaking jurisdiction with deep capital markets, a favourable time zone bridging Asia and the Americas, and a legal system rooted in common law — the same framework India inherited.

The Indian diaspora itself plays a catalytic role. With an estimated 1.9 million people of Indian origin in Britain — the country's largest visible minority — there is a built-in talent pool, consumer base, and cultural familiarity that lowers the friction of setting up operations. Second- and third-generation British Indians increasingly occupy C-suites and boardrooms, creating networks that funnel investment both ways.

## What It Means for the Diaspora

For NRIs in Britain, the numbers validate a transformation that has been quietly under way for decades. Indian-owned businesses are no longer confined to the curry-house-and-corner-shop stereotype. They build cars, roll steel, write software, and run data centres. The £105 billion turnover figure is not far from the entire GDP of a country like Sri Lanka.

Yet the report also carries a quiet warning. The pace of expansion — 60 per cent in a single year — is partly a function of counting improvements and new entrants at the smaller end of the scale. Whether these firms survive and scale in a sluggish British economy, where GDP growth has hovered below 1.5 per cent, remains an open question.

For the diaspora, though, the direction is clear. Indian capital in Britain is no longer an anecdote. It is an economic fact that shapes towns, funds public services, and employs neighbours. The living bridge Jaishankar likes to invoke has acquired, quite literally, a balance sheet."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Sent Its Largest-Ever Business Delegation to Canada. Here's What They Want.",
        "subheadline": "Commerce Minister Piyush Goyal led more than 100 companies to Toronto, with a $50 billion bilateral trade target on the table and the Indo-Canadian community positioned as the bridge.",
        "slug": make_slug("piyush-goyal-largest-india-business-delegation-canada-cepa"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Indo-Canadian community — 1.8 million strong — is central to both the diplomatic thaw and the commercial opportunity, with diaspora business leaders explicitly enlisted as accelerants for trade and investment flows.",
        "tags": ["nri", "diaspora", "canada", "trade", "cepa", "piyush-goyal"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/piyush-goyal-lauds-role-of-indian-diaspora-in-canada/"},
            {"name": "India Tribune", "url": "https://indiatribune.com/"},
            {"name": "Great White Northern Spirits / Indian Aisle", "url": "https://theindianeye.com/great-white-northern-spirits-launches-indian-aisle-in-canada/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "image_caption": "Indian Commerce Minister Piyush Goyal at an official event",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers alone make the point. More than 100 Indian companies travelled to Canada with Commerce and Industry Minister Piyush Goyal in what the ministry is calling the largest Indian business delegation ever sent to the country. The agenda: accelerate negotiations on the Comprehensive Economic Partnership Agreement and push bilateral trade from its current $8.5 billion toward an ambitious $50 billion target by 2030.

The visit comes at a moment when India-Canada relations, frosty for much of the past two years over the Nijjar affair and mutual diplomatic expulsions, are tentatively warming. Trade, both governments appear to have concluded, is the most pragmatic path back to normalcy.

## CEPA: The Prize on the Table

The Comprehensive Economic Partnership Agreement has been under negotiation, in fits and starts, for nearly a decade. A deal would lower tariffs on goods moving in both directions, open services trade — particularly in IT and professional services where Indian firms dominate — and potentially ease the movement of skilled workers, a perennial demand from India's technology sector.

Goyal's meetings in Toronto included sessions with the Ontario Teachers' Pension Plan and CPP Investments, two of the largest institutional investors in the world, to discuss opportunities in Indian infrastructure, renewable energy, logistics, financial services, and the digital economy. The implicit pitch: India's growth story is investable, and CEPA would make it more so.

The minister also met members of the Canada-India Foundation, praising what he called "the invaluable contribution of the Indo-Canadian community in bringing the two nations closer through stronger business engagement and people-to-people ties."

## The Diaspora as Diplomatic Asset

India's 1.8 million diaspora in Canada — the largest per-capita Indian community of any major Western nation — has become central to the government's trade calculus. Goyal explicitly positioned the community not as passive beneficiaries of improved relations but as active conduits: business networks that span both countries, cultural familiarity that reduces deal friction, and a voter base that Canadian politicians cannot afford to alienate.

The timing dovetails with a broader Indian push to enlist its global diaspora as a trade accelerant. The Indiaspora report released in March estimated the global Indian diaspora's annual income at $730 billion and argued it was evolving from a source of remittances into "a powerful force of capital, capability, and credibility."

## Indian Products Hit Canada's Duty-Free Shelves

In a parallel development that underscores the cultural dimension of the commercial push, the "Indian Aisle in Canada" was formally launched at airports including Toronto Pearson and Vancouver International, as well as key land-border duty-free locations in Ontario and British Columbia.

The initiative, led by Great White Northern Spirits, marks the first time Indian beverage brands have entered Canada's premium duty-free retail ecosystem. It is being framed as a soft-power milestone — Indian products on display at the country's busiest international gateways, positioned alongside global brands.

For the Indo-Canadian community, the symbolism is hard to miss. A decade ago, Indian products in Canadian airports would have been unthinkable. Now they sit on shelves where millions of travellers pass through each year.

## The Road Ahead

Whether the $50 billion trade target is realistic depends largely on CEPA. Without a deal, tariffs on Indian textiles, agriculture, and manufactured goods will continue to limit the relationship's commercial ceiling. With one, both sides believe the numbers could move quickly — India's appetite for Canadian pulses, potash, and natural resources is growing, while Canada wants access to India's digital services, pharmaceutical, and automotive markets.

For the 1.8 million Indians in Canada, the stakes are personal. A thriving bilateral relationship means more direct flights, easier movement of family and capital, and the kind of institutional scaffolding — trade offices, cultural centres, joint research programmes — that makes diaspora life richer. A stalled one means more of the same: a relationship full of potential that never quite arrives."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Wealthy Indians Are Choosing Dubai Over Delhi. The Tax Maths Leaves Little Room for Debate.",
        "subheadline": "Zero capital gains tax, rental yields three times higher than Mumbai's, and a dirham pegged to the dollar — the NRI investor class is voting with its chequebooks, and India's property market is noticing.",
        "slug": make_slug("wealthy-indians-dubai-over-delhi-real-estate-nri-investment"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs are uniquely positioned to exploit the Dubai-India arbitrage — earning in dollars or dirhams, buying in a tax-free jurisdiction, and maintaining proximity to India for family and cultural ties. The shift reflects a maturing diaspora that evaluates real estate globally, not sentimentally.",
        "tags": ["nri", "diaspora", "dubai", "real-estate", "investment", "uae"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/dubai-over-delhi-ncr-the-new-investment-haven-for-wealthy-indians/"},
            {"name": "Knight Frank Wealth Report", "url": "https://www.knightfrank.com/"},
            {"name": "Gulf Business", "url": "https://gulfbusiness.com/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28350363/pexels-photo-28350363.jpeg",
        "image_caption": "Skyscrapers of Dubai Marina reflected in the waterfront at dusk",
        "image_attribution": "Pexels",
        "body": """The spreadsheet does the talking. A two-bedroom apartment in Downtown Dubai will net you a rental yield somewhere between 7.5 and 11 per cent. The same money parked in a comparable flat in South Delhi or Bandra will return 2 to 4 per cent — before taxes, before maintenance charges, before the annual fight with a tenant who stops paying in month nine.

This is the arithmetic driving a quiet but unmistakable shift among India's wealthiest property investors, and it is being watched nervously in Mumbai boardrooms and Delhi brokerage offices alike.

## The Tax Gap That Changes Everything

Dubai imposes no capital gains tax on property. No income tax on rental earnings. No inheritance tax. India, by contrast, layers stamp duty, registration charges, long-term capital gains tax, TDS on rental income, and a wealth tax regime that was officially abolished but replaced by surcharges that accomplish roughly the same thing.

For an NRI earning in US dollars or UAE dirhams, the calculus is devastating for Indian property markets. The UAE dirham's peg to the US dollar provides currency stability that the rupee — which has depreciated roughly 40 per cent against the dollar over the past decade — simply cannot match. An NRI who bought a flat in Gurgaon in 2016 and sold it today would find that much of the nominal appreciation has been eaten by the rupee's slide.

In Dubai, the same dollar-denominated investment has appreciated in real terms, with the added bonus that the rental income along the way was untaxed.

## Cheaper, Bigger, Better Built

The price gap carries its own logic. Premium properties in Dubai are priced 20 to 25 per cent lower than comparable options in Mumbai or Delhi NCR, yet they come with construction quality, amenities, and common-area standards that most Indian residential projects struggle to match. A swimming pool in a Mumbai high-rise is a luxury selling point. In Dubai Marina, it is table stakes.

The Knight Frank Wealth Report projects the number of ultra-rich Indians (net worth above $30 million) will rise by more than 50 per cent by 2028, to nearly 20,000 individuals. A significant proportion of this cohort already holds assets in multiple jurisdictions, and Dubai sits at the top of their shortlist.

## Four Hours from Home

Geography seals the deal. Dubai is a four-hour flight from Mumbai, Delhi, or Bengaluru — close enough that an NRI investor can check on a property over a weekend without rearranging a life. The city's Indian expatriate population, estimated at 3.5 million across the UAE, has built a parallel India: schools that teach the CBSE curriculum, temples and gurudwaras, restaurants serving everything from Chettinad to Kashmiri wazwan, and a social ecosystem dense enough that moving to Dubai feels less like emigration and more like changing neighbourhoods.

For families weighing retirement destinations, the combination of world-class healthcare, personal safety, and a familiar cultural fabric makes the decision straightforward in a way that Lisbon or London does not.

## What India Could Do About It

Indian policymakers are not unaware of the outflow. The RBI has been tightening scrutiny of outbound capital under the Liberalised Remittance Scheme, and SEBI has been widening access for NRI investors in Indian equities — partly to offer alternative asset classes that might compete with Dubai property.

Budget 2026 raised the individual NRI investment limit in listed Indian companies from 5 per cent to 10 per cent, and the combined holding limit from 10 to 24 per cent. It is a start, but it addresses the stock market, not the property market, and the friction of Indian real estate — opaque pricing, uncertain title, glacial construction timelines, and regulatory whack-a-mole — cannot be fixed by tweaking FPI limits.

For now, the money is going where the maths says it should. Dubai's tax-free, dollar-pegged, proximity-friendly proposition is not exotic to Indian investors. It is rational. And until India can make its own property market equally rational — transparent pricing, reliable delivery, competitive taxation — the shift will continue, one chequebook at a time."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
