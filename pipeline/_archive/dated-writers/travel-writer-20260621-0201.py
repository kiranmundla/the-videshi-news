#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
    return slug[:70].rstrip('-') + "-" + "20260621"

thailand_body = """For Indian travelers, Thailand has long been the easy yes — a visa-free hop for a beach week, a Phuket wedding, or a quick stopover on a longer Asia trip. That is about to get harder, and the diaspora planning a 2026 Thailand trip on an Indian passport needs to pay attention now.

On May 19, 2026, the Thai Cabinet approved a sweeping rollback of the 60-day visa-free entry it had extended to 93 countries, India among them. Under the revised policy, Indian passport holders will be moved to a visa-on-arrival regime: a maximum stay of 15 days, a THB 2,000 fee, and the paperwork and queues that the visa-free scheme had eliminated. The generous two-month window that made Thailand a casual destination is being pulled back to a tightly capped two weeks.

## What Has Actually Changed — and What Hasn't

The crucial detail is timing. As of late May 2026, the change is approved but not yet in force. The new rule takes legal effect only 15 days after it is published in Thailand's Royal Gazette, and that publication had not happened at the time of writing. The Tourism Authority of Thailand and the Thai Embassy in New Delhi confirmed that the existing 60-day visa exemption remains valid until the Gazette notification triggers the countdown.

In practical terms, there is a window — but no one can promise how wide it is. A trip taken before the Gazette publication, plus the 15-day grace period, still falls under the old 60-day rules. A trip after that cutoff falls under visa-on-arrival with the 15-day cap. Because no firm date has been announced, travelers are booking into uncertainty.

## Why Thailand Is Tightening

The reversal is part of a broader regional rethink of the post-pandemic open-door visa policies. Thailand extended visa-free access aggressively in 2024 to rebuild tourism, but the loosened rules also fueled concerns about visa-run workers, overstays, and people using long visa-free windows for unofficial business. Capping stays at 15 days and reattaching a fee gives Thai immigration tighter control and a clearer line between tourists and de facto residents.

## What It Means for the Diaspora

For Indian Americans, the impact splits along which passport you carry. NRIs who travel on a US passport are unaffected — the rollback targets the 93-country visa-free list, and US passport holders fall under separate arrangements. But the large share of the diaspora that still travels on an Indian passport, including green card holders and recent immigrants who have not naturalized, will feel the change directly.

The most exposed group is anyone planning a Thailand wedding or a multi-week stay. Phuket, Krabi, and Koh Samui have become popular destination-wedding venues for Indian families, and those events routinely run longer than 15 days once you count setup, ceremonies, and a post-wedding holiday. Under visa-on-arrival, a 15-day cap simply will not cover a typical wedding week plus travel — meaning families will need to apply for a proper tourist visa in advance through a Thai mission, with the lead time and documentation that involves.

Stopover travelers are the second group to watch. Indians who used Bangkok as a several-day break on the way to or from another destination will find the shorter window less forgiving, especially if onward plans shift.

## What's Next

The single most important thing to track is the Royal Gazette. Until the notification publishes, the 60-day exemption stands; once it does, the 15-day visa-on-arrival regime begins 15 days later. Travelers with Indian passports planning a long Thailand trip in late 2026 should either build flexibility into their dates or plan from the outset to secure a 60-day tourist visa from a Thai consulate rather than relying on arrival processing.

The era of treating Thailand as a no-paperwork beach run on an Indian passport is ending. For the diaspora, the move is simple: if your trip is short and soon, you are likely fine; if it is long, or far out on the calendar, assume you will need a visa in hand before you fly."""

