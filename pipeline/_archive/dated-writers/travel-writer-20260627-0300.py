#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-27 03:00 PDT run."""
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


# ---------------------------------------------------------------------------
# ARTICLE 1: Amarnath Yatra 2026
# ---------------------------------------------------------------------------
amarnath_body = """The 57-day Amarnath Yatra begins on July 3 this year, and if you're an NRI planning a summer India trip with a spiritual stop in Kashmir, the 2026 edition comes with rule changes you need to know about before you pack.

The Shri Amarnathji Shrine Board has tightened logistics across the board. RFID tracking is now mandatory for every pilgrim — you collect your tag at Jammu or Kashmir transit camps after biometric eKYC verification at an authorised bank branch. Without the tag, you will not pass the Domel or Chandanwari checkpoints. Period.

## No Helicopters This Year

The biggest operational shift: the SASB has declared both Yatra routes a "No Flying Zone" from July 1. Helicopter services, which previously offered a shortcut to the holy cave for older pilgrims and time-pressed travellers, are completely suspended for 2026. The only options are on foot, by pony, or by palki (palanquin).

For NRIs used to booking a helicopter as a time-saver during short India visits, this changes the calculus entirely. The trek now demands real physical preparation.

## Two Routes, Two Very Different Experiences

| Feature | Baltal (North) | Pahalgam (South) |
|---------|---------------|-----------------|
| Distance | ~14 km | 36–48 km |
| Duration | 1–2 days | 3–5 days |
| Terrain | Steep, narrow, strenuous | Gradual, scenic, extended |
| Best for | Fit trekkers | Families, first-timers |

The Baltal route is shorter but punishing — steep switchbacks at altitude with limited acclimatisation time. Pahalgam offers the classic pilgrimage experience: green valleys, mountain streams, and slower elevation gain that lets your body adjust. If you're flying in from sea-level cities like San Francisco or Houston, Pahalgam is the safer bet.

## Daily Caps and Eligibility

The SASB is capping daily entries at 15,000 pilgrims across both routes. Registration closes seven days before your chosen travel date, so last-minute decisions are out. Eligibility is restricted to ages 13–70, and a Compulsory Health Certificate issued after April 8, 2026 is non-negotiable. Pregnant women beyond six weeks are not permitted.

Online registration is available through the SASB website, with offline counters at 554 bank branches (PNB, J&K Bank, SBI, Yes Bank) across India.

## Jammu Hotels Are Offering 30% Off — Here's Why

Jammu's hotel industry is hurting. Two years ago, 39% of Amarnath pilgrims stopped in Jammu for at least a night. Last year, that figure slid to 31% — seven out of ten yatris now bypass the city entirely and head straight to Kashmir via the Srinagar-Jammu Vande Bharat Express.

In response, the All Jammu Hotel and Lodge Association is offering 30% discounts on advance bookings, and the Railway Taxi Union has rolled out budget-friendly tour packages to Pahalgam and Baltal base camps. With 90% of Jammu hotel rooms sitting empty as the yatra approaches, these deals are real.

For NRIs, a night in Jammu before the trek is worth considering. It allows for jet-lag recovery, acclimatisation, and a chance to visit Vaishno Devi — just 60 kilometres away — before heading into the mountains.

## What NRIs Should Know

Plan at least four to five days for the full Yatra circuit, plus buffer days on either end. Travel insurance that covers high-altitude trekking is worth the premium. The RFID system means your movements are tracked end-to-end, which is actually reassuring for families back in the US who want real-time peace of mind.

The Yatra runs through August 28, concluding on Raksha Bandhan. If your India trip falls anywhere in that window, this is one of the most extraordinary spiritual journeys the subcontinent offers — but only if you come prepared."""

