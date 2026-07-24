#!/usr/bin/env python3
"""Travel writer — 2026-06-27 19:00 PT run. 3 articles."""
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

# ────────────────────────────────────────────────
# ARTICLE 1: India Passport Fee Hike from July 1
# ────────────────────────────────────────────────

art1_body = """India's passport fees are going up on July 1 — and for the millions of Indian-origin residents abroad who still hold or renew Indian travel documents, the clock is already ticking.

The Ministry of External Affairs has issued the Passports (Amendment) Rules, 2026, raising charges across nearly every category of passport service. The revision is the broadest in years, touching fresh applications, renewals, replacements, Tatkal (expedited) processing, and even Police Clearance Certificates.

## What's changing

The new fee schedule applies from **July 1, 2026**. Here's the short version:

| Service | Old Fee (₹) | New Fee (₹) | Tatkal (₹) |
|---|---|---|---|
| 36-page passport (fresh/renewal) | 1,500 | 2,500 | 5,000 |
| 60-page passport (fresh/renewal) | 2,000 | 3,500 | 6,000 |
| Lost/damaged 36-page replacement | — | 5,000 | 7,500 |
| Lost/damaged 60-page replacement | — | 6,000 | 8,500 |
| Minor (under 18) 36-page | — | 1,750 | 4,250 |

Children under eight and seniors over sixty still get a 10 per cent discount — but only on fresh passport applications, not renewals.

For applicants outside India, revised local pricing from Indian missions is expected shortly after the global schedule takes effect. Consulates in the US, UAE, UK, and Canada typically announce their updated fee tables within days of the domestic revision.

## The OCI angle most families miss

Passport renewals trigger a separate obligation that many diaspora families overlook: updating the Overseas Citizen of India card.

Under current rules, every OCI cardholder must upload a copy of the new passport and a recent photograph to the OCI portal within **three months** of receiving a renewed passport. Miss that window and a $25 penalty applies — plus the update must then go through VFS Global's physical submission process rather than a quick online upload.

The rules on full OCI card reissue have been relaxed significantly. Cardholders between 21 and 50 no longer need to reissue the card at all when renewing a passport — an online update suffices. The mandatory reissue now kicks in only once: when a cardholder obtains a new passport after turning 20. After 50, no reissue is required either.

Fresh OCI applications carry a revised fee of **$275**, while reissuance for change of particulars or on turning 20 costs **$25**. Replacement for a lost OCI card is **$100**.

## Why it matters for NRIs

The Indian passport remains the foundation document for every consular service — from OCI applications to attestations for property transactions back home. For a family of four in the Bay Area or New Jersey renewing two adult and two minor passports through Tatkal, the total consular outlay now crosses ₹18,500 (roughly $220) before service charges at VFS or BLS Global centres.

The fee hike also coincides with a major consular infrastructure transition. In the UAE, the handover from BLS International to Alhind Tours and Travels as the new Indian Consular Application Centre operator begins on July 1 as well. Applicants in Dubai and Abu Dhabi should expect appointment scheduling to shift to the new ICAC platform, with processing targeted at 30 minutes per application and a Dh19 service fee per transaction.

For NRIs planning summer trips home, the practical advice is straightforward: if your passport renewal is due in the next six months, submitting before July 1 saves ₹1,000 to ₹2,000 per booklet. After that date, budget for the higher fees and ensure OCI updates are completed within the three-month window to avoid the penalty and the physical-submission hassle.

The passport validity itself — ten years for adults, five years or until age 18 for minors — remains unchanged. What has changed is the price of keeping it current."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Passport Fees Jump on July 1 — Here's the New Math for Every NRI Family",
    "subheadline": "The broadest passport fee revision in years hits fresh applications, renewals, and Tatkal processing just as summer travel peaks. OCI card rules add another layer.",
    "slug": make_slug("india-passport-fee-hike-july-1-oci-update-nri"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "Every NRI family renewing Indian passports or updating OCI cards faces higher fees from July 1 — submitting before the deadline saves ₹1,000-₹2,000 per booklet.",
    "tags": ["travel", "passport", "oci", "visa", "nri", "consular"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-introduces-higher-passport-charges/"},
        {"name": "CA Club India", "url": "https://www.caclubindia.com/news/passport-application-fee-revised-rates-from-1st-july-2026-87921.asp"},
        {"name": "Fragomen Immigration", "url": "https://www.fragomen.com/insights/overseas-citizen-of-india-cardholders-processes-streamlined.html"},
        {"name": "VisaVerge", "url": "https://visaverge.com/india-oci-rules-2026/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An open passport displaying international travel stamps",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}

# ────────────────────────────────────────────────
# ARTICLE 2: Air Suvidha 2.0 health declaration
# ────────────────────────────────────────────────

art2_body = """If you are flying to India this summer, there is a new box to tick before you board — and this one is not optional.

India launched **Air Suvidha 2.0** on June 25, reviving the mandatory online health self-declaration system that most travellers thought they had left behind with Covid. This time the trigger is not a respiratory virus but the Ebola outbreak in Central and East Africa that the World Health Organisation declared a Public Health Emergency of International Concern on May 17.

