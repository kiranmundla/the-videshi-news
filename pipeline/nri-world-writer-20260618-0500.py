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
    "headline": "An Indian-Born Banker Will Run America's Fifth-Largest Bank. The Diaspora Has Run Out of First Times to Celebrate.",
    "subheadline": "Gunjan Kedia takes the helm at U.S. Bancorp this spring, becoming the first Indian American to lead a top-tier U.S. bank. The milestone is striking precisely because the diaspora is running out of ceilings to break.",
    "slug": make_slug("gunjan-kedia-us-bancorp-first-indian-american-bank-ceo-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian Americans have long dominated the C-suites of American technology and consumer goods. Banking, the most conservative corner of corporate America, was the last big holdout — and a diaspora woman just took its keys.",
    "tags": ["nri", "diaspora", "gunjan-kedia", "us-bancorp", "banking", "indian-american"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/u-s-bancorp-appoints-gunjan-kedia-as-first-indian-american-ceo/"},
        {"name": "U.S. Bancorp (NYSE: USB) announcement", "url": "https://www.usbank.com/about-us-bank/company-blog.html"}
    ]),
    "score_total": 80,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/70/US_Bancorp_Center_Minneapolis_1.jpg",
    "image_caption": "The U.S. Bancorp Center in Minneapolis, headquarters of the bank Gunjan Kedia will lead as CEO.",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": """When the list of Indian-origin chief executives at America's largest companies is read aloud — Nadella at Microsoft, Pichai at Alphabet, Narayen at Adobe, Subramaniam at FedEx, soon Jejurikar at Procter & Gamble — one industry has always been conspicuously missing. Banking, the most hidebound and credential-obsessed corner of corporate America, never produced a diaspora name at the very top of a marquee institution. That gap has now closed.

Gunjan Kedia, currently president of U.S. Bancorp, will become chief executive officer of the Minneapolis-based bank at the close of its annual shareholder meeting on April 15, the company announced. She was also elected to the board of directors. Andy Cecere, who has run the bank for nearly eight years, becomes executive chairman. U.S. Bancorp is the fifth-largest commercial bank in the United States, which makes Kedia the first Indian American to lead a U.S. bank of that size.

## The last ceiling

The symbolism is heavier than the usual corporate succession note. American banking is not technology. It does not lionize the immigrant outsider who arrives with a degree and an accent and rewrites the rules. It rewards people who spent decades inside the institution, who understand regulators and risk committees, and who look the part in a way that has historically been narrow. For a woman born and educated in India to rise to the apex of that world is a different kind of arrival than another software CEO.

"One of the hallmarks of U.S. Bancorp is its thorough and measured approach to succession planning," said lead independent director Roland Hernandez, framing the handover as the product of years of internal grooming rather than an outside rescue. That framing matters: Kedia is not a celebrity hire parachuted in to fix a crisis. She is the inside candidate who won on merit, which is the harder and more durable kind of win.

## A familiar arc, an unfamiliar address

Kedia's path will read as familiar to many in the diaspora — an education that began in India, a move west, and a steady climb through some of the most demanding institutions in American finance, including senior roles at State Street and Bank of New York Mellon before U.S. Bancorp. What is unfamiliar is the destination. The diaspora's corporate success has clustered in technology, pharmaceuticals, consulting and consumer goods. Wall Street and the big commercial banks, with their clubby cultures and their long memories, were the stubborn exception.

That exception is precisely why the news lands the way it does. For Indian American professionals who chose finance — and there are many, in trading floors and risk departments and back offices across New York, Charlotte and Minneapolis — Kedia's appointment removes the quiet caveat that always trailed their ambition: that the very top was, for people like them, effectively closed.

## Running out of firsts

There is a curious melancholy buried inside these milestones. Each "first Indian American to..." headline is a celebration, but it is also a reminder of how recently the door was shut. The diaspora has now produced firsts in software, hardware, pharmaceuticals, consulting, accounting, consumer goods, hospitality and, now, big-bank leadership. The supply of unbroken ceilings is dwindling.

That is the real story of Kedia's promotion. It is less about one executive than about a generational shift reaching its logical conclusion: the children and grandchildren of immigrants who arrived in the 1960s and 1970s are no longer breaking into the establishment. In an increasing number of boardrooms, they *are* the establishment.

## What it signals

For younger Indian Americans weighing careers in finance, the message is unambiguous. The path that once seemed to plateau at managing director or divisional head now visibly runs all the way to the corner office of a top-five bank. Representation at the summit changes how the people below it calculate their own odds.

