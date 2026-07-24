#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-25 11:00 PDT batch"""
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
    # ── Article 1: Ebola travel advisory ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Ebola Is Back — and It's Already Changing How NRIs Fly Through Africa and the Middle East",
        "subheadline": "India has banned non-essential travel to three African nations. The US is screening at airports. For NRIs with Ethiopian Airlines connections or Africa-bound plans, here's what just shifted.",
        "slug": make_slug("ebola-bundibugyo-nri-travel-advisory-africa-flights"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who route through Addis Ababa on Ethiopian Airlines — one of the cheapest India-US corridors — now face enhanced CDC screening and potential 21-day monitoring. Those with business ties to East Africa or family in the Gulf need to know the new entry rules.",
        "tags": ["travel", "ebola", "health advisory", "africa", "airports", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/zai7jjehe04d/"},
            {"name": "India Ministry of Health", "url": "https://mohfw.gov.in"},
            {"name": "CDC Enhanced Screening", "url": "https://www.usatoday.com/story/travel/airline-news/2026/05/23/cdc-ebola-screening-atlanta-airport/84476744007/"},
            {"name": "CurlyTales India Advisory", "url": "https://curlytales.com"},
            {"name": "VisaHQ India Advisory", "url": "https://www.visahq.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4021190/pexels-photo-4021190.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The Bundibugyo strain of Ebola — rarer and more unpredictable than the Zaire variant most people remember — has been tearing through the Democratic Republic of the Congo since mid-May, with cases confirmed in Uganda and risk spreading to South Sudan. On May 17, the World Health Organization declared a Public Health Emergency of International Concern. Within a week, a cascade of border restrictions followed.

For NRIs, this isn't abstract. It's operational.

## What India Has Done

India's Directorate General of Health Services issued a formal travel advisory on May 24, urging citizens to avoid all non-essential travel to the DRC, Uganda, and South Sudan. At airports, passengers arriving from these countries now face mandatory self-declaration forms, thermal screening, and symptom assessments. Anyone showing signs of fever, vomiting, or severe fatigue gets pulled aside for evaluation by designated health officers.

The advisory also requires a 21-day self-monitoring period after arrival — the maximum incubation window for Ebola. Hospitals across India have updated isolation protocols and stockpiled protective equipment, though no domestic cases have been reported.

For OCI holders and Indian passport carriers planning trips to East Africa — whether for safari holidays, business, or religious travel — the message is unambiguous: postpone unless essential.

## The US Side: Screening Expands

The CDC began enhanced entry screening at Washington-Dulles on May 20, adding Atlanta's Hartsfield-Jackson on May 23. Travelers who've been in the DRC, Uganda, or South Sudan within the prior 21 days face health questionnaires, temperature checks, and mandatory contact-information collection. Non-US passport holders from these countries face temporary entry suspension.

In one striking incident, a flight was diverted from Detroit to Montreal after it was discovered a passenger who should have been barred from boarding had been allowed on.

NRIs who route through Addis Ababa on Ethiopian Airlines — long one of the cheapest India-US corridors — should pay attention. While Ethiopia itself isn't on the restricted list, connecting through East African hubs now carries the risk of secondary screening delays and heightened scrutiny if your itinerary touches the affected region.

## Why the Bundibugyo Strain Matters More

Unlike the Zaire strain that dominated the 2014 West Africa outbreak, there are no approved vaccines or targeted antivirals for the Bundibugyo variant. That makes containment through border controls and early detection the only real defense. Uganda has already reported over 860 suspected cases and more than 200 deaths.

For NRIs, the practical calculus is straightforward: avoid East Africa for now, verify your airline routing doesn't include surprise layovers in affected zones, and if you've recently traveled through the region, be honest on screening forms and monitor your health. The 21-day window is long enough to overlap with your entire return-and-settle-back-in period.

## What to Watch

The WHO assessment is evolving weekly. If cases reach Kenya or Tanzania — both of which have significant Indian diaspora business communities — the travel calculus changes dramatically. The Gulf states of Bahrain and Jordan have already imposed entry bans for recent travelers from affected countries, which could complicate India-to-US routing through the Middle East.

Keep an eye on your airline's booking policies. Several carriers are now offering free rebooking for Africa-bound tickets. If you have trips planned, check before you pack."""
    },

    # ── Article 2: America First visa scheduling tool ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Rubio's 'America First' Visa Tool Could Fast-Track Indian Business Travelers — If They Qualify",
        "subheadline": "During his first India visit as Secretary of State, Marco Rubio unveiled a priority-based visa scheduling system. For the thousands of Indian executives and investors flying to the US monthly, the stakes are real.",
        "slug": make_slug("rubio-america-first-visa-scheduling-india-business-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian professionals and NRI business owners who regularly need US visa appointments — for partners, parents, employees, or clients — could see faster scheduling. But the tool rewards documentation of US economic benefit, not family ties.",
        "tags": ["travel", "visa", "india-us relations", "business travel", "marco rubio"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NRI Page", "url": "https://www.nripage.com/articles/visa-immigration/2026/05/23/america-first-visa-tool-may-speed-up-us-visa-scheduling-for-india-us-business-travel"},
            {"name": "Inshorts", "url": "https://inshorts.com"},
            {"name": "Fox News", "url": "https://www.foxnews.com"},
            {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3885601/pexels-photo-3885601.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """US Secretary of State Marco Rubio, on his first official visit to India, dropped a policy announcement on May 23 that caught the Indian business community's attention: a new "America First" visa scheduling tool designed to prioritize travelers whose trips strengthen US commercial and strategic interests.

The timing was deliberate. It came exactly one day after USCIS announced that most temporary-status holders would need to return to their home countries for green card processing — a rule that sent shockwaves through the Indian H-1B community. Rubio's visa tool appeared calibrated to soften the blow, signaling that while immigration pathways are tightening, the door for business travel is being propped wider open.

## How the Tool Works

The system is built around a priority principle: applicants whose travel demonstrably supports US business, investment, trade, or strategic cooperation get earlier access to consular appointment scheduling. Think of it as a triage system for the US visa appointment queue, which in cities like Mumbai, Hyderabad, and Chennai can mean weeks or months of waiting.

For Indian company executives visiting US headquarters, investors scouting acquisitions, founders attending board meetings, or trade delegates participating in bilateral discussions, faster appointment access could shave weeks off planning timelines. Delayed visa appointments have long been a silent tax on India-US business — deals stall, partnerships slow, expansion plans get pushed back a quarter.

## Who Benefits — and Who Doesn't

The biggest advantage goes to applicants who can clearly document that their travel creates economic value for the United States. That means meeting invitations from US companies, investment term sheets, conference registrations, partnership agreements, or letters from American counterparties.

What it doesn't do is help the average tourist, family visitor, or wedding guest. If your mother-in-law needs a B-2 visitor visa to attend a graduation in Dallas, the America First tool probably won't move her up the queue. The system's logic is economic, not humanitarian.

For NRI business owners who employ people in both countries, though, the implications are meaningful. If you're bringing Indian employees to the US for training, onboarding clients, or closing deals, the documentation requirements should be straightforward — and the scheduling relief could be significant.

## The Broader Context

Rubio's announcement came during a four-day India visit focused on deepening the bilateral relationship. The timing was strategic: India-US trade has been expanding, and the business travel corridor between the two countries is one of the busiest in the world. By signaling that legitimate business travel will get smoother processing, the administration is trying to thread the needle between immigration restriction and commercial openness.

But Indian applicants should be clear-eyed about what this is and isn't. It's a scheduling prioritization tool, not a new visa category. The underlying consular process, documentation requirements, and approval standards remain unchanged. You still need to qualify for a visa on the merits. You just might get your appointment sooner.

## What Indian Travelers Should Do

If you're planning business travel to the US in the coming months, start assembling your documentation now. The more clearly you can demonstrate that your trip benefits US commercial interests, the better positioned you'll be under the new scheduling logic. Keep meeting invitations, company letters, investment details, and conference registrations organized and ready to present.

For those already in the NRI ecosystem — with US companies, American clients, or cross-border operations — this is a small but meaningful quality-of-life improvement in what has been an increasingly uncertain immigration landscape."""
    },

    # ── Article 3: US tourism decline and NRI family visits ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Four Million Fewer Tourists Came to America Last Year — and NRI Family Visits Are Getting Caught in the Downdraft",
        "subheadline": "The US just posted its worst tourism decline since the pandemic. Indian visitor numbers are down over 4%. For NRIs waiting to host parents and in-laws, the obstacles are stacking up.",
        "slug": make_slug("us-tourism-decline-india-visitors-nri-family"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs who host parents, in-laws, and relatives visiting from India, the converging pressures — restricted Middle East airspace, a proposed $250 visa fee, Brand USA defunding, and India visitor numbers declining 4%+ — are making what was already an expensive trip even more daunting.",
        "tags": ["travel", "us tourism", "india", "family visits", "visa fees", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/05/25/travel/analysis-tourism-fewer-international-visitors-2025-vis"},
            {"name": "World Travel and Tourism Council", "url": "https://wttc.org"},
            {"name": "Tourism Economics", "url": "https://www.tourismeconomics.com"},
            {"name": "Brand USA", "url": "https://www.thebrandusa.com"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4064147/pexels-photo-4064147.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The numbers are in, and they're ugly. Four million fewer international visitors came to the United States in 2025 compared to 2024. Total foreign visitor spending dropped by $8.4 billion. It's the worst single-year decline in two decades, pandemic excluded — and unlike COVID, this one was largely self-inflicted.

For NRIs, the headline number is bad enough. But the India-specific data is worse: visitor numbers from India are projected to dip more than 4% in 2026, according to estimates cited in CNN's analysis. That's parents who didn't make the trip, in-laws who postponed, cousins who decided the hassle wasn't worth it.

## What's Driving the Decline

Three forces are compounding at once, and all three hit the India-US travel corridor particularly hard.

**Restricted airspace over the Middle East.** The war in Iran has forced airlines to reroute flights that previously transited Gulf airspace. For India-US routes — many of which connect through Dubai, Abu Dhabi, or Doha — this means longer flight times, higher fuel costs, and more expensive tickets. The rerouting isn't temporary; as long as the conflict continues, the most efficient air corridors between South Asia and North America are compromised.

**A proposed $250 visa integrity fee.** The Trump administration has floated a new fee on top of existing visa application costs for certain visitor categories. While not yet implemented, the mere proposal has created confusion and hesitation among Indian families planning visits. When you're already paying $185 for a B-2 visa application with no guarantee of approval, the prospect of an additional $250 feels punitive — especially for elderly parents on fixed incomes.

**The defunding of Brand USA.** The only organization that marketed US tourism to international audiences has had its funding pulled. Bills to restore it have stalled in Congress. The practical effect: while other countries aggressively court Indian travelers — Dubai, Singapore, Thailand, and Japan all run sophisticated India-targeted campaigns — the US has gone quiet. Brand USA recently launched a "build traveler confidence" campaign to counter misinformation, but the damage to perception is already baked in.

## The NRI Family Visit Problem

Every Indian American knows the ritual: months of planning, visa appointment anxiety, expensive tickets, jet-lagged parents adjusting to a house where the spices are in the wrong cabinet. It was always logistically demanding. Now it's becoming financially prohibitive.

A round-trip Delhi-to-San Francisco ticket that cost $900 two years ago now regularly clears $1,300 in peak season. Add visa fees, travel insurance (which elderly Indian visitors increasingly need), and the general cost of hosting — and a three-month parental visit can easily run $5,000-$6,000 before the first restaurant bill.

The decline in Indian visitors isn't just a tourism statistic. It's grandparents who didn't see their grandchildren this year. It's family events — weddings, graduations, baby showers — where the India contingent was smaller than expected. For a diaspora community that maintains unusually strong transnational family ties, fewer visits means weaker connections.

## What Other Countries Are Doing

The contrast is instructive. While the US makes visiting harder and more expensive, competitors are doing the opposite. Japan streamlined its Indian visa process in early 2026. Singapore extended its visa-free transit allowance. Dubai continues to offer visa-on-arrival to Indian passport holders. Even the UK, hardly known for welcoming immigration policy, has simplified its electronic visa system.

The World Travel and Tourism Council put it bluntly: 80 million more people traveled internationally in 2025 compared to the year before. They just chose to go elsewhere.

## What NRIs Can Do

If you're planning to host family from India this year, book flights early — summer fares are already elevated. Consider alternate routing through European hubs (Lufthansa via Frankfurt, KLM via Amsterdam) where airspace restrictions have less impact. For visa applications, ensure your invitation letter clearly documents the purpose and duration of the visit; consular officers are reportedly applying greater scrutiny to B-2 applications.

And if your parents are on the fence about making the trip? The honest answer might be that this year, it makes more sense for you to go to them."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
