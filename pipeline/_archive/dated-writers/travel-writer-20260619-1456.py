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
        "headline": "India's New 10-Year E-Visa Is Live — and It Quietly Solves the Diaspora's Mixed-Passport Headache",
        "subheadline": "From June 1, US and UK passport holders can hold a decade-long e-visa for India. For NRI families where the kids carry American passports, the annual visa scramble is over.",
        "slug": make_slug("india-10-year-evisa-us-uk-citizens-nri-family-mixed-passport"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Most NRI households are split-passport — Indian-born parents on OCI, US-citizen children who still need a visa to enter India; the new 10-year e-visa means those kids no longer need a fresh application before every trip home.",
        "tags": ["travel", "visa", "evisa", "india", "nri", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Atlas Guide Travel News", "url": "https://atlas-guide.com/india-10-year-e-visa-us-uk-citizens"},
            {"name": "Consulate General of India, San Francisco — E-Visa", "url": "https://cgisf.gov.in/page/e-visa/"},
            {"name": "Fragomen — India E-Visa Program Expanded", "url": "https://www.fragomen.com/insights/e-visa-program-to-be-expanded.html"},
            {"name": "Government of India — Indian Visa Online", "url": "https://indianvisaonline.gov.in/evisa/tvoa.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1058959/pexels-photo-1058959.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An international airport terminal, where e-visa holders now clear dedicated counters in Delhi and Bengaluru",
        "image_attribution": "Pexels",
        "body": """India's Ministry of Home Affairs has rolled out a 10-year electronic visa for US and UK passport holders, a change that took effect on June 1 and applies equally to first-time applicants and renewals. It is the longest-validity e-visa India has ever offered, and for the Indian American diaspora it lands squarely on a problem most families have lived with for years.

The new visa permits stays of up to 180 days per visit for tourism, business or medical purposes. Applicants still complete the standard online form, upload a digital photograph and a passport scan, and wait the usual 72 hours for processing. An expedited 24-hour option is available for an extra $30. The visa cannot be used for employment or long-term study, and border officers retain the right to deny entry to anyone who cannot show onward tickets or sufficient funds.

## Why this matters to NRI families

The headline number — ten years — is not the real story for the diaspora. The real story is the passport split inside the average NRI household. Parents who emigrated from India typically carry Indian passports or hold an Overseas Citizen of India (OCI) card, which already lets them enter without a fresh visa. Their children, born in the United States, are American citizens. Under the old rules, those US-citizen kids needed a tourist visa for every visit to grandparents in Hyderabad or a cousin's wedding in Pune — and the standard tourist e-visa carried short validity, forcing a new application before nearly every trip.

A ten-year visa changes the rhythm of family travel. A child who gets the e-visa at age eight is covered through high school. A graduate student who lands one before a summer trip does not have to reapply for the next several India runs. For families that travel home every year or two, that is one less piece of paperwork in an already crowded pre-trip checklist.

## The fine print that still bites

The 180-day cap is per visit, not per year, but immigration officers can and do scrutinise travellers who appear to be living in India on a tourist document. The visa does not confer any work or study rights — an NRI returning to take a job or enroll in a university still needs the correct category. And the e-visa remains unavailable to anyone of Pakistani origin, who must apply for a regular paper visa at an Indian mission.

There is also the question of which document to carry. Indian consulates have long advised that if an e-visa was issued against an old passport, the traveller must carry that old passport alongside the new one. With a ten-year validity, the odds of a passport renewal mid-visa go up sharply, so families should keep the original travel document handy rather than assume the electronic authorisation travels automatically to a new booklet.

## Part of a wider opening

The 10-year visa is the most generous piece of a broader liberalisation. India has expanded its e-Visa program to 166 countries this year under the "Visit India 2026" campaign, added new ports of arrival including Coimbatore, Mangalore and Pune, and stood up dedicated e-visa counters that officials say have shaved roughly three minutes off average immigration clearance in Delhi and Bengaluru during peak morning banks. The government has signalled it intends to extend the longer-validity scheme to Canadian and Australian passport holders later this year — which would sweep in two more of the largest diaspora populations.

For now, the move is squarely aimed at the US and UK, home to the two biggest concentrations of people of Indian origin outside India. Analysts expect a measurable bump in repeat visits, with one estimate putting the rise in bookings from those two markets at around 15 percent through 2027.

## What to do now

If your family includes US or UK citizens who travel to India even occasionally, apply through the official portal at indianvisaonline.gov.in rather than any intermediary — consulates warn repeatedly against agents who promise "express" service for a fee. Build in the four-day minimum lead time the system requires, keep the confirmation and the passport used for the application together, and treat the ten-year window as exactly that: a decade in which the trip home is one form shorter.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Mumbai–Bengaluru Vande Bharat Sleeper Just Got Its First Look — and It Reshapes the Overnight Run South",
        "subheadline": "Private cabins, a 14-to-16-hour timetable and 823 berths: the sleeper version of India's flagship train is about to make the Mumbai–Bengaluru corridor a serious alternative to flying.",
        "slug": make_slug("mumbai-bengaluru-vande-bharat-sleeper-train-first-look-nri-rail"),
        "category": "travel",
        "vertical": "infrastructure",
        "diaspora_angle": "NRIs visiting family split between Mumbai and Bengaluru — two of the biggest landing points for the US and Gulf diaspora — finally get a premium overnight train that saves a domestic flight and a hotel night between the two cities.",
        "tags": ["travel", "railways", "vande-bharat", "india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Curly Tales — Mumbai-Bengaluru Vande Bharat Sleeper First Look", "url": "https://curlytales.com/mumbai-bengaluru-vande-bharat-sleeper-train-first-look/"},
            {"name": "Wikipedia — Vande Bharat Sleeper Express", "url": "https://en.wikipedia.org/wiki/Vande_Bharat_Sleeper_Express"},
            {"name": "Indian Railways / Integral Coach Factory", "url": "https://icf.indianrailways.gov.in/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
        "image_caption": "A Vande Bharat Express trainset near Mumbai; the new sleeper variant will run the overnight Mumbai–Bengaluru corridor",
        "image_attribution": "Wikimedia Commons",
        "body": """The first images of India's Mumbai–Bengaluru Vande Bharat Sleeper trainset are out, and they confirm what rail watchers have been anticipating since the spring: the country's flagship train is finally getting a proper overnight version, and it is launching on one of the busiest intercity corridors in the south.

The reveal, circulated this week, shows a 16-coach, fully air-conditioned rake built to carry 823 passengers. The first-AC coaches feature private cabins with sliding doors, internal stairs to the upper berths, and soft-toned premium interiors that look closer to a European night train than the Rajdhani sleepers most travellers grew up with. The trainset uses advanced suspension intended to smooth out the ride — a meaningful upgrade on a route that winds through the Western Ghats.

## A 14-hour answer to a 20-hour problem

The headline operational change is time. The Mumbai–Bengaluru rail journey today runs well over 20 hours on most services. The Vande Bharat Sleeper is expected to compress that to roughly 14 to 16 hours, running via Tumakuru, Davangere, Haveri, Hubballi-Dharwad and Belagavi with a deliberately limited set of stops to protect the timetable.

That puts it in genuine competition with the overnight choices NRIs and domestic travellers actually weigh: a late flight plus airport transfers and a hotel, or a long, dated overnight train. A premium sleeper that departs in the evening and arrives the next morning — with a real bed behind a closing door — collapses a travel day and a hotel night into a single fare.

## Why the corridor matters to the diaspora

Mumbai and Bengaluru are not random dots on India's map for the diaspora. Mumbai is a primary gateway for Gulf and European traffic; Bengaluru has become the south's main long-haul hub, now drawing nonstop service from carriers reaching the US West Coast and Europe. A very large share of NRI families have roots or relatives split across Maharashtra and Karnataka — the classic pattern of a wedding in one city and parents in the other.

For those travellers, the domestic leg between the two has long been the annoying part of the trip: a short but pricey flight that still eats half a day once you add airport time on both ends. A comfortable overnight train that you board after dinner and leave after breakfast is, for many families with children and elderly parents, a less exhausting option than a 6 a.m. domestic flight — and it sidesteps the monsoon-season flight delays that plague western India in July and August.

## Where it fits in the bigger rollout

The Mumbai–Bengaluru rake is part of a deliberate national push. Indian Railways launched its first commercial Vande Bharat Sleeper service — Howrah to Kamakhya in the northeast — in January, and has said it intends to roll out 12 sleeper trainsets by March 2027. The trains are designed and built domestically at the Integral Coach Factory in Chennai under the Make in India programme, the same line that has turned out the seated Vande Bharat fleet now running on dozens of corridors.

For the diaspora specifically, the sleeper expansion is part of the same story as the seated Vande Bharats that have already cut journey times on tourist routes like Jammu–Srinagar and the temple runs of Uttar Pradesh. Faster, cleaner, more reliable rail makes the in-India portion of a homecoming trip far less of a grind — and a premium overnight option between two diaspora-heavy metros is one of the most useful additions yet.

## What's still unconfirmed

Indian Railways has not published a firm commercial launch date or fare table for the Mumbai–Bengaluru sleeper, and timings remain "expected" until the Commissioner of Railway Safety signs off and the operating schedule is finalised. Travellers planning a winter trip should watch for the official booking window to open on the IRCTC platform rather than rely on the leaked first-look images. But the direction is clear: the overnight run south is about to get a serious upgrade, and it is aimed at exactly the corridor the diaspora uses most.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ladakh Is Quietly Becoming India's Next Must-Do Trip — and a New Tunnel Is About to Make It a Year-Round One",
        "subheadline": "At India's biggest travel trade show, Ladakh pitched itself as a rising global hotspot. For NRI families chasing a high-altitude escape from the summer heat, the timing is right.",
        "slug": make_slug("ladakh-rising-destination-zoji-la-tunnel-nri-summer-escape"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "For NRIs who already do the annual India trip but want more than family obligations, Ladakh offers a cool, dramatic, English-friendly add-on — and improving road and air access is making it viable even for families travelling with kids and older parents.",
        "tags": ["travel", "ladakh", "india", "destinations", "nri", "adventure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Tourism Cairns News — Ladakh & New Delhi Shine at SATTE 2026", "url": "https://tourismcairns.com.au/ladakh-new-delhi-satte-2026/"},
            {"name": "Press Information Bureau — Tourism initiatives", "url": "https://pib.gov.in/"},
            {"name": "TravelBiz Monitor — Tourism, Culture & Heritage", "url": "https://www.travelbizmonitor.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Pangong_Tso%2C_Ladakh_%2827988698864%29.jpg/1280px-Pangong_Tso%2C_Ladakh_%2827988698864%29.jpg",
        "image_caption": "Pangong Tso, the high-altitude lake that anchors most Ladakh itineraries",
        "image_attribution": "Wikimedia Commons",
        "body": """At SATTE 2026, India's largest travel trade gathering, one destination kept coming up in conversations that usually centre on Rajasthan palaces and Kerala backwaters: Ladakh. The union territory used the event to present itself as a rapidly rising global tourism hotspot — and for the diaspora, it is one of the more compelling pitches in years.

Ladakh's appeal is not subtle. Pangong Tso, Nubra Valley, Leh town and the Khardung La pass remain the flagship draws, combining cinematic, high-altitude landscapes with easy add-on experiences like short treks and monastery visits. The pitch at SATTE widened the map to include Magnetic Hill, Tso Moriri, Hemis Monastery, Shanti Stupa, Zanskar Valley, Lamayuru and the war-memorial town of Drass — a circuit of culture, history and scenery that few other Indian destinations can match in a single trip.

## The tunnel that changes everything

The single most consequential development for travellers is infrastructure. The Zoji La Tunnel, under construction on the Srinagar–Leh corridor, is designed to give Ladakh all-weather connectivity. At over 14 kilometres and built as a bi-directional tunnel, it is engineered to keep open a route that currently shuts for several months each year under heavy snow.

That matters because Ladakh's biggest limitation has always been its season. For most of the year the region is effectively reachable only by air into Leh, and the spectacular overland routes close in winter. An all-weather tunnel stretches the viable travel window, smooths out the road journey, and — critically for families — reduces the reliance on a single daily flight bank into a high-altitude airport prone to weather cancellations. Officials also pointed to expanding road infrastructure from Leh out to remote border valleys, spreading visitors beyond the handful of overcrowded marquee sites.

## Why it fits the diaspora trip

For NRI families, Ladakh solves a specific problem. The standard India trip is built around relatives and rituals — necessary, but rarely restful. Adding a few days in Ladakh turns an obligation trip into something closer to a real holiday, and it does so without leaving the country or needing another visa.

The timing works, too. As India's plains bake through the summer, Ladakh stays cool and dry — a genuine high-altitude escape at the exact moment most diaspora families are travelling during school breaks. English is widely spoken in the tourism trade, the experiences scale from gentle (monastery visits, lakeside stays) to serious (multi-day treks), and the region photographs like nowhere else in India, which matters to a generation that travels with a camera roll in mind.

One caution is real and worth planning around: altitude. Leh sits at roughly 3,500 metres, and itineraries that climb to Khardung La or Pangong go considerably higher. Families travelling with young children or older parents should build in a full acclimatisation day or two in Leh before attempting the high passes, and consult a doctor about altitude medication before the trip.

## A niche worth watching

Ladakh also showcased a distinctive draw at the trade show: dark-sky tourism. Hanle, home to the Indian Astronomical Observatory and one of the world's highest optical telescopes, sits under some of the clearest night skies in the country. The blend of astrophotography, stargazing and surrounding monastery culture is turning Hanle into a fast-growing, if still niche, addition to Ladakh itineraries — the kind of bucket-list experience that travels well in diaspora WhatsApp groups.

The push is backed by national policy. This year's Union Budget leaned hard into experience-led, sustainable tourism, with mountain trails earmarked across Himachal, Uttarakhand and Jammu & Kashmir and immersive sound-and-light shows planned for heritage sites including Leh. The throughline is consistent: India wants visitors to go beyond the Golden Triangle, and it is putting infrastructure behind the ambition.

For NRIs plotting this year's or next year's trip home, the practical takeaway is to treat Ladakh as a serious add-on rather than a someday destination. Book Leh flights early, build the itinerary around acclimatisation, and watch the Zoji La tunnel timeline — because once that route is all-weather, the region's brief, crowded season becomes a much longer, easier window.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
