#!/usr/bin/env python3
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

qatar_body = """Qatar has quietly halved one of the most important countdowns in an expatriate's life. Foreign residents whose residence permit is cancelled or expires must now leave the country within **14 days**, down from the 30 days the rule allowed for years. Miss the new deadline and the meter starts: **QR10 (roughly $2.75) per day** in overstay fines.

The change was disclosed by Captain Ali Ahmed Ali Al Kuwari of the Ministry of Interior's Airport Passports Department during a "Safe Travel" webinar in Doha on June 16, and reported across Gulf media days later. "Previously it was 30 days, but it is now two weeks," he said. Authorities have not said whether the cut is temporary or permanent, which makes the safe assumption the strict one.

### Why a fortnight is tighter than it sounds

For an Indian professional in Doha, a residence permit cancellation is rarely a standalone event. It usually arrives bundled with a job change, a termination, a company restructuring, or a family sponsorship ending. Each of those carries its own paperwork, and the new 14-day clock now runs alongside all of it.

Two weeks is barely enough time to settle an end-of-service gratuity, close a bank account, give notice on a flat, pull children out of school, ship belongings, and book flights home or to a new posting — all while a new employer races to transfer sponsorship before the window shuts. The 30-day buffer used to absorb administrative delays. The 14-day version does not.

### What it means for the Indian diaspora

Indians are among the largest expatriate communities in Qatar, heavily concentrated in construction, hospitality, healthcare, engineering, and the energy sector — exactly the industries where contracts end and sponsorships transfer most often. For NRI families in the tri-state area or the Bay Area with relatives working in Doha, this is the kind of rule that turns a phone call about a lost job into an emergency about a departure date.

The practical advice from immigration specialists is to stop treating permit cancellation as the start of a planning period and start treating it as a deadline that is already running. Anyone anticipating a job change should line up the sponsorship transfer, the exit logistics, and a backup flight *before* the cancellation is processed, not after.

Captain Al Kuwari also reminded visitors — including the many NRIs who fly into Doha on visit visas to see family — to check the exact stay duration printed on their visa sticker. Overstaying a **visit visa** carries a much steeper QR200 per day penalty. He urged everyone to verify their status through Qatar's **Metrash** app before travelling, since unpaid traffic fines, overstay charges, or travel bans can quietly block a departure at the airport.

### The wider Gulf pattern

Qatar's move does not stand alone. Across the Gulf, immigration authorities are tightening compliance and leaning harder on digital monitoring. The UAE is winding down a special overstay-fine exemption granted after this spring's airspace disruptions, with a final grace window closing on July 9. The direction of travel is unmistakable: shorter buffers, faster fines, and more enforcement automated through apps and e-gates.

For the diaspora, the takeaway is less about any single emirate and more about a habit. The era of assuming a comfortable month to wrap things up is ending. Keep documents current, keep the Metrash (or the equivalent national app) checked, and keep an exit plan ready — because in Doha, the grace period just got two weeks shorter.

**Sources:** Gulf Times via Dubai Standard; Curly Tales; VisasUpdate."""

