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

# ============================================================================
# ARTICLE 1 — JW Marriott Ranthambore / luxury wildlife
# ============================================================================
body1 = """When Marriott opened the JW Marriott Ranthambore Resort & Spa this week, it did two things at once. It gave Rajasthan its most polished tiger-country address yet, and it quietly handed Marriott its 10,000th hotel worldwide — a milestone the chain timed for the edge of a national park rather than a city skyline. For the Indian diaspora that flies home every winter, that choice says something about where the high end of Indian travel is headed.

## A luxury bet on the forest, not the fort

For decades, the diaspora's Rajasthan itinerary ran through palaces: Udaipur's lake hotels, Jaipur's heritage suites, Jodhpur's fort views. Ranthambore was a day's detour, a dawn jeep safari squeezed between Jaipur and Agra. The new JW Marriott reframes it as a destination in its own right — a full resort sitting a short drive from Ranthambore National Park, built around the park's biggest draw, its tigers.

The resort leans into what the industry now calls "wildlife luxury": large rooms, a destination spa, and naturalist-led safari logistics handled by the hotel rather than left to the traveller to cobble together. Marriott's Asia Pacific president Rajeev Menon and board chairman David Marriott both turned up for the opening, a level of attention that signals how seriously the group is treating India's conservation destinations as a growth lane rather than a novelty.

## Why the 10,000th-property label matters here

Hotel chains plant milestone flags deliberately. Marriott could have made any of its thousands of openings the symbolic 10,000th. It chose a tiger reserve in Rajasthan, months before its own centennial. The message to investors and to the market is that India's national parks — long under-served at the top end — are now considered prime real estate for global luxury brands.

For travellers, that competition is the real story. When a flagship brand commits to a wildlife destination, others follow, and the standard of lodges, guides, and access tends to rise across the board. Ranthambore already had respected boutique camps; a JW Marriott raises the ceiling and, eventually, the floor.

## What it means for NRIs

For Indian Americans planning the annual trip home, this lands at a useful moment. The classic problem with a Ranthambore add-on has been the gap between safari quality — excellent — and lodging that often felt like a compromise after a week in palace hotels. A JW Marriott closes that gap, which makes it far easier to sell a wildlife leg to family members, especially older parents or US-born kids, who want the safari without roughing it.

It also fits the multi-generational travel pattern that defines diaspora trips. A resort with a spa, reliable dining, and in-house safari coordination is the kind of base where grandparents can rest while the younger crowd does back-to-back game drives. Tiger sightings are never guaranteed in any park, but Ranthambore remains one of India's most reliable for them, and having a single property handle permits, zones, and jeep bookings removes the part of the trip that usually goes wrong.

The practical caveats are worth flagging. Ranthambore's safari season runs roughly October through June, with the park's core zones typically closed during the peak monsoon months — so this is a winter-holiday property, aligning neatly with the December–January window when most of the diaspora flies in. Park entry is tightly regulated by zone and vehicle quota, so even guests at a flagship hotel should let the resort book safaris well in advance rather than assume walk-up availability.

## The bigger shift

Marriott's milestone is one data point in a broader move: India's hospitality giants and global chains are both racing into leisure and wildlife destinations rather than just metro business hotels. The Oberoi group has wildlife retreats in its pipeline near Gir; Hilton, the Taj, and others are expanding aggressively across leisure markets. For a diaspora that has watched Indian travel infrastructure lag its ambitions for years, the upgrade at the top end is finally arriving in the places — like a Rajasthan tiger reserve — that were easiest to overlook.

The next time the family WhatsApp group debates whether to "do Ranthambore properly," the answer just got a lot simpler.
"""

