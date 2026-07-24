#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

guwahati_body = """Air India will begin its first-ever direct international flights from Guwahati, connecting Assam's largest city to Dubai and Abu Dhabi from August 4. For a region that has spent decades funneling every overseas journey through Delhi or Kolkata, it is the kind of quiet structural change that reshapes how a whole community travels.

## What is launching

The carrier confirmed nonstop services from Lokpriya Gopinath Bordoloi International Airport at Borjhar to both Dubai and Abu Dhabi, the two busiest gateways in the Gulf. Fares and full schedules have not yet been released, but the August start date places the launch squarely inside the strongest stretch of India–Gulf demand, when labour traffic, family visits and tourism all peak at once.

The move is part of a deliberate decentralisation push by Indian carriers. Rather than routing every long-haul and medium-haul passenger through the saturated metros, airlines are seeding international routes from second-tier cities. Guwahati, the commercial and administrative heart of the Northeast, is the natural anchor for that strategy in the eastern half of the country.

## Why the Northeast needed this

For travellers from Assam and the surrounding states, an overseas trip has long meant an awkward two-step: a domestic hop to Delhi or Kolkata, an overnight wait, and only then the actual international leg. That added cost, time and the very real risk of a missed connection. A direct Gulf service collapses that into a single boarding pass.

The Gulf matters here more than the route map suggests. The UAE is home to a large and growing population of workers and professionals from the Northeast, and Abu Dhabi and Dubai also function as one-stop hubs onward to Europe, North America and Southeast Asia. A Guwahati flyer can now reach a global network without ever transiting a domestic Indian airport.

## The diaspora angle

For Indian Americans with roots in Assam, Meghalaya, Nagaland, Manipur and the rest of the Northeast, the change is indirect but real. The hardest part of bringing elderly parents to the United States, or sending them home, has rarely been the transatlantic leg — it has been the domestic shuffle inside India, with luggage re-checks, terminal changes and tight layovers that punish older travellers.

A nonstop from Guwahati to Abu Dhabi means a relative in Jorhat or Shillong can now reach a Gulf hub in one flight, then connect to a single onward service to the US. Air India and its partners already operate Abu Dhabi and Dubai connections that feed North American gateways, so the door is opening to genuinely one-stop, one-airline itineraries from the Northeast to American cities — a first for a region that has always been treated as the end of the line.

## What is next

Industry watchers expect the Gulf links to be the opening move rather than the finish. Once immigration, customs and cargo handling are proven at Borjhar on these routes, additional international destinations become far easier to justify. Guwahati is being positioned as the Northeast's international gateway in the same way Hyderabad and Bengaluru emerged as southern hubs a generation ago.

For now, the practical advice is simple. NRIs planning to fly parents or relatives out of the Northeast after August should price the new Guwahati–Gulf options against the old metro-transit routes before booking. The fare may or may not undercut the incumbents at launch, but the time saved and the connections avoided will, for many families, be worth more than the difference on the ticket.

**Sources:** Curly Tales; The Hindu BusinessLine; Travel And Tour World."""

