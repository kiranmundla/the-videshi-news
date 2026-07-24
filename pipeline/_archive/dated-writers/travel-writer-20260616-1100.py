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
    "headline": "Air India's First Lounge Outside India Lands at SFO — and It's Built for the Bay Area Diaspora",
    "subheadline": "The new Maharaja Lounge near SFO's A Gates is the airline's first overseas signature lounge, a quiet signal that North America is now central to its turnaround.",
    "slug": make_slug("air-india-maharaja-lounge-sfo-bay-area-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "San Francisco is one of the largest Air India gateways for the Bay Area's enormous Indian tech diaspora, and a dedicated premium lounge means a far more comfortable wait for the millions who fly the SFO-Delhi and SFO-Bengaluru corridors each year.",
    "tags": ["travel", "airlines", "air india", "sfo", "lounge"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Points Guy", "url": "https://thepointsguy.com/news/air-india-maharaja-lounge-sfo/"},
        {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/air-india-opens-1st-overseas-maharaja-lounge-at-san-francisco-airport/"},
        {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/about-us/press-release.html"}
    ]),
    "score_total": 78,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/San_Francisco_International_Airport_-_aerial_photo.jpg/1280px-San_Francisco_International_Airport_-_aerial_photo.jpg",
    "image_caption": "Aerial view of San Francisco International Airport, where Air India opened its first overseas Maharaja Lounge near the A Gates",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": """Air India has opened its first signature lounge outside India, and it is no accident that the location is San Francisco. The new Maharaja Lounge, which began welcoming guests on May 23, sits past security near the A Gates in SFO's International Terminal — the same terminal that funnels tens of thousands of Bay Area engineers, students, and families onto the long haul home each year.

For an airline still rebuilding its reputation under Tata ownership, the choice of SFO over London, Singapore, or New York says a great deal about where Air India sees its future passengers.

## What the lounge actually offers

The space spans roughly 3,300 square feet — modest next to the 16,000-square-foot flagship Maharaja Lounge that opened at Delhi's Terminal 3 in February, but generous by the standards of a single overseas gateway. Designed by the global hospitality firm Hirsch Bedner Associates, it blends contemporary luxury with Indian craft motifs, the same design language Air India has rolled out across its refreshed cabins.

Access is reserved for First and Business Class passengers and for Platinum and Gold members of the airline's loyalty programme, along with eligible Star Alliance Gold members. The lounge is expected to operate daily from roughly 6:30 a.m. to 10 p.m., though hours flex with the flight schedule. To reach it, travelers clear security, turn left, walk past the Air France lounge, and take the escalators up one level.

## Why San Francisco came first

Air India currently runs around 65 weekly flights between North America and India, and CEO Campbell Wilson has repeatedly called the region a "critical pillar" of the airline's global network. The Bay Area is the densest knot in that network. SFO connects to both Delhi and Bengaluru, and Bengaluru in particular is the airline's bridge to the Silicon Valley-to-Silicon Plateau tech corridor that defines so much diaspora travel.

That makes the lounge less a vanity project and more a competitive necessity. Until now, premium Air India passengers at SFO used contract lounges shared with other carriers. A branded, Indian-hospitality space gives the airline a way to hold onto the high-margin business and first-class travelers it most needs to win back — many of whom defected to Emirates, Qatar Airways, and United during the airline's lean years.

## What it means for the Bay Area diaspora

For the region's Indian community — among the largest and highest-earning in the United States — the practical upside is straightforward. Anyone flying Air India business class on the roughly 15-hour SFO-Delhi or SFO-Bengaluru runs now has a dedicated place to eat, work, and rest before boarding, rather than a crowded shared lounge or a terminal seat.

There is a longer game here too. The Maharaja Lounge is the second signature lounge Air India has opened in 2026, after Delhi, and it represents the airline's first international lounge launch since the Tata Group took over in January 2022. If SFO performs, expect similar lounges to follow at other heavy diaspora gateways such as Newark, New York JFK, and Chicago — cities with their own large Gujarati, Punjabi, and South Indian populations who fly these routes for weddings, elder care, and the annual trip home.

## The caveat

The lounge arrives at an awkward moment. Air India has spent the early summer trimming flights on some North American, European, and Australian routes, citing high fuel costs, a weak rupee, and the longer flight paths forced by closed Pakistani airspace and regional conflict. A polished lounge does not undo a thinner schedule, and travelers chasing the cheapest SFO-India fare may still find better frequency and timing on a Gulf carrier with a Dubai or Doha stop.

Still, for the segment Air India most wants — premium flyers who would rather fly nonstop on the national carrier than connect through the Gulf — the SFO Maharaja Lounge is a tangible improvement, and a clear signal that the airline is investing in the diaspora's home airport first.

## The bottom line

If you fly Air India business class out of SFO, the new Maharaja Lounge is now part of your journey. If you fly economy, it is a sign of where the airline is putting its money — and a reason to watch for cabin and service upgrades on the Bay Area routes in the months ahead."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "Europe's New Biometric Border Is Fully Live — Here's What NRIs Flying Through Schengen Need to Know",
    "subheadline": "Fingerprint and face scans have replaced the passport stamp across 29 European countries, and the early summer rollout has meant hours-long queues. A practical guide for the India-via-Europe traveler.",
    "slug": make_slug("eu-ees-biometric-border-schengen-nri-guide"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "Frankfurt, Paris, Amsterdam, and Zurich are among the most common one-stop layovers for NRIs flying between North America and India, and the new biometric entry system can add long waits and missed connections for anyone who does not understand how it works.",
    "tags": ["travel", "visa", "europe", "schengen", "ees"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "European Commission, Migration and Home Affairs", "url": "https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/smart-borders/entry-exit-system_en"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/travel/2026/06/why-travelers-waiting-hours-enter-europe/"},
        {"name": "The Times", "url": "https://www.thetimes.com/travel/ees-entry-exit-system-eu-border-checks/"}
    ]),
    "score_total": 80,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An open passport at an international border, where biometric scans now replace stamps across the Schengen Area",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": """If your trip between the United States and India runs through a European hub — and for a huge share of NRIs it does — your layover just changed. The European Union's Entry/Exit System, or EES, is now fully operational across the Schengen Area, replacing the old ink passport stamp with fingerprint and facial scans for every non-EU traveler on a short stay.

The system finished its phased rollout on April 10, 2026, after launching gradually from October 2025. The transition has not been smooth: travelers this summer have reported waits of up to several hours at busy airports in Italy, Portugal, and Spain, and some have missed connections. For anyone connecting through Europe on the way to Delhi, Mumbai, or Bengaluru, understanding the new process is now part of trip planning.

## What EES actually is

EES is a centralized biometric database. The first time you enter the Schengen Area after the system went live, border officials register your facial image, fingerprints, and passport data. On entry and exit, the system records the crossing digitally instead of stamping your passport. The goal is to automatically track the 90-days-in-any-180 short-stay rule and flag overstays.

It applies in 25 of the 27 EU member states — Ireland and Cyprus still stamp manually — plus Iceland, Liechtenstein, Norway, and Switzerland. Since October, the system has logged roughly 90 million crossings and refused entry to about 40,000 people.

## Does it affect you if you are only connecting?

This is the question that matters most for NRIs, and the answer depends on the airport. If you stay airside — landing at Frankfurt or Paris and connecting to another flight without passing immigration — you generally are not registered. But many itineraries do require you to clear immigration: if you change terminals, have a long layover, or your bags are not checked through, you may be funneled to the EES kiosks.

The safest assumption is that on any Schengen connection long enough to leave the secure transit zone, you will go through biometric registration the first time. Build in extra buffer — two to three hours on a connection that used to take one — especially this summer while staff and kiosks are still catching up.

## What the kiosk process looks like

At a typical EES kiosk you select a language, scan your passport, have your photo taken, and provide fingerprints. You may be asked a few questions: proof of accommodation, whether you have a return ticket, citizenship status, and whether you have funds and medical insurance for the trip. Registration itself takes a few minutes. The bottleneck is the queue behind it — and early reports note that fingerprint readers fail for a meaningful share of travelers, who are then sent to a human officer.

One reassurance from EU-LISA, the agency running EES: there is no legal requirement to hold a return ticket. You must be able to show you will leave within the permitted window, but a return flight is only one of several acceptable proofs alongside financial means or family ties.

## EES is not ETIAS — know the difference

These two systems are easy to confuse. EES tracks your entries and exits with biometrics. ETIAS, the European Travel Information and Authorisation System, is a separate pre-travel permit for visa-exempt nationalities, expected to roll out later. It costs roughly 7 euros and must be obtained before boarding.

Crucially, most Indian passport holders still need a full Schengen visa, so ETIAS does not apply to them — but it does apply to NRIs traveling on a US, UK, Canadian, or other visa-exempt passport. If you carry a Western passport, watch for ETIAS launch dates; if you travel on an Indian passport, your Schengen visa process is unchanged, and the favorable two-year and five-year multiple-entry "cascade" visas remain available to frequent travelers with a clean record.

## The practical takeaway

Three rules for the India-via-Europe traveler this summer. First, pad your layover — assume the connection takes longer than the schedule suggests. First-time registration is the slow part, so once you are in the system, future trips speed up. Second, keep your documents handy: accommodation, onward ticket, and insurance details ready to show. Third, know which passport you are traveling on, because it determines whether you need a Schengen visa, an ETIAS permit, or neither. Get those straight before you book, and Europe's new digital border becomes a minor speed bump rather than a missed flight home."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "Two Indian Airports Just Made a Global 'Most Beautiful' List — and One Is the New Mumbai Gateway NRIs Will Soon Use",
    "subheadline": "Navi Mumbai International and Guwahati's Terminal 2 earned spots in the Prix Versailles 2026 design listing, a sign that India's airport boom is now about more than raw capacity.",
    "slug": make_slug("navi-mumbai-guwahati-airports-prix-versailles-design-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "Navi Mumbai International Airport is set to handle international flights and ease the crush at Mumbai's overloaded main airport — the single busiest entry point for the western Indian diaspora returning from the US, UK, and the Gulf.",
    "tags": ["travel", "airports", "india", "navi mumbai", "infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/adani-airport-holdings-prix-versailles-2026/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/navi-mumbai-international-airport-begins-commercial-flight-operations/"}
    ]),
    "score_total": 70,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
    "image_caption": "Navi Mumbai International Airport, recognized in the Prix Versailles 2026 listing of the world's most striking airport designs",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": """For years the story of Indian aviation was a story of numbers: more passengers, more aircraft orders, more runways. This week brought a different kind of recognition. Two Indian airports — Navi Mumbai International and Terminal 2 of Guwahati's Lokpriya Gopinath Bordoloi International — were named in the Prix Versailles 2026 listing of the world's most architecturally striking airports, putting India alongside design showcases in Guangzhou, Frankfurt, Pittsburgh, and San Diego.

Presented at UNESCO headquarters in Paris each year since 2015, the Prix Versailles honors terminals that pair architectural ambition with environmental awareness and passenger-focused design. For the Indian diaspora, the more interesting half of the news is not the prize. It is which airport won it.

## The new Mumbai gateway

Navi Mumbai International Airport, built and run by Adani Airports, opened to commercial flights on December 25, 2025, after years of delays. It is India's newest greenfield airport and was conceived to do one thing the existing Chhatrapati Shivaji Maharaj International Airport simply cannot: grow. Mumbai's main airport is hemmed in by the city and has no room for a parallel runway, which is part of why it lost its position as India's busiest airport to Delhi.

Navi Mumbai is being built in five phases. When complete, it is designed to handle 90 million passengers a year, with dedicated cargo terminals and multimodal connectivity. The first phase alone cost roughly 19,650 crore rupees, and the airport was inaugurated by Prime Minister Narendra Modi in October 2025.

For now the operation is deliberately modest — domestic flights from IndiGo, Air India Express, Akasa Air, and Star Air, running on a 12-hour schedule that has been scaling up through 2026. But officials have confirmed the airport is built for international flights, and that is what makes it matter to NRIs.

## Why this matters to the diaspora

Mumbai is the front door for the western Indian diaspora. Gujaratis, Maharashtrians, and Konkani families across the US, UK, and the Gulf route through it for weddings, elder care, and the long-delayed trip home. For decades that has meant funneling through a single congested airport, often at 2 a.m., into immigration halls that strain under the load.

A second major airport changes the geometry. As Navi Mumbai ramps up international service, it will give travelers a less crowded alternative, spread arrival and departure traffic across two facilities, and — because it sits on the Navi Mumbai side of the metro — cut ground travel time for families living in Pune-corridor suburbs and the eastern reaches of the metropolitan region.

The design recognition is a useful tell here. An airport built to win architecture prizes is an airport built for the long haul, with the passenger-flow planning and capacity headroom that the older terminal never had. Prime Minister Modi has framed Navi Mumbai as a project that will establish the Mumbai region as "Asia's largest connectivity hub."

## The Guwahati piece

The second honoree, Guwahati's Terminal 2, points to a quieter trend: India's airport boom is no longer confined to the big metros. The Northeast has a substantial diaspora of its own, and a design-forward terminal in Guwahati signals that tier-two gateways are getting the same investment in passenger experience that until recently was reserved for Delhi, Mumbai, and Bengaluru.

## What to watch

The practical question for NRIs is timing: when will Navi Mumbai actually carry international flights, and which carriers and routes will use it? Akasa Air has already flagged plans to scale toward 50 international weekly departures from the airport, focused on the Middle East and Southeast Asia — the very markets the western diaspora uses most. Air India Express and IndiGo's growing international networks are the other ones to watch.

The recognition this week is, in the end, a marker of intent. India is no longer just adding airport capacity; it is building airports it wants the world to admire. For the diaspora that passes through them twice a year or more, that ambition is about to translate into a real, second option for flying into Mumbai."""
}
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
