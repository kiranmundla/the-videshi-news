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
        "headline": "Five South Asian Candidates Just Won Georgia Primaries. One Could Become the State's First Sikh Official.",
        "subheadline": "In a state with 600,000 Asian American residents, Indian and South Asian candidates swept five races in the May 19 primary — including a milestone for the Sikh community that Georgia has never seen.",
        "slug": make_slug("south-asian-candidates-georgia-primary-wins-sikh-jyot-singh"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian and South Asian Americans are building political power in Georgia at an unprecedented pace — from state house seats to a potential lieutenant governorship. The results mark a generational shift in how the diaspora engages with American democracy beyond the coasts.",
        "tags": ["nri", "diaspora", "politics", "georgia", "elections", "indian-american"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/05/21/indian-american-impact-congratulates-endorsed-candidates-on-historic-wins-in-georgia/"},
            {"name": "Indian American Impact", "url": "https://www.iaimpact.org/"},
            {"name": "Wikipedia — 2026 Georgia Lt. Gov Election", "url": "https://en.wikipedia.org/wiki/2026_Georgia_lieutenant_gubernatorial_election"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Georgia_State_Capitol%2C_Atlanta%2C_West_view_20160716_1.jpg/1920px-Georgia_State_Capitol%2C_Atlanta%2C_West_view_20160716_1.jpg",
        "image_caption": "The Georgia State Capitol in Atlanta, where newly elected South Asian lawmakers will take their seats",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The results landed late on the night of May 19 and kept landing. Across Georgia's primary ballot, five South Asian candidates backed by Indian American Impact either won outright or advanced to runoff elections — a sweep that the organization, which has endorsed more than 200 candidates nationally since 2016, called historic.

The most symbolically charged victory belonged to **Jyot Singh**, who secured the Democratic nomination for State House District 97. If he wins the general election, Singh will become the first Sikh elected official in Georgia's history. In a state where the Sikh community has grown steadily but remained largely invisible in the halls of the Gold Dome, the win carries weight that extends well beyond one legislative seat.

## The lieutenant governor's race

Nabilah Islam Parkes, a state senator from Gwinnett County who has represented the 7th Senate district since 2023, advanced to a Democratic runoff for lieutenant governor with 39.5 per cent of the vote — just behind Josh McLaurin's 41.4 per cent in a three-way race. If Parkes wins the runoff, she would become the first South Asian and Asian American lieutenant governor nominee from any party in Georgia's history.

Parkes, the daughter of Bangladeshi immigrants, has been a fixture in Gwinnett County politics since her first campaign in 2020. Her district — Peachtree Corners, Norcross, Duluth, Suwanee — reads like a map of Georgia's South Asian suburbs. She has served on the Veterans, Military and Homeland Security Committee and the Science and Technology Committee, and was recognized by Georgia Asian Times as one of the 25 most influential Asian Americans in the state.

## Three more wins

The sweep extended further down the ballot. **Saira Draper** won a competitive primary for State Senate District 44. **Rahul Garabadu** advanced to a runoff for State Senate District 7 in a crowded field. And **Akbar Ali** secured the Democratic nomination for House District 106, where he will continue serving as the youngest state legislator in Georgia.

Chintan Patel, executive director of Indian American Impact, framed the results in demographic terms: Georgia now has more than 600,000 Asian American residents, and the primary showed that community is no longer content to be counted without being represented.

"Last night's results speak to the growing political power and representation of our communities," Patel said. "We are thrilled to see so many South Asian leaders stepping into the halls of power."

## What the numbers say

The Georgia results are part of a broader pattern. Indian American Impact has channelled upwards of $20 million to candidates and voter mobilisation efforts since its founding in 2016. The organisation's track record includes support for candidates at every level — from school boards to the US Congress.

But Georgia is a particular bellwether. The state's Asian American population has grown by more than 50 per cent over the past decade, concentrated in the suburban counties around Atlanta — Gwinnett, Forsyth, Fulton — that have swung from reliably Republican to competitive or solidly Democratic. The Indian and South Asian share of that population is growing faster still.

What makes the 2026 results distinctive is not just the number of candidates but the breadth of offices they contested. A state house seat, two state senate races, and a lieutenant governorship — that is not a symbolic showing. That is a slate.

## The general election ahead

The victories are, for now, Democratic primaries. Georgia remains a closely contested state, and winning a primary is not the same as winning a general election. Jyot Singh's House District 97 leans Democratic, but the statewide races — particularly the lieutenant governor's contest — will be fought on different terrain.

For the diaspora, the significance is less about any single outcome than about the trajectory. A decade ago, the idea of five South Asian candidates winning primaries on the same night in a Southern state would have been aspirational at best. On May 19, it was Tuesday."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's $135 Billion Remittance Lifeline Is Under Pressure From Three Directions at Once.",
        "subheadline": "AI-driven tech layoffs, a $100,000 H-1B visa fee, and a new US remittance levy are squeezing the financial pipeline that covers nearly half of India's trade deficit — and the consequences are about to reach millions of NRI families.",
        "slug": make_slug("india-remittance-pressure-ai-layoffs-h1b-fee-us-levy"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs in the US, who now send more money home than Gulf workers, face a triple squeeze: their jobs are being automated, their visas cost more, and their transfers are being taxed. The shift threatens household budgets from Hyderabad to Houston.",
        "tags": ["nri", "diaspora", "remittances", "h1b", "ai-layoffs", "economy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/opinion/remittances-a-buffer-now-under-pressure/article71053696.ece"},
            {"name": "HDFC International Life", "url": "https://hdfclife-international.com/blog/us-proposes-3-5-percent-remittance-tax"},
            {"name": "IBEF — The Diaspora Effect", "url": "https://www.ibef.org/blogs/the-diaspora-effect-remittances-to-india-rising"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12008048/pexels-photo-12008048.jpeg",
        "image_caption": "A currency exchange office window displaying conversion rates in a city centre",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For most of the past quarter-century, India's remittance story has been reassuringly dull. Money came in. It kept coming in. Even during the 2008 financial crisis, even during Covid, the flows held steady — a $135 billion buffer in 2024-25 that covered nearly 47.5 per cent of the country's merchandise trade deficit and comfortably exceeded gross foreign direct investment. Since 2008, India has been the world's largest recipient of remittances. The pipeline was treated as structural, almost geological.

That assumption is now being tested from three directions simultaneously.

## The AI displacement

The first pressure is technological, and it is arriving faster than most policy frameworks can absorb. Through mid-May 2026, roughly 113,000 tech-sector jobs were eliminated globally across 179 companies, with more than three-quarters of those losses concentrated in the United States. A separate study found that 47.9 per cent of the cuts were explicitly attributed by employers to AI or workflow automation.

The displacement is concentrated in precisely the occupations that have been the mainstay of Indian white-collar workers for the past decade: software engineering, customer service, marketing, and sales. These are the jobs that turned the US into the largest single source of Indian remittances, overtaking the UAE. The US share of India's remittance inflows rose from 22.9 per cent in 2016-17 to 27.7 per cent in 2023-24, according to the latest RBI survey.

California, home to the largest concentration of Indian tech workers in the country, is already trying to address the fallout. On May 21, Governor Gavin Newsom signed Executive Order N-6-26 — the first such action by any US governor to tackle AI-driven workforce disruption. The order directs state agencies to recommend revisions to the California WARN Act, expanded unemployment insurance and retraining programmes, and what Newsom termed "universal basic capital" — a mechanism to give residents a small ownership stake in productive assets so that displaced workers can share in AI-generated profits.

The catch for NRIs: these benefits, as currently framed, will not extend to H-1B visa holders. The safety net is being redesigned. Indian workers may not be inside it.

## The visa squeeze

The second pressure is regulatory. A $100,000 fee for certain new H-1B visas took effect on September 21, 2025 — layered on top of an existing fee envelope that already ran several thousand dollars per petition. The fee does not directly reduce remittances, but it raises the cost of being an NRI in the US, narrows the pipeline of new arrivals, and signals a broader tightening of skilled-worker pathways.

The third channel — a reported tightening of US student visas — may take longer to show up in the numbers but could prove equally consequential. Fewer students arriving today means fewer high-earning professionals remitting in five years.

## The remittance levy

Then there is the One Big Beautiful Bill Act, signed into law on July 4, 2025. The legislation introduced a 1 per cent levy on certain cash-based remittance methods — cash, money orders, and cashier's cheques. It exempts electronic transfers from US bank accounts and US-issued debit and credit cards, which means the immediate financial impact on most NRIs is limited. Most Indian professionals in the US remit through bank transfers and digital platforms.

But as professors at IIM Calcutta and NIBM Pune have pointed out, the levy's significance lies less in what it collects today than in what it signals. A 1 per cent tax on cash transfers is a foot in the door. An earlier version of the legislation proposed a 3.5 per cent tax on all outbound remittances by non-citizens — a rate that, had it passed, would have cost Indian families $3,500 for every $100,000 sent home.

## The Gulf risk

If the US-origin risks are technological and regulatory, the Gulf faces a different combination of geopolitical and labour-market pressures. The GCC countries, which still account for 38 per cent of India's remittance inflows, are exposed to a potential Israel-Iran escalation that could disrupt oil revenues and business activity.

Separately, sustained softening of crude prices could accelerate labour-nationalisation programmes — Saudi Arabia's Nitaqat (Saudization) and the UAE's Emiratisation — that would displace large numbers of Indian blue-collar workers. The Gulf has long been the other pillar of India's remittance architecture. If both pillars are under stress at the same time, the arithmetic changes.

## What it means

India's remittance composition has shifted decisively toward high-income economies, particularly the US. Advanced economies now supply more than half of total inflows. That concentration bought India higher per-capita remittance values from skilled professionals, but it also created a vulnerability: the pipeline is now exposed to host-country policy changes and labour-market disruptions in ways it never was when Gulf construction workers dominated the flows.

The consequences are not abstract. Remittances flow directly to household balance sheets — paying for school fees in Andhra Pradesh, medical bills in Kerala, home loans in Punjab. They carry no reversal risk and dampen rather than amplify external-sector stress. When they shrink, the impact is felt at kitchen tables, not trading floors.

India's most stable source of foreign exchange earnings is facing a set of headwinds that are structural, not cyclical. The question is not whether the $135 billion number will hold. It is whether policymakers in Delhi and diaspora families in Dallas are preparing for a world where it does not."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Trade Deal With Oman Just Went Live. For 700,000 Gulf Indians, It's More Than Tariffs.",
        "subheadline": "The India-Oman CEPA, which entered into force on June 1, is Oman's first bilateral trade agreement since the US deal in 2006 — and it includes mobility provisions that could reshape how Indian professionals work in the Gulf.",
        "slug": make_slug("india-oman-cepa-live-gulf-diaspora-mobility-trade"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Nearly 700,000 Indians live in Oman, many in merchant families with roots stretching back two centuries. The CEPA's enhanced mobility provisions — easing entry for accountants, architects, healthcare workers — directly affect the professional class of the Gulf diaspora.",
        "tags": ["nri", "diaspora", "trade", "oman", "gulf", "cepa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/india-oman-cepa-opens-duty-free-access-for-textile-and-apparel-exports/article71055321.ece"},
            {"name": "Bhaskar English", "url": "https://bhaskarenglish.in/business/india-us-trade-deal-almost-done-us-official-says-deal-finalised-133963339.html"},
            {"name": "IndBiz — Economic Diplomacy Division", "url": "https://indbiz.gov.in/india-and-oman-sign-cepa/"},
            {"name": "Nation Press", "url": "https://nationpress.com/bhupender-yadav-hails-india-oman-cepa-as-new-trade-era"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36254459/pexels-photo-36254459.jpeg",
        "image_caption": "Aerial view of Muscat port with ship, cranes, and mountains in the background",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """On June 1, the India-Oman Comprehensive Economic Partnership Agreement quietly entered into force. There was no ceremony — just a date on a calendar and a shift in tariff schedules. But for the nearly 700,000 Indians living in the Sultanate, many of them from merchant families whose presence in Oman predates Indian independence by a comfortable margin, the deal carries implications that go well beyond customs duties.

Under the agreement, Oman will grant India duty-free access on 98.08 per cent of its tariff lines, covering 99.38 per cent of India's exports to the country. India, in turn, has liberalised tariffs on 77.79 per cent of its own tariff lines, accounting for 94.81 per cent of imports from Oman. On paper, this is a trade deal. In practice, it is the closest thing to a free-trade relationship that either country has offered the other.

## Oman's first in two decades

The CEPA is Oman's first bilateral trade agreement since its deal with the United States in 2006. That two-decade gap is not a sign of inaction — it is a measure of how deliberately Muscat approaches these negotiations. For India, the agreement is only its second with a Gulf Cooperation Council country, after the UAE pact signed in February 2022.

The timing is strategic. India has signed nine free trade agreements in the past three and a half years, covering 38 developed economies, and is expected to roll out another six to seven in the coming year. The India-UK Comprehensive Economic and Trade Agreement, the India-New Zealand FTA, and the India-EFTA deal (which includes a $100 billion investment commitment from Switzerland, Norway, Iceland, and Liechtenstein over 15 years) are all part of the same push. Commerce Minister Piyush Goyal has described Oman as a "strategic gateway" for Indian goods and services to the wider GCC region, Eastern Europe, Central Asia, and Africa.

## The mobility clause

For NRIs in the Gulf, the most consequential provisions may not be about goods at all. The CEPA includes enhanced mobility rules for Indian professionals — liberalising entry and stay norms in sectors such as accountancy, taxation, architecture, and healthcare. This is a quiet but meaningful shift.

Indian professionals in the Gulf have traditionally operated under kafala-adjacent sponsorship systems that tie their residency to a single employer. While Oman has progressively reformed its labour laws, the practical barriers to professional mobility remain significant. A trade agreement that formally lowers regulatory restrictions on entry for specific professions gives the Indian diaspora a legal foothold that bilateral goodwill alone could not provide.

Over 6,000 Indian establishments operate across Oman, concentrated in the Sohar and Salalah free zones. Annual bilateral trade stands at over $10 billion, and remittances from Indians in Oman run approximately $2 billion per year. The CEPA framework is designed to expand both numbers.

## Textiles and beyond

The sectoral winners are already visible. India's textile and apparel exports to Oman stood at $95.1 million in FY 2025-26, a modest figure given that Oman imports nearly $598 million in textiles annually — meaning India holds only about 16 per cent of the market. The CEPA's duty-free provisions for textiles, gems and jewellery, and food processing are designed to close that gap.

The agreement also incorporates a digital Certificate of Origin framework, eliminating much of the paperwork that has historically slowed cross-border trade. And it provides for mutual recognition of Geographical Indications — a provision that could boost the visibility of India's GI-tagged handloom and handicraft products in the Omani market, from Banarasi silk to Chanderi saris.

For Indian food exporters, the deal is particularly relevant. Although Oman's most sensitive agricultural products — fresh fruits, curd, milk, cream, frozen fish, and butter — have been excluded, the duty elimination on a broad range of processed food items opens a channel that the diaspora has long demanded. Indian grocery stores in Muscat and Salalah are a fixture of daily life for the community; cheaper import duties mean lower shelf prices.

## The port advantage

There is a geographic dimension that makes the Oman deal distinct from India's other Gulf engagements. Oman borders the Strait of Hormuz but also operates ports like Sohar that bypass the chokepoint entirely. In a region where Red Sea shipping disruptions and Iran-related tensions periodically scramble supply chains, Oman's port infrastructure offers India an alternative route to GCC markets and East Africa.

The Bhaskar English newspaper reported that the deal is part of India's broader strategy of signing agreements with economies that do not compete with India's labour-intensive export interests — a pragmatic filter that has shaped Delhi's FTA negotiations since 2014.

## What it means for the diaspora

For the Indian community in Oman — the oldest and among the most established in the Gulf — the CEPA is less a revolution than a formalisation. Indian merchant families in Muscat have traded in spices, textiles, and gold for centuries. Indian engineers and doctors staff Oman's hospitals and infrastructure projects. The community's integration into Omani economic life is deep enough that a trade agreement feels like paperwork catching up with reality.

But paperwork matters. The enhanced professional mobility provisions, the reduced trade friction, and the mutual recognition of credentials give India's Gulf diaspora something that cultural ties alone never could: legal infrastructure. And in a region where residency is precarious and rights are contingent, legal infrastructure is worth more than tariff schedules."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
