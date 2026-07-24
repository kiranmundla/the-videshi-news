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
        "headline": "The US Work-Visa Queue in India Just Got Longer — and It's the H and L Lines, Not the Tourist One, That Are Jammed",
        "subheadline": "Appointment waits for H-1B and L visas have stretched to 75 to 125 days at every Indian consulate, even as visitor and student slots stay short. The fix the diaspora keeps reaching for — booking in a third country — is closing too.",
        "slug": make_slug("us-work-visa-h1b-l-backlog-india-75-125-days-consulate-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "For Indian American families and the companies that employ them, a stamping trip home now carries the risk of a three- to four-month wait before the interview even happens — long enough to derail a job start, a client onboarding, or a planned return flight.",
        "tags": ["travel", "visa", "us", "h1b", "immigration", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — Update on Visa Appointment Backlogs at U.S. Consulates in India", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-u-s-consulates-in-india.html"},
            {"name": "U.S. Department of State — Global Visa Wait Times", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/wait-times.html"},
            {"name": "Outlook Traveller — US To Offer Faster Visa Appointments Within 10 Days For An Additional Fee", "url": "https://www.outlooktraveller.com/destinations/international/us-to-offer-faster-visa-appointments-within-10-days-for-an-additional-fee"}
        ]),
        "score_total": 82,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport and visa documents on a desk; US work-visa interview waits in India have stretched past three months.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "published_at": now,
        "body": """Most coverage of America's visa crunch fixates on the tourist line. The real squeeze right now is somewhere less visible: the employment-based queue that the working diaspora actually depends on.

According to a fresh advisory from immigration firm Fragomen, U.S. consulates across India are running 75 to more than 125 days behind on appointments for H, L and other employment-based nonimmigrant visas. That covers all five posts — Chennai, Hyderabad, Kolkata, Mumbai and New Delhi. The reason is blunt: demand has climbed for months, and consular staffing has not.

## The split that matters

Here is the distinction the headlines miss. Visitor (B-1/B-2) and student (F-1) appointments are moving briskly — four to 22 days, per the same advisory. It is the H-1B and L-1 categories, the visas that move engineers, managers and intra-company transferees between India and the United States, where the calendar has seized up.

That inversion is unusual. For two years the visitor line was the nightmare, with B-1/B-2 waits in Mumbai once exceeding nine months. State Department data through this spring still showed visitor waits of roughly 10 months in Mumbai and well over a year in Hyderabad and New Delhi for first-time tourist applicants. But for the salaried diaspora doing a routine visa stamping while home in India, the binding constraint has shifted to the work categories.

## Why this lands hard on NRIs

An H-1B or L-1 holder who travels to India and lets their visa stamp lapse cannot re-enter the United States until they are re-stamped at a consulate. If the nearest appointment is 100 days out, that is 100 days stuck — missing a job start date, a project deadline, a child's school term, or the return leg of a ticket already paid for.

The people most exposed are precisely those who fly home most: tech workers on H-1B, managers on L-1, and their dependent families on H-4 and L-2. A summer trip to see parents in Hyderabad can quietly turn into a forced sabbatical if the stamp expires while abroad.

## The escape routes are narrowing

The diaspora's usual workaround — applying as a third-country national at a U.S. consulate outside India, often in a Gulf state or Southeast Asia — still exists, but it is getting expensive and slower. Fragomen notes Kolkata, which once had a 13-day backlog and was a favored fast lane, has ballooned to roughly 126 days. Third-country applications also carry the cost of extra flights and, frequently, a separate visa to enter the country where you are interviewing.

There is one more lever, but it is a pricey one. From July 1, the State Department is piloting a paid expedited-appointment service: eligible B-1/B-2 applicants can buy an interview within 10 business days for an extra $750 on top of the $185 fee. Crucially, the pilot as announced is aimed at visitor visas, not the H and L categories that are actually backed up — and the list of participating posts has not been published. It also buys a faster interview, not a faster decision; security and administrative reviews run on the same clock as before.

## What to do before you fly

For anyone on a work visa planning an India trip this year, the math has changed:

- **Check whether your visa stamp expires while you'll be abroad.** If it does, assume re-stamping in India could take three to four months and plan the trip around that, not the other way around.
- **Book the appointment before you book the flight.** The interview slot, not the airfare, is now the scarce resource.
- **Keep the interview-waiver (Dropbox) option in view.** Many renewing applicants qualify to drop documents rather than interview in person; eligibility has widened in recent years and avoids the in-person calendar entirely.
- **Carry the paperwork that speeds approval** — the I-797 approval notice, an employer letter, and proof of continued employment — so that once you reach the window, the case clears without an administrative hold.

The takeaway for the working diaspora is unglamorous but important: the visa system that gets the most attention is not the one most likely to strand you this summer. Plan for the work-visa queue, because that is the one that is jammed.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Western Ghats' Best Travel Season Lasts Only a Few Weeks — and It's the One Most Diaspora Visitors Skip",
        "subheadline": "Frog walks, firefly trails and night-biodiversity treks turn the monsoon rainforest into a destination in its own right. For NRI families used to chasing big mammals on a winter safari, it's a different way to see India — and 2026's lighter monsoon makes it safer.",
        "slug": make_slug("western-ghats-monsoon-frog-walks-biodiversity-trails-nri-2026"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "Diaspora families almost always visit India in the dry winter and never see the Ghats at full intensity; a monsoon trip offers a rare, kid-friendly nature experience that doesn't exist anywhere on the standard NRI itinerary.",
        "tags": ["travel", "monsoon", "western-ghats", "nature", "india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Better India — Inside the Western Ghats' Four-Month Monsoon Window", "url": "https://thebetterindia.com/"},
            {"name": "StayVista Journal — Agumbe Rainforest Trek 2026 Guide", "url": "https://www.stayvista.com/journal/agumbe-rainforest-trek"},
            {"name": "Wego Travel Blog — Best Monsoon Destinations in India 2026", "url": "https://blog.wego.com/best-monsoon-destinations-in-india/"}
        ]),
        "score_total": 70,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Mystic_Layers_of_Agumbe.jpg/1280px-Mystic_Layers_of_Agumbe.jpg",
        "image_caption": "Mist layers over the Agumbe hills in Karnataka's Western Ghats, the heart of India's monsoon rainforest belt.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "published_at": now,
        "body": """For decades, monsoon travel in the Western Ghats meant the same handful of crowded stops: a Mahabaleshwar viewpoint, a Munnar tea estate, the scrum at Dudhsagar Falls. That is starting to change — and the new version is far more interesting for the kind of trip an overseas Indian family rarely gets to take.

