#!/usr/bin/env python3
"""NRI World writer — 2026-06-27 17:00 PT run."""

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
        "headline": "Modi Wrote in Creole to a Diaspora That Has Been in Seychelles Since Before America Was a Country",
        "subheadline": "India's prime minister is visiting a 115-island archipelago in the Indian Ocean where Tamil settlers arrived in 1770 — and where Indians now make up nearly a tenth of the population.",
        "slug": make_slug("modi-seychelles-diaspora-creole-golden-jubilee-indian-ocean"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Indian community in Seychelles is one of the oldest continuous diaspora settlements in the world, yet remains almost invisible to the broader NRI conversation. Modi's visit — and his choice to address them in the local Creole language — underscores how far-flung India's people-to-people ties really are, even in a nation of just 121,000.",
        "tags": ["nri", "diaspora", "seychelles", "modi", "indian-ocean", "golden-jubilee"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/indian-diaspora-in-seychelles-excited-to-welcome-pm-modi-calls-him-indias-dhurandhar--20260627113605"},
            {"name": "Nation Press", "url": "https://www.nationpress.com/national/modi-hails-indian-diaspora-in-seychelles"},
            {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/international/3337441-pm-modis-historic-visit-to-seychelles-strengthening-ties-and-celebrating-milestones"},
            {"name": "Seychelles Nation", "url": "https://www.nation.sc/articles/250-years-ago"},
            {"name": "Sociology Institute", "url": "https://sociology.institute/people-of-indian-origin-in-francophone-africa/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Big_Ben_Clock_Tower_-_Victoria_-_Mahe_-_Seychelles_-_01.jpg/1280px-Big_Ben_Clock_Tower_-_Victoria_-_Mahe_-_Seychelles_-_01.jpg",
        "image_caption": "The clock tower in Victoria, Mahé — the capital of Seychelles and the smallest capital city in the world",
        "image_attribution": "Wikimedia Commons",
        "body": """When Prime Minister Narendra Modi landed in Victoria, the capital of Seychelles, on Saturday, the Indian community on this tiny archipelago had already spent weeks rehearsing dances, stringing garlands, and plastering welcome posters across the city's narrow streets. Then Modi did something unexpected: he posted on social media in Seychellois Creole, the local lingua franca. "*Kominote Endyen dan Sesel in akord mwan en lakey salere ozordi swar*," he wrote — "The Indian community in Seychelles gave me a warm welcome this evening."

It was a small linguistic gesture, but a pointed one. The Indian diaspora in Seychelles is not large in absolute numbers — perhaps 10,000–12,000 people in a country of 121,000 — yet its roots run deeper than those of almost any other Indian settlement abroad. Tamil labourers and traders arrived on these islands in 1770, the same year the first permanent settlers stepped ashore. Indians were, in the most literal sense, among the founders of the Seychellois nation.

## Older than independence

The archipelago itself only became an independent republic in 1976. Its Indian community predates that milestone by more than two centuries. Five Indians — named in colonial records as Charvy, Moutia, Cormara Mienate, Corinthe, and Domingue — were among the 28 people who disembarked from the *Thélèmaque* at Anse Cabot on Sainte Anne Island in August 1770. They were brought as slaves by French colonists from Mauritius. Later waves of indentured labourers and free traders followed, and by the turn of the twentieth century, roughly 3,500 Tamil speakers lived among a total population of about 19,000.

Today, the Indian community represents approximately 9 per cent of the population, according to the National Bureau of Statistics — up from 4.4 per cent in 2010, driven partly by fresh economic migration. A statue of Mahatma Gandhi stands in Victoria's Peace Park, and Indian cultural troupes regularly perform on the islands. Hinduism accounts for 5.4 per cent of the country's religious composition, making it the second-largest faith after Christianity.

## Why Modi came

The formal occasion for the three-day state visit (June 27–29) is the Golden Jubilee of the National Day of Seychelles — 50 years of independence. Modi was invited as Guest of Honour by President Patrick Herminie. It is his third visit to the archipelago, following trips in 2015 and 2018, and it comes under India's Vision MAHASAGAR framework — short for Mutual and Holistic Advancement for Security and Growth Across Regions — which positions Indian Ocean island states as priority partners in maritime security, blue-economy cooperation, and people-to-people diplomacy.

Indian High Commissioner Rohit Rathish described the visit as a "historic milestone" and pointed to the 250-year thread connecting the two nations. "Our destinies have been intertwined for 250 years," Rathish said. "The bilateral partnership, the diplomatic relations, are but the latest chapter in this relationship."

For the business community, the visit carries commercial weight. Seychelles is a fully import-dependent economy, and India currently supplies less than half of its imports, leaving significant headroom for expansion in food, medical supplies, construction materials, and tourism. Venu Gopal Beravelli, Group Managing Director of Global Supply Centre Group, told ANI that the visit had already attracted attention from international markets: "As soon as the news comes out that PM Modi is visiting, all the other markets have already started looking at Seychelles."

## A diaspora that seldom makes headlines

For the 37 million-strong global Indian diaspora, the Seychelles chapter is almost never discussed. Silicon Valley engineers, Gulf construction workers, NHS doctors — these are the archetypes that dominate the NRI narrative. The Tamil shopkeepers of Victoria, the Gujarati hoteliers of Beau Vallon, the Hindi-speaking workers preparing cultural dances at the airport — they occupy a different register entirely.

"I have been working here for the last 15 years," Bharat Irani, a Gujarati member of the community, told IANS. "We cannot express how happy we are. It has been 11 years since he last visited Seychelles."

Others, newer arrivals, said they were meeting a sitting prime minister for the first time. "This will be the first time I will see Prime Minister Modi in person," said one community member who has lived in Seychelles since 2016. "Indians receive great respect in Seychelles, and the people here also embrace our culture."

What sets this diaspora apart is not achievement on the world stage but endurance in a very small place — a quarter-millennium of quiet contribution to a country most Indians could not find on a map. Modi's Creole-language post was, in that context, a nod not just to cultural diplomacy but to a community that has outlasted empires and still shows up to dance at the airport."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Saudi Arabia Just Told 2.4 Million Indians They Can Stop Renting. Few Know What That Actually Means.",
        "subheadline": "A new digital portal lets foreigners buy property across the Kingdom for the first time — opening the door for millions of Indian workers who have spent decades as tenants in the Gulf's biggest economy.",
        "slug": make_slug("saudi-arabia-property-portal-nri-indian-workers-gulf-ownership"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the 2.4 million Indians living in Saudi Arabia — the largest expatriate group in the Kingdom — the ability to own property transforms the economic equation of Gulf migration from temporary labor to potential long-term investment and stability.",
        "tags": ["nri", "diaspora", "saudi-arabia", "real-estate", "gulf", "property", "investment"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Dainik Bhaskar English", "url": "https://www.bhaskarenglish.in/business/news/saudi-arabia-property-buy-for-indians-online-apply-real-estate-138292910.html"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/saudi-arabia-opens-property-ownership-to-foreigners-all-you-need-to-know-102322.htm"},
            {"name": "REGA Saudi Arabia", "url": "https://www.rega.gov.sa/en/ownership"},
            {"name": "Mondaq", "url": "https://www.mondaq.com/saudiarabia/real-estate/1597640/saudi-arabia-foreign-property-ownership-a-transformational-shift"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Riyadh_Skyline.jpg/1280px-Riyadh_Skyline.jpg",
        "image_caption": "The Riyadh skyline — Saudi Arabia's capital and the centre of its expanding real estate market",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, the deal has been simple: Indians go to Saudi Arabia, earn a salary, send money home, and rent a flat until the contract ends. Ownership — of a house, a shop, a piece of land — was never part of the arrangement. It was, by law, off the table.

That changed this month. Saudi Arabia's Real Estate General Authority (REGA) launched a digital portal called "Saudi Properties," the first official platform allowing foreign nationals and companies to apply online to purchase property anywhere in the Kingdom, except the holy cities of Mecca and Medina. The portal emerged from the Foreign Real Estate Ownership Law, implemented in January 2026, which dismantled the legal barrier that had kept non-Saudis as perpetual tenants.

For the 2.4 million Indians who live and work in Saudi Arabia — the country's largest expatriate population — the implications are significant, if far from straightforward.

## What the portal actually does

The Saudi Properties platform is, in REGA's words, a "one-stop shop." Foreign buyers can check their eligibility, browse approved properties and investment zones, apply for ownership, and track the status of their application — all digitally. For Indians living in Saudi Arabia, the process requires only their residency number. NRIs based outside the Kingdom will need a digital ID obtained through the Saudi embassy. Companies can apply after registering on the "Invest Saudi" platform.

The geographic scope is broad: developed urban areas across Saudi Arabia, plus the mega-projects that have come to define the Vision 2030 agenda — NEOM, the Red Sea Project, Diriyah, and Al-Ula among them. The restrictions are surgical. In Mecca and Medina, ownership is limited to Saudi companies and Muslim expatriates. Everywhere else, the door is technically open.

## The Dubai comparison

The obvious question is whether Saudi Arabia can replicate Dubai's success with foreign property buyers — and the answer is: not yet, and possibly not soon. Dubai has operated a freehold property market for over two decades. Indians are already its largest foreign buyer group, accounting for roughly a fifth of all transactions in some recent quarters. The regulatory infrastructure is mature, the secondary market is liquid, and the legal precedents are well established.

Anuj Kejriwal, CEO (Retail) at Anarock Group, noted the contrast. "Since Saudi's market is new, many buyers may still prefer tried and tested markets like Dubai," he said. "Initially, Indian demand may also remain somewhat limited because regulations are still being formed." But, he added, the long-term trajectory is different: "Large urban and tourism projects are underway in Saudi under Vision 2030. Capital growth is expected in the long term."

The Saudi real estate market was valued at roughly $81 billion in 2025 and is projected to nearly double to $155 billion by 2034. The giga-projects alone represent hundreds of billions in planned investment. For investors willing to take the early-mover bet, the scale is hard to ignore.

## What it means for the Gulf diaspora

The broader significance lies not in whether Indians rush to buy Saudi flats tomorrow — most will not — but in what the policy shift signals about the relationship between Gulf states and their migrant workforces.

For decades, the kafala (sponsorship) system and ownership restrictions kept Indian workers in a transactional relationship with the Gulf: labour in exchange for wages, with no stake in the place itself. Dubai began chipping away at that model years ago. Saudi Arabia is now following, partly out of economic necessity — Vision 2030 needs foreign capital and long-term residents, not just temporary hands — and partly as a competitive response to the UAE's head start.

The shift arrives at a time when India's Gulf diaspora faces broader pressures. Remittances from West Asia remain the largest single corridor of Indian remittances globally, but the composition of migration is changing. Fewer low-skilled workers, more white-collar professionals. Fewer short-term contracts, more semi-permanent relocations. Property ownership fits a diaspora that is, slowly, settling in rather than passing through.

## The fine print matters

Several cautions apply. The regulations are still being formed; the geographic-scope document governing which zones are open has not been fully published for all cities. Property ownership does not confer or modify residency rights — you can buy a flat, but it does not get you a visa. The secondary market for foreign-owned properties is essentially nonexistent. And financing options for non-Saudi buyers remain thin, though Saudi banks and Indian lenders that specialise in NRI financing are likely to expand offerings as the market develops.

Then there is the macroeconomic context. Regional real estate has been under pressure since the US-Iran conflict disrupted confidence in the Gulf. Dubai residential sales fell about 20 per cent in parts of early 2025. Saudi Arabia may be entering a buyer's market — which could be a feature, not a bug, for early adopters.

For the 2.4 million Indians in the Kingdom, the real question is not whether they *can* own a piece of Saudi Arabia. The question is whether, after generations of renting, they trust the offer enough to stay."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
