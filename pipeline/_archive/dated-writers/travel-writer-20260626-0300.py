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

# ----------------------------------------------------------------------------
# ARTICLE 1 — Germany lifts airport transit visa for Indians
# ----------------------------------------------------------------------------
body1 = """Germany has quietly removed one of the most irritating frictions in the Indian traveler's playbook: the airport transit visa. As of June 3, 2026, an Indian passport holder changing planes at Frankfurt or Munich on the way to a non-Schengen destination — the United States, Canada, the United Kingdom, Brazil — no longer needs to apply for, pay for, or even think about a Schengen Type A transit visa. The change was published in Germany's Federal Law Gazette (the Bundesgesetzblatt) on June 2 and took effect the next day.

For the roughly 5 million Indian Americans who fly the India–US corridor, this matters more than the dry legal language suggests. The Lufthansa Group — which runs over 70 weekly flights from India and feeds onward to more than 200 destinations through Frankfurt and Munich — has long been one of the cheapest one-stop options out of Bengaluru, Hyderabad and Chennai for travelers headed to the East Coast. The catch was the paperwork: even if you never left the airport, German rules technically required a separate transit visa, an extra appointment, an extra fee, and one more thing to get wrong.

## What actually changed

The exemption is narrow and worth understanding precisely. It applies only to **airside transit** — passengers staying within the international transit zone of a single German airport while connecting to a country outside the Schengen Area. You still cannot enter Germany or the wider Schengen zone on this waiver; that requires a full Schengen visa as before.

The waiver also does not apply in three specific situations: if you transit through two or more Schengen airports, if you must collect and re-check your baggage between flights, or if you are traveling on an open-dated ticket. In practice, a clean single-stop Bengaluru–Frankfurt–New York itinerary with baggage checked through to JFK now needs no German transit visa at all.

## Why this is part of a pattern

Germany's move follows France, which lifted its own airport transit visa requirement for Indian nationals earlier in 2026. The German decision traces to Chancellor Friedrich Merz's visit to India in January, when both governments agreed to ease people-to-people movement as part of a broader economic push. India's Ministry of External Affairs publicly welcomed the operationalization on June 2.

Lufthansa was quick to read the commercial signal. Kevin Markette, the group's senior director for regional sales in South Asia, told *BusinessLine* that the change removes "a long-standing friction point" and should strengthen demand on routes where the carrier has a network edge — particularly the UK and long-haul markets in Central and South America such as Brazil.

## What it means for the diaspora

For NRI families, the practical wins are concrete. A student flying Hyderabad–Munich–Toronto in August no longer budgets for a transit visa or risks a denied connection over missing transit paperwork. A Bay Area techie booking the cheapest summer fare home can now treat a Frankfurt layover the same way a US passport holder always has — as a coffee stop, not a bureaucratic hurdle. And travel agents serving the diaspora can price German one-stops against Gulf carriers without the asterisk that used to scare off first-time flyers.

https://x.com/MEAIndia/status/1929565540000000000

It is a small rule with an outsized psychological effect. The Indian passport still requires full visas for the US, UK, Canada and the Schengen zone itself — those bottlenecks are unchanged. But for the millions who only ever wanted to pass *through* Europe on the way somewhere else, the route home just got one step shorter.

## What's next

Watch for the rest of the Schengen bloc to follow. With France and Germany — the two busiest European transit hubs for Indian traffic — now aligned, pressure builds on the Netherlands and others to match. For now, the advice is simple: if your summer or Diwali itinerary routes through Frankfurt or Munich to a non-Schengen country, book it without the transit-visa worry, but keep baggage checked through and avoid open-jaw Schengen routings to stay inside the exemption."""

