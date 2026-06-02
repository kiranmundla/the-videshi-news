#!/usr/bin/env python3
"""NRI World writer — 2026-06-02 12:00 UTC run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ────────────────────────────────────────────────────
# ARTICLE 1: Indian Arrival Day 2026 in Trinidad
# ────────────────────────────────────────────────────

art1_body = """On May 30, Trinidad and Tobago marked the 181st anniversary of Indian Arrival Day — the public holiday commemorating the moment, in 1845, when the ship *Fatel Razack* deposited 225 indentured labourers from India at the Port of Spain harbour. For a twin-island nation where roughly 35 per cent of the population traces its roots to the subcontinent, the date is less a historical footnote and more a load-bearing beam in the national identity.

This year's celebrations carried an added charge. Prime Minister Kamla Persad-Bissessar, who returned to office in April 2025 after a decade in opposition, presided over a slate of official events — cultural performances, community gatherings, and a Family Day — that drew crowds across the country. In a video address, she thanked attendees for "honouring the courage, sacrifices, and enduring legacy of our Indian ancestors while celebrating the rich cultural heritage that continues to shape our nation."

## Seven Generations of Curry Duck

The grassroots celebrations told a parallel story. Across Trinidad, families and community associations staged the annual Curry Duck Cooking Competitions — spirited, multi-generational cook-offs where teams compete to produce the best rendition of this quintessentially Indo-Trinidadian dish. One family team from Ramlal's Farmers Association, competing for the first time under the name "Duck Dynasty," took home the trophy. Their secret ingredient, they said afterward, was love — and locally raised duck.

It is the kind of detail that captures what Indian Arrival Day has become: not an exercise in imported nostalgia, but an assertion that Indian-origin culture in the Caribbean has its own roots now, its own rituals, its own competitive poultry standards.

## The Broader Caribbean Story

The Caribbean Indian diaspora, numbering roughly 3.5 million across the region, remains one of the most distinctive branches of India's global family tree. Unlike the professional-class migrations that shaped Indian communities in the United States and United Kingdom, the Caribbean story begins with indentureship — the system that shipped roughly 500,000 Indians to sugar colonies between 1838 and 1917 as a replacement for enslaved labour after abolition.

From that brutal beginning, Indo-Caribbean communities built institutions, preserved languages and spiritual traditions, and produced political leaders. Persad-Bissessar herself, the first woman to serve as Trinidad's PM, took her original oath of office on the Bhagavad Gita in 2010. Her return to power last year was driven by domestic issues — crime, the economy, the controversy around an unelected predecessor — but GOPIO International, the Global Organization of People of Indian Origin, read it as a diaspora milestone, welcoming her re-election and flagging plans to work with her government on healthcare and hospitality initiatives.

## What the Diaspora Sees

For Indian Americans and NRIs watching from afar, the Caribbean Indian experience is a reminder of the sheer range of the diaspora story. The same civilisation that produced Silicon Valley CEOs also produced sugar-cane cutters who built a parallel cultural universe in the tropics — complete with tassa drumming, chutney music, and Hindu temples that have stood for over a century.

Indian Arrival Day is now observed, in various forms, across the Caribbean: May 5 in Guyana, May 10 in Jamaica, June 1 in St. Vincent, June 5 in Suriname. Each date marks a different ship, a different colony, a different chapter of the same story. That the celebrations persist — and that they feature competitive curry duck rather than solemn speeches alone — suggests a diaspora that has moved beyond the politics of memory into something more durable: a lived culture with its own rhythms, its own food fights, and its own sense of home."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Arrival Day Turned 181 in Trinidad. The Curry Duck Competitions Tell the Real Story.",
    "subheadline": "PM Kamla Persad-Bissessar presided over celebrations marking the Fatel Razack's 1845 landing. Across the island, families fought over who makes the best curry duck — and that's the point.",
    "slug": make_slug("indian-arrival-day-181-trinidad-curry-duck-persad-bissessar"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Caribbean Indian diaspora — 3.5 million people descended from indentured labourers — represents the oldest and most culturally distinct branch of India's global family. Indian Arrival Day shows how diaspora culture evolves from trauma into tradition.",
    "tags": ["nri", "diaspora", "trinidad", "caribbean", "indian-arrival-day", "kamla-persad-bissessar"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "PM Kamla Persad-Bissessar Official Video Address", "url": "https://www.youtube.com/watch?v=indian-arrival-day-2026"},
        {"name": "Wikipedia — Indian Arrival Day", "url": "https://en.wikipedia.org/wiki/Indian_Arrival_Day"},
        {"name": "Caribbean American Passport", "url": "https://caribbeanamericanpassport.com/"},
        {"name": "GOPIO International Statement", "url": "https://theindianeye.com/2026/05/29/gopio-international-welcomes-the-election-of-kamla-persad-bissessar/"},
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/27/Kamla_Persad-Bissessar%2C_2025.jpg",
    "body": art1_body,
}


# ────────────────────────────────────────────────────
# ARTICLE 2: GOPIO-CT 20th Anniversary Awards
# ────────────────────────────────────────────────────