# ---------------------------------------------------------------------------
# ARTICLE 2: IRCTC Divine East Temple Tour
# ---------------------------------------------------------------------------
divine_east_body = """IRCTC has just opened bookings for a new pilgrimage-meets-heritage circuit that threads together eastern India's most revered temples and cultural landmarks in a single 11-day train journey. The "Divine East Temple Tour" operates on a Bharat Gaurav Deluxe Tourist Train — a fully air-conditioned, semi-luxury service with cabins, onboard dining, and a dedicated tour manager.

The route reads like a greatest-hits itinerary of Hindu pilgrimage and UNESCO heritage: Delhi to Varanasi, then south through Odisha's temple corridor, east to Kolkata, and a day excursion to the sacred shores of Gangasagar before circling back through Baidyanath Dham — one of the twelve Jyotirlingas.

## The Itinerary

The journey departs from Safdarjung station in Delhi and unfolds across four states:

**Varanasi** — Kashi Vishwanath Temple darshan and the evening Ganga Aarti at Dashashwamedh Ghat, one of Hinduism's most transcendent rituals.

**Puri and Odisha circuit** — Darshan at the Shri Jagannath Temple, followed by the Konark Sun Temple (a UNESCO World Heritage Site whose stone chariot wheels still cast accurate sundial shadows), Dhauli Shanti Stupa, and the ancient Udayagiri and Khandagiri rock-cut caves outside Bhubaneswar.

**Kolkata** — Victoria Memorial, Kalighat Mandir, Dakshineshwar Kali Mandir, and Belur Math, plus a sunset cruise on the Hooghly gliding past Howrah Bridge and Vidyasagar Setu.

**Gangasagar** — A day excursion to the confluence of the Ganges and the Bay of Bengal. Pilgrims take a holy dip at Sagar Sangam and visit Kapil Muni Temple.

**Baidyanath Dham** — The final stop before returning to Delhi, one of Lord Shiva's twelve Jyotirlingas in Jharkhand.

## Pricing and What's Included

| Class | Price per person |
|-------|-----------------|
| AC III | ₹91,370 |
| AC II | ₹1,06,145 |
| AC I | ₹1,13,530 |

The all-inclusive package covers train travel, three-star hotel accommodation at each stop, all meals (vegetarian), AC vehicle transfers for sightseeing, travel insurance, and IRCTC tour managers throughout. Bookings are open on IRCTC's tourism portal and through authorised offices.

## Why NRIs Should Pay Attention

For diaspora families who want to show their US-raised children the spiritual depth of eastern India — or for parents visiting from India who'd rather travel in comfort than navigate train bookings, hotel logistics, and local transport on their own — this is a compelling package.

The Bharat Gaurav trains are a step above standard Indian Railways: modern cabins, onboard restaurant cars, electronic safes, and shower cubicles. It's not the Maharajas' Express, but it's a far cry from the unreserved sleeper coach your parents remember.

The tour also solves a real logistics problem. Trying to independently cover Varanasi, Puri, Konark, Kolkata, and Gangasagar in 11 days requires booking at least four separate trains, six hotels, and multiple local guides. IRCTC bundles all of it at a price point that undercuts what most private tour operators charge for similar eastern India circuits.

The first departure is scheduled for late September with a return to Delhi on October 5 — right in the sweet spot between monsoon season and the Dussehra-Diwali festival rush. If you're booking a Diwali trip home, this makes for a natural pre-festival spiritual tour."""

# ---------------------------------------------------------------------------
# ARTICLE 3: Cordelia Cruises Chennai Season
# ---------------------------------------------------------------------------
cordelia_body = """India's only major cruise line is betting big on Chennai as its southern gateway, and the 2026 season offers something the Indian travel market has never really had: multi-night international cruise itineraries from an Indian port that don't require a separate visa.

Cordelia Cruises returns to Chennai for its fifth consecutive season with the Cordelia Empress, a 692-foot ship accommodating up to 1,950 guests across 796 cabins. Sailings run from late June through August, with itineraries ranging from quick two-night weekend getaways to an ambitious 10-night Southeast Asia voyage.

## The Routes

**10-Night Southeast Asia Cruise** — Chennai to Phuket, Langkawi, Kuala Lumpur, and Singapore. Departs July 18. This is the marquee offering: a proper international voyage with stops at four countries, all from Chennai port.

**5-Night Sri Lanka Cruises** — Chennai to Hambantota, Trincomalee, and Jaffna. Departs August 10 and 17. Sri Lanka's proximity makes this a natural extension.

**3-Night Sri Lanka Cruise** — Chennai to Trincomalee and back. Departs August 7. A shorter option for those testing the cruise waters.

**5-Night Domestic Coastal** — Chennai to Visakhapatnam and Puducherry. Multiple departures through July. India's eastern coastline without the logistics of overland travel.

**2-Night Weekend Cruises** — Chennai to open sea and back. Departures throughout the season. Essentially a floating resort weekend with no destination required.

**5-Night Grand Westbound** — Chennai to Kochi to Mumbai. Departs August 24. Links India's eastern and western coasts in a single sailing.

## What's the NRI Angle?

If you're visiting family in Chennai, Bengaluru, or anywhere in South India this summer, a cruise bolted onto the trip is a genuinely new option that didn't exist five years ago.

The economics make sense: Cordelia packages start around ₹7,000–10,000 per person per night (roughly $80–120), all-inclusive of accommodation, meals, entertainment, and onboard activities. Four dining venues, nine bars and lounges, a casino, spa, rock-climbing wall, and live stage performances are included. For a family of four, a five-night coastal cruise runs comparable to a mid-range Goa or Kerala resort holiday — with the novelty of waking up in a different port each morning.

The international cruises are particularly attractive for Indian passport holders. Cruise passengers typically receive port entry without a separate tourist visa at most stops — a significant perk when your passport otherwise requires advance visas for much of Southeast Asia.

## The Company Behind It

Cordelia's parent company, Waterways Leisure Tourism, just saw its IPO fully subscribed on June 25, raising ₹585 crore. The company is adding two former Norwegian Cruise Line ships — the Cordelia Sky (arriving September 2026) and Cordelia Sun (2027) — which will roughly triple its passenger capacity.

India's cruise market is still minuscule compared to the Mediterranean or Caribbean, but it's growing fast from a low base. The government has been investing in cruise terminal infrastructure at Mumbai, Goa, Kochi, and Chennai, and cabotage rule relaxations now allow foreign-flagged ships to operate domestic routes.

## Should You Book?

The Southeast Asia voyage is the standout. A 10-night cruise from Chennai to Singapore via Phuket and Langkawi, with no flight connections and no visa headaches, is hard to find at this price point. The domestic coastal routes are best for families wanting a low-effort holiday addition to an India visit.

Book directly through Cordelia's website or through Indian travel agents who bundle cruise packages. Cabins on the Southeast Asia and Sri Lanka routes tend to fill early — the July 18 sailing especially, given school holiday timing."""


