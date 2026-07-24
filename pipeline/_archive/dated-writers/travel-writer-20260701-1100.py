#!/usr/bin/env python3
"""Travel writer — 2026-07-01 11:00 run. Two articles:
1. Digital nomad visas for Indian professionals
2. Mexico & Caribbean visa-free travel with US visa
"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

# ─── ARTICLE 1: Digital Nomad Visas ──────────────────────────────────────
article1_body = """Your US tech salary. A flat in Lisbon overlooking the Tagus. A legal visa that lets you stay for a year. This is not a gap-year fantasy — it is a bureaucratic product that over seventy countries now sell, and Indian professionals are buying it in record numbers.

Nearly a million Indians were classified as digital nomads worldwide in 2024, according to State of Digital Nomads data. The number has only grown since. What changed is not the desire to live abroad — that has always been there — but the paperwork. Governments from Tallinn to Dubai now issue dedicated residence permits for remote workers, distinct from tourist visas and work permits, with income thresholds that a mid-career software engineer in the Bay Area clears comfortably.

## The top five destinations, ranked for NRIs

**Portugal** remains the frontrunner. Its D8 digital nomad visa requires a minimum monthly income of €3,480 (roughly $3,800) and leads to a two-year residence permit, renewable for three more. After five years, permanent residency — and eventually citizenship — is on the table. Lisbon's tech ecosystem, mild climate, and direct Air India flights from Mumbai make it the path of least resistance for NRIs exploring Europe.

**Spain** is closing the gap. Its visa, refined again in early 2026, requires €2,849 per month and grants up to five years of residency. The real draw is the Beckham Law: qualifying remote workers pay a flat 24 per cent income tax rate instead of Spain's progressive scale, which tops out at 47 per cent. Barcelona and Madrid have thriving co-working scenes and growing Indian communities.

**The UAE** appeals to a different calculus. Dubai's remote work visa processes in days, not months, charges zero personal income tax, and puts you a four-hour flight from Mumbai or Delhi. For NRIs who visit family in India frequently, the proximity alone justifies it. The minimum income requirement is $3,500 per month.

**Estonia**, the birthplace of Skype, targets tech workers specifically. Its one-year visa requires €4,500 per month but grants full Schengen access — meaning you can work from Tallinn on Monday and take a train to Helsinki or a flight to Berlin on Friday without a second visa. Living costs run about ₹1.5–2 lakh per month, far below Western European capitals.

**Slovenia** is the newest entrant, having launched its programme in late 2025. It asks for roughly €27,000 per year (about $29,000), includes family members, and comes with Schengen mobility. Ljubljana rents average €800 per month for a one-bedroom — roughly half of Lisbon — and the country's proximity to the Alps and the Adriatic makes it an increasingly popular choice among early adopters.

## What NRIs need to watch

**Tax residency is the trap.** Most digital nomad visas do not create local tax obligations for stays under 183 days — but your US tax obligations remain. If you hold a green card or are a US tax resident, you owe the IRS on worldwide income regardless of where you file from. Consult a cross-border tax advisor before relocating; the Beckham Law or Portugal's tax regime may help, but double-taxation treaties vary by country.

**Your employer must consent.** A digital nomad visa does not require employer sponsorship, but most US companies have policies about employees working from abroad — payroll, data security, and permanent establishment risk are real concerns. Get sign-off in writing before you book the flight.

**Health insurance is non-negotiable.** Every programme requires comprehensive coverage valid in the host country. Your US employer's plan likely will not qualify. Budget $150–300 per month for a compliant international policy.

**Timing matters.** Spain and Portugal process applications in four to eight weeks. Estonia moves faster at 15–30 days. The UAE can turn around approvals within a week. If you are planning a winter relocation — say, escaping the Bay Area's December fog for Lisbon's mild 15°C — start the paperwork in September.

## The bigger picture

Digital nomad visas are not immigration in the traditional sense. They are a lifestyle product designed by governments competing for high-earning, tax-light residents who spend locally. For NRIs caught in the US green card backlog — the India EB-2 queue now stretches decades — they offer something the H-1B never did: the freedom to live somewhere legally without tying your residency to a single employer.