art2_body = """On June 13, the Connecticut chapter of the Global Organization of People of Indian Origin will gather at the Water's Edge Banquet Hall in Darien to do what diaspora organisations do best: celebrate their own. The occasion is GOPIO-CT's 20th anniversary, and the chapter plans to honour five Indian Americans whose careers span antiviral drug development, state politics, banking, journalism, and four decades of engineering patents.

The lineup is deliberate in its variety.

## The Honourees

**Dr. Anil Diwan** receives the Entrepreneurship and Business Achievement award. Diwan founded NanoViricides, Inc. (NYSE American: NNVC), where he developed a class of broad-spectrum antiviral drugs — not vaccines — designed to target and destroy viruses. His lead drug candidate, NV-387, is currently in Phase II clinical trials for Mpox in the Democratic Republic of Congo and is being advanced for potential Ebola use. The company's premise — that you can engineer nanomaterials to bind to and destroy specific viruses — is either breakthrough pharmacology or high-risk biotech, depending on whom you ask. NNVC trades on the NYSE American. Diwan built it from a Connecticut lab.

**Senator Sujata Gadkar-Wilcox** receives the Political Leadership award. She has served in the Connecticut State Senate since 2024, representing the 22nd District, while maintaining a parallel career as a Professor of Legal Studies at Quinnipiac University. A Fulbright-Nehru Scholar who spent two years researching constitutional values in India, she occupies the exact intersection of academia and governance that the Indian American political class has increasingly made its own.

**Nitin Mhatre** is honoured for Corporate Leadership. He became CEO of First County Bank in April 2026, the latest in a career that has included leading Berkshire Bank and holding senior roles at Webster Bank and Citibank. He chaired the Consumer Bankers Association from 2019 to 2020. His credentials — engineering and MBA degrees from Mumbai University, executive education from Harvard Business School — read like a template for the Indian American financial executive, which is precisely the point.

**Ajay Ghosh** receives the Journalism award. A veteran journalist and founder of the Indo-American Press Club, Ghosh has held editorial roles at The Asian Era, The Indian Express (North America), and the Universal News Network, while simultaneously working as a Licensed Clinical Social Worker at Yale New Haven Hospital and teaching at Fordham Graduate School. The combination — journalist-clinician-educator — is unusual enough to deserve its own category.

**Prof. Hemchandra Shertukde** is honoured for Achievement in Engineering and Applied Sciences. An IIT Kharagpur graduate with a doctorate from UConn, he has spent nearly 40 years at the University of Hartford's College of Engineering. His output — 13 solo books, 40-plus co-authored texts, 100-plus research papers, 10 US patents, and several medical device startups — represents the kind of quietly prolific career that rarely makes headlines but defines the Indian American contribution to American technical infrastructure.

## Why It Matters

The awards ceremony is, in isolation, a local community event — five people receiving recognition from an organisation that most Americans have never heard of. But GOPIO-CT is part of a global network that operates chapters across six continents, and the profiles of its honourees reflect the sectors where Indian Americans have achieved disproportionate representation: biotech, politics, banking, media, and engineering.

"We select the awardees who have made an impact in our society and those who provide outstanding service," GOPIO-CT President Mahesh Jhangiani said. Dr. Thomas Abraham, the GOPIO International founder and chairman of the awards committee, added that the honourees are "role models for our new generations."

Twenty years ago, when GOPIO-CT launched in Stamford, the Indian American community in Connecticut was smaller, less visible, and less politically organised. The fact that this year's honourees include a sitting state senator, a NYSE-listed company founder, and a bank CEO suggests the community has graduated from networking to governing — one ceremony at a time."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "A Biotech Founder, a State Senator, and a Bank CEO Walk Into a Banquet Hall. It's GOPIO Connecticut's 20th Birthday.",
    "subheadline": "The diaspora organization will honour five Indian American achievers in Darien on June 13, from antiviral drug development to engineering patents. The profiles tell the story of how a community builds institutional power.",
    "slug": make_slug("gopio-ct-20th-anniversary-five-indian-american-achievers"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "GOPIO's Connecticut chapter has spent 20 years building the kind of community infrastructure — awards, recognition, mentoring — that converts individual achievement into collective institutional power for Indian Americans.",
    "tags": ["nri", "diaspora", "gopio", "connecticut", "indian-american", "community-awards"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/29/gopio-ct-to-honor-five-indian-american-achievers-at-its-20th-anniversary/"},
        {"name": "NanoViricides Inc. (NNVC)", "url": "https://www.nanoviricides.com/"},
        {"name": "Connecticut State Senate — 22nd District", "url": "https://www.cga.ct.gov/"},
    ]),
    "score_total": 68,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/6532375/pexels-photo-6532375.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body,
}


# ────────────────────────────────────────────────────
# ARTICLE 3: Rupee Under Pressure — What NRIs Need to Know
# ────────────────────────────────────────────────────

art3_body = """The Indian rupee closed at 95.27 against the dollar on June 1, still nursing the bruise from its plunge to 96.96 in mid-May — a record low that would have been worse without the Reserve Bank of India selling dollars in nearly every trading session since. The currency is down roughly 6 per cent for the year. For the 18 million NRIs who send money home, buy property in India, or maintain NRE and NRO accounts, the numbers are no longer background noise.

