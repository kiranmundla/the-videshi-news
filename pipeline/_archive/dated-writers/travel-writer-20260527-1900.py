#!/usr/bin/env python3
"""Travel writer — 2026-05-27 19:00 PDT batch"""
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

# ─────────────────────────────────────────────
# ARTICLE 1: India's First Underwater Museum
# ─────────────────────────────────────────────

article1_body = """Maharashtra has quietly begun assembling what will become India's first underwater museum — and it chose an unlikely centrepiece. On May 19, the decommissioned Indian Navy warship Ex-INS Guldar was lowered onto the seabed near the Nivati Rock formations in Sindhudurg district, roughly 500 kilometres south of Mumbai along the Konkan coast. The vessel now sits at a depth of 22 metres, where it will serve as the anchor of an artificial reef, a dive site, and eventually, a submarine tourism hub.

The project is a collaboration between the Maharashtra Tourism Development Corporation (MTDC) and Mazagon Dock Shipbuilders Limited, which handled the technical operation of sinking the 40-year-old warship. Scientific assessments by the Maharashtra Maritime Board and the CSIR-National Institute of Oceanography confirmed the site had no natural coral reefs and that the environmental impact would be minimal.

## A Warship's Second Life

INS Guldar was a Magar-class Landing Ship Tank, first launched in Poland in 1985 and decommissioned in 2024 after nearly four decades of service in amphibious operations, troop transport, and coastal security exercises. Before being sunk, the vessel underwent thorough environmental cleaning to strip hazardous materials.

The plan is for the hull to become a substrate for coral growth and marine biodiversity over the coming years — a controlled experiment in reef regeneration that doubles as a tourism asset. Tourists will access the site by speedboat from a jetty to Nivati Rock, then board barges for submarine rides and scuba experiences. The activity menu includes guided wreck diving, discover scuba sessions at 12 metres, certified dives to 18 metres, advanced diving to 30 metres, and underwater photography programmes.

## Why the Konkan Coast Matters

Sindhudurg is not an accidental choice. The district is home to the 17th-century Sindhudurg Fort, built by Chhatrapati Shivaji Maharaj on a rocky island offshore — itself one of Maharashtra's most distinctive historical sites. The state government has been investing in the broader Konkan corridor as an alternative to the more established Goa tourism circuit, and the underwater museum is its most ambitious gambit yet.

Maharashtra's tourism ministry has separately announced a ₹2,500 crore plan to develop 100 tourism circuits across the state by 2047, and the Sindhudurg project fits squarely within that framework. For adventure tourism, the Konkan coast offers clear Arabian Sea waters, relatively undeveloped coastline, and proximity to Mumbai — all ingredients that Goa leveraged decades ago.

## The NRI Opportunity

For the Indian American diaspora, this matters in practical terms. NRIs visiting family in Mumbai or Pune during summer trips have historically had limited adventure tourism options beyond Goa. Sindhudurg is a 9-hour drive or a short flight from Mumbai to Sindhudurg's Chipi Airport, which began commercial operations in 2023. A wreck-diving experience at an underwater museum is precisely the kind of differentiated offering that can extend an India trip beyond the obligatory family rounds.

India's adventure tourism sector has been growing at roughly 20% annually, but most of that growth has been concentrated in Ladakh, Rishikesh, and the Andaman Islands. The Konkan coast is the next frontier — and a sunken warship is a compelling calling card.

The project is still in its early stages; no official opening date has been announced. But the hardest part — getting a 2,000-tonne warship onto the ocean floor — is done."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Sank a Warship to Build Its First Underwater Museum — and It's on the Konkan Coast",
    "subheadline": "Maharashtra deployed the decommissioned INS Guldar at 22 metres depth off Sindhudurg, anchoring an ambitious submarine tourism project that could reshape adventure travel along India's western seaboard.",
    "slug": make_slug("india-first-underwater-museum-sindhudurg-konkan-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting Mumbai or Pune now have a genuine adventure tourism option beyond Goa — wreck diving and submarine tourism at Sindhudurg, reachable via Chipi Airport or a coastal drive.",
    "tags": ["travel", "adventure tourism", "Maharashtra", "Konkan coast", "diving", "museums"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Curly Tales", "url": "https://curlytales.com/india/trending/indias-first-underwater-museum-is-coming-to-maharashtra-with-a-retired-warship-submarine-tourism-hub/"},
        {"name": "The Economic Times", "url": "https://economictimes.indiatimes.com/"},
        {"name": "Maharashtra Tourism Development Corporation", "url": "https://www.maharashtratourism.gov.in/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Sindhudurg_fort.JPG",
    "image_caption": "Sindhudurg Fort, built by Chhatrapati Shivaji Maharaj in the 17th century, overlooks the waters where India's first underwater museum is taking shape.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ─────────────────────────────────────────────
# ARTICLE 2: IndiGo's Widebody Long-Haul Bet
# ─────────────────────────────────────────────

article2_body = """India's aviation industry is having a split-personality moment. Air India has slashed 22% of its domestic flights between June and August. IndiGo, the country's largest carrier, has trimmed 7-10% of planned domestic operations for the same period. Jet fuel prices, inflated by the Iran conflict and Strait of Hormuz disruptions, are hammering margins. The two airlines together control roughly 90% of India's domestic air passenger market, and the cuts will tighten seat availability and keep fares elevated through the peak summer travel season.