# ============================================================================
# ARTICLE 2 — Spark by Hilton / budget travel India
# ============================================================================
body2 = """Hilton has brought its budget brand to India, opening the first two Spark by Hilton hotels in Bengaluru and Goa — and signing a deal to build 150 of them across the country. For the Indian diaspora, the headline isn't the brand launch. It's that a global chain is finally betting big on the unglamorous middle of Indian travel: the clean, reliable, reasonably priced room that an NRI family actually needs for a domestic hop.

## What Spark is — and isn't

Spark by Hilton, launched in 2023, is Hilton's entry-level brand: a no-frills, value-focused product aimed at "practical travellers" rather than the luxury or business set. The two Indian debuts are modest by design — an 82-room property in Bengaluru and a 64-room hotel in Goa's Calangute, the beach belt's busiest stretch.

The expansion runs through a partnership with Olive Hospitality to develop 150 Spark hotels across India. Globally the brand already has more than 240 operating hotels and roughly 230 more in the pipeline across the US, UK, and Canada. India is now squarely on that map.

## Why a budget brand is the interesting story

Most diaspora travel coverage chases the extremes: a new business-class suite on the nonstop to Delhi, or a palace hotel in Udaipur. But the trip that actually eats up an NRI's India itinerary is the domestic connection — Bengaluru to a relative's wedding, a few nights in Goa, a stopover near a parent's hometown. That middle tier has long been a gamble: independent hotels with inconsistent cleanliness, unreliable booking, and no recourse when a room doesn't match its photos.

A standardized global brand at the value end changes the calculus. The appeal of Spark isn't the amenities — there are few. It's the predictability: a known check-in process, consistent housekeeping standards, and a loyalty programme that travels. For diaspora visitors who book on trust from 8,000 miles away, that predictability is worth real money.

## The Hilton Honors angle NRIs will care about

Here's the part that matters for the frequent flyer set. Spark hotels participate in Hilton Honors, which means the points and status that diaspora travellers accumulate on US business travel can now be earned and burned on budget stays in India. An NRI who holds Hilton status from domestic American travel can, in theory, use that same account for a value room in Goa — and earn toward free nights along the way.

That's a meaningful perk that independent Indian budget hotels simply cannot match. For families making multiple domestic stops on a single India trip, the ability to consolidate spending into one rewards account, with predictable redemption, turns a string of forgettable nights into something that compounds.

## The locations are a tell

The choice of Bengaluru and Goa is not random. Bengaluru is a magnet for the tech diaspora — the city most likely to host returning NRIs visiting family, attending weddings, or scouting a move home. Goa is India's default leisure-beach destination and an increasingly popular spot for diaspora families who want a relaxed few days that doesn't require a long domestic flight.

Calangute, where the Goa property sits, is the commercial heart of North Goa's beach scene — walkable to the sand, surrounded by restaurants, and notoriously thin on dependable mid-priced lodging. A branded budget hotel there fills a genuine gap.

## What to watch

The 150-hotel target is ambitious, and the rollout will take years. Early properties will be the test: if Spark can hold its standards at Indian price points — the brand's whole promise — it could reshape the domestic-stay experience for exactly the kind of traveller the diaspora most often is. If it can't, it will blend into India's crowded budget field.

For now, the signal is clear. The global hotel industry has decided that India's value traveller is worth fighting for — and the NRI booking a few domestic nights on a winter trip home is squarely in that bracket.
"""

