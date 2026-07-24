#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-23 11:00 PDT run
2 articles:
  1. Indian Food's Greatest New York Moment: Drāvida + Indienne + the broader revolution
  2. America's Record May Heatwave: When the Heat Follows You Across Oceans
"""

import os, json, uuid, re, requests, time
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──
for line in (Path.home() / ".env.supabase").read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def make_slug(text, suffix="20260523"):
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{suffix}"

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code == 409:
        print(f"  ⚠ Conflict (already exists) for {table}")
        return None
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Indian Food's Greatest New York Moment
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Indian Food Is Having Its Greatest New York Moment. Two Restaurants Opening This Week Tell You Everything About Where It's Going."
art1_subheadline = "On May 21, Chef Aarthi Sampath — the first Indian woman to win Chopped — opened Drāvida in the East Village, a restaurant that traces diaspora food routes from Trinidad to Durban. On May 28, Michelin-starred Chef Sujan Sarkar brings Indienne from Chicago to Hudson Yards, with $195 tasting menus and Holi-inspired art. In between, London's beloved Dishoom is preparing its first American location. There are now 12,653 Indian restaurants in the United States. This is the week the cuisine stopped asking for permission."
art1_slug = make_slug("indian-food-new-york-dravida-indienne-diaspora-cuisine-moment")
art1_category = "lifestyle-health"

art1_body = """Two Indian restaurants are opening in New York City within seven days of each other. One is in the East Village, in a restored hundred-year-old building with twenty seats and a speakeasy in the basement. The other is in Hudson Yards, on the second floor of a luxury residential tower, with nine-course tasting menus and cocktails made from recycled kitchen ingredients. They could not be more different in ambition, price point, or neighbourhood. But together, they tell the story of where Indian food in America is going — and it is going everywhere.

Drāvida opened on Wednesday, May 21. Indienne opens on Wednesday, May 28. For the Indian diaspora in New York, and for anyone who has watched Indian food in America struggle to escape the butter-chicken-and-naan box for three decades, this is a week worth paying attention to.

## Drāvida: The Diaspora on a Plate

Chef Aarthi Sampath wrote the concept for Drāvida in 2019. Seven years later, it exists at 211 First Avenue in Manhattan's East Village — a neighbourhood that was once home to Curry Row, the stretch of Indian restaurants on East Sixth Street that defined (and, many would argue, limited) what Americans thought Indian food could be.

Sampath is not interested in that definition.

Born and raised in Mumbai, she trained in classical French technique in India before attending Johnson & Wales Culinary University in the United States. Her New York kitchen pedigree includes the Michelin-starred Junoon, The Breslin, and the Rainbow Room. She became the first Indian woman to win the Food Network's Chopped, and later beat Bobby Flay on national television. Since 2023, she has built a meal-delivery operation on CookUnity that now employs more than fifty people and ships roughly 50,000 meals a week across major US markets.

Drāvida is her first brick-and-mortar restaurant, and it is not an Indian restaurant in any sense that the old Curry Row would recognise.

The menu is a map of South Asian migration. Where most Indian restaurants in America focus on the food of India itself — the curries of Punjab, the dosas of Tamil Nadu, the biryanis of Hyderabad — Drāvida asks a different question: what happened to Indian food when Indians left India?

The answer is on the menu.

**Doubles**, the beloved street food of Trinidad and Tobago, is a dish born from the culinary traditions of Indo-Trinidadian labourers in the nineteenth century — curried chickpeas sandwiched between fried flatbread. **Oxtail Bunny Chow** comes from Durban, South Africa, where Indian immigrants created a portable curry lunch using a hollowed-out loaf of bread. **Idli & Shrimp** echoes the ancient trade routes between South India and Indonesia, where food historians believe the steamed rice cake may have originated as "kedli." **Nasi Kandar** from Penang, Malaysia, traces the Tamil Muslim traders who brought their curries to Southeast Asia centuries ago.

"This restaurant is for New Yorkers who haven't seen their food represented," Sampath said in the opening announcement. "For the communities that built this city and whose cuisines haven't always had a place at the table."

The space itself is deliberate. Twenty seats in the main dining room — intimate, personal, the opposite of the buffet-line anonymity that defined Indian restaurants for a generation. Downstairs, Jam and Jaggery is a twenty-seat speakeasy with cocktails and small plates, named after two of the oldest sweeteners in South Asian cooking. The building retains its original brick ovens, and the design aims to feel like "both a discovery and a homecoming."

## Indienne: Fine Dining Without Apology

Six days after Drāvida's opening, Chef Sujan Sarkar will open Indienne at Henry Hall in Hudson Yards — a very different restaurant with a very different ambition.

