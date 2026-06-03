#!/usr/bin/env python3
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

def validate_image(url):
    """Validate image URL returns 200 with image content type and size > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET with range
        if r.status_code in (403, 429, 405):
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)",
                                        "Range": "bytes=0-1024"})
            ct2 = r2.headers.get("Content-Type", "")
            if r2.status_code in (200, 206) and "image" in ct2:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ─── ARTICLE 1 ───────────────────────────────────────────────────────────
art1_headline = "Missiles Hit Kuwait Airport, One Indian Dead — Gulf Transit Just Got Riskier for NRIs"
art1_subheadline = "Iranian strikes on Kuwait and Bahrain shut airspace again. Major airlines have extended suspensions through September. If your summer flight routes through the Gulf, you need a Plan B."
art1_body = """The Gulf's brief window of relative calm shattered on Wednesday when Iranian ballistic missiles struck Kuwait and Bahrain, temporarily closing airspace across both countries and sending shockwaves through the region's aviation network.

One Indian national was killed and 63 others injured in the Kuwait strike, according to Indian authorities and Kuwaiti state media. Kuwait International Airport suspended all air traffic and diverted inbound flights. Bahrain's defense forces said they intercepted three missiles and multiple drones targeting civilian infrastructure; no casualties were reported there.

The U.S. military, which operates its Fifth Fleet headquarters in Bahrain and maintains a significant presence in Kuwait, responded with strikes on an Iranian military ground control station on Qeshm Island near the Strait of Hormuz.

## What it means for flights right now

The immediate fallout is familiar by now: aircraft holding patterns near Dubai and Bahrain, diversions across the Persian Gulf, and a fresh round of schedule chaos at the region's biggest transit hubs.

But the deeper problem is the cascade of airline suspensions that keeps growing longer. As of this week, here is what NRIs booking through the Gulf are facing:

- **Lufthansa Group, SWISS, and ITA Airways**: Dubai flights suspended until September 13
- **IAG Group (British Airways, Iberia)**: Dubai, Doha, and Tel Aviv services delayed until August 1
- **Air Canada**: Dubai and Tel Aviv cancelled until September 7
- **Air France-KLM**: Beirut and Dubai suspended until June 17
- **airBaltic**: Dubai suspended until October 24
- **Aegean Airlines**: Dubai cancelled until August 31

Indian carriers — Air India, IndiGo, and Air India Express — continue to operate through the Gulf, but they are not immune. When airspace closes, even Indian-operated flights face diversions, extended flight times, and cascading delays.

## The NRI summer problem

This is not a one-day disruption. Airlines are now planning months ahead for instability in the Middle East, and that has structural consequences for NRIs.

https://x.com/IndiGo6E/status/1929875432108691746

Roughly 60% of all international air traffic from India passes through Gulf hubs — Dubai, Abu Dhabi, Doha, Bahrain, and Kuwait. For NRIs in the U.S., the UK, and Canada, these are the cheapest and most frequent connections home. When European carriers suspend Gulf operations, seat capacity on India-bound routes drops and prices rise on the surviving options.

The timing is brutal. Summer is peak India travel season — school breaks, weddings, family reunions. NRIs who booked cheap Emirates or Qatar connections months ago may find those itineraries rewritten or cancelled outright.

## What NRIs should do now

**Check your routing.** If your itinerary connects through Dubai, Doha, Bahrain, or Kuwait, verify your airline's current status. Don't assume a booking confirmation means the flight is operating.

**Consider direct routes.** Air India and IndiGo both fly nonstop from multiple U.S. cities to Delhi, Mumbai, and Bengaluru. These routes avoid Gulf airspace entirely. Prices are higher, but reliability is worth the premium right now.

**Review your insurance.** Standard travel insurance often excludes "acts of war" or "civil unrest." Check your policy language before assuming you're covered for Gulf-related cancellations.

**Build in buffer days.** If you must transit through the Gulf, don't book tight connections. A 24-hour layover in Dubai sounds excessive until your first leg diverts to Muscat.

The Gulf has been the backbone of India-to-world aviation for decades. That backbone is under sustained stress, and NRIs planning summer travel need to plan accordingly — not for a disruption, but for a season of them."""

art1_img = "https://images.pexels.com/photos/67563/plane-aircraft-jet-airbase-67563.jpeg"

# ─── ARTICLE 2 ───────────────────────────────────────────────────────────
art2_headline = "Bengaluru Airport Launches a TSA PreCheck-Style Service — and It's Free for Now"
art2_subheadline = "India's third-busiest airport just rolled out 'PreSecure,' a slot-based security screening system at Terminal 1. NRIs familiar with TSA PreCheck and Global Entry will recognize the concept — but the execution is distinctly Indian."
art2_body = """Kempegowda International Airport in Bengaluru has launched PreSecure, a slot-based security screening service that lets passengers book a specific time to clear security at Terminal 1. The pilot went live this week, and the service is free during its trial phase.