And yet, IndiGo is simultaneously executing one of the most aggressive widebody fleet buildups in Asian aviation history. The airline now has firm orders for 60 Airbus A350-900 aircraft — a $9 billion commitment to long-haul international routes that would bypass the Gulf hubs entirely and connect Indian cities directly to North America and Europe.

## The Gulf Hub Detour

This is the part that matters most to the Indian diaspora. Today, most NRIs flying between the US and India route through Dubai, Doha, or Abu Dhabi. It adds 4-8 hours to the journey, generates revenue for Gulf carriers, and keeps Indian airlines out of the most lucrative segment of the market. Emirates, Qatar Airways, and Etihad have built their business models around being the preferred connection point between India and the West.

IndiGo's A350 strategy is a direct challenge to that model. The A350-900 can fly roughly 15,000 kilometres nonstop — enough to cover Delhi-New York, Mumbai-San Francisco, or Bengaluru-London without touching down in the Middle East. With 60 of these aircraft joining the fleet over the coming years, IndiGo is positioning itself to offer something Air India has struggled to deliver at scale: reliable, competitively priced nonstop service on the routes that matter most to the 4.4 million Indian Americans.

## Already in the Air

IndiGo is not waiting for the A350s to start testing international waters. In January 2026, it launched nonstop flights to Athens using the Airbus A321XLR — India's first deployment of that aircraft type. The A321XLR is a narrowbody jet stretched for medium-to-long-haul routes, and Athens was a deliberate proving ground: a European destination with growing Indian tourist demand but no existing nonstop service from India.

The airline already flies to over 30 international destinations across Southeast Asia, the Middle East, and Central Asia. But those are all short-to-medium-haul routes flown on narrowbody A320 family aircraft. The A350 orders represent a structural shift in ambition.

## What NRIs Should Watch

The practical impact for diaspora travellers is still years away — IndiGo's first A350 deliveries are expected in the latter half of this decade. But the pricing implications are significant. IndiGo built its domestic business on aggressive cost management and high aircraft utilisation, consistently undercutting Air India on fares. If it brings the same philosophy to long-haul routes, the SFO-DEL and JFK-BOM corridors could see meaningful fare competition for the first time in years.

There is a catch. The current aviation crisis — fuel costs, airspace restrictions from the Iran-Pakistan conflict, Air India's $2.4 billion annual loss — is exactly the kind of environment that can delay fleet expansion plans. Engine deliveries from Rolls-Royce (which powers the A350) have faced supply chain constraints globally. And IndiGo has no experience operating widebody aircraft; the operational learning curve is steep.