schengen_body = """Indian travellers heading to Europe in 2026 are navigating two changes at once: a "cascade" visa regime that hands frequent flyers multi-year Schengen visas, and a new electronic border system that tracks every entry and exit to the minute. For NRIs who criss-cross between the US, India and Europe, understanding how the two interact is now essential.

## The cascade, explained

Under rules the European Commission adopted in 2024 and that are now firmly in force, Indian nationals who have obtained and lawfully used two Schengen visas within the previous three years qualify for a two-year, multiple-entry visa. Use that one properly, and the next step up is a five-year multiple-entry visa — provided the passport has enough validity left to cover it.

During the life of these visas, holders effectively travel like visa-free nationals: into and out of all 29 Schengen countries, for stays of up to 90 days in any 180-day window, for tourism or business, with no need to specify a single purpose. The one hard limit is work — the visa never grants the right to earn locally.

The practical upshot is that an established Indian traveller no longer has to grind through a fresh application for every European trip. France, Italy and the Netherlands consulates are historically the most generous with long-validity multiple-entry visas for qualifying applicants, which is worth knowing when you choose where to lodge your file.

## The catch: EES is now live

The looser visa regime arrives alongside a tighter border. The EU's Entry/Exit System (EES) went live in April 2026, replacing manual passport stamps with biometric, automated logging of every non-EU arrival and departure. The system counts your 90-in-180 days for you — and an overstay now registers instantly, with no chance that a sympathetic officer simply forgets to stamp.

This is the part that trips people up. A five-year visa does not mean a five-year stay. The 90/180 rule applies throughout, and EES enforces it automatically. The era of casually losing track of how many days you have spent in the Schengen zone is over.

## Why this matters for NRIs

For Indian Americans, the wrinkle is which passport you travel on. A US citizen of Indian origin enters Schengen visa-free (and, separately, will soon need the ETIAS travel authorisation). But a green-card holder or H-1B worker still travelling on an Indian passport must use the Schengen visa system — and for them, the cascade is a genuine prize.

Consider the typical pattern: a Bay Area engineer on an H-1B who visits family in India every year and tacks on a European leg, or attends conferences in Berlin and Amsterdam. Two correctly used short-stay visas, and they graduate to a two-year multiple-entry visa, then a five-year one — covering years of spontaneous European trips without a single new application. The travel history that NRIs naturally accumulate is exactly what the cascade rewards.

## Practical steps

Keep clean records of every Schengen entry and exit; under EES the data is captured for you, but your own log helps you plan against the 90/180 ceiling. Hold onto old visas and boarding passes as proof of the "lawful use" the cascade requires. Buy multi-trip travel insurance with at least €30,000 of coverage, valid across the zone — it is mandatory and strengthens an application for a longer-validity visa. And if you are on an Indian passport with a strong recent travel history, ask explicitly for the longest multiple-entry validity you qualify for rather than accepting a single-trip sticker by default.

For a community that lives across three continents, the combination is a net win: easier repeat access to Europe, balanced by a border system that demands you actually count your days.

**Sources:** EEAS (European External Action Service); Fragomen; Visard Visa Guides."""

