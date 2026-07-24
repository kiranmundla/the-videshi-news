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
        "headline": "75,000 Indians Left the UK Last Year — and Britain Keeps Making It Harder to Stay",
        "subheadline": "Visa fees up 25 percent, student numbers cratering, and a settlement path that now stretches to 20 years. For the million-strong Indian community in Britain, the message from Westminster is getting louder.",
        "slug": make_slug("uk-indian-exodus-visa-fees-ilr-tightening"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Directly affects UK-based NRIs, Indian students considering UK education, and US-based families advising relatives on study-abroad options. The UK was the second most popular destination for Indian students after the US — that calculus is shifting fast.",
        "tags": ["travel", "uk", "visa", "students", "immigration", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "DevDiscourse / ONS Data", "url": "https://www.devdiscourse.com/article/politics/3916702-indian-students-workers-lead-exit-trend-as-uk-net-migration-falls"},
            {"name": "Leverage Edu", "url": "https://leverageedu.com/blog/uk-student-visa/"},
            {"name": "NBot Indian Diaspora Pulse", "url": "https://nbot.ai"},
            {"name": "UK Home Office Fee Order 2026", "url": "https://www.legislation.gov.uk/ukdsi/2026/9780348271348"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16771428/pexels-photo-16771428.png",
        "body": """Britain used to be the obvious choice. For decades, Indian families treated a UK degree the way previous generations treated an IAS posting — as proof that you'd made it. Oxford, Cambridge, Imperial, LSE: the names carried weight in every drawing room from Chandigarh to Chennai.

That era is ending, and the numbers tell the story with brutal clarity.

## The Exodus, by the Numbers

The UK's Office for National Statistics released its latest net migration data in late May, and Indians topped the charts — but not in the way anyone in Delhi or London would celebrate. Around 51,000 Indians who had come to study left Britain last year. Another 21,000 who came for work did the same. Add 3,000 who left for unspecified reasons, and you get 75,000 Indians walking away from the UK in a single year.

They weren't deported. They chose to leave.

The UK's overall net migration has dropped to 171,000 — down from a Conservative-era peak of 944,000. Home Secretary Shabana Mahmood called it "restoring order and control." For the Indian families who packed their bags, it felt more like being shown the door.

## What Changed

The squeeze started in January 2024, when the UK banned most student dependants. Only PhD and postgraduate research students can now bring family members. That single policy change slashed dependant applications by 86 percent.

Then came the fee hikes. From April 8, 2026, a student visa costs £558 (up from £524). A six-month visitor visa is £135. A Skilled Worker visa runs £819 for up to three years. Indefinite Leave to Remain — the UK's equivalent of a green card — now costs £3,226 per applicant. For a family of four, that's nearly £13,000 just for the settlement application, before you count the Immigration Health Surcharge at £776 per person per year.

The Electronic Travel Authorisation fee jumped 25 percent, from £16 to £20. Even short visits got more expensive.

But the real blow is structural. The UK is moving toward what it calls "earned settlement," stretching the path to permanent residency from five years to potentially 10 or even 20. The Graduate Route visa — the post-study work permit that made UK education attractive in the first place — is being cut from two years to 18 months starting January 2027. And universities now face stricter compliance rules: maintain 95 percent enrollment, 90 percent completion rates, and under 5 percent visa refusal rates, or risk losing their sponsor licence entirely.

## The Ripple Effect on Indian Students

The consequences are already measurable. Indian student visa grants to the UK fell 26 percent in 2024 compared to 2023. China has reclaimed the top spot as the UK's largest international student source, with 102,940 visas to India's 88,860.

The decline isn't just at the master's level, where dependant restrictions hit hardest. Undergraduate numbers are falling too — a signal that Indian families are rethinking the UK altogether, not just adjusting around one policy.

Where are they going instead? Canada and Australia remain popular despite their own tightening. The US continues to dominate for graduate education. But some families are looking closer to home — at IITs, IIMs, and Indian universities whose global rankings have climbed steadily.

## Why This Matters to NRIs in America

For the 4.4 million Indian Americans, this isn't abstract. Many have siblings, cousins, or children considering UK education. The advice from London-based relatives has shifted from "come here, it's worth it" to "think carefully."

It also mirrors trends NRIs are watching at home. The US adjustment-of-status upheaval, the EB-2 India retrogression, the rising cost of H-1B renewals — the pattern is the same across the Anglosphere: countries that once competed for Indian talent are now competing to make immigration harder.

For families weighing whether to send a child to the UK for a master's degree, the math has changed. A one-year program at a mid-tier London university costs £25,000-35,000 in tuition, plus £15,000-20,000 in living expenses, plus £558 in visa fees, plus £776 in health surcharge — and you get 18 months of post-study work instead of two years, no dependants, and a settlement path measured in decades.

The UK is still excellent for certain programs. Oxbridge remains Oxbridge. But for the broader Indian student market, Britain is pricing itself out of the conversation — and 75,000 departures in a single year suggest many have already done the arithmetic."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Vande Bharat Sleeper Kills the Waitlist — Confirmed Tickets Only, Fares Above Rajdhani",
        "subheadline": "The new overnight trains promise confirmed berths, no RAC, and 16-coach comfort at 130 kmph. For NRIs used to dreading Indian Railways, this might actually be worth trying.",
        "slug": make_slug("vande-bharat-sleeper-confirmed-tickets-no-rac-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India often avoid trains because of the RAC/waitlist chaos and aging Rajdhani stock. Vande Bharat Sleeper's confirmed-only policy and premium comfort could change that, especially for families visiting multiple cities during a 2-3 week India trip.",
        "tags": ["travel", "india", "railways", "vande-bharat", "trains", "infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Glance/News9 (Vande Bharat Sleeper Details)", "url": "https://trends.glance.com/newz/astrology/IN/en/news9/"},
            {"name": "WhispersInTheCorridors (52 Railway Reforms)", "url": "https://whispersinthecorridors.in/detail/153429-Railways+To+Initiate+52+major+reforms+in+2026.html"},
            {"name": "WhispersInTheCorridors (₹2.78 Lakh Crore Budget)", "url": "https://whispersinthecorridors.com/detail/153396-Record+2.78+Lakh+Crore+Boost+Indian+Railways+Eyes+High-Speed+Revolution+in+2026-27+Budget.html"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
        "body": """Every NRI who has tried to book an Indian train ticket for a family trip home knows the ritual: check IRCTC, see "WL 47," try Tatkal at 10 AM sharp, lose to the bots, give up and book a flight for five times the price.

Indian Railways just made an argument for trying again.

## No Waitlist. No RAC. Confirmed or Nothing.

The Vande Bharat Sleeper — India's new premium overnight train — has broken with one of Indian Railways' most entrenched traditions. There is no Reservation Against Cancellation. There is no waitlist. If you have a ticket, you have a berth. If the train is full, the booking simply won't go through.

This is not how Indian trains have worked for 170 years. The RAC system, which crams two passengers onto a single berth in the hope that someone cancels, has been the default since most NRIs' grandparents were booking tickets at the station window. Killing it for Vande Bharat Sleeper is a statement: this train is not the Rajdhani with new paint. It's a different product.

## What You Get

The 16-coach trains run at 130 kmph — not bullet-train territory, but fast enough to cut meaningful time off overnight routes. The first service, Guwahati to Howrah, is already operational. Mumbai to Bengaluru is next, promising to shrink a journey that currently takes 22 hours on Rajdhani down to 15-17 hours.

Inside, the trains offer wider berths, better suspension, improved air conditioning, and modular bio-toilets. The coaches are purpose-built for overnight comfort rather than adapted from daytime seating configurations. Every berth is a confirmed berth.

The fares are higher than Rajdhani. Indian Railways has set a minimum distance charge equivalent to 400 kilometres, which means short hops won't be offered on these routes. This is for intercity overnight travel — Delhi to Mumbai, Chennai to Bengaluru, Kolkata to Guwahati — the routes where NRIs most often need to move between family bases.

## The Bigger Picture: ₹2.78 Lakh Crore and 52 Reforms

Vande Bharat Sleeper isn't an isolated launch. It sits inside the most ambitious railway modernization India has attempted.

The 2026-27 Union Budget allocated ₹2.78 lakh crore to Indian Railways — a 15-20 percent increase over last year and the largest railway budget in Indian history. The money is going toward expanded Vande Bharat services, full electrification of the network, and the rollout of Kavach 4.0, an indigenous automatic train protection system designed to prevent collisions.

Railway Minister Ashwini Vaishnaw has announced 52 major reforms under what the ministry calls "Reform Express." By the end of 2026, Vande Bharat sleeper trains are expected to begin replacing Rajdhani Express on key routes. Mass production of 24-coach Vande Bharat sleepers is underway. Hydrogen-powered trains are in development for regional routes.

Maharashtra alone is receiving ₹24,000 crore for railway infrastructure, including high-speed corridor work. Uttar Pradesh gets over ₹20,000 crore. The Northeast — long the network's weakest link — is receiving ₹11,486 crore, including a 40-kilometre underground track section.

## What This Means for NRIs

For NRIs planning a multi-city India visit — landing in Delhi, spending a few days with family in Lucknow, then heading to Varanasi before flying home from Mumbai — the domestic travel logistics have historically been the worst part of the trip. Flights are expensive and unreliable during peak season. Trains were uncomfortable and unpredictable. Driving was exhausting.

Vande Bharat Sleeper changes the equation for specific corridors. A confirmed overnight berth from Mumbai to Bengaluru, arriving refreshed in the morning, is genuinely competitive with a flight when you factor in airport time, delays, and the midnight taxi to a distant terminal.

The confirmed-ticket policy matters most. NRIs booking from abroad, weeks in advance, need certainty. "Your ticket is confirmed" means you can plan around it. "WL 23" means you're checking IRCTC every morning during your vacation wondering if you should book the backup flight.

## The Catch

Availability. These trains are new and routes are being added gradually. The first few months will see heavy demand and limited frequency. Booking windows will be competitive, especially around Diwali, Christmas, and summer — exactly when NRIs travel.

Fares above Rajdhani also mean these trains are targeting a premium segment. For NRIs, the prices are still trivial compared to the US-India flight that got them there. For domestic travelers, it's a different calculation.

But the direction is clear. Indian Railways is building a two-tier system: premium confirmed travel on Vande Bharat, and the traditional network for everything else. For NRIs who abandoned trains a decade ago, it might be time to check IRCTC again."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Monsoon Destinations That Justify Dragging Your NRI Family to India in July",
        "subheadline": "Monsoon hit Kerala five days early this year. Hotel prices are half of what they'll be in December. Ayurveda works better in the humidity. Here's where to go — and why your American kids might actually enjoy it.",
        "slug": make_slug("monsoon-india-destinations-nri-families-july"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI families typically visit India in December or summer break. Monsoon season (June-September) offers dramatically lower prices, unique experiences like Ayurveda and monsoon treks, and thinner tourist crowds — but most NRIs don't even consider it. This guide makes the case.",
        "tags": ["travel", "india", "monsoon", "kerala", "goa", "family", "destinations"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-india/"},
            {"name": "InsideAsia Tours", "url": "https://insideasiatours.com/india/when-to-visit/"},
            {"name": "Ease India Trip (Kerala in June)", "url": "https://easeindiatrip.com/blog/visiting-kerala-in-june/"},
            {"name": "Medium / TripperTrails", "url": "https://medium.com/@trippertrails/best-places-to-visit-in-india-in-july"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17928231/pexels-photo-17928231.jpeg",
        "body": """Every NRI knows the December drill. Book the SFO-DEL ticket in August, overpay by $400 because it's peak season, land in Delhi fog, sit in Diwali-aftermath smog, and fight every other returning desi for the same Taj Mahal sunrise slot.

Here's an alternative: go in July.

India's monsoon arrived five days early this year, sweeping into Kerala on May 25 instead of the usual June 1. By mid-June, most of the country will be drenched, green, and — crucially — half the price. The same resort that charges ₹25,000 a night in December drops to ₹12,000. The same houseboat that's booked three months ahead in winter has openings next week.

Monsoon India is a different country. And for NRI families willing to trade sunshine for spectacle, it might be the better one.

## 1. Kerala: Ayurveda Actually Works Better in the Rain

This isn't marketing. Traditional Ayurvedic practitioners have prescribed monsoon-season treatments for centuries because the humidity opens pores and makes the body more receptive to Panchakarma therapies — the detox-and-rejuvenation protocols that Kerala is famous for.

Kochi and Alleppey are your entry points. The backwater houseboats run through rain-swollen canals framed by coconut palms so green they look retouched. Munnar's tea plantations disappear into mist every afternoon and re-emerge every morning like a nature documentary on loop. Wayanad, in northern Kerala, has recovered from the 2024 landslides and is welcoming visitors again — fewer crowds than Munnar, wilder forests, and misty mornings that your teenager will photograph whether they want to admit it or not.

**The NRI move:** Book a week at an Ayurvedic resort in Alleppey or Varkala. Combine it with a two-night houseboat cruise. Total cost for a family of four, including treatments: roughly what you'd spend on three days at a mid-range Maui hotel.

## 2. Goa: Empty Beaches and Half-Price Everything

Monsoon Goa is Goa's best-kept non-secret. The beach shacks in North Goa close for the season, the package tourists vanish, and what's left is the Goa that residents actually live in — lush green interiors, dramatic afternoon downpours followed by golden evenings, and restaurants that don't charge tourist markup.

The Sao Joao festival in late June is Goa's monsoon celebration: locals jump into wells and rivers, there's feni flowing freely, and the whole thing has a chaotic joy that December Goa's trance parties can't touch. Dudhsagar Falls, a trickle in winter, becomes a roaring cascade that justifies the muddy trek to reach it.

**The catch:** You can't swim in the ocean. Tides are high, currents are strong, and red flags are everywhere. But if your idea of Goa is pool villas, spice plantation tours, and reading on a covered veranda while rain hammers the tile roof, monsoon is perfect.

## 3. Valley of Flowers, Uttarakhand: The Trek Your Kids Will Remember

This UNESCO World Heritage Site in the Garhwal Himalayas only opens during monsoon. From mid-July through August, the valley floor erupts with over 600 species of wildflowers — Himalayan blue poppies, cobra lilies, marigolds, and orchids carpeting an alpine meadow framed by glaciers.

The trek from Govindghat is moderate: about 17 kilometres each way, manageable for fit teenagers. The nearby Hemkund Sahib gurdwara, at 4,329 metres, adds a spiritual and physical challenge.

**Why NRIs should care:** This is the India trip that doesn't exist in your parents' photo album. It's not temples and relatives' houses. It's genuinely world-class trekking in a landscape most Indians haven't seen. Your Bay Area kids who've done Yosemite and Zion will be legitimately impressed.

## 4. Udaipur: The Monsoon Palace Earns Its Name

Rajasthan in July sounds like a heat stroke waiting to happen. But Udaipur during monsoon is an exception. The lakes fill up — Lake Pichola, which is sometimes embarrassingly low in May, becomes the shimmering expanse that earned the city its "Venice of the East" nickname. The Sajjangarh Palace, literally called the Monsoon Palace, was built specifically for watching rain clouds roll across the Aravalli hills.

Temperatures drop to a pleasant 28-32°C. Hotel rates drop further. The City Palace, Jag Mandir, and the rooftop restaurants overlooking the lake are all less crowded and more atmospheric with storm clouds as backdrop.

**The NRI move:** Book a heritage hotel — Udaipur has dozens converted from havelis and minor palaces — and spend three days doing nothing but boat rides, palace walks, and rooftop dinners. This is the India that Instagram dreams about, at off-season prices.

## 5. The Western Ghats from Mumbai: Weekend Monsoon Escapes

If your India trip includes time in Mumbai, the Western Ghats are two hours away and transformed by rain. Lonavala and Mahabaleshwar offer waterfalls visible from the highway. Malshej Ghat brings flamingos and cloud-level drives. Matheran — India's only car-free hill station — is reached by toy train or a short trek through dripping forest.

These aren't week-long destinations. They're overnight escapes that break up the Mumbai humidity and give your family something to do besides visiting one more auntie.

## The Practical Bits

**Flights:** US-India fares are 20-30 percent cheaper in July than December. You're flying against the grain — most NRIs travel October through January.

**Packing:** Waterproof everything. Quick-dry clothes, a good rain jacket, waterproof phone case, and shoes that can handle mud. Leave the white sneakers at home.

**Health:** Mosquito repellent is mandatory. Carry oral rehydration salts. Drink bottled water, obviously, but this applies year-round.

**What to skip:** Beach holidays (ocean is dangerous), desert safaris (flooding risk in low-lying areas), and any destination that requires unpaved mountain roads (landslide season).

The monsoon isn't for everyone. But for NRI families who've done the December-India trip five times and are looking for something different — cheaper, greener, less crowded, and genuinely memorable — July might be the move your family didn't know it wanted."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
