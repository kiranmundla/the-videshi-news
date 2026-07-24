#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-07 06:00 UTC run. Two articles."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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

# Verify images before inserting
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        print(f"  ⚠ Image check failed: status={r.status_code}, type={ct}, size={cl}")
        return False
    except Exception as e:
        print(f"  ⚠ Image verify error: {e}")
        return False

# ─────────────────────────────────────────────
# ARTICLE 1: Germany Drops Transit Visa
# ─────────────────────────────────────────────

art1_headline = "Germany Just Made Frankfurt and Munich Visa-Free Transit Hubs for Indians — Here's What NRIs Should Do With That"

art1_subheadline = "Effective June 3, Indian passport holders connecting through German airports no longer need a transit visa. For the diaspora routing through Europe to get home, this changes the math on which flights to book."

art1_body = """The Federal Republic of Germany has officially removed the airport transit visa requirement for Indian nationals connecting through German airports. The policy, published in Germany's Federal Law Gazette on June 2, 2026, took effect the following day. Indian travellers flying to a non-Schengen destination — the United States, United Kingdom, Canada, or anywhere outside the EU's border-free zone — can now change planes at Frankfurt or Munich without obtaining a separate Type A transit visa.

The change is not symbolic. Until last week, Indian passport holders who wanted to connect through a German airport en route to, say, New York or Toronto had to apply for and pay for an airport transit visa — a separate document from a Schengen tourist visa, required purely to sit in the transit lounge for a few hours between flights. The requirement affected millions of potential bookings and steered Indian travellers toward hubs in the Gulf, Istanbul, or London instead.

## What actually changed

The German Embassy in New Delhi confirmed that the decision followed discussions during German Chancellor Friedrich Merz's visit to India in January 2026. India's Ministry of External Affairs spokesperson Randhir Jaiswal welcomed the move, noting it was "operationalised" effective June 3.

The rules are specific. Indian passengers may now transit through the international zone of a German airport without a visa, provided they are travelling to a **non-Schengen** country and remain airside — meaning they do not leave the transit area or pass through German immigration. The transit must be completed within 24 hours.

If your layover involves exiting the airport (to stay at an airport hotel, for instance), you still need a Schengen visa. If your connection involves transiting through two Schengen airports — say, Frankfurt and then Amsterdam — you will need a Schengen visa because leaving the transit area in one Schengen state constitutes entry into the zone.

## Why this matters to NRIs

For the 4.4 million Indian-Americans in the United States, Germany has long been an awkward gap in the European hub map. Emirates through Dubai, Qatar Airways through Doha, Turkish Airlines through Istanbul — these were the default options for flying to India, partly because none required a separate transit visa.

Lufthansa Group, which operates over 70 weekly flights between India and Europe, stands to gain the most. The airline group — which includes Lufthansa, SWISS, and Austrian Airlines — is already expanding aggressively into India. SWISS will launch its first-ever nonstop Bengaluru-to-Zurich service this winter. Lufthansa is deploying its new Allegris premium cabins on Boeing 787-9 flights from Delhi and Hyderabad. And the A380 service between Mumbai and Munich is getting additional capacity.

For NRIs, the practical impact is this: Frankfurt and Munich now join the list of hassle-free connecting hubs alongside Dubai, Doha, Abu Dhabi, Istanbul, and Singapore. That opens up competitive fares on Lufthansa Group metal for US-India routes that were previously off-limits to casual consideration.

## The fine print NRIs should know

Before you rebook, a few caveats worth noting:

**Airside only.** You cannot leave the transit zone. If your connecting flight is cancelled and Lufthansa rebooks you through a hotel stay, you may need emergency documentation to leave the airport.

**Non-Schengen destinations only.** This applies when you are flying through Germany to a country outside the Schengen area. If your final destination is Paris, Rome, or Barcelona, the transit visa exemption does not help — those are Schengen countries, and you would need a proper Schengen visa regardless.

**24-hour limit.** Your transit must be completed within 24 hours. Overnight connections are technically possible but plan carefully.

**Other Schengen states still require transit visas.** France, the Netherlands, and most other Schengen countries continue to require Indian nationals to hold an airport transit visa. Germany's decision is unilateral — it has not triggered a bloc-wide change.

India is Lufthansa Group's largest intercontinental market in the Asia-Pacific region. The transit visa removal is not charity; it is commercial strategy. But for the NRI booking a flight home for Diwali or a summer visit, the effect is the same: one fewer form, one fewer fee, one fewer reason to avoid the Frankfurt connection.

*Sources: German Embassy New Delhi, Ministry of External Affairs India, Outlook Traveller, Aviation A2Z, Travel Trade Journal*"""

art1_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/202201_Atrium_and_Transit_Re-Security_Area_at_Frankfurt_Airport_Terminal_1_Concourse_AZ.jpg/1280px-202201_Atrium_and_Transit_Re-Security_Area_at_Frankfurt_Airport_Terminal_1_Concourse_AZ.jpg"

# ─────────────────────────────────────────────
# ARTICLE 2: The Evren Luxury Hotel in Goa
# ─────────────────────────────────────────────

art2_headline = "Sanjay Dutt Just Opened a Luxury Hotel in Vagator — And Goa's NRI Vacation Playbook Is Changing Fast"

art2_subheadline = "The Evren, a boutique property backed by the actor-entrepreneur and inducted into the Small Luxury Hotels of the World collection, signals that North Goa's hospitality scene is growing up."