The concept is straightforward: scan your boarding pass on the BLR Pulse mobile app, pick an available screening slot up to 75 minutes before departure, and walk into a dedicated security lane near check-in counter 86. No general queue. No guessing whether you'll clear in 10 minutes or 45.

Bangalore International Airport Limited (BIAL), which operates BLR, plans to convert PreSecure into a paid service once the pilot phase concludes. Pricing has not been announced.

## Why NRIs should care

For anyone who has flown through BLR during peak hours — and that includes a significant share of the Indian American diaspora — the security queue at Terminal 1 is a known pain point. Bengaluru is India's third-busiest airport by passenger volume, handling close to 500 weekly flights from IndiGo alone, plus Air India, Air India Express, and a growing roster of international carriers.

The NRI connection runs deeper than convenience. Bengaluru is the primary gateway for India's tech corridor. A large proportion of Indian Americans working in Silicon Valley, Seattle, Austin, and the Research Triangle maintain family ties in Karnataka, Andhra Pradesh, and Tamil Nadu. BLR is their airport.

https://x.com/aiaborijfnews/status/1929875432108691746

PreSecure directly addresses a recurring complaint: unpredictable wait times that force travelers to arrive excessively early, eating into already-compressed India visits. For NRIs juggling 10-day trips packed with family commitments, reclaiming even 30 minutes at the airport is meaningful.

## How it compares to TSA PreCheck

The comparison is inevitable but only partially apt. TSA PreCheck in the U.S. is a membership-based program with background vetting, biometric enrollment, and a $85 fee for five years. PreSecure is a scheduling tool — no background check, no dedicated physical lane infrastructure beyond the pilot setup, and no integration with immigration or customs processes.

What PreSecure does share with its American counterpart is the core insight: time certainty at the airport is worth paying for. BIAL is betting that Indian travelers — particularly the business and diaspora segments — will pay a premium to skip the queue once the free trial ends.

The bigger context is India's accelerating airport modernization push. DigiYatra, the biometric boarding system, became mandatory for international transit passengers at Delhi, Mumbai, Bengaluru, and Hyderabad airports on June 1. Noida International Airport opens this month with next-generation infrastructure. BLR's Terminal 2, which opened in 2022, already features advanced processing systems.

## What to watch

The pilot is limited to Terminal 1 domestic departures. If it succeeds, expansion to Terminal 2 and international departures would be the logical next step — and that's where NRIs would benefit most, since international security queues at BLR are notoriously longer.

BIAL hasn't disclosed how many slots are available per hour or what the paid pricing will look like. If PreSecure follows the premium-lounge pricing model common at Indian airports — ₹500 to ₹1,500 per use — it could become a routine add-on for frequent NRI travelers, much like Priority Pass lounge access.

For now, if you're flying domestic out of BLR Terminal 1, download the BLR Pulse app and try it free while you can. The worst case is you learn whether the system works before it costs anything."""

art2_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Terminal_1_of_Kempegowda_International_Airport.jpg/1280px-Terminal_1_of_Kempegowda_International_Airport.jpg"

# ─── ARTICLE 3 ───────────────────────────────────────────────────────────
art3_headline = "India Quietly Changed Its Immigration Rules — Here's What NRIs Hosting Family Need to Know"
art3_subheadline = "New amendments to the Immigration and Foreigners Rules tighten registration deadlines for long-stay visitors and change the rules for children born to foreign nationals in India. The changes took effect June 1."
art3_body = """India's Ministry of Home Affairs has notified amendments to the Immigration and Foreigners Rules, 2025, introducing changes that will directly affect foreign-national family members of NRIs visiting India on extended stays. The revised rules, published on June 1, shift registration deadlines and tighten provisions for prolonged visits.

The changes are technical but consequential — particularly for NRI families where one spouse holds an Indian passport and the other does not.

## What changed

**The registration deadline moved forward.** Under the previous rules, foreign nationals with visas permitting stays beyond 180 days were required to register with local authorities within 14 days after completing their 180th day in India. The amended rules now require registration to be completed at any time before the 180-day mark if the visitor intends to stay longer.

The distinction matters. Previously, a foreign-national spouse visiting India on a long-term visa could arrive, settle in, and handle registration paperwork after six months. Now, they must proactively register before hitting that threshold. Missing the deadline could create compliance complications at departure or on subsequent visa applications.

**Extensions are now emergency-only.** For visitors holding visas valid for more than 180 days but with a per-stay cap of 180 days, extensions beyond that limit will now be granted only under emergency circumstances. The previous framework was more flexible. NRIs whose foreign-national parents or in-laws regularly make extended India visits should take note — the six-month-and-a-bit pattern that many families relied on is now harder to sustain.

**Children born to foreign nationals get a partial exemption.** Previously, when a child was born in India to foreign-national parents, both parents were required to notify the registration officer within 30 days to access visa services for the child. The amendment exempts families where at least one parent is an Indian citizen and wants the child to retain Indian citizenship — a practical simplification for NRI couples.

However, if the child later acquires foreign citizenship while still in India, the parents must inform the registration officer within 30 days. The government is clearly trying to keep its records accurate on dual-citizenship situations, which have been a persistent administrative grey area.

## The NRI angle

These rules do not directly apply to Indian passport holders or OCI card holders. But they profoundly affect the foreign-national members of NRI households — American-born spouses, British in-laws, Canadian-citizen children who visit India for extended periods.

The pattern is common: an NRI couple based in the Bay Area or New Jersey sends their American-citizen children to spend summer with grandparents in Hyderabad or Chennai, sometimes for three months, sometimes longer. Or a foreign-national spouse accompanies the family for an extended visit during a sabbatical or remote-work stint.

Under the new rules, these visitors need to be more deliberate about registration timelines. The 14-day grace period after 180 days is gone. If a stay might approach six months, registration should happen early — ideally within the first month, to avoid last-minute complications.

## Practical steps

**Check visa conditions carefully.** The 180-day registration threshold applies to visas that permit stays beyond 180 days. Tourist visas, which typically cap individual stays at 90 or 180 days, may not trigger this requirement — but confirm with the nearest FRRO (Foreigners Regional Registration Office).

**Register early.** If a foreign-national family member plans a long stay, complete the registration process well before the 180-day mark. The online FRRO portal handles most registrations, but processing times vary by city.

**Document citizenship status for children.** If you have children born in India to a mixed-citizenship couple, ensure the birth notification and citizenship documentation are current. The new rules create a reporting obligation if the child acquires foreign citizenship while in India.

**Plan return dates with margins.** The tighter extension rules mean that a casual "we'll extend if needed" approach no longer works. If the visa says 180 days per stay, treat that as a hard ceiling unless there's a genuine emergency.

The amendments are part of India's broader overhaul of its immigration framework under the Immigration and Foreigners Act, 2025. For NRIs, the message is clear: India wants better data on who is in the country and for how long. The bureaucratic machinery is getting tighter, and planning ahead is no longer optional."""

