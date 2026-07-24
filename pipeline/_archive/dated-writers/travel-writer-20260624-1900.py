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

JAPAN_BODY = """Japan is about to make a trip to Kyoto noticeably more expensive at the consulate window — and which passport you hand over decides whether you feel it at all.

From **July 1, 2026**, Japan will raise its visa fees for the first time since 1978, a near-five-decade freeze that the government is ending in one stroke. A single-entry tourist visa jumps from ¥3,000 to **¥15,000** (about ₹8,750, or roughly $93). A multiple-entry visa climbs from ¥6,000 to **¥30,000** (around ₹17,580, or about $186). Foreign Minister Toshimitsu Motegi framed the increase as an overdue correction for "inflation and exchange rate fluctuations," and Tokyo insists it does not expect the higher charges to dent a tourism boom that drew a record 42.7 million visitors in 2025.

## Why The Indian Passport Feels The Full Weight

Here is the detail that matters for the diaspora: the fee increase lands hardest on travelers from countries that require a visa to enter Japan — and India is one of them. Indian passport holders cannot enter Japan visa-free, which means every Indian citizen planning a Kyoto autumn or a Hokkaido ski week now pays the full, fivefold rate. A family of four applying for single-entry visas will spend roughly ₹35,000 on visa fees alone before a single flight or hotel is booked.

The split runs straight through Indian-American households. A naturalized US citizen of Indian origin travels to Japan visa-free under the US passport's waiver and pays **nothing** — the fee hike is invisible to them. Their green-card-holding spouse or visiting parents on an Indian passport, by contrast, must apply for a visa and now pay the new rate. The same trip, the same family, two very different cost structures depending on the booklet in each person's pocket.

## The Multiple-Entry Math Changes

For NRIs who treat Japan as a recurring destination — and a growing number do, pairing business in Tokyo with leisure in the Kansai region — the multiple-entry visa is the line item that stings. At ¥30,000 it is now five times its old cost, but it remains the smarter buy for anyone visiting twice or more within its validity. A single multiple-entry visa still costs less than two single-entry applications under the new structure, so frequent flyers should price the multiple-entry option deliberately rather than defaulting to single-entry out of habit.

There is also a timing play. The new fees apply only to applications **submitted on or after July 1**. Anyone with firm Japan plans for the second half of 2026 should weigh filing before the deadline to lock in the old ¥3,000 rate — though visa validity windows mean this only helps travelers with trips reasonably close at hand.

## What Else Is Moving

The visa fee is not the only cost creeping up. Japan is also raising fees for permanent-residency applications and has been tightening enforcement against overstayers, with revenue from the increases earmarked for processing efficiency and expanded Japanese-language programs. Separately, several Japanese destinations have introduced or tripled local tourist taxes, a parallel squeeze that shows up at hotels rather than consulates.

For the diaspora, the practical takeaways are concrete. Indian-passport travelers should budget the new fee into trip costs now and avoid the assumption that a long-planned Japan trip will cost what it did even a year ago. Mixed-passport families should map out who needs a visa and who does not before booking, because the consular paperwork — and its price — is no longer uniform across the household. And anyone weighing repeat visits should run the multiple-entry numbers rather than paying single-entry rates twice.

Japan remains one of the most rewarding destinations in Asia for the Indian traveler, and a one-time fee, however sharp the jump, is unlikely to keep determined visitors away. But the era of the trivially cheap Japanese visa is over, and for the millions of Indian passport holders who cannot simply wave a waiver at immigration, the cost of the dream trip just went up by a factor of five."""

