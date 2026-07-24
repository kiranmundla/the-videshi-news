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
        "headline": "The Gulf Was Supposed to Be the Weak Link. Instead, NRI Money Came Pouring In.",
        "subheadline": "War in West Asia threatened to choke the remittance pipeline that nine million Indians keep flowing home. The latest numbers show the opposite happened.",
        "slug": make_slug("gulf-nri-remittances-resilient-west-asia-conflict-fcnr-record"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the millions of Indian families whose monthly budgets are written in dirhams and riyals, the question of whether the money keeps moving is not abstract economics — it is rent, school fees and aging parents' medicine.",
        "tags": ["nri", "diaspora", "remittances", "gulf", "finance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "India Press Agency (Newspack)", "url": "https://ipanewspack.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Mint", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18341554/pexels-photo-18341554.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Dubai skyline at dusk; the UAE is the second-largest source of remittances to India after the United States.",
        "image_attribution": "Pexels",
        "body": """When refineries went quiet across the Gulf this spring and lower-level Indian workers began drifting home, India's finance ministry braced for a hit to one of the economy's most dependable arteries: the money its diaspora sends back. Nearly 9.9 million Indians live across the six Gulf Cooperation Council states, and a meaningful share of household budgets from Kerala to Punjab is denominated in dirhams and riyals. If the war in West Asia dragged on, officials warned, workers holding their cash rather than wiring it would dent remittances — and a prolonged conflict might send them back for good.

The opposite happened.

Inward remittances to India in the most recent quarter were not merely stable; they were unusually strong. Bankers tracking the flows say receipts from Gulf-based non-resident Indians actually rose, and they offered a counterintuitive explanation: geopolitical uncertainty itself nudged the diaspora to move money home faster, parking it where it felt safer. For the full year, India's net inward remittances reached roughly $144.8 billion, up from $124.6 billion the year before and more than double the figure of a decade ago. India remains, by a wide margin, the world's largest recipient of such flows — Mexico, the next in line, trails by tens of billions.

## A Pipeline That Bends Without Breaking

The resilience tells a deeper story about how the diaspora's geography has shifted. The United States is now the single largest source of remittances to India, at 27.7 percent of gross inflows, followed by the UAE at 19.2 percent, the United Kingdom at 10.8 percent, Saudi Arabia at 6.7 percent and Singapore at 6.6 percent. That is a quiet revolution. As recently as a few years ago, the Gulf dominated; the GCC's share of total remittances has slid from around 54 percent in 2017 to roughly 30 percent in 2024.

The reason is not that Gulf workers send less. It is that the composition of who leaves India has changed. A rising tide of skilled migrants — engineers, doctors, technologists — now lands in advanced economies, where salaries are higher and currencies stronger. The blue-collar worker in a Sharjah warehouse has not vanished, but he now shares the remittance ledger with a software architect in Seattle and a consultant in Singapore. That diversification is precisely what cushioned India when one region wobbled.

## The Reserve Bank's Hand on the Scale

Policy is also doing its part. The Reserve Bank of India's recent move to lift interest-rate caps on FCNR(B) and NRE deposits — letting banks dangle dollar returns of around 7 percent at the diaspora — has given Gulf NRIs a fresh reason to route money through Indian banks rather than sit on it abroad. Economists expect that scheme to support inflows in the near term, partially offsetting any softening once regional tensions ease.

There are caveats. Some of the recent surge may have been "front-loaded" — money sent early out of caution that would otherwise have arrived later — which means a quarter or two of moderation cannot be ruled out. A sustained spike in crude prices would strain the fiscal health of Gulf economies and could, eventually, slow the hiring and wage growth that underwrites remittances. But forecasters are not predicting a cliff. One bank has kept its remittance projections for the coming year broadly level with this year's record.

## What It Means at the Kitchen Table

For the diaspora, the abstraction of balance-of-payments math resolves into something intimate. Remittances are how a nurse in Abu Dhabi pays for a sibling's college in Kochi, how a mason in Doha funds a parent's surgery in Lucknow. India's foreign-exchange reserves, now around $691 billion, are buttressed in no small part by these millions of individual transfers — flows that have proven steadier than foreign direct investment or the "hot money" of portfolio flows, both of which have been in retreat.

The lesson of this spring is that the diaspora's loyalty to home is not a fair-weather phenomenon. When the region around them grew dangerous, Indians abroad did the most Indian thing of all: they sent it home. The pipeline bent. It did not break. And in an economy where capital can be skittish, that quiet dependability may be the most valuable asset India does not have to pay for."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Indian Americans Just Won Seats on Harvard's Governing Boards. Thirty Thousand Ballots Made It Happen.",
        "subheadline": "A tech executive and an Air Force reserve attorney have been elected to the university's leadership councils — a marker of how far the diaspora has climbed into the rooms where elite institutions are run.",
        "slug": make_slug("arti-garg-medha-gargeya-harvard-board-overseers-indian-american"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian Americans have long topped the income and education charts; quietly winning seats on the governing boards of America's oldest university is a different kind of arrival — moving from being counted to doing the counting.",
        "tags": ["nri", "diaspora", "harvard", "indian-american", "academia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Bazaar", "url": "https://americanbazaaronline.com/2026/06/01/two-indian-americans-win-harvard-leadership-board-seats-481873/"},
            {"name": "Harvard University", "url": "https://www.harvard.edu/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Harvard_Science_Center_from_the_Yard.jpg/1280px-Harvard_Science_Center_from_the_Yard.jpg",
        "image_caption": "Harvard University's Science Center, seen from Harvard Yard in Cambridge, Massachusetts.",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers Indian Americans tend to be celebrated for are the ones that fit on a chart: highest median household income of any group in the United States, a striking density of advanced degrees, a roster of immigrant CEOs. Less remarked upon is a slower, harder ascent — into the governance of the institutions that made those degrees mean something. This month, two more rungs were climbed.

In an election that drew more than 30,000 ballots from Harvard degree-holders around the world, voters chose data technologist Arti Garg for the university's Board of Overseers and attorney Medha Gargeya for the board of directors of the Harvard Alumni Association. Both bring South Asian heritage into the upper reaches of Ivy League governance — not as honorary guests, but as elected stewards.

## From Hayward to the Board of Overseers

Garg is a tech executive based in Hayward, California, who earned her doctorate from Harvard in 2008 and holds additional degrees from Stanford and the University of Washington. She is Executive Vice President and Chief Technologist at AVEVA, an industrial-software firm. The Board of Overseers, one of Harvard's two governing bodies, is no ceremonial perch. Established in 1642 — making it older than almost any institution on the continent — the board directs the "visitation" process, the primary mechanism by which Harvard's schools and departments are assessed by outside experts. Overseers counsel the university on priorities, plans and strategic direction. For a working technologist to sit among them is to give the diaspora a vote on how one of the world's most-watched universities measures itself.

## A Captain in the Reserves, a Lecturer at the Law School

Gargeya's path is its own study in the hyphenated American résumé. A double Harvard alumna, she earned her undergraduate degree magna cum laude in 2014 and her law degree in 2019. She is a senior associate at the law firm WilmerHale and a lecturer on law at Harvard Law School — and a Captain in the U.S. Air Force Reserves. Her three-year term on the alumni board begins on July 1. Her brief leans toward community: strengthening outreach to recent graduates, developing volunteer leadership and building inclusive alumni networks across the globe.

That global frame matters. The Harvard Alumni Association is, in effect, the connective tissue of a worldwide network — and a growing slice of that network is Indian, whether by birth, ancestry or the simple fact of having studied in Cambridge before returning to Bengaluru or Mumbai or London.

## The Quiet Part of the Diaspora Story

The American story Indian immigrants usually tell themselves is one of merit converting into money. The board seats represent a different conversion — of presence into power, of being counted into doing the counting. It is a transition that institutions often resist quietly and grant slowly. Universities, in particular, guard their governing boards as the inner sanctum where culture and capital are decided.

Harvard has spent the past two years under intense political scrutiny, its leadership and its admissions practices the subject of national argument. To win a board seat in that climate, by ballot of tens of thousands of alumni, is to be handed responsibility at a moment when the stakes of university governance feel unusually raw. Garg and Gargeya step into that.

For the broader diaspora, the elections land as a familiar but never tired signal. The first generation arrived to study and to work, often with the explicit understanding that the institutions they joined were not theirs to shape. Their children — and, increasingly, they themselves — are being asked to shape them anyway. A data scientist directing how Harvard audits its own schools; a reservist-lawyer knitting together its alumni: these are not the headline-grabbing appointments of a Sundar Pichai or a Satya Nadella. They are something quieter and, arguably, more structural.

When the diaspora's children look at who runs the institutions they aspire to, they will increasingly see names they recognize from their own dinner tables. That recognition — more than any income statistic — is what arrival actually looks like."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "In Paris, Modi Told the Diaspora They Are India's Reflection Abroad. The Crowd Believed Him.",
        "subheadline": "Addressing Indians in the City of Light, the prime minister framed the expatriate community not as people who left, but as ambassadors carrying the country's values onto foreign soil.",
        "slug": make_slug("modi-paris-indian-diaspora-address-france-soft-power-values"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every diaspora lives with a low hum of guilt about leaving; a prime minister telling a Paris auditorium that they are the nation's mirror abroad is an answer to a question Indians overseas never stop asking themselves.",
        "tags": ["nri", "diaspora", "modi", "france", "soft-power"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "IANS Live", "url": "https://ianslive.in/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
        "image_caption": "The official portrait of Narendra Modi, Prime Minister of India.",
        "image_attribution": "Wikimedia Commons",
        "body": """"Paris is a city of lights, colours, ideas and innovation," Narendra Modi told a hall packed with Indians who had made the French capital their home. Then he gave them their lines. The diaspora, he said, had added to that vibrancy by bringing India's "rich cultural diversity" — and in doing so had become a living reflection of the country they left behind.

It is a familiar piece of stagecraft from a prime minister who has turned the diaspora address into a signature genre, from Madison Square Garden to Wembley to, this week, Paris. But the familiarity does not blunt its effect on the people in the room. To a community that lives with the quiet ambivalence of having left, being told you are the nation's mirror abroad is not a throwaway flourish. It is an absolution.

## The Many Indias in One European City

Modi worked the geography of the crowd deliberately, noting that Tamils, Punjabis, Gujaratis, Marathis and Bengalis were all represented in the Paris diaspora — every corner of India folded into one European auditorium. The diaspora, he said, had "brought new colours" to the city and served as a reflection of India's unity in diversity. It is a message tuned precisely to an audience that often experiences its Indianness more sharply abroad than it ever did at home, where regional identity tends to crowd out the national one.

The Paris stop carried an extra texture because France has become one of India's more enthusiastic strategic partners, and because the diaspora there is genuinely woven into that relationship. Cultural ensembles turned out for the welcome — the Dhoad Gypsies of Rajasthan, the Jaipur Maharaja Brass Band — and students spoke of the two-year work permits that the India-France friendship has opened up for young Indians. "I feel honoured to be an Indian citizen and to have met the Prime Minister," one said. The sentiment was less about policy than belonging.

## A Speech Aimed Two Ways

Modi's address, as ever, pointed in two directions at once. To the diaspora in front of him, it offered recognition. To the audience watching back home and online, it offered a narrative of national ascent. "When historians look back 50 or 100 years from now," he said, "one fact will stand out: this era was driven by the aspirations of the people of India. This is a new age of Indian aspirations." He pressed the theme of transformation — "what was once a dream is now a reality" — and then, in a characteristic move, deflected the credit. "It is not because of Modi. It is because of the people of India," he said. "When everyone progresses together, the nation progresses together."

For the expatriates listening, that framing does specific work. It recasts their own leaving as part of the national project rather than a defection from it. The engineer in Toulouse, the researcher at a Paris lab, the student on a work permit — all are invited to see themselves not as people who chose France over India, but as Indians extending India's footprint into France.

## The Politics of the Mirror

There is, of course, a transactional logic beneath the warmth. India has been increasingly explicit about wanting its roughly 35-million-strong diaspora to act as informal ambassadors — selling the country to their foreign friends, championing its causes, investing back home through schemes like the freshly sweetened NRI deposit accounts. The "you are India's reflection" message is the emotional companion to that economic ask. Flattery and mobilization travel together.

But it would be too cynical to reduce the Paris evening to strategy. For many in the hall, the encounter was simply moving. The diaspora performers who welcomed Modi spoke of him arriving "as though a member of our own family had come." That is the register these events operate in — somewhere between a state function and a family reunion.

The deeper truth Modi keeps tapping is that the diaspora never fully stops asking whether it made the right choice. Every NRI carries some version of the question. A prime minister standing in Paris, telling them they are the country's living reflection abroad, hands them an answer they can carry home to their flats in the 13th arrondissement: you didn't leave India. You brought it with you."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