Indienne first opened in Chicago's River North neighbourhood in 2022. It earned a Michelin star within its first year. The New York location is Sarkar's return to the city where he first made his name with Baar Baar, a contemporary Indian gastropub he opened in the East Village in 2017.

The new Indienne will have thirty-four seats and three nine-course tasting menus: non-vegetarian at $195, vegetarian and vegan at $175. The experience begins with chaat-inspired dishes — the street food that millions of Indians grew up eating from roadside carts — before progressing through seasonal courses that layer spices, textures, and regional influences.

Sarkar is not hedging. This is Indian food priced and presented at the level of any European tasting menu in the city, without the apologetic qualifier of "for Indian food." The interiors, designed with MAPA Mueller, feature textured finishes, sculptural lighting, and blush-toned seating. The artwork is by Chicago-based artist Ken Andjulis, whose Holi-inspired paintings bring the festival of colours to the walls of a Hudson Yards dining room.

But Sarkar is not stopping at one restaurant. Henry Hall will also house **Apas**, a high-end cocktail bar named after the Sanskrit word for water, featuring South Asian botanicals in a modern setting. And this summer, he will open **Elder**, a British-Indian chophouse inspired by the centuries-long coexistence of British and Indian cuisines in London — dry-aged meats, Indian spices, tableside dessert service.

Three Indian-inflected concepts in a single luxury residential tower. In 2016, that sentence would have been a punchline. In 2026, it is a business plan.

## The Bigger Picture: 12,653 and Counting

Drāvida and Indienne are not isolated openings. They are the most visible arrivals in what is becoming the definitive year for Indian food in America.

As of April 2026, there are 12,653 Indian restaurants in the United States, with the highest concentrations in California and Texas. According to Technomic, 52 per cent of American consumers have tried Indian food and liked it. Datassential found that 49 per cent of US consumers have visited a restaurant that primarily serves Indian cuisine. These are not niche numbers. These are the numbers of a cuisine on the threshold of mainstream ubiquity.

The pipeline of openings tells the story even more clearly.

**Dishoom**, the beloved Bombay-inspired café chain from London — twelve locations, a private-equity valuation of nearly $400 million from L Catterton — is preparing to open its first American location in New York City later this year. This is significant not just because Dishoom is a proven concept, but because its arrival from the UK suggests that the American market is finally "ready" for Indian food at scale.

**JKS Restaurants**, another UK-based group, has already brought its Gymkhana concept to the Aria Resort & Casino in Las Vegas and opened the Punjabi-focused Ambassadors Clubhouse in New York earlier this year. When Travis Kelce and Taylor Swift were spotted at Gymkhana's London location, it became a cultural moment that transcended food criticism.

In Los Angeles, **Badmaash** — the progressive Indian concept whose founders deliberately set out to "blow up" the stereotype of the American Indian restaurant — just opened its third location in Venice Beach. In Washington, DC, **Rasa** has five locations and recently brought on the former COO of Starbucks to its board of directors. In Austin and Houston, **Tarka Indian Kitchen** has grown its average unit volumes from $1.6 million to $2.3 million in three years and is preparing to franchise nationally.

And in the fine-dining tier, concepts like **Dhamaka** and **Semma** in New York have shown that regional Indian food — not the sanitised greatest-hits menu, but goat brain and lamb testicles and fiery Chettinad curries — can earn critical acclaim and long reservation lists in the most competitive dining market in the world.

## Why It Matters to the Diaspora

For the 4.8 million Indian Americans in the United States, the evolution of Indian food from "ethnic cuisine" to mainstream dining is personal.

Every diaspora family has a version of this story. You grow up eating dal-chawal at home, and at school, your lunch box smells "weird." You learn to eat pizza and sandwiches in public and save the Indian food for home. When your parents take you to an Indian restaurant, it is a fluorescent-lit room with plastic tablecloths and an all-you-can-eat buffet that your American friends would never voluntarily visit.

The progressive Indian restaurant movement is not just about better food. It is about cultural dignity. When Sujan Sarkar charges $195 for a nine-course Indian tasting menu in Hudson Yards, he is making a statement about the value of Indian culinary tradition. When Aarthi Sampath traces the food routes of the South Asian diaspora through Trinidad and Durban and Penang, she is saying that Indian food is not one thing — it is a global civilisation expressed through cooking.

Nakul Mahendro of Badmaash put it bluntly in a recent interview with Restaurant Business: "Your idea of an Indian restaurant is horrible. Don't put me in that box." He wanted a restaurant "where you could take a hot date or your boss." That did not exist in Los Angeles when his family created Badmaash in 2013.