ba_body = """Indians living in America's mid-sized cities have spent years accepting a hard truth about flying home: the more obscure your US airport, the uglier the routing to India. British Airways is quietly rewriting that math, and the diaspora in cities like St. Louis, Dallas, and Miami is the direct beneficiary.

Over the past year, BA has built out a US network that funnels straight into its India operation through London Heathrow. The carrier launched four-times-weekly service to St. Louis on April 19, runs a daily flight to Dallas/Fort Worth, and operates twice-daily service to Miami. Each of those US gateways connects at Heathrow to one of the densest India route maps any Western airline flies — and that combination turns a once-painful three-leg journey into a clean one-stop trip.

## The India Side of the Bridge

What makes the strategy work is the depth of BA's India schedule. From June 1, 2026, British Airways operates twice-daily flights to Bengaluru, runs up to three daily services to Delhi, and altogether flies 56 weekly direct services to five Indian cities through Heathrow. That frequency is the difference between a smooth connection and a marathon layover: with multiple departures a day to the major metros, a missed or delayed inbound leg does not strand a traveler overnight.

BA flies Boeing 787 Dreamliners on much of this network, with three cabin classes, and the airline says more than 75,000 passengers connected through Heathrow between the US and India on its services last year — a figure that underscores how much of this traffic is diaspora travel rather than point-to-point business.

## Why the New US Cities Matter

The headline for NRIs is geographic. Indians in St. Louis have historically had no good single-connection option to India; the city's international service is thin, and reaching Delhi or Bengaluru usually meant a domestic hop to a coastal hub followed by a long-haul leg and then the India sector. A four-times-weekly BA flight to Heathrow collapses that into one connection.

Dallas/Fort Worth tells a similar story for the fast-growing Texas diaspora. While DFW has some direct India service, a daily BA option into the Heathrow-India machine adds schedule flexibility and a strong alternative when nonstops are full or overpriced during peak season. Miami, with twice-daily Heathrow service, opens a cleaner path home for the Indian community across South Florida, which has long been underserved on India routings.

The Bengaluru piece deserves special emphasis. The twice-daily BLR service from June 1 is tailor-made for the South Indian tech corridor — the engineers, founders, and families who move between Bangalore and US tech hubs. Two daily departures means someone flying from Dallas or Miami can reach Bengaluru with a single, well-timed change rather than a connection that involves an overnight in another country.

## What It Means for the Diaspora

The practical value here is not a fare headline — it is reliability and reach. For NRIs in second-tier US cities, the choice has often been between a cheap-but-grueling multi-stop itinerary and an expensive repositioning to a coastal gateway. BA's build-out offers a third path: a single connection through one of the world's largest hubs, on a widebody, with enough daily India frequency to absorb delays.

There are trade-offs. Heathrow connections mean Terminal 5 transit times and the usual peak-season congestion, and a one-stop routing through London is rarely the cheapest option on the market. Travelers chasing the lowest fare may still prefer a Gulf carrier through Doha or Dubai. But for diaspora families who value a familiar hub, English-language transit, and the security of multiple daily onward flights, the Heathrow bridge is now genuinely competitive from cities that never had a good option before.

## What's Next

BA's expansion signals where the competition is heading: away from a handful of coastal gateways and toward the mid-sized US cities where the diaspora has spread over the past decade. For Indians in St. Louis, Dallas, and Miami planning a trip home, the advice is to price the BA one-stop against the Gulf carriers and the limited nonstops — and to weigh the value of two and three daily India departures when a tight connection is on the line."""