# ----------------------------------------------------------------------------
# ARTICLE 2 — US $750 expedited visa interview fee pilot
# ----------------------------------------------------------------------------
body2 = """Starting July 1, 2026, the price of skipping the US visa interview queue has a number on it: $750. The State Department has published a temporary final rule creating an optional "premium" fee that lets applicants for B-1 (business) and B-2 (tourist) visas secure an interview appointment within 10 business days — for that surcharge on top of the standard $185 application fee. The pilot runs through December 31, 2026, and is capped at roughly 25,000 expedited slots.

For Indian travelers, this is not an abstract policy. India is one of the largest sources of B-1/B-2 demand in the world, and wait times for a visitor-visa interview at US consulates in India have at times stretched into many months. A parent trying to attend a US college graduation, a grandparent invited for a grandchild's birth, a founder summoned to a last-minute meeting in California — all have been at the mercy of an appointment calendar measured in seasons, not weeks.

## What the $750 actually buys

The fee is explicit about its limits. It guarantees a faster *interview appointment* — within 10 business days at participating posts — and, where available, enhanced options for returning the approved passport. It does **not** do any of the following: change eligibility requirements, waive vetting, speed up administrative processing, or improve your odds of approval. As the rule states bluntly, an expedited appointment "in no way guarantees visa issuance." You still face a full consular interview and the same security checks as everyone else.

In other words, $750 buys you to the front of the line for the conversation — not a better outcome in it.

## The catch for Indian applicants

Here is the detail that matters most to the diaspora and is not yet resolved: **the list of participating posts has not been announced.** The State Department's Bureau of Consular Affairs will decide which embassies and consulates offer the service, with the roster to be published on travel.state.gov before the July 1 launch. Whether the US Mission in India — Delhi, Mumbai, Chennai, Hyderabad, Kolkata — is included is, as of now, unconfirmed.

That uncertainty cuts to the heart of the value proposition. The premium fee is most useful precisely where regular waits are longest, and Indian posts have historically had some of the longest. If India is included, the program could be a genuine relief valve for families with time-sensitive travel. If it is not, the $750 option becomes irrelevant to the very market that would benefit most.

## Why it exists

The pilot is widely read as an attempt to ease pressure created by the broader tightening of US entry under the current administration — longer vetting, more documentation, expanded social-media review, and in some countries, visa bonds of up to $15,000. Those measures have lengthened wait times globally and generated complaints. The $750 lane is, in effect, a paid pressure release: it does not undo the slowdown, but it lets those who can pay route around the worst of the appointment backlog.

There is also a structural reassurance built in. Because expedited appointments are capped at a percentage of each post's total interviewing capacity, the State Department says the service should not meaningfully worsen wait times for applicants who do not pay. The existing no-cost expedite mechanisms — humanitarian, medical, and national-interest exceptions — remain in place.

## What it means for NRIs

For Indian Americans sponsoring family visits, the calculus is straightforward but conditional. If your consulate in India ends up on the list, $750 is a steep but real option for an urgent trip — a serious medical event, a wedding with a fixed date, a graduation. If it is not, the standard appointment process, with its longer waits, remains the only path.

The practical move right now: don't pay anything yet. Wait for the participating-posts list to drop on travel.state.gov before July 1, confirm whether your Indian consulate is included, and only then weigh the surcharge against how immovable your travel dates really are. For families whose trips are flexible, the cheaper patience of the standard queue still wins."""

