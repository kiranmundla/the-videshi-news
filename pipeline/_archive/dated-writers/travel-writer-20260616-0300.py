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
        "headline": "Gulf Airspace Turmoil Is Snarling NRI Flights Home — and the Layover You Booked May Not Be Safe",
        "subheadline": "Etihad's free 15-day insurance and Emirates' \"Fly You Home\" pledge signal how fragile the Dubai and Abu Dhabi transit hubs have become for the millions of Indians who route through them.",
        "slug": make_slug("gulf-airspace-disruption-nri-dubai-abu-dhabi-transit"),
        "category": "travel",
        "vertical": "diaspora-safety",
        "diaspora_angle": "The Gulf hubs of Dubai, Abu Dhabi, and Doha are the default connecting points for most NRIs flying between North America and India, so airspace closures and insurance gaps directly threaten the cheapest and most common route home.",
        "tags": ["travel", "airlines", "middle-east", "advisory", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Gulf travel risk disruption", "url": "https://www.travelandtourworld.com/news/article/pih7ddujykwo/"},
            {"name": "Travel And Tour World — IndiGo Gulf advisory", "url": "https://www.travelandtourworld.com/news/article/"},
            {"name": "The Indian Eye — multi-nation transit routes", "url": "https://theindianeye.com/2026/03/24/govt-activates-multi-nation-transit-routes-to-repatriate-indians-amid-w-asia-airspace-closures/"}
        ]),
        "score_total": 85,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Zayed_International_Airport_-_02.jpg/1280px-Zayed_International_Airport_-_02.jpg",
        "image_caption": "The terminal at Abu Dhabi's Zayed International Airport, one of the Gulf transit hubs most NRIs route through.",
        "image_attribution": "Wikimedia Commons",
        "body": """If you are flying between the United States and India this summer, look closely at where your itinerary connects. The odds are high that it routes through Dubai, Abu Dhabi, or Doha — the three Gulf hubs that funnel the bulk of diaspora traffic between North America and the subcontinent. And right now, those hubs are operating under a level of uncertainty that should change how you book.

A wave of airspace restrictions tied to renewed conflict across West Asia has rippled through the region's aviation network. On one recent day, carriers across Asia and the Middle East logged more than 5,300 delays and 477 cancellations, with major gateways in the UAE, Saudi Arabia, Oman, and India all reporting operational strain. IndiGo issued an urgent travel advisory warning passengers on Gulf corridors to monitor schedules closely and prepare for last-minute route changes.

## What the airlines are actually doing

The most telling sign is what the Gulf carriers themselves have rolled out. Etihad Airways has launched free 15-day medical travel insurance, automatically covering eligible passengers — a direct response to the fact that some standard travel-insurance policies now carry exclusions for high-risk regions. Emirates went further, building a "Fly You Home" repatriation pledge that promises to return stranded passengers, including on partner airlines if necessary.

Read between the lines and the message is clear: the airlines are stepping into roles normally filled by insurers and governments because passenger confidence has cracked. UAE hotel occupancy has reportedly slid to around 33% nationally, well below the levels typical of a strong tourism cycle, as long-haul leisure travelers reconsider stopovers in Dubai and Abu Dhabi.

## Why this hits NRIs harder than most

For the Indian diaspora, the Gulf is not an optional detour — it is the backbone of affordable travel home. Emirates, Etihad, and Qatar Airways have spent two decades undercutting nonstop fares on the India–US and India–UK runs by routing through their hubs. A family of four flying San Jose to Hyderabad or New Jersey to Kochi very often saves hundreds of dollars by connecting in the Gulf rather than paying for an Air India or United nonstop.

That savings now comes with a question mark. India ranks as the single highest-volume passenger market exposed to this disruption, and the combination of price sensitivity and transit risk puts diaspora travelers squarely in the crosshairs. The Indian government has already activated multi-nation transit routes to help repatriate citizens caught by West Asian airspace closures — a reminder of how quickly a routine layover can turn into a stranded one.

## What to do before you book

The practical steps are not complicated, but they matter more than usual this season:

- **Buy travel insurance before booking flights, and read the exclusions.** Confirm in writing that your policy covers transit through the UAE and Qatar. If it does not, the airline-provided coverage from Etihad or Emirates may be your only safety net.
- **Avoid non-refundable fares while advisories remain fluid.** A slightly higher flexible fare is cheaper than a forfeited ticket if your connection is cancelled.
- **Monitor airline notifications directly.** Make sure the mobile number on your booking is current — carriers are pushing rebooking options to registered numbers first.
- **Consider an alternate hub if your risk appetite is low.** Routing through Europe (Frankfurt, Munich, London) or via East Asia adds time but sidesteps the Gulf entirely. Fares there have softened relative to other corridors.
- **Enroll in your government's traveler alert program** — STEP for US citizens, the MEA's portal for Indian nationals — for real-time updates while abroad.

## The bigger picture

None of this means the Gulf hubs are shutting down. Flights continue across most of the region, and Dubai and Abu Dhabi remain among the busiest transit points on earth. But the risk has shifted from theoretical to financial: insurance gaps, rerouting fuel surcharges, and the possibility of a cancelled connecting leg are now part of the calculus.

For NRIs who have long treated a Gulf layover as the obvious, frictionless way to get home, this summer calls for a little more homework than usual. The cheapest fare on the screen is not always the cheapest fare you actually pay — especially when the route runs through contested airspace."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Rewrote Its Visa Rulebook — and the Changes Quietly Favor OCI Families and NRI Spouses",
        "subheadline": "Delhi has collapsed 26 visa categories into 21, extended business and employment visas to 10 years, and is letting people of Indian origin work and study without switching visa types. Here's what it means for diaspora families.",
        "slug": make_slug("india-visa-overhaul-oci-nri-spouses-categories-streamlined"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Many NRI families travel with foreign-passport spouses, children, and OCI cardholders, and the new rules let people of Indian origin take up work, study, or business in India without converting their visa — removing a long-standing bureaucratic headache.",
        "tags": ["travel", "visa", "immigration", "oci", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — Visa Processes and Categories Streamlined", "url": "https://www.fragomen.com/insights/visa-processes-and-categories-to-be-further-streamlined.html"},
            {"name": "Fragomen — Immigration Policies Further Relaxed", "url": "https://www.fragomen.com/insights/immigration-policies-further-relaxed.html"},
            {"name": "Press Information Bureau — Ministry of Home Affairs", "url": "https://pib.gov.in/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Immigration_at_IGIA.JPG/1280px-Immigration_at_IGIA.JPG",
        "image_caption": "Immigration counters at Indira Gandhi International Airport in New Delhi.",
        "image_attribution": "Wikimedia Commons",
        "body": """India's Ministry of Home Affairs has spent the past year steadily rebuilding the machinery that governs how foreigners — including foreign-passport members of NRI families — enter and stay in the country. The latest round of changes consolidates the visa system and, more importantly for the diaspora, relaxes several rules that have long frustrated mixed-nationality households.