Still, the signal is clear. India's largest airline is betting that the future of Indian long-haul aviation does not run through Dubai. For the millions of NRIs who have spent decades connecting through Gulf airports, that is a bet worth watching."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo's $9 Billion Widebody Bet Could End the NRI's Least Favourite Layover",
    "subheadline": "While slashing domestic flights amid soaring fuel costs, India's largest airline is quietly building a fleet of 60 Airbus A350s to bypass Gulf hubs and fly nonstop to the US and Europe.",
    "slug": make_slug("indigo-a350-widebody-long-haul-bypass-gulf-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "IndiGo's 60-aircraft widebody order targets the exact routes NRIs fly most — SFO-DEL, JFK-BOM, ORD-HYD — with budget-carrier pricing that could undercut both Gulf connectors and Air India nonstops.",
    "tags": ["travel", "airlines", "IndiGo", "A350", "aviation", "Gulf airlines", "nonstop flights"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/air-india-indigo-cut-domestic-capacity-new-indian-express-reports-2026-05-27/"},
        {"name": "Airbus", "url": "https://www.airbus.com/en/newsroom/press-releases/2025-10-indigo-places-firm-order-for-30-additional-a350-900-airbus"},
        {"name": "TradingView / Reuters", "url": "https://id.tradingview.com/news/reuters.com,2025:newsml_L1N3NB0FQ:0/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/EGLF_-_Airbus_A350-941_-_F-WZNW.jpg/1280px-EGLF_-_Airbus_A350-941_-_F-WZNW.jpg",
    "image_caption": "An Airbus A350-900 — the widebody aircraft IndiGo has ordered 60 of for its long-haul push into direct India-US and India-Europe routes.",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}

# ─────────────────────────────────────────────
# ARTICLE 3: Orchha UNESCO Nomination
# ─────────────────────────────────────────────

article3_body = """UNESCO has accepted the nomination dossier for Orchha, the medieval Bundela capital in Madhya Pradesh, putting it on track for possible inscription as a World Heritage Site in the 2027-28 cycle. If approved, it would become India's 45th entry on the list — and arguably the most undervisited one.

Orchha sits on the banks of the Betwa River in Niwari district, about 15 kilometres from Jhansi and roughly 500 kilometres southeast of Delhi. Founded in 1531 by Bundela Rajput ruler Rudra Pratap Singh, the town is an open-air museum of 16th- to 18th-century Indian architecture that somehow never made it onto the mainstream tourist circuit. Its nomination is notable for another reason: it is the only state-protected heritage site in India to be put forward for World Heritage status, rather than a centrally protected one managed by the Archaeological Survey of India.

## What Makes Orchha Different

The Orchha heritage ensemble is a mashup of architectural traditions that you do not find together anywhere else in India. The Jahangir Mahal, built in 1605 to honour the Mughal emperor Jahangir's visit, combines Rajput military architecture with Mughal decorative sensibility — latticed windows, tiled floors, and symmetrical courtyards perched on a massive stone plinth overlooking the Betwa. The Chaturbhuj Temple, with its towering shikhara, was designed to be visible for miles and is one of the few Hindu temples in India that incorporates Mughal arches and minarets into its structure.

The Ram Raja Temple is unique in all of India: the only temple where Lord Rama is worshipped as a king rather than a deity, with a guard of honour presented daily. The cenotaphs (chhatris) along the Betwa riverbank, built in the Mughal-Rajput hybrid style, are perhaps Orchha's most photogenic feature — a row of ornate memorial towers reflected in the river, often compared to a miniature Varanasi without the crowds.

## The Tourism Case

Orchha already draws around 300,000 visitors annually, but that figure is dwarfed by Jaipur (15 million), Agra (8 million), or even Khajuraho (800,000). The UNESCO tag would change the calculus. India's existing World Heritage Sites see a measurable tourism bump after inscription — the Maratha Military Landscapes in Maharashtra, inscribed in 2025, saw visitor numbers jump 35% within six months.

Madhya Pradesh has been investing in accessibility. Orchha is connected by road to Jhansi, which sits on the Delhi-Mumbai rail corridor and is served by the Vande Bharat Express. A small airstrip at Khajuraho, 175 kilometres away, handles seasonal flights from Delhi and Varanasi. The state has also been upgrading local accommodation, with heritage properties like the Amar Mahal and the Orchha Resort offering mid-range options alongside budget guesthouses.

## Why NRIs Should Visit Before the Crowds Come

For diaspora families planning a heritage trip to India, Orchha is the kind of destination that rewards going early. The town's charm lies partly in its relative emptiness — you can walk through the Jahangir Mahal essentially alone at sunrise, something impossible at Fatehpur Sikri or Hampi. The Chaturbhuj Temple's prayer hall echoes. The cenotaphs are unguarded and unlit, which means sunrise and sunset photography is unrestricted.

A UNESCO inscription would bring conservation funding and international recognition, but it would also bring tour buses, entrance fees, and fences. The sweet spot for visiting is right now — after the infrastructure improvements but before the crowds.

The practical logistics work for an NRI itinerary. Orchha can be combined with a Jhansi-Khajuraho circuit: fly into Delhi, take the Vande Bharat to Jhansi (4.5 hours), spend two days in Orchha, drive to Khajuraho, and fly back to Delhi. The entire side trip adds four days to an India visit and covers two of the country's most significant — and least crowded — historical sites.

The UNESCO Committee's next evaluation cycle begins in 2027. Orchha's dossier will undergo review by ICOMOS (the International Council on Monuments and Sites) before a final vote, likely in 2028. The outcome is not guaranteed — India's previous nomination for Delhi's Mehrauli Archaeological Park was deferred twice. But the Bundela ensemble is architecturally distinctive enough, and well-documented enough, to have a strong case."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Orchha Is One Step Closer to Becoming India's 45th UNESCO World Heritage Site — and Most NRIs Have Never Heard of It",
    "subheadline": "UNESCO has accepted the nomination dossier for Madhya Pradesh's medieval Bundela capital, a town with Mughal-Rajput hybrid architecture, empty temples, and riverside cenotaphs that could soon join the Taj Mahal on the World Heritage List.",
    "slug": make_slug("orchha-unesco-world-heritage-nomination-nri-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Orchha is an uncrowded alternative to Agra and Jaipur that fits neatly into an NRI heritage itinerary — Vande Bharat from Delhi to Jhansi, two days exploring Bundela architecture, then on to Khajuraho. Visit before the UNESCO tag brings the crowds.",
    "tags": ["travel", "UNESCO", "heritage", "Madhya Pradesh", "Orchha", "cultural tourism"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "India Tribune", "url": "https://indiatribune.com/orchhas-dossier-for-world-heritage-status-accepted-by-unesco-mp-govt/"},
        {"name": "Wikipedia - Orchha", "url": "https://en.wikipedia.org/wiki/Orchha"},
        {"name": "Architexturez", "url": "https://architexturez.net/doc/az-cf-226979"}
    ]),
    "score_total": 70,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Chaturbhuj_Temple%2C_Orchha.jpg/1280px-Chaturbhuj_Temple%2C_Orchha.jpg",
    "image_caption": "The Chaturbhuj Temple in Orchha — one of the few Hindu temples in India incorporating Mughal arches and minarets.",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body
}

# ─────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone — {len(articles)} articles submitted at {now}")