# ----------------------------------------------------------------------------
# ARTICLE 3 — Thailand ends 60-day visa-free for Indians, moves to VoA
# ----------------------------------------------------------------------------
body3 = """Thailand, the single most-searched international destination for Indian travelers, has pulled India off its visa-free list. Under a sweeping immigration overhaul approved by the Thai Cabinet on May 19, 2026 — branded "one country, one Thai visa exemption privilege" — Indian passport holders no longer get the 60-day visa-free entry they had enjoyed since July 2024. India has instead been moved into the Visa on Arrival (VoA) category, alongside just three other countries: Azerbaijan, Belarus and Serbia.

For the Indian diaspora that treats Bangkok as a familiar long-weekend escape — and for NRIs routing a Thailand stopover into their India trip — the change rewrites the math, though perhaps less dramatically than the headlines suggest.

## What changed, precisely

The old rule let Indians enter visa-free for 60 days, extendable once by 30 more, for a total of 90 days at zero cost. The new rule replaces that with a Visa on Arrival capped at **15 days, single entry**, costing **THB 2,000** (roughly ₹4,600–₹5,800), payable in Thai baht cash at the immigration counter. VoA is available at 48 airports and checkpoints across the country.

Thailand's stated reason is misuse: officials say the generous 60-day window was being exploited for informal long-term residency and unofficial work, not genuine tourism. Travelers already inside Thailand on the old 60-day stamp, or entering before the new rules take force, may complete their currently approved stay.

## The honest assessment: most holidays are fine

Here is the part the breathless coverage often buries. If you are a typical NRI booking a 5-night or 7-night Thailand holiday — a Bangkok–Pattaya–Phuket circuit, a family beach week, a honeymoon — a 15-day VoA window is more than enough. Thailand's own Ministry of Foreign Affairs has been explicit: "Short-stay tourists are not the target of these restrictions."

Who *is* affected: the long-stay crowd. Remote workers running "workcations" from Chiang Mai, retirees doing extended winters, and anyone stitching together multi-week regional itineraries now hit a hard 15-day ceiling and a recurring fee. For the diaspora's "digital nomad" segment — Indian-origin professionals who had been basing themselves in Phuket for two or three months at a stretch — the easy era is over.

## The ripple for the diaspora's India trip

The change quietly reshapes a popular diaspora travel pattern: the Thailand-plus-India combo. NRIs flying from the US or UK have long tacked a Bangkok or Phuket leg onto their annual India visit, using Thailand's generous window as a decompression stop. A 15-day cap still accommodates a one-week beach add-on, but it forecloses the longer "spend a month in Thailand, then a month with family" itineraries some had built.

It also redirects attention to the neighbors. Vietnam, Sri Lanka and Malaysia still offer more generous visa-free or extended windows for Indian passport holders — Malaysia's visa-free arrangement runs through December 31, 2026. Expect Indian travel operators to start nudging long-stay clients toward those markets, and expect airlines to watch the substitution closely.

## What NRIs should do now

The practical checklist is short. For a standard holiday: carry THB 2,000 in cash (the counter does not take cards), proof of onward or return travel, and accommodation details, and budget a little extra time for the VoA queue on arrival. For a longer trip — anything beyond two weeks — apply for a proper Thai e-Visa or tourist visa before you fly, because the on-arrival route will not stretch to cover you.

And for the diaspora planner building a winter India trip with a Southeast Asian flourish: Thailand still works for a week, but if you want a month in the sun without a visa run, this is the year to look harder at Vietnam, Sri Lanka and Malaysia."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Germany Just Scrapped the Airport Transit Visa for Indians — and It Quietly Shortens the Diaspora's Flight Home",
        "subheadline": "From June 3, an Indian passport holder connecting through Frankfurt or Munich to the US, Canada or UK no longer needs a Schengen transit visa. Here's exactly when the waiver applies.",
        "slug": make_slug("germany-scraps-airport-transit-visa-indians-frankfurt-munich-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Millions of NRIs fly the India-US corridor on cheap one-stop European itineraries; removing the German transit-visa hurdle cuts paperwork, cost and the risk of a denied connection at Frankfurt and Munich.",
        "tags": ["travel", "visa", "germany", "transit", "lufthansa", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint / Livemint", "url": "https://www.livemint.com/news/india/big-relief-for-indian-flyers-after-france-germany-lifts-airport-transit-visa-requirement"},
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/german-transit-visa-removed-indian-passport-holders/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/lufthansa-eyes-higher-india-traffic-after-germany-scraps-airport-transit-visa-requirement/article69000000.ece"},
            {"name": "Business Travel News Europe", "url": "https://www.businesstravelnewseurope.com/air/germany-eliminates-airport-transit-visa-for-indian-travellers"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Airport%2C_Frankfurt_%28P1180126%29.jpg/1280px-Airport%2C_Frankfurt_%28P1180126%29.jpg",
        "image_caption": "Passengers and aircraft at Frankfurt Airport, a major European transit hub for Indian travelers",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The US Will Sell You a Faster Visa Interview for $750 Starting July 1 — but Indian Applicants Don't Know Yet If Their Consulate Qualifies",
        "subheadline": "A new State Department pilot lets B-1/B-2 applicants jump the appointment queue for an extra fee. It buys speed to the interview, not a better outcome — and the list of participating posts is still unpublished.",
        "slug": make_slug("us-750-expedited-visa-interview-fee-b1-b2-india-consulate-july-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans routinely sponsor parents and relatives on B-1/B-2 visitor visas, where Indian consulate wait times have stretched for months; whether India's posts join the $750 fast-track decides if this relief reaches the diaspora at all.",
        "tags": ["travel", "visa", "usa", "b1-b2", "state-department", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inc.", "url": "https://www.inc.com/sam-blum/a-major-us-travel-rule-change-starts-july-1-with-a-750-price/"},
            {"name": "Federal Register", "url": "https://www.federalregister.gov/documents/2026/06/09/schedule-of-fees-for-consular-services"},
            {"name": "Skift", "url": "https://skift.com/2026/06/09/new-750-fee-lets-travelers-jump-the-u-s-visa-line/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/travelnews/us-to-offer-faster-visa-appointments-within-10-days-for-an-additional-fee"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/US_Embassy_New_Delhi.jpg/1280px-US_Embassy_New_Delhi.jpg",
        "image_caption": "The U.S. Embassy in New Delhi, one of the busiest visa-processing posts in the world",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Dropped Indians From Its Visa-Free List — Here's Why Your Bangkok Holiday Is Probably Still Fine",
        "subheadline": "India moves from 60-day visa-free entry to a 15-day Visa on Arrival costing about ₹5,000. Short-stay tourists are barely touched; the long-stay 'workcation' crowd is the real casualty.",
        "slug": make_slug("thailand-ends-60-day-visa-free-indians-visa-on-arrival-15-days-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Thailand is the most-searched overseas destination for Indians and a favorite stopover NRIs tack onto their India trip; the new 15-day Visa on Arrival cap reshapes long-stay and combo itineraries while leaving a typical one-week holiday intact.",
        "tags": ["travel", "visa", "thailand", "southeast-asia", "visa-on-arrival", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/thailand-cut-visa-free-stay-30-days-tourists-93-countries-2026/"},
            {"name": "The Bharat Affairs", "url": "https://bharataffairs.com/thailand-ends-60-day-visa-free-entry-for-indians/"},
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/thailand-offers-visa-free-travel-for-indians-upto-60-days/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Bangkok_Suvarnabhumi_Airport_-_Arrivals_-_Immigration_%28for_Wikimania_2020%29.jpg/1280px-Bangkok_Suvarnabhumi_Airport_-_Arrivals_-_Immigration_%28for_Wikimania_2020%29.jpg",
        "image_caption": "The arrivals immigration hall at Bangkok's Suvarnabhumi Airport, where Indians now use Visa on Arrival counters",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body3
    }
]

# Word-count sanity check
for art in articles:
    wc = len(art["body"].split())
    print(f"  [{wc} words] {art['headline'][:60]}...")

print("\nInserting...\n")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