## What Air Suvidha 2.0 requires

Every international passenger arriving in India — regardless of origin — must now submit a digital health declaration before clearing immigration. The form covers three areas:

- **21-day travel history**: everywhere you have been in the three weeks before arrival
- **Exposure history**: any contact with confirmed or suspected Ebola/Bundibugyo virus disease cases
- **Symptoms**: fever, unexplained bleeding, severe headache, muscle pain, and other Ebola-associated indicators

The form can be completed up to 24 hours before landing in India. Authorities strongly recommend filling it during web check-in or before boarding. On arrival, passengers show the downloaded declaration at the International Travel Health Desk or immigration counter. No physical paperwork is needed — the process is fully contactless.

## The Ebola context

The outbreak driving this measure is the Bundibugyo virus disease in the Democratic Republic of the Congo and Uganda, which has killed over 270 people since it was detected. South Sudan has been classified by the WHO as a high-risk area for transmission. While no cases have been reported in India, the government is treating the PHEIC designation as a trigger for proactive screening rather than reactive containment.

The Air Suvidha platform is not new. It was first launched in August 2020 during the pandemic and became the primary digital gateway for Covid-era travel to India, processing over one crore (10 million) passenger declarations before it was wound down as restrictions eased. The 2.0 version retains the contactless architecture but narrows the health screening to Ebola-specific risk factors.

## What NRIs need to know

For the Indian diaspora, the practical impact is a single extra step in pre-departure planning — but one that cannot be skipped. The declaration is mandatory for all international arrivals, not just passengers from African countries. A family of four flying SFO–DEL or JFK–BOM for summer vacation needs four separate declarations submitted before boarding.

The portal is administered jointly by the Ministry of Civil Aviation, Delhi International Airport Limited, and the Directorate General of Health Services under the Ministry of Health. Passenger data is shared in real time with airport health officers, the Bureau of Immigration, the Integrated Disease Surveillance Programme, and state surveillance officers for faster identification of at-risk travellers.

Unlike the Covid-era Air Suvidha — which required negative RT-PCR certificates, vaccination proof, and sometimes institutional quarantine — the current version demands only the self-declaration. There are no testing or quarantine requirements attached to arrival from non-affected countries. The screening is informational, not restrictive.

## Timing and travel tips

The reactivation comes at peak season for diaspora travel. June through August is when most NRI families visit India — school summer breaks in the US align with festival preparation and family time back home. Adding a health declaration to the checklist alongside visa verification, OCI card updates, and travel insurance is a minor inconvenience, but missing it could mean delays at immigration.

The Air Suvidha 2.0 portal is accessible via the Delhi airport website. Passengers arriving at Mumbai, Bengaluru, Hyderabad, Chennai, and other international airports should use the same portal — the declaration is not airport-specific.

