#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's SFO Flight Turned Back Over China — and NRIs on the Bay Area Route Should Be Concerned",
        "subheadline": "Flight AI173 spent eight hours in the air before returning to Delhi after both TCAS channels failed. For the 400,000-plus Indians in the Bay Area, the incident raises hard questions about fleet reliability on one of the diaspora's most critical corridors.",
        "slug": make_slug("air-india-sfo-delhi-tcas-failure-nri-bay-area"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "SFO-DEL is one of the busiest NRI routes in the world, serving the Bay Area's massive Indian tech workforce. With Air India already suspending Delhi-Newark and Mumbai-New York for the summer, fleet reliability incidents like this leave diaspora travelers with fewer trusted options.",
        "tags": ["travel", "airlines", "air india", "san francisco", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-flight-to-san-francisco-returns-midway-due-to-technical-snag/article69624580.ece"},
            {"name": "IANS via News89", "url": "https://news89.com/in-air-for-8-hours-us-bound-air-india-flight-returns-to-delhi-after-snag/"},
            {"name": "Aviation Today India", "url": "https://aviationtoday.in/air-india-flight-to-san-francisco-returns-to-delhi-after-mid-air-technical-malfunction/"},
            {"name": "Daily Jagran", "url": "https://www.thedailyjagran.com/aviation/air-india-to-cut-22-indigo-to-slash-7-domestic-flights-amid-high-fuel-prices"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33404485/pexels-photo-33404485.jpeg",
        "body": """On May 27, Air India Flight AI173 — a Boeing 777-300ER carrying roughly 230 passengers from Delhi to San Francisco — turned around over Chinese airspace and limped back to Indira Gandhi International Airport. The aircraft had been airborne for barely three hours when the crew detected a failure in the Traffic Collision Avoidance System, the onboard radar that prevents mid-air collisions and is considered non-negotiable for transoceanic routes. Reports from aviation monitoring channels indicate both TCAS channels went dark simultaneously, though Air India has not officially confirmed the specific malfunction.

The return journey took another three and a half hours. Before landing, the 777 had to circle for nearly an hour to jettison fuel — a standard but dramatic procedure required because long-haul aircraft depart at weights far too heavy for a safe landing with full tanks. Total time in the air: more than eight hours, covering zero miles of the 7,700-mile route to San Francisco.

## Why This Matters to NRIs

The Delhi–San Francisco corridor is not a casual route. It is the primary artery connecting India to the heart of American tech — the Bay Area, home to more than 400,000 Indian-origin residents, thousands of H-1B workers commuting between offices and families, and a steady stream of elderly parents visiting on B-2 visas. When AI173 fails, it is not an abstract operational hiccup. It is someone's mother stuck in a Delhi hotel room wondering when she will see her grandchildren.

The timing makes it worse. Air India has already announced the suspension of Delhi-Newark, Delhi-Chicago, and Mumbai-New York routes from June 1 through August 31, driven by a fuel crisis that has also prompted a 22 percent cut in domestic flights. IndiGo, meanwhile, has slashed 17 percent of its international capacity. The NRI corridor is being squeezed from both ends: fewer flights, and now questions about the mechanical condition of the ones that remain.

## A Pattern, Not an Anomaly

This is not the first safety scare involving Air India's long-haul fleet in recent weeks. On May 21, Flight AI2802 from Bengaluru to Delhi experienced an engine fire after landing. The Tata-owned carrier recently completed a $400 million cabin overhaul of its Boeing 787 Dreamliner fleet, and it logged a record annual loss exceeding $2.4 billion — battered by high fuel costs, a strong dollar, and Pakistan's closure of its airspace to Indian carriers.

For the diaspora traveler weighing options this summer, the calculus has shifted. Foreign carriers — Emirates, Singapore Airlines, Cathay Pacific, British Airways — are adding India capacity precisely as Air India pulls back. The premium for a one-stop itinerary through Dubai or Singapore may be the price of peace of mind.

## What NRIs Should Do Now

If you hold a confirmed booking on Air India for any US-India route between June and August, check the airline's website for schedule changes. Delhi-Newark and Mumbai-JFK passengers need to rebook immediately; those routes are suspended. For SFO-DEL, the route remains active, but the turnaround incident is a reminder to purchase comprehensive travel insurance that covers delays and rebooking — not just lost baggage.

Air India said it is "providing all necessary assistance" to stranded passengers, including hotel accommodation and rescheduling options. The airline added that it will "continue to monitor demand and operating conditions closely." For NRIs who have heard that language before, the translation is simple: book a backup."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "South Africa Wants 100,000 Indian Visitors This Year — and It's Finally Fixing the Two Things That Kept Them Away",
        "subheadline": "A fully digital visa system is live, direct flight talks with Air India and IndiGo are underway, and Cricket World Cup travel packages are already being designed. South Africa is making its most aggressive play yet for Indian tourists — and NRIs are the quiet target.",
        "slug": make_slug("south-africa-100k-indian-visitors-digital-visa-direct-flights"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs with US passports already have easy South Africa access, but millions of Indian passport-holding H-1B and green card holders still face visa friction. The new digital visa system and potential direct flights from India could make SA the next big diaspora vacation destination, especially with Cricket World Cup 2027 on the horizon.",
        "tags": ["travel", "south africa", "visa", "cricket", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelBiz Monitor", "url": "https://travelbizmonitor.com/top-stories/south-africa-targets-100000-indian-visitors-in-2026-with-digital-visa-push/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/south-africa-joins-united-kingdom-germany-france-italy-spain-poland-and-other-major-countries-in-the-largest-ever-global-digital-visa-and-border-revolution/"},
            {"name": "Africa's Travel Indaba 2026 (Durban)", "url": "https://travelbizmonitor.com/top-stories/south-africa-targets-100000-indian-visitors-in-2026-with-digital-visa-push/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/136721/pexels-photo-136721.jpeg",
        "body": """South Africa's Tourism Minister Patricia de Lille stood before the Indian media at Africa's Travel Indaba 2026 in Durban last week and said something no South African official has said quite this directly before: the country wants 100,000 Indian visitors this year, and it has finally removed the two obstacles that have kept that number stubbornly low.

The first obstacle was the visa. South Africa's paper-heavy, appointment-dependent visa process had long been the single biggest complaint from Indian travelers — a bureaucratic wall that turned a spectacular destination into a logistical headache. That wall is now down. "We have a completely digital visa system in place," de Lille said. The new eVisa and Electronic Travel Authorization (ETA) system allows Indians to apply online with automated processing, eliminating the need for in-person embassy visits.

The second obstacle was getting there. India and South Africa currently have no direct commercial flights. Every itinerary requires a connection through the Gulf, Nairobi, or Addis Ababa — adding six to ten hours to what should be a nine-hour flight. De Lille revealed that her government is actively negotiating with Air India and IndiGo for direct service. "Both airlines are prepared to begin operations," she said, "but the shortage of aircraft remains a challenge."

## The Numbers Tell the Story

In 2025, South Africa welcomed 69,680 Indian visitors. In the first quarter of 2026 alone, 12,912 arrived — roughly on pace to match last year's total, but still a fraction of what the Rainbow Nation believes it can attract. For context, South Africa hosted 10.5 million international visitors last year and has set a target of 15 million by 2029. India, with its massive and increasingly affluent middle class, is seen as the market that can bridge that gap.

What is less discussed is the NRI dimension. The 4.5 million-strong Indian American community holds US passports that make South African entry relatively painless. But millions more hold Indian passports with H-1B or green card status — and for them, the old visa process was a dealbreaker. The digital overhaul changes that equation overnight.

## Cricket, Weddings, and the MICE Machine

De Lille's most intriguing play is cricket. South Africa will host the ICC Cricket World Cup in 2027, and the minister said her team is already curating specialized travel packages aimed at Indian cricket fans. "Indians love cricket, and we are designing packages keeping this in mind," she said. If the 2011 and 2023 World Cups are any guide, Indian fans travel in enormous, enthusiastic numbers — and they spend generously.

Beyond cricket, the MICE (Meetings, Incentives, Conferences, Exhibitions) segment already accounts for a striking 45 percent of all Indian arrivals to South Africa. Corporate India, it turns out, has discovered Cape Town's conference venues and Johannesburg's business infrastructure. De Lille also flagged multi-generational travel and honeymoon tourism as the fastest-growing segments — both categories where NRI families are natural fits.

## What NRIs Should Know

The practical picture is improving fast. South Africa's eVisa for Indian passport holders is available online through the Department of Home Affairs portal. Processing is typically same-day to 48 hours. Flights remain indirect — the best routing is usually Emirates via Dubai (about 15 hours total) or Ethiopian Airlines via Addis Ababa (about 13 hours) — but if Air India or IndiGo launches a Delhi-Johannesburg nonstop, the travel time drops to under ten hours.

For NRIs planning a 2027 Cricket World Cup trip, the advice is simple: start watching for direct flight announcements, apply for your eVisa as a test run this year if you are on an Indian passport, and earmark Cape Town in February or March — the South African summer, when the weather is impeccable and the Winelands are at their best.

South Africa has tried to court India before. This time, the infrastructure is finally catching up to the ambition."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your H-1B Is a Travel Hack — 12 Countries NRIs Can Visit This Summer Without a Separate Visa",
        "subheadline": "Mexico for 180 days, the Philippines for 30, Turkey on an eVisa in minutes. Indian passport holders with a valid US visa have access to a shadow network of visa-free destinations that most never use.",
        "slug": make_slug("us-visa-travel-hack-nri-visa-free-countries-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRIs on H-1B, L-1, or green cards focus exclusively on India trips and domestic US travel. But a valid US visa or green card opens visa-free or simplified entry to over a dozen countries — from Cancun beach weekends to Bali getaways — often with zero additional paperwork.",
        "tags": ["travel", "visa", "nri", "h1b", "mexico", "caribbean"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Voye Global", "url": "https://voyeglobal.com/countries-indians-can-visit-with-us-visa/"},
            {"name": "TripAdvisor Mexico Forum", "url": "https://www.tripadvisor.co.uk/ShowTopic-g150805-i8-k14393640-Visit_Cancun_with_Indian_passprt_and_valid_H1B_visa-Cancun_Yucatan_Peninsula.html"},
            {"name": "India in Mexico Embassy Advisory", "url": "https://indiainmexico.gov.in/"},
            {"name": "iVisa Travel Guide", "url": "https://www.ivisa.com/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6840004/pexels-photo-6840004.jpeg",
        "body": """Every summer, millions of Indian Americans face the same decision: fly home to India, or take the family somewhere new. Most choose India — understandably, when parents are waiting and wedding season is in full swing. But for the weekends, the long weekends, and the rare year when the India trip is already booked for Diwali, there is a question that surprisingly few NRIs ask: where else can I go without dealing with another visa?

The answer, it turns out, is a lot of places. A valid US visa — whether H-1B, L-1, B-1/B-2, or a green card — unlocks visa-free or visa-on-arrival access to more than a dozen countries. Here is the practical list, stripped of the usual travel-blog fluff.

## Mexico: The Obvious One (Up to 180 Days)

Indian passport holders with a valid multiple-entry US visa can enter Mexico without a Mexican visa for up to 180 days. No appointment, no consulate visit, no separate application. You show your Indian passport and US visa at immigration, and you are in.

Cancun is the entry point most NRIs know — direct flights from Houston, Dallas, and Miami run under four hours and frequently dip below $250 round-trip. But Mexico is far more than a beach. Mexico City is one of the world's great food capitals, Oaxaca is a UNESCO-listed cultural treasure, and the Yucatán's cenotes and ruins (Chichén Itzá, Tulum) are genuinely unlike anything else in the Americas.

**Practical note:** Airlines may ask for proof of accommodation and a return flight. Have both on your phone. The old FMM paper form is no longer required at airports — passports are stamped directly.

## The Philippines: Visa-Free for 30 Days

Indian citizens with a valid US visa can enter the Philippines without a separate visa for up to 30 days. This applies equally to H-1B holders and green card holders. Palawan, Cebu, and Boracay are world-class beach destinations at a fraction of Maldives prices, and Manila's food scene has exploded in the past three years.

## Turkey: eVisa in Under Five Minutes

Indian passport holders can obtain a Turkish eVisa online in minutes. The process is entirely digital, costs about $50, and is approved almost instantly. Istanbul alone justifies the trip — the Hagia Sophia, the Grand Bazaar, and the Bosphorus are bucket-list landmarks. Cappadocia's hot air balloon rides are the most photographed experience on Instagram for a reason.

## Costa Rica: Visa-Free for 30 Days

With a valid US visa, Indian passport holders can enter Costa Rica for up to 30 days without a separate visa. The country is compact enough for a week-long trip that combines cloud forests, Pacific beaches, and volcanic hot springs. Direct flights from Houston, Miami, and Los Angeles make it surprisingly accessible.

## Panama: Visa-Free for 30 Days

Panama accepts Indian passport holders with a valid US visa for stays up to 30 days. Panama City's Casco Viejo neighborhood is a gem, and the canal is worth seeing at least once. It is also a surprisingly affordable family destination — hotels and restaurants run about 40 percent cheaper than comparable spots in Costa Rica.

## The Full List

Beyond the headliners, Indian passport holders with a valid US visa or green card can also visit: **Colombia** (90 days), **Georgia** (one year), **Albania** (90 days), **Bermuda** (up to 90 days), **Dominican Republic** (visa on arrival), **Jamaica** (visa on arrival for some categories), and **Oman** (eVisa). Each has its own fine print, so verify current rules on the destination's immigration website or the Indian Embassy page before booking.

## The NRI Blind Spot

The reason most NRIs do not use these options is not ignorance — it is inertia. The annual India trip consumes the PTO budget, the mental bandwidth, and often the airfare budget too. But a three-day Cancun weekend or a five-day Costa Rica escape costs less than most domestic US vacations, requires zero additional paperwork, and gives the kids something to talk about at school that is not "we went to Nani's house again."

For H-1B holders specifically, there is one critical caveat: re-entry to the US requires a valid visa stamp in the passport. If your H-1B stamp has expired (even if your I-797 is current), you cannot re-enter the US after traveling internationally without first getting a new stamp at a US consulate. This is not a Mexico or Philippines issue — it is a US immigration issue. Confirm your stamp validity before booking anything.

Your US visa is doing more work than you think. Use it."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
