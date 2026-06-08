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
        "headline": "Ladakh Just Had Its Best Month Ever — and American Visitors Are Part of the Surge",
        "subheadline": "May 2026 brought 73,000 tourists to the Himalayan territory, a 121% jump from last year. The US is now among the top three source countries for foreign arrivals.",
        "slug": make_slug("ladakh-tourism-record-may-2026-nri-american-visitors"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "US-based Indians planning summer trips to India now have a data-backed reason to add Ladakh to their itinerary. American tourist arrivals are climbing, infrastructure has improved dramatically, and the window between June and September is wider and more accessible than ever.",
        "tags": ["travel", "ladakh", "india-tourism", "adventure", "summer-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/germany-joins-thailand-uk-vietnam-us-japan-france-and-more-countries-as-ladakh-records-jaw-dropping-tourism-increase-in-2026/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/ladakh-sees-43-rise-in-tourist-arrivals-in-2026/"},
            {"name": "Bhasha Times", "url": "https://www.bhashatimes.com/ladakh-records-historic-tourist-surge-in-2026/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Pangong_Tso_2.jpg/1280px-Pangong_Tso_2.jpg",
        "image_caption": "Pangong Tso lake in Ladakh, one of the region's most visited landmarks",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers out of Leh are hard to ignore. In May 2026, Ladakh welcomed 72,834 tourists — a 121% increase over the same month last year, when just 32,927 visitors made the journey. For the first five months of the year, total arrivals hit 117,546, up 44% from 2025 and a staggering 128% above the same window in 2024.

This is not a slow recovery. This is a region that has found its stride.

## Who Is Going — and Where They're Coming From

The growth is not purely domestic. Foreign arrivals between January and May rose 15% year-on-year to 6,961 visitors. The top three source countries tell an interesting story: Thailand leads with 1,321 visitors, followed by Vietnam at 722 and the United States at 642. Japan, the UK, Germany, and France round out the list.

That US figure matters. A growing number of Indian Americans are folding Ladakh into their summer India trips — and the infrastructure is finally catching up to the ambition. Leh's Kushok Bakula Rimpochee Airport has expanded capacity, road connectivity from Manali and Srinagar has improved markedly since Ladakh became a Union Territory in 2019, and the administration has simplified documentation requirements for tourism operators.

## What Changed

Lieutenant Governor Vinai Kumar Saxena has attributed the surge to a deliberate overhaul of tourism policy. Hotels and guest houses have been granted industry status, reducing the compliance burden on operators. Permit processes for restricted areas — previously a notorious source of delays — have been streamlined. International marketing campaigns targeting Southeast Asia and Europe have expanded Ladakh's visibility beyond the traditional Delhi-to-Leh backpacker circuit.

The results are showing up in occupancy data. Hotels around Pangong Lake and in Nubra Valley are reporting near-full bookings through September. Adventure tourism operators offering motorcycle tours, rafting on the Zanskar River, and high-altitude treks to Stok Kangri are seeing demand they haven't experienced since before the pandemic.

## The NRI Calculus

For the 4.4 million Indian Americans, Ladakh has historically been the trip you plan but never take. The altitude, the remoteness, the logistics of getting a family from JFK or SFO through Delhi and then onto a dawn flight to Leh — it all felt like too much friction for a two-week India visit already packed with family obligations.

That equation is shifting. Air India and IndiGo now operate multiple daily flights from Delhi to Leh, and early-morning departures mean you can land before the afternoon winds that used to cancel half the schedule. The new wave of boutique hotels — properties like The Grand Dragon, Stok Palace Heritage, and several new luxury camps — offer comfort levels that make the trip viable for parents and children alike.

A practical tip for NRI families: book Leh flights for the first leg of your India trip, when jet lag works in your favour. The 3,500-metre altitude demands a full rest day on arrival anyway, and the time difference means you will be wide awake at sunrise with the mountains.

## The Sustainability Question

Not everyone is celebrating without reservation. Leh's resident population is roughly 31,000. When 73,000 tourists arrive in a single month, the strain on water, waste management, and road capacity is real. Environmental groups have raised concerns about plastic waste around Pangong Lake and diesel emissions from the thousands of SUVs that ferry tourists through mountain passes.

The administration has responded with a push for electric vehicles on key routes and a ban on single-use plastics in protected areas, but enforcement remains uneven. Responsible tourism operators are beginning to market "slow Ladakh" itineraries — longer stays in fewer places, homestays over hotels, and off-season visits in September and October when the crowds thin but the weather holds.

## The Window Is Open

For NRIs considering a Ladakh trip this summer, the data suggests booking sooner rather than later. The peak season runs June through September, and the 121% surge in May indicates that peak-season availability will be tighter than any year in recent memory. Direct flights from Delhi are the bottleneck — IndiGo's morning slots sell out weeks in advance during July and August.

The region that was once the furthest reach of the India trip is becoming, for a growing number of diaspora travelers, the reason to go in the first place."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sri Lanka Just Dropped Visa Fees for Indians — Here's What NRIs With Indian Passports Should Know",
        "subheadline": "A new policy effective May 25 waives the ETA fee for 40 countries including India, making Sri Lanka one of the easiest international getaways for Indian passport holders in the US.",
        "slug": make_slug("sri-lanka-free-eta-indians-visa-waiver-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs holding Indian passports can now visit Sri Lanka without paying visa fees — a significant reduction in friction for a destination that's just a short flight from South Indian cities many NRIs already visit during family trips home.",
        "tags": ["travel", "sri-lanka", "visa", "indian-passport", "nri-travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-joins-china-pakistan-indonesia-us-uk-and-more-in-sri-lankas-bold-move-granting-free-30-day-etas-to-40-countries/"},
            {"name": "Unimoni", "url": "https://www.unimoni.in/blog/sri-lanka-extends-visa-free-travel-to-40-countries/"},
            {"name": "VisasNews", "url": "https://www.visasnews.com/sri-lanka-the-free-visa-eta-scheme-could-be-introduced-within-one-or-two-months/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Sigiriya_%28141688197%29.jpeg",
        "image_caption": "Sigiriya rock fortress in central Sri Lanka, a UNESCO World Heritage Site",
        "image_attribution": "Wikimedia Commons",
        "body": """Sri Lanka has waived Electronic Travel Authorisation fees for citizens of 40 countries, and India is on the list. The policy, effective since May 25, 2026, means Indian passport holders can now apply for a free 30-day tourist ETA — no visa fee, no consulate visit, no payment at the border. Just an online form before departure.

The move is part of Colombo's aggressive push to rebuild a tourism sector that was gutted first by the 2019 Easter bombings, then by the pandemic, and then by the 2022 economic crisis. India has consistently been Sri Lanka's largest source of tourists, and removing the fee eliminates the last bit of financial friction for a trip that already costs less than most domestic Indian vacations.

## What Exactly Changed

Previously, Indian nationals paid approximately $50 for a tourist ETA. That fee has been waived for all 40 countries on the new list, which also includes the US, UK, China, Australia, Canada, Japan, Germany, France, and Saudi Arabia. The ETA itself — the online application — is still required. You still need to submit it before you fly. But the fee is gone.

The ETA covers a single tourist entry for up to 30 days. Extensions of up to 90 days are available through Sri Lanka's immigration authorities once you are in the country. The policy applies to holders of ordinary, diplomatic, official, and service passports.

## Why NRIs Should Pay Attention

Here is where it gets interesting for Indian Americans. If you hold an Indian passport — even if you live in New Jersey, Dallas, or Fremont — this policy applies to you. And Sri Lanka is a destination that slots perfectly into the kind of trip many NRIs already take.

Consider the geometry. You are flying to Chennai or Bengaluru to see family. Colombo is a 90-minute flight from either city. For roughly the cost of a domestic Indian flight, you can add three or four days in a country with pristine beaches, UNESCO World Heritage sites, world-class tea country, and some of the best seafood in South Asia — all without the visa headache that usually accompanies an international side trip.

The practical math: a return flight from Chennai to Colombo on SriLankan Airlines or IndiGo runs between $80 and $150. A solid beachfront hotel in Unawatuna or Mirissa costs $40–80 a night. A driver for the day — the best way to see the island — is about $35–50. For a family of four, a three-night Sri Lanka add-on during an India trip can come in under $1,500 all-in, and you come home with stories that have nothing to do with wedding shopping or temple visits.

## The Five-Day NRI Itinerary

For those with limited time, the most efficient Sri Lanka circuit covers the Cultural Triangle and the southern coast:

**Day 1**: Fly into Colombo, drive to Sigiriya (4 hours). Check into a hotel near the rock fortress. **Day 2**: Climb Sigiriya at dawn, visit the Dambulla cave temples in the afternoon. **Day 3**: Drive south to Galle (5 hours through tea country with a stop in Ella or Nuwara Eliya). **Day 4**: Explore Galle Fort, spend the afternoon at Unawatuna Beach. **Day 5**: Morning in Mirissa or a whale-watching boat, then drive to Colombo airport for an evening flight back to India.

This is dense but doable, and it gives you a cross-section of what makes Sri Lanka compelling: ancient ruins, colonial architecture, hill country, and Indian Ocean coastline.

## What You Still Need

The free ETA does not mean you can show up without preparation. You must apply online through Sri Lanka's official ETA portal before departure — ideally 24 to 48 hours ahead. You will need a passport valid for at least six months, proof of a return or onward flight, and accommodation details.

A few practical notes for NRIs: your US address is fine on the application. Travel insurance is not mandatory but strongly recommended. Sri Lanka accepts US dollars widely, but the Sri Lankan rupee gives better value for local purchases. And if you are visiting during monsoon season (May through September on the southwest coast), shift your beach days to the east coast — Trincomalee and Arugam Bay are dry when Galle is wet.

## The Bigger Picture

Sri Lanka's fee waiver is part of a regional trend. Southeast Asian countries have been loosening visa requirements for Indian passport holders for the past two years — Thailand, Malaysia, and Indonesia all offer visa-free or visa-on-arrival entry. But Sri Lanka's proximity, cultural familiarity, and sheer affordability make it the easiest add-on destination for NRIs already in South India.

For the 1.3 million Indian tourists who visited Sri Lanka in 2019 — a number that Colombo is desperate to exceed — the removed fee is less about the $50 saved and more about the signal. Sri Lanka is saying: we want you here, and we have made it as easy as we possibly can.

The smart NRI move is to plan the Sri Lanka leg now, before summer flight prices on the Chennai–Colombo and Bengaluru–Colombo routes climb any higher."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
