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

article1_body = """The cheapest part of a trip to the United States was never the flight. For most Indian travelers, it was the visa — a $185 visitor-visa fee that, however irritating the interview wait, at least had a fixed and knowable cost. That era is ending. A new $250 "visa integrity fee," written into the One Big Beautiful Bill Act that President Trump signed last July, is now working its way into the price of nearly every nonimmigrant visa the U.S. issues. For the Indian diaspora — the single largest source of U.S. student and H-1B visas — it is one of the most consequential cost changes in years.

## What the fee is, and who pays it

The charge is a flat minimum of $250, levied at the moment a visa is **issued** rather than when you apply. It applies across the board to nonimmigrant categories: B-1/B-2 visitor visas, F-1 student visas, and the employment-based H-1B, L-1, O-1 and TN classes. It is not a replacement for existing fees — it sits on top of them. An H-1B applicant already paying a $205 petition-linked fee should now budget for roughly $455 once the integrity fee is layered in, and a tourist visa that cost $185 effectively becomes $435.

Crucially for Indians, there is no escape hatch through the Visa Waiver Program. Citizens of most of Western Europe, Australia and Japan travel to the U.S. on the ESTA system and are exempt from the integrity fee entirely. Indian passport holders are not in the visa-waiver club; they need a stamped visa, which means they pay. The fee cannot be waived, cannot be reduced, and from 2026 onward will rise automatically each year with inflation.

## The refund that probably isn't

On paper, the fee is refundable. The law says a traveler can be reimbursed after their visa expires — provided they followed every rule: left on time, never overstayed by more than five days, never worked without authorization. In practice, immigration attorneys are warning clients to treat it as money gone. The Department of Homeland Security has not built a refund mechanism, has published no process, and the reimbursement only becomes available after a visa expires — which for a ten-year B-1/B-2 means waiting a decade to claim $250 back. Most travelers will never see it again.

## Why this lands hard on the diaspora

Do the math at the household level and the number stops looking small. A family of four flying from Delhi to visit relatives in New Jersey now faces an extra $1,000 in integrity fees alone, before airfare, before the existing consular charges, before the hiked I-94 fee that rose from $6 to $24 under the same bill. For the parents of an H-1B holder coming to meet a new grandchild, or for in-laws attending a wedding, the visa line item just got materially heavier.

Students feel it differently but just as sharply. An incoming F-1 from Hyderabad or Pune, already absorbing tuition, the SEVIS fee, airfare and a deposit, now adds another $250 to the pile at issuance. Multiply that across the tens of thousands of Indian students who make up the largest foreign cohort on American campuses, and the fee becomes a real factor in the calculus of whether the U.S. still offers the best return for the money — especially as Canada, the U.K. and Australia run their own fee increases.

## What to do before the cost climbs again

The practical advice from immigration practitioners is straightforward. First, if you have a pending application or an interview already scheduled, finish it — the fee bites at issuance, and earlier issuance locks in today's amount before the inflation escalator kicks in. Second, build the $250 per person into the trip budget from the start rather than treating it as a surprise at the counter; for group and family travel, that is the difference between a planned expense and a thousand-dollar shock. Third, do not bank on the refund. Keep the receipt, comply scrupulously with your visa terms — overstaying by more than five days voids any reimbursement claim anyway — but plan your finances as though the money is non-recoverable.

The broader signal matters too. The integrity fee is part of a coordinated tightening — Japan has raised its visa fee fivefold, the U.K. and Australia are lifting charges, and the U.S. is layering on costs while shrinking the interview-waiver "dropbox" that once spared renewal applicants a trip to the consulate. For the diaspora that shuttles between two countries for work, study and family, the price of keeping that bridge open is going up on both ends. The visa is no longer the cheap part of the trip.

**Sources:** Boundless Immigration; Manifest Law; TravelPulse; AFAR."""