monsoon_body = """While much of the diaspora plans its India trip around Diwali or the winter wedding season, a growing number of travellers are discovering the case for the opposite end of the calendar. India in the monsoon — roughly July through September — is greener, cheaper and far less crowded, and 2026's booking data shows desis at home are already moving.

## The numbers behind the trend

Domestic flight fares drop 30 to 50 percent against peak-winter pricing on popular routes during the rains, and hotel rates across the country fall sharply from July into early September. Travellers have noticed. Hill destinations are seeing booking surges — Shimla up 76 percent, with overflow into lesser-known spots like Dobhi, Rajgundha and Kareri — while platforms report searches for Leh up 143 percent and Kasol up 126 percent year on year as Indians chase cooler, trek-friendly escapes.

This year's monsoon stalled for two weeks over western India before reviving and pushing into the central belt, so timing is a little less predictable than usual. But the broad pattern holds: Kerala from late May, Goa and coastal Karnataka in early June, Mumbai and Maharashtra by mid-June, and full national coverage by mid-July.

## Where to go

**Kerala** is the original monsoon destination, and for good reason. The state's own tourism campaign promotes June through August for Ayurvedic treatment, when the humid climate makes the body more receptive to therapies like Panchakarma. Kochi and Alleppey open onto houseboat cruises through rain-swollen backwaters, and Munnar's tea plantations turn an almost electric green.

**The Western Ghats** deliver the weekend-getaway version. Lonavala and Mahabaleshwar offer waterfalls and valley views within easy reach of Mumbai and Pune; Malshej Ghat brings flamingos and cloud-level drives; and Matheran, India's only car-free hill station, is reached by toy train or a short trek.

**Coorg and the Tamil hills** — Madikeri's coffee plantations, plus Ooty and Kodaikanal — round out the south, while the more adventurous head north to Meghalaya's Cherrapunji for living root bridges and waterfalls at full roar.

## The diaspora angle

For Indian American families, the monsoon trip solves several problems at once. School summer break in the US runs from June into August, lining up almost perfectly with the start of the Indian rains — so children can travel without missing class, exactly when winter trips force a holiday-season scramble. The lower airfares and hotel rates matter for a family of four flying from the US, where the India leg is already the single biggest line in the budget.

There is a cultural payoff, too. Monsoon India is the India of memory for many first-generation parents — the smell of the first rain, chai on a wet verandah, fields gone impossibly green. It is a version of the homeland that children raised on dry-season holiday visits rarely see, and arguably the more authentic one.

## Practical notes

Build slack into the itinerary. Rain can disrupt road travel and the occasional regional flight, so avoid tight same-day connections and keep a buffer day before any onward international leg. Coastal and hill roads can be slow or briefly closed during heavy spells; check local advisories, especially in landslide-prone stretches of the Ghats and northern Kerala. Pack quick-dry clothing, sturdy footwear and effective mosquito protection. And book early on the hill routes — the secret is clearly out, and the best-value stays in Munnar, Coorg and the Maharashtra Ghats are filling faster than the discounted fares suggest.

Go in with the right expectations — afternoon downpours, some beach-shack closures in Goa — and the monsoon rewards you with the country at its most beautiful and least expensive.

**Sources:** Wego Travel; Curly Tales; Reuters."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's First International Flights From Guwahati Open the Northeast's Door to the Gulf — and the World Beyond",
        "subheadline": "Direct Dubai and Abu Dhabi services from August 4 end the domestic-transit ordeal for travellers from Assam and the wider Northeast.",
        "slug": make_slug("air-india-guwahati-dubai-abu-dhabi-first-international-northeast-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For Indian Americans with roots in Assam and the Northeast, a one-flight hop to a Gulf hub finally makes one-stop, one-airline trips between the homeland and the US realistic for elderly parents.",
        "tags": ["travel", "airlines", "air india", "guwahati", "northeast"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Curly Tales", "url": "https://curlytales.com/air-india-to-launch-first-ever-direct-flights-from-guwahati-to-abu-dhabi-and-dubai/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-make-foreign-travel-more-accessible-to-bharat-ai-ceo/article.ece"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/guwahati-emerges-as-northeast-indias-new-aviation-gateway/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Lokapriya_Gopinath_Bardoloi_International_Airport%2C_Terminal_-_2.jpg/1280px-Lokapriya_Gopinath_Bardoloi_International_Airport%2C_Terminal_-_2.jpg",
        "image_caption": "Terminal of Lokpriya Gopinath Bordoloi International Airport in Guwahati, Assam",
        "image_attribution": "Wikimedia Commons",
        "body": guwahati_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe Just Got Easier and Stricter for Indians at Once — How the Schengen Cascade and the New Border System Work Together",
        "subheadline": "Frequent travellers can now climb to five-year multiple-entry visas, but a live electronic border counts every day you spend in the zone.",
        "slug": make_slug("schengen-cascade-visa-ees-border-indians-multiple-entry-nri-2026"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Green-card and H-1B holders travelling on Indian passports are exactly the frequent flyers the Schengen cascade rewards — turning years of US-India-Europe trips into multi-year visa-free-style access.",
        "tags": ["travel", "visa", "schengen", "europe", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "EEAS (European External Action Service)", "url": "https://www.eeas.europa.eu/delegations/india/european-union-adopts-more-favourable-schengen-visa-rules-indians_en"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/european-union-schengen-visa-rules-relaxed.html"},
            {"name": "Visard Visa Guides", "url": "https://visard.io/blog/multiple-entry-schengen-visa-2026-cascade-rules/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Paris_Night.jpg/1280px-Paris_Night.jpg",
        "image_caption": "Night view of Paris with the Eiffel Tower, a top Schengen destination for Indian travellers",
        "image_attribution": "Wikimedia Commons",
        "body": schengen_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora's Off-Season Secret: Why an India Trip in the Monsoon Beats the Winter Crush",
        "subheadline": "Fares fall 30 to 50 percent, the hills turn electric green, and US school break lines up almost perfectly with the rains.",
        "slug": make_slug("india-monsoon-travel-2026-cheaper-greener-diaspora-summer-break"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "US summer break overlaps the Indian monsoon almost exactly, so NRI families get cheaper flights, emptier hill stations and the rain-soaked India of their parents' memory without pulling kids out of school.",
        "tags": ["travel", "india", "monsoon", "tourism", "kerala"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-india/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/monsoon-travel-shimla-sees-76-rise-in-bookings/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-monsoon-revives-after-two-week-stall-heads-into-central-belt-2026/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Munnar_Tea_Plantations-WUS07343-Pano.jpg/1280px-Munnar_Tea_Plantations-WUS07343-Pano.jpg",
        "image_caption": "Tea plantations turning green in the hills of Munnar, Kerala, during the monsoon",
        "image_attribution": "Wikimedia Commons",
        "body": monsoon_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