Across the Sahyadris and the rainforest belts of Karnataka, Maharashtra and Kerala, a quieter form of monsoon tourism has taken hold. Instead of postcard landscapes, travellers are signing up for frog walks, nocturnal biodiversity trails, firefly camps, birdwatching weekends and rainforest stays led by local naturalists. The catch — and the appeal — is that these experiences last only a few weeks each year.

## When the forest finally opens up

The Western Ghats are one of the planet's biodiversity hotspots, home to thousands of species found nowhere else. Most of them are invisible for nine months of the year. The first rains flip a switch: amphibians breed, forest streams revive entire microhabitats, and the canopy turns an almost electric green.

In Agumbe in Karnataka — long nicknamed the "Cherrapunji of the South" for its rainfall — naturalists guide small groups along wet trails after dark. Torches are kept dim. Visitors crouch beside leaf litter and waterlogged rocks while guides identify endemic species by call: the Malabar gliding frog, the dancing frog, colourful bush frogs, and, for the lucky, a Malabar pit viper coiled on a branch. Agumbe also holds India's densest king cobra population, radio-tracked from a research station there since 2008.

Amboli in Maharashtra and parts of Wayanad in Kerala run similar walks. The point is not adrenaline; it is a completely different understanding of biodiversity than the big-mammal safari most visitors know.

## Why this is the trip the diaspora never takes

Almost every NRI itinerary lands in the dry season — December weddings, January holidays, the predictable winter trip home. The Ghats in that window are pleasant but dormant. The diaspora simply never sees the rainforest at full volume.

That is the opportunity. For a family flying in from California or New Jersey with school-age kids, a two- or three-day monsoon nature trip is something genuinely new — and it doubles as the kind of slow, screen-free experience that is hard to engineer back home. Frog walks and firefly trails are low-exertion and well-suited to children, provided the group sticks with a registered Forest Department guide.

## 2026 is, oddly, a good year to try it

A heavier monsoon means landslides and road closures; a lighter one means clearer mornings and safer roads. The India Meteorological Department has forecast 2026 rainfall at about 92% of the long-period average — below normal — with Skymet near 94%. For comparison, the catastrophic 2024 Wayanad landslides came in a year that ran well above normal. A below-normal monsoon points to fewer washouts and more usable view-windows for travellers.

That said, the Ghats demand respect. The Chooralmala–Mundakkai area of Wayanad remains restricted after the 2024 landslides, and forest departments routinely close trekking routes and waterfall approaches during heavy spells to prevent flash-flood incidents.

## How to do it without getting it wrong

- **Go with a registered naturalist or Forest Department guide.** Many trails legally require one, and on a night walk it is the difference between a great trip and a dangerous one.
- **Pick your base by access, not Instagram.** Agumbe (reached via Udupi), Amboli and the Sringeri belt have homestays running roughly ₹1,200–4,000 a night, often including meals.
- **Time it after the official Kerala onset.** Waterfalls peak about 7–10 days after onset; biodiversity trails come alive after the first sustained rains.
- **Skip the risk zones.** Favour stable belts like Coorg's Madikeri side; avoid the landslide-prone Wayanad pockets and the most crowded ghat viewpoints in peak downpours.
- **Pack out everything.** These are fragile, protected ecosystems; the guides will tell you there are no bins in the forest for a reason.

