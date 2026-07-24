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
    "headline": "No More Flying Home Just to Renew a Visa — the US Pilot That Could Spare Indian Workers the Trip",
    "subheadline": "From December, the State Department will stamp 20,000 visas for people already inside the US, and Indian professionals are the explicit target.",
    "slug": make_slug("us-domestic-visa-renewal-pilot-indians-h1b-no-trip-home"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "Tens of thousands of Indian H-1B workers currently have to fly back to crowded consulates in Hyderabad or Mumbai — where visitor-visa waits run past a year — just to renew a stamp; the domestic pilot would let them do it without leaving the country.",
    "tags": ["travel", "visa", "h1b", "immigration", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian EYE — US to launch new plan for work visas in December", "url": "https://theindianeye.com/us-to-launch-new-plan-for-work-visas-in-december-likely-to-benefit-the-indians-most/"},
        {"name": "VisaVerge — US Visa Process for Indians 2026", "url": "https://www.visaverge.com/documentation/us-visa-process-for-indians-2026-new-rules-wait-times/"},
        {"name": "NRI Globe — NRI News Roundup June 8 2026", "url": "https://nriglobe.com/nri-news-roundup-june-8-2026/"}
    ]),
    "score_total": 85,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32642491/pexels-photo-32642491.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A US passport with travel documents and tickets, the stamp Indian professionals currently fly home to renew.",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": """For the Indian tech worker on an H-1B, the visa stamp has long carried a quiet dread. The visa itself can be renewed on paper, but the physical stamp inside the passport — the thing an airline checks before it lets you board back to the United States — has to be issued by a US consulate abroad. In practice, that has meant booking a trip to India, gambling on an appointment slot, and hoping nothing goes wrong while you are 8,000 miles from your job and your kids' school.

That gamble is about to get smaller. The US State Department has confirmed it will begin a **domestic visa renewal pilot in December 2026**, issuing 20,000 visas to people who are already inside the country. The vast majority of those, officials say, will be Indian nationals.

## What the pilot actually does

"We want to make sure that Indian travelers can get appointments as quickly as possible," said Julie Stufft, Deputy Assistant Secretary of State for Visa Services. "One way we are doing that is through the domestic visa renewal program, which is focused very much on India."

The mechanics are simple but consequential. Instead of mailing your passport to a consulate overseas or flying to one, eligible applicants will be able to renew certain visa categories — H-1B chief among them — from within the US. Stufft framed it bluntly: the program "will prevent people from having to travel back to India or anywhere for a visa appointment to get their visa renewed."

A federal register notice — the first formal step — is expected shortly, laying out who qualifies in the first tranche and how to apply. The initial batch is capped at 20,000, with the State Department signaling it will expand the program as it scales.

## Why the wait times make this urgent

The reason this matters is buried in the appointment calendar. As of March 2026, visitor-visa waits stood at roughly **442 days in New Delhi, 429 days in Hyderabad, and 10 months in Mumbai**. Even where work-visa waits are shorter — 10 to 37 days across the major posts — the act of physically getting to a consulate in India turns a routine renewal into a multi-week ordeal involving flights, leave from work, and the risk of administrative processing that can strand a traveler abroad indefinitely.

In 2025, the US issued over 1.4 million visas to Indian nationals, more than any other nationality. Every one of those renewals that can be handled domestically frees up an interview slot back in India for a first-time applicant — which is precisely the secondary benefit Stufft highlighted: it lets US missions in India "concentrate on new applicants."

## What it means for the diaspora

For Indian Americans, this is one of the more practical pieces of good news in a year crowded with harder immigration headlines — the $100,000 supplemental H-1B fee that remains in effect, the wage-weighted lottery now favoring higher earners, and EB-1 and EB-2 India priority dates that retrogressed in the June visa bulletin.

The domestic renewal pilot does not touch any of that. But it removes a specific, expensive friction point: the renewal trip. A Bay Area engineer whose stamp is expiring no longer has to weigh a two-week trip to Hyderabad against the risk of being unable to return. A family in New Jersey can plan summer travel around what they actually want to do, rather than around a consular appointment.

## What to watch

The program was announced by Prime Minister Modi during his address to the diaspora at the Ronald Reagan Centre and folded into the broader India-US joint statement, which gives it political momentum on both sides. Still, the details that matter — exact eligibility, which visa classes beyond H-1B are included, and how applicants will be selected for the first 20,000 slots — will only be clear once the federal register notice publishes.

If you are an Indian professional in the US with a stamp expiring in 2027, the move is straightforward: hold off on booking that renewal trip to India until the notice lands. The pilot may well let you skip the flight entirely.
"""
},
{
    "id": str(uuid.uuid4()),
    "headline": "Landing in India? The Paper Arrival Form Is Gone — Here's the App You Now Need Before You Fly",
    "subheadline": "The e-Arrival Card is fully mandatory for OCI cardholders and foreign nationals, and it must be filed within 72 hours of touchdown.",
    "slug": make_slug("india-e-arrival-card-mandatory-su-swagatam-app-oci-guide"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "OCI cardholders — the legal status most US-born and naturalized NRIs travel on — are explicitly covered by the new rule, so the family flying to Mumbai this summer now has paperwork to do before they leave home, not on the plane.",
    "tags": ["travel", "india", "oci", "immigration", "airports"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Envoy Global — India e-Arrival Card for All Foreign Nationals", "url": "https://www.envoyglobal.com/blog/india-e-arrival-card-for-all-foreign-nationals-within-72-hours-before-arrival/"},
        {"name": "U.S. Embassy & Consulates in India — India's new digital arrival system", "url": "https://in.usembassy.gov/indias-new-digital-arrival-system/"},
        {"name": "Wego Travel Blog — India e-Arrival Card 2026", "url": "https://blog.wego.com/india-e-arrival-card/"}
    ]),
    "score_total": 80,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/15068317/pexels-photo-15068317.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A traveler using a smartphone in an airport terminal — the e-Arrival Card is now filed online before flying to India.",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": """If you flew to India last year, you remember the ritual: a flight attendant handing out a small paper disembarkation card somewhere over the Arabian Sea, and the scramble to fill it in with a borrowed pen before landing. That ritual is over. As of **April 1, 2026, India's digital e-Arrival Card is fully mandatory**, and the paper form has been discontinued.

For the diaspora, the detail that matters most is who it applies to. The requirement covers **all foreign nationals and, crucially, Overseas Citizen of India (OCI) cardholders** — the very status most US-born or naturalized NRIs carry when they visit family. Only Indian passport holders are exempt. If you travel to India on a US passport with an OCI card, you now have a form to file before you fly.

## How it works

The e-Arrival Card replaces the paper form, but it is not a visa and does not replace one. It is purely an arrival-information declaration, integrated into India's immigration clearance process and cross-checked against your visa and travel records at the counter.

The rules are specific:

- **File within 72 hours of arrival** — no earlier. The system will not accept a submission made a week out, a common mistake that leaves travelers scrambling at the gate.
- **Submit through one of three official channels**: the Bureau of Immigration website (boi.gov.in), the Indian visa portal (indianvisaonline.gov.in/earrival), or the official **Indian Visa Su-Swagatam** mobile app, available for Android and iOS.
- **It is free.** Avoid any third-party site that asks for payment — these are scams that have proliferated around the rollout.

You will need your passport details, flight and arrival information, your purpose of visit, your accommodation address in India, and a list of countries you visited in the days before arrival. Submit it correctly and the system generates a **QR code** that you present at immigration.

## What to expect at the airport

The process at the counter now hinges on timing. Forms submitted within 72 hours before arrival generate a code you present at customs to complete clearance. The enforcement is live at all major international gateways — **Delhi, Mumbai, Bengaluru, Chennai, Hyderabad, Kolkata, Kochi, and Ahmedabad** — as well as seaports and land crossings.

Delhi, Mumbai, and Bengaluru have set up **dedicated assist desks** near immigration for travelers who arrive without having completed the card or who hit a snag with the QR code. That is a useful safety net, but it is exactly the queue you want to avoid after a 16-hour flight with jet-lagged kids in tow.

## Why India is doing this

The shift is part of the government's broader digitization push. Delhi International Airport has marketed it as "a seamless, paperless arrival experience," and the Bureau of Immigration says it is meant to cut queues and shorten wait times while tightening security. The e-Arrival Card first went live in October 2025 with a six-month transition window during which the paper form was still accepted; that window closed on April 1.

Travel analysts have been measured about how much it actually transforms the arrivals experience — the deeper bottlenecks in Indian airport immigration are about staffing and infrastructure, not paperwork. But for the individual traveler, the practical takeaway is clear.

## The NRI checklist

Before your next trip home, three things:

1. **Download the Su-Swagatam app** or bookmark the official portal — and ignore any site charging a fee.
2. **Set a reminder for the 72-hour window.** File too early and the submission may not be valid on arrival.
3. **Have your India address ready**, including the relatives you are staying with, since the form requires it.

It is one more box to tick before you board. But ticking it at home, in your own time, beats discovering at the immigration counter that the paper card you were expecting no longer exists.
"""
},
{
    "id": str(uuid.uuid4()),
    "headline": "Indian Travelers Are Discovering the 'Coolcation' — and Finland's Arrivals From India Just Jumped 52%",
    "subheadline": "As a heat-weary, rupee-squeezed summer reshapes travel, the Nordic north is emerging as the diaspora's contrarian escape.",
    "slug": make_slug("finland-coolcation-indian-arrivals-surge-nri-nordic-escape"),
    "category": "travel",
    "vertical": "tourism",
    "diaspora_angle": "For NRIs scoping a summer trip that isn't another sweltering week in Delhi or an overpriced flight to London, Finland's surging popularity and visa-free access for many diaspora passport holders make the Nordic 'coolcation' a genuinely fresh option.",
    "tags": ["travel", "finland", "nordic", "summer", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World — Finland 93 visa-free countries report", "url": "https://www.travelandtourworld.com/news/article/france-joins-us-italy-greece-switzerland-germany-uk-hungary-denmark-uae-and-more-among-93-visa-free-countries-boosting-finland-tourism/"},
        {"name": "Reuters — India's Royal Orchid plans to add 50 hotels", "url": "https://www.reuters.com/business/indias-royal-orchid-plans-add-50-hotels-betting-local-demand-boost/"},
        {"name": "NBC — Soaring Airfares Reshape Summer Travel Plans", "url": "https://nbcpalmsprings.com/2026/soaring-airfares-reshape-summer-travel-plans-as-fuel-costs-drive-domestic-vacation-surge/"}
    ]),
    "score_total": 68,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17408748/pexels-photo-17408748.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Helsinki Cathedral under a clear sky — Finland is drawing a record wave of Indian visitors in 2026.",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": """There is a word doing the rounds in travel circles this year, and it is not "staycation." It is **"coolcation"** — the deliberate choice to fly somewhere cold while much of the world bakes. And the data suggests Indian travelers have embraced it faster than almost anyone. Finland reported that **Indian arrivals surged 52% in early 2026**, one of the steepest jumps from any source market.

For the diaspora — caught this summer between a heat-battered Indian subcontinent, a weak rupee, and transatlantic airfares that have spiked 30 to 45% year-on-year — the Nordic north is starting to look less like an indulgence and more like a smart hedge.

## Why Finland, why now

Finland welcomed a record 5.1 million foreign tourists in 2025, and 2026 is running 7.1% ahead in early-year arrivals. Helsinki, Rovaniemi, and Finnish Lapland are all reporting sharp growth, with long-haul markets — India and the broader Asia-Pacific — driving an outsized share of it.

The appeal is partly meteorological. While Delhi pushes past 45°C and the American Southwest swelters, a Finnish summer hovers in the comfortable high teens and low twenties, with daylight stretching past midnight. The "coolcation" pitch — temperate weather, clean air, dramatic landscapes, and none of the crush of an overtouristed Mediterranean coast — lands neatly with families looking for something different.

There is also an access story underneath the trend. Finland sits inside the Schengen Area, and a recent industry tally placed it among destinations reachable visa-free for citizens of 93 countries. For diaspora travelers holding US, UK, Canadian, or EU passports, that means Finland is a no-separate-visa trip; for those on an Indian passport, a single Schengen visa unlocks Finland alongside two dozen neighboring countries — useful leverage for a multi-stop European itinerary.

## The economics that are reshaping summer

This Finnish surge is not happening in a vacuum. It is part of a broader rewiring of how people — including NRIs — are planning summer 2026.

Jet-fuel costs have climbed sharply after disruptions in the Strait of Hormuz, and airlines have responded by trimming routes and raising fares. Kayak data shows flights to London up more than 45% year-on-year, with average fares jumping past $1,100, and Paris fares up over 30%. Expedia found 63% of US travelers are now prioritizing domestic trips, partly to be near FIFA World Cup matches and America 250 celebrations.

The same pressures are visible back in India. Royal Orchid Hotels announced plans to add 50 properties in 12 to 18 months, with its founder explicitly betting that "a lot of people who were planning to go for holidays to the Middle East and other places cancelled their trips and boosted domestic tourism demand." When the familiar routes get expensive or fraught, travelers go looking for alternatives — and a chunk of them are landing in Helsinki.

## What it means for the diaspora traveler

For an NRI family weighing the summer options, the calculus is shifting. The default trips — a sweltering week in India, an overpriced London layover, a Mediterranean beach packed shoulder to shoulder — all carry friction this year. A Nordic coolcation offers a contrarian alternative: cooler temperatures, manageable crowds, and, for many passport holders, a smoother entry.

Practical notes if you are tempted. Lapland is the marquee winter draw — Northern Lights, husky sleds, the Santa Village at Rovaniemi — but a **summer** trip trades the aurora for the midnight sun, hiking, and lake country, often at lower prices and with far thinner crowds. Helsinki makes an easy, walkable base with strong onward rail and ferry links to Tallinn and Stockholm. And because Finland anchors a Schengen itinerary, it pairs naturally with a wider Baltic or Scandinavian loop on one visa.

The "coolcation" may have started as a marketing coinage. But with a 52% jump in Indian arrivals, it is now a genuine trend — and one the diaspora is helping to drive.
"""
}
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