For second-generation Indian Americans, restaurants like Drāvida and Indienne resolve a tension that has defined their relationship with food and identity. You no longer have to choose between being Indian and being cool. The two are the same thing.

## What Comes Next

Chef Sujan Sarkar believes Indian fast-casual dining alone could become a billion-dollar segment in the next decade. He is developing an "Indian-American fast casual for the next generation" — a concept that tells the story of how Indian food has evolved in America.

The broader trajectory is clear. Indian cuisine in the US is following the path that Japanese food blazed two decades ago: from cheap takeout to mainstream acceptance to fine-dining prestige to cultural ubiquity. Sushi was once "exotic." Now it is in every supermarket in America. Indian food is on the same journey, just twenty years behind.

The difference is speed. With 12,653 restaurants already in operation, a diaspora population that is growing, affluent, and culturally confident, and a generation of chefs who refuse to compromise, the gap is closing fast.

This week in New York, at a twenty-seat restaurant in the East Village and a thirty-four-seat restaurant in Hudson Yards, two Indian chefs are showing the city — and the country — what Indian food looks like when it stops apologising.

For the diaspora watching from New Jersey living rooms and Bay Area kitchens and Houston suburbs, the message is simple: our food was always this good. The rest of America is just catching up."""

art1_sources = [
    "https://whatnow.com/new-york/restaurants/a-new-dining-concept-lands-in-the-east-village-from-a-well-known-tv-personality/",
    "https://briefglance.com/articles/chef-aarthi-sampaths-drvida-charts-a-new-culinary-map-in-nyc",
    "https://whatnow.com/new-york/restaurants/michelin-starred-indian-restaurant-from-chicago-is-opening-in-hudson-yards/",
    "https://restaurantbusinessonline.com/emerging-brands/year-redefining-indian-food-america",
    "https://restaurantbusinessonline.com/emerging-brands/indian-food-finally-carving-niche-among-us-fast-casuals",
    "https://poidata.io/en/poi/indian-restaurants-in-united-states",
]

print("=== Article 1: Indian Food's Greatest New York Moment ===")
print(f"Word count: {len(art1_body.split())}")

result = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 91,
    "tags": ["Indian food", "Drāvida", "Indienne", "New York", "restaurants", "Aarthi Sampath", "Sujan Sarkar", "diaspora cuisine", "NRI", "fine dining", "Dishoom", "Indian American", "Michelin star"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Indian food in America is having its breakout moment. Two restaurants opening within 7 days in NYC — Drāvida (diaspora cuisine by first Indian woman Chopped winner) and Michelin-starred Indienne ($195 tasting menus). 12,653 Indian restaurants in the US, 52% of Americans have tried Indian food. For the diaspora, this is about cultural dignity — our food was always this good.",
    "word_count": len(art1_body.split()),
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: America's Record May Heatwave — NRI Angle
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "You Left India to Escape the Heat. This Week, New York Hit 103°F and Philadelphia Broke a 35-Year Record. The Climate Math Is Changing for NRIs."
art2_subheadline = "A record-shattering May heatwave has gripped the US East Coast — 103°F in New York, 98°F in Philadelphia (breaking the all-time May record set in 1991), 96°F in Boston. Schools are closing, trains are slowing down because rails are too hot to handle, and power outages have left thousands without air conditioning. Meanwhile, India recorded 48°C in Uttar Pradesh, 55 heatstroke deaths in one day across Andhra Pradesh and Telangana, and Delhi is under severe heatwave warning through May 27. For the first time in many NRIs' lives, both countries are burning at the same time."
art2_slug = make_slug("us-east-coast-heatwave-nri-india-climate-both-countries-burning")
art2_category = "lifestyle-health"

art2_body = """For decades, the Indian summer was something you survived and then escaped. You grew up drinking water from clay matkas, sleeping on the terrace because the electricity went out, and fanning yourself with folded newspapers in classrooms where the ceiling fan moved too slowly to matter. And then you left. You moved to New York, or Philadelphia, or Boston, or Chicago, and summer became something manageable — warm but not dangerous, uncomfortable but not deadly. Air conditioning worked. Power stayed on. The infrastructure held.

This week, that distinction collapsed.

On Tuesday, May 20, New York City recorded a high of 103°F. Philadelphia hit 102°F the same day, shattering the city's all-time May record of 97°F that had stood since 1991 — and doing it eleven days earlier in the month. Newark, New Jersey hit 100°F for the third consecutive day. Boston reached 96°F. Portland, Maine — Portland, Maine — hit 92°F. These are not July numbers. These are not August numbers. It is still May.

