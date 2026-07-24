#!/usr/bin/env python3
"""NRI World Writer — 2026-06-27 05:00 PDT"""
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

# ─── ARTICLE 1: Indian Restaurants Going Global ──────────────────────────

art1_body = """From a 3,000-square-foot flagship in London's Leicester Square to a two-storey walk-up in Manhattan's East Village, a new generation of Indian restaurants is making landfall across two continents this summer — and doing so with an ambition that would have been unthinkable a decade ago.

The most eye-catching arrival is Haldiram's, the 88-year-old Indian snack empire that has spent nearly a century teaching the subcontinent the meaning of bhujia and soan papdi. This June it opened its first full-service restaurant outside India, right in the heart of London's theatre district. The 120-cover venue — steered by Rhea Agarwal, a third-generation member of the founding family — goes well beyond Haldiram's traditional quick-service counter. Its menu revolves around the street-food dishes that have always been the brand's calling card — chole bhature, pav bhaji, raj kachori, and an expansive chaat selection — but the format is unrecognisable: premium casual dining, a dedicated sweets retail counter, fusion desserts designed for British palates, and interiors pitched somewhere between heritage motif and "quiet luxury."

"For many Indians living abroad, these flavours carry a deep sense of nostalgia," Agarwal told Broadsheet. "At the same time, we want to introduce a wider audience to the diversity of Indian cuisine."

Haldiram's already operates a production facility in Southall that has been supplying sweets across the UK and Europe since 2018. The Leicester Square restaurant is the next logical step — and arguably the riskiest, staking a beloved mass-market brand on the notoriously unforgiving London dining scene.

Across the Atlantic, chef Aarthi Sampath has taken a different route entirely. Her debut restaurant, Drāvida, opened in late June at 211 First Avenue in Manhattan's East Village. Sampath, who moved from Mumbai to the United States in 2013 and won both *Chopped* and *Beat Bobby Flay* on the Food Network, has built a menu that reads like a map of South Asian migration itself. There are Trinidad's beloved Doubles, South Africa's Oxtail Bunny Chow served in bread, Indonesian-inflected Idli & Shrimp, and a Malaysian Nasi Kandar Feast — each dish tracing a real diaspora corridor across the Caribbean, Africa, and Southeast Asia.

It is, in other words, not simply an Indian restaurant. It is a restaurant about what happens to Indian food when Indians leave India — which, for a community that has scattered itself across 200 countries and 35 million people, is an uncommonly resonant concept. A speakeasy-style bar called Jam and Jaggery occupies a 20-seat annexe upstairs, serving cocktails like the Passionfruit Lassi and the Drāvida Highball.

Meanwhile, in the City of London, another opening is pushing the same envelope from the opposite direction. Bulbul, the first UK venture from India-based restaurateurs Rohan D'Souza and Twinkle Keswani — she was named Young Restaurateur of the Year by *The Economic Times* in 2023 — takes inspiration from the pair's travels across India. Their acclaimed portfolio spans from Goa's Lazy Goose to a café in the Himalayan town of Leh and a restaurant on the backwaters of Kerala. Bulbul brings that range to Tudor Street near Blackfriars: forest pepper crab dosa, Goan shrimp balchão on melba toast, nilgiri beef short rib korma. Interiors by Mumbai's Right Brain Design Studio, carpets from Jaipur Rugs, staff uniforms from Mumbai label Papa Don't Preach. Every detail, down to the floral installation, is sourced from India.

What unites these openings is not geography or price point but a shared thesis: that Indian cuisine, in the hands of entrepreneurs who have grown up eating it, has been radically undervalued abroad. The old curry-house model — chicken tikka masala as a British national dish — served its purpose, but it flattened a subcontinent's worth of culinary range into a handful of familiar dishes. The new generation is betting that diners in New York and London are ready for something more specific: regional, concept-driven, unapologetically rooted.

For NRIs, the stakes are personal. Every one of these restaurants is, at some level, answering a question that the diaspora has been asking for decades: why does the food we actually grew up eating never seem to make it onto a menu? Haldiram's chole bhature at Leicester Square, Sampath's bunny chow in the East Village, D'Souza's dosa in the City — each is an attempt to close that gap, one plate at a time."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Haldiram's at Leicester Square, Drāvida in the East Village: Indian Restaurants Are Finally Playing Offence Abroad",
    "subheadline": "An 88-year-old snack empire, a Food Network champion, and two Goa-to-London restaurateurs are betting that the diaspora's food has been undersold for too long.",
    "slug": make_slug("haldirams-dravida-bulbul-indian-restaurants-london-nyc-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "These openings reflect the diaspora's long frustration that the food they actually grew up eating — regional, street-level, migration-shaped — rarely made it onto restaurant menus abroad. The new wave is correcting that.",
    "tags": ["nri", "diaspora", "food", "restaurants", "london", "new-york", "haldirams", "indian-cuisine"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Hospitality & Catering News", "url": "https://hospitalityandcateringnews.com/2026/05/indias-largest-sweet-and-snack-brand-haldirams-launches-first-central-london-restaurant-in-leicester-square/"},
        {"name": "Curly Tales", "url": "https://curlytales.com/india/food/new-yorks-new-indian-restaurant-takes-diners-from-mumbai-to-chennai-in-a-single-bite/"},
        {"name": "The Caterer", "url": "https://thecaterer.com/news/india-based-restaurateurs-to-open-contemporary-indian-diner-in-the-city-of-london"},
        {"name": "Broadsheet", "url": "https://broadsheet.com/london/food-and-drink/just-in-haldirams-indias-largest-sweet-and-snack-brand-is-opening-its-first-uk-restaurant-in-london/"},
        {"name": "Restaurant India", "url": "https://restaurantindia.in/news/haldirams-to-open-first-full-service-uk-restaurant-in-london.html"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/9316203/pexels-photo-9316203.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    "image_caption": "An Indian restaurant table set with traditional dishes and warm lighting",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}

# ─── ARTICLE 2: Anil Menon ISS Mission ──────────────────────────────────

art2_body = """On July 14, a Soyuz spacecraft will lift off from the Baikonur Cosmodrome in Kazakhstan carrying three crew members to the International Space Station. One of them, a 44-year-old emergency medicine physician and US Space Force colonel named Anil Menon, will become the latest astronaut of Indian descent to reach orbit — and, by most measures, one of the most overqualified people ever to strap into a seat.