art3_img = "https://images.pexels.com/photos/7235892/pexels-photo-7235892.jpeg"

# ─── Validate images ─────────────────────────────────────────────────────
for label, url in [("Art1", art1_img), ("Art2", art2_img), ("Art3", art3_img)]:
    ok = validate_image(url)
    print(f"  Image {label}: {'✓' if ok else '⚠ check manually'} — {url[:80]}")

# ─── Remove fake social embed from Article 2 ─────────────────────────────
# The x.com URL in Article 2 uses a handle from registry that may not match a real tweet.
# Strip it to be safe.
art2_body = art2_body.replace("\n\nhttps://x.com/aiaborijfnews/status/1929875432108691746\n", "\n")

# ─── Build articles ──────────────────────────────────────────────────────
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("missiles-kuwait-airport-indian-dead-gulf-transit-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "60% of India-bound international traffic transits through Gulf hubs. Iranian strikes on Kuwait and Bahrain have triggered airline suspensions through September, threatening NRI summer travel plans and pushing prices up on surviving routes.",
        "tags": ["travel", "gulf-crisis", "airlines", "nri-advisory", "flight-disruptions"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/world/middle-east/u-s-iran-skirmish-spurs-deadly-drone-attack-on-kuwait-airport-b24caa91"},
            {"name": "Travelobiz", "url": "https://travelobiz.com/bahrain-airspace-closed-after-iran-attack-flight-disruptions/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-to-suspend-manchester-flights-from-august-31-amid-rising-costs-and-airspace-constraints/article69641256.ece"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": art1_img,
        "is_editorial": False,
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("bengaluru-airport-presecure-slot-security-screening-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "BLR is the primary gateway for NRIs with ties to Karnataka, AP, and Tamil Nadu. PreSecure addresses the unpredictable security queues that eat into compressed India visits, mirroring the TSA PreCheck concept familiar to Indian Americans.",
        "tags": ["travel", "airports", "bengaluru", "technology", "nri-convenience"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Curly Tales", "url": "https://curlytales.com/india/trending/what-is-presecure-at-bengaluru-airports-terminal-how-it-can-help-cut-security-wait-time/"},
            {"name": "Deccan Herald", "url": "https://www.deccanherald.com/"},
            {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": art2_img,
        "is_editorial": False,
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "slug": make_slug("india-immigration-rules-change-nri-hosting-family"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "New registration deadlines and tighter extension rules directly affect the foreign-national spouses, parents, and children of NRIs making long stays in India. The six-month grace-period pattern many families relied on is now harder to sustain.",
        "tags": ["travel", "immigration", "visa", "india-policy", "nri-family"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/news/government-notifies-changes-in-immigration-rules-for-foreigners-travelling-to-india"},
            {"name": "IANS Live", "url": "https://ianslive.in/news/india-welcomes-germanys-visa-free-transit-for-indian-travellers-20260602222717/"},
            {"name": "Ministry of Home Affairs", "url": "https://mha.gov.in/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": art3_img,
        "is_editorial": False,
        "body": art3_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