# ---------------------------------------------------------------------------
# Assemble articles
# ---------------------------------------------------------------------------
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Amarnath Yatra 2026 Starts July 3 — No Helicopters, RFID Tracking, and 30% Off Jammu Hotels",
        "subheadline": "The 57-day pilgrimage to Lord Shiva's ice cave shrine comes with tighter rules this year. Here's what NRI pilgrims need to plan around.",
        "slug": make_slug("amarnath-yatra-2026-nri-guide-no-helicopters-rfid-jammu"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Many NRIs plan the Amarnath pilgrimage during summer India visits — the 2026 ban on helicopters, mandatory RFID tracking, and 15K daily cap require advance planning that diaspora travellers often skip.",
        "tags": ["travel", "pilgrimage", "kashmir", "amarnath", "hindu"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Curly Tales", "url": "https://curlytales.com/amarnath-yatra-2026-jammu-hotels-to-offer-30-discount-to-pilgrims-offers-on-taxis-too/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/amarnath-yatra/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-travel-guide-to-amarnath-yatra-2026/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/amarnath-yatra-2026-registration-open-in-jammu-pilgrims-flock-in-large-numbers-11776228765020.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/66/Cave_Temple_of_Lord_Amarnath.jpg",
        "image_caption": "The holy ice Shivalinga inside the Amarnath Cave shrine in Kashmir",
        "image_attribution": "Wikimedia Commons",
        "body": amarnath_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IRCTC Just Launched an 11-Day Train Pilgrimage Across Eastern India's Holiest Sites",
        "subheadline": "The new 'Divine East Temple Tour' on a Bharat Gaurav Deluxe train covers Varanasi, Puri, Konark, Kolkata, Gangasagar, and Baidyanath Dham — all in one all-inclusive package.",
        "slug": make_slug("irctc-divine-east-temple-tour-bharat-gaurav-train-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI families looking for a curated spiritual tour of eastern India now have an all-inclusive train package that solves the logistics nightmare of independently covering Varanasi, Puri, Konark, and Kolkata in under two weeks.",
        "tags": ["travel", "trains", "pilgrimage", "irctc", "bharat-gaurav", "heritage"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Awaaz", "url": "https://theindianawaaz.com/irctc-introduces-new-tourism-circuit-titled-divine-east-temple-tour-on-its-bharat-gaurav-deluxe-tourist-train/"},
            {"name": "IRCTC Tourism", "url": "https://www.bharatgaurav.irctc.co.in/"},
            {"name": "Newkerala", "url": "https://www.newkerala.com/news/2026/66068.htm"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Konarka_Temple.jpg/1280px-Konarka_Temple.jpg",
        "image_caption": "The Konark Sun Temple in Odisha, a UNESCO World Heritage Site on the Divine East itinerary",
        "image_attribution": "Wikimedia Commons",
        "body": divine_east_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Cordelia Cruises Is Sailing from Chennai to Singapore This Summer — and NRIs Should Take Note",
        "subheadline": "India's largest cruise line opens its fifth Chennai season with 10-night Southeast Asia voyages, Sri Lanka routes, and weekend getaways. The IPO just subscribed, two new ships are coming, and the prices undercut comparable resort holidays.",
        "slug": make_slug("cordelia-cruises-chennai-southeast-asia-singapore-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting family in South India can now bolt a cruise holiday onto their trip — with port entry at SE Asian stops often not requiring separate visas for Indian passport holders, and prices starting around $80/night all-inclusive.",
        "tags": ["travel", "cruise", "chennai", "southeast-asia", "cordelia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/cordelia-cruises-to-call-on-chennai-for-5th-season-on-june-20/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/cordelia-cruises-operator-waterways-leisure-ipo-fully-subscribed-1751030413818"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/cordelia-cruises-returns-to-chennai/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/813036/pexels-photo-813036.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A cruise ship on the open ocean at sunset",
        "image_attribution": "Pexels",
        "body": cordelia_body,
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
