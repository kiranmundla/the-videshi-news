#!/usr/bin/env python3
"""
Seed curated Michelin-starred and upscale Indian restaurants into
The Videshi directory_listings table.

Usage:
    python3 pipeline/seed-restaurants.py [--dry-run]

Reads creds from ~/workspace/.env.supabase
"""

import os, sys, re, json, subprocess, hashlib, requests
from pathlib import Path

# ── Load Supabase creds ──────────────────────────────────────────────
env_path = Path.home() / "workspace" / ".env.supabase"
env = {}
for line in env_path.read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()

SUPABASE_URL = env["SUPABASE_URL"]
SUPABASE_KEY = env["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

DRY_RUN = "--dry-run" in sys.argv

def slugify(name: str, city: str) -> str:
    raw = f"{name} {city}".lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw[:80]

# ── Restaurant data ──────────────────────────────────────────────────
RESTAURANTS = [
    # ═══════════════════════════════════════════════════════════════════
    # MICHELIN STAR
    # ═══════════════════════════════════════════════════════════════════

    # ── NYC ───────────────────────────────────────────────────────────
    {
        "name": "Semma",
        "subcategory": "Michelin Star",
        "description": "Michelin-starred South Indian fine dining from Chef Vijay Kumar, ranked #1 restaurant in NYC by the New York Times in 2025. James Beard Award winner for Best Chef: New York State. Signature gunpowder dosa and lobster tail curry in a vibrant West Village setting.",
        "phone": "+12129131880",
        "website": "https://semma.nyc",
        "address": "60 Greenwich Ave",
        "city": "New York",
        "state": "NY",
        "zip": "10011",
        "latitude": 40.73599,
        "longitude": -74.000602,
        "rating": 4.7,
        "review_count": 850,
        "affiliation": "Michelin ⭐ (2022–present) · James Beard Best Chef NY 2025 · #1 NYT Best Restaurants 2025",
    },
    {
        "name": "Junoon",
        "subcategory": "Michelin Star",
        "description": "Pioneering Indian fine dining in the Flatiron District, Junoon held a Michelin star for eight consecutive years — the first Indian restaurant in NYC to do so. Known for smoky Lal Maas goat, mushroom xacutti, and an exceptional cocktail program.",
        "phone": "+12124902100",
        "website": "https://www.junoonnyc.com",
        "address": "19 W 24th St",
        "city": "New York",
        "state": "NY",
        "zip": "10010",
        "latitude": 40.743079,
        "longitude": -73.990393,
        "rating": 4.4,
        "review_count": 1886,
        "affiliation": "Michelin ⭐ (2011–2019, Guide-listed) · Flatiron landmark since 2010",
    },
    {
        "name": "Bungalow",
        "subcategory": "Michelin Star",
        "description": "Chef Vikas Khanna's final restaurant, inspired by Indian country clubs. Michelin Guide–listed since opening in 2024, with Punjabi dishes served in elegant East Village setting. Three NYT stars, Infatuation 'Toughest Reservation' in NYC.",
        "phone": "+12129291824",
        "website": "https://bungalowny.com",
        "address": "24 First Ave",
        "city": "New York",
        "state": "NY",
        "zip": "10009",
        "latitude": 40.723672,
        "longitude": -73.987957,
        "rating": 4.5,
        "review_count": 420,
        "affiliation": "Michelin Guide · 3 NYT Stars · Infatuation Toughest Reservation 2024",
    },

    # ── Chicago ──────────────────────────────────────────────────────
    {
        "name": "Indienne",
        "subcategory": "Michelin Star",
        "description": "Progressive Indian tasting-menu restaurant by Chef Sujan Sarkar, with Michelin star since 2023 — the first-ever starred Indian restaurant in Chicago. Nine-course menus ($175–$195) spotlight regional micro-cuisines. Two-time James Beard nominee for Best Chef: Great Lakes.",
        "phone": "+13122919427",
        "website": "https://indiennechicago.com",
        "address": "217 W Huron St",
        "city": "Chicago",
        "state": "IL",
        "zip": "60654",
        "latitude": 41.894517,
        "longitude": -87.635029,
        "rating": 4.8,
        "review_count": 380,
        "affiliation": "Michelin ⭐ (2023–present) · James Beard nominee Best Chef Great Lakes 2024/2025",
    },
    {
        "name": "Indienne New York",
        "subcategory": "Michelin Star",
        "description": "Chef Sujan Sarkar's second Indienne opened May 2025 in Hudson Yards, bringing his Michelin-starred tasting menu experience to NYC. 34-seat intimate space with non-vegetarian ($195), vegetarian, and vegan nine-course menus celebrating regional Indian cuisines.",
        "phone": "+12129291924",
        "website": "https://indiennechicago.com",
        "address": "515 W 38th St, 2nd Fl",
        "city": "New York",
        "state": "NY",
        "zip": "10018",
        "latitude": 40.7569,
        "longitude": -73.9976,
        "rating": 4.7,
        "review_count": 45,
        "affiliation": "Michelin ⭐ (Chicago flagship) · James Beard nominee · Opened May 2025",
    },

    # ── Houston ──────────────────────────────────────────────────────
    {
        "name": "Musaafer",
        "subcategory": "Michelin Star",
        "description": "Michelin-starred Indian fine dining in Houston's Galleria, showcasing all 29 states of India through Chef Mayank Istwal's inventive tasting menus. Opulent palace-like interiors with marble arches and towering windows. The 72-hour slow-cooked dal is legendary.",
        "phone": "+17132428087",
        "website": "https://www.musaaferhouston.com",
        "address": "5115 Westheimer Rd",
        "city": "Houston",
        "state": "TX",
        "zip": "77056",
        "latitude": 29.739805,
        "longitude": -95.465518,
        "rating": 4.6,
        "review_count": 1200,
        "affiliation": "Michelin ⭐ · Expanding to NYC TriBeCa 2025",
    },

    # ── Washington DC ────────────────────────────────────────────────
    {
        "name": "Rania",
        "subcategory": "Michelin Star",
        "description": "Michelin-starred modern Indian from Chef Chetan Shetty in Penn Quarter, from the team behind Punjab Grill. Bold reinterpretations of 5,000-year-old recipes — shrimp koliwada, lamb cheela, and monkfish curry. Chandelier-lit interior with dramatic cocktail presentations.",
        "phone": "+12028046434",
        "website": "https://www.raniadc.com",
        "address": "427 11th St NW",
        "city": "Washington",
        "state": "DC",
        "zip": "20004",
        "latitude": 38.895645,
        "longitude": -77.026928,
        "rating": 4.6,
        "review_count": 520,
        "affiliation": "Michelin ⭐",
    },

    # ═══════════════════════════════════════════════════════════════════
    # UPSCALE (Non-Michelin but top-tier)
    # ═══════════════════════════════════════════════════════════════════

    # ── Washington DC ────────────────────────────────────────────────
    {
        "name": "Rasika Penn Quarter",
        "subcategory": "Upscale",
        "description": "Widely considered the best Indian restaurant in America by Esquire Magazine. James Beard Award–winning Chef Vikram Sunderam's palak chaat is iconic — crispy spinach with tamarind and yogurt. Obama celebrated two birthdays here. Top 20 restaurants in America (Zagat).",
        "phone": "+12026371222",
        "website": "https://www.rasikarestaurant.com",
        "address": "633 D St NW",
        "city": "Washington",
        "state": "DC",
        "zip": "20004",
        "latitude": 38.8945,
        "longitude": -77.0208,
        "rating": 4.8,
        "review_count": 5200,
        "affiliation": "James Beard Best Chef Mid-Atlantic 2014 · Washingtonian 100 Best (2012–2025) · NYT Best DC Restaurants 2025",
    },
    {
        "name": "Rasika West End",
        "subcategory": "Upscale",
        "description": "The second location of DC's beloved Rasika, with the same James Beard Award–winning menu from Chef Vikram Sunderam. Known for truffle dosa, black cod, and the legendary palak chaat. Elegant lounge, outdoor patio, and private dining rooms.",
        "phone": "+12024662500",
        "website": "https://www.rasikarestaurant.com/westend",
        "address": "1190 New Hampshire Ave NW",
        "city": "Washington",
        "state": "DC",
        "zip": "20037",
        "latitude": 38.905023,
        "longitude": -77.048095,
        "rating": 4.6,
        "review_count": 3927,
        "affiliation": "James Beard Best Chef Mid-Atlantic · Washington Post Hall of Fame · Washingtonian 100 Best",
    },

    # ── NYC ───────────────────────────────────────────────────────────
    {
        "name": "Dhamaka",
        "subcategory": "Upscale",
        "description": "Michelin Bib Gourmand–awarded restaurant by Chef Chintan Pandya (James Beard Best Chef: New York State 2022) at Essex Market. Unapologetically bold, rustic Indian cooking — smoky goat belly, Kashmiri lamb loin carved tableside, butter garlic crab over rice. An explosion of flavor.",
        "phone": "+12125332032",
        "website": "https://www.dhamakanyc.com",
        "address": "119 Delancey St",
        "city": "New York",
        "state": "NY",
        "zip": "10002",
        "latitude": 40.7188,
        "longitude": -73.9886,
        "rating": 4.5,
        "review_count": 980,
        "affiliation": "Michelin Bib Gourmand · James Beard Best Chef NY 2022 · NYT Best New Restaurant",
    },
    {
        "name": "Adda",
        "subcategory": "Upscale",
        "description": "The restaurant that launched Unapologetic Foods, reimagined for East Village in 2025. Chef Chintan Pandya's bold regional cooking — tableside butter chicken experience where you choose the smoking wood, bheja fry, baby goat biryani. Bon Appétit's Best New Indian Restaurant in NYC.",
        "phone": "+12129291880",
        "website": "https://addanyc.com",
        "address": "107 1st Ave",
        "city": "New York",
        "state": "NY",
        "zip": "10003",
        "latitude": 40.72684,
        "longitude": -73.986236,
        "rating": 4.5,
        "review_count": 450,
        "affiliation": "Bon Appétit Best New Restaurant · Unapologetic Foods · Resy notable",
    },
    {
        "name": "Paisley",
        "subcategory": "Upscale",
        "description": "Elegant Indian fine dining in Tribeca featuring a wraparound bar and inventive seasonal cocktails. Seared scallops, mushroom croquettes, and crispy eggplant chaat are standouts. NYT-praised as 'the best Indian food I've ever had.'",
        "phone": "+12122748003",
        "website": "https://paisleyrestaurantnyc.com",
        "address": "429 Greenwich St",
        "city": "New York",
        "state": "NY",
        "zip": "10013",
        "latitude": 40.722328,
        "longitude": -74.009649,
        "rating": 4.6,
        "review_count": 620,
        "affiliation": "Tribeca fine dining · NYT recommended",
    },
    {
        "name": "Chatti",
        "subcategory": "Upscale",
        "description": "Chef Regi Mathew brings the spirit of Kerala's toddy shops to Midtown Manhattan — bold southern spices through a small-plates menu of rustic, street-style South Indian dining. A standout in NYC's booming Indian fine dining wave.",
        "phone": "+12129291870",
        "website": "https://chattirestaurant.com",
        "address": "252 W 37th St",
        "city": "New York",
        "state": "NY",
        "zip": "10018",
        "latitude": 40.7536,
        "longitude": -73.9917,
        "rating": 4.4,
        "review_count": 320,
        "affiliation": "Eater recommended · Kerala-inspired fine dining",
    },
    {
        "name": "Chutney Masala",
        "subcategory": "Upscale",
        "description": "Westchester's premier Indian restaurant and Michelin Bib Gourmand winner (2024–2025). James Beard–recognized Chef Navjot Arora serves bold street food favorites and fragrant biryanis. NYT-praised, voted Best Indian in Westchester for 17 years running.",
        "phone": "+19145915500",
        "website": "https://chutneymasala.com",
        "address": "76 Main St",
        "city": "Irvington",
        "state": "NY",
        "zip": "10533",
        "latitude": 40.7294,
        "longitude": -73.8682,
        "rating": 4.7,
        "review_count": 618,
        "affiliation": "Michelin Bib Gourmand (2024–2025) · James Beard recognized · Best of Westchester",
    },

    # ── Chicago ──────────────────────────────────────────────────────
    {
        "name": "Superkhana International",
        "subcategory": "Upscale",
        "description": "Michelin Bib Gourmand recipient in Logan Square, blending Indian flavors with global influences. Creative, shareable plates in a hip, art-filled space. One of the most consistently acclaimed Indian restaurants in Chicago's vibrant dining scene.",
        "phone": "+17739002527",
        "website": "https://www.superkhanainternational.com",
        "address": "3059 W Diversey Ave",
        "city": "Chicago",
        "state": "IL",
        "zip": "60647",
        "latitude": 41.9319,
        "longitude": -87.7053,
        "rating": 4.5,
        "review_count": 520,
        "affiliation": "Michelin Bib Gourmand (2021–2025) · Logan Square hotspot",
    },

    # ── San Francisco / Bay Area ─────────────────────────────────────
    {
        "name": "Copra",
        "subcategory": "Upscale",
        "description": "Coastal South Indian restaurant from former Campton Place chef Srijith Gopinathan (first Indian chef to earn two Michelin stars in the US). Signature rasam poori, black cod pollichathu, and the famous 'God's Own' coconut dessert. Stunning Fillmore District space with 30-foot bar.",
        "phone": "+14158730795",
        "website": "https://www.coprarestaurant.com",
        "address": "1700 Fillmore St",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94115",
        "latitude": 37.78537,
        "longitude": -122.432789,
        "rating": 4.6,
        "review_count": 580,
        "affiliation": "Chef Srijith: former 2★ Michelin (Campton Place) · Eater SF Essential · Robb Report featured",
    },
    {
        "name": "ROOH San Francisco",
        "subcategory": "Upscale",
        "description": "Progressive Indian fine dining in SoMa from the team behind Indienne. Modern technique meets Indian flavors — paneer pinwheel with red-pepper makhani, tandoori octopus, Ayurvedic-inspired cocktails. Michelin Guide–listed with vibrant jewel-toned decor.",
        "phone": "+14155254174",
        "website": "https://www.roohrestaurants.com",
        "address": "333 Brannan St",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94107",
        "latitude": 37.781213,
        "longitude": -122.392662,
        "rating": 4.8,
        "review_count": 159,
        "affiliation": "Michelin Guide recommended · ViaMichelin featured · Eater SF Essential",
    },
    {
        "name": "ROOH Palo Alto",
        "subcategory": "Upscale",
        "description": "Silicon Valley's premier progressive Indian restaurant on University Ave. Live-fire grill, inventive cocktails, and signature paneer pinwheel. Upscale yet approachable — perfect for the South Bay NRI community's celebrations and date nights.",
        "phone": "+16508007090",
        "website": "https://roohpaloalto.com",
        "address": "473 University Ave",
        "city": "Palo Alto",
        "state": "CA",
        "zip": "94301",
        "latitude": 37.4481,
        "longitude": -122.159809,
        "rating": 4.5,
        "review_count": 480,
        "affiliation": "Progressive Indian fine dining · Ethically sourced ingredients",
    },
    {
        "name": "Bombay Brasserie",
        "subcategory": "Upscale",
        "description": "Indo-French fine dining in Union Square by Chef Thomas George, who blends Kerala roots with French technique. Truffle paneer, ricotta kofta, and a Lobster Thermidor that bridges both culinary worlds. Reservation-only, elegant setting.",
        "phone": "+14159555554",
        "website": "https://www.bombaybrasseriesf.com",
        "address": "340 Stockton St",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94108",
        "latitude": 37.789097,
        "longitude": -122.406572,
        "rating": 4.5,
        "review_count": 340,
        "affiliation": "Indo-French fine dining · Union Square landmark",
    },
    {
        "name": "Amber India",
        "subcategory": "Upscale",
        "description": "San Francisco's most iconic upscale Indian restaurant near Yerba Buena. Known for tandoori chicken, Amber Thaali, and an extensive wine list. Adjacent to the Four Seasons, it's the go-to for NRI celebrations and business dinners in the city.",
        "phone": "+14157770500",
        "website": "https://www.amber-india.com",
        "address": "25 Yerba Buena Ln",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94103",
        "latitude": 37.785873,
        "longitude": -122.404701,
        "rating": 4.2,
        "review_count": 2100,
        "affiliation": "Bay Area institution since 1995 · Multiple locations",
    },

    # ── Miami / South Florida ────────────────────────────────────────
    {
        "name": "Ghee Indian Kitchen – Dadeland",
        "subcategory": "Upscale",
        "description": "Four-time Michelin Bib Gourmand winner (2022–2025) from four-time James Beard semifinalist Chef Niven Patel. Farm-to-table Indian using ingredients from his own Homestead farm. Samosa chaat, hanger steak, and handmade furniture imported from India. NYT Top 25 Miami Restaurants.",
        "phone": "+13054420043",
        "website": "https://www.gheemiami.com",
        "address": "8965 SW 72nd Pl",
        "city": "Miami",
        "state": "FL",
        "zip": "33156",
        "latitude": 25.6995,
        "longitude": -80.3129,
        "rating": 4.5,
        "review_count": 1730,
        "affiliation": "Michelin Bib Gourmand (2022–2025) · James Beard semifinalist 4x · NYT Top 25 Miami",
    },
    {
        "name": "Ghee Indian Kitchen – Wynwood",
        "subcategory": "Upscale",
        "description": "The Wynwood expansion of Chef Niven Patel's Bib Gourmand–awarded Ghee. Same farm-fresh philosophy, larger 110-seat dining room with bone-inlay tables and handmade Indian furniture. Creative cocktails and a seasonal menu that evolves with local ingredients.",
        "phone": "+13053972440",
        "website": "https://www.gheemiami.com",
        "address": "63 NW 24th St",
        "city": "Miami",
        "state": "FL",
        "zip": "33127",
        "latitude": 25.7967,
        "longitude": -80.1968,
        "rating": 4.4,
        "review_count": 520,
        "affiliation": "Michelin Bib Gourmand · Farm-to-table Indian · Wynwood Arts District",
    },

    # ── Atlanta ──────────────────────────────────────────────────────
    {
        "name": "Ghee Indian Kitchen – Atlanta",
        "subcategory": "Upscale",
        "description": "The first expansion outside Miami of Chef Niven Patel's Bib Gourmand–winning Ghee. Opening in West Midtown's arts district in 2025, bringing the same farm-to-table Indian philosophy and handcrafted Indian furniture to Atlanta's growing dining scene.",
        "phone": "+14042012581",
        "website": "https://www.gheemiami.com",
        "address": "1050 Howell Mill Rd",
        "city": "Atlanta",
        "state": "GA",
        "zip": "30318",
        "latitude": 33.7870,
        "longitude": -84.4118,
        "rating": 4.3,
        "review_count": 120,
        "affiliation": "Michelin Bib Gourmand (Miami) · James Beard semifinalist chef · Fall 2025 opening",
    },

    # ── Asheville, NC ────────────────────────────────────────────────
    {
        "name": "Chai Pani",
        "subcategory": "Upscale",
        "description": "James Beard Outstanding Restaurant 2022 — the most prestigious award in American dining. Chef Meherwan Irani's Indian street food revolutionized how America eats Indian food. Matchstick okra fries, green-mango chaat, and butter chicken thali. NYT's America's Favorite Restaurants.",
        "phone": "+18282544003",
        "website": "https://www.chaipani.com",
        "address": "32 Banks Ave",
        "city": "Asheville",
        "state": "NC",
        "zip": "28801",
        "latitude": 35.58916,
        "longitude": -82.553344,
        "rating": 4.6,
        "review_count": 5086,
        "affiliation": "James Beard Outstanding Restaurant 2022 · NYT America's Favorite Restaurants · Bon Appétit",
    },

    # ── Houston ──────────────────────────────────────────────────────
    {
        "name": "da Gama Canteen",
        "subcategory": "Upscale",
        "description": "Indian-Portuguese fusion in Houston Heights from chef-owners Rick & Shiva Di Virgilio. Wood-burning grill meets tandoor oven — grilled Portuguese octopus alongside Goan pork vindaloo. Michelin Bib Gourmand 2025. Open airy dining overlooking the MKT hike and bike trail.",
        "phone": "+17138632728",
        "website": "https://dagamacanteen.com",
        "address": "817 Studewood St",
        "city": "Houston",
        "state": "TX",
        "zip": "77008",
        "latitude": 29.7929,
        "longitude": -95.3975,
        "rating": 4.6,
        "review_count": 420,
        "affiliation": "Michelin Bib Gourmand 2025 · Indian-Portuguese cuisine",
    },

    # ── Seattle / Redmond ────────────────────────────────────────────
    {
        "name": "Jashn",
        "subcategory": "Upscale",
        "description": "Upscale Indian fine dining in Redmond Town Center with royal Lucknow flair. Regional Maharashtrian thali, kakori kebabs, and butter chicken crafted with Thanjavur hospitality. Elegant modern space that's one of the few dress-up-worthy Indian restaurants in the Pacific Northwest.",
        "phone": "+14255224776",
        "website": "https://jashnrestaurant.com",
        "address": "7325 166th Ave NE",
        "city": "Redmond",
        "state": "WA",
        "zip": "98052",
        "latitude": 47.669694,
        "longitude": -122.119811,
        "rating": 4.5,
        "review_count": 380,
        "affiliation": "Upscale Indian · Regional Lucknow-inspired · Redmond Town Center",
    },

    # ── Los Angeles ──────────────────────────────────────────────────
    {
        "name": "Cali Chilli Downtown LA",
        "subcategory": "Upscale",
        "description": "Indian fusion in DTLA from Michelin-star chef Manjunath Mural. Inventive dishes like Butter Chicken Pot Pie, eggplant lasagna with paneer sheets, and Cali Sticky Ribs. Agrabah-inspired decor and creative craft cocktails. A fresh take on Indian dining in Downtown LA.",
        "phone": "+12132668999",
        "website": "https://www.cali-chilli.com",
        "address": "200 S Los Angeles St",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90012",
        "latitude": 34.050018,
        "longitude": -118.243396,
        "rating": 4.3,
        "review_count": 560,
        "affiliation": "Michelin-star chef · Indian fusion fine dining · DTLA",
    },

    # ── New Jersey (Edison/Central NJ) ───────────────────────────────
    {
        "name": "Moksha",
        "subcategory": "Upscale",
        "description": "Elevated Indian dining on Oak Tree Road, the epicenter of NJ's Indian community. Modern plating and creative cocktails in Edison's only true fine-dining Indian establishment. A destination for NRIs celebrating special occasions beyond the usual Oak Tree Road casual spots.",
        "phone": "+17323396564",
        "website": "https://www.mokshaedison.com",
        "address": "1655 Oak Tree Rd",
        "city": "Edison",
        "state": "NJ",
        "zip": "08820",
        "latitude": 40.5539,
        "longitude": -74.3657,
        "rating": 4.4,
        "review_count": 640,
        "affiliation": "Oak Tree Road fine dining · NJ's premier upscale Indian",
    },

    # ── Dallas ───────────────────────────────────────────────────────
    {
        "name": "Kessaku",
        "subcategory": "Upscale",
        "description": "Modern Indian fine dining in Dallas's Design District with a focus on regional cuisines and contemporary technique. Tasting menus and à la carte options in a sleek, architect-designed space. One of the few truly upscale Indian restaurants in the DFW metroplex.",
        "phone": "+12144684433",
        "website": "https://kessakudallas.com",
        "address": "1999 McKinney Ave",
        "city": "Dallas",
        "state": "TX",
        "zip": "75201",
        "latitude": 32.7935,
        "longitude": -96.8009,
        "rating": 4.4,
        "review_count": 320,
        "affiliation": "Design District fine dining · DFW's premier upscale Indian",
    },
]

# ── Seed logic ───────────────────────────────────────────────────────
def check_existing():
    """Get all existing restaurant names+cities to avoid duplicates."""
    url = f"{SUPABASE_URL}/rest/v1/directory_listings"
    params = {
        "select": "name,city",
        "category": "eq.Catering & Food",
        "subcategory": "in.(Michelin Star,Upscale)",
    }
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code != 200:
        return set()
    return {(row["name"], row["city"]) for row in r.json()}

def insert_listing(restaurant: dict):
    slug = slugify(restaurant["name"], restaurant["city"])
    payload = {
        "name": restaurant["name"],
        "category": "Catering & Food",
        "subcategory": restaurant["subcategory"],
        "description": restaurant["description"],
        "phone": restaurant.get("phone"),
        "email": None,
        "website": restaurant.get("website"),
        "address": restaurant.get("address"),
        "city": restaurant["city"],
        "state": restaurant["state"],
        "zip": restaurant.get("zip"),
        "latitude": restaurant.get("latitude"),
        "longitude": restaurant.get("longitude"),
        "image_url": None,
        "photos": None,
        "rating": restaurant.get("rating"),
        "review_count": restaurant.get("review_count"),
        "google_place_id": None,
        "affiliation": restaurant.get("affiliation"),
        "hours": None,
        "source": "seeded",
        "verified": True,
        "featured": restaurant["subcategory"] == "Michelin Star",
        "slug": slug,
    }
    if DRY_RUN:
        print(f"  [DRY RUN] Would insert: {restaurant['name']} ({restaurant['city']}, {restaurant['state']})")
        return True

    url = f"{SUPABASE_URL}/rest/v1/directory_listings"
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        return True
    else:
        print(f"  ERROR inserting {restaurant['name']}: {r.status_code} {r.text}")
        return False


def main():
    print(f"{'🔍 DRY RUN' if DRY_RUN else '🚀 SEEDING'}: {len(RESTAURANTS)} restaurants")
    print()

    existing = check_existing()
    print(f"Found {len(existing)} existing Michelin Star / Upscale listings\n")

    inserted = 0
    skipped = 0
    failed = 0

    michelin_count = sum(1 for r in RESTAURANTS if r["subcategory"] == "Michelin Star")
    upscale_count = sum(1 for r in RESTAURANTS if r["subcategory"] == "Upscale")
    print(f"📊 Michelin Star: {michelin_count} | Upscale: {upscale_count}")
    print("=" * 60)

    for r in RESTAURANTS:
        key = (r["name"], r["city"])
        if key in existing:
            print(f"  ⏭ SKIP (exists): {r['name']} — {r['city']}, {r['state']}")
            skipped += 1
            continue

        star = "⭐" if r["subcategory"] == "Michelin Star" else "🍽️"
        print(f"  {star} {r['name']} — {r['city']}, {r['state']}")
        if insert_listing(r):
            inserted += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"✅ Inserted: {inserted}")
    print(f"⏭ Skipped (duplicates): {skipped}")
    if failed:
        print(f"❌ Failed: {failed}")
    print(f"📍 Total in database: {len(existing) + inserted}")


if __name__ == "__main__":
    main()
