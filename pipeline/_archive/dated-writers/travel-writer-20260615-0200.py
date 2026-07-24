#!/usr/bin/env python3
"""Travel writer — 2026-06-15 02:00 UTC run. Three fresh travel articles for The Videshi."""
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
    # ─────────────────────────────────────────────────────────
    # ARTICLE 1: Air India Cabin Overhaul
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's Summer Cabin Overhaul Hits Eight Routes — First Class Included",
        "subheadline": "New Boeing 787-9s on Mumbai-London, first class suites on Delhi-Melbourne, and premium economy rolling out to Toronto and Bengaluru-London. The Tata-era product transformation starts in two weeks.",
        "slug": make_slug("air-india-summer-cabin-overhaul-first-class-routes"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying home this summer on Air India's busiest corridors — Mumbai-London, Delhi-Toronto, Bengaluru-London, Amritsar-Birmingham — will finally get premium cabins that compete with Emirates and Singapore Airlines.",
        "tags": ["travel", "airlines", "air-india", "first-class", "premium-economy", "cabin-upgrade"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CAPA - Centre for Aviation", "url": "https://centreforaviation.com/news/air-india-to-adjust-aircraft-on-eight-international-services-from-summer-2026"},
            {"name": "TTR Weekly", "url": "https://www.ttrweekly.com/site/2026/02/air-india-upgrades-cabin-experience/"},
            {"name": "The Traveler", "url": "https://thetraveler.org/air-india-brings-first-class-suites-to-delhi-melbourne-boeing-777-route/"},
            {"name": "Upstox", "url": "https://upstox.com/news/business/aviation/air-indias-international-makeover-more-flights-new-interiors-first-class-expansion/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
        "image_caption": "An Air India Boeing 787-9 Dreamliner at John F. Kennedy International Airport",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, the biggest complaint Indian Americans had about Air India wasn't the food or the delays — it was the seats. Fraying upholstery, broken entertainment screens, cabins that hadn't seen a refresh since the Maharaja was a government employee. That era is ending, and the calendar says July 1.

Starting next month, Air India will deploy aircraft with entirely new or retrofitted cabin interiors on eight international routes — most of them corridors that NRIs treat as lifelines between their American lives and Indian families. The changes span three cabin classes and two aircraft types, and they represent the most visible proof yet that Tata Group's multi-billion-dollar turnaround plan is reaching the passenger.

## Mumbai-London: The Flagship Gets a New Wardrobe

From July 1, Air India's flagship Mumbai-London Heathrow service switches from aging Boeing 777-300ERs to a combination of factory-new Boeing 787-9 Dreamliners and retrofitted 787-8s. Both feature all-new cabin interiors — the same product that debuted on Mumbai-Frankfurt in February to broadly positive reviews. The 787-9 in particular brings a three-class layout with business class seats that convert to fully flat beds, a new premium economy cabin, and refreshed economy seats with larger screens.

For the roughly 120,000 Indian Americans who fly the Mumbai-London corridor annually — many connecting onward to the US via British Airways or Virgin Atlantic — the upgrade means Air India finally competes on product, not just price and loyalty.

## Delhi-Melbourne: First Class Arrives

The boldest move is on Delhi-Melbourne. From July 1, the daily service shifts to upgraded Boeing 777-300ERs configured with eight first class suites, 40 fully flat business class beds, and 280 economy seats. The first class product is based on the well-regarded Etihad Diamond First suites — enclosed pods with sliding doors, beds stretching roughly two metres, and direct aisle access. It is the first time Air India has offered first class on any Australia route.

Melbourne is home to one of Australia's fastest-growing Indian communities. The state of Victoria now counts over 350,000 residents of Indian ancestry, and visitor numbers from India have seen double-digit growth year over year. The addition of first class — plus nearly 4,000 extra seats per month — positions Air India to capture high-yield corporate and affluent leisure traffic that currently defaults to Gulf carriers.

## August: UK Regionals, Toronto, and Bengaluru

From August 1, the transformation extends further:

- **Bengaluru-London Heathrow** gets retrofitted 787-8s with new interiors, introducing premium economy on the route for the first time. With this, every Air India flight to and from Heathrow will feature new or upgraded cabins.
- **Delhi-Toronto** deploys new 787-9 aircraft on seven of its ten weekly frequencies, bringing premium economy to Canada's busiest India corridor. Air India says more than 50 percent of its North America flights will then operate with new or upgraded cabins.
- **Delhi-Birmingham**, **Amritsar-Birmingham**, **Ahmedabad-London Gatwick**, and **Amritsar-London Gatwick** all receive 777-300ERs with first class suites — a startling upgrade for routes that historically operated with some of the airline's most tired equipment.

The Amritsar and Ahmedabad routes matter disproportionately to the Punjabi and Gujarati diaspora in the UK, communities that have long endured Air India's worst hardware because no other carrier offered nonstop alternatives from their home cities.

## What It Means for NRIs

The cabin overhaul doesn't fix everything. Air India still trails the Gulf three on lounges, ground handling, and on-time performance. Its app remains a work in progress, and frequent flyer redemptions can feel adversarial. But the hard product — the seat you sit in for 9 to 14 hours — is the one thing that matters most on a long-haul flight, and Air India is finally getting that right.

For NRIs booking summer trips home, the practical advice is simple: check your aircraft type before you book. Flights on 787-9 or retrofitted 787-8 equipment will deliver the new experience. Legacy 777s on some Toronto frequencies will not. The difference is night and day, and it's worth the extra click to confirm."""
    },

    # ─────────────────────────────────────────────────────────
    # ARTICLE 2: IndiGo Goes Global
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Now Flies to 46 Countries — How India's Budget Carrier Went Global",
        "subheadline": "From Reunion Island to Istanbul nonstop, and from Tbilisi to Manchester, IndiGo's A321XLR-powered expansion is giving NRIs affordable options their parents never had.",
        "slug": make_slug("indigo-46-countries-global-budget-airline-a321xlr"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who grew up thinking IndiGo only flew Delhi-Mumbai now have budget options to Istanbul, Athens, London, Manchester, Baku, and Reunion — routes that were exclusive to full-service carriers until this year.",
        "tags": ["travel", "airlines", "indigo", "a321xlr", "international-expansion", "budget-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/indigo-international-flights/"},
            {"name": "AeroRoutes", "url": "https://aeroroutes.com/2026/04/indigo-moves-forward-a321xlr-delhi-istanbul-service-to-april-2026/"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/indigo-adds-new-a321xlr-flights-to-istanbul/"},
            {"name": "Travel Trends Today", "url": "https://traveltrendstoday.in/indigo-deploys-second-a321xlr-on-delhi-istanbul-route/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1280px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo, the workhorse of India's largest airline",
        "image_attribution": "Wikimedia Commons",
        "body": """Five years ago, IndiGo was a domestic airline that happened to fly to Dubai. Today it serves 46 international destinations across four continents, operates close to 500 weekly international flights — up more than 50 percent from last year — and has become the first Indian carrier to fly the Airbus A321XLR, the narrow-body aircraft that is rewriting the economics of long-haul aviation.

For Indian Americans, the transformation matters for a simple reason: IndiGo's fares are often 30 to 40 percent cheaper than legacy carriers on the same routes, and its expanding network means budget options now exist on corridors that were once the exclusive preserve of Gulf and European airlines.

## The A321XLR Changes Everything

The aircraft at the center of IndiGo's global push is the Airbus A321XLR — a stretched, extra-long-range version of the A321neo that can fly up to 4,700 nautical miles nonstop. That range covers Delhi to Istanbul, Delhi to Athens, and potentially Delhi to destinations in East Africa or Southern Europe that were previously impossible without a widebody.

IndiGo became the first Indian airline to operate the A321XLR in early 2026, deploying it on Athens service. On April 19, it brought the type to the Delhi-Istanbul route, replacing the previous one-stop A320neo service that required a technical halt in Jeddah. The nonstop cuts nearly two hours from the journey. A second A321XLR was deployed on the same route immediately, and the service now operates daily with a dual-class configuration: 183 economy seats and 12 IndiGoStretch seats, the airline's business product.

The Istanbul route is strategically significant beyond just Turkey. Through IndiGo's codeshare with Turkish Airlines, passengers can connect to over 50 onward destinations in Europe, Africa, and the Americas through Istanbul's massive hub. For NRIs visiting family across Eastern Europe, the Balkans, or Central Asia, this is often the cheapest and fastest routing.

## Central Asia, the Caucasus, and Beyond

IndiGo's international map now reads like an atlas of emerging travel destinations that Indian Americans rarely considered a decade ago. The airline serves Tbilisi in Georgia, Baku in Azerbaijan, Almaty in Kazakhstan, and Tashkent in Uzbekistan — all routes that opened as India's visa and trade relationships with Central Asia deepened.

For NRIs, these routes unlock affordable access to some of the world's most underrated travel destinations. Georgia offers visa-free entry for Indian passport holders with valid US visas. Azerbaijan's e-visa takes 48 hours. A week in Tbilisi — with its wine country, ancient churches, and $15 dinners — costs less than a weekend in most European capitals.

Further afield, IndiGo launched Chennai to Reunion Island in April 2026, making it the only direct India-Reunion connection currently operating. The French overseas territory in the Indian Ocean — visa-free for Schengen visa holders — joins Mauritius and the Seychelles as IndiGo's Indian Ocean beach destinations. The airline also serves London Heathrow and now Manchester, giving UK-based NRIs budget alternatives to British Airways and Air India on the India corridor.

## The IndiGoStretch Question

The elephant on the plane is the premium product. IndiGoStretch is not business class in any traditional sense — there are no lie-flat seats, no lounges, no priority immigration. The 12 seats offer extra legroom, complimentary hot meals, free alcoholic beverages, and streaming entertainment on personal devices. On a six-hour Istanbul flight, that is adequate. On a ten-hour London flight, it is a stretch in every sense.

IndiGo's bet is that price-sensitive travelers — and Indian Americans are nothing if not value-conscious — will trade cabin luxury for a fare that leaves room for an extra suitcase of gifts and sweets. The data suggests they are right: IndiGo's weekly international flights have surged past 500, and the airline says international operations drove the bulk of its capacity growth this summer.

## What NRIs Should Know

IndiGo's baggage allowance on international flights is 25 kilograms for economy — competitive with full-service carriers and far above the 15-kilogram domestic standard. Vegetarian meals are default, with non-vegetarian options available for pre-booking. The airline does not interline bags with partner carriers on most routes, so connections require re-checking luggage.

The Central Asia and Caucasus routes can be seasonal, so confirm current schedules on goindigo.in before booking. And while IndiGo's on-time performance domestically is legendary, its international network is still maturing — delays on European sectors are more common than on Gulf routes.

Still, the headline is hard to argue with. India's largest airline now flies to 46 countries. For the diaspora, that means more choices, lower fares, and the strange novelty of booking an IndiGo flight to Baku."""
    },

    # ─────────────────────────────────────────────────────────
    # ARTICLE 3: Hilton's India Luxury Bet
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Hilton Is Going All-In on India — LXR in Bengaluru, Waldorf Astoria in Jaipur",
        "subheadline": "With plans to 10x its India portfolio and debut five luxury brands including its first LXR resort, Hilton is chasing the same NRI traveler who made Taj and Oberoi household names.",
        "slug": make_slug("hilton-india-lxr-bengaluru-waldorf-jaipur-luxury"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India increasingly want international-standard luxury hotels that take Hilton Honors points — and Hilton's aggressive India expansion means they can now redeem free nights in Bengaluru, Jaipur, and a dozen other cities.",
        "tags": ["travel", "hotels", "hilton", "luxury", "bengaluru", "jaipur", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/hilton-to-double-brand-presence-in-india-in-five-years-with-luxury-hotel-expansion/article69283283.ece"},
            {"name": "YourStory", "url": "https://yourstory.com/2025/05/hiltons-big-bet-india-announces-launch-luxury-properties"},
            {"name": "Hilton Newsroom", "url": "https://stories.hilton.com/releases/hilton-confirms-plans-to-double-brand-presence-in-india-in-the-next-five-years"},
            {"name": "Meetings Today", "url": "https://www.meetingstoday.com/articles/new-global-hotel-openings-in-india-portugal-and-shanghai"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14036253/pexels-photo-14036253.jpeg",
        "image_caption": "A sleek luxury hotel lobby with modern design and warm lighting",
        "image_attribution": "Pexels",
        "body": """When an NRI books a hotel in India, the calculus has always been peculiar. The Taj and Oberoi deliver world-class luxury but run on their own loyalty ecosystems — useless points for someone who primarily travels in the US on Marriott or Hilton. Marriott solved this years ago with a growing India portfolio, and now Hilton is making its move with an ambition that dwarfs anything it has attempted in the subcontinent.

The American hospitality giant has announced plans to 10x its current India portfolio within a decade, debuting five luxury and lifestyle brands that will stretch from enclosed first-floor suites in Bengaluru to a Waldorf Astoria overlooking Jaipur's pink ramparts. For the Indian American traveler — particularly the roughly 4.4 million who visit India at least once a year — this means something concrete: Hilton Honors points, earned on business trips in Chicago and Dallas, will soon buy free nights across India's most compelling destinations.

## The Den: LXR Arrives in Bengaluru

The marquee opening is The Den Bengaluru, Hilton's first LXR Hotels & Resorts property in India, scheduled for August 2026. Located on ITPL Main Road in Whitefield — the nerve center of Bengaluru's tech economy — the 226-room property positions itself at the intersection of business travel and luxury leisure.

LXR is Hilton's collection of independent luxury hotels, each with its own identity but connected to the Hilton Honors ecosystem. The Den promises three distinct dining concepts: Layla, blending Indian spices with Mediterranean technique; The Creek, a 24/7 global kitchen; and The Nest, a rooftop cocktail lounge. Nearly 9,000 square feet of event space, a spa, outdoor pool, and EV charging stations round out the offering.

For NRIs in tech — and there are a lot of them — the location is deliberate. Whitefield houses offices of Google, SAP, Wipro, and dozens of startups. A luxury hotel within walking distance of these campuses, accepting Hilton Honors Diamond status and all its perks, fills a gap that Indian American business travelers have complained about for years.

## Waldorf Astoria and Conrad in Jaipur

Hilton's India ambitions extend well beyond Bengaluru. Jaipur will receive three premium brands over the next two years: a Waldorf Astoria (ultra-luxury, expected 2027), a Signia by Hilton (Hilton's premier events-focused brand, 2028), and a Conrad. Together, they will make Jaipur one of Hilton's most densely branded cities in Asia.

The Waldorf Astoria is the crown jewel. The brand — which operates the iconic New York property and recently debuted in places like the Maldives and Osaka — promises to bring its signature service philosophy to Rajasthan's tourism capital. For NRIs planning destination weddings in India — a $50 billion market that attracted the DWP Congress to Udaipur for the first time this month — a Waldorf Astoria in Jaipur offers both the prestige and the loyalty point integration that Indian heritage hotels cannot match.

## Scaling Beyond Luxury

The luxury openings grab headlines, but Hilton's volume play is equally significant. DoubleTree by Hilton remains the company's largest brand in India with 11 operating hotels and 12 more under development. Hilton Garden Inn is expanding to five new Indian locations. And two economy brands — Spark by Hilton (150 hotels planned across India) and Hampton by Hilton (75 hotels in Gujarat, Rajasthan, Punjab, and Bihar) — will push Hilton into Tier 2 and Tier 3 cities where international chains have barely ventured.

For NRIs, the economy push matters as much as the luxury play. Visiting family in Bhopal, Siliguri, or Chandigarh currently means choosing between unbranded local hotels and a two-hour drive to the nearest international property. Hampton and Spark promise standardized rooms, reliable Wi-Fi, and — crucially — Hilton Honors earning, even in cities that most global hotel chains pretend do not exist.

## The Loyalty Angle

The real story here is not bricks and mortar but points and status. An estimated 100 million travelers worldwide hold Hilton Honors memberships, and Indian Americans are disproportionately represented thanks to heavy business travel within the US. Every Hilton opening in India effectively monetizes that existing loyalty base — turning Honors points earned in Hampton Inns along the I-95 corridor into free stays at LXR resorts in Bengaluru.

Hilton CEO Chris Nassetta put it plainly: "India is a critical part of Hilton's global growth strategy." With Marriott already at scale in India, IHG expanding its Holiday Inn and InterContinental footprints, and Hyatt pushing Andaz and Park Hyatt, the battle for the NRI traveler's loyalty is now a full-fledged race. Hilton's bet is that 10x growth, five luxury debuts, and 250-plus properties in the pipeline will make it impossible for the diaspora to ignore."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
