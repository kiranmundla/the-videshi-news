#!/usr/bin/env python3
"""Travel writer — 3 articles for The Videshi, 2026-06-27 23:00 PT run."""

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
# ARTICLE 1: Germany transit visa waiver + Lufthansa India push
# ─────────────────────────────────────────────
art1_body = """Germany quietly made one of the most consequential travel changes for Indian passport holders this year — and most NRIs haven't noticed yet.

Effective June 3, Berlin abolished the airport transit visa requirement for Indian nationals connecting through German airports. The policy, announced by the German Embassy in New Delhi, means Indians flying through Frankfurt or Munich to a third country — London, São Paulo, Johannesburg, anywhere — no longer need to apply for a separate transit visa just to change planes.

For the roughly 4.5 million Indians who hold US, UK, or Canadian residency, the change eliminates a long-standing friction point. An NRI in Chicago routing through Frankfurt to visit family in Hyderabad, or a Bay Area tech worker connecting in Munich en route to a European holiday, can now book Lufthansa connections without the extra paperwork.

## Why Lufthansa Is the Biggest Winner

The timing is not accidental. Lufthansa Group — which includes SWISS, Austrian Airlines, and Brussels Airlines — currently operates more than 70 weekly flights between India and Europe, including over 50 services to Germany alone. India is the group's largest intercontinental market in the Asia-Pacific region and its second-largest globally, behind only the United States.

"UK is clearly one of the key markets that will benefit from this development, alongside other long-haul destinations, including markets in Central and South America such as Brazil," Kevin Markette, Lufthansa Group's Senior Director for Regional Sales in South Asia, told *The Hindu BusinessLine*.

The carrier is doubling down. Lufthansa is deploying its award-winning Allegris cabin interiors — a ground-up redesign of Business, Premium Economy, and Economy — on additional Boeing 787-9 services from Delhi and Hyderabad. The A380, the double-decker superjumbo, is getting enhanced service between Mumbai and Munich.

And in what may be the most significant network addition for South India's diaspora, SWISS is launching its first-ever direct service between Bengaluru and Zurich in the Winter 2026 schedule. For the estimated 1.5 million Kannadigas and broader South Indian diaspora in Europe, that's a game-changer — no more backtracking through Delhi or Mumbai for a European connection.

## The West Asia Factor

The transit visa waiver arrives at a moment when Gulf hubs — the traditional connecting points for India–Europe and India–Americas traffic — are unreliable. Airspace closures over West Asia since early 2026 have forced Indian carriers to reroute, cancel, or slash capacity on Gulf-bound flights by as much as 77 per cent at the peak of disruptions in April.

For NRIs accustomed to routing through Dubai or Doha, Frankfurt and Munich now offer a visa-free alternative that sidesteps the entire West Asia corridor. Lufthansa's Frankfurt hub alone connects to more than 200 onward destinations.

The competitive implications are significant. Emirates, Qatar Airways, and Etihad have long dominated India–Europe connecting traffic by offering lower fares and convenient one-stop routings through their Gulf hubs. Germany's visa waiver chips away at one of their structural advantages — the Gulf carriers' home airports never required Indians to hold a transit visa.

## What NRIs Should Know

The waiver applies to airside transit only — passengers connecting through Frankfurt or Munich without leaving the international transit area. It does not grant entry into Germany's Schengen zone. Indians who wish to leave the airport, even briefly, still need a Schengen visa.

Practically, this means NRIs booking Lufthansa Group flights should ensure their connecting itinerary keeps them in the transit zone. Most standard connections do, but passengers with very long layovers (over 12 hours) may want to confirm their routing.

For price-sensitive NRI families booking summer or Diwali trips to India, the change opens up a new set of competitive fares. Lufthansa Group's India–US pricing through Frankfurt has historically been within 10–15 per cent of Gulf carrier fares, and the elimination of the transit visa fee (previously around €80) narrows the gap further.

Germany's move follows a broader European trend of easing transit requirements for Indian nationals — a recognition that India's outbound travel market, projected to reach 50 million trips annually by 2030, is too large to ignore."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Germany Drops Transit Visa for Indians — and Lufthansa Is Already Betting Big on What Happens Next",
    "subheadline": "Berlin's decision to waive airport transit visas at Frankfurt and Munich opens a cheaper, faster corridor to the UK and South America — precisely when Gulf hubs are unreliable.",
    "slug": make_slug("germany-transit-visa-waiver-indians-lufthansa-swiss-india"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs routing through Frankfurt or Munich to India, the UK, or South America no longer need a separate transit visa — eliminating paperwork and opening competitive Lufthansa fares as an alternative to disrupted Gulf hub connections.",
    "tags": ["travel", "visa", "germany", "lufthansa", "airlines", "europe", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/lufthansa-group-welcomes-visa-free-airport-transit-for-indian-nationals-via/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/lufthansa-eyes-higher-india-traffic-after-germany-scraps-airport-transit-visa-requirement/article69698123.ece"},
        {"name": "WebWire", "url": "https://www.webwire.com/ViewPressRel.asp?aId=331742"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/D-AIXH_Lufthansa_Airbus_A350-941_airplane%2C_Miami%2C_Florida.jpg/1280px-D-AIXH_Lufthansa_Airbus_A350-941_airplane%2C_Miami%2C_Florida.jpg",
    "image_caption": "A Lufthansa Airbus A350-900 on the tarmac — the carrier operates over 70 weekly flights between India and Europe",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2: Air India B787 retrofit turnaround + CEO on route restoration
# ─────────────────────────────────────────────
art2_body = """Air India's customers have spent years complaining about worn-out seats, broken entertainment screens, and the unmistakable odour of a cabin that had seen better decades. The Tata-owned carrier has heard them — and the numbers suggest the turnaround is finally real.