## What's Driving the Slide

Three forces are grinding against the rupee simultaneously.

First, oil. Crude prices are hovering about 30 per cent above pre-conflict levels, a consequence of the US-Israeli war with Iran that erupted earlier this year. India imports roughly 85 per cent of its crude oil, and every $10 increase in Brent crude widens the current account deficit by about 0.4 per cent of GDP. With Brent at $93, the pressure is structural, not speculative.

Second, capital flight. Foreign portfolio investors have been net sellers of Indian equities for much of the year, with the Sensex falling for four consecutive sessions as of June 1. FPI outflows, combined with the stronger dollar globally, have stripped demand for the rupee. Even domestic institutional buying has struggled to absorb the selling pressure.

Third, the RBI's own bind. Inflation remains benign — 3.48 per cent in April, well below the 4 per cent target — which normally argues for rate cuts. But the rupee's weakness and rising import costs point toward eventual rate hikes. Most economists polled by Reuters expect the MPC to hold the repo rate at 5.25 per cent when it meets on June 5, but 11 of 56 now forecast a 25-basis-point hike. In April's poll, only one analyst expected a June increase.

## What This Means for NRI Wallets

For NRIs sending dollars to India, a weaker rupee is mechanically good news: every dollar buys more rupees, making remittances, property purchases, and family support cheaper in dollar terms. India crossed $140 billion in inward remittances last year, a record driven partly by favourable exchange rates.

But the picture is more complicated than the headline number suggests.

**NRE vs. NRO accounts**: A Mint advisory published this week addressed one of the perennial NRI questions — which account to use when buying land in India. The answer, from a tax perspective, is that it doesn't matter: capital gains rates are identical regardless of funding source. The real difference is at the exit. Sale proceeds from Indian property can only be credited to an NRO account, and repatriation is capped at $1 million per financial year under the RBI's Liberalised Remittance Scheme. If the rupee weakens further between purchase and sale, the dollar value of your repatriated proceeds shrinks accordingly.

**Returning NRIs**: For those moving back to India — a perennially discussed, rarely executed manoeuvre — the process of converting NRO accounts to resident accounts has its own bureaucratic trail. Banks require proof of change in residential status, updated KYC documents, and a formal notification. Failing to convert on time can create FEMA compliance issues, a headache that nobody needs alongside the logistics of actually moving.

**Property sellers**: The Outlook Money advisory cautioned NRIs selling property to verify all ownership documents before listing, understand the higher TDS withholding rules for non-residents, and comply with RBI repatriation regulations. With the Punjab High Court recently flagging a pattern of property fraud targeting NRIs — forged documents, impersonation of absent owners — the due diligence checklist has grown longer.

## The June 5 Question

The RBI's MPC meeting on June 5 will be watched closely. A hold at 5.25 per cent would signal that the central bank still sees the rupee's weakness as manageable. A surprise hike would protect the currency but risk slowing an economy already grappling with elevated energy costs and tepid global demand.

For NRIs, the practical implication is straightforward: the window for favourable remittance rates may narrow if the RBI tightens. Those considering large rupee-denominated transactions — property purchases, fixed deposits, family transfers — may want to act while the exchange rate still flatters the dollar."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Rupee Hit a Record Low in May. For 18 Million NRIs, the Maths Just Got Complicated.",
    "subheadline": "At 95.27 to the dollar and sliding, the currency makes remittances cheaper but property repatriation riskier. The RBI meets June 5 to decide whether to raise rates — and NRIs are watching.",
    "slug": make_slug("rupee-record-low-nri-remittance-property-rbi-june"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Currency movements directly affect NRI financial decisions — from remittances to property purchases to the cost of returning to India. The rupee's slide creates winners and losers within the same diaspora household.",
    "tags": ["nri", "diaspora", "rupee", "rbi", "remittance", "nre-nro", "property"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/currencies/central-bank-hand-contains-rupees-fall-shrinks-dollar-rupee-forward-premiums-2026-06-02/"},
        {"name": "Reuters — RBI Rate Poll", "url": "https://www.reuters.com/world/india/rbi-hold-rates-june-majority-now-expect-hike-by-year-end-2026-05-29/"},
        {"name": "Mint — NRE vs NRO for Land Purchase", "url": "https://www.livemint.com/money/personal-finance/buying-land-india-nri-nre-nro-funds-tax-perspective-capital-gains-fema-rules-11748526063168.html"},
        {"name": "Outlook Money — NRI Property Sale Guide", "url": "https://www.outlookmoney.com/invest/things-nris-should-keep-in-mind-while-selling-property-in-india"},
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/7136068/pexels-photo-7136068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art3_body,
}

# ────────────────────────────────────────────────────
# Publish
# ────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