India is not the only country tightening screening. Several Gulf states and East African nations have introduced similar pre-arrival declarations. For NRIs transiting through Dubai, Abu Dhabi, or Doha en route to India, check whether transit countries have their own declaration requirements — layering compliance across multiple stops is the real logistical headache this summer."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Flying to India This Summer? There's a New Health Form You Can't Skip",
    "subheadline": "India has relaunched Air Suvidha as a mandatory pre-arrival health declaration for all international passengers, triggered by the Ebola outbreak in Central Africa.",
    "slug": make_slug("air-suvidha-2-health-declaration-india-ebola-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Every NRI flying home this summer must submit a mandatory digital health declaration before boarding — no exceptions, regardless of origin country.",
    "tags": ["travel", "air-suvidha", "health", "ebola", "india", "nri", "airport"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "India Strategic", "url": "https://www.indiastrategic.in/india-launches-air-suvidha-2-0-amid-ebola-outbreak/"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/india-launches-portal-to-screen-travellers-amid-ebola-outbreak"},
        {"name": "Curly Tales", "url": "https://curlytales.com/are-you-travelling-to-india-from-the-uae-india-makes-health-declaration-mandatory/"},
        {"name": "GK Today", "url": "https://www.gktoday.in/india-restores-air-suvidha-for-ebola-affected-travellers/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Delhi_airport_terminal_3.jpg/1280px-Delhi_airport_terminal_3.jpg",
    "image_caption": "Delhi's Indira Gandhi International Airport Terminal 3, where Air Suvidha declarations are processed at arrival",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

# ────────────────────────────────────────────────────────
# ARTICLE 3: India's 7 bullet train corridors + NHSRCL
# ────────────────────────────────────────────────────────

art3_body = """India's bullet train ambitions have spent years stuck on a single corridor. That is about to change — and for the diaspora, the implications reach far beyond engineering bragging rights.

The seven high-speed rail corridors announced in Union Budget 2026 are now moving from paper to procurement. The National High Speed Rail Corporation Limited has begun reviewing domestic manufacturers' capability to build indigenous high-speed trainsets, signalling that India intends to reduce its dependence on Japanese Shinkansen technology and develop its own rolling stock for future lines. The assessment covers propulsion systems, onboard digital management, vehicle electronics, mechanical structures, and safety-critical engineering — the full stack of what makes a bullet train work at 300-plus kilometres per hour.

## The seven corridors

The approved routes, together spanning more than 4,000 kilometres with an estimated investment of ₹16 lakh crore ($190 billion), form a high-speed spine across western, southern, and northern India:

- **Mumbai–Pune**: 48 minutes (currently 3.5 hours by road, longer by rail)
- **Pune–Hyderabad**: 2 hours 8 minutes
- **Hyderabad–Bengaluru**: 2 hours 10 minutes
- **Hyderabad–Chennai**: projected under 2 hours 30 minutes
- **Chennai–Bengaluru**: 73 minutes (currently 5-6 hours by road)
- **Delhi–Varanasi**: 3 hours 15 minutes (Vande Bharat currently takes 8 hours)
- **Varanasi–Siliguri**: approximately 6 hours (currently a gruelling overnight journey)

These sit alongside the foundational **Mumbai–Ahmedabad corridor** — the 508-kilometre, 320 kmph Shinkansen-technology project launched in 2017, now expected to be operational by late 2029.

## Why NRIs should care about a train they may never ride daily

The diaspora's India trips follow a predictable pattern: fly into a hub airport (Delhi, Mumbai, Bengaluru, Hyderabad, Chennai), then endure the last-mile slog to the family hometown. That slog — whether it is the Mumbai–Pune expressway, the Bengaluru–Mysuru highway, or the crawl from Chennai to Coimbatore — eats hours that turn a two-week vacation into an exercise in transit management.

High-speed rail rewrites that calculus. A Bengaluru-Chennai corridor at 73 minutes means a family landing at Kempegowda International can be in Chennai's T. Nagar within two hours of touching down — door to door. The Mumbai–Pune link at 48 minutes makes Pune's tech corridor and the Konkan coast beyond it effectively suburban to Mumbai's international terminal. For Telugu families in the US flying into Hyderabad, bullet train connections to both Bengaluru and Chennai turn a three-city visit from a week-long road trip into a single day's circuit.

The Delhi–Varanasi corridor matters for a different reason. Varanasi is a spiritual anchor for millions in the diaspora, but the journey from Delhi — eight hours by the fastest train, often unreliable by road — has always made it a pilgrimage that demands dedicated travel days. At 3 hours 15 minutes, it becomes a comfortable day trip from Delhi, or a seamless connection from Air India's new Easy Connect hub-and-spoke flights that route through the capital.

## The indigenous angle

India's decision to develop its own high-speed trainsets is as much about industrial strategy as transport. The Mumbai–Ahmedabad corridor relies on Japanese Shinkansen technology — a $15 billion Japanese loan finances the project and Japanese firms supply the trains. For the seven new corridors, NHSRCL is evaluating whether Indian manufacturers can design propulsion, electronics, and safety systems domestically.

The push carries echoes of India's Vande Bharat programme, where domestically designed semi-high-speed trains (operating at 160 kmph) have been deployed across dozens of routes. Scaling that capability to 300-plus kmph is a different engineering challenge entirely, but the intent to try signals that India sees high-speed rail as a long-term domestic industry, not a one-off import.

## Timeline reality

Construction on the new corridors is unlikely to begin before 2028. Detailed project reports, land acquisition, environmental clearances, and funding arrangements will consume the next two years at minimum. The Mumbai–Ahmedabad corridor — which has been under construction since 2020 — offers a sobering reference point for the pace of Indian infrastructure delivery.

But the network effect, once even two or three corridors are operational, could fundamentally reshape how the diaspora experiences India. Fewer rental car nightmares. Fewer missed connections. More time with family, less time on the road. For NRIs who visit once a year and measure every hour, that is the real revolution."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Bullet Train Map Just Got Seven New Lines — and the Diaspora's Commute Home Is in the Blueprint",
    "subheadline": "Seven high-speed rail corridors will cut Mumbai-Pune to 48 minutes and Bengaluru-Chennai to 73. India is now evaluating whether it can build the trains itself.",
    "slug": make_slug("india-bullet-train-seven-corridors-nhsrcl-indigenous-nri"),
    "category": "travel",
    "vertical": "infrastructure",
    "diaspora_angle": "NRIs spend hours on the last mile from hub airports to hometowns — bullet train corridors connecting Mumbai-Pune, Bengaluru-Chennai, and Delhi-Varanasi could compress those slogs to under an hour.",
    "tags": ["travel", "bullet-train", "high-speed-rail", "india", "infrastructure", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-ignites-travel-revolution-with-massive-bullet-train-expansion/"},
        {"name": "Livemint", "url": "https://www.livemint.com/economy/budget/union-budget-2026-nirmala-sitharaman-proposes-7-high-speed-rail-corridors-11738389600121.html"},
        {"name": "Urban Acres", "url": "https://urbanacres.in/nhsrcl-reviews-capability-for-high-speed-trains/"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2104257"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37554867/pexels-photo-37554867.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A modern high-speed train traveling through lush greenery",
    "image_attribution": "Pexels",
    "body": art3_body.strip(),
}

# ──────────────
# INSERT ALL
# ──────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
