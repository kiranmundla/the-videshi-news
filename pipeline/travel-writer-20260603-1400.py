#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-03 14:00 UTC run."""
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
    # ──────────────────────────────────────────────
    # ARTICLE 1: SAS Copenhagen-Mumbai nonstop
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "SAS Returns to India After 17 Years — Mumbai Gets a Nonstop to Copenhagen",
        "subheadline": "Scandinavian Airlines launched five-weekly A330 service on June 2, giving Nordic-based NRIs a direct lifeline to Mumbai and unlocking onward connections across Scandinavia.",
        "slug": make_slug("sas-copenhagen-mumbai-nonstop-india-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "An estimated 30,000 Indians live in Denmark and over 100,000 across the Nordic region — tech professionals, students, healthcare workers, and families who until now had to route through Dubai, Doha, or Frankfurt to reach home. SAS's return gives this diaspora a direct corridor to Mumbai.",
        "tags": ["travel", "airlines", "scandinavia", "copenhagen", "mumbai", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/sas-connects-india-and-denmark-launching-direct-flights-between-mumbai-and-copenhagen-revolutionizing-long-haul-travel-for-business-and-leisure-travelers-alike/"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airports-networks/50-new-routes-launching-june-2026"},
            {"name": "Scandinavian Airlines", "url": "https://www.flysas.com"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/91/Airbus_A330-343X%2C_Scandinavian_Airlines_-_SAS_AN0800442.jpg",
        "image_attribution": "Wikimedia Commons",
        "body": """For 17 years, Indian travellers headed to Scandinavia had no choice but to connect — through the Gulf hubs, through Frankfurt, through Istanbul. That era ended on June 2, when Scandinavian Airlines touched down in Mumbai with its first scheduled service to India since the late 2000s.

The new Copenhagen–Mumbai route operates five times a week on an Airbus A330-300, restoring direct connectivity between India and Denmark and creating only the second nonstop link between India and the Nordic region. Air India's Delhi–Copenhagen service, the sole survivor until now, had left Mumbai — India's financial capital and its largest source of outbound business travel — without a direct Scandinavian option.

## The schedule and what it means

SAS flight SK969 departs Copenhagen at 16:10 local time and lands in Mumbai at 04:30 the following day. The return, SK970, leaves Mumbai at 06:30 and arrives in Copenhagen at 12:15 — early enough for same-day connections across SAS's Scandinavian network.

That timing matters. Copenhagen is SAS's primary hub, and from there passengers can connect onward to Stockholm, Oslo, Helsinki, Gothenburg, and dozens of smaller Nordic cities, many within an hour's flight. For NRIs scattered across the Nordic region, this means a single-stop journey home instead of the two- or three-connection itineraries that Gulf routing often demands.

The service runs on Mondays, Wednesdays, Fridays, Saturdays, and Sundays from Mumbai, giving travellers flexibility around both weekend breaks and business schedules.

## Why this route, and why now

India's international aviation market has been reshuffled. IndiGo now commands roughly 17.6 per cent of India's international passenger share, Air India under Tata Group ownership is rapidly rebuilding its long-haul network, and Middle Eastern carriers — Emirates, Qatar Airways, Etihad — have seen their India market shares erode. European carriers that once ceded the India corridor to Gulf super-connectors are circling back.

SAS's move also reflects the arithmetic of India–Scandinavia demand. Denmark alone hosts over 30,000 Indian nationals, many in IT, life sciences, and shipping — industries where Copenhagen is a European nerve centre. Across the wider Nordic region, the Indian diaspora exceeds 100,000. Add students (Denmark's English-taught master's programmes pull thousands of Indians annually), visiting family traffic, and the growing corporate shuttle between Mumbai's financial district and Copenhagen's pharma-shipping-tech cluster, and the commercial case is clear.

SAS is now part of the SkyTeam alliance through its integration into the Lufthansa Group, which means NRIs booking through partner airlines — including Air France, KLM, and Delta — can earn and redeem miles on these flights, a practical advantage for frequent India–Europe travellers.

## What NRIs should know before booking

A few practical details matter. The A330-300 offers both SAS Business and SAS Go (economy) cabins, with the business product featuring a lie-flat bed and direct aisle access. Fares on the route are expected to be competitive with Gulf-carrier pricing on comparable origin-destination pairs, though early-stage availability may command a premium.

Travellers connecting onward within Scandinavia should note that SAS operates a single-terminal hub at Copenhagen Kastrup, so minimum connection times are typically 45–60 minutes for intra-Schengen flights. Since Denmark is within the Schengen zone, transit passengers heading to other Schengen destinations do not require an additional transit visa — a meaningful convenience given that Germany and France have both recently dropped airport transit visa requirements for Indian passport holders.

For NRIs in Sweden, Norway, and Finland who have long relied on circuitous Gulf routings, the Copenhagen hub now offers a geographically logical alternative. A Mumbai–Stockholm journey via Copenhagen takes roughly 12 hours gate-to-gate, compared with 14–16 hours through Dubai.

## The bigger picture

SAS's return to India is part of a broader European re-engagement with the Indian market. SWISS International Air Lines has announced Zurich–Bengaluru nonstops starting in October. Air India has added London–Bengaluru and expanded its Tokyo services. The European–Indian air corridor, once dominated by indirect Gulf connections, is being redrawn by carriers that see India not as a transit market to be captured, but as a destination worth serving directly.

For the 100,000-plus Indians across Scandinavia, June 2 marked something simpler: one fewer layover between their two homes."""
    },

    # ──────────────────────────────────────────────
    # ARTICLE 2: SWISS Zurich-Bengaluru nonstop
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "SWISS Launches Zurich–Bengaluru Nonstop — South India Gets Its First Direct Link to Switzerland",
        "subheadline": "Swiss International Air Lines will fly its new A350 to Bengaluru five times a week from October, connecting India's tech capital to Zurich and the wider Lufthansa Group network.",
        "slug": make_slug("swiss-zurich-bengaluru-nonstop-south-india"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bengaluru is India's largest tech talent hub and the source of tens of thousands of IT professionals who work with Swiss and European firms. The direct Zurich link cuts hours off Europe-bound business trips and gives South Indian NRIs a one-stop corridor to dozens of European cities via the Lufthansa Group network.",
        "tags": ["travel", "airlines", "switzerland", "bengaluru", "swiss", "europe", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/swiss-international-air-lines-launches-nonstop-flights-from-bengaluru-to-zurich/"},
            {"name": "EuropeSays", "url": "https://europesays.com/1755946/bengalureans-now-enjoy-direct-flights-from-bengaluru-to-zurich-with-swiss-international-air-lines-switzerland/"},
            {"name": "Aviation Source News", "url": "https://aviationsourcenews.com/airline/swiss-to-launch-first-ever-direct-flights-to-bengaluru-india/"},
            {"name": "Travel Turtle", "url": "https://travelturtle.world/swiss-expands-india-network-with-bengaluru-route-and-a350-rollout/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/82/SWISS_A350_WANDERLUST_ZURICH_AIRPORT_ZRH.jpg",
        "image_attribution": "Wikimedia Commons",
        "body": """Swiss International Air Lines has announced nonstop service between Zurich and Bengaluru starting October 26, 2026 — the airline's first-ever route to South India and its third Indian destination after Delhi and Mumbai. The service will operate five times a week on SWISS's newest Airbus A350, complete with the carrier's recently unveiled "SWISS Senses" cabin design.

For NRIs in South India, and for the vast population of tech professionals who shuttle between Bengaluru and European corporate offices, this is the route they have been asking for.

## Flight details and timing

Flight LX 140 departs Zurich at 13:20 and lands in Bengaluru at 02:55 the following day — roughly nine hours eastbound. The return, LX 141, leaves Bengaluru at 04:50 and touches down in Zurich at 10:50, making it possible to land in Switzerland before lunch and connect onward the same day.

The service will operate every day except Mondays and Wednesdays (eastbound) and Tuesdays and Thursdays (westbound), running through the winter schedule until March 27, 2027. Bookings opened on May 19 through SWISS's website and travel agency partners, with introductory fares starting from CHF 685 (approximately ₹64,000) round trip.

## Why Bengaluru matters

Bengaluru is not just India's IT capital — it is the city where European business meets Indian talent at scale. Major Swiss and German firms, from Novartis and Roche to Siemens and ABB, maintain significant operations in the city. The Lufthansa Group (of which SWISS is a member alongside Lufthansa and Austrian Airlines) already operates high-frequency services from Frankfurt and Munich to Delhi and Mumbai. Adding Bengaluru plugs a geographic gap that has forced South India-bound European travellers to backtrack through North Indian airports or connect via Gulf hubs.

SWISS CEO Jens Fehlinger framed the route explicitly: "India's Silicon Valley has a lot to offer both leisure and business travellers, and is also a perfect gateway for exploring Southern India. Our new Bengaluru service is particularly aimed at meeting the growing demand among the business community for direct flights to this major technology hub."

The numbers support him. Bengaluru's Kempegowda International Airport handled over 37 million passengers in the last fiscal year, with international traffic growing at 18 per cent annually. European traffic is among the fastest-growing segments.

## The A350 and the onboard experience

The Bengaluru route will be among the first to feature the SWISS Senses cabin product across all classes. The A350 offers fully flat business-class seats with direct aisle access, a refreshed premium economy cabin, and an economy section with wider seats and improved legroom compared to the airline's ageing A340 fleet. In-flight Wi-Fi and the latest entertainment system come standard.

SWISS plans to have five A350s in its fleet by the end of 2026, with the aircraft also serving Boston, Seoul, Johannesburg, and Shanghai.

## What NRIs should plan for

The Zurich hub is the gateway to Switzerland and, through the Lufthansa Group's Star Alliance connections, to nearly every European city. An NRI family in Bengaluru visiting relatives in Zurich, Geneva, Basel, Frankfurt, Munich, or Vienna can now build a single-ticket itinerary with one stop at most.

Visa logistics are also worth noting. Switzerland is a Schengen member, so a single Schengen visa covers transit through Zurich as well as visits to 28 other countries. For Indian passport holders who already hold a valid US visa, Germany and France have recently eliminated airport transit visa requirements — but Switzerland had never imposed one for direct ticketed connections in the first place, making Zurich an unusually friction-free European hub for Indian travellers.

Travellers should also know that SWISS participates in the Miles & More loyalty programme, shared across all Lufthansa Group carriers. Frequent flyers on Air India (a Star Alliance member) can earn and redeem miles on SWISS flights, adding practical value for NRIs who split their flying between Indian and European carriers.

## The broader trend

SWISS joins a queue of European airlines returning to or expanding in India. SAS Scandinavian Airlines launched Copenhagen–Mumbai nonstops on June 2. Air India has added London–Bengaluru and daily Tokyo services. The message from European carriers is unmistakable: India is no longer a market they are willing to serve only through Gulf intermediaries. Bengaluru, with its tech economy, its diaspora, and its growing airport, is now on the direct map."""
    },

    # ──────────────────────────────────────────────
    # ARTICLE 3: DigiYatra mandatory at 4 airports
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Made Face Scans Mandatory for International Transit — Here's What NRIs Need to Do",
        "subheadline": "DigiYatra's biometric system is no longer optional at Delhi, Mumbai, Bengaluru, and Hyderabad. International connecting passengers must now upload an Aadhaar-verified selfie 48 hours before departure.",
        "slug": make_slug("digiyatra-mandatory-international-transit-nri-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Delhi, Mumbai, Bengaluru, and Hyderabad are the four airports NRIs use most for international connections. The new mandatory policy means every NRI transiting through these hubs must now set up DigiYatra or face delays — a significant change from the opt-in system that most diaspora travellers have been ignoring.",
        "tags": ["travel", "airports", "digiyatra", "biometric", "india", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/india-makes-digiyatra-biometric-transit-mandatory-at-four-airports/"},
            {"name": "VisaHQ", "url": "https://www.visahq.com/india/"},
            {"name": "Ministry of Civil Aviation", "url": "https://www.civilaviation.gov.in"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/18/Inside_Terminal_3_at_Indira_Gandhi_International_Airport.JPG",
        "image_attribution": "Wikimedia Commons",
        "body": """India's Ministry of Civil Aviation has crossed a line that most NRIs have not noticed yet. From June 1, 2026, all international passengers connecting through Delhi, Mumbai, Bengaluru, and Hyderabad are required to use DigiYatra — the country's facial-recognition boarding system — to clear transit security. The system is no longer voluntary. If you are transiting through any of these four airports, your face is now your boarding pass, and there is no paper alternative.

The move is being described as a "hub-and-spoke pilot," which suggests it will expand further. The government's target is 27 airports by 2027.

## How it works

Under the new mandate, travellers must download the DigiYatra app and upload an Aadhaar-verified selfie along with their boarding passes at least 48 hours before departure. On arrival at one of the four designated airports, cameras at e-gates match the live facial image against the encrypted template stored in the DigiYatra cloud. If the match clears, the international-transfer corridor opens without any need to rescan a paper boarding pass or present physical documents at each checkpoint.

The Airports Authority of India estimates the biometric lane trims 12 to 18 minutes from typical transit times at Delhi's Terminal 3 — a meaningful saving at an airport where international connections routinely involve a security re-screen, a long walk between terminals, and at least one queue that seems designed to test patience.

## Why NRIs should care — now

Here is the issue most diaspora travellers have not reckoned with: DigiYatra requires Aadhaar authentication. That means an active Aadhaar number linked to your mobile number. For NRIs who left India years ago, whose Aadhaar may be dormant, whose Indian SIM is long deactivated, or who hold OCI cards but not Indian citizenship, this requirement creates a practical hurdle that needs to be sorted before the flight, not at the airport.

The four airports covered by the mandate — Delhi, Mumbai, Bengaluru, Hyderabad — handle the overwhelming majority of NRI international traffic. Almost every diaspora route from the US, UK, Canada, and the Gulf touches at least one of these hubs. If you are flying SFO–DEL–home-city, or JFK–BOM–hometown, this policy applies to you.

The Ministry has not yet published detailed guidance for OCI holders or foreign nationals transiting through India, and that ambiguity is itself a problem. The current DigiYatra enrolment flow assumes Indian citizenship and a working Aadhaar. Whether a workaround will be offered for non-citizen frequent transitors — a significant share of diaspora traffic — remains unclear.

## The privacy question

India's data-protection advocates have been raising flags about DigiYatra since its domestic launch in 2022. The government's position is that no passenger data is stored centrally: all biometric information is encrypted and held in the traveller's phone wallet, shared only with the departure airport, and purged within 24 hours of the flight.

That assurance has not convinced everyone. Unlike opt-in systems where privacy-conscious travellers could simply present a paper boarding pass, the mandatory rollout removes the alternative. For NRIs accustomed to TSA PreCheck and Global Entry in the United States — systems that also use biometrics but offer clear data-handling policies and congressional oversight — the opacity of DigiYatra's governance structure may be unsettling.

The DigiYatra Foundation, which manages the system, is a not-for-profit entity with the Airports Authority of India and private airport operators as shareholders. It is not directly subject to parliamentary scrutiny, and its data-retention policies have not been independently audited.

## What to do before your next India trip

For NRIs planning summer travel through any of the four airports, here is the practical checklist:

**Verify your Aadhaar status.** Log into the UIDAI portal (uidai.gov.in) and confirm your Aadhaar is active and linked to a working mobile number. If your Indian SIM is inactive, you may need to update your mobile number through an Aadhaar enrolment centre — which can only be done in person in India.

**Download the DigiYatra app.** Available on both iOS and Android. Registration requires your Aadhaar number and a live selfie.

**Upload your boarding pass early.** The system requires boarding pass data at least 48 hours before departure. Do not wait until airport check-in.

**Check with your airline.** Several carriers, including Air India and IndiGo, have begun sending DigiYatra reminders in their pre-flight communications. Follow their instructions.

**If you hold an OCI card**, monitor the Ministry of Civil Aviation's website for updated guidance. As of early June, no formal exemption or alternative pathway has been announced for non-Aadhaar holders.

## The bigger shift

The mandatory DigiYatra rollout is part of India's broader push to digitise every airport touchpoint. The country has already made the e-Arrival Card mandatory for all foreign nationals arriving in India, replacing the paper disembarkation form. The direction is clear: India wants its airports to run on facial recognition, digital documents, and minimal human interaction at checkpoints.

For NRIs, the practical implication is straightforward. Your next India trip requires slightly more preparation than it used to. The days of showing up with a boarding pass printout and breeze through on familiarity are ending. DigiYatra is here, it is mandatory, and your face is now the document that matters most."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Published: {art['headline'][:70]}...")
        print(f"   Slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