art2_body = """For decades, Goa has been the default vacation for NRI families returning to India. The formula was reliable: rent a beach shack, eat fish curry rice at Martin's Corner, maybe squeeze in a trip to Old Goa's churches, and fly back to Newark or San Francisco tanned and overfed. The accommodation options ranged from antiseptic chain hotels on Candolim to charmingly decrepit guesthouses in Anjuna.

That formula is getting an upgrade. Hotel The Evren, a new luxury boutique property in Vagator, North Goa, has opened its doors — and it has already been inducted into the Small Luxury Hotels of the World (SLH) collection before its official launch, a distinction that puts it alongside some of the most curated independent hotels on the planet.

## Who is behind it

The Evren is backed by a group of entrepreneurs including Harkaran Chawla, Angad Singh, Kunal Patel, Suved Lohia, and actor-turned-businessman Sanjay Dutt. The Bollywood connection will generate headlines, but the more interesting detail is the operating philosophy: The Evren is not a hotel that happens to have a restaurant. It is a lifestyle destination where hospitality, dining, nightlife, and workspace converge under one roof.

Lohia, whose portfolio includes One8 Commune (Virat Kohli's restaurant brand), brings a track record in the food-and-nightlife intersection. His vision for The Evren's flagship venue, Nines by The Evren, is a space that operates as an all-day dining destination before transitioning into a nightlife venue with live music programming in the evening.

## The food programme

The culinary strategy is anchored by Chef Prachi Mehta, who has spent 13 years at venues that read like a greatest-hits of global fine dining: The Wolseley in London, Copenhagen's Michelin-starred 108, a pop-up stint at New York's Eleven Madison Park, and Mumbai's The Bombay Canteen. Her menu at Nines blends European technique with Indian flavours — Balchão Charred Broccoli, Kismur Grilled King Prawns with Goan Poee bread, Chettinad Fried Chicken, Sichuan Pepper Soft Shell Crab, and Blue Cheese Cappelletti.

The cocktail list includes the Ampana, Imli Drop, and Cheeky Mosambi — drinks that nod to Indian ingredients without descending into gimmick.

For the caffeine-dependent, The Evren has also launched Suenos de Cafe, a specialty café curated by Geetu Mohnani, who made history as the first woman to win India's National Barista Championship in 2018 and later represented the country at the World Barista Championship in Amsterdam. The café has been designed with remote workers and digital professionals in mind — a detail that speaks directly to the growing cohort of NRIs who work US hours from Goa for weeks at a stretch.

## What this means for the NRI Goa trip

The Evren is not the only signal that Goa's luxury hospitality market is maturing. The state has seen a wave of new boutique hotels, farm-to-table restaurants, and co-working spaces in the past two years, driven in part by the pandemic-era remote-work migration that turned Goa into a satellite office for Mumbai and Bengaluru's tech workforce.

For NRI families, this evolution matters. A generation ago, Goa meant budget beach holidays. Today, it can accommodate the kind of trip where you fly business class from JFK, work from a café with World Barista Championship-grade coffee during the day, dine on Eleven Madison Park-trained cuisine at night, and still be ten minutes from the beach.

The SLH affiliation is particularly significant. The collection's properties are bookable through global travel agents and loyalty programmes, which means The Evren will show up in the same searches as a Four Seasons or an Aman — a visibility boost that Goa's boutique hotel scene has historically lacked.

Rooms at The Evren are suites with personalised guest services. Pricing has not been publicly disclosed, but the SLH positioning and the calibre of the food programme suggest this is firmly in the premium segment — a Goa stay designed for travellers who have outgrown the beach-shack phase but are not yet ready for the Leela Palace circuit.

Vagator, for those who have not been back in a while, has quietly become North Goa's most interesting neighbourhood — close to the Chapora Fort viewpoint, removed from the Baga-Calangute tourist corridor, and home to a growing cluster of design-forward cafés and bars. The Evren's location is a bet on where Goa's centre of gravity is shifting.

*Sources: Restaurant India, Small Luxury Hotels of the World, industry reports*"""

art2_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Vagator_Beach%2C_Goa%2C_India.jpg/1280px-Vagator_Beach%2C_Goa%2C_India.jpg"

# ─────────────────────────────────────────────
# Build article payloads
# ─────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("germany-transit-visa-dropped-indians-nri-frankfurt"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying between the US and India can now connect through Frankfurt and Munich without a transit visa, opening up competitive Lufthansa Group fares on routes previously avoided due to visa hassle.",
        "tags": ["travel", "visa", "germany", "lufthansa", "airports", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/"},
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/"},
            {"name": "German Embassy New Delhi", "url": "https://india.diplo.de/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art1_image,
        "image_caption": "The transit re-security area at Frankfurt Airport Terminal 1",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
        "is_editorial": False,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("evren-sanjay-dutt-luxury-hotel-vagator-goa-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs who vacation in Goa, The Evren represents the maturation of North Goa's hospitality scene — world-class dining, remote-work cafés, and SLH-level curation that matches what the diaspora is used to abroad.",
        "tags": ["travel", "goa", "hotels", "luxury", "bollywood", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Restaurant India", "url": "https://www.restaurantindia.in/"},
            {"name": "Small Luxury Hotels of the World", "url": "https://www.slh.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": art2_image,
        "image_caption": "Vagator Beach in North Goa, home to the newly opened Evren luxury hotel",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body,
        "is_editorial": False,
    },
]

# Verify images
for art in articles:
    print(f"Verifying image for: {art['slug']}")
    if not verify_image(art['image_url']):
        print(f"  ❌ Skipping {art['slug']} — image verification failed")
        continue

# Insert articles
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