That is not a small thing. For the generation of Indian tech workers who built Silicon Valley's products while waiting years for a piece of plastic from USCIS, the option to spend a year in Lisbon, Barcelona, or Dubai on their own terms is less about wanderlust and more about agency."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your US Salary, a European Address — the NRI Guide to Digital Nomad Visas in 2026",
    "subheadline": "Portugal, Spain, the UAE, Estonia and Slovenia are competing for Indian tech workers who can work from anywhere. Here is what each visa costs, how long it lasts, and the tax traps to avoid.",
    "slug": make_slug("digital-nomad-visa-nri-guide-portugal-spain-uae"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "Indian-American tech workers stuck in green card backlogs or simply seeking a year abroad can legally relocate to Europe or the UAE while keeping their US salary — these visas offer agency the H-1B never did.",
    "tags": ["travel", "visa", "digital-nomad", "remote-work", "europe", "uae"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "LinkedIn — Digital Nomad Visas for Indians", "url": "https://www.linkedin.com/pulse/digital-nomad-visas-indians-your-gateway-global-remote-career/"},
        {"name": "Jobbatical — Estonia Digital Nomad Visa 2026 Guide", "url": "https://jobbatical.com/blog/estonia-digital-nomad-visa-for-indians"},
        {"name": "Klevvera — Spain Digital Nomad Visa 2026", "url": "https://klevvera.com/spain-digital-nomad-visa/"},
        {"name": "Oyster HR — Portugal D8 Visa Guide 2026", "url": "https://www.oysterhr.com/library/portugal-digital-nomad-visa"},
        {"name": "Deel — Digital Nomad Visas Complete 2026 List", "url": "https://www.deel.com/blog/digital-nomad-visas/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Lisboa_-_Portugal_%2852597836992%29.jpg/1280px-Lisboa_-_Portugal_%2852597836992%29.jpg",
    "image_caption": "Lisbon's waterfront skyline along the Tagus river — Portugal's D8 visa is the most popular digital nomad route for Indian professionals",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ─── ARTICLE 2: Mexico & Caribbean Visa-Free ─────────────────────────────
article2_body = """Every Indian passport holder in the United States carries a hidden travel perk that most never use: their US visa — tourist, work, or student — doubles as a skeleton key to Mexico and much of the Caribbean. No separate visa application. No consulate appointment. No six-month wait.

Mexico's immigration rules are explicit. Any foreign national holding a valid visa or permanent resident card issued by the United States, Canada, Japan, the United Kingdom, or any Schengen country may enter Mexico visa-free for up to 180 days. That covers every Indian on an H-1B, L-1, F-1, B-1/B-2, or green card. You need only a valid passport and a completed Multiple Immigration Form (FMM), which the airline provides or you fill out at the border.

## What this means for the July 4th weekend — and beyond

The maths is simple. A round-trip flight from Dallas to Cancún costs under $250. Houston to Mexico City runs about $200. Los Angeles to Cabo San Lucas, $300. These are not sales — they are baseline summer fares on routes with heavy competition from Southwest, United, Volaris, and VivaAerobus. For an NRI family of four used to spending $8,000 on Delhi return tickets, a long weekend in the Riviera Maya is pocket change.

Cancún and the surrounding Riviera Maya — Playa del Carmen, Tulum, the cenotes — are the obvious entry point. The Hotel Zone's all-inclusive resorts start at $150 per night and go as high as your credit card allows. But the real value is in Playa del Carmen's rental apartments ($60–80 per night) and Tulum's boutique hotels, where you eat street tacos for $2 and swim in ancient limestone sinkholes for $15.

Mexico City is the underrated play. A world-class food city with museums, architecture, and a cost of living that embarrasses San Francisco. A nice dinner for two in Roma Norte runs $40. The National Museum of Anthropology, Frida Kahlo's Casa Azul, and the Teotihuacan pyramids are all within a day's reach. And for the vegetarian NRIs: Mexico City's plant-based dining scene has exploded, with restaurants like Por Siempre Vegana offering Mexican-Indian fusion that makes the transition painless.

## Beyond Mexico: the Caribbean visa map for Indian passport holders

The US visa's reach extends further south. Several Caribbean nations waive visa requirements for Indians holding valid US visas or green cards:

**No visa needed with valid US visa:** Mexico (180 days), Costa Rica (30 days), Panama (180 days), Colombia (90 days), Chile (90 days), Argentina (90 days with US B-2 visa). The Philippines also grants 30-day visa-free entry to Indians with valid US, Schengen, Australian, Canadian, Japanese, UK, or Singapore visas.

**Visa on arrival:** Turkey (e-visa, roughly $50), Oman (14 days), and Jordan (with valid US/UK/Schengen visa) are also accessible for NRIs looking for a different flavour of beach.

**The automatic revalidation bonus:** If you are on an F-1 or J-1 visa — even an expired one — US immigration rules allow you to travel to Canada, Mexico, or adjacent Caribbean islands (the Bahamas, Barbados, Bermuda, Jamaica, the Dominican Republic, Trinidad and Tobago, and most British, French, and Dutch Caribbean territories) and re-enter the US within 30 days without needing to renew your visa stamp first. This is the "automatic revalidation" provision, and it is one of the most underused benefits in the NRI student playbook.

## Practical notes

**Currency:** The Mexican peso trades at roughly 17–18 per US dollar. ATMs give better rates than airport exchange counters. Most tourist areas accept credit cards, but carry pesos for markets, street food, and smaller shops.

**Safety:** Stick to tourist corridors. Cancún's Hotel Zone, Playa del Carmen, Tulum, San Miguel de Allende, Oaxaca, and Mexico City's central neighbourhoods (Roma, Condesa, Polanco, Coyoacán) are all well-patrolled and heavily touristed. Use registered taxis or Uber. The State Department maintains a travel advisory page updated by state — check it before booking.

**Food for Indian travellers:** Mexican and Indian cuisines share a surprising affinity for chillies, cumin, coriander, and slow-cooked stews. The adjustment is easier than you think. Vegetarians will find beans, rice, cheese, and grilled vegetables at every taquería. Ask for "sin carne" and you will not go hungry.

**Flights from India:** If you are visiting family in the US and want to tack on a Mexico trip, the routing works beautifully. Fly Delhi–Newark on Air India, spend a week in New Jersey, then grab a $180 Spirit fare to Cancún for a long weekend before heading home. The FMM form takes five minutes.

## Why NRIs should stop overlooking Latin America

The Indian American travel playbook has three chapters: India, Europe, and maybe Southeast Asia. Latin America barely registers. But for a community that collectively earns more than any other ethnic group in the United States, a region where the US visa eliminates paperwork, flights cost less than a nice dinner in Manhattan, and the beaches rival Goa without the monsoon — the question is not why go, but why it took this long to notice."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your US Visa Unlocks Mexico and the Caribbean — an NRI Summer Travel Cheat Sheet",
    "subheadline": "Indian passport holders with any valid US visa or green card can enter Mexico visa-free for 180 days. Here are the routes, the costs, and the dozen other countries your American paperwork opens up.",
    "slug": make_slug("mexico-caribbean-visa-free-us-visa-nri-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Most Indian Americans do not realise their H-1B, green card, or student visa eliminates the need for a separate Mexican visa — unlocking cheap beach getaways that rival Goa without the 20-hour flight.",
    "tags": ["travel", "visa-free", "mexico", "caribbean", "summer", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Mexican Consulate — Visa Exemption Rules", "url": "https://consulmex.sre.gob.mx/"},
        {"name": "Wikipedia — Visa policy of Mexico", "url": "https://en.wikipedia.org/wiki/Visa_policy_of_Mexico"},
        {"name": "US State Department — Automatic Revalidation", "url": "https://travel.state.gov/"},
        {"name": "Columbia ISSO — Returning from Canada, Mexico and Caribbean", "url": "https://isso.columbia.edu/content/returning-canada-mexico-and-adjacent-caribbean-islands"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Canc%C3%BAn_-_Playa_Gaviota_Azul_-_08.jpg/1280px-Canc%C3%BAn_-_Playa_Gaviota_Azul_-_08.jpg",
    "image_caption": "Playa Gaviota Azul in Cancún — Mexico grants Indian passport holders with a valid US visa up to 180 days visa-free",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}

# ─── INSERT ──────────────────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
