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
        "headline": "Europe Quietly Killed the Passport Stamp — and the New Biometric Gates Are Slowing Down the Trip Home",
        "subheadline": "The EU's fully live Entry/Exit System means face and fingerprint scans for every Indian-passport traveler — and a €20 ETIAS fee is coming next. Here's how to clear the line without missing your connection.",
        "slug": make_slug("eu-entry-exit-system-biometric-border-indian-passport-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Most NRIs route home through a European hub like Frankfurt, Paris or Amsterdam, and the EU's new biometric border now adds face and fingerprint enrollment for every Indian-passport holder on the first crossing — turning a layover into a missed connection if you don't budget the time.",
        "tags": ["travel", "visa", "europe", "schengen", "airports"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "European Commission — Migration and Home Affairs", "url": "https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/smart-borders/entry-exit-system_en"},
            {"name": "USA Today — Why some travelers are waiting hours to enter Europe", "url": "https://www.usatoday.com/story/travel/2026/06/europe-ees-border-waits/"},
            {"name": "EEAS — What travellers need to know about EES", "url": "https://www.eeas.europa.eu/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/13716228/pexels-photo-13716228.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Passengers move through a modern European airport terminal, where biometric kiosks now replace passport stamping for non-EU travelers.",
        "image_attribution": "Pexels",
        "body": """If you have flown home to India through a European hub in the last few weeks, you may have noticed the inkpad is gone. As of April 10, 2026, the European Union's **Entry/Exit System (EES)** is fully operational across all Schengen border crossings, replacing the familiar passport stamp with a digital record built on your face and fingerprints. For the large share of Indian Americans who connect through Frankfurt, Paris, Amsterdam or Zurich on the way to Delhi, Mumbai or Bengaluru, this is the most significant change to the journey home in a decade — and it is quietly costing travelers time.

## What actually changed at the gate

EES applies to all non-EU nationals entering the Schengen Area for short stays of up to 90 days in any 180-day window. That includes every Indian-passport holder, whether you are transiting, on a short Schengen visa, or visiting visa-free. On your first crossing after the system went live, a border officer or a self-service kiosk captures four fingerprints, a facial image, and the data page of your travel document. The record is then stored for three years, which means subsequent trips are meant to be faster because your biometrics are already on file.

The promise is smoother repeat travel. The reality this summer has been long lines. The European Commission says more than 52 million entries and exits have been registered since the phased rollout began, with over 27,000 refusals of entry. But the transition has produced hours-long queues at popular gateways. British travelers have been warned of waits of up to six hours at airports in Italy, Portugal and Spain, and passengers at Brussels reported kiosks that were offline or out of service with little guidance from staff.

## Why this hits NRIs specifically

The diaspora's travel pattern makes this more than a European inconvenience. A huge proportion of US-to-India itineraries are one-stop routings through a Schengen hub, and the tightest of those connections — a 90-minute window at Frankfurt, say — was already unforgiving. Add a first-time biometric enrollment at a crowded kiosk and the math can break. The travelers most exposed are precisely the ones who fly home once or twice a year: infrequent enough that every trip counts as a "first crossing" if their three-year record has lapsed, and often traveling with elderly parents or children who need extra time at the gate.

There is some relief in the fine print. Children under 12 are exempt from fingerprinting, though they still need a facial image and document check. And several countries now offer a "Travel to Europe" mobile app that lets you pre-register your passport data and facial image before you fly, shaving time off that first crossing. Availability varies by country, so check the specific airport you are connecting through.

## The fee that is coming next

EES is the first half of a two-part overhaul. The second is **ETIAS**, the European Travel Information and Authorisation System — a pre-travel authorization that visa-exempt visitors will need to apply for online before departure. The fee has been set to rise to €20 from an earlier proposed €7, and the launch is expected in the final quarter of 2026, though the EU has not confirmed an exact operational date. ETIAS will not apply to Indian-passport holders who already need a Schengen visa, but it matters enormously for the growing number of NRIs traveling on US, UK, Canadian or Australian passports who have until now breezed through visa-free.

## How to clear the line cleanly

A few practical moves make the difference this season. Build at least three hours into any Schengen connection on the way to India, not the 90 minutes the booking engine suggests. If your hub offers the pre-registration app, use it before you leave home. Keep your passport, boarding passes and any visa documentation in hand luggage rather than buried in a carry-on, because the kiosks photograph your document directly. And if you are traveling with parents or young children, head for the staffed lanes rather than the self-service kiosks, where an officer can process the family together.

The stamp in your passport was a souvenir, but it was also fast. The biometric era trades that speed up front for smoother trips later — provided you give the first crossing the time it now demands."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Newest Airports Just Won a Global Design Prize — and They're Built for the NRIs Coming Home",
        "subheadline": "Navi Mumbai and Guwahati's gleaming new terminals made the Prix Versailles 2026 list, capping a building boom that is finally giving diaspora travelers an alternative to overcrowded Delhi and old Mumbai.",
        "slug": make_slug("navi-mumbai-guwahati-airports-prix-versailles-design-nri"),
        "category": "travel",
        "vertical": "infrastructure",
        "diaspora_angle": "For NRIs who dread the chaos of arriving at India's legacy terminals after a 16-hour flight, the new Navi Mumbai and Guwahati airports — now globally recognized for design — promise shorter queues, faster immigration and a less punishing first hour back on Indian soil.",
        "tags": ["travel", "airports", "india", "infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Prix Versailles 2026 airports listing", "url": "https://www.travelandtourworld.com/news/article/adani-airport-holdings-navi-mumbai-guwahati-prix-versailles-2026/"},
            {"name": "Press Information Bureau — Ministry of Civil Aviation", "url": "https://pib.gov.in/PressReleasePage.aspx"},
            {"name": "Wikipedia — Navi Mumbai International Airport", "url": "https://en.wikipedia.org/wiki/Navi_Mumbai_International_Airport"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "Navi Mumbai International Airport, recognized in the Prix Versailles 2026 listing of the world's most striking airport terminals.",
        "image_attribution": "Wikimedia Commons",
        "body": """Two of India's newest airport terminals have landed on a list usually dominated by Singapore, Doha and the marquee hubs of East Asia. Navi Mumbai International Airport and Terminal 2 of Guwahati's Lokpriya Gopinath Bordoloi International Airport were both named in the **Prix Versailles 2026** selection of the world's most visually striking airports — a recognition presented annually at UNESCO headquarters in Paris. It is a small headline with a large implication for the diaspora: India is no longer just adding airport capacity, it is building terminals good enough to compete on design with the gateways NRIs already admire on their layovers.

## Why an architecture prize matters to a tired traveler

For most Indian Americans, the airport is the punishing bookend of the trip home. You step off a flight from San Francisco or Newark, exhausted, into immigration halls that were built for a fraction of today's traffic. The Prix Versailles is, on its face, about architecture — Navi Mumbai and Guwahati were honored alongside new terminals in Guangzhou, Frankfurt, Pittsburgh and San Diego. But the awards explicitly reward terminals that pair design with passenger-focused flow and sustainability. In practice, the airports winning this recognition are the ones with the wider concourses, the faster immigration layouts, and the natural light that makes a 3 a.m. arrival feel survivable.

## The bigger build-out behind the headline

The two award winners are part of a genuinely large expansion. Navi Mumbai, developed by Adani Airport Holdings, is designed to take pressure off the saturated Chhatrapati Shivaji Maharaj International Airport across the bay — a relief that matters to the enormous Maharashtrian and Gujarati diaspora in the US who funnel through Mumbai. Guwahati's new terminal opens the door wider to the Northeast, a region that has historically been hard to reach for visiting family. And these sit within a national push: the government has inaugurated or expanded airports at Navi Mumbai, Patna, Tuticorin, Purnea, Amravati and others, while a brand-new gateway at Noida (Jewar) has just begun commercial flights to decongest the Delhi NCR region.

## What it changes for the diaspora

The practical payoff is choice. For decades, an NRI flying home had essentially two world-class options — Delhi's Terminal 3 and the newer parts of Bengaluru — and a long list of airports that felt like an endurance test. A wave of modern terminals changes the calculus. A traveler with roots in Pune or Nashik may soon prefer routing through Navi Mumbai over the older Mumbai terminal. Families visiting Assam and the Northeast get a far more comfortable point of entry. And as more of these airports add international-grade immigration capacity, the bottleneck that turns a long-haul arrival into a two-hour queue starts to ease.

There is also a quieter signal here about where India sees itself. Airports are the first thing a returning NRI touches and the first thing a foreign-born grandchild remembers. For years, the gap between the polished hubs of the Gulf and Southeast Asia and India's own gateways was a small, recurring embarrassment for the diaspora. Terminals that now win design prizes in Paris narrow that gap.

## What to watch next

Recognition is not the same as a finished network. Several of these airports are still ramping up international service, and immigration staffing — not terminal beauty — remains the real determinant of how fast you get through. The Navi Mumbai and Noida gateways in particular will be worth tracking over the next year as carriers decide how much long-haul capacity to shift toward them. For now, the diaspora can take a modest pleasure in a list from Paris: the airport at the end of the journey home is, finally, becoming a destination worth arriving at."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indians Can Now Get Global Entry — but a Government Shutdown Showed Why You Still Need a Backup Plan",
        "subheadline": "The Trusted Traveler program that lets Indian citizens skip the customs line is open and worth the $100. Here's how to apply through the embassy, and why this winter's suspension is a warning.",
        "slug": make_slug("global-entry-indian-citizens-trusted-traveler-tsa-precheck-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian citizens on green cards and visas who fly the US-India route several times a year can cut the customs line to minutes with Global Entry — but the program's recent shutdown-driven suspension is a reminder for NRIs to keep TSA PreCheck and extra connection time as a fallback.",
        "tags": ["travel", "visa", "airports", "global-entry"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. Customs and Border Protection — Global Entry eligibility", "url": "https://www.cbp.gov/travel/trusted-traveler-programs/global-entry"},
            {"name": "Embassy of India, Washington DC — Global Entry Program", "url": "https://www.indianembassyusa.gov.in/"},
            {"name": "Travel + Leisure Asia — India's new visa service provider in the UAE", "url": "https://www.travelandleisureasia.com/in/news/india-new-visa-passport-service-provider-uae/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32223420/pexels-photo-32223420.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Travelers wait in a passport control line — the kind of queue Global Entry members bypass at US airports.",
        "image_attribution": "Pexels",
        "body": """For the frequent flyer on the US-India route, the worst part of coming back is not the 16 hours in the air — it is the customs hall at the other end, where a planeload of jet-lagged passengers funnels into a single snaking line. Indian citizens have a way around it that is still underused: **Global Entry**, the US Customs and Border Protection Trusted Traveler program that India joined as the eleventh eligible country. If you hold an Indian passport and fly to America regularly, it is one of the best $100 you can spend — with a caveat that this winter made painfully clear.

## How it works, and what it gets you

Global Entry lets pre-approved, low-risk travelers skip the traditional inspection line and clear customs at an automated kiosk. You scan your passport, get photographed, complete the customs declaration on screen, and walk to baggage claim. The more than four million members bypass the queues that swallow everyone else. Crucially for the diaspora, membership also includes **TSA PreCheck**, the expedited domestic security screening that keeps your shoes on and your laptop in the bag — a real perk if your India trip connects through a US hub.

Membership is valid for five years and costs a non-refundable $100. The catch for Indian citizens is that the application has an extra step compared with US passport holders. You first create an account and apply through CBP's online portal at ttp.dhs.gov. Then — and this is the India-specific part — you must complete a background verification through the Indian government's portal before your application can proceed, after which you submit documents and attend an in-person interview at an enrollment center. The Embassy of India in Washington and the consulates in Atlanta, Chicago, Houston, New York and San Francisco all facilitate the process.

## The warning from this winter

Here is the part that should temper your enthusiasm. During the federal government shutdown earlier this year, the Department of Homeland Security **suspended Global Entry arrival processing nationwide** as an emergency cost-conserving measure, prioritizing core security operations over what it called facilitative programs. TSA PreCheck kept running, but the marquee benefit of Global Entry — the fast customs lane — simply went dark for a stretch, with no clear timeline for resumption. For an NRI who had built a tight connection around skipping the customs line, that was a nasty surprise.

The lesson is not to skip Global Entry; it is to treat it as a convenience, not a guarantee. Keep enough buffer in your connections that a suspended lane does not blow up your itinerary, and lean on TSA PreCheck, which proved more resilient. The membership still pays for itself across five years of US-India trips — just do not architect a one-hour domestic connection on the assumption the fast lane will always be open.

## A parallel shift for NRIs in the Gulf

There is a related change worth flagging for the large Indian community in the UAE, many of whom fly onward to the US. India has appointed a new outsourced consular service provider in the UAE: BLS International and SGIVS Global will process applications only until June 30, 2026, after which **Al Hind Tours and Travels LLC** takes over passport renewals, visa applications, OCI cards — and Global Entry Programme verification. If you are based in the Emirates and planning to enroll, factor the handover into your timing so your paperwork does not get caught in the transition.

## Bottom line

Global Entry remains a high-value upgrade for any Indian citizen who flies to the United States more than once or twice a year. Apply early — the background verification and interview scheduling can take weeks — route your application through the right consulate, and pair it with a realistic connection buffer. The fast lane is excellent when it is open. The travelers who came through this winter unscathed were the ones who did not bet the whole trip on it."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