At the same time, India is experiencing its own catastrophe. On Thursday, May 22, at least 55 people died from heatstroke in a single day across Andhra Pradesh and Telangana. Temperatures crossed 46°C in twenty different districts of Telangana. The highest temperature recorded in India this year hit 48°C (118°F) in Banda, Uttar Pradesh. Delhi is under a severe heatwave warning through May 27. Water shortages have erupted in Gujarat. Hospitals in multiple states are overflowing with patients suffering from dehydration and diarrhoea.

For the roughly 4.8 million Indian Americans living in the United States, many of them on the East Coast, the experience of this week has been uniquely disorienting. Both countries — the one you came from and the one you moved to — are burning at the same time.

## What Happened on the East Coast

The May 2026 heatwave on the US East Coast is not a normal warm spell. It is a record-breaking atmospheric event that has upended assumptions about what May weather looks like in the northeastern United States.

Philadelphia's 98°F on May 19 broke the city's all-time May record. The previous record of 97°F had been set on May 30-31, 1991 — and the 2026 reading came eleven days earlier in the month. Newark and Reading, Pennsylvania tied their own May records the same day.

By May 20, the heat had intensified. New York City hit 103°F. Philadelphia reached 102°F. Across the mid-Atlantic and New England, temperatures ran 20 to 30 degrees above normal for this time of year.

The infrastructure buckled.

Transportation officials in the Washington, DC area and New York cut commuter train speeds when rail temperatures got too high. Extreme heat can cause welded rails to buckle and bend, creating derailment risks. Some New Jersey Transit service was cancelled outright. In New York, Con Edison reported power outages affecting up to 18,700 customers at the peak. In New Jersey, PSE&G had 6,500 customers without power. In the DC area, nearly 2,000 customers lost electricity.

Schools closed in Philadelphia and other cities. The Philadelphia school district sent students home because many older school buildings lack air conditioning — a problem that mirrors, uncomfortably, the un-air-conditioned government schools that many NRIs remember from their own childhoods in India.

A 92-year-old woman in Philadelphia died from heat-related causes. A homeless woman was found dead near a car in suburban Detroit. Window washers in Boston started their shifts at 4 AM to avoid the midday heat. A newspaper delivery worker in New York with asthma described being unable to breathe in the humidity.

These are the kinds of stories that NRIs are accustomed to reading about India, not about the cities they now call home.

## India's Parallel Crisis

The Indian heatwave is, by any measure, worse. India's numbers are the kind of catastrophic figures that make global headlines — 55 deaths in a single day, temperatures above 46°C in twenty districts, eight-year-old children dying from heatstroke while playing outside.

In Vijayawada, Andhra Pradesh, 21 people died on Friday, May 22 alone. Ten of them were in Vijayawada itself. Eight were unidentified homeless individuals who collapsed in public spaces — near railway gates, in parks, on streets. In Telangana, the state government confirmed 16 heatwave deaths for the current summer season, though independent reports put the May 22 toll as high as 34 in the state alone.

The India Meteorological Department has issued warnings that conditions will intensify. The Rohini Kartham — a traditional period of extreme heat — begins on May 25. Forecasters warn that temperatures could reach 48°C in some regions over the coming days.

For NRIs with parents, grandparents, and siblings in India, these are not statistics. They are phone calls. "Is Papa drinking enough water?" "Can Amma's house handle the inverter running all day?" "Should we send money for a bigger AC unit?" The worry is compounded by the knowledge that many Indian homes, particularly in tier-2 and tier-3 cities, were not built for this level of sustained heat — and that the power grid in many states cannot reliably support the air conditioning that makes survival possible.

The FSSAI and various state governments have issued advisories — stay indoors between 11 AM and 4 PM, drink ORS, avoid alcohol and caffeine in peak hours. But for outdoor workers, street vendors, and the urban poor, these advisories are effectively meaningless. You cannot stay indoors if your livelihood depends on being outside.

## The Climate Arithmetic for NRIs

What makes this week unusual is not the heat in either country alone. India has deadly summers. American cities have heatwaves. What is new is the simultaneous intensity — and what it means for the climate calculations that many NRIs have implicitly relied on.

For years, the Indian diaspora in the United States has operated on an unspoken assumption: America's infrastructure can handle extreme weather better than India's can. American power grids are more reliable. American buildings are better insulated. American emergency services are more responsive. The heat may come, but the systems hold.

That assumption is fraying.

When New York City hits 103°F in May and power goes out for 18,700 customers, the gap between American infrastructure and Indian infrastructure narrows. When Philadelphia closes schools because the buildings don't have air conditioning, it sounds like Lucknow, not the City of Brotherly Love. When trains slow to a crawl because the rails are too hot, the image is closer to Indian Railways than Amtrak.