Menon's résumé is the kind of thing that reads like parody until you confirm every line. He holds a degree in neurobiology from Harvard, a master's in mechanical engineering and a medical degree from Stanford, and completed residencies in both emergency medicine and aerospace medicine. He was SpaceX's first flight surgeon, helping to launch the company's first human mission — the Demo-2 flight in May 2020 — and built the medical organisation that now supports crewed Dragon flights. Before that, he served as a crew flight surgeon for NASA's own expeditions aboard the ISS. In his spare time he practises emergency medicine at Memorial Hermann's Texas Medical Center, teaches residents at the University of Texas, and has completed an Ironman triathlon.

He will spend approximately eight months aboard the station, returning to Earth in spring 2027, as part of Expeditions 74 and 75.

The mission has particular resonance for India's diaspora. Menon was born and raised in Minneapolis to an Indian father and a Ukrainian mother — immigrants who planted roots in the American Midwest and produced a son who would become, literally, the highest-achieving member of either community. He was selected for NASA's 2021 astronaut class, the 23rd in the agency's history, and graduated in 2024 after two years of intensive training.

His wife, Anna Menon, is herself a NASA astronaut candidate — selected in the agency's 24th class — and previously served as Lead Space Operations Engineer at SpaceX and a crew member on the Polaris Dawn mission, part of Jared Isaacman's Polaris programme. Both appeared in the Netflix documentary *Countdown: Inspiration4 Mission to Space*. Their children will watch one parent launch into orbit this July and may, in a few years, watch the other follow.

