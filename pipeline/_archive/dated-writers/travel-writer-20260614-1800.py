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
        "headline": "Srinagar Airport Faces October Shutdown — and NRIs Planning Autumn Kashmir Trips Should Worry",
        "subheadline": "Chief Minister Omar Abdullah is lobbying Delhi to shorten or shift a 16-day runway closure that falls right in the peak October tourism window. A ₹1,677-crore expansion promises a fourfold capacity boost — but not before NRIs trying to book autumn flights get caught in the squeeze.",
        "slug": make_slug("srinagar-airport-october-shutdown-kashmir-autumn-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "October is when diaspora Kashmiris and NRI tourists flock to the Valley for autumn foliage and Durga Puja holidays — a full airport shutdown during this window could force costly reroutes through Jammu or road travel via the Jawahar Tunnel.",
        "tags": ["travel", "kashmir", "airports", "srinagar", "infrastructure", "omar-abdullah"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Kashmir Horizon", "url": "https://thekashmirhorizon.com/2026/06/13/cm-omar-takes-up-srinagar-airport-closure-issue-with-defence-civil-aviation-ministers-in-new-delhi/"},
            {"name": "JKNS - Jammu Kashmir News Service", "url": "https://jknewsservice.net/"},
            {"name": "IANS via hi INDiA", "url": "https://hiindia.com/"},
            {"name": "ANI / LatestLY", "url": "https://www.latestly.com/agency-news/business-news-cabinet-approves-expansion-of-srinagar-airport-to-71500-sqmt-from-existing-20659-sqmt-to-invest-rs-1677-crore-6671327.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Aru_Valley_Kashmir_in_Autumn.jpg/1280px-Aru_Valley_Kashmir_in_Autumn.jpg",
        "image_caption": "Aru Valley in Kashmir during the autumn season",
        "image_attribution": "Wikimedia Commons",
        "body": """If you're an NRI pencilling in a Kashmir trip this October, you may want to check the fine print. Srinagar International Airport — the Valley's sole commercial air link — is set to shut down entirely from October 1 to 16 for Phase III of a runway resurfacing project. And starting July 1, flights will stop on Mondays and Tuesdays as earlier phases of the same work continue.

Chief Minister Omar Abdullah spent last week in Delhi making the case that the timing couldn't be worse. In separate meetings with Defence Minister Rajnath Singh and Civil Aviation Minister Kinjarapu Rammohan Naidu, he urged either a shorter closure, a phased schedule, or a shift to a leaner travel window. His core argument: October is one of Kashmir's busiest tourism months, and a full shutdown would devastate the hospitality, transport, and handicraft sectors that thousands of Kashmiris depend on.

## The numbers tell the story

Srinagar Airport handled 4.47 million passengers in 2024-25, more than double its 2014-15 figure of 2.04 million. Traffic dipped to 3.38 million in 2025-26 following the Pahalgam incident, but autumn has historically been the recovery window — the season when the Valley's chinar trees, saffron fields, and Dal Lake shikaras draw visitors from across India and the diaspora.

Air services have already been curtailed since April when the resurfacing began. A complete October shutdown, Abdullah warned, could trigger "large-scale travel disruptions and cancellations."

## Awantipora as a backstop?

Abdullah proposed a workaround: operating limited civilian flights from Awantipora Air Base, about 33 kilometres south of Srinagar. It's not unprecedented. During similar runway closures in 1998 and 2010, civil flights ran out of Awantipora under a coordinated arrangement between the Defence and Civil Aviation ministries.

"We are working on possible alternatives to minimise the disruption and maintain a basic flight schedule, as was done in the past," the Chief Minister said.

He also met Railway Minister Ashwini Vaishnaw to push for more Vande Bharat trains between Jammu and Srinagar during the closure — a rail lifeline that's become increasingly viable since the Jammu-Srinagar Vande Bharat Express launched.

## The bigger picture: a ₹1,677 crore transformation

The runway work is part of a broader, Cabinet-approved overhaul worth ₹1,677 crore. When complete, Srinagar's terminal will expand from 20,659 square metres to 71,500 square metres. Peak-hour capacity will jump to 2,900 passengers, and annual throughput will reach 10 million — roughly quadruple today's actual traffic. The expanded apron will accommodate 15 aircraft, including one widebody bay, up from nine today. A 1,000-car multi-level parking facility is included.

The new terminal's design will blend Kashmiri woodwork and local craftsmanship with modern passenger processing — a nod to the Valley's heritage that AAI Director Javed Anjum highlighted at a pre-celebration of Yatri Suvidha Diwas on June 15.

## What NRIs should do

For diaspora Kashmiris who plan annual autumn pilgrimages home — and for the growing number of NRI families booking October trips for the foliage — the practical advice is straightforward: don't book refundable flights to Srinagar for early October yet. If the shutdown holds, the alternatives are a flight into Jammu followed by a six-hour road journey through the Jawahar Tunnel, or the Vande Bharat from Jammu — scenic but slow.

Watch for a resolution from Delhi in the coming weeks. If the 2010 Awantipora precedent is repeated, limited flights may continue. If it isn't, October in the Valley gets a lot harder to reach — right when the chinars are at their best."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe's New Biometric Border System Is Causing Four-Hour Queues — and Indian Travelers Are in the Thick of It",
        "subheadline": "The EU's Entry/Exit System went fully live in April and has already turned some of Europe's biggest airports into bottlenecks. With ETIAS coming later this year, here's what NRIs flying to the continent need to know.",
        "slug": make_slug("europe-ees-biometric-border-queues-indian-travelers"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs — whether traveling on Indian passports with Schengen visas or on US passports — are all subject to the new EES biometric registration, turning routine European arrivals into multi-hour ordeals during peak summer travel.",
        "tags": ["travel", "europe", "schengen", "visa", "ees", "etias", "airports"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Parade", "url": "https://parade.com/travel/ees-europe-border-system-tips"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"},
            {"name": "The Sun UK", "url": "https://www.thesun.co.uk/travel/"},
            {"name": "U.S. State Department via The Travel", "url": "https://www.thetravel.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Man_using_the_automatic_gate_in_Munich_airport_02.jpg/1280px-Man_using_the_automatic_gate_in_Munich_airport_02.jpg",
        "image_caption": "A traveler using an automated border gate at Munich Airport",
        "image_attribution": "Wikimedia Commons",
        "body": """If your summer Europe trip involves landing at Charles de Gaulle, brace yourself. The European Union's Entry/Exit System — EES for short — went fully operational on April 10, and the early returns are not encouraging. Paris CDG and Geneva have reported waits of up to four hours at immigration. Vienna, Brussels, Madrid, Barcelona, and Palma de Mallorca have seen three-hour delays. And summer hasn't even peaked yet.

For Indian travelers, the new regime adds a layer of bureaucratic friction to what was already one of the more documentation-heavy travel corridors in the world.

## What EES actually does

The system replaces the old passport-stamp model with digital biometric registration. Every non-EU traveler entering the Schengen Area now has their fingerprints and facial image scanned and logged in a centralised database. The system tracks entry and exit dates, monitors compliance with the 90-day-in-180-day rule, and flags overstays automatically.

Twenty-nine countries participate, covering the 25 EU Schengen members plus Iceland, Liechtenstein, Norway, and Switzerland. Ireland and Cyprus still use manual checks.

The idea is sound: a unified digital record eliminates stamping errors, catches visa violations, and speeds up repeat crossings. In practice, the rollout has been anything but smooth. Kiosks malfunction. Fingerprint scanners fail for roughly 30 percent of travelers, sending them to manual border control. First-time registrants face a gauntlet of questions about accommodation, return tickets, financial means, and medical insurance.

## The Indian passport wrinkle

NRIs on Indian passports already need a Schengen visa to enter Europe — a process that involves its own documentation marathon through VFS Global. The EES doesn't replace the visa requirement; it stacks on top of it. So an Indian passport holder arriving at Frankfurt now needs a valid Schengen visa, a completed EES biometric registration at the kiosk, and possibly a secondary interview at the border gate.

NRIs traveling on US passports are visa-exempt for short Schengen stays, but they're still subject to the full EES registration on their first trip after April 10. The biometric profile persists for three years, so repeat visitors should find subsequent entries faster — in theory.

## ETIAS is next

If EES is the stick, ETIAS is the paperwork. The European Travel Information and Authorisation System is expected to launch in Q4 2026, adding a pre-travel screening layer for visa-exempt travelers. US, UK, Canadian, Australian, and Japanese passport holders will need to apply online and receive authorization before boarding a flight to Europe. The fee is €7, and the authorization lasts three years.

For Indian passport holders, ETIAS doesn't apply directly — you already need a visa. But it signals a broader shift: Europe is building a layered digital border infrastructure where visa issuance, biometric tracking, and pre-arrival screening all feed into a single ecosystem. The Schengen Borders Code now evaluates applicants based on financial records, travel history, and return intent with increasing rigour, particularly for first-time applicants from India and other Asian countries.

## What NRIs should know before booking

The practical advice for summer 2026 is unglamorous but essential. Book connecting flights with at least a three-hour layover at your first Schengen port of entry — the EES queue comes before you can make a domestic connection within Europe. Carry printed proof of accommodation, return flights, and travel insurance; border agents are asking for them more consistently than before.

If you're entering through a smaller airport — Lisbon, Ljubljana, or Tallinn — the queues are significantly shorter than at the major hubs. Some countries, including Spain, France, and Greece, are temporarily relaxing enforcement during peak season to prevent tourism damage, but don't count on it.

Late-evening and early-morning arrivals see about 40 percent fewer disruptions than midday flights, when multiple long-haul services converge. And if you've already been registered in the EES database on a previous trip, your subsequent entries should be faster — the system recognises your biometric profile and skips the full registration.

Europe isn't getting harder to visit. It's getting more bureaucratic to enter. For NRIs who've navigated the Schengen visa gauntlet for years, the EES is one more hoop — but one that demands early planning, not last-minute optimism."""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