Kedia will inherit a bank navigating a higher-rate environment, intensifying competition from fintech, and the perennial pressure to grow without taking on reckless risk. Those are ordinary executive challenges. The extraordinary part happened the moment her name was read into the record — a diaspora that has spent decades collecting firsts just claimed one of the last big ones left."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "Nine Million Indians Abroad Sent Home $138 Billion. A Proposed 5% U.S. Tax Could Take a Bite Out of It.",
    "subheadline": "India remains the world's largest remittance recipient by a wide margin. But a proposed American levy on outbound transfers, and a volatile balance of payments, are reminding everyone how exposed those diaspora dollars really are.",
    "slug": make_slug("india-remittances-138-billion-us-5-percent-tax-diaspora-dollars"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "For the NRI sending money to parents in Kerala or a sister's wedding in Lucknow, remittances are personal. In aggregate they are macroeconomic infrastructure — and policy in Washington and Delhi now treats the diaspora's money as a strategic asset to be courted or taxed.",
    "tags": ["nri", "diaspora", "remittances", "nre-nro", "rbi", "fcnr", "nri-finance"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters — India balance of payments", "url": "https://www.reuters.com/world/india/"},
        {"name": "Livemint — Diaspora dollars", "url": "https://www.livemint.com/"},
        {"name": "The Hindu BusinessLine — SBI Research", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Indian rupee notes and coins — remittances now exceed $135 billion a year, the largest such flow in the world.",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": """Every month, tens of millions of Indians working abroad perform the same quiet ritual: they move money home. A nurse in Abu Dhabi, an engineer in New Jersey, a construction supervisor in Riyadh — each transfer is small, personal, and unremarkable. In aggregate, they add up to the single largest flow of its kind on earth.

According to the International Organization for Migration's World Migration Report 2026, India received nearly $138 billion in remittances in 2024, more than double the roughly $53 billion it took in back in 2010. Mexico, the next-largest recipient, was a distant second at about $68 billion. India has now held the world's top spot for more than 25 consecutive years, and SBI Research projects FY26 inflows will hit a fresh record of $137–140 billion before settling around $135–137 billion the following year.

## From safety valve to strategic asset

For most of that history, remittances were treated as a humble safety valve — money that kept households in Kerala, Uttar Pradesh and Bihar afloat, covering school fees, hospital bills and home loans. That framing is changing. With foreign portfolio investors pulling money out of Indian equities and net foreign direct investment running thin, the diaspora's steady dollars have quietly become one of the most reliable props under India's external accounts.

The numbers show why policymakers care. India's overall balance of payments slipped into a $6.6 billion deficit in April as capital flowed out, even as the current account swung to a $4.7 billion surplus. Net transfers — which include worker remittances — jumped to $16 billion for the month, up from $9.4 billion a year earlier. Without that diaspora cushion, the external picture would look considerably more fragile. The Reserve Bank of India has gone a step further, drawing dollars directly from non-resident Indians through a subsidised swap scheme to shore up the rupee.

## The tax cloud from Washington

That reliance is exactly why a proposal taking shape in the United States has set off alarm bells. A mooted 5% levy on outbound remittances from the U.S. could, by one Global Trade Research Initiative estimate, reduce India's dollar inflows by 10–15%. The U.S. is one of the largest single sources of remittances to India, and a tax on transfers would land squarely on the diaspora — taxing money that has already been earned and taxed once.

"The pain wouldn't stop at the exchange rate," the GTRI report warned. "In states like Kerala, Uttar Pradesh and Bihar, millions of families rely on remittances to cover essential expenses such as education, healthcare and housing. A sudden decline in these flows could hit household consumption hard." India is not alone in its exposure — El Salvador, where remittances exceed 25% of GDP, and Mexico would feel a similar squeeze — but India's sheer volume makes it the most consequential case.

## Delhi's counter-move: court the capital

While Washington weighs a tax, Delhi is trying to pull diaspora money deeper into the economy. The 2026 Union Budget doubled the individual investment limit under the Portfolio Investment Scheme from 5% to 10% and raised the aggregate cap to 24%, an explicit attempt to convert consumption-oriented remittances into stickier, long-term equity capital. It also simplified property transactions involving non-residents, scrapping the cumbersome TAN requirement for resident buyers purchasing from NRIs in favour of a PAN-based system — removing a long-standing headache for diaspora families trying to sell or transfer Indian property.

## What it means for the NRI

For the individual sender, the macroeconomics can feel abstract. But the policy currents are converging on the same wallet. A U.S. transfer tax would raise the cost of supporting family back home. India's new investment incentives, meanwhile, offer a more attractive return on NRE and NRO balances and on Indian equities than NRIs have seen in years.

The lesson buried in the figures is that the diaspora's money is no longer taken for granted by anyone. Two governments now treat it as a lever — one tempted to tax it, the other racing to court it. For the nine million Indians abroad doing the monthly ritual of sending money home, that scrutiny is a backhanded compliment: their quiet transfers have become big enough to move a national economy."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "A TV Host Mocked Indians for Loving Mangoes. The Diaspora's Reply Was a Lesson in What 'Home' Tastes Like.",
    "subheadline": "A throwaway segment ridiculing the WhatsApp groups Indian Americans use to buy seasonal mangoes turned into a referendum on belonging — and on how a single fruit carries an entire community's idea of home.",
    "slug": make_slug("indian-mango-row-diaspora-backlash-belonging-whatsapp-identity"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Few things capture the diaspora's split existence like the summer mango hunt — the WhatsApp coordination, the costly imported boxes, the ritual of tasting a flavour from childhood thousands of miles from where it grew. When that ritual was mocked, the reaction revealed how much identity a community can pack into a fruit.",
    "tags": ["nri", "diaspora", "mango", "indian-american", "identity", "culture"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "American Bazaar", "url": "https://americanbazaaronline.com/2026/06/06/indian-mango-row-sparks-diaspora-backlash-482303/"},
        {"name": "Consulate General of India, Seattle / APEDA", "url": "https://indiainseattle.gov.in/"}
    ]),
    "score_total": 70,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16882398/pexels-photo-16882398.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A heap of ripe yellow mangoes on display — the seasonal fruit at the centre of a diaspora identity row.",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": """There is a particular madness that overtakes Indian American households every late spring. Group chats light up. Spreadsheets appear. Someone's cousin knows a distributor, and a coordinated order goes out for boxes of Banganapalli, Kesar or Alphonso mangoes — fruit so expensive by the time it clears customs that buying it makes no rational economic sense at all. People do it anyway, because the mango is not really a fruit. It is a taste of a childhood that exists nine thousand miles away.

So when conservative commentator Sara Gonzales devoted airtime to mocking exactly this ritual — ridiculing the WhatsApp groups Indian Americans use to coordinate mango buys and suggesting the fruit's popularity was driven by immigrants rather than "mainstream" American consumers — the response was swift and disproportionate to the slight. Across social media, members of the diaspora accused her of trafficking in xenophobic stereotypes. What looked like a minor culture-war jab had landed on something far more tender than Gonzales seemed to realise.

## Why a fruit hits a nerve

To understand the backlash, you have to understand what the mango represents to a diaspora that lives perpetually between two worlds. The annual hunt for a decent Alphonso is a small act of cultural maintenance — a way of importing, quite literally, a piece of home into a suburban American kitchen. The WhatsApp coordination Gonzales found so mockable is not eccentric; it is community infrastructure, the same networks that organise temple visits, carpools and the search for a good Indian grocer.

Mocking the mango, then, read to many as mocking the entire project of holding onto an identity while building a life elsewhere. It is the kind of slight that stings precisely because it targets something the community had assumed was private, harmless and its own.

## The facts behind the jab

Gonzales also cited Japan's recent suspension of fresh Indian mango imports, claiming the fruit posed health risks. The record is less dramatic than the insinuation. Reports on Japan's decision attributed the suspension to deficiencies in fumigation and phytosanitary procedures at certain export facilities — a paperwork-and-process problem — rather than any contamination of the fruit itself. The health-scare framing did not survive contact with the details.

Meanwhile, the mango's American footprint keeps growing, and not only among Indians. Retailers including Costco have expanded their imported Indian varieties, and demand has surged despite eye-watering prices. Indian diplomatic missions have leaned in: the Consulate General of India in Seattle partnered with India's Agricultural and Processed Food Products Export Development Authority to host mango promotion events across the Pacific Northwest, showcasing Dussehri, Langra, Chausa and Banganapalli to curious American palates.

## A bigger argument under the peel

For many Indian Americans, the dispute was never really about fruit. Community advocates noted that the reaction reflects deeper tensions — over immigration, over skilled-worker visas, and over the increasing visibility of Indian Americans in business, technology and public life. The mango became a convenient proxy for a more uncomfortable question: whether a community that has grown prosperous and prominent is still expected to apologise for its tastes, its networks and its difference.

That is the strange weight a piece of seasonal produce can be made to carry. The diaspora's defenders were quick to draw the line that mattered — criticism of trade rules or import regulations is fair game; ridicule aimed at the communities that made Indian mangoes a sought-after American delicacy is something else entirely.

## What home tastes like

The episode will fade, as these online flare-ups do. But it offered an unusually clear window into the emotional economics of the diaspora. A community will pay absurd sums, build elaborate logistics, and mobilise instantly in defence of a fruit — not because the fruit is worth it on any spreadsheet, but because of what it stands in for.

For the immigrant generation, the first bite of a properly ripe Alphonso each summer is a small annual homecoming. For their American-born children, it is an inheritance — a flavour that connects them to a place they may have visited only a handful of times. Mock that, and you are not mocking a fruit. You are mocking the lengths people will go to so that home, however far away, still tastes like home."""
}
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