The headline number: India's main visa categories have been collapsed from 26 down to 21, with sub-categories cut from 104 to roughly 65. The Project Visa now sits under the Employment Visa; the Intern and Research visas have folded into the Student Visa family. On its own, that is bureaucratic housekeeping. But bundled with it are several substantive relaxations that directly touch diaspora life.

## The change that matters most for OCI and PIO families

The single most consequential update: persons of Indian origin, along with the spouses and children of Indian nationals, will be able to take up employment, business, study, or research opportunities **without converting their visa to the matching category**.

For anyone in a mixed-nationality marriage, this removes a recurring headache. Until now, a foreign-passport spouse who arrived on an entry or dependent visa and then wanted to take a job, enroll in a course, or start a business typically had to navigate a visa conversion — a process that meant paperwork, delays, and sometimes a trip back to a consulate abroad. The new framework lets families of Indian origin move between those activities far more freely.

This dovetails with the OCI (Overseas Citizen of India) regime, under which roughly 50 lakh cards have already been issued and the application portal has been revamped for easier service. OCI holders were already exempt from most visa requirements; the new rules smooth the path for the foreign-national relatives who travel alongside them but do not hold an OCI card.

## Longer visas, fewer return trips

Two other relaxations stand out for diaspora professionals and entrepreneurs who split time between India and the West:

- **Employment and business visas can now be extended for up to 10 years**, double the previous five-year ceiling. Crucially, holders no longer need to fly back to their home country to apply for a fresh visa after five years — extensions can be done from within India.
- **Two new electronic visa sub-categories** — e-Conference and e-Medical Attendant — have been added, so relatives accompanying a medical-visa patient and delegates at government-sponsored conferences can now apply online instead of queuing at a consulate.
- **The minimum salary threshold for interns has been cut by more than half**, to ₹3,60,000 a year, making it easier for companies to bring on younger diaspora talent.

## Faster issuance, smarter borders

The administrative backbone is being modernized in parallel. The Cabinet has extended the Immigration, Visa, Foreigners Registration & Tracking (IVFRT) scheme through 2031 with an ₹1,800 crore budget. Average visa issuance has dropped from several weeks to under a day for complete applications. The number of immigration check posts has grown from 82 to 114, and the Fast-Track Immigration–Trusted Traveller Program now clears pre-verified travelers in about a minute at eight major airports, including Delhi, Mumbai, Bengaluru, Chennai, and Hyderabad — with Kozhikode, Thiruvananthapuram, Amritsar, and others next in line.

## What NRIs should actually do

A few practical takeaways:

- **If you have a foreign-passport spouse or child**, the conversion barrier to work or study in India has eased. Confirm the current rules with an Indian consulate before assuming the change applies to your exact situation — the MHA has indicated detailed guidelines are still rolling out.
- **If you hold a long-term business or employment visa**, ask about the 10-year extension at your next renewal rather than restarting the process from scratch abroad.
- **If you travel frequently**, the Trusted Traveller fast-track lane is worth enrolling in now, especially as it expands to more airports.