uae_body = """The clock that has protected thousands of Indian residents in the UAE from overstay fines is about to stop. The Federal Authority for Identity, Citizenship, Customs and Ports Security (ICP) has announced a **final 30-day grace period**, running from **June 10 to July 9, 2026**, for people who benefited from the overstay-fine exemptions granted during this spring's regional airspace disruptions. After July 9, the protection ends.

This is the last off-ramp from a temporary relief scheme born of crisis. When airspace closures and flight suspensions tore through the region from February 28, the ICP waived overstay penalties for visa holders, people with cancelled residence visas who could not fly out, and those holding departure permits. With "regional stability restored and normal travel conditions resumed," as the ICP put it, that emergency cushion is being retired.

### What you actually have to do

The good news first: eligible individuals **do not need to file a fresh application** to use the grace period. The ICP has said the window applies automatically to those already covered by the earlier exemption.

The decision point is what to do inside the window. People who want to stay can use these 30 days to **regularise their status** — renew or transfer a residence visa, switch sponsorship, or sort out employment paperwork. People who plan to leave can **exit through standard procedures** without incurring the overstay fines that would otherwise have piled up.

What you cannot do is let July 9 slide past. Once the grace period closes, the normal fine regime resumes, and the conflict-era leniency that excused months of disruption will no longer apply. Daily overstay penalties in the UAE add up quickly, and a status that was being held harmless for months can turn into a mounting bill almost overnight.

### Why this matters to the Indian diaspora

Indians are the single largest expatriate group in the UAE, and the community sits at the center of this. Many were caught mid-transition when the airspace closed — a residence visa cancelled just as flights stopped, a job change frozen by a grounded route home, a family visit stretched into an accidental overstay by cancelled return tickets.

For NRI families in the US watching relatives in Dubai, Sharjah, or Abu Dhabi, the message to relay is simple and time-bound: if a UAE residence visa lapsed or a stay ran long because of the spring disruptions, **act before July 9**. After that date, the slate that was being held clean starts accumulating charges again.

### A region tightening at once

The UAE's deadline lands in the middle of a Gulf-wide compliance squeeze. Qatar has just cut its post-cancellation residency grace period from 30 days to 14, with daily fines for overstays. Across the region, immigration enforcement is increasingly automated — e-gates, status-check apps, and digital monitoring that flag an overstay the moment it happens.

Immigration advisers suggest UAE residents use these few weeks to do a full status check: confirm the residence visa is valid and correctly linked, clear any outstanding fines, and verify that passport details match official records. The tools are there — the ICP's smart services and apps let residents check and regularise status without a counter visit.

The exemption was an act of leniency during an extraordinary disruption. Its expiry is the UAE signalling a return to business as usual. For the hundreds of thousands of Indians who call the Emirates home, the next three weeks are the time to make sure their paperwork has caught up with that return to normal.

**Sources:** ICP via Madhyamam Online; Wego Travel Blog."""

