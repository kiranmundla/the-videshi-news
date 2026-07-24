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

article1_body = """The Indian Embassy in the United Arab Emirates is about to go quiet for five days, and the timing will catch a lot of families flat-footed. From **June 26 to June 30, 2026**, routine passport, visa and attestation appointments across the UAE will be suspended while the mission swaps out its outsourced service provider. Routine bookings resume July 1.

This is not a shutdown — it is a handover. The current operators, **BLS International** and **SGIVS Global**, stop accepting new applications at close of business on **Thursday, June 25**. From July 1, a new contractor, **Al Hind Tours and Travel LLC**, takes over passport, visa and attestation services, with a fresh online appointment portal going live the same day. Applications already submitted before the cutoff will keep moving through the existing centres without disruption.

## Why this matters to the diaspora

The UAE is home to roughly 3.5 million Indians — the single largest expatriate community in the country and one of the most important nodes in the global Indian diaspora. Many are not citizens of their host country; they live on residence permits and rely on the Indian mission for the paperwork that anchors their lives abroad: renewing a passport, registering a newborn, getting a document attested for a property deal back home, or securing a visa for a visiting relative.

For NRIs in the US, UK and Canada, the UAE link runs deeper than it looks. The Gulf is the layover capital of the diaspora — the place where family routes converge, where parents stop en route to visit children, and where a surprising number of cross-border document chores get done because consular access there has historically been faster than in North America. A planning break in Dubai or Abu Dhabi ripples outward.

## What to do before Thursday

The embassy's guidance is blunt and worth following:

- **If your need is urgent, file before close of business June 25.** Anything submitted through BLS or SGIVS before the cutoff continues to be processed normally.
- **If it can wait, wait.** Non-urgent passport and visa work should be deferred until the new portal opens July 1, rather than scrambling for a slot that does not exist during the freeze.
- **Genuine emergencies are still covered.** Medical crises, deaths in the family and other critical matters are handled directly by the Embassy of India in Abu Dhabi and the Consulate General in Dubai. The mission has published a toll-free line (800 46342), a WhatsApp number (+971 54 309 0571) and an email channel for these cases.
- **Use official sources only.** The embassy has explicitly warned against unofficial third-party agents and outdated booking links during the transition — exactly the window when scam operators tend to surface.

## The bigger picture

Service-provider changes at Indian missions are routine on paper and disruptive in practice. The diaspora has learned this the hard way through the OCI portal migration earlier this year and the broader shift of consular work onto VFS Global and BLS International around the world. Each handover promises smoother digital processing and delivers, in the short term, a queue.

The lesson for NRIs is the same one that applies to every consular interaction in 2026: build slack into the calendar. A passport that expires within a year, a visa appointment for visiting parents, an attestation needed for a home loan — none of these should be left to the last clear week before travel. The UAE freeze is only five days. The next provider transition, somewhere in the consular network, is never far off.

For families routing through the Gulf this summer, the practical takeaway is simple. Sort the paperwork now, or sort it after the first of July — but not in between."""