article2_body = """Every NRI who has flown home in late June knows the feeling: the connecting flight to Mumbai or Delhi that pushes back from the gate an hour late, the holding pattern over the runway as a wall of rain moves through, the missed onward connection to Pune or Patna. The southwest monsoon has arrived across India this week, and with it comes the most operationally fragile stretch of the Indian flying calendar. For diaspora families traveling on the school-summer window, the next ten weeks demand a different kind of trip planning.

## The monsoon has crossed the country — and the disruption follows it

The India Meteorological Department reports the monsoon's northern limit has now pushed well inland, with heavy rain bands settling over Maharashtra, Telangana, Odisha, Bihar and Jharkhand and the system still advancing. That advance is not just a weather story; it is a flight-operations story. Heavy rain, low visibility, wind shear and convective storm cells near hub airports routinely force diversions, ground holds and last-minute reschedules. In May, a single thunderstorm system over the Delhi NCR forced more than 20 flights to divert away from Indira Gandhi International as crosswinds and lightning shut the safe-operating window; dust storms followed by heavy rain triggered multi-hour aviation red alerts. The transition months stack unstable pre-monsoon heat against the incoming rains, producing exactly the squalls that wreck a tight schedule.

Airlines are already adjusting. IndiGo has revised its monsoon timetable at several airports — reworking the days and frequencies of flights out of Ranchi's Birsa Munda Airport, among others — precisely because heavy rain makes fixed schedules unreliable. When a storm cell parks over a smaller airport with a single runway, the backlog spills into the national network and reaches routes the diaspora actually flies: the domestic legs from a metro gateway out to a hometown in Bihar, eastern UP or the Northeast.

## Why this hits NRI itineraries harder than domestic travelers'

A passenger flying Bengaluru to Kolkata can rebook the same evening. An NRI family flying San Francisco to Delhi to Patna cannot — the international leg is the expensive, inflexible anchor, and the domestic onward hop is the vulnerable link. A two-hour monsoon delay on the Delhi–Patna segment can blow a same-day connection that was the whole point of the routing, stranding a family overnight in a transit city with children and luggage. The asymmetry is the core problem: the diaspora itinerary is long, multi-leg and built around a fixed international ticket, so a small domestic disruption cascades into a large, costly one.

## How to monsoon-proof the trip home

The fixes are practical, and seasoned NRI travelers already use them. Build a long connection, not a tight one — if the domestic onward flight leaves four or five hours after the international arrival rather than ninety minutes, a monsoon delay becomes an inconvenience instead of a missed flight and a hotel bill. Where possible, book the international and domestic legs on a **single ticket** with one airline or alliance, so that a weather delay makes rebooking the airline's responsibility rather than yours; separate tickets leave you on your own when the first leg slips.

Favor morning departures for the domestic leg. Convective monsoon storms typically build through the afternoon and evening, so an early flight out of the metro hub is statistically more likely to depart on time than a late-afternoon one. Keep the airline's app installed and notifications on — IndiGo, Air India and others now push schedule changes by SMS and app before the airport boards update. And leave genuine buffer days on either end of any fixed event back home; a wedding or a parent's medical appointment is not the day to be testing the monsoon's patience with a same-day arrival.

## The flip side: it is still a good time to go

None of this means skipping the trip. The monsoon is also when airfares from the U.S. dip below the brutal summer peak, when India's hill stations and Kerala's backwaters are at their most spectacular, and when the crowds thin at heritage sites. The diaspora families who travel well in the rains are simply the ones who plan for the delay rather than denying it — long layovers, single tickets, morning flights, buffer days. Treat the monsoon as a known variable in the itinerary, not a surprise at the gate, and the trip home is as rewarding as ever. Just check the IMD bulletin before you book that connection.

**Sources:** India Meteorological Department / Travel And Tour World; The Daily Jagran (IndiGo Ranchi schedule); The Traveler."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The $250 'Visa Integrity Fee' Is Now Real — and Indian Travelers Can't Use the Exit Everyone Else Has",
        "subheadline": "A new charge on top of every U.S. visa is hitting the diaspora hardest, because India isn't in the visa-waiver club that skips it. The 'refund' is unlikely to ever arrive.",
        "slug": make_slug("us-250-visa-integrity-fee-indians-no-waiver-refund-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indians need a stamped visa for every U.S. trip, so unlike Western European or Japanese travelers on ESTA they cannot avoid the new $250 fee — and for a family of four it adds $1,000 per visit, with little real chance of the promised refund.",
        "tags": ["travel", "visa", "immigration", "usa", "nri", "students", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Boundless Immigration", "url": "https://www.boundless.com/blog/visa-integrity-fee/"},
            {"name": "Manifest Law — Visa Integrity Fee Explained", "url": "https://www.manifestlaw.com/blog/new-us-visa-integrity-fee-explained"},
            {"name": "TravelPulse", "url": "https://www.travelpulse.com/news/impacting-travel/us-announces-new-visa-integrity-fee-heres-how-much-it-will-cost"},
            {"name": "AFAR", "url": "https://www.afar.com/magazine/us-to-charge-visa-integrity-fee-for-foreign-visitors"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A U.S. passport with hundred-dollar bills, illustrating the rising cost of American visas",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Monsoon Has Crossed India — Here's How NRI Families Keep It From Wrecking the Trip Home",
        "subheadline": "Heavy rain is already forcing flight reschedules and diversions. The diaspora's long, multi-leg itineraries are the most exposed — and the most fixable.",
        "slug": make_slug("india-monsoon-flight-disruption-nri-connection-planning-summer"),
        "category": "travel",
        "vertical": "travel-advisory",
        "diaspora_angle": "An NRI flying San Francisco–Delhi–Patna can't easily rebook a missed monsoon connection the way a domestic traveler can, because the expensive international leg is fixed — so long layovers, single tickets and morning domestic flights are essential this season.",
        "tags": ["travel", "monsoon", "india", "flights", "nri", "advisory", "indigo"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — IMD Weekend Advisory", "url": "https://www.travelandtourworld.com/news/article/new-imd-india-travel-advisory-weekend-weather-updates-you-need-to-know/"},
            {"name": "The Daily Jagran — IndiGo Ranchi Monsoon Schedule", "url": "https://www.thedailyjagran.com/jharkhand/indigo-revises-ranchi-flight-timings-for-monsoon"},
            {"name": "The Traveler — Weather and Safety Jitters Hit India's Peak Summer Air Routes", "url": "https://thetraveler.org/"}
        ]),
        "score_total": 71,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12717154/pexels-photo-12717154.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Passengers check a departure board as flight schedules shift during disruption",
        "image_attribution": "Pexels",
        "body": article2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  word count [{art['slug']}]: {wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
