#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-26 07:00 PDT batch"""

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
    # ─── ARTICLE 1: India e-Arrival Card ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India Killed the Paper Landing Card — and the Replacement Has a Gotcha Every NRI Should Know",
        "subheadline": "Since April 1, all foreign nationals and OCI cardholders must submit a digital e-Arrival Card within 72 hours of landing. Miss the QR code, and you could spend your first hour in India at a staffed kiosk.",
        "slug": make_slug("india-e-arrival-card-mandatory-oci-nri-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Every NRI and OCI cardholder landing in India must now complete the digital e-Arrival Card before arrival. The paper disembarkation form that flight attendants handed out for decades is gone. For the estimated 4.7 million OCI holders and millions more who visit India annually, this is the single most immediate travel change of 2026 — and the QR code retrieval issue is catching people off guard at immigration.",
        "tags": ["travel", "india", "oci", "immigration", "e-arrival-card", "visa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Envoy Global", "url": "https://www.envoyglobal.com/news-alert/india-e-arrival-card-for-all-foreign-nationals-within-72-hours-before-arrival/"},
            {"name": "High Commission of India, London", "url": "https://www.hcilondon.gov.in"},
            {"name": "U.S. Embassy in India", "url": "https://in.usembassy.gov"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "body": """If you've flown to India any time in the last three decades, you know the ritual: somewhere over the Arabian Sea, a flight attendant hands you a small white card. You fish out a pen, scribble your passport number, your address in India (always a guess), and the purpose of your visit. You hand it to the immigration officer, who barely glances at it.

That card is dead.

## What Changed

On April 1, 2026, India's Bureau of Immigration made the **e-Arrival Card** mandatory for every foreign national entering the country. That includes tourists, business travelers, diplomats — and, critically, the millions of Indian Americans who hold **Overseas Citizen of India (OCI)** cards.

The shift didn't happen overnight. India first announced the move to a digital arrival process on October 1, 2025, and gave travelers a six-month transition window to adjust. During that period, the paper form still worked. That grace period is now over.

## How It Works

The process itself is straightforward. Within **72 hours** of your scheduled arrival, you visit the government's portal or download the **Su-Swagatam** mobile app, fill in your travel and passport details, and submit. No fee. No documents to upload. The whole thing takes about five minutes.

The system then generates a completed arrival card with a **QR code**. You present that QR code — on your phone screen or a printout — to the immigration officer at the airport. That's it.

## The Gotcha

Here's where it gets tricky, and immigration consultants say this is already catching travelers off guard.

Once you submit the form and the system generates your QR code, **you must download or screenshot it immediately**. If you close the browser window without saving it, there is no reliable way to retrieve it. Submitting a new form may create a duplicate record in the system. And showing up at immigration without the QR code doesn't mean the officer can simply look you up — in many cases they cannot, or it means a long wait at a staffed assistance kiosk while they sort it out.

"The process takes about five minutes. There's no fee and no documents to upload," said Ashok Sharma, VP of Operations at Envoy Global, an immigration services firm. "Here's the catch we keep seeing: once you submit the form, if you close the browser without downloading or screenshotting it, you won't be able to retrieve it."

The U.S. Embassy in India confirmed the requirement in an April 8 advisory, noting that OCI cardholders are explicitly included.

## What NRIs Should Do

**Before you leave for the airport:**

1. Complete the e-Arrival Card on [the official portal](https://in.indianvisaonline.gov.in/) or via the Su-Swagatam app (available on iOS and Android)
2. **Screenshot the QR code** the moment it generates
3. Email it to yourself as a backup
4. Save a PDF or image to your phone's camera roll — don't rely on the browser tab staying open
5. Consider printing a paper copy if you're traveling with elderly family members who may not have a charged phone at immigration

**Timing matters:** The 72-hour window means you can fill it out up to three days before landing. Don't leave it for the flight — in-flight Wi-Fi on India-bound routes is unreliable, and the last thing you want is to be filling out government forms while taxiing at Indira Gandhi International.

## The Bigger Picture

India's move mirrors a global trend. Thailand launched its own Digital Arrival Card in 2025, replacing its longstanding TM6 paper form. The European Union's EES biometric system went live this year. Even the U.S. has been pushing toward digital I-94 forms for years.

For NRIs planning summer trips home — and with monsoon season, wedding season, and school breaks converging in the next few months, that's a lot of people — this is a five-minute task that can save you a miserable hour in the immigration queue.

The paper card served its purpose for decades. Its replacement is better in every way, with one exception: it punishes you for not saving a screenshot. Don't be that person."""
    },

    # ─── ARTICLE 2: Summer 2026 Fare Surge ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Summer 2026 India Flights Are the Priciest in Years — Here's the NRI's Playbook for Beating the Surge",
        "subheadline": "Brent crude nearly doubled since February, United's CEO is warning of 20% fare hikes, and airlines are slashing India capacity. For NRIs planning summer trips home, booking strategy matters more than it has in a decade.",
        "slug": make_slug("summer-2026-india-flights-expensive-nri-booking-tips"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The 4.5 million Indian Americans who fly to India each summer are facing a perfect storm of higher fares, fewer seats, and longer flights. The Iran conflict's impact on jet fuel, combined with airline capacity cuts on India routes, means the annual summer pilgrimage to see family is significantly more expensive in 2026. Practical booking strategies can save NRI families $500-1,500 per ticket.",
        "tags": ["travel", "flights", "fares", "airlines", "india", "summer", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/industry/india-aviation-west-asia-war-iran-us-conflict-airline-losses-indigo-air-india-international-flights-gulf-routes-11779724762871.html"},
            {"name": "Morningstar", "url": "https://www.morningstar.com"},
            {"name": "United Airlines / The Travel", "url": "https://www.thetravel.com"},
            {"name": "GasBuddy / DevDiscourse", "url": "https://www.devdiscourse.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png",
        "body": """Every summer, millions of Indian Americans do the same thing: open Google Flights, type in SFO-DEL or JFK-BOM, and wince. This year, the wince is worse.

The numbers tell a grim story. Brent crude has surged from **$70 to $118 per barrel** since the U.S. struck Iran on February 28, and jet fuel — which accounts for 30-40% of an airline's total operating costs — has tracked that spike almost exactly. United Airlines CEO Scott Kirby warned travelers to expect fare increases of **up to 20%** this summer season. Patrick De Haan of GasBuddy called it "the most volatile summer at the pump in years," adding that even after the Strait of Hormuz reopens, full price recovery could take a year or more.

For NRIs, this isn't abstract macroeconomics. It's the difference between a $1,200 round-trip to Delhi and a $1,800 one.

## Why India Routes Are Hit Harder

Global airfares are up about **10% on average** compared to summer 2025, according to aviation data firm OAG. But India-bound routes from the U.S. are taking a disproportionate hit for three reasons:

**The Gulf detour.** Most affordable India flights from the U.S. route through Dubai, Abu Dhabi, or Doha. Iranian airspace closures have forced these flights onto longer paths, burning more fuel per trip. Routes that once took 16 hours via Emirates or Etihad now run 18-19 hours on some days.

**Capacity cuts.** Air India has already reduced frequency on select international routes for June through August, citing impact on "commercial viability of certain planned services." IndiGo's international traffic dropped 37% in March alone. Fewer seats means higher prices for the seats that remain.

**Seasonal demand.** Summer is peak season for the India corridor — school breaks, weddings, family visits. Airlines know NRIs will pay a premium to get home. When supply shrinks and demand stays rigid, fares spike.

## The Playbook

There's no magic trick to dodge a systemic fare increase, but booking strategy can shave hundreds off each ticket:

**1. Book now, not later.** Fares on India routes typically climb steadily from June onward and peak in July. If you're traveling in July or August, the cheapest window was two weeks ago. The second cheapest window is today.

**2. Consider September.** Historically the cheapest month to fly USA-India, September fares can be 30-40% lower than peak July. If your schedule is flexible — and especially if you're visiting parents rather than attending a fixed-date event — pushing the trip by six weeks saves real money.

**3. Route through Europe, not the Gulf.** The "Paris Pivot" is real. Air France via Paris, Lufthansa via Frankfurt, and SWISS via Zurich (which just launched direct Zurich-Bengaluru service) are operating normally because their routes don't cross Middle Eastern airspace. Their fares haven't spiked as sharply.

**4. Watch for nonstop flash sales.** Air India's nonstop flights (SFO-BLR, JFK-DEL, EWR-BOM) avoid the Gulf entirely and don't incur the extra fuel penalty. These routes are in high demand, but Air India periodically runs sales to fill off-peak departures. Set Google Flights alerts for your specific route.

**5. Split the ticket.** Flying into one Indian city and out of another (open-jaw) sometimes unlocks lower fares. JFK-DEL with BOM-JFK, for instance, occasionally prices lower than a simple JFK-DEL round trip because of different load factors on each leg.

**6. Use miles strategically.** If you've been hoarding credit card points, this is the summer to burn them. Award availability on Air India (now Star Alliance) and Emirates is tighter than usual, but midweek departures in August still show availability on several programs.

## The Outlook

Analysts broadly expect a truce in the Middle East at some point, which would ease fuel costs and restore normal routing. Airline stock prices haven't cratered — they're down roughly 10% since the conflict began — suggesting markets expect resolution. But "at some point" doesn't help someone booking a July flight today.

The practical reality: summer 2026 is a year to be strategic about India travel, not spontaneous. Book early, route smart, and if you can, fly in September. Your wallet will thank you."""
    },

    # ─── ARTICLE 3: Kerala Gulf Corridor Crisis ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Kerala's Airports Are India's Biggest Casualty of the Gulf Corridor Crisis — and 2 Million Malayali Workers Feel It Most",
        "subheadline": "Kozhikode lost 54% of its international flights in March. Thiruvananthapuram lost 43%. Kochi lost 42%. No other Indian state depends on the Gulf corridor as heavily as Kerala — and no other state is paying this steep a price.",
        "slug": make_slug("kerala-airports-gulf-corridor-crisis-malayali-diaspora"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Kerala's Malayali diaspora is the single largest Indian community in the Gulf states, with an estimated 2.1 million workers across the UAE, Saudi Arabia, Qatar, Kuwait, Oman, and Bahrain. For Malayali Americans — many of whom still have parents, siblings, or property in Kerala — the Gulf corridor collapse means fewer flights, higher fares, and longer journeys home. The crisis also threatens the $12+ billion annual remittance flow that sustains Kerala's economy.",
        "tags": ["travel", "kerala", "gulf", "flights", "diaspora", "airlines", "iran"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint / HowIndiaLives", "url": "https://www.livemint.com/industry/india-aviation-west-asia-war-iran-us-conflict-airline-losses-indigo-air-india-international-flights-gulf-routes-11779724762871.html"},
            {"name": "IATA", "url": "https://www.iata.org"},
            {"name": "Travel and Tour World", "url": "https://travelandtourworld.com"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/06/Cochin_international_airport_terminal.jpg",
        "body": """When the data on Indian airports in March 2026 landed, the numbers out of Kerala read like a casualty report.

**Kozhikode: down 54%.** More than half the international flights gone. **Thiruvananthapuram: down 43%.** **Kochi: down 42%.** Three airports, all in the same state, all recording the sharpest declines of any airports in the country.

By comparison, Delhi's international flights fell just 3.4%. Bengaluru dropped 8%. Kolkata actually grew — marginally, at 0.9%. The pain was not distributed evenly across India. It landed, with devastating precision, on Kerala.

## Why Kerala

The answer is geography and history, both pointing to the same place: the Persian Gulf.

Kerala's international aviation network is overwhelmingly built around one corridor. The UAE alone accounts for more of Kerala's outbound traffic than all of Europe, North America, and East Asia combined. The state's three airports — Cochin International (CIAL), Trivandrum International, and Calicut International — function less like typical Indian airports and more like satellite terminals of Dubai and Abu Dhabi.

This isn't an accident. An estimated **2.1 million Malayalis** work across the six Gulf Cooperation Council states. They are nurses in Riyadh, engineers in Dubai, shop managers in Muscat, construction foremen in Doha. They fly home for Onam, for weddings, for emergencies. Their families fly out to visit them. The corridor runs both ways, and it runs constantly.

When the U.S. struck Iran on February 28 and Tehran retaliated, closing airspace across the region, this corridor didn't just thin out. For weeks, it essentially shut down.

## The Mechanics of Collapse

The Iranian airspace closure forced aircraft to fly circuitous longer routes around the conflict zone. For airlines operating relatively short hops between Kerala and the Gulf — flights that normally take three to four hours — the detours added fuel costs that destroyed the economics of the route.

Airlines responded rationally, and ruthlessly. Air India Group temporarily suspended scheduled flights to major Gulf destinations, shifting to restricted ad-hoc operations. IndiGo, which had been posting strong international growth through January and February, saw its international traffic drop 37% in March. Low-cost carriers that depended on thin margins and high load factors on Gulf routes simply couldn't make the math work.

The result: **India recorded 21% fewer international flights in March 2026 compared to March 2025.** But that national average masks the real story. The big metro hubs absorbed the shock through diversified networks — Delhi has flights to Europe, East Asia, and North America that are unaffected by Gulf disruptions. Kerala's airports had no such buffer.

## The Remittance Shadow

The flight crisis is the visible symptom. The deeper concern is what it signals for Kerala's economy.

Kerala receives an estimated **$12-15 billion in annual remittances** from its Gulf diaspora, a flow that funds everything from home construction to education to healthcare. When flights are disrupted, worker rotations slow down. New contracts get delayed. Emergency family travel becomes prohibitively expensive or logistically impossible.

The state's economy has long been described as a "remittance economy." If the Gulf corridor remains constrained through the summer — and airlines have already announced capacity cuts extending into August — the ripple effects extend well beyond airport traffic numbers.

## The Far East Is Not a Substitute

India's aviation analysts have pointed to the Far East as a resilient alternative corridor. Vietnam grew 69% year-on-year. Thailand grew 20% on a large base. Five of India's top six East Asian markets posted growth in the January-March quarter.

But this pivot means almost nothing for Kerala. Malayalis don't fly to Bangkok for work. The Gulf traffic that Kerala's airports have lost — 2.1 million workers, decades of established routes, the entire economic logic of those three airports — cannot be replaced by leisure traffic to Southeast Asia. The UAE alone handles more Indian passenger traffic than the top six Far East countries combined.

## What NRIs Should Know

For Malayali Americans — and there are an estimated 200,000 in the U.S. alone — the corridor crisis has practical consequences:

**Flying to Kerala is harder and more expensive.** Fewer connecting options through the Gulf means longer routings through Europe or direct flights via Delhi/Mumbai with a domestic connection. Round-trip fares from the U.S. to Kochi or Trivandrum have jumped 25-40% on some routes.

**Family visits from the Gulf are disrupted.** Parents or siblings working in Dubai or Sharjah face reduced flight frequencies and inflated fares for what used to be a routine weekend hop to Kerala.

**Emergency travel is the real pain point.** When a parent falls ill or a family emergency arises, the Gulf-Kerala corridor is the lifeline. Reduced capacity means fewer last-minute seats, higher walk-up fares, and more stress during already difficult moments.

The airlines will restore capacity when the conflict eases and fuel economics normalize. Markets expect it, and share prices reflect that expectation. But until then, Kerala's airports — and the millions of families whose lives are organized around the flights that pass through them — are bearing a cost that no other part of India is asked to carry."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