navi_body = """Mumbai's relief valve is about to open to the world. **Navi Mumbai International Airport (NMIA)** will begin scheduled international passenger and cargo flights on **July 15, 2026**, the Adani-run airport has confirmed — and the first routes are pointed squarely at the destinations the Indian diaspora uses most: the Gulf.

NMIA opened to domestic traffic in December 2025 to ease the chronic congestion at Chhatrapati Shivaji Maharaj International Airport (CSMIA), which has long run near the limits of its single-runway, two-terminal setup. The international launch is the next phase. **IndiGo and Air India Express** are expected to lead the opening services, with the initial schedule focused on short-haul Gulf and Middle East routes, pending final regulatory sign-off. Customs has already inspected the airport's readiness; the remaining approvals are in process.

### Built for scale

NMIA is not a satellite strip. The airport is being developed to eventually handle up to **90 million passengers a year**, a capacity that would make it one of the largest in the world and finally give the Mumbai metropolitan region the dual-airport system that Delhi, with its new Noida airport, is also building toward. Phase one alone substantially expands the seats available out of greater Mumbai.

The Gulf-first strategy is deliberate. The Middle East corridor carries enormous year-round demand from the Indian workforce in the UAE, Qatar, Saudi Arabia, and beyond — the same community squeezed this year by Air India's international route cuts and high fares. Adding a second Mumbai gateway pumps fresh capacity into exactly the routes that have been most strained, and gives carriers room to grow without fighting for slots at an airport that has effectively been full for years.

### A new map for India's airports

NMIA's debut is part of a broader rewiring of how Indians fly. On June 17, Akasa Air launched the first direct service between Navi Mumbai and the new **Noida International Airport** near Delhi — the first time two of India's greenfield mega-hubs have been linked directly, without routing passengers back through the congested legacy terminals at CSMIA or Delhi's IGI.

https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Akasa_Air_737_max_8-200.jpg/1280px-Akasa_Air_737_max_8-200.jpg

That single route hints at the bigger shift: secondary hubs are starting to talk to each other directly, and the whole network is decongesting around the edges rather than forcing everything through the center.

### Why it matters to NRIs

For the diaspora, a new Mumbai gateway is more than an infrastructure headline. It promises shorter ground times, less of the crush that has made CSMIA a stressful first or last stop on a trip home, and — over time — more seat capacity and more competitive fares on the high-traffic Gulf and eventually long-haul routes.

There is a practical near-term catch worth flagging: NMIA sits on the eastern side of the metro region, closer to Navi Mumbai, Pune-side suburbs, and the new Atal Setu sea link, but farther from the western suburbs where many Mumbai families live. NRIs booking summer-and-beyond trips should check which airport their flight actually uses, since "Mumbai" will soon mean two very different drives. Ground links — including dedicated road and eventual metro connectivity — are being built out, but for now the airport choice will shape the airport-run on both ends of the journey.

The longer game is clear. As IndiGo and Air India Express plant their flags at NMIA and the airport scales toward its 90-million-passenger ambition, the diaspora's busiest gateway to India is finally getting a second front door. The first one opens July 15.

**Sources:** Outlook Traveller; Travel and Leisure Asia; Curly Tales; NomadLawyer."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Qatar Just Cut the Clock in Half: Expats Now Have 14 Days to Leave After a Permit Ends",
        "subheadline": "The Gulf state slashed its post-cancellation residency grace period from 30 days to two weeks, with daily fines after. For the large Indian workforce in Doha, a job change just became a sprint.",
        "slug": make_slug("qatar-residence-permit-grace-period-14-days-overstay-nri-workforce"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among Qatar's largest expat communities, concentrated in jobs where sponsorships end and transfer often — the 14-day window now leaves far less time to settle affairs after a permit is cancelled.",
        "tags": ["travel", "visa", "qatar", "gulf", "nri", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Dubai Standard (Gulf Times)", "url": "https://www.dubaistandard.com/qatar-has-reduced-the-post-cancellation-residency-grace-period-to-14-days/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/middle-east/travel/cancelled-residency-in-qatar-expats-now-get-just-days-before-fines-start/"},
            {"name": "VisasUpdate", "url": "https://www.visasupdate.com/post/qatar-residence-permit-grace-period-14-days-2026"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Hamad_Airport_terminal%2C_May_2014.jpg/1280px-Hamad_Airport_terminal%2C_May_2014.jpg",
        "image_caption": "The terminal at Hamad International Airport in Doha, Qatar's main gateway",
        "image_attribution": "Wikimedia Commons",
        "body": qatar_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The UAE's Overstay Amnesty Ends July 9 — Indian Residents Have One Last Window to Get Right",
        "subheadline": "A final 30-day grace period, running June 10 to July 9, closes the books on the fine waivers granted during this spring's airspace chaos. After that, the meter runs again.",
        "slug": make_slug("uae-final-30-day-grace-period-july-9-overstay-fine-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the UAE's largest expat group; many were caught mid-transition when airspace closed this spring, and the July 9 deadline is the last chance to regularise status or exit without the overstay fines piling back up.",
        "tags": ["travel", "visa", "uae", "dubai", "gulf", "nri", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Madhyamam Online (ICP)", "url": "https://madhyamamonline.com/middle-east/uae/uae-grants-final-30-day-visa-grace-period-after-flight-disruption-exemptions-1530114"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Dubai_International_Airport_interior_of_Terminal_3%2C_2019%2C_04.jpg/1280px-Dubai_International_Airport_interior_of_Terminal_3%2C_2019%2C_04.jpg",
        "image_caption": "Inside Terminal 3 at Dubai International Airport, the UAE's busiest gateway",
        "image_attribution": "Wikimedia Commons",
        "body": uae_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Mumbai Gets a Second Front Door: Navi Mumbai Airport Goes International on July 15, Starting With the Gulf",
        "subheadline": "IndiGo and Air India Express are set to launch the first international flights from India's newest mega-hub — and a fresh Navi Mumbai–Noida link shows how the country's airport map is being rewired.",
        "slug": make_slug("navi-mumbai-airport-international-july-15-gulf-nri-gateway"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "A second Mumbai gateway adds badly needed capacity on the Gulf routes the diaspora relies on, promises shorter ground times than congested CSMIA, and over time should mean more seats and more competitive fares home.",
        "tags": ["travel", "airlines", "airports", "mumbai", "nri", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/"},
            {"name": "NomadLawyer", "url": "https://nomadlawyer.org/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Navi_Mumbai_Airport.jpg/1280px-Navi_Mumbai_Airport.jpg",
        "image_caption": "Navi Mumbai International Airport, which opened to domestic flights in December 2025",
        "image_attribution": "Wikimedia Commons",
        "body": navi_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
