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
        "headline": "GOPIO-Connecticut Turns Twenty. The Five People It Chose to Honour Tell You Everything About Where Indian America Is Heading.",
        "subheadline": "A state senator, a biotech founder, a veteran journalist, a bank CEO, and an engineering professor — Connecticut's Indian diaspora organisation marks two decades by spotlighting the professionals who shaped the community from within.",
        "slug": make_slug("gopio-connecticut-20th-anniversary-indian-american-awards"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "GOPIO-CT's awards reflect how Indian American community organisations have matured from cultural preservation into recognising professional and civic leadership across multiple fields — a mirror of how the diaspora itself has evolved over two decades.",
        "tags": ["nri", "diaspora", "gopio", "indian-american", "connecticut", "community-awards"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/29/gopio-ct-to-honor-five-indian-american-achievers-at-its-20th-anniversary/"},
            {"name": "GOPIO International", "url": "https://gopio.net/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37198377/pexels-photo-37198377.jpeg",
        "body": """When the Global Organisation of People of Indian Origin set up its Connecticut chapter in 2006, the Indian American population in the state was still small enough that most community leaders knew each other by first name. Two decades later, GOPIO-CT is preparing to honour five professionals whose combined résumés span the state legislature, Wall Street, the biotech industry, the newsroom, and the university lab.

The awards banquet, scheduled for June 13 at the Water's Edge Banquet Hall in Darien, is not merely a dinner. It is an institutional self-portrait — a community organisation choosing to say, through its selections, what it values most right now.

## The five

**Senator Sujata Gadkar-Wilcox** represents Connecticut's 22nd district and teaches legal studies at Quinnipiac University. A Fulbright-Nehru Scholar who spent two years researching constitutional values in India, she has been in the state senate since 2024. Her recognition for "political leadership" marks a category that would have been unthinkable at GOPIO-CT's founding, when Indian Americans in elected office anywhere in Connecticut were essentially nonexistent.

**Dr. Anil Diwan** founded NanoViricides, Inc., a publicly traded biotech firm on the NYSE American exchange. His company's lead drug candidate, NV-387, is currently in Phase II clinical trials for Mpox in the Democratic Republic of Congo and is being developed for potential use against Ebola. His award for "entrepreneurship and business achievements" represents a generation of Indian American founders who went beyond the IT services playbook.

**Ajay Ghosh** brings more than three decades of journalism experience, having held editorial positions at The Indian Express (North America), The Asian Era, and the Universal News Network. He founded the Indo-American Press Club and currently serves as a licensed clinical social worker at Yale New Haven Hospital — an unusual dual career that the community, to its credit, chose to recognise rather than compartmentalise.

**Nitin Mhatre** became CEO of First County Bank on April 15 this year. The bank has served Fairfield County for over 174 years. His previous roles include the top job at Berkshire Bank and senior positions at Webster Bank and Citibank. He chaired the Consumer Bankers Association in 2019-2020. His "corporate leadership" award signals the diaspora's quiet expansion into regional financial institutions — not just the global banks where Indian-origin executives have long been visible.

**Professor Hemchandra Shertukde** has taught engineering at the University of Hartford for nearly four decades. An IIT Kharagpur alumnus with a PhD from UConn, he has authored 13 solo books, co-authored over 40 technical publications, holds 10 U.S. patents, and founded several technology and medical device companies. His presence on the list is a reminder that the first wave of Indian academic emigration built infrastructure that still stands.

## Why it matters

GOPIO International's founder, Dr. Thomas Abraham, described the awardees as "role models for our new generations." The phrase is familiar, but the selection is not. Twenty years ago, an Indian community awards night in Connecticut would likely have centred on cultural preservation — a temple fundraiser, a dance school, a Diwali organiser. The 2026 list centres on civic power, scientific innovation, corporate governance, and press freedom.

GOPIO-CT president Mahesh Jhangiani put it more directly: "We select the awardees who have made an impact in our society." The shift from "our community" to "our society" is not accidental. It reflects a broader transformation across Indian American organisations, from inward-facing cultural preservation to outward-facing civic ambition.

The banquet will also recognise GOPIO-CT's founding members, including Dr. Abraham and Viresh Sharma, along with past chapter presidents. A special recognition will go to Sharon Priya Banta, who served as the chapter's youth coordinator in its early years — a nod to the generational continuity that community organisations depend on but rarely celebrate.

Several Connecticut lawmakers are expected to attend. The entertainment will include Bollywood DJ sets, because some things about Indian community events never change, and shouldn't."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Wonder Just Launched an Indian Food Brand Across 100 Locations. It Might Be the Moment Indian Cuisine Stops Being 'Ethnic' in America.",
        "subheadline": "The fast-growing food hall company is testing Dabba in Philadelphia before a national rollout, while Michelin-starred Indienne heads to Hudson Yards and the US now has over 12,600 Indian restaurants. Something has shifted.",
        "slug": make_slug("wonder-dabba-indian-cuisine-mainstream-america"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The mainstreaming of Indian food in America is both a cultural milestone and an economic one for the diaspora — every tikka masala on a fast-casual menu normalises a cuisine that was once ghettoised as 'ethnic,' while Indian-origin restaurateurs lead much of the fine-dining revolution.",
        "tags": ["nri", "diaspora", "indian-food", "restaurants", "wonder", "dabba", "indian-cuisine", "america"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Restaurant Business Online", "url": "https://www.restaurantbusinessonline.com/food/wonder-launches-indian-concept"},
            {"name": "WhatNow NYC", "url": "https://whatnow.com/new-york/michelin-starred-indian-restaurant-from-chicago-is-opening-in-hudson-yards/"},
            {"name": "WhatNow NYC", "url": "https://whatnow.com/new-york/a-new-dining-concept-lands-in-the-east-village-from-a-well-known-tv-personality/"},
            {"name": "POI Data", "url": "https://poidata.io/indian-restaurants-in-united-states/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/941869/pexels-photo-941869.jpeg",
        "body": """Wonder, the fast-growing food hall and delivery company backed by $900 million in venture capital, launched an Indian concept called Dabba this week. It is testing in four Philadelphia locations before what the company says will be a systemwide rollout across more than 100 storefronts on the East Coast.

The name is borrowed from Mumbai's legendary dabbawallas — the 130-year-old tiffin delivery network that has become a Harvard Business School case study. The menu features chicken tikka masala, butter chicken, lamb vindaloo, and samosas, developed by Wonder's in-house culinary team. Prices range from $8.95for samosas to $19.95 for butter chicken.

If it works, Dabba will become one of the largest-scale Indian food operations in America. And there is every reason to think it will work, because Indian cuisine in America is no longer climbing — it has arrived.

## The numbers

The United States now has over 12,650 Indian restaurants, according to April 2026 data from POI Data. California leads with 1,320, followed by Texas with 754. That is not a niche. That is a cuisine category with the density and geographic spread of Thai or Korean food, both of which crossed the "mainstream" threshold years ago.

At the high end, the trajectory is even sharper. Data from Datassential counts 154 upscale Indian dining restaurants in the US, up from 101 in January 2018. New Indian restaurant openings hit 115 in a single month in late 2024, more than double the pace from six years earlier. Resy CEO Pablo Rivero has noted that demand for high-end Indian restaurants continues to widen with no signs of slowing.

## Three openings that tell the story

In May alone, three high-profile Indian restaurants opened in New York City — each one representing a different facet of the cuisine's evolution.

Celebrity chef and television personality Aarthi Sampath opened **Drāvida** in the East Village on May 21. The restaurant describes itself as rooted in the South Asian diaspora, blending recipes from India, Sri Lanka, Pakistan, Nepal, Trinidad, and Guyana. The menu includes Lhasa lamb momos, duck nihari hand pies, and oxtail bunny chow. It is housed in a restored building with original brick ovens and features a speakeasy called Jam and Jaggery on the lower level.

Michelin-starred chef Sujan Sarkar is bringing **Indienne** from Chicago to Hudson Yards this summer. Alongside the fine-dining restaurant, he will open Apas, a cocktail bar featuring South Asian flavours, and Elder, a British-Indian chophouse named after elderflower — a plant found in both British and South Asian botanical traditions. The three concepts together represent a full-service Indian hospitality ecosystem in one of Manhattan's most commercially visible developments.

Meanwhile, at the fast-casual end, **Indian Bites** celebrated its grand opening at the Worcester Public Market in Massachusetts — a sister location to Desi Bar & Grill, offering what it calls "authentic Indian fast food." The restaurant was founded by four immigrant entrepreneurs from India and Nepal who between them run three food businesses in the Worcester area.

## What changed

Vikas Khanna, the Michelin-starred chef who has been in the American restaurant scene for over two decades, has described watching the landscape shift from "cheap food and curry houses" to sophisticated sit-down establishments. The transformation tracks with broader demographic and cultural shifts.

Gen Z and millennial diners have what food industry analysts call a "quest for flavours" — an openness to global cuisines that their parents' generation did not share at the same age. Indian food, with its layered spice profiles and regional diversity, is well-positioned to benefit.

But the real infrastructure has been built by the diaspora itself. The 12,650 Indian restaurants across the country were not opened by Wonder or any corporate food platform. They were opened, one lease at a time, by Indian and South Asian immigrants who took the financial risk of introducing an unfamiliar cuisine to American strip malls, food courts, and downtown corners. Wonder's Dabba concept, whatever its commercial fate, is downstream of that work.

The company acknowledged the complexity: "We've built a vertically integrated model that allows us to control the full process — from recipe development through production and final preparation," a spokesperson said. For a cuisine known for its labour-intensive techniques and depth of flavour, consistency at scale remains the hardest test. The four-store pilot is designed to answer that question before the national rollout.

For the Indian diaspora, the mainstreaming of its cuisine is not just a food story. It is a visibility story. Every butter chicken on a Wonder menu, every Michelin star on a tasting menu, and every Indian Bites storefront in a public market is a small act of cultural normalisation in a country where "ethnic food" was, until recently, code for "cheap and unfamiliar." That era is ending."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Highest Astronautics Honour Just Went to Chandrayaan-3. India's Ambassador Accepted It in Washington.",
        "subheadline": "The AIAA's Goddard Astronautics Award — named for the father of rocketry — was presented to ISRO's lunar mission at the ASCEND 2026 Conference, with Ambassador Vinay Kwatra using the moment to pitch deeper US-India space collaboration.",
        "slug": make_slug("chandrayaan-3-goddard-astronautics-award-aiaa-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The award ceremony in Washington, with India's Ambassador accepting on ISRO's behalf, crystallises a moment the diaspora has been building toward: Indian scientific achievement recognised at the highest level of American aerospace, in a city where Indian-origin engineers and scientists have been part of the space establishment for decades.",
        "tags": ["nri", "diaspora", "isro", "chandrayaan-3", "space", "aiaa", "goddard-award", "vinay-kwatra"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/22/aiaa-honors-chandrayaan-3-with-goddard-astronautics-award/"},
            {"name": "American Institute of Aeronautics and Astronautics", "url": "https://www.aiaa.org/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Chandrayaan-3_%E2%80%93_Image_of_Vikram_lander_on_lunar_surface_taken_by_Pragyan_rover_navcam_at_1104_IST%2C_30_August_2023_from_15_meters_away_%28with_text%29.webp",
        "body": """On May 21, at the ASCEND 2026 Conference in Washington, DC, the American Institute of Aeronautics and Astronautics presented its 2026 Goddard Astronautics Award to India's Chandrayaan-3 mission. It is the highest honour the AIAA bestows for achievements in astronautics — and the first time it has gone to an Indian space programme.

India's Ambassador to the United States, Vinay Kwatra, accepted the award on behalf of the Indian Space Research Organisation. The setting was deliberate. The Goddard Award is named for Robert H. Goddard, whose early liquid rocket engine launches in the 1920s and 1930s set the foundation for everything that followed in spaceflight. Placing ISRO's lunar achievement in that lineage was the point.

## What Chandrayaan-3 actually did

On August 23, 2023, Chandrayaan-3's Vikram lander touched down near the Moon's south pole — a region of immense scientific and strategic interest that no spacecraft had previously reached at the surface level. The landing made India the fourth country to achieve a soft lunar landing, after the Soviet Union, the United States, and China, and the first to reach the south polar region.

The Pragyan rover, deployed from the lander, confirmed the presence of key chemical elements in the south polar soil — data relevant to future plans for in-situ resource utilisation, the concept of using local materials to sustain operations on the lunar surface rather than shipping everything from Earth. For nations planning crewed Moon missions in the 2030s, that data has immediate practical value.

The mission cost approximately $75 million. For context, that is less than the production budget of several Hollywood films about space. The cost efficiency has become part of the Chandrayaan narrative, though ISRO's scientists have generally preferred to let the science speak.

## The diplomatic layer

Ambassador Kwatra's acceptance speech went beyond the mission itself. He outlined Prime Minister Modi's Space Vision 2047 — India's roadmap for deep space exploration, human spaceflight through the Gaganyaan programme, and the rapid growth of India's commercial space sector, which has seen over 200 startups register since space sector reforms in 2020.

He called for strengthened collaboration between the governments, industries, and research institutions of India and the United States. The pitch landed in a receptive room. US-India space cooperation has deepened significantly in recent years, with NASA and ISRO signing the Artemis Accords in 2023 and planning a joint mission to the International Space Station.

For Indian-origin scientists and engineers in the American aerospace ecosystem, the moment carried personal weight. The AIAA's membership includes thousands of Indian-origin professionals working at NASA, SpaceX, Boeing, Lockheed Martin, and universities across the country. Many of them grew up watching ISRO launches on Doordarshan; some have parents or relatives who worked on earlier Chandrayaan missions. The Goddard Award places their country of origin's space programme alongside those of the organisations that employ them.

## What the award means in context

The Goddard Astronautics Award has historically gone to American and European space programmes and individuals. Past recipients include teams from NASA's Jet Propulsion Laboratory and the European Space Agency. ISRO's inclusion marks a shift in how the global aerospace establishment perceives India's space capabilities — from impressive-for-the-budget to genuinely world-class.

The award also arrives at a moment when India's space ambitions are accelerating. The Gaganyaan crewed mission is in advanced testing. ISRO is planning a Venus orbiter mission and a follow-up lunar mission, Chandrayaan-4, designed to bring back soil samples. The commercial space sector, led by companies like Skyroot Aerospace and Agnikul Cosmos, is developing small satellite launch vehicles.

For the Indian diaspora, these developments serve as a counterpoint to the narratives that typically dominate NRI conversations about India — infrastructure challenges, bureaucratic friction, brain drain. ISRO's trajectory suggests that brain drain can coexist with institutional excellence, that a country can simultaneously export talent and build world-class programmes at home.

The Goddard Award will be added to ISRO's growing shelf of international recognitions. But the image that will likely endure from the ceremony is of India's ambassador standing at a podium in Washington, DC, accepting the American aerospace community's highest honour for a $75 million mission that landed where no one else had. The diaspora, watching from both sides of the world, understood what that moment cost to build."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