article2_body = """The United States will start selling speed at its visa windows. From **July 1, 2026**, eligible business and tourism applicants can pay an extra **$750** to lock in an interview appointment within **10 business days** — a pilot program that runs through December 31 and, for the Indian diaspora, lands squarely on one of its rawest nerves: the wait.

The State Department's Bureau of Consular Affairs is framing the surcharge, formalised in a Temporary Final Rule, as an optional time-saver rather than a fast track to approval. The fee sits on top of the standard **$185** visa application fee, and it buys exactly one thing: a faster slot. Background checks, administrative reviews and the final decision still run on their normal timelines. Pay the $750 and you may reach the interview chair sooner; you are no more likely to walk out with a visa.

## The backlog the fee is chasing

To understand why this matters, look at the numbers coming out of US consulates in India. Employment-based applicants for H and L visas are facing waits of **75 to more than 125 days** in Chennai, Hyderabad, Kolkata, Mumbai and New Delhi, according to immigration firm Fragomen. Kolkata, long the relief valve with a 13-day backlog, has ballooned to 126 days. The cause is structural: demand has surged for months while consular staffing has not grown.

Visitor and student visas tell a calmer story — B-1/B-2 and F-1 waits in India currently run from a few days to around three weeks — but the broader global picture is grim, with first-time tourist applicants in some markets staring down waits beyond a year.

## Why this hits NRIs hardest

No community feels the US-India visa machine more acutely than the diaspora. This is the population that flies parents over for the birth of a grandchild, sponsors siblings' visits, and hosts a rotating cast of relatives for weddings and graduations. When a B-1/B-2 appointment for visiting parents is months out, it is not an abstraction — it is a missed milestone.

The pilot's design, though, comes with a catch the diaspora should read carefully. The program is limited to **B-1 (business) and B-2 (tourism)** applicants. It does not cover the employment-based H and L categories where India's backlogs are worst — the very visas that keep the tech corridor between Bengaluru and the Bay Area moving. And crucially, the State Department has **not yet published which embassies and consulates will participate.** Whether India's missions are even in the pilot remains unconfirmed.

## Do the math before you pay

At $750 on top of $185, the expedited route costs nearly five times the base fee. For a family of four flying parents and in-laws over, that is a meaningful sum stacked on already-rising airfares. The calculus only works if three things are true: your consulate is in the pilot, your visa type qualifies, and your travel genuinely cannot flex around the standard queue.

For most NRIs bringing relatives over for a fixed event — a wedding date, a due date, a convocation — the guarantee of an interview within 10 business days may be worth it. For everyone else, the old advice still holds: apply early, check the portal obsessively for cancellation slots, and treat the $750 as insurance, not a solution. After December, the State Department will decide whether the experiment lives on. Until then, it is a premium lane on a road that is still very much congested."""