worldcup_body = """The 2026 FIFA World Cup is about to hand the Indian diaspora in America an unusual opportunity: a chance to watch World Cup football in Mexico without applying for a Mexican visa at all. But the rules that make it possible also come with re-entry traps that could leave an H-1B holder stranded outside the US. Here is what diaspora fans need to know before they book.

With matches scheduled across Mexico in June and July 2026, the US Embassy and Mexican authorities have issued guidance aimed squarely at the millions of foreign nationals living in the United States who want to cross the border for a game. For Indians on work and student visas, the mechanics are favorable — if you understand them.

## The Mexico Entry Rule

The key provision is straightforward: travelers who hold a valid US visa can enter Mexico visa-free for up to 180 days. That means an Indian citizen living in the US on an H-1B, L-1, F-1, or similar visa does not need to apply for a separate Mexican visa to attend a World Cup match. The valid US visa itself is the entry credential.

Travelers will still need to complete Mexico's Forma Migratoria Múltiple (FMM), the tourist entry form, when crossing. FIFA's PASS system — the fan registration tied to ticketing and stadium entry — is separate from immigration and does not replace the FMM or any visa requirement. Fans should treat the football credential and the immigration paperwork as two different things.

## The Real Risk Is Coming Back

The visa-free entry into Mexico is the easy part. The danger for diaspora fans is re-entering the United States, and this is where careful planning matters.

US immigration rules include a provision called automatic visa revalidation. Under it, certain nonimmigrant visa holders — including those on H-1B and J-1 status — can re-enter the US from a trip of less than 30 days to Mexico or Canada even if their visa stamp has expired, provided they maintain valid status and have not applied for a new visa while abroad. For a World Cup trip, that means an H-1B holder whose visa stamp lapsed can still drive or fly back from Mexico, as long as the trip stays under 30 days and they carry a valid I-797 approval and passport.

But the exceptions are sharp. Automatic visa revalidation does not apply if you apply for a new US visa while in Mexico — once you do, you must wait for it to be issued before you can return. It also generally does not extend to nationals of countries designated as state sponsors of terrorism, and it requires that the trip not exceed 30 days and not include travel beyond Mexico or Canada. An H-1B holder who pops down to Mexico for a match, then decides to renew the visa stamp at a US consulate there, can be stuck waiting if administrative processing kicks in.

## What It Means for the Diaspora

For the large Indian community on US work visas, the upshot is genuinely good news: attending a World Cup match in Mexico is achievable on a long weekend without a Mexican visa application, and even with an expired US visa stamp in many cases. Green card holders have it simplest — a permanent resident can travel to Mexico and return with a valid green card and passport, no visa questions involved.

The travelers who need to be most careful are H-1B and student-visa holders whose US stamps have expired. For them the rule of thumb is: keep the trip under 30 days, carry every status document (passport, I-797 or I-20, recent pay stubs), do not apply for a new visa while in Mexico, and confirm the latest CBP guidance before departing. Anyone with a complicated immigration history, a prior visa refusal, or pending applications should consult an immigration attorney before crossing.

## What's Next

The World Cup will draw enormous diaspora crowds to Mexican host cities, and border processing is likely to be heavy during match windows. Fans should build buffer time around games, keep digital and paper copies of all documents, and monitor US Embassy Mexico advisories as the tournament approaches. The football is the easy part; the paperwork, planned right, is what gets you back to your desk on Monday."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Is About to End Visa-Free Entry for Indian Passports — Here's the Window Before the 15-Day Cap Hits",
        "subheadline": "A May 19 Cabinet decision moves Indian travelers to visa-on-arrival with a 15-day limit, but the old 60-day exemption stands until the Royal Gazette publishes — and no date is set.",
        "slug": make_slug("thailand-visa-free-india-passport-15-day-cap-voa"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs traveling on Indian passports — including green card holders and recent immigrants — face a rollback from 60-day visa-free to a 15-day visa-on-arrival cap that won't cover a typical Phuket wedding week; US passport holders are unaffected.",
        "tags": ["travel", "thailand", "visa", "india", "voa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Lexology", "url": "https://www.lexology.com/"},
            {"name": "TAT Newsroom (Tourism Authority of Thailand)", "url": "https://www.tatnews.org/"},
            {"name": "Royal Thai Embassy, New Delhi", "url": "https://newdelhi.thaiembassy.org/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Templo_Wat_Arun%2C_Bangkok%2C_Tailandia%2C_2013-08-22%2C_DD_30.jpg/1280px-Templo_Wat_Arun%2C_Bangkok%2C_Tailandia%2C_2013-08-22%2C_DD_30.jpg",
        "image_caption": "Wat Arun on the Chao Phraya River in Bangkok, a fixture of the Thailand trips Indian travelers may soon need a visa to extend",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": thailand_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "British Airways Just Made It Easier to Fly Home to India From St. Louis, Dallas, and Miami",
        "subheadline": "New and expanded US routes feed straight into a Heathrow-India network of 56 weekly flights to five cities — turning a three-leg ordeal into a single connection for the mid-city diaspora.",
        "slug": make_slug("british-airways-india-us-heathrow-st-louis-dallas-miami-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indians in underserved US cities like St. Louis, Dallas, and Miami gain a clean one-stop path home through Heathrow, with twice-daily Bengaluru service tailored to the South Indian tech corridor.",
        "tags": ["travel", "airlines", "british airways", "heathrow", "bengaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"},
            {"name": "Indian Eagle", "url": "https://www.indianeagle.com/"},
            {"name": "Simple Flying", "url": "https://simpleflying.com/"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Two_British_Airways_Boeing_787-9_on_stand_at_London_Heathrow.jpg/1280px-Two_British_Airways_Boeing_787-9_on_stand_at_London_Heathrow.jpg",
        "image_caption": "British Airways Boeing 787-9 Dreamliners on stand at London Heathrow, the hub bridging its expanded US network to India",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": ba_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Want to Watch the 2026 World Cup in Mexico? Indians on US Visas Can Skip the Mexican Visa — but Mind the Re-Entry Trap",
        "subheadline": "A valid US visa gets you into Mexico visa-free for the tournament, and automatic visa revalidation can bring H-1B holders back with an expired stamp — if the trip stays under 30 days.",
        "slug": make_slug("world-cup-2026-mexico-nri-us-visa-reentry-h1b-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indians on H-1B, F-1, and other US visas can attend World Cup matches in Mexico without a separate Mexican visa, but must understand automatic visa revalidation rules to re-enter the US without getting stranded.",
        "tags": ["travel", "world cup", "mexico", "h1b", "visa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "U.S. Embassy & Consulates in Mexico", "url": "https://mx.usembassy.gov/"},
            {"name": "Voye Global", "url": "https://www.voyeglobal.com/"},
            {"name": "USA.gov", "url": "https://www.usa.gov/"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Cancun_beach_aerial_-_Luftbild_%2818632395003%29.jpg/1280px-Cancun_beach_aerial_-_Luftbild_%2818632395003%29.jpg",
        "image_caption": "Aerial view of the Cancun coastline; Mexico's beaches and host cities draw diaspora fans for the 2026 World Cup",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": worldcup_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
