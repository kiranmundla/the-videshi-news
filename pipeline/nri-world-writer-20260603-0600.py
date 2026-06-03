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
        "headline": "India Sent Its Largest-Ever Business Delegation to Canada. The Diaspora Did the Groundwork.",
        "subheadline": "Piyush Goyal arrived in Toronto with 112 companies and a mandate to triple bilateral trade to $50 billion by 2030. For 1.8 million Indo-Canadians, the reset they spent two bruising years waiting for is finally in motion.",
        "slug": make_slug("india-largest-business-delegation-canada-cepa-goyal-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Indo-Canadian diaspora served as the informal diplomatic back-channel during the bilateral crisis and is now positioned as the engine of the $50B trade target — their business networks, institutional relationships, and community organizations made this delegation possible.",
        "tags": ["nri", "diaspora", "india-canada", "trade", "cepa", "piyush-goyal"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/28/piyush-goyal-lauds-role-of-indian-diaspora-in-canada/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/india-and-canada-aim-for-usd-50-billion-trade-by-2030/"},
            {"name": "Ministry of Commerce & Industry, India", "url": "https://pib.gov.in"},
            {"name": "India Shipping News", "url": "https://indiashippingnews.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "image_attribution": "Wikimedia Commons",
        "body": """India's Commerce Minister Piyush Goyal touched down in Toronto last week with something no Indian trade delegation has ever carried before: 112 companies and a political mandate to treat the India-Canada corridor as if the past two years of diplomatic permafrost never happened.

By the time he left Ottawa three days later, Goyal had met Ontario Premier Doug Ford, addressed faculty at the University of Toronto's Munk School, toured the Ontario Centre of Innovation, sat with institutional investors managing hundreds of billions in pension assets, and delivered a joint press conference with Canada's Trade Minister Maninder Sidhu that would have been unthinkable twelve months ago.

The headline number — tripling bilateral trade from the current $17 billion to $50 billion by 2030 — is ambitious enough to invite scepticism. But the mechanics beneath it suggest both governments are treating it as an engineering problem rather than a slogan.

## The CEPA clock is ticking

At the centre of the reset is the Comprehensive Economic Partnership Agreement, or CEPA, a free trade deal that has been in negotiation since 2010 and stalled repeatedly through political crises, pandemic disruptions, and — most recently — the diplomatic rupture over the assassination of Hardeep Singh Nijjar in British Columbia in June 2023.

What changed is Mark Carney. The former Bank of Canada governor became Prime Minister in March 2026, visited India almost immediately, and signed a framework of preferences that effectively restarted the CEPA clock. Goyal said both prime ministers have tasked their trade teams with completing the agreement "before the end of this year or earlier."

"The speed and intent of both sides is phenomenal," Goyal told reporters in Ottawa. "When it comes to working together for the shared prosperity of the people of India, the people of Canada, providing business opportunities for both countries — this is very much doable."

## The diaspora as infrastructure

The delegation's size — 112 companies spanning clean energy, aerospace, food processing, critical minerals, and technology — is a statement in itself. But the less visible story is how it was assembled.

The Canada-India Foundation, a Toronto-based diaspora business group, helped identify Canadian counterparts, arranged introductions, and provided the institutional memory that government trade offices lack. Goyal acknowledged their role explicitly, calling the Indo-Canadian community's contribution "invaluable" to bringing the two nations closer.

For India's 1.8 million-strong diaspora in Canada — the country's largest source of new immigrants — the reset is personal. Many watched the 2023-2024 diplomatic crisis erode business relationships they had spent years building. Student visa processing slowed. Investment inquiries dried up. Community organisations found themselves navigating a political environment in which their dual loyalties were suddenly a liability rather than an asset.

## What the pension funds heard

Among the most consequential meetings were those with the Ontario Teachers' Pension Plan and CPP Investments, two of the world's largest institutional investors. Both already have India exposure — CPP Investments has deployed billions across Indian infrastructure, real estate, and technology — but the meetings focused on expanding into renewables, logistics, financial services, and the digital economy.

For NRIs working in Canadian finance, this is the kind of structural alignment that creates career opportunities on both ends of the corridor. India's infrastructure pipeline alone is projected to require $1.4 trillion in investment over the next decade. The question for Canadian pension funds is no longer whether to invest in India but how fast they can deploy.

## What $50 billion actually requires

Bilateral trade between India and Canada currently stands at roughly $8.5 billion, with both governments citing the $17 billion figure that includes services. Reaching $50 billion by 2030 would require roughly 30 percent compound annual growth — a rate that is achievable only if the CEPA eliminates tariff barriers, services trade expands significantly, and supply chains are rerouted to take advantage of the agreement.

The sectors Goyal emphasised — clean energy, critical minerals, AI, agritech, and food processing — are deliberately chosen. Canada has the raw materials and research infrastructure; India has the manufacturing scale and domestic demand. If the CEPA creates the regulatory framework for these complementary advantages to connect, the $50 billion target starts to look less like aspiration and more like arithmetic.

For the Indo-Canadian diaspora, the delegation is a vindication of sorts. They kept the corridor alive when both governments were barely speaking to each other. Now they are being asked to scale it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thirty-Two Lawmakers Now Back Congress's Hinduphobia Resolution. The Community Is Still Counting.",
        "subheadline": "H.Res.69, introduced by Indian American Congressman Shri Thanedar, has quietly accumulated bipartisan support as temple vandalism incidents pile up and the FBI's hate crime numbers keep climbing.",
        "slug": make_slug("hinduphobia-resolution-congress-32-cosponsors-ro-khanna-temple"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Hindu Americans are building institutional political power to address a safety crisis — temple vandalism, campus bullying, and rising hate crimes — that previous generations absorbed in silence. The resolution's growing co-sponsor count reflects a community learning to use legislative tools to protect its own.",
        "tags": ["nri", "diaspora", "hinduphobia", "congress", "hate-crimes", "temples"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Daily Jagran", "url": "https://thedailyjagran.com"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/01/a-resolution-introduced-in-us-congress-on-hinduphobia-by-rep-thanedar/"},
            {"name": "NRI Globe", "url": "https://nriglobe.com"},
            {"name": "LegiScan", "url": "https://legiscan.com/US/bill/HR69/2025"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Shri_Thanedar%2C_official_portrait_%28119th_Congress%29.jpg",
        "image_attribution": "Wikimedia Commons",
        "body": """When California Congressman Ro Khanna announced on Monday that he was co-sponsoring H.Res.69 — the House resolution condemning Hinduphobia, anti-Hindu bigotry, and attacks on temples — it raised the total number of co-sponsors to 32. By the standards of congressional resolutions, that is a meaningful number. By the standards of the community it is meant to protect, it is a start.

The resolution was introduced in January 2025 by Shri Thanedar, a Democrat from Michigan and one of a handful of Indian Americans in Congress. It has since been referred to the House Committee on Oversight and Accountability, where it sits alongside the accumulated weight of FBI data, community testimony, and a growing list of vandalised mandirs.

The co-sponsor roster now includes some of the most prominent Indian American voices in Congress: Raja Krishnamoorthi of Illinois, Suhas Subramanyam of Virginia, and now Khanna, who represents a Silicon Valley district where Hindu Americans are a significant constituency. Khanna framed his support as a matter of democratic principle: "I'm proud to cosponsor this bill that celebrates the continued contributions and vibrant diversity of the Hindu-American community as we work to strengthen our nation's multiracial democracy."

## The numbers behind the resolution

The resolution does not propose new law. It is a formal expression of congressional sentiment — a declaration that Hindu Americans contribute to the fabric of the nation and that the rising tide of anti-Hindu incidents deserves federal attention. Its text references the FBI's Hate Crimes Statistics Report, which has documented a year-over-year increase in anti-Hindu incidents, and notes that Hindu Americans face "stereotypes and disinformation about their heritage and symbols" alongside "bullying in schools and on college campuses, as well as discrimination, hate speech, and bias-motivated crimes."

The data, while incomplete — the FBI's hate crime statistics rely on voluntary reporting by local agencies — paints a pattern that community organisations have been tracking independently for years. The Coalition of Hindus of North America (CoHNA) reports that at least 12 Hindu temples across denominations have faced vandalism or burglary in the United States since 2022.

## The temple trail

The incidents have come in clusters, which is part of what makes them alarming. In September 2024, BAPS Swaminarayan temples in Melville, New York and Sacramento, California were hit within days of each other. In March 2025, the BAPS temple in Chino Hills, California was defaced with the words "Hindustan Murdabad" — a phrase meaning "death to India" — along with expletives targeting Prime Minister Modi. India's External Affairs Ministry condemned the attack. San Bernardino County authorities investigated it as a hate crime.

More recently, a BAPS temple in Greenwood, Indiana and another in New York were vandalised, prompting the Indian Consulate to call for "swift action" and reinforcing the perception among NRIs that their places of worship are being systematically targeted.

## A letter to the DOJ

About two weeks before Khanna's co-sponsorship announcement, five Indian American members of Congress — Krishnamoorthi, Khanna, Thanedar, Ami Bera, and Pramila Jayapal — sent a joint letter to the Department of Justice requesting a briefing on the status of investigations into temple vandalism.

The letter was notable for its tone. It did not accuse any particular group or ideology. Instead, it focused on the pattern: "The number of incidents and the closeness of the timing of incidents raise troubling questions about linkages and the intent behind them. It takes relatively few coordinated acts of hate to create fear nationally within a community that has often been marginalized or neglected."

The DOJ has not publicly responded to the request.

## What a resolution can and cannot do

Critics of congressional resolutions point out, correctly, that they carry no legal force. H.Res.69 will not fund temple security, create a dedicated hate crimes unit, or compel the FBI to improve its reporting methodology. What it can do is establish a political marker — a formal acknowledgement that Hinduphobia exists as a category of hate, that the federal government has noticed, and that a growing number of lawmakers consider it worth their political capital to say so.

For the 3.2 million Hindu Americans in the United States, the resolution is both a practical tool and an emotional signal. Community organisations like CoHNA and the Hindu American Foundation have spent years building the advocacy infrastructure — the lobbying days, the campus testimonies, the constituent meetings — necessary to move legislation in Washington. H.Res.69 is, in part, the product of that work.

The 32 co-sponsors suggest the advocacy is gaining traction. Whether it translates into federal resources, improved hate crime tracking, or meaningful security assistance for vulnerable temples remains an open question — one that 32 lawmakers have now, at minimum, agreed is worth asking."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