India has spent years signaling that it wants to make legitimate travel and work easier while tightening security tracking — the IVFRT extension funds exactly that dual goal. For diaspora families who have spent too many hours in consulate waiting rooms, the latest rewrite is a quiet but real win."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "AirAsia's New Kuala Lumpur Bridge Makes Angkor Wat a One-Ticket Trip for Indian Travelers",
        "subheadline": "A four-country aviation-tourism pact uses AirAsia's Fly-Thru system to route Indian flyers to Cambodia via Kuala Lumpur — no separate bookings, no immigration stop, no baggage re-check at the layover.",
        "slug": make_slug("airasia-kuala-lumpur-cambodia-fly-thru-indian-travelers"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "Affordable, low-friction Southeast Asia trips are a favorite for NRI families on India visits, and a single-ticket corridor to Cambodia through Kuala Lumpur makes Angkor Wat a realistic add-on without the usual multi-booking hassle.",
        "tags": ["travel", "airlines", "southeast-asia", "cambodia", "nri"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Travel And Tour World — AirAsia aviation-tourism pact", "url": "https://www.travelandtourworld.com/news/article/ndmx0ho5ttt2/"},
            {"name": "AirAsia Fly-Thru — official", "url": "https://www.airasia.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Angkor_Wat_Sunrise_%28209237385%29.jpeg/1280px-Angkor_Wat_Sunrise_%28209237385%29.jpeg",
        "image_caption": "Sunrise over Angkor Wat in Siem Reap, Cambodia — newly easier to reach from India via Kuala Lumpur.",
        "image_attribution": "Wikimedia Commons",
        "body": """For NRI families who structure a trip home to India around a short, affordable getaway nearby, Southeast Asia has always been the sweet spot — close enough for a long weekend, cheap enough to justify, and rich enough to feel like a real holiday. A new four-country partnership just added Cambodia to that shortlist, and it did so by attacking the one thing that usually keeps the country off the itinerary: the hassle of getting there.

Cambodia, India, Australia, and Malaysia have linked up in an aviation-tourism pact led by AirAsia and the Cambodia Tourism Board. The mechanism at its heart is AirAsia's Fly-Thru system, routed through Kuala Lumpur. The promise is simple but meaningful: a single ticket from an Indian city to Cambodia, with baggage checked straight through to the final destination and no need to clear immigration during the Kuala Lumpur layover.

## Why connectivity, not interest, has been the barrier

Cambodia has never lacked appeal. Angkor Wat — the largest religious monument on earth, and a Hindu-Buddhist temple complex with deep resonance for Indian travelers — is one of Asia's signature sights. Siem Reap, Phnom Penh, and the country's emerging coastal towns round out a genuinely rich destination.

What it has lacked is direct, frictionless access. Long-haul routes into Cambodia remain limited compared with regional rivals like Thailand and Vietnam, so reaching it has typically meant cobbling together separate bookings, re-checking baggage at a transit point, and sometimes clearing immigration mid-journey. For a family weighing a quick Southeast Asia add-on, that friction is often enough to pick somewhere easier. The Fly-Thru model is designed to erase exactly that calculation.

## What it means for the Indian traveler

India is one of the two primary target markets in the campaign — the other being Australia — and the strategy is explicitly built around how Indian flyers actually behave. India's outbound travel has surged on the back of rising middle-class incomes and a growing appetite for short-haul international trips, and Southeast Asia is the natural beneficiary. AirAsia already connects a broad set of Indian cities, primary and secondary, into its network, which means the Kuala Lumpur bridge can pull travelers from well beyond just Delhi and Mumbai.

For the diaspora specifically, the appeal is the same one that makes these trips popular in the first place: you are often already in India visiting family, with the hardest and most expensive leg — the transcontinental flight — already behind you. From there, a single-ticket hop to Angkor Wat via Kuala Lumpur is a far easier sell than a multi-booking puzzle. Cambodia is positioned as both affordable and culturally substantial, which is precisely the combination that converts a vague "we should go someday" into an actual booking.

## The fine print to keep in mind

A few realities are worth flagging:

- **This is a marketing and connectivity push, not a fare guarantee.** The partnership is backed by a relatively modest US$100,000 joint campaign focused on digital promotion, travel-trade exhibitions, and influencer familiarization trips. The structural win is the Fly-Thru routing; deals will come through AirAsia's usual promotional cycles.
- **Check visa requirements for Cambodia separately.** Indian passport holders generally need a visa for Cambodia, available as an e-visa or visa-on-arrival — the seamless transit applies to the Kuala Lumpur layover, not to your Cambodia entry.
- **Confirm baggage and transit terms at booking.** Fly-Thru's no-immigration, through-checked-baggage benefit applies to qualifying single-itinerary bookings; piecing together separate AirAsia tickets does not get you the same treatment.

The campaign rolled out its first phase in May 2026 before the wider mid-June announcement, starting with digital storytelling around Cambodia's heritage and gradually scaling into trade events. For Indian travelers, the practical upshot is straightforward: one of Asia's most storied destinations just got materially easier to reach, and the layover that used to be a chore is now meant to be invisible."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
