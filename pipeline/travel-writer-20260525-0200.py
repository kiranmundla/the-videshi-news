#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-25 02:00 UTC batch"""
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
    # ── Article 1: Thailand ends visa-free for Indians ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Ends Visa-Free Entry for Indians — What NRIs Need to Know Before Booking That Bangkok Trip",
        "subheadline": "Thailand's cabinet has scrapped the popular 60-day visa-free scheme for 93 countries including India, moving Indian passport holders to a 15-day visa-on-arrival regime. For the millions of NRIs who treat Bangkok as a quick getaway, the rules have changed overnight.",
        "slug": make_slug("thailand-ends-visa-free-indians-voa"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Thailand is the most popular short-haul international destination for Indians living in the US, frequently used as a stopover on India-bound trips and a go-to for quick PTO getaways. The shift from visa-free to VOA changes planning for an estimated 2 million Indian visitors annually.",
        "tags": ["travel", "visa", "thailand", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "LiveMint", "url": "https://www.livemint.com/news/trends/thailand-visa-news-tourist-visa-free-stay-for-indians-ends-11779550734027.html"},
            {"name": "Thailand Dept of Consular Affairs", "url": "https://www.mfa.go.th/en"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/30970845/pexels-photo-30970845.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Thailand has ended the 60-day visa-free arrangement that made it one of the easiest international destinations for Indian passport holders to visit. The Thai cabinet approved the overhaul on May 19, 2026, and the new rules take effect 15 days after publication in the Royal Gazette — likely by early June.

## What Changed

Under the previous scheme, introduced in July 2024 to revive post-pandemic tourism, Indians could enter Thailand without a visa and stay for up to 60 days, with a 30-day extension available on request. That is now gone.

India has been moved to the **Visa on Arrival (VOA)** category. Indian passport holders will need to obtain a visa at authorised immigration checkpoints upon landing, present supporting documentation, and will be permitted a maximum stay of **15 days**. No extensions.

The broader policy, branded "one country, one Thai visa exemption privilege," also cuts the 30-day visa-free list from 57 to 54 countries, eliminates the 60-day scheme entirely for all 93 nationalities that enjoyed it, and slashes the VOA list from 31 countries to just four. The Thai government cited security risks, illegal employment, nominee businesses, and transnational crime as driving the tightening.

## Why This Hits the NRI Community Hard

Thailand is not just another holiday destination for the Indian diaspora in America — it occupies a specific niche. For NRIs on H-1B or green card timelines who cannot always swing a full two-week India trip, Bangkok has long served as the affordable, no-hassle international break: direct flights from multiple US cities (via connections in Tokyo, Seoul, or Doha), cheap once you land, and until now, zero visa paperwork.

The numbers bear this out. India was among the top five source markets for Thai tourism in 2025, sending roughly 2 million visitors. A significant chunk of those were US-based Indians — visiting during Songkran, stopping over on the way to Delhi or Mumbai, or using Thailand for destination weddings that their friends could actually afford to attend.

The shift to a 15-day VOA does not make Thailand inaccessible. But it adds friction: you now need to carry documentation to the immigration desk, queue for processing on arrival, and plan around a hard 15-day cap instead of the generous two-month window.

## What NRIs Should Do Now

**If you are already in Thailand** on the existing visa-free arrangement, you can stay until the end of your approved period. No changes apply retroactively.

**If you have a trip booked before the new rules take effect** (likely early June 2026), you should still enter under the current visa-free terms. Check the Royal Gazette publication date for the exact cutoff.

**For future trips**, prepare for VOA requirements: a passport valid for at least six months, proof of accommodation, a return ticket, and evidence of funds (typically 10,000 baht or ~$280 per person). Arrive with documentation ready to avoid delays at the immigration counter.

**Consider an e-visa instead.** Thailand's e-visa system allows advance processing, which avoids the VOA queue entirely. For NRIs who hold a US passport alongside their Indian one, US citizens remain on the 30-day visa-free list — Thailand has not touched that arrangement.

## The Bigger Picture

Thailand's move is part of a global pattern of post-pandemic visa liberalisation being quietly walked back. Countries that opened doors to boost recovery — Thailand, Malaysia, Sri Lanka — are reassessing as security and overstay concerns mount. For Indian passport holders, the Henley Index ranking (currently 85th, with access to 27 visa-free and 47 VOA destinations) remains stubbornly modest.

The practical takeaway: if you are planning a Thailand trip for later this year, start the visa process early. The days of booking a last-minute Bangkok weekend with nothing but your passport are over."""
    },

    # ── Article 2: Memorial Day 2026 travel chaos ──
    {
        "id": str(uuid.uuid4()),
        "headline": "17,000 Flight Disruptions and a Sinkhole: Memorial Day Weekend 2026 Is a Disaster for Anyone Flying in America",
        "subheadline": "A LaGuardia runway sinkhole, East Coast thunderstorms, and record passenger volumes have combined to produce the most disrupted Memorial Day in modern US aviation. For NRIs with India-bound connections through JFK or Newark, the fallout is personal.",
        "slug": make_slug("memorial-day-2026-flight-chaos-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying India routes through JFK, Newark, and O'Hare are directly affected by LaGuardia overflow and East Coast storm delays. Air India connections through EWR and JFK are disrupted. Passengers with long-haul bookings face missed connections and rebooking nightmares.",
        "tags": ["travel", "flights", "memorial-day", "airports", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TravelTourister", "url": "https://www.traveltourister.com/news/memorial-day-weekend-17000-disruptions-may-23-2026-atlanta-laguardia-survival/"},
            {"name": "NBC Palm Springs / AAA", "url": "https://nbcpalmsprings.com/2026/05/23/millions-take-to-the-skies-for-memorial-day-weekend/"},
            {"name": "Mappr / AAA Forecast", "url": "https://mappr.co/data-maps/memorial-day-travel-2026/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3750210/pexels-photo-3750210.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Memorial Day weekend 2026 will be remembered as the one where everything broke at once. Since Thursday May 22, more than 17,000 flights across the United States have been delayed or cancelled — roughly double the disruption level of a normal Memorial Day — making this the worst holiday travel weekend in modern American aviation.

## Three Crises, One Weekend

The chaos stems from three independent failures hitting simultaneously.

**The LaGuardia sinkhole.** On May 20, airfield crews discovered a sinkhole near Runway 4/22 during a routine morning inspection. The runway was immediately shut down. Three days later, it remains closed. LaGuardia operates with only two intersecting runways — losing one cuts the airport's capacity roughly in half. Delta, American, United, and JetBlue have cancelled or delayed hundreds of flights. JFK and Newark, already at peak Memorial Day volume, are overwhelmed with overflow passengers rerouted from LaGuardia.

**Record passenger volumes.** AAA projected 45.1 million Americans would travel this weekend, with actual volumes tracking at or above that forecast. Atlanta's Hartsfield-Jackson alone is bracing for 2.7 million passengers across the holiday window — 50% above its normal peak-day capacity. The system was already strained before anything went wrong.

**East Coast storms.** Severe thunderstorms have been sweeping from New England to Georgia since Friday, compressing an already-overstretched network. The FAA issued active advisories for Boston, New York, Philadelphia, Washington DC, Charlotte, and Atlanta simultaneously.

## Why NRIs Should Care

If you are flying to or from India this weekend, the disruptions are not abstract. The JFK-to-India corridor — served by Air India, Emirates, Qatar Airways, and United — runs through the exact infrastructure that is buckling. Newark, United's transatlantic hub and a key India routing point, is processing overflow from LaGuardia on top of its own peak holiday traffic. Air India's operations at both JFK and Newark have been affected.

The practical consequences for NRIs on long-haul itineraries are severe. A 90-minute domestic delay that merely annoys someone flying to Orlando can mean a missed international connection for someone heading to Delhi or Mumbai — and rebooking a cancelled Air India flight on a sold-out holiday weekend is not a two-hour problem. It is a two-day problem.

This is also happening in the wake of Spirit Airlines' shutdown three weeks ago, which removed roughly 300 daily flights from the US network and pushed 60,000 passengers onto already-full competing carriers. Every seat is scarce.

## What to Do Right Now

**Check your flight obsessively.** Use FlightAware or your airline's app. In single-runway operations at LaGuardia, departure times shift by 30 to 60 minutes continuously.

**If your flight is cancelled, demand a cash refund.** Under DOT regulations, airlines must provide full cash refunds to your original payment method for all cancellations, regardless of cause. The magic phrase: "Under DOT regulations, I am requesting a full cash refund to my original payment method."

**Build in connection buffer.** If you are connecting through JFK, EWR, or ATL to an India-bound flight, 90 minutes is no longer enough. Allow at least three hours for international connections this weekend.

**Consider alternate routings.** If your JFK connection is wrecked, check if your airline can reroute through Chicago O'Hare or Washington Dulles, which are under less pressure than the New York airports.

**Use the airline app, not the desk.** Airport rebooking queues at JFK and Newark are running multiple hours. The Delta, United, and American apps process rebookings faster.

## The Bigger Pattern

This is not an isolated bad weekend. The US aviation system has been in elevated disruption for 53 consecutive days, dating back to Good Friday. Airlines entered the summer season with tight staffing — particularly among pilots, maintenance technicians, and air traffic controllers — and fuller schedules than their infrastructure can reliably support. For NRIs who fly the US-India corridor regularly, building resilience into travel plans is no longer optional. Book refundable fares when possible, carry overnight essentials in your cabin bag, and assume that connections under two hours are a gamble until the system stabilises."""
    },

    # ── Article 3: India's luxury hotel boom ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Palaces, Bonvoy Points, and Eco-Lodges: India's Luxury Hotel Boom Is Built for the NRI Homecoming",
        "subheadline": "Fairmont has opened a 327-room palace in Udaipur, Marriott has hit 50 hotel openings in six months, and Accor is bringing eco-luxury to the edge of a tiger reserve. India's hospitality sector is scaling fast — and it is targeting the diaspora dollar.",
        "slug": make_slug("india-luxury-hotel-boom-nri-fairmont-marriott"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs planning India trips — whether for weddings, family visits, or pure tourism — now have dramatically more upscale options outside the traditional Mumbai-Delhi-Goa corridor. Marriott Bonvoy integration means US-earned points work seamlessly at 50+ new Indian properties.",
        "tags": ["travel", "hotels", "india", "luxury", "marriott", "fairmont", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/stay/indias-newest-palace-hotel-is-a-lesson-in-crafty-opulence"},
            {"name": "PR Newswire / Marriott International", "url": "https://www.prnewswire.com/news-releases/marriott-international-and-the-fern-hotels--resorts-celebrate-75-signings-and-50-openings-for-series-by-marriott-in-india-302778012.html"},
            {"name": "Nomad Lawyer / Accor", "url": "https://nomadlawyer.org/accor-brings-mantis-eco-luxury-brand-to-india/"},
            {"name": "Glance / Leela Hotels", "url": "https://trends.glance.com/leela-unveils-exclusive-luxury-resort-in-coorg/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33810146/pexels-photo-33810146.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Something is happening in Indian hospitality that NRIs planning their next trip home should pay attention to. Over the past six months, the country's luxury hotel landscape has expanded faster than at any point in its history — and much of it is designed, whether explicitly or not, for the diaspora visitor.

## Fairmont Arrives in Udaipur

The most eye-catching opening is Fairmont Udaipur Palace, Accor's first Fairmont-branded property in India. Spread across 18 acres in the Aravalli hills on Udaipur's quieter outskirts, the 327-room property is a ground-up palace — not a heritage conversion — with domes, chhatris, and colonnades drawn from Mewar's architectural vocabulary, executed in stone and marble.

The scale is deliberate. With over 140,000 square feet of event space, including the chandelier-lit Jewel ballroom, the Mehfil courtyard, and a dramatic stepwell-inspired Chand Baori venue, Fairmont Udaipur is positioning itself squarely as a destination wedding venue. Eight dining concepts, butler service, and suites with private pools and marble dining tables complete the picture. Room categories run from standard Fairmont Rooms to the Maharaja and Maharani suites, which feature bejewelled roll-top tubs and private lap pools.

For NRIs, the relevance is straightforward. Udaipur has long been the aspirational Indian wedding destination, but hotel inventory at the top end was limited to a handful of heritage properties — the Oberoi Udaivilas, Taj Lake Palace, and Leela. Fairmont adds 327 rooms of genuine luxury to a market that desperately needed more capacity, particularly for large wedding parties where booking an entire 80-room heritage property still did not accommodate the guest list.

## Marriott's 50-Hotel Sprint

While Fairmont went big with one property, Marriott went wide across the country. In under six months since its November 2025 debut, the Series by Marriott brand — a collaboration between Marriott International and The Fern Hotels & Resorts — has signed 75 hotels in India and opened 50, adding 3,556 rooms across 43 cities.

The properties span Tier 1, 2, and 3 markets: The Fern Mumbai in Goregaon, The Fern Jaipur, The Fern Habitat Goa in Candolim, a resort in Igatpuri, and a residency in Bengaluru's Seshadripuram, among others. The brand targets the "global domestic traveller" — someone who wants Marriott Bonvoy reliability and points earning without paying Ritz-Carlton prices.

This matters enormously for NRIs. Most US-based Indians already carry Marriott Bonvoy status through American credit card ecosystems — the Amex Marriott Bonvoy Brilliant and Chase Marriott Bonvoy Boundless are among the most popular travel cards in the desi community. Having 50 new properties in India where those points and elite status actually work — including in cities like Surat, Bhubaneswar, and Igatpuri that were previously Bonvoy deserts — changes the calculus for non-metro India travel.

## Eco-Luxury Enters the Picture

Accor is also bringing its Mantis eco-luxury brand to India, with a 31-key retreat planned near Nagarhole Tiger Reserve in Karnataka. The property, expected to open in 2028, will emphasise conservation-led luxury: wildlife experiences, sustainable practices, and intimate scale. Meanwhile, Leela Palaces has acquired a new luxury resort in Coorg — another Karnataka nature destination — expanding its south Indian footprint.

Both moves signal that India's luxury hotel development is finally moving beyond the golden triangle of Delhi-Agra-Jaipur and the beach corridor of Goa. For NRIs who grew up visiting grandparents in Karnataka, Kerala, or the Northeast and have watched those regions remain underserved by international hotel brands, the shift is overdue.

## The NRI Calculation

The combined effect of these openings reshapes how diaspora Indians can plan trips home. A family visiting from the Bay Area can now build an itinerary that moves from a Marriott Bonvoy property in Bengaluru to the new Leela in Coorg to Fairmont Udaipur — earning and burning points the entire way, with service standards that match what they are used to in the US.

For wedding planners, Fairmont Udaipur alone adds meaningful supply to a market where premium venues were booked 18 months in advance. For business travellers hitting Tier 2 cities, Marriott's Fern partnership means a reliable room in Rajkot or Surat instead of rolling the dice on an unbranded property.

India's hotel sector added roughly 15,000 branded rooms in the first five months of 2026. For NRIs, the message is simple: the next trip home does not have to involve compromising on where you stay."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
