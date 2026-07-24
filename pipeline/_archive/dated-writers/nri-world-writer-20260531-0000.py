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
        "headline": "Your Ancestral Home in Punjab Was Just Sold. You Weren't There. You Didn't Know. A Court Says This Is Now a Pattern.",
        "subheadline": "A Punjab and Haryana High Court ruling lays bare the growing epidemic of property fraud targeting NRIs — and explains why most victims never get their land back.",
        "slug": make_slug("nri-property-fraud-punjab-high-court-impersonation-epidemic"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Millions of NRIs own property in India they rarely visit. This court case exposes how their absence is being systematically exploited — and what they can do before it happens to them.",
        "tags": ["nri", "diaspora", "property", "punjab", "fraud", "legal", "high-court"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "LinkedIn / Col. CVS Sehgal", "url": "https://www.linkedin.com/pulse/real-court-case-nri-loss-cvs-sehgal-97dqc"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/things-nris-should-keep-in-mind-while-selling-property-in-india"},
            {"name": "Punjab and Haryana High Court (Bagel Singh v. State of Punjab)", "url": "https://indiankanoon.org"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8362585/pexels-photo-8362585.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On 21 February 2025, a routine inspection at a Sub-Registrar's office in Ludhiana turned up a transaction that looked perfectly ordinary. A sale deed, registered ten days earlier, had transferred a 14-kanal property in Village Noorpur Bet-2. The paperwork was complete. The stamps were in order. The money had changed hands.

There was one problem. The actual owner — a Non-Resident Indian living abroad — had never authorised the sale. He didn't even know it had happened.

Someone had walked into the Sub-Registrar's office, impersonated the NRI owner, and executed a sale deed. Revenue officials, according to the subsequent police investigation, were allegedly complicit in the transaction. The fraud was discovered only because a routine audit flagged irregularities. Without that inspection, the NRI might not have learned of the theft for years.

## A Judge Names the Pattern

The case eventually reached Justice Harpreet Singh Brar of the Punjab and Haryana High Court, via anticipatory bail applications filed by two of the accused — Bagel Singh and Raghuvir Singh. Justice Brar refused bail. But it was his language that carried the real weight.

"This case is yet another example of a disturbing trend that is steadily gaining ground," he wrote, "wherein unscrupulous individuals take advantage of Non-Resident Indians, particularly those who are unable to visit India frequently or manage their properties here."

The court went further: "The scale of this deceit is symptomatic of systemic abuse — where absence is weaponised and legal safeguards are routinely undermined."

These are not the words of a judge describing a rare occurrence. "Yet another example." "Steadily gaining ground." "Systemic abuse." This is a jurist who has seen this pattern enough times to call it exactly what it is: an epidemic.

## Why the NRI Almost Never Wins

The legal mechanics make the situation worse. When a property is fraudulently sold to an innocent third-party buyer — someone who paid market value and had no knowledge of the deception — Indian courts generally uphold the sale under the doctrine of "bona fide purchaser for value without notice." The buyer keeps the property. The NRI's legal remedy is against the fraudster, not the land.

And the fraudster, in most cases, has disappeared.

Colonel CVS Sehgal, a retired military officer who has spent four decades in Punjab real estate, has catalogued the most common fraud patterns: NRIs granting General Powers of Attorney to relatives who then sell the property without consent; identities being impersonated at Sub-Registrar offices with the assistance of revenue staff; forged sale deeds registered using fabricated documents; and NRIs discovering the fraud only on a visit to India, sometimes years after the fact.

## The Diaspora's ₹14 Lakh Crore Exposure

The scale of NRI financial engagement with India makes this more than an anecdotal concern. Total NRI deposits in Indian banks stood at approximately ₹14.16 lakh crore ($164.7 billion) as of March 2025. Property holdings add substantially to that exposure. A significant portion of this wealth is held in real estate across Punjab, Haryana, Kerala, Gujarat, and Andhra Pradesh — states with large emigrant populations and correspondingly large volumes of absentee-owned property.

India's Budget 2026 attempted to address some compliance friction for NRIs, including simplified TDS procedures on property transactions and a one-time foreign asset disclosure window. But none of these measures directly address the physical vulnerability of property left unattended for years while its owner lives in Toronto or Houston or Dubai.

## Three Defences That Actually Work

Property consultants who specialise in NRI cases consistently recommend the same three measures:

**Never grant a General Power of Attorney.** A Specific POA — limited to one transaction, one property, registered with the Sub-Registrar, with a hard expiry of six months — is the only defensible instrument. Revoke it in writing the moment it is no longer needed. Register the revocation.

**Run an annual encumbrance certificate check.** This reveals whether any transaction — legitimate or fraudulent — has been registered against your property. It is available online in most states and takes ten minutes. Treat it like a credit check: do it every year without fail.

**Appoint a named custodian** who physically visits the property monthly and photographs it with a date stamp. Not a vague family understanding. A specific person with specific accountability and a documented trail.

The Punjab and Haryana High Court has sent a clear signal: the judiciary recognises the pattern and is willing to deny bail to perpetrators. But courts move slowly, and prevention costs a fraction of what litigation does. For the estimated 18 million NRIs and PIOs who own property in India, the lesson from Ludhiana is stark. Your absence is being noticed — and not only by your family."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Canada's Duty-Free Shops Just Got an 'Indian Aisle.' It Matters More Than You Think.",
        "subheadline": "Indian beverages have landed in airport duty-free stores across Toronto, Vancouver, and Alberta — the first time Indian brands have occupied premium retail space in Canada's travel corridor.",
        "slug": make_slug("indian-aisle-canada-duty-free-gwns-beverages-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For decades, Indians abroad have carried products from home in suitcases. Now Indian brands are arriving through the front door of international retail — and the 1.9 million-strong Canadian Indian diaspora helped make it possible.",
        "tags": ["nri", "diaspora", "canada", "business", "culture", "trade", "beverages"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/29/great-white-northern-spirits-launches-indian-aisle-in-canada/"},
            {"name": "The Indian Eye / Piyush Goyal Canada visit", "url": "https://theindianeye.com/2026/05/29/piyush-goyal-lauds-role-of-indian-diaspora-in-canada/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/25383731/pexels-photo-25383731.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On 21 May 2026, at a launch event in Brampton, Ontario, a company called Great White Northern Spirits did something that sounds mundane but actually isn't: it placed Indian beverage products on the shelves of Canadian duty-free stores.

Not in an ethnic grocery aisle. Not at a diaspora festival booth. In the duty-free retail corridor — the premium commercial space that travellers encounter at Toronto Pearson International Airport, Vancouver International Airport, key airports across Alberta, and major land-border crossings in Ontario and British Columbia.

The initiative, branded "Indian Aisle in Canada," represents the first time Indian beverage brands have been positioned in Canada's duty-free ecosystem alongside Scotch, French wine, Japanese whisky, and the other products that have long dominated international travel retail. A ribbon-cutting ceremony at Brampton's Nuvo Event Space drew government officials, diplomatic representatives, cultural leaders, and trade stakeholders.

## Beyond Commerce

The temptation is to file this under "product launch" and move on. But for the Indian diaspora in Canada — estimated at 1.9 million people, with over 400,000 in British Columbia alone — the symbolism runs deeper than shelf space.

For decades, Indian consumer products have existed in a parallel retail universe in Western countries: ethnic grocery stores, community-run importers, the odd Haldiram's packet in the international section of a large supermarket. The products were there because the diaspora demanded them, but they were segregated — culturally and commercially — from mainstream retail.

The duty-free channel is different. It is premium, international, and curated. Products placed there carry an implicit endorsement: this belongs here, alongside the best the world produces. For Indian brands, it is less about the revenue from airport sales and more about the positioning statement. The same shift has happened over the past decade with Indian cuisine, Indian fashion, and Indian cinema — each gradually moving from niche to mainstream in Western markets.

"Today is not just about launching products into a new market," said Balaji Nagaraja and Pooja S, founders of GWNS. "It is about opening doors for Indian heritage, craftsmanship and stories to travel globally."

## The Timing Is Not Accidental

The launch coincided with a broader thaw in India-Canada commercial relations. Just days later, Union Commerce Minister Piyush Goyal concluded a three-day visit to Canada — his first — focused on trade, investment, and the ongoing negotiations for the India-Canada Comprehensive Economic Partnership Agreement (CEPA).

Goyal's itinerary read like a diplomatic tour: meetings with Ontario Premier Doug Ford to discuss manufacturing and clean energy; a keynote at the University of Toronto's Munk School of Global Affairs; discussions with the Ontario Centre of Innovation on artificial intelligence and quantum computing; and engagement with regional business chambers operating in the India-Canada trade corridor.

At every stop, the minister highlighted the Indian diaspora's role as an economic bridge. The ministry's official readout described the engagements as reinforcing "the sustained momentum in the India-Canada economic partnership" and positioning India as "a premier global destination for investment, technology collaboration, and long-term partnerships."

## What the Diaspora Built

Canada is home to one of the fastest-growing Indian-origin populations in the world. In British Columbia, Premier David Eby has spoken openly about the Indo-Canadian community as an asset in building commercial connections with India. Former BC premier Ujjal Dosanjh, a Pravasi Bharatiya awardee, has urged the diaspora to take pride in its heritage while recognising the economic leverage that comes with demographic weight.

That weight is now visible in retail. Indian restaurants are no longer exotic in Vancouver or Toronto — they are neighbourhood establishments. Indian grocery chains operate at scale. And now, Indian beverages sit in the same duty-free cabinets where travellers have always reached for single malts and champagne.

The Indian Aisle is a small initiative by global retail standards. But it represents something the diaspora has spent decades building toward: the normalisation of Indian products in international commercial spaces, not as curiosities, but as contenders. For the NRI who has spent years explaining Indian chai or bringing back bottles in checked luggage, it is a quiet, commercial vindication."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Commerce Minister Just Toured Canada for Three Days. The Diaspora Was the Subtext of Every Meeting.",
        "subheadline": "Piyush Goyal's visit to Toronto and Ottawa was officially about CEPA negotiations and clean energy. Unofficially, it was a demonstration of how 1.9 million Indo-Canadians have become India's most effective trade envoys.",
        "slug": make_slug("piyush-goyal-canada-cepa-diaspora-trade-investment"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "India's trade diplomacy increasingly treats its diaspora not as a sentimental connection but as economic infrastructure. Goyal's Canada trip made that explicit.",
        "tags": ["nri", "diaspora", "canada", "trade", "cepa", "piyush-goyal", "investment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/29/piyush-goyal-lauds-role-of-indian-diaspora-in-canada/"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Piyush_Goyal"},
            {"name": "Ministry of Commerce & Industry, India", "url": "https://commerce.gov.in"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "body": """When India's Commerce Minister Piyush Goyal wrapped up a three-day visit to Canada on 28 May 2026, the official communiqués spoke the expected language of trade corridors, investment partnerships, and bilateral economic momentum. But beneath every meeting, every keynote, every handshake with Ontario's business establishment, the same quiet force was at work: the Indian diaspora.

Goyal's visit — which took him to Toronto and Ottawa — was ostensibly about advancing the India-Canada Comprehensive Economic Partnership Agreement (CEPA), a trade pact that has been under negotiation for years. But his itinerary told a more nuanced story about how India has come to view its overseas communities: not as nostalgic ties to be celebrated at annual conventions, but as functional economic infrastructure that can accelerate bilateral commerce.

## The Itinerary as Strategy

Start with the academic stop. Goyal addressed faculty, researchers, and students at the University of Toronto's Munk School of Global Affairs and Public Policy. The topic was India's economic trajectory and the opportunities in bilateral trade. But the audience composition mattered as much as the content — Toronto's universities are dense with Indian-origin students, researchers, and academics who form the connective tissue between Canadian institutions and Indian industry.

Then came the innovation visit. The Ontario Centre of Innovation and Canada-India Tech Connect became the venue for discussions on artificial intelligence, quantum computing, cleantech, and agritech. These are not abstract sectors — they are precisely the domains where Indian-Canadian entrepreneurs and engineers are disproportionately represented.

The political meeting carried the heaviest commercial weight. Goyal met Doug Ford, Ontario's premier, to discuss manufacturing, infrastructure, clean energy, food processing, and critical minerals. Ontario is home to the largest concentration of Indo-Canadians in the country, and Ford's government has been increasingly attuned to the economic interests and connections that community represents.

## The CEPA Negotiations

The India-Canada CEPA has moved in fits and starts. Diplomatic relations between the two countries have been turbulent in recent years, with political tensions occasionally freezing economic dialogue. But trade numbers have their own logic. Bilateral trade has been climbing, and both sides recognise that a comprehensive partnership agreement would formalise what the diaspora has been building informally for decades.

Goyal's ministry described the visit's engagements as reinforcing "the sustained momentum in the India-Canada economic partnership" and highlighting India as "a premier global destination for investment, technology collaboration, and long-term partnerships." The language is diplomatic boilerplate, but the intent is clear: India wants Canadian capital, Canadian technology partnerships, and Canadian market access. The diaspora is how it plans to get them.

## The Bridge Community

The Indo-Canadian community's role as economic intermediary is not new, but it has scaled dramatically. At roughly 1.9 million people, Indo-Canadians are the third-largest visible minority group in the country. In British Columbia, where the community exceeds 400,000, Premier David Eby has spoken about the Indian-origin population as a strategic asset for commercial engagement with India.

This community is not simply sending remittances home. Its members run technology companies, sit on hospital boards, manage investment portfolios, teach at universities, and operate supply chains that cross the Pacific. When Goyal met with regional chambers and business leaders "operating in the India-Canada corridor," he was meeting people who live in that corridor — who navigate its regulatory peculiarities, its cultural expectations, and its commercial opportunities every day.

## What the Visit Signals

India's trade diplomacy has undergone a conceptual shift over the past decade. The diaspora was once treated primarily as a cultural asset — people who could be invited to Pravasi Bharatiya Divas, honoured for their achievements, and asked to invest in Indian bonds during currency crises. That framing has not disappeared, but it has been supplemented by something harder-edged: the recognition that overseas Indians are, collectively, a trade facilitation network that no government programme could replicate.

Goyal's three days in Canada were a practical demonstration of this shift. Every meeting had a diaspora dimension — not as sentimental backdrop, but as operational reality. The Indian-Canadian entrepreneur who runs an AI startup in Toronto is not just a success story for the Pravasi Bharatiya programme. She is a potential channel for Indian technology exports, a possible investor in Indian infrastructure, and a living argument for why a CEPA makes commercial sense.

The minister's visit has ended. The negotiations continue. But the subtext is already settled: India-Canada trade will be built by the people who already live in both countries."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
