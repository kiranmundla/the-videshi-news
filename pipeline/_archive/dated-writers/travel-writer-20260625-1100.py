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

article1_body = """Two changes landed in the same week that, taken together, redraw how Indians move through American airports — one for green-card holders and citizens, one for the relatives who visit them.

The first is the quiet but consequential fact that **Global Entry, U.S. Customs and Border Protection's flagship Trusted Traveler Program, is open to all eligible citizens of India.** India is one of only a handful of countries whose passport holders can enroll, joining a list that includes Germany, the United Kingdom, Singapore and South Korea. The second is **Google Wallet becoming the first digital wallet to support TSA PreCheck Touchless ID**, a facial-comparison system that lets enrolled flyers clear security without pulling out a physical ID or boarding pass.

For the Indian diaspora, these are not abstract policy notes. They directly shorten two of the most dreaded lines in American air travel: the customs hall after a 16-hour flight from Delhi, and the security snake at departure.

## How Global Entry works for Indian passport holders

The mechanics are deliberately two-sided, because India runs its own background check in parallel with CBP's. An applicant first creates an account in CBP's Trusted Traveler portal, completes the application and pays the **$100 non-refundable fee** for five years of membership. That is only half the process.

The India leg requires paying a separate fee of **₹500 through the Passport Seva portal** and — critically — an **in-person visit to a Passport Seva Kendra** to capture fingerprints, an ICAO-standard photograph and complete an interview. Only after both governments clear the applicant does CBP schedule the final U.S.-side interview at an enrollment center. The Embassy of India in Washington advises applicants who are not currently in India to time their CBP application close to a planned India visit, so the domestic biometric step can be finished in one trip.

Once approved, members skip the regular inspection lines and use an automated kiosk on arrival — scanning a passport, getting fingerprinted and photographed, and completing the customs declaration onscreen. As a bonus, Global Entry membership also confers eligibility for **TSA PreCheck** expedited screening on domestic and connecting flights.

## The touchless layer that just got easier

TSA PreCheck Touchless ID uses secure facial comparison to verify identity at the checkpoint. Until now, members had to manually enter passport details for each airline they flew, and the feature worked with only a limited set of carriers across 65 airports.

Google's update changes the plumbing. Eligible travelers add a digital ID built from their passport to Google Wallet, save a boarding pass, and opt in once — after which the touchless badge appears across roughly **100 participating airlines**. Google emphasized that identity data is shared with the TSA only after a traveler explicitly opts in and authenticates by unlocking the device, and that digital IDs are encrypted and stored locally on the phone.

## Why this matters to NRIs

The diaspora is among the heaviest users of the India–U.S. corridor, where Air India, United, Emirates, Qatar and others move tens of thousands of passengers a week. The pain points are predictable: families clearing immigration at JFK, Newark, SFO or ORD after ultra-long-haul flights, and the same families shuttling between U.S. cities for weddings, graduations and reunions.

A Global Entry membership turns the arrival ordeal into a kiosk tap. For visiting parents and relatives on Indian passports, it is now an option they can pursue — though the in-person biometric step in India means it pays to plan around a trip home. And for the millions of Indian-Americans who already hold PreCheck, the Google Wallet integration removes the per-airline friction that made touchless ID feel more trouble than it was worth.

The combined effect is incremental, not revolutionary. But for a community that flies the world's longest nonstop routes more than almost any other, shaving an hour off both ends of the journey is the kind of upgrade that actually gets noticed.

## What to do now

- **If you hold a U.S. passport or green card and fly to India regularly,** apply for Global Entry first; the PreCheck benefit is bundled in.
- **If you hold an Indian passport,** start the CBP application, then complete the ₹500 Passport Seva step and biometric visit during your next India trip.
- **If you already have PreCheck,** set up a digital ID in Google Wallet and opt into Touchless ID on your next domestic boarding pass.

**Sources:** Fragomen; CBP / Immigration.com; Embassy of India, Washington D.C.; Google Blog; Engadget."""