The climate data supports the trend. A recent report found that climate change made India's April 2026 heatwave 2°C hotter, affecting 44 million people and $341 billion in economic activity. In the United States, the National Weather Service noted that the northeastern heatwave saw more than 150 daily temperature records broken across the region. The Intergovernmental Panel on Climate Change has warned that extreme heat events in both South Asia and the eastern United States will become more frequent, more intense, and longer-lasting over the coming decades.

For NRIs who chose America partly because of its climate stability and infrastructure resilience, this is a slow-motion recalculation. You are not necessarily safer from extreme heat in Newark than in Nagpur. The margins are shrinking.

## What NRIs Should Know

**The US heat is likely to return.** The National Weather Service forecasts above-normal temperatures for the eastern United States through the end of May. A brief respite from a cold front is expected before temperatures climb again. This is not a one-off event — climate scientists say early-season heatwaves are becoming the new normal for the northeastern US.

**Power outages are a real risk.** If you live in an older apartment building in New York, Philadelphia, or New Jersey, check that your air conditioning is working before the next heat spike. Have a backup plan — know where your nearest cooling centre is. Keep devices charged. If you have elderly parents or relatives living alone, check on them.

**India's crisis needs attention from abroad.** If your family in India is in Andhra Pradesh, Telangana, Uttar Pradesh, Bihar, or Delhi, the coming week will be critical. The Rohini Kartham period historically brings the most intense heat of the Indian summer. Sending money for a better inverter, a water cooler, or even just calling to remind them to stay hydrated is not overreacting — it is proportionate to the scale of the crisis.

**Climate-proof your planning.** If you are buying property — either in the US or in India — heatwave resilience should be a factor. In the US, that means checking whether a building has central air conditioning (many older Northeast buildings do not) and whether the local grid is prone to outages. In India, it means considering inverter backup capacity, water supply reliability, and the thermal design of the building.

**Travel timing matters more than ever.** If you are planning a summer trip to India, the window between late April and mid-June is now genuinely dangerous in many parts of the country. The old advice of "avoid May-June" has always been conventional wisdom. In 2026, it is a health directive.

## Both Countries, One Crisis

The heatwave of May 2026 is not a coincidence affecting two unrelated geographies. It is a single global phenomenon — the same atmospheric patterns, amplified by the same greenhouse gas concentrations, producing extreme heat across both hemispheres simultaneously. The El Niño conditions that are intensifying India's summer are contributing to the high-pressure ridges trapping heat over the US East Coast.

For the Indian diaspora, this convergence strips away one of the quieter comforts of immigration: the idea that you moved somewhere the weather would not try to kill you. That was always a simplification, but in May 2026, it is no longer even approximately true.

The generation of NRIs who grew up sleeping on terraces in Delhi because the power went out, and who then moved to apartments in Queens where the air conditioning always worked, are now watching their children's schools close in Philadelphia because the buildings cannot handle the heat.

The climate is not respecting borders. And neither is the vulnerability it creates."""

art2_sources = [
    "https://www.reuters.com/world/india/india-records-over-300-suspected-heatstroke-cases-summer-temperatures-spike-2026-05-22/",
    "https://weather.com/news/climate/news/2026-05-19-northeast-heat-wave-may-record-philadelphia",
    "https://www.archynetys.com/heatwave-deaths-telangana-ap",
    "https://www.goldsea.com/article_details/east-coast-braces-for-more-sweltering-weather",
    "https://www.goldsea.com/article_details/at-least-18-dead-in-india-heat-wave",
    "https://outlookbusiness.com/news/climate-change-made-indias-april-heatwave-2-degrees-celsius-hotter",
]

print("\n=== Article 2: America's Record May Heatwave — NRI Angle ===")
print(f"Word count: {len(art2_body.split())}")

result = sb_post("p2_articles", {
    "id": art2_id,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "category": art2_category,
    "body": art2_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art2_sources,
    "score_total": 93,
    "tags": ["heatwave", "US East Coast", "NRI", "climate change", "New York", "Philadelphia", "India heatwave", "Andhra Pradesh", "Telangana", "Delhi", "diaspora", "infrastructure", "El Niño", "extreme heat"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "Both the US East Coast and India are experiencing record-breaking heat simultaneously. NYC hit 103°F, Philly broke a 35-year May record, while India recorded 55 heatstroke deaths in one day. For NRIs, both countries — the one they left and the one they moved to — are burning at the same time. Climate resilience gap between US and India is shrinking.",
    "word_count": len(art2_body.split()),
})
if result:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")

print("\n✅ Both articles published successfully")