The Western Ghats monsoon window is short, and that is exactly what makes it worth planning a trip around. For a diaspora used to seeing India dry, dusty and warm, the forest at full intensity is a side of home most of them have never met.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Kerala Spends the Monsoon Selling the One Thing the Diaspora Is Short On: Time to Heal",
        "subheadline": "The state's official tourism line is that June through August — peak rains — is the ideal season for Ayurvedic treatment, when the humid climate makes the body more receptive. With flights and rooms 30–50% cheaper, it's the most cost-effective wellness trip an NRI can take home.",
        "slug": make_slug("kerala-monsoon-ayurveda-wellness-season-nri-cheaper-2026"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "A monsoon Ayurveda trip lets time-starved overseas Indians combine a visit home with a structured wellness reset — at off-season fares and room rates that make the same retreat far cheaper than a winter booking.",
        "tags": ["travel", "kerala", "ayurveda", "wellness", "monsoon", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wego Travel Blog — Best Monsoon Destinations in India 2026", "url": "https://blog.wego.com/best-monsoon-destinations-in-india/"},
            {"name": "Curly Tales — 11 Best Monsoon Staycations Across India", "url": "https://curlytales.com/"},
            {"name": "Nativeplanet — Monsoon Travel Kerala 2026 Tips", "url": "https://www.nativeplanet.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Kerala_backwaters%2C_Houseboat%2C_India.jpg/1280px-Kerala_backwaters%2C_Houseboat%2C_India.jpg",
        "image_caption": "A houseboat on the Kerala backwaters; the state markets the monsoon as its prime Ayurveda season.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "published_at": now,
        "body": """Most travellers treat the monsoon as the season to avoid Kerala. Kerala's tourism establishment treats it as the season to sell. The two views are not in conflict — they just have different ideas about what a trip is for.

The state's official monsoon-tourism campaign has long promoted June through August, the heaviest stretch of rain, as the best window for Ayurvedic treatment. The logic, rooted in traditional practice, is that the cool, humid, low-dust climate opens the body's pores and makes it more receptive to therapies like Panchakarma — the multi-day detox-and-rejuvenation regimen at the core of serious Ayurveda. Karkidakam, the Malayalam month that falls roughly across July and August, is traditionally the season of rejuvenation, when households take herbal preparations and rest.

## Why the timing works for the diaspora specifically

The thing overseas Indians never have enough of is time, and Ayurveda is a treatment that rewards it. A genuine Panchakarma course runs one to three weeks; a single massage is a spa add-on, not therapy. The monsoon is precisely when reputable centres slow down, run full programmes, and have the staff bandwidth to supervise them properly.

It also happens to be the cheapest time to come. Domestic flight fares drop 30–50% against peak winter pricing on popular routes, and hotel and resort rates across India fall sharply from July through early September. For an NRI weighing a wellness retreat in Kerala against a comparable one in California or Europe, the monsoon booking is not just more authentic — it is dramatically less expensive, even after the long-haul ticket.

## What a monsoon Kerala trip actually looks like

The classic base is the southern coast — Kovalam and the Thiruvananthapuram belt — where retreats like Niraamaya's Surya Samudra pair sea views with backwater cruises, yoga and Ayurvedic therapy. Further north, the Bekal and Kochi areas offer fort walks, calmer beaches and backwater stays; mid-range monsoon rooms in these belts run from roughly ₹6,500 a night, with the marquee wellness resorts higher.

Between sessions, the monsoon landscape is the draw rather than a drawback. Munnar's tea plantations turn vivid green, Alleppey's backwaters swell for houseboat cruises, and the rain itself becomes part of the slowness the trip is supposed to deliver.

## The practical cautions

A monsoon wellness trip is restful by design, but Kerala in heavy rain still demands planning:

- **Choose a centre, not just a hotel.** Look for a GreenLeaf or OliveLeaf classified Ayurveda property, or a retreat with resident physicians and a structured programme — not a resort offering one-off "Ayurvedic massages."
- **Block real time.** A meaningful course needs a week or more; a two-day stopover is a spa visit, not a treatment.
- **Build in weather slack.** The IMD issues frequent heavy-rain alerts for coastal Kerala and the Western Ghats through the season; keep travel days flexible and avoid tight same-day connections to hill areas.
- **Mind the road trips.** Day excursions into the Ghats can be cut short by closures; treat them as bonuses, not anchors of the itinerary.
- **Book the off-season rate early.** The discounts are real, but the best retreats fill their monsoon Panchakarma slots well ahead.

For a diaspora that flies home for weddings and winters and rarely for itself, the monsoon offers an unfamiliar proposition: a trip built around recovery rather than obligation, in the one season the state actually recommends for it — and at the lowest prices of the year.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