article2_body = """Europe is about to add a new step between Indian-American travelers and the continent's airports — but exactly which step depends on which passport you pull out of your bag.

The **European Travel Information and Authorisation System (ETIAS)** is scheduled to begin operations in the **last quarter of 2026**, the European Union's official guidance now states, with the exact start date to be announced at least six months in advance. It is the missing piece in a broader tightening of Europe's borders that already saw the biometric **Entry/Exit System (EES)** begin rolling out, and it lands squarely on the dual-passport reality of the diaspora.

## What ETIAS actually is

First, the clarification that matters most: **ETIAS is not a visa.** It is an online pre-authorization linked to a traveler's passport, similar to the United States' ESTA, the U.K.'s ETA, Canada's eTA and Australia's ETA. It applies to citizens of visa-exempt countries — a list of more than 60 nations that includes the **United States, the United Kingdom, Canada, Japan and Australia.**

A valid ETIAS authorization lets the holder enter 30 European countries for short stays — generally up to **90 days in any 180-day period** — as often as they like, though it never guarantees entry; a border officer still makes the final call. It is tied to the passport, valid for up to three years or until the passport expires, and a new passport requires a fresh authorization.

The fee has been a moving target. After initially being floated at 7 euros, EU officials set the ETIAS application fee at **20 euros** (roughly $23), with exemptions for certain age groups. For comparison, the U.K.'s ETA runs about £16–£20, the U.S. ESTA costs $40.27, Canada's eTA is CAD 7 and Australia's ETA carries an AUD 20 charge.

## The dual-passport split that defines the diaspora

Here is where it gets specifically relevant to NRIs. The Indian-American community is a mix of U.S. citizens, green-card holders and Indian passport holders, and ETIAS treats them very differently.

- **If you travel on a U.S. (or U.K., Canadian, Australian) passport,** you are visa-exempt for short European stays — and once ETIAS is live, you will need to obtain the authorization before you fly. No embassy visit, no biometrics appointment; an online form and 20 euros.
- **If you travel on an Indian passport,** ETIAS does not apply to you at all. India is not on the visa-exempt list, so Indian nationals still need a **Schengen visa** for Europe — the traditional, appointment-based, documents-heavy process.

This means a single household can face two entirely different pre-trip checklists for the same family vacation. The U.S.-citizen children fill out an online ETIAS form in minutes; the green-card-holding or Indian-passport parents queue for Schengen appointments. Families planning multi-generational European trips for 2027 and beyond should map each traveler's path now rather than discovering the mismatch at booking.

## How it fits with EES

ETIAS does not arrive alone. The **Entry/Exit System** — which digitally records fingerprints, facial images and passport details of non-EU nationals on entry and exit — has been phasing in, and the EU has said ETIAS will go live roughly six months after EES is fully operational. Together they replace passport stamps with a biometric, database-driven border. For Indian-passport holders, that means the data captured at the Schengen border is now electronic and tracked; for visa-exempt NRIs, ETIAS is the front door to that same system.

## Why this matters to NRIs

Europe is one of the diaspora's favorite discretionary destinations — summer holidays, honeymoons, business trips routed through Frankfurt, Paris, Amsterdam and Zurich. The practical takeaways:

- **Use only the official EU site** (europa.eu/etias) when ETIAS launches. The EU has repeatedly warned about copycat sites that mimic the official logo, harvest personal and card data, and tack on fees.
- **Apply before you book non-refundable travel,** since authorization, while usually quick, is not guaranteed.
- **Don't confuse ETIAS with a Schengen visa.** If anyone in your party travels on an Indian passport, they are on the visa track regardless of what ETIAS does.

The system is not operational yet, and "no action is required from travellers at this point," the EU notes. But for a community that books Europe months ahead and travels on a patchwork of passports, the time to understand the split is before the 2027 summer planning begins.

**Sources:** European Union External Action Service (EEAS) / europa.eu; The Points Guy; Barchart."""