In an internal memo to employees this week, CEO and Managing Director Campbell Wilson disclosed that customer Net Promoter Score on Air India's two retrofitted Boeing 787 aircraft has improved by more than 74 points — swinging from minus 31 to plus 43. Customer satisfaction scores across cabin comfort, ambience, inflight entertainment, and meals have jumped from 2.7 out of five to 4.1.

Those are not incremental improvements. They are the kind of numbers that suggest passengers on the new planes are flying a fundamentally different airline.

## The Fleet Is Changing — Fast

Air India is currently retrofitting 26 legacy Boeing 787-8 aircraft with brand-new interiors and repainting them in the airline's refreshed livery. Another 787-8 is in the hangar now. Eight additional new or retrofitted widebody aircraft are expected to enter service this year, including a brand-new Boeing 787-9 that Wilson said would arrive "this weekend."

The route-by-route rollout reads like a checklist of the diaspora's most-flown corridors:

**Mumbai–London Heathrow** gets new Boeing 787-9s and retrofitted 787-8s starting July 1, replacing the ageing 777-300ER fleet on the route. Every seat will feature Air India's new cabin interior.

**Delhi–Melbourne** goes daily from July 1 with an upgraded Boeing 777-300ER — and for the first time, introduces First Class on the route with eight private suites, alongside 40 Business Class flatbeds and 280 Economy seats. That adds roughly 4,000 seats monthly on a corridor that serves Australia's 800,000-strong Indian diaspora.

**Bengaluru–London Heathrow** gets a retrofitted 787-8 with the new Premium Economy cabin from August 1.

**Delhi–Toronto** increased from seven to ten weekly flights in March, with the majority shifting to new-interior 787-9s by August.

By mid-2026, Air India says over 50 per cent of its North America flights will feature new or upgraded interiors — a threshold that should be noticeable to NRIs booking SFO–Delhi, JFK–Mumbai, or ORD–Hyderabad.

## Route Restoration on the Horizon

Wilson's memo also hinted at something NRI travellers have been waiting to hear: the airline may bring back routes it cut during the West Asia crisis.

"Should this trend continue, we may be able to wind back some of the schedule reductions we'd taken in recent months," Wilson wrote, citing easing tensions in the Middle East, reopened airspace, and a significant decline in international jet fuel prices.

Air India had rationalised services on select international routes between June and August 2026 owing to airspace restrictions and record fuel costs. The airline continued to operate more than 1,200 international flights monthly, but frequency and capacity took hits on several key corridors.

## On-Time Performance Hits a Record