article3_body = """The single longest nonstop flight in American Airlines' entire global network is not a transpacific marathon to Australia or a polar haul to Asia. It is the daily run between **New York's JFK and Delhi** — and in 2026 it stretches to a punishing **17 hours** in the air. For the tri-state diaspora, that number is both a badge of convenience and a quiet warning about the state of the India-US sky bridge.

According to scheduling data from aviation analytics firm Cirium, American has nine routes between June and December 2026 with maximum block times above 14 hours. JFK-Delhi tops the list. When American launched the route in November 2021, the return leg was blocked at 16 hours and 39 minutes. The reason it has crept toward 17 is geopolitical, not commercial: with **Russian airspace closed** to US carriers, the Boeing 787-9 now flies a longer, more circuitous arc to stay clear of it. The aircraft seats 285 passengers across three cabins and operates daily.

## The Russia detour is a diaspora tax

That extra time is not a rounding error. A longer block means more fuel, more crew hours and tighter aircraft scheduling — costs that flow straight into fares on exactly the routes NRIs depend on. Indian and US carriers can still overfly Russia, but American, United and Delta cannot, which is why US-flag nonstops to India now run noticeably longer than their Gulf-routed or Air India counterparts. Every diaspora traveller who has compared a nonstop fare against a one-stop through Doha or Dubai has felt the edge of this asymmetry.

It also reshapes the competitive map. American's own pitch leans on its **Qatar Airways partnership** and its Seattle-Bengaluru route to argue it offers more US-India connections than any rival alliance. In other words, the nonstop is the flagship, but the connecting product through the Gulf is the workhorse — a tacit admission that the 17-hour haul is as long as the math comfortably allows.

## Why the route still matters

For the roughly 700,000-strong Indian community across New York, New Jersey and Connecticut, a daily nonstop to Delhi is precious. It removes the Gulf or European layover that turns a long trip into an ordeal with elderly parents or young children in tow. It keeps baggage on one aircraft. And it gives the Northeast a same-metal link to the Indian capital that complements Air India's own JFK and Newark services.

But 17 hours is near the practical ceiling for a twin-engine widebody on this corridor, and the padding is a reminder that the convenience is fragile. Should fuel prices spike or demand soften, ultra-long routes operating this close to the limit are the first candidates for trimming — a pattern the diaspora has already watched play out with Air India's summer pullback of some US nonstops.

## What flyers should take from this

Three practical notes. First, **book the nonstop early if you need it** — daily does not mean abundant, and these flights fill in the summer and Diwali peaks. Second, **weigh the time against the price**: a one-stop through the Gulf can be hours longer door-to-door but materially cheaper, and for flexible travellers the saving is real. Third, **watch the schedules**, because as long as Russian airspace stays shut, the US-India nonstop map will keep flexing — and the route that is 17 hours today could be re-timed, re-fleeted or thinned tomorrow.

For now, the JFK-Delhi run holds a peculiar distinction: the longest line American flies anywhere on earth, drawn that way not by geography but by a war's airspace, and carrying a community home one ultra-long night at a time."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's UAE Consulates Go Dark for Five Days From June 26 — Sort Your Passport Before Thursday or Wait Until July",
        "subheadline": "The Indian Embassy is swapping service providers across the UAE, freezing routine passport, visa and attestation appointments from June 26 to 30. Here's how the diaspora's busiest consular hub navigates the gap.",
        "slug": make_slug("india-uae-embassy-consular-services-pause-june-26-30-passport-visa-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "The UAE hosts the world's largest Indian expatriate community and serves as the Gulf transit hub for NRIs worldwide, so a five-day freeze on passport, visa and attestation services forces millions to either file before June 25 or defer until the new portal opens July 1.",
        "tags": ["travel", "visa", "passport", "UAE", "consular", "diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/indian-embassy-bls-international-sgivs-global-halt-uae-visa-services-till-june-30/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/urgent-update-changes-to-indian-visa-and-passport-services-in-uae/"},
            {"name": "Channel I'M", "url": "https://en.channeliam.com/2026/06/23/india-embassy-uae-pauses-services/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "An open passport showing immigration stamps from international travel",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The US Will Sell You a Visa Interview in 10 Days for $750 — but Read the Fine Print Before the Diaspora Reaches for It",
        "subheadline": "A State Department pilot running July through December lets B-1/B-2 applicants pay to skip the appointment queue. It won't speed approvals, may not include India, and skips the employment visas where the backlog is worst.",
        "slug": make_slug("us-expedited-visa-interview-750-fee-pilot-b1b2-india-diaspora-backlog"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "NRIs routinely sponsor parents and relatives on B-1/B-2 visas for weddings, births and graduations, so a paid fast lane to a 10-day interview slot is tempting — but it excludes the H and L work visas where India's backlogs run past 125 days and may not even cover Indian consulates.",
        "tags": ["travel", "visa", "USA", "immigration", "diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/global/news/us-visa-interview-750-appointment-10-days/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/travelnews/us-to-offer-faster-visa-appointments-within-10-days-for-an-additional-fee"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-u-s-consulates-in-india.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32642490/pexels-photo-32642490.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "A US passport with travel documents and tickets laid out on a table",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "American Airlines' Longest Flight on Earth Is Now JFK–Delhi at 17 Hours — and the Reason Is a Tax on the Diaspora",
        "subheadline": "Closed Russian airspace has pushed the daily New York–Delhi nonstop to the top of American's global network. For the tri-state diaspora, the marathon is both a lifeline and a warning.",
        "slug": make_slug("american-airlines-jfk-delhi-17-hour-longest-flight-russia-airspace-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The JFK-Delhi nonstop is a lifeline for the 700,000-strong tri-state Indian community, but the Russia-airspace detour that made it American's longest route also drives up fares and makes ultra-long US-India nonstops the first candidates for cuts.",
        "tags": ["travel", "airlines", "American Airlines", "JFK", "Delhi", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Simple Flying", "url": "https://simpleflying.com/american-airlines-ultra-long-routes-2026/"},
            {"name": "American Airlines Newsroom", "url": "https://news.aa.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18136344/pexels-photo-18136344.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "View of clouds and sunset from an airplane window at cruising altitude",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