article3_body = """The cheapest seat home for Diwali is the one you book before most of the diaspora starts thinking about it — and for the 2026 festive season, that window is closing fast.

The arithmetic on the India–U.S. corridor is unforgiving. Travel-pricing data consistently shows that **October through December is the single most expensive stretch of the year** to fly between the United States and India, because the Diwali homecoming collides head-on with Thanksgiving and Christmas demand. Economy round-trips that sit around $850 in the off-season routinely climb into the **$1,400–$2,000 range** during the festive crunch. The advice from fare analysts is blunt: for festive travel, **book five to seven months ahead** and turn on price alerts the day you commit to dates.

## The September loophole

For NRIs with flexibility, there is a well-documented sweet spot. **September is repeatedly flagged as the "golden month"** for the India route — U.S. summer vacations have ended, the Diwali wave has not yet crested, and airlines drop fares to fill seats. Round-trips in this window can fall as low as **$750–$850**, less than half the peak. Travelers who can land in India in mid-to-late September and stretch the trip into the festive period capture the low fare without missing the celebrations.

This year that math is sharpened by a structural problem. Indian carriers have been **trimming nonstop international capacity** through the summer and into autumn because of airspace restrictions over Pakistan and West Asia and stubbornly high jet-fuel prices. Air India has converted several North American services to one-stop operations and suspended others; IndiGo has pulled back on a string of international routes. Fewer nonstop seats into a fixed festive demand window is a recipe for steeper prices — which makes booking early less of a nicety and more of a necessity.

## Tactics that actually move the price

The savings on this route come from structure, not luck:

- **Fly midweek.** Tuesday and Wednesday departures are consistently cheaper than weekend flights, as business demand spikes Monday and Friday. The gap can be $80 or more per ticket.
- **Use secondary gateways.** Flying out of Newark (EWR) instead of JFK, or arriving into Bengaluru (BLR) or Hyderabad (HYD) instead of Mumbai, can shave meaningful amounts off the fare.
- **Embrace the layover.** With nonstop fares climbing as capacity tightens, one-stop itineraries via Doha (Qatar Airways), Dubai (Emirates), Abu Dhabi (Etihad) or Istanbul (Turkish, codesharing with IndiGo) frequently undercut the direct flights — sometimes substantially. The trade is a longer journey for a lower price.
- **Set alerts immediately.** AI-driven fare tools and basic price alerts both rely on the same principle: festive fares move in jumps, and the early, quiet drops are the ones worth catching.

## The domestic leg most NRIs forget

The flight to India is only half the trip. Domestic festive fares inside India surge just as hard — Thomas Cook India has cited demand jumps of **50–60% to leisure destinations** like Kashmir, Himachal and the Andamans, and **25–30% on metro routes** as India's own migrant workforce heads home for Diwali. An NRI who books a great fare into Delhi and then waits to sort the onward leg to a hometown like Patna, Lucknow or Kochi can lose much of the saving on the connection. Book the domestic segment in the same planning pass.

## Why this matters to NRIs

Diwali falls in the autumn, and for millions of Indian-Americans the festival is the anchor of the year's most emotionally important — and most expensive — trip. The combination of festive demand, holiday-season overlap and a genuine squeeze on nonstop capacity means 2026 is shaping up to be a tougher fare year than usual on the India route.

The good news is that none of the levers require luck. Booking by roughly May–July for an October–December trip, flying midweek, leaning on secondary airports and accepting a strategic layover are the same moves that have worked for years — they simply matter more in a constrained year. The single most expensive thing an NRI family can do is wait until the calendar reads October and hope.

**Sources:** Flyopedia; Airtripmasters; OneAir; Investment Guru India (Thomas Cook India); Travel And Tour World."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Global Entry Is Now Open to Indian Citizens — and Google Just Made the TSA Line Disappear Too",
        "subheadline": "Two changes in one week cut the customs hall and the security snake for the diaspora — but the Indian-passport route to Global Entry runs through a Passport Seva Kendra.",
        "slug": make_slug("global-entry-indian-citizens-tsa-precheck-touchless-google-wallet-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian citizens can now enroll in U.S. Global Entry and, with Google Wallet's new TSA PreCheck Touchless ID, the diaspora can skip both the customs and security lines on America's busiest India routes.",
        "tags": ["travel", "global entry", "tsa precheck", "airports", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — Global Entry Opens to All Eligible Citizens of India", "url": "https://www.fragomen.com/insights/global-entry-opens-to-all-eligible-citizens-of-india.html"},
            {"name": "Embassy of India, Washington D.C. — Global Entry Program", "url": "https://www.indianembassyusa.gov.in/"},
            {"name": "Google Blog — Google Wallet adds TSA PreCheck Touchless ID", "url": "https://blog.google/products/google-pay/tsa-precheck-touchless-id-google-wallet/"},
            {"name": "Engadget — Easier TSA PreCheck Touchless ID via Wallet", "url": "https://www.engadget.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37847918/pexels-photo-37847918.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Travelers undergo security screening at an airport terminal checkpoint.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe's New ETIAS Permit Lands in Late 2026 — and It Treats Your US Passport and Your Indian One Completely Differently",
        "subheadline": "The 20-euro online authorization is required for US, UK and Canadian passport holders, but Indian-passport NRIs still need a full Schengen visa — splitting a single family's trip into two paths.",
        "slug": make_slug("etias-europe-launch-2026-us-indian-passport-split-schengen-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "When ETIAS goes live in late 2026, US-citizen NRIs will need the new online permit while Indian-passport relatives still need a Schengen visa — meaning one diaspora household can face two entirely different pre-trip checklists for the same Europe vacation.",
        "tags": ["travel", "visa", "etias", "europe", "schengen"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "EEAS / European Union — Travelling to Europe (ETIAS)", "url": "https://www.eeas.europa.eu/"},
            {"name": "European Union — Official ETIAS information (europa.eu/etias)", "url": "https://travel-europe.europa.eu/etias_en"},
            {"name": "The Points Guy — The EU's ETIAS will launch in 2026", "url": "https://thepointsguy.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061952/pexels-photo-8061952.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport rests on an airline boarding pass and travel documents.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Booking Your Diwali Flight Home? In a Year of Shrinking Nonstops, the Cheap Seat Is the One You Buy Now",
        "subheadline": "Festive-season India fares run $1,400–$2,000 round-trip, and 2026's airspace squeeze makes them worse — but September timing, midweek departures and a strategic layover still beat the crunch.",
        "slug": make_slug("diwali-2026-flight-booking-strategy-india-nri-fares-festive-season"),
        "category": "travel",
        "vertical": "economy",
        "diaspora_angle": "Diwali is the diaspora's most important and most expensive trip home, and a 2026 squeeze on nonstop India capacity means NRIs who book early, fly midweek and accept a strategic layover will pay far less than those who wait for October.",
        "tags": ["travel", "flight deals", "diwali", "airlines", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Flyopedia — Best Time to Book Flights from USA to India", "url": "https://www.flyopedia.com/blog/"},
            {"name": "Airtripmasters — Cheapest Flights from USA to India 2026", "url": "https://www.airtripmasters.com/"},
            {"name": "Investment Guru India — Surge in airfares ahead of festive season (Thomas Cook India)", "url": "https://www.investmentguruindia.com/"},
            {"name": "Travel And Tour World — India aviation airspace crisis route changes", "url": "https://www.travelandtourworld.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37772239/pexels-photo-37772239.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Crowds move through a busy airport departure hall.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    try:
        wc = len(art["body"].split())
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