The experiments Menon will conduct aboard the ISS during his eight months aloft focus on problems that sound mundane until you realise no one has solved them in microgravity. Among the hundreds of investigations planned, he will study how astronaut vein structure, blood flow, and blood composition change in weightlessness — research that could reshape how the medical community understands cardiovascular health both in space and on Earth. He will also test whether the station's potable water system can produce intravenous fluids, a capability that would be essential on missions to the Moon or Mars, where resupply from Earth is not an option.

The timing is notable. NASA has been steadily adjusting its 2026 flight plan, moving the SpaceX Crew-13 mission from November to mid-September to accelerate US crew rotations. Against this backdrop, Menon's Soyuz MS-29 flight underscores the continuing US-Russia cooperation on the station even as geopolitical tensions simmer elsewhere.

For Indian-Americans, the Menon family story carries a specific, almost aspirational weight. The Indian diaspora in the US — now more than 4.4 million strong — has sent its members to the corner offices of Microsoft, Google, and IBM, to the governor's mansions of Louisiana and South Carolina, and to the mayoralty of New York City. Space was one of the few frontiers that remained relatively untouched. Kalpana Chawla, who flew on the shuttle twice and died in the Columbia disaster in 2003, remains the community's most emotionally resonant space figure. Sunita Williams has logged 322 days in orbit across four missions. Raja Chari commanded SpaceX Crew-3 in 2021.

Menon's mission adds a new chapter — and a new kind of story. He is not a pilot or a military test jock in the traditional astronaut mould but a physician-engineer whose path to space ran through earthquake relief in Haiti, a flight surgeon's seat in an F-15, and the medical tent at a Reno air show crash. If the old astronaut archetype was the steely-eyed missile man, Menon's is something closer to the diaspora's self-image: relentlessly credentialled, quietly versatile, and comfortable operating at the intersection of disciplines that most people treat as entirely separate fields.

His launch from Baikonur in two-and-a-half weeks will be watched, with particular attention, from Minneapolis to Mumbai."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Son of Indian and Ukrainian Immigrants Is About to Board the ISS. He Brought His Stethoscope.",
    "subheadline": "NASA astronaut Anil Menon, SpaceX's first flight surgeon and a US Space Force colonel, launches for an eight-month station mission on July 14 — adding a new chapter to the diaspora's quietly growing presence in orbit.",
    "slug": make_slug("anil-menon-nasa-astronaut-iss-soyuz-ms29-indian-diaspora-space"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Menon, born to Indian and Ukrainian immigrant parents in Minneapolis, represents the diaspora's expanding footprint beyond corporate boardrooms and into one of the last frontiers. His mission builds on the legacy of Kalpana Chawla, Sunita Williams, and Raja Chari.",
    "tags": ["nri", "diaspora", "nasa", "space", "anil-menon", "iss", "astronaut", "indian-american"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NASA", "url": "https://www.nasa.gov/news-release/nasa-astronaut-anil-menon-available-for-prelaunch-virtual-interviews/"},
        {"name": "NASA", "url": "https://www.nasa.gov/people/nasa-astronaut-anil-menon/"},
        {"name": "NASA", "url": "https://www.nasa.gov/news-release/nasa-astronaut-anil-menon-to-discuss-upcoming-launch-mission/"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Anil_Menon_(astronaut)"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/NASA_Astronaut_Anil_Menon_%28jsc2024e013690_alt%29.jpg/1280px-NASA_Astronaut_Anil_Menon_%28jsc2024e013690_alt%29.jpg",
    "image_caption": "NASA astronaut Anil Menon in his official flight suit portrait at Johnson Space Center",
    "image_attribution": "Wikimedia Commons / NASA",
    "body": art2_body.strip()
}

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