The fleet upgrades come alongside operational improvements that frequent flyers will notice. June marked record performance levels for Air India, with overall on-time performance (OTP) reaching 86 per cent and domestic OTP hitting 90 per cent.

For an airline that was once synonymous with chronic delays, those numbers represent a quiet cultural shift. Airlines globally consider 80 per cent on-time a respectable benchmark.

## What This Means for NRIs

The practical takeaway is straightforward: if you last flew Air India before 2025 and swore you wouldn't again, the airline landing at your gate in the second half of 2026 may be materially different from the one you remember.

The retrofit program is still rolling out — not every Air India flight has new interiors yet, and the legacy 777-300ERs on some routes still carry the old product. Check the aircraft type when booking. Routes flagged for new 787-9s or retrofitted 787-8s are the ones to target.

For the diaspora, Air India remains the only carrier offering the widest direct network between India and North America, Europe, and Australia under a single brand. If the product now matches the network, the calculus changes — and the Gulf carriers that captured NRI traffic over the past decade may find some of it returning to India's flag carrier."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India's Retrofitted Dreamliners Are Winning Over Passengers — and the CEO Wants to Restore the Routes He Cut",
    "subheadline": "Customer satisfaction on Air India's refurbished Boeing 787s has swung 74 points. CEO Campbell Wilson says easing West Asia tensions may let the airline bring back curtailed long-haul services.",
    "slug": make_slug("air-india-787-retrofit-nps-turnaround-wilson-routes-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Air India's fleet overhaul is landing on the routes NRIs fly most — Mumbai-London, Delhi-Melbourne, Bengaluru-London, and North America corridors — with over 50% of US-India flights getting new interiors by mid-2026.",
    "tags": ["travel", "airlines", "air-india", "fleet", "boeing-787", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-may-restore-curtailed-international-services-as-west-asia-crisis-eases-ceo/article69727614.ece"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/business/3369872-air-india-eyes-restoration-of-flight-schedules-amid-west-asia-stability"},
        {"name": "TravelMedia.in", "url": "https://www.travelmedia.in/aviation/air-india-upgrades-product-and-customer-experience-on-more-international-routes-this-summer/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/VT-ANS_Boeing_787-9_Dreamliner_Air_India_LHR_191018.jpg/1280px-VT-ANS_Boeing_787-9_Dreamliner_Air_India_LHR_191018.jpg",
    "image_caption": "An Air India Boeing 787-9 Dreamliner at London Heathrow — the type now receiving brand-new cabin interiors",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 3: Kerala monsoon tourism — NRI guide
# ─────────────────────────────────────────────
art3_body = """Every NRI who visits India in summer knows the drill: it's hot, it's humid, and everyone tells you December is better. What most don't know is that one state has spent decades building its entire tourism identity around the very season you're already there for.

Kerala Tourism actively promotes June through August as its premier travel season. Not as a consolation prize for off-peak visitors, but as the period when the state is at its most beautiful and when a 3,000-year-old Ayurvedic tradition says the human body is most receptive to healing.

The monsoon arrived in Kerala on May 24 this year — eight days ahead of schedule, the earliest since 2009 — and by now the Western Ghats are in full transformation. Rivers have swollen, waterfalls roar at peak force, tea plantations glow emerald, and hotel rates have cratered to a fraction of winter prices.

## The Karkkadakam Tradition

In the traditional Malayalam calendar, the monsoon month of Karkkadakam (roughly mid-July to mid-August) has been considered the ideal time for physical rejuvenation for millennia. The logic is not mystical: the high humidity and cool temperatures during monsoon make the body's pores more open and skin more absorbent, enhancing the effectiveness of Ayurvedic oil treatments like Panchakarma.

Kerala's network of certified Ayurvedic resorts — from basic centres in Thrissur to luxury retreats in Kovalam and Kumarakom — runs at peak capacity during monsoon, not winter. Fourteen-day Panchakarma packages that cost ₹2–3 lakh in December can be booked for ₹80,000–1.2 lakh in July. For NRIs paying in dollars, that's a medically supervised wellness retreat for under $1,000.

The monsoon also brings cultural events that winter visitors never see. The Aanayoottu — a public elephant-feeding ceremony — takes place at the Vadakkumnathan and Guruvayur temples in Thrissur district, drawing crowds who watch captive temple elephants receive special medicinal diets and treatments. The Malabar River Festival in Kozhikode district hosts international kayaking competitions on the rain-swollen Chalipuzha and Iruvanjipuzha rivers.

## The Money Case

The economics of monsoon Kerala are almost absurdly favourable for NRI families.

Domestic flight fares to Kochi drop 30 to 50 per cent compared to peak winter pricing, according to travel aggregator Wego. Hotel rates across the state dip significantly from July through early September. A houseboat on the Alleppey backwaters that commands ₹15,000–25,000 per night in December can be had for ₹6,000–10,000 in July.

For a family of four flying from Delhi or Bengaluru, a week in monsoon Kerala — including flights, a mid-range resort, a houseboat night, and Ayurvedic treatments — can come in under ₹1.5 lakh. The same trip in December would run ₹3.5–4 lakh.

## Where to Go

**Munnar** remains the default for a reason. The hill station's tea plantations turn an electric green in monsoon, waterfalls like Attukal and Cheeyappara are at full force, and the town is blanketed in mist that parts just often enough to reveal the Kannan Devan hills. Fewer tourists mean you might actually get a table at a restaurant without waiting.

**Wayanad** in northern Kerala has recovered from the 2024 landslides and is welcoming visitors again, though the Chooralmala-Mundakkai area remains restricted. Its misty forests, wildlife, and bamboo-raft experiences on Banasura Sagar — India's largest earth dam — are worth the winding drive from Kozhikode.

**Kochi and Alleppey** offer the classic backwater houseboat experience, and monsoon is when the canals are fullest and most photogenic. Morning cruises through rain-dimpled waterways, past coconut groves and village churches, feel like private screenings of a Kerala Tourism ad — except you're the only audience.

**Thekkady** and Periyar National Park become a wildlife haven during monsoon. The lake rises, elephants and deer move closer to the water's edge, and covered boat rides across Periyar Lake take on a moody, cinematic quality.

## Practical Tips for NRI Visitors

Expect afternoon downpours — mornings are often clear and bright. Pack light rain gear, waterproof bags for electronics, and shoes that can handle wet trails. Leeches are a genuine nuisance on forest treks; tuck your trousers into socks and carry salt.

Road travel in the Western Ghats can be slow during heavy rain. Landslide-prone stretches on routes like the Kochi–Munnar highway may see occasional closures. Check Kerala State Disaster Management Authority advisories before heading into the hills, and keep flexible travel days built into your itinerary.

The best window is late July to early August — peak bloom in the hills, full waterfalls, and the cultural calendar in gear — but even September, when the rains begin to taper, offers lush scenery with fewer disruptions."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Season Most NRIs Never See: Why Kerala in Monsoon Is India's Best-Kept Travel Secret",
    "subheadline": "Flights are half-price, hotel rates crater, and a 3,000-year-old Ayurvedic tradition says the rain is when your body heals best. Kerala Tourism wants you to book July, not December.",
    "slug": make_slug("kerala-monsoon-tourism-ayurveda-nri-summer-travel-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Most NRI families visit India during US summer break — which perfectly overlaps with Kerala's monsoon season. Flights and hotels are 30-50% cheaper than December, and Ayurvedic retreats run at a fraction of winter prices.",
    "tags": ["travel", "kerala", "monsoon", "ayurveda", "destinations", "nri", "budget"],
    "urgency": "low",
    "sources": json.dumps([
        {"name": "Kerala Tourism", "url": "https://www.keralatourism.org/kerala-in-june.php"},
        {"name": "Wego Travel Blog", "url": "https://blog.wego.com/monsoon-destinations-india/"},
        {"name": "TravelTriangle", "url": "https://traveltriangle.com/blog/monsoon-in-kerala/"},
        {"name": "CurlyTales", "url": "https://curlytales.com/monsoon-staycations-india/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Kerala_backwaters%2C_Houseboats%2C_India.jpg/1280px-Kerala_backwaters%2C_Houseboats%2C_India.jpg",
    "image_caption": "Houseboats on the Kerala backwaters — the monsoon season fills the canals and turns the landscape electric green",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