CANADA_BODY = """For two years the message reaching Indian families has been that Canada slammed its doors on international students. Canada's top diplomat in Delhi spent this week arguing the opposite — that it may now be the best moment in living memory to apply.

Speaking to ANI, Canadian High Commissioner to India **Chris Cooter** said the widespread perception that Canada has turned unwelcoming is "a misperception," and that the country is "not at all" shutting its doors. "This is probably the best time ever to apply as an Indian student," Cooter said, "because we want you there and there's space in these caps." Canada, he noted, currently hosts around 400,000 international students — "more than the EU, UK and Australia combined. It's more than the US hosts."

## Why The Diaspora Should Care

Indian students are, by a wide margin, the largest single nationality in Canada's international classroom, and the Canadian education pathway has long doubled as a family migration strategy for the diaspora — a three-year Post-Graduation Work Permit and a relatively clear route to permanent residency. When the narrative soured, applications from India cooled, and families that had banked on a Canadian degree for a son or daughter started looking elsewhere. Cooter's pitch is aimed squarely at reversing that chill.

His central claim is that intake remains **below** the cap. Canada set a study-permit ceiling of 408,000 for 2026, down from 437,000 in 2025, of which only about 155,000 are reserved for first-time international students. Cooter's argument is that the doom narrative scared off enough applicants that the cap is not even being filled — which, if true, means a well-prepared Indian application faces less competition than the headlines suggest.

## The Improvements That Back The Pitch

The diplomacy is paired with measurable processing gains. Study-permit processing times for Indian applicants fell to roughly three weeks earlier this year, a dramatic improvement that puts students targeting a September 2026 intake squarely in the optimal application window. Cooter tied the cleanup directly to Prime Minister Mark Carney's visit to India earlier this year, saying Ottawa is "actively at work" on fixing complaints about inconsistent and slow visa decisions. "I'd like to see us be best in class," he said.

There is also a structural sweetener that took effect this year: from January 1, 2026, **master's and PhD students at public institutions are exempt** from both the study-permit cap and the Provincial Attestation Letter (PAL) requirement. For Indian graduate applicants — a large and growing slice of the pipeline — that removes one of the most frustrating bottlenecks entirely.

## Read The Fine Print

Cooter's optimism comes with caveats the diaspora should not gloss over. Proof-of-funds requirements rose to **CA$22,895** (in addition to first-year tuition) from September 2025, raising the financial bar for families. Work-permit processing for Indian applicants has moved the wrong way — up to about eight weeks — even as study-permit times improved. The Student Direct Stream that once fast-tracked Indian applications has closed. And spousal open work permits are now restricted largely to partners of master's, PhD and certain professional-degree students, while dependent children are no longer eligible — a meaningful change for families planning to move together.

The PGWP rules also reward planning: master's graduates can now secure a three-year work permit even for programs under two years, provided the program ran at least eight months at a designated institution, but students at private colleges licensing public curriculum remain shut out of PGWP eligibility. Choosing the wrong institution can quietly cost a graduate the very work permit that justified the move.

The practical message for Indian families weighing a 2026 application is straightforward. The window is genuinely open, processing is faster than it has been in years, and the cap is not full — but the financial thresholds are higher, the institution you pick determines your work rights, and family-accompaniment rules have tightened. Cooter is right that the door is open. Walking through it cleanly still demands the kind of complete, early, well-documented application that has always separated approvals from refusals."""

