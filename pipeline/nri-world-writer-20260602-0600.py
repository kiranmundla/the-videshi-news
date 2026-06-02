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
        "headline": "Five South Asian Candidates Just Swept Georgia's Primaries. The Runoff Could Make History Again.",
        "subheadline": "Nabilah Islam Parkes is one runoff away from becoming the first South Asian lieutenant governor nominee in Georgia history. She is not alone on the ticket.",
        "slug": make_slug("georgia-primaries-south-asian-candidates-nabilah-jyot-singh"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Georgia's South Asian community — over 600,000 Asian Americans in the state — is translating demographic growth into political representation at an unprecedented pace, with candidates winning across state house, senate, and statewide races in a single primary cycle.",
        "tags": ["nri", "diaspora", "politics", "georgia", "elections", "south-asian"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/21/indian-american-impact-congratulates-endorsed-candidates-on-historic-wins-in-georgia/"},
            {"name": "Wikipedia - 2026 Georgia lieutenant gubernatorial election", "url": "https://en.wikipedia.org/wiki/2026_Georgia_lieutenant_gubernatorial_election"},
            {"name": "Georgia Trend Daily", "url": "https://www.georgiatrend.com/2026/03/06/georgia-trend-daily-march-6-2026/"},
            {"name": "Wikipedia - 2026 Georgia House of Representatives election", "url": "https://en.wikipedia.org/wiki/2026_Georgia_House_of_Representatives_election"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7103185/pexels-photo-7103185.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On May 19, Georgia held its primary elections. By Wednesday morning, five South Asian candidates endorsed by Indian American Impact had either won outright or advanced to runoff contests — a single-night performance that would have been unimaginable a decade ago in a state where the community's political presence was effectively zero.

The headline result belongs to Nabilah Islam Parkes. The state senator from Duluth advanced to a June 16 runoff in the race for lieutenant governor, putting her one election away from becoming the first South Asian and Asian American nominee for the position in Georgia history, from any party. Parkes, who previously represented State Senate District 7, had initially filed to run for state insurance commissioner before switching to the lieutenant governor race in early March — a last-minute pivot that appears to have paid off. She will face state senator Josh McLaurin in the runoff.

Then there is Jyot Singh. The CEO and community organiser won the Democratic primary outright in State House District 97, defeating Jacques Laurent. Singh is on track to become the first Sikh elected official in Georgia's history. He succeeds Ruwa Romman, the Palestinian American incumbent who vacated the seat to run for state senate, and arrives with endorsements from U.S. Representatives Hank Johnson and Jonathan Jackson, as well as the Georgia Working Families Party.

## A deeper bench than it looks

Saira Draper won a competitive Democratic primary for State Senate District 44. Rahul Garabadu advanced to a runoff for State Senate District 7. And Akbar Ali secured the Democratic nomination for House District 106, continuing his tenure as the youngest state legislator in Georgia.

These are not isolated victories. They are the product of a sustained organisational infrastructure that has been building for years. Indian American Impact, the political action group that endorsed all five candidates, has now backed more than 200 candidates since its founding in 2016 and marshalled upwards of $20 million toward campaigns and voter mobilisation efforts.

## The Georgia calculus

Georgia is home to more than 600,000 Asian American residents, a population that has grown rapidly in the suburban counties ringing Atlanta — Gwinnett, Forsyth, and Fulton in particular. The state's South Asian community, concentrated in technology corridors and professional suburbs, has been registering and voting at increasing rates since the 2020 election cycle.

What makes this primary cycle different is the breadth. In previous years, a single South Asian candidate winning a state legislative seat was treated as a milestone. Five candidates advancing simultaneously — across state house, state senate, and a statewide constitutional office — suggests the community has moved past the milestone phase and into something more structural.

Chintan Patel, executive director of Indian American Impact, framed it in institutional terms. "Last night's results in Georgia speak to the growing political power and representation of our communities," he said. "Each of these leaders will fight every day to lower costs for working families, protect fundamental freedoms, and fiercely defend immigrant communities."

## What the runoff means

The June 16 runoff will determine whether Parkes's candidacy becomes a general election reality. Georgia's runoff system, which requires a majority rather than a plurality to win a primary, has historically disadvantaged candidates from smaller demographic blocs — they can win a crowded primary on plurality but struggle to consolidate support in a head-to-head contest.

For Parkes, the math is straightforward but not easy. She will need to turn out the same coalition that propelled her through the primary while persuading voters who backed eliminated candidates to consolidate behind her campaign. The lieutenant governor's office in Georgia carries real procedural power — the officeholder presides over the state senate and controls committee assignments.

For the diaspora, the symbolism extends beyond Georgia. If Parkes secures the nomination, she would be among the highest-ranking South Asian elected officials in the American South, a region where the community's political representation has historically lagged behind states like California, New Jersey, and Illinois.

Singh's victory is equally significant for a different constituency. Sikh Americans, who have faced persistent discrimination and violence — including the 2012 Oak Creek temple shooting — have long been underrepresented in elected office. His win in Georgia, a state not traditionally associated with Sikh political activism, signals that the community's political engagement is broadening geographically.

The general election is in November. The primaries just drew the map."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "London's Favourite Indian Restaurants Are Invading New York. The Diaspora Built the Beachhead.",
        "subheadline": "Dishoom has locked down a Madison Square Park address. Ambassadors Clubhouse is already impossible to book. Darjeeling Express and Kricket are next. The British Indian restaurant wave has arrived in Manhattan.",
        "slug": make_slug("british-indian-restaurants-new-york-dishoom-ambassadors-clubhouse"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The wave of British Indian restaurants crossing the Atlantic reflects how the diaspora's culinary heritage — shaped in London's Brick Lane and Bombay's Irani cafés — is now setting the global fine-dining agenda, with Indian Americans as both the audience and the business case.",
        "tags": ["nri", "diaspora", "restaurants", "food", "new-york", "london", "dishoom"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Caper Media", "url": "https://caper.media/p/where-exactly-is-dishoom-opening-in-new-york"},
            {"name": "The Caterer", "url": "https://www.thecaterer.com/news/whats-next-dishoom-investor-deal"},
            {"name": "Restaurant Online", "url": "https://www.restaurantonline.co.uk/Article/2025/02/19/restaurant-brands-looking-to-crack-the-us"},
            {"name": "Meyka", "url": "https://meyka.com/articles/dishoom-us-debut-uk-restaurant-expansion"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/9738992/pexels-photo-9738992.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """A filing with the New York State Liquor Authority has revealed what curry obsessives on both sides of the Atlantic have been waiting for: Dishoom, the London-born restaurant chain that turned Bombay's vanishing Irani café culture into a dining phenomenon, will open at 11 East 26th Street, a luxury office building steps from Madison Square Park. A representative has confirmed the opening for 2027.

This is not one restaurant crossing the pond. It is a wave.

JKS Restaurants' Ambassadors Clubhouse, a Punjabi fine-dining concept, has already opened in Manhattan and promptly become one of the most difficult reservations in the city. Asma Khan's Darjeeling Express, famous for its all-women kitchen and a Netflix appearance that made it a London institution, is planning a New York outpost after a sold-out pop-up. Kricket, the Indian small plates restaurant that built its reputation at Brixton's Pop Brixton before expanding across London, is eyeing a 2026 Manhattan launch. And Gymkhana, JKS's Michelin-starred Indian restaurant, is headed to Las Vegas.

## The Dishoom factor

Dishoom is the one most likely to change the conversation. Founded by Shamil and Kavi Thakrar in Covent Garden in 2010, the chain now operates ten restaurants across London, Manchester, Edinburgh, and Birmingham, plus its Permit Room bar spin-off. It secured a major investment deal valued at £300 million and has been exploring American locations since before the pandemic.

The 2024 pop-up at Pastis — the New York French brasserie owned by Stephen Starr — served as a proof of concept. Dishoom took over Pastis's kitchen for weekday breakfast service, bringing its signature bacon naan rolls, chilli cheese toast, and house chai to Meatpacking District diners. It sold out immediately.

"I was blown away by breakfast at Dishoom," Starr said at the time. "There's no Indian restaurant that's ever done that, and I still think about it all the time."

CEO Brian Trollip has been characteristically patient about the expansion. "We've been looking fairly patiently for a long time now," he told The Caterer. "Someone can furnish you with all the data in the world and it's still no substitute for truly understanding a city and the way that people live within it." The team also looked at sites in Boston, Chicago, and Washington, D.C. before settling on New York.

## Why Britain, why now

The question worth asking is why London's Indian restaurants are the ones crossing the Atlantic, rather than India's own fine-dining establishments or the existing Indian restaurant ecosystem in the United States.

The answer lies partly in the diaspora itself. Britain's Indian restaurant culture is nearly 80 years old, shaped by waves of migration from the subcontinent that created a culinary tradition distinct from anything in India. The chicken tikka masala, the balti, the Irani café breakfast — these are diaspora inventions, born from the collision of Punjabi, Bengali, and Bombay food traditions with British tastes and British ingredients. They carry a cultural confidence that many American Indian restaurants, often caught between authenticity and accessibility, have struggled to project.

The economic case is equally compelling. New York diners accept higher checks, which offsets the punishing rents and labour costs. Dollar revenue looks attractive when converted to pounds. And the Indian American population — 4.4 million strong, the highest-earning ethnic group in the country — represents a built-in audience that understands both the food and the cultural references.

## The competitive landscape

New York is not short of Indian restaurants. The city has Junoon, Semma, Dhamaka, Adda, and dozens of other establishments that have pushed Indian cuisine well beyond the butter-chicken-and-naan template. What the British imports bring is something different: a particular approach to hospitality that wraps Indian food in a broader cultural narrative — the Irani café nostalgia of Dishoom, the members-club exclusivity of Ambassadors Clubhouse, the feminist kitchen of Darjeeling Express.

For the diaspora in particular, these restaurants carry a specific emotional charge. Many Indian Americans have encountered Dishoom during trips to London, standing in the famously long queues outside the King's Cross or Shoreditch locations. The restaurant's aesthetic — ceiling fans, cracked tile, sepia photographs of old Bombay — speaks to a particular kind of diasporic longing that transcends geography.

If Dishoom's Manhattan unit delivers strong table turns and controlled costs, Trollip has suggested the brand could expand to other American cities. He has also floated the idea of a Dishoom hotel, which he described as "either a bonkers or a brilliant idea."

The British Indian invasion of New York is a story about food. It is also a story about the diaspora's cultural products — shaped in one country, refined in another, now being exported to a third — finally being valued at the prices they deserve."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