# ============================================================================
# ARTICLE 3 — Vietnam visa-free push for Indians
# ============================================================================
body3 = """Vietnam is weighing visa-free entry for Indian travellers, a move that would put it alongside Sri Lanka and Thailand in the Southeast Asian scramble for India's fast-growing outbound market. For the diaspora, it's another sign that the region is rewriting its rules specifically to court the Indian passport — and a reminder to read the fine print, because the policies are shifting month to month.

## What's on the table

Vietnam's tourism minister has pushed for short-term visa exemptions for key markets including India and China, raised at a conference chaired by the prime minister. Right now, Vietnam waives visas for nationals of around 25 countries — mostly Western European — and Indians still need either an e-visa or a narrow visa-free workaround. Folding India into the exemption list would be a major liberalization.

Vietnam has already been chipping away at the friction. It moved to an e-visa open to all nationalities valid for 90 days with multiple entries, and has cut processing time for that e-visa sharply — in some cases to under 24 hours. Full visa-waiver talks with India are, in the government's own words, "on the table."

## The catch diaspora travellers keep tripping over

Before booking on the strength of "visa-free Vietnam" headlines, NRIs should know the rules are not as loose as they sound. Vietnam's long-standing visa waiver for the resort island of Phu Quoc — a favourite shortcut for Indian beachgoers — was quietly narrowed this year. The waiver now applies only to travellers arriving on a direct international flight to Phu Quoc who do not continue to the mainland. Indians flying in via Ho Chi Minh City, Bangkok, or Kuala Lumpur — which is how most actually reached the island — no longer qualify and need an e-visa in advance.

That distinction matters because connecting itineraries are exactly how the diaspora tends to travel: a stop in a Gulf or Southeast Asian hub, then onward. The safe move for now remains the 90-day multiple-entry e-visa, which costs around US$25 and clears quickly, rather than gambling on a waiver with conditions buried in immigration circulars.

## Why Southeast Asia is competing this hard for Indians

The push isn't sentiment; it's math. India is projected to become one of the world's largest outbound travel markets within the decade, and the region's tourism economies are racing to capture the spend. Thailand and Malaysia have both extended visa-free entry for Indians through 2026. Sri Lanka restored free tourist entry. The Philippines opened a 14-day visa-free window. Each waiver is a bid for the same traveller.

Connectivity is following the policy. Weekly flights between India and Vietnam have climbed sharply, with carriers like IndiGo, Air India Express, VietJet, and Vietnam Airlines adding routes to Hanoi, Ho Chi Minh City, Da Nang, and Phu Quoc from a widening list of Indian cities. More seats plus easier visas is the combination that turns a destination from aspirational to bookable.

## What it means for NRIs

For Indian Americans, Vietnam slots neatly into the trip-home calculus. A growing number of diaspora travellers tack a Southeast Asian leg onto their India visit — a week of beaches or city food before or after the family obligations. Vietnam's pitch is strong: a favourable exchange rate, a deep food culture that resonates with Indian palates, and beaches at Da Nang, Nha Trang, and Phu Quoc that rival pricier regional rivals.

If the visa waiver lands, Vietnam becomes a near-frictionless add-on for the Indian-passport holders in a mixed-citizenship family — the relatives in India who would otherwise face the most paperwork. For US-citizen members of the family, Vietnam's e-visa is already straightforward, so a waiver for Indian passports would remove the last coordination headache of travelling together.

## The bottom line

Nothing is final yet — the exemption is a proposal, not law. But the direction is unmistakable: Southeast Asia is bending its entry rules toward the Indian traveller, and Vietnam doesn't want to be the last to do it. Until the waiver is signed, book the e-visa, fly direct if you want Phu Quoc on a waiver, and watch the announcements. In this region, the rules change fast — usually in the diaspora's favour.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Marriott Made Its 10,000th Hotel a Tiger Resort in Rajasthan — and Fixed the Weakest Link in the Diaspora's India Trip",
        "subheadline": "The new JW Marriott Ranthambore turns a dawn-safari detour into a destination, and signals that India's national parks are now prime luxury real estate.",
        "slug": make_slug("jw-marriott-ranthambore-tiger-luxury-wildlife-rajasthan-nri"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "NRI families who add a Ranthambore safari leg to their winter India trip finally get flagship-grade lodging to match the safari, closing the quality gap that made the wildlife detour a hard sell to parents and US-born kids.",
        "tags": ["travel", "india", "rajasthan", "wildlife", "hotels", "luxury"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/ranthambore-rajasthan-and-india-welcome-jw-marriott-ranthambore-resort-spa-as-marriott-opens-its-10000th-global-property/"},
            {"name": "IHCL / Marriott International", "url": "https://news.marriott.com/"},
            {"name": "Ranthambore National Park", "url": "https://en.wikipedia.org/wiki/Ranthambore_National_Park"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/080_Bengal_tiger_in_Ranthambore_National_Park_Photo_by_Giles_Laurent.jpg/1280px-080_Bengal_tiger_in_Ranthambore_National_Park_Photo_by_Giles_Laurent.jpg",
        "image_caption": "A Bengal tiger in Ranthambore National Park, Rajasthan, the draw behind the new JW Marriott resort",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Hilton's Budget Brand Just Landed in India — and It Solves the NRI's Most Annoying Travel Problem",
        "subheadline": "Spark by Hilton opens in Bengaluru and Goa with a 150-hotel plan, bringing a standardized, points-earning value room to the domestic stays diaspora trips actually depend on.",
        "slug": make_slug("spark-by-hilton-india-budget-hotels-bengaluru-goa-nri-honors"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "The unglamorous domestic-hop hotel is where NRI India trips usually go wrong; a global value brand with Hilton Honors lets diaspora travellers book India stays on trust and earn points from US travel toward free nights.",
        "tags": ["travel", "india", "hotels", "budget", "goa", "bengaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/spark-by-hilton-debuts-in-apac-opens-2-hotels-in-bengaluru-goa"},
            {"name": "Hilton (company statement)", "url": "https://newsroom.hilton.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28368719/pexels-photo-28368719.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A beach in Goa, where Hilton opened one of its first two Spark by Hilton hotels in India",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Vietnam Is Weighing Visa-Free Entry for Indians — but the Phu Quoc Loophole Just Got Smaller",
        "subheadline": "As Southeast Asia races to court India's outbound boom, Vietnam mulls joining Thailand and Sri Lanka — while quietly tightening the beach-island waiver diaspora travellers relied on.",
        "slug": make_slug("vietnam-visa-free-indians-phu-quoc-evisa-southeast-asia-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Vietnam is a fast-rising add-on leg for diaspora India trips; a visa waiver would remove the last paperwork headache for mixed-citizenship families, but the narrowed Phu Quoc rule means NRIs on connecting flights still need an e-visa.",
        "tags": ["travel", "visa", "vietnam", "southeast-asia", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Vietcetera", "url": "https://vietcetera.com/en/vietnam-considers-visa-free-entry-for-indians-following-sri-lanka-thailand"},
            {"name": "Seasia.co", "url": "https://seasia.co/2026/06/18/viet-nam-contemplates-visa-free-entry-for-indian-travelers-following-thailand-and-sri-lanka"},
            {"name": "VisaHQ", "url": "https://www.visahq.com/india/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/View_of_sea_from_Titov_Island%2C_Ha_Long_Bay%2C_Vietnam%2C_20240128_1337_3732.jpg/1280px-View_of_sea_from_Titov_Island%2C_Ha_Long_Bay%2C_Vietnam%2C_20240128_1337_3732.jpg",
        "image_caption": "The view from Titov Island in Ha Long Bay, Vietnam, a top draw for Indian travellers",
        "image_attribution": "Wikimedia Commons",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   [{art['slug']}] words={wc} headline_len={len(art['headline'])}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