VIZAG_BODY = """Andhra Pradesh's coast is about to get its first greenfield international gateway, and for the Telugu diaspora it means the long detour through Hyderabad or Chennai may finally be optional.

**Alluri Sitarama Raju International Airport** at Bhogapuram — widely known simply as Bhogapuram Airport — is scheduled to open in early July 2026, with Wikipedia and multiple Indian outlets citing an **8 July** commercial start. Built by the GMR Group at a first-phase cost of around ₹4,600 crore, the airport sits about 40 kilometers from Visakhapatnam off National Highway 16, and is designed to handle six million passengers a year initially, with land banked for expansion through 2030. Two 3.8-kilometer runways are already complete, and a validation flight carrying the civil aviation minister has confirmed the field is ready for operations.

## Why It Matters To The Telugu Diaspora

Visakhapatnam — Vizag — anchors a coastal Andhra region that has sent large numbers of professionals, students and IT workers to the United States, the UK and the Gulf. For decades, those families have flown home the hard way: an international leg into Hyderabad, Chennai or Bengaluru, followed by a domestic hop or a long road journey to the coast. The existing Visakhapatnam airport, a naval enclave with constrained civilian operations and limited international reach, never closed that gap.

A purpose-built international airport on the doorstep changes the calculus. Once international carriers begin operations from Bhogapuram, NRIs from coastal Andhra gain the prospect of one-stop connections home through Gulf hubs — the same Dubai, Abu Dhabi and Doha gateways that already knit the rest of India to the diaspora — without the final domestic scramble. For a Telugu family in New Jersey or the Bay Area visiting parents in Vizag or Vizianagaram, that can mean hours shaved off every trip and one fewer missed-connection risk during monsoon season.

## What's Actually Opening, And When

A note of precision matters here, because airport launches in India have a habit of slipping. Bhogapuram has been described variously as a June and a July opening as deadlines moved; the most recent and specific marker is an 8 July commercial commencement, with full international scaling expected to follow as airlines file routes. Early operations typically begin with domestic and select international services before the network thickens, so diaspora travelers should expect the menu of nonstop and one-stop options to grow over the months after launch rather than arrive complete on day one.

The airport is being built as more than a passenger terminal. GMR has outlined an "Aerotropolis" with an integrated aerospace zone across 500 acres, an MRO (maintenance, repair and overhaul) hub and a dedicated cargo terminal — the kind of ecosystem that, in Hyderabad, turned an airport into an economic anchor. For the region, that promises jobs and investment; for the diaspora, it signals that Bhogapuram is intended as durable infrastructure, not a ribbon-cutting showpiece.

## The Ground Game Still Lags

The honest caveat for anyone planning to use it soon is road access. Bhogapuram is roughly 60 kilometers from central Visakhapatnam, and the connecting-road network is still under construction — an elevated expressway from Anandapuram is in detailed-planning stages, and the state has identified some 15 internal roads for widening to decongest the route. Until those corridors are finished, the time saved in the air could be partly eaten on the ground between the terminal and the city. Travelers should budget generously for the airport transfer in the first phase.

For the Telugu-American and Gulf-Telugu communities, Bhogapuram is the infrastructure story they have waited on for years: a real international gateway to their home region, opening this summer, with a Gulf-connectivity future that mirrors how the rest of India already flies home. The connections will not all materialize on opening day, and the drive into Vizag remains a work in progress. But the structural barrier — no international airport on coastal Andhra — is finally coming down."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Japan Just Made Its Tourist Visa Five Times Costlier — and the Indian Passport Pays Full Price While the US One Pays Nothing",
        "subheadline": "From July 1, Japan's first visa fee hike since 1978 quintuples the cost for Indian citizens, splitting the bill right down the middle of mixed-passport diaspora families.",
        "slug": make_slug("japan-visa-fee-5x-hike-july-2026-indian-passport-us-citizen-split-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian passport holders must hold a visa to enter Japan and now pay the full fivefold fee, while Indian-American US citizens travel visa-free — splitting the cost within the same diaspora family.",
        "tags": ["travel", "visa", "japan", "nri", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"},
            {"name": "Inshorts", "url": "https://www.inshorts.com/"},
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/20181110_Fushimi_Inari_Torii_12.jpg/1280px-20181110_Fushimi_Inari_Torii_12.jpg",
        "image_caption": "The torii gates of Fushimi Inari Taisha shrine in Kyoto, a top draw for Indian visitors to Japan",
        "image_attribution": "Wikimedia Commons",
        "body": JAPAN_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Canada's Envoy Says It's the 'Best Time Ever' for Indian Students — Here's What He Left Out",
        "subheadline": "High Commissioner Chris Cooter insists the doors are open and the cap isn't full, but the higher funds bar, slower work permits and tighter family rules still decide who gets in cleanly.",
        "slug": make_slug("canada-best-time-ever-indian-students-study-permit-cooter-cap-fine-print-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are Canada's largest international cohort and the study route doubles as a family migration path for the diaspora; the envoy's pitch and its caveats directly shape 2026 application decisions.",
        "tags": ["travel", "visa", "canada", "students", "immigration", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Devdiscourse / ANI", "url": "https://www.devdiscourse.com/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Immigration News Canada", "url": "https://immigrationnewscanada.ca/"},
            {"name": "Collegedunia", "url": "https://collegedunia.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/University_of_Toronto_Scarborough_Campus.jpg/1280px-University_of_Toronto_Scarborough_Campus.jpg",
        "image_caption": "The University of Toronto Scarborough campus, one of Canada's destinations for Indian international students",
        "image_attribution": "Wikimedia Commons",
        "body": CANADA_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Coastal Andhra Finally Gets Its Own International Airport — Bhogapuram Opens This July",
        "subheadline": "The new Alluri Sitarama Raju International Airport near Visakhapatnam promises the Telugu diaspora a route home that skips the Hyderabad and Chennai detour — once the roads catch up.",
        "slug": make_slug("bhogapuram-alluri-sitarama-raju-airport-vizag-opening-july-2026-telugu-diaspora-nri"),
        "category": "travel",
        "vertical": "infrastructure",
        "diaspora_angle": "The Telugu diaspora from coastal Andhra has long flown home via Hyderabad or Chennai; a new international airport near Visakhapatnam opens the prospect of one-stop Gulf connections straight to their home region.",
        "tags": ["travel", "airports", "india", "andhra-pradesh", "infrastructure", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia — Alluri Sitarama Raju International Airport", "url": "https://en.wikipedia.org/wiki/Alluri_Sitarama_Raju_International_Airport"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Swarajya", "url": "https://swarajyamag.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Visakhapatnam_beach_road_near_Kailasagiri.jpg/1280px-Visakhapatnam_beach_road_near_Kailasagiri.jpg",
        "image_caption": "The beach road near Kailasagiri in Visakhapatnam, the metropolitan region the new Bhogapuram airport will serve",
        "image_attribution": "Wikimedia Commons",
        "body": VIZAG_BODY
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  {art['slug']}  ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
