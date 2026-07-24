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
        "headline": "The Work-Visa Wait Is Back to Four Months — and It's About to Get Worse Before October",
        "subheadline": "H and L appointment backlogs at U.S. consulates in India have stretched to 75–125 days, even as visitor and student slots stay quick. The squeeze lands just as the H-1B cap season heats up.",
        "slug": make_slug("us-consulate-india-h1b-l-visa-backlog-75-125-days-nri-summer"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "For the hundreds of thousands of Indian tech and finance workers on H-1B and L visas, a stamping trip home this summer can now strand them in India for months — long enough to miss a project start, a school year, or a return flight already booked.",
        "tags": ["travel", "visa", "h-1b", "immigration", "consulate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — Update on Visa Appointment Backlogs at U.S. Consulates in India", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-u-s-consulates-in-india.html"},
            {"name": "U.S. Department of State — Global Visa Wait Times", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/wait-times.html"},
            {"name": "VisaVerge — US Visa Process for Indians 2026", "url": "https://www.visaverge.com/"}
        ]),
        "score_total": 85,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061949/pexels-photo-8061949.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An applicant's passport and travel documents being prepared for a visa appointment.",
        "image_attribution": "Pexels",
        "body": """For the Indian professional who timed a summer trip home around a routine visa stamping, the math has quietly turned hostile. U.S. consulates in India are now quoting appointment waits of **75 to more than 125 days** for H, L and other employment-based nonimmigrant visas — a backlog that can turn a two-week holiday into a four-month exile.

The numbers come from immigration firm Fragomen, which tracks consular wait times across the five posts that handle U.S. visas in India: Chennai, Hyderabad, Kolkata, Mumbai and New Delhi. The bottleneck is specific. Visitor visas (B-1/B-2) and student visas (F-1) are still moving fast, with waits of just **four to 22 days**. It is the work-visa applicants — the engineers, consultants and managers who form the backbone of the Indian-American professional class — who are stuck.

## What changed, and why it bites now

The cause is not a single policy but a collision of them. Demand for U.S. visas has climbed steadily over the past year, yet consular staffing at the U.S. mission in India has not grown to match. On top of that, two earlier shifts funneled even more pressure onto Indian posts: the introduction of mandatory social-media vetting for employment-based applicants, which slowed each interview, and the end of "third-country" visa stamping for many Indian nationals, which closed off the safety valve of getting stamped in a nearby country like Mexico or the UAE.

The result is a calendar that has run dry. Kolkata, long the quiet workaround with a 13-day wait, has seen its backlog balloon past **126 days**. The posts in the big metros are no better.

## Why this matters to the diaspora

This is the trip-home trap, and it is sprung most often in summer. An H-1B or L-1 holder living in the U.S. whose visa stamp has expired must get re-stamped at a consulate abroad before re-entering — and for Indians, "abroad" now effectively means India, where the queue is longest. Plan a June wedding in Hyderabad, and you may not get an interview slot until October. Employers are left with workers unable to return; families are left with kids missing the start of the U.S. school year.

The pressure is set to intensify. The backlog typically worsens as the **October 1 start date** for the new fiscal-year H-1B cap approaches, when a fresh wave of approved petitions all need stamping at once.

## What NRIs can actually do

A few practical moves can soften the blow:

- **Don't let the stamp lapse if you can avoid it.** If your current visa is still valid, weigh whether you truly need to travel before renewing.
- **Book the interview before you book the flight.** Treat the consular slot, not the airfare, as the fixed point of the trip.
- **Watch for cancellation slots.** Consulates release openings irregularly; applicants who already have a far-off appointment can rebook earlier if they check the portal often.
- **Consider the Dropbox / interview-waiver route** where eligible — drop-off processing at the visa application centers in Chennai, Hyderabad, Kolkata, Mumbai or New Delhi can sidestep the in-person interview queue entirely for those who qualify.
- **Third-country stamping is now a costly gamble**, not a quick fix — it carries extra travel expense and, often, a separate visa to enter that country.

The blunt takeaway for the summer of 2026: if your livelihood depends on returning to the U.S. on an H or L visa, build months of slack into any India trip — or stay put until the calendar clears."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Made It Easier to Fly a Foreign Passport Home — 11 New Gateways and a 120-Day Window",
        "subheadline": "The e-Tourist Visa has been rebranded 'e-Visa' and rebuilt: more entry points, longer application validity, and combinable visa types. For mixed-passport NRI families, the friction of visiting just dropped.",
        "slug": make_slug("india-evisa-overhaul-11-new-ports-120-day-window-nri-foreign-passport"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Plenty of NRI households travel on two passports — an Indian parent and a US- or UK-citizen spouse or child. India's e-Visa overhaul, with new ports like Coimbatore and Goa and a 120-day application window, makes coordinating that mixed-passport trip home far less of a paperwork scramble.",
        "tags": ["travel", "visa", "e-visa", "india", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — Additional Countries and Ports of Arrival Added to e-Visa Program", "url": "https://www.fragomen.com/insights/additional-countries-and-ports-of-arrival-added-to-e-visa-program.html"},
            {"name": "Ministry of Tourism, Government of India", "url": "https://tourism.gov.in/"},
            {"name": "India e-Visa official portal", "url": "https://indianvisaonline.gov.in/evisa/tvoa.html"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16737432/pexels-photo-16737432.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Travelers passing through an airport immigration and arrivals hall.",
        "image_attribution": "Pexels",
        "body": """India has quietly given its online visa system its biggest tune-up in years, and the changes land squarely in the favor of the diaspora's foreign-passport-holding relatives. The Ministry of Home Affairs has relaunched the old e-Tourist Visa under a broader name — simply **'e-Visa'** — and rebuilt the program around more entry points, a longer planning window, and the ability to mix visa types on a single trip.

## What actually changed

The headline numbers: the e-Visa is now open to nationals of **161 countries**, after **11 were added** (Angola, Azerbaijan, Burundi, Cameroon, Cyprus, **Italy**, Mali, Niger, Rwanda, Sierra Leone and Uzbekistan). More useful for travelers already eligible — including U.S., U.K., Canadian and Australian citizens — is the expanded list of where you can land.

**Eleven new designated ports of arrival** now accept e-Visa entries: Bagdogra Airport, Calicut Airport, Chandigarh Airport, Kochi Seaport, Coimbatore Airport, Goa Seaport, Guwahati Airport, Mangalore Airport and Seaport, Nagpur Airport and Pune Airport. That spread matters: a foreign-passport spouse can now fly straight into Coimbatore for a Tamil Nadu family visit, or into Mangalore or Calicut for the coastal Kerala-Karnataka belt, instead of clearing immigration in Delhi or Mumbai and backtracking.

## The flexibility upgrades

Three changes make trip-planning genuinely easier:

- **A 120-day application window.** You can now travel to India within 120 days of applying for the Electronic Travel Authorisation, up from the old 30-day window. Booking visas months ahead of a peak-season trip no longer risks the authorization expiring before you fly.
- **Three sub-categories, combinable.** Applicants choose among e-Tourist, e-Medical and e-Business visas — and may **combine types** if a visit covers more than one purpose. e-Tourist and e-Business now grant **double entries**; e-Medical grants triple.
- **Twice a year.** Foreign nationals can use the e-Visa program twice per calendar year.

The core rules still hold: the e-Visa is valid for **60 days from arrival and cannot be extended**, the passport must have at least six months' validity plus a return or onward ticket, and entry must be through a designated port (though you may exit from any authorized check post). It remains unavailable to diplomatic/official passport holders and to anyone of Pakistani origin or traveling on a Pakistani passport.

## Why this is a diaspora story

The e-Visa is, in practice, the document most NRI families wrestle with — not for themselves, but for the foreign-citizen members of the household. An OCI card covers an Indian-origin spouse or child, but a non-Indian-origin partner, a foreign in-law, or a friend joining the trip still needs a visa. For those travelers, the old 30-day window forced awkward timing: apply too early and the authorization lapsed; apply too late and you sweated the approval. The new 120-day runway removes that trap.

The new ports also reshape routing. A family splitting time between, say, Pune and Goa can now have its foreign-passport members enter at either rather than funneling everyone through a megahub. And the combinable visa types quietly help the common NRI pattern of a trip that is part holiday, part medical check-up for an aging parent, part business.

None of this is a fee giveaway — standard e-Visa charges still apply for most nationalities — but the friction has dropped. For households that have long treated the foreign-passport visa as the most annoying line item of any India trip, the 2026 overhaul is a welcome simplification. Apply through the official portal, indianvisaonline.gov.in, and budget the same processing buffer you always have; the rules are looser, but the queues at peak season are not."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Delhi-NCR Finally Has Its Third Airport — and Mumbai's Second One Goes Global Next Month",
        "subheadline": "Noida International at Jewar began commercial flights on June 15; Navi Mumbai opens to international traffic on July 15. Two long-delayed mega-airports are reshaping how the diaspora's two busiest gateways work.",
        "slug": make_slug("noida-jewar-airport-open-navi-mumbai-international-july-nri-gateways"),
        "category": "travel",
        "vertical": "infrastructure",
        "diaspora_angle": "Delhi and Mumbai are the two airports nearly every NRI passes through. A third runway in NCR and a second international gateway in greater Mumbai mean shorter drives, less congestion, and — eventually — new nonstop options closer to where families actually live.",
        "tags": ["travel", "airports", "india", "infrastructure", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine — Navi Mumbai Airport to launch international flights from July 15", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Wikipedia — Noida International Airport", "url": "https://en.wikipedia.org/wiki/Noida_International_Airport"},
            {"name": "Outlook Business — Noida International Airport Begins Freight Operations", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg/1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "image_caption": "The inauguration ceremony of the Noida International Airport at Jewar, Uttar Pradesh.",
        "image_attribution": "Wikimedia Commons",
        "body": """After more than a decade of groundbreakings, deadlines and slips, India's two most-trafficked metros are getting the airport relief they have needed for years. **Noida International Airport** at Jewar began commercial passenger operations on **June 15**, giving the Delhi-National Capital Region its third airport. And **Navi Mumbai International Airport**, the Adani-run second gateway for the Mumbai region, is set to open to international flights on **July 15**. For a diaspora that routes almost all its India travel through Delhi and Mumbai, this is the most consequential infrastructure shift in years.

## Noida (Jewar): NCR's pressure valve

Located in Jewar, in Uttar Pradesh's Gautam Buddha Nagar district, Noida International (IATA code **DXN**) was inaugurated by Prime Minister Narendra Modi on March 28 and cleared for commercial service after the Bureau of Civil Aviation Security signed off on its security program. **IndiGo** operated the first flight on June 15, with Akasa Air and Air India Express expected to follow. The airline plans to build out direct service to **more than 16 destinations**, mixing metros like Bengaluru and Hyderabad with tier-2 and tier-3 cities such as Amritsar, Chandigarh, Dharamshala, Jaipur, Lucknow and Srinagar. Cargo is already moving too: the first freighter, a Chennai-Noida service, landed days after the passenger launch.

Phase one handles **12 million passengers a year** through a single runway and terminal, and is meant to complement — not replace — the perennially congested Indira Gandhi International. For NRI families whose roots are in western UP or who are tired of the long haul across Delhi traffic to IGI, a closer eastern gateway changes the calculus of a trip home.

## Navi Mumbai: the international piece arrives

On the west coast, Navi Mumbai International began domestic operations last Christmas and has already grown to roughly 149 daily flights serving 46 destinations, handling about 20,000 passengers a day. The next step is the big one: **international service from July 15**, starting with freighters and Gulf-region passenger routes — exactly the corridors the diaspora uses most.

Air India Express and IndiGo have filed international route plans, and the airport's chief executive expects movements to scale quickly. Planners are already thinking bigger than the original blueprint: **Terminal 2 is being redesigned to handle 50 million passengers** annually, up from 30 million, with overall capacity eventually targeted near 90 million. The lotus-inspired terminal also landed on the **Prix Versailles** list of the world's most beautiful airports for 2026.

## Why the diaspora should care

Two structural shifts matter here. First, **congestion relief.** Delhi's IGI and Mumbai's Chhatrapati Shivaji Maharaj International are among the busiest in Asia, and peak-season arrivals — when the diaspora floods home for Diwali and winter weddings — can mean long taxi-ways, slow immigration and missed connections. Splitting traffic across a second or third field eases all of it.

Second, **geography.** Greater Mumbai and the NCR are sprawling; a single airport forces many travelers into hours of ground transit. A Navi Mumbai gateway is far closer for those in the eastern suburbs, Pune corridor and beyond, while Jewar serves the NCR's eastern and southern reaches. As international routes mature at both airports — Gulf hops first, long-haul later — the prospect grows of a nonstop that lands closer to where family actually lives, rather than the default megahub.

The international long-haul map at these airports will take time to fill in, and the Gulf-conflict airspace disruptions of early 2026 have already pushed some plans back. But the direction is set. For the NRI who has spent years bracing for the IGI or BOM crush every trip home, the summer of 2026 marks the moment the alternatives finally came online."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
