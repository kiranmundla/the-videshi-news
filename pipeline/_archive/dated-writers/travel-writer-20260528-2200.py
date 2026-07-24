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
        "headline": "Your Airport Could Be Next — DHS Threatens to Kill International Flights at Every Major NRI Gateway",
        "subheadline": "Homeland Security Secretary Markwayne Mullin is drawing up plans to pull customs officers from sanctuary city airports — a list that includes Newark, SFO, LAX, O'Hare, and nearly every hub NRIs depend on to fly home.",
        "slug": make_slug("dhs-sanctuary-city-airports-nri-flights-threat"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Every major NRI travel corridor — SFO-DEL, JFK-BOM, EWR-BLR, ORD-HYD, LAX-BLR — runs through airports on the sanctuary city list. If customs processing stops, NRIs cannot clear immigration on arrival, effectively stranding international flights.",
        "tags": ["travel", "airlines", "immigration", "sanctuary-city", "newark", "airports"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/us-agency-could-soon-stop-processing-international-flights-newark-dhs-secretary-2026-05-28/"},
            {"name": "New York Post", "url": "https://nypost.com/2026/05/27/us-news/dhs-head-markwayne-mullin-doubles-down-on-plan-to-cut-customs-processing-from-sanctuary-city-airports/"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/travel/airline-news/2026/05/27/mullin-sanctuary-city-airports/"},
            {"name": "North Jersey", "url": "https://www.northjersey.com/story/travel/2026/05/28/newark-airport-international-flights/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/13404727/pexels-photo-13404727.jpeg",
        "image_caption": "Passengers queuing at an airport gate — a scene that could vanish at sanctuary city airports if DHS follows through on its threat.",
        "body": """On Thursday, Homeland Security Secretary Markwayne Mullin went on Fox News and said the quiet part loud: if sanctuary cities don't cooperate with federal immigration enforcement, his department will stop processing international flights at their airports.

"If things don't change, we're going to have to make this step pretty quick," Mullin told *Fox & Friends*, singling out Newark Liberty International — a United Airlines hub that processed 15 million international passengers last year alone.

## The List That Should Worry Every NRI

The Justice Department's sanctuary city list reads like a directory of Indian American life. Newark. New York. San Francisco. Los Angeles. Chicago. Seattle. Denver. Philadelphia. Boston.

Strip customs and immigration processing from these airports and the consequences are not hypothetical — they are arithmetic. Roughly 80% of all nonstop flights between the United States and India originate from airports on that list. Air India's flagship routes, United's trans-Pacific network, Emirates and Qatar connections through JFK and SFO — all would face an operational wall.

An NRI family flying home to Hyderabad through Chicago O'Hare would land to find no one authorized to stamp them in. A tech worker returning to San Francisco from Bangalore would be, in legal terms, unable to enter the country at their destination.

## Why This Is Happening Now

The immediate trigger is a standoff over Delaney Hall, a 1,000-bed immigration detention center in Newark. Anti-ICE protesters have blockaded the facility for days, and Mullin claims local law enforcement is preventing federal agents from entering and exiting. His proposed remedy — pulling customs officers from the airport — is a pressure tactic aimed at New Jersey's political establishment.

But the threat has metastasized far beyond Newark. On Tuesday, Mullin told Sean Hannity that DHS is "drawing up plans" to extend the policy to all sanctuary jurisdictions. The timing is not subtle: the FIFA World Cup kicks off June 11, and the final will be played at MetLife Stadium in East Rutherford — twelve miles from Newark airport. More than a million international visitors are expected.

## The Opposition Is Bipartisan

Even within the Trump administration, the plan has critics. Transportation Secretary Sean Duffy pushed back publicly: "We shouldn't shut down air travel in a state that doesn't agree with our politics." Airlines for America and the U.S. Travel Association have both condemned the proposal. The industry group estimates that halting international travel at major airports would cost the American economy billions in tourism revenue.

Mullin, for his part, is unbothered. "They're barricading our employees from coming in and out of the facility," he said. "Then why are we processing international flights into the airport there?"

## What NRIs Should Do Right Now

The threat has not been executed. No customs officers have been reassigned, and international flights continue to operate normally at all listed airports. But the political dynamics are volatile, and the window between threat and action has historically been short in this administration.

**Monitor before you book.** If you're planning a summer trip to India or expecting family from abroad, keep flexible tickets. Direct routes on Air India or United through non-sanctuary cities — Dallas, Houston, Washington Dulles — remain unaffected.

**Have a Plan B airport.** Charlotte, Atlanta, Miami, and Houston Intercontinental are not on the sanctuary city list and offer connections to India via European and Gulf hubs.

**Check your visa status.** The threat is about customs processing, not visa validity. Your visa remains valid, but if customs officers are pulled from your arrival airport, you simply cannot be processed there — you would need to reroute to a functioning port of entry.

**Watch for airline announcements.** If the threat escalates, carriers will reroute international flights to non-affected airports. United, which has 70% of Newark's international traffic, would be the first to pivot.

## The Bigger Picture

This is not an aviation story. It is an immigration enforcement story that happens to use airports as leverage. For the 4.4 million Indian Americans concentrated in exactly the metro areas under threat — the Bay Area, the New York–New Jersey corridor, greater Chicago, greater LA — the message is uncomfortable: your ability to travel internationally is now a variable in a political negotiation you have no seat at.

The DHS has not set a deadline. But Mullin's language — "pretty quick" — suggests the status quo has a shelf life. The prudent NRI traveler is already looking at the map."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe's New Biometric Border Is Already Broken — and NRIs Are Stuck in the Queue",
        "subheadline": "The EU's Entry/Exit System replaced passport stamps with fingerprints and facial scans on April 10. Six weeks in, it's causing four-hour queues, stranded passengers, and a scramble by countries to suspend it before summer peaks.",
        "slug": make_slug("eu-ees-biometric-border-nri-europe-travel-delays"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs traveling to Europe on Indian or US passports are non-EU nationals subject to mandatory EES registration. With processing times 4x longer than the old stamp system, summer trips to London-Paris-Rome itineraries are now logistical minefields.",
        "tags": ["travel", "europe", "visa", "biometric", "schengen", "ees"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Times", "url": "https://www.thetimes.com/travel/destinations/europe/four-hour-dover-queues-france-ees-border-checks"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/europe-airport-chaos-why-new-ees-rules-are-triggering-3-hour-queues-and-missed-flights-in-2026/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/ees-border-queues-2026/"},
            {"name": "European Parliament", "url": "https://www.europarl.europa.eu/doceo/document/E-10-2026-000679_EN.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29485309/pexels-photo-29485309.jpeg",
        "image_caption": "European passports — but for non-EU travelers including NRIs, the new EES biometric system has turned border crossings into multi-hour ordeals.",
        "body": """The pitch was elegant: replace the clunky passport stamp with a clean digital scan, track entry and exit automatically, and make European borders smarter and faster. The reality, six weeks after the EU's Entry/Exit System went live on April 10, is something closer to controlled chaos.

At Milan's Linate Airport, more than 100 passengers — families with children among them — were stranded last month when a three-hour border queue meant their flight to Manchester departed with most seats empty. At Dover, France suspended EES checks entirely during the half-term holiday rush after queues hit four hours. Airlines have no legal obligation to compensate passengers who miss flights due to border processing. One traveler told reporters: "We were told we were 'no-shows' while we were standing right there in the queue."

For Indian Americans planning summer trips to Europe, this is not background noise. It is a direct threat to itineraries, connections, and sanity.

## What Changed on April 10

The EES replaces manual passport stamps across 29 Schengen Area countries with a mandatory digital registration. Every non-EU traveler — which includes anyone on an Indian passport, and crucially, anyone on a US passport — must now provide four fingerprints and a facial biometric scan at their first point of entry.

The registration creates a digital profile valid for three years. Subsequent entries are supposed to be faster, requiring only a facial match. But here is the problem: since the system only launched in April, virtually every traveler entering Europe this summer is a first-time registrant. The maximum processing time applies to every single person in every queue.

Industry estimates suggest the initial registration takes four to six times longer than the old stamp-and-go method. At scale, across airports designed for the old speed, the math breaks down fast.

## The Worst Airports Right Now

Not all entry points are equally affected. The worst bottlenecks, based on traveler reports and industry data through late May:

**Paris Charles de Gaulle** — Consistently the longest waits, with reports of two to three hours during peak morning arrivals. Kiosk failures and software glitches have compounded the staffing shortage.

**Dover/Calais** — The English Channel crossing has been worst hit. France suspended biometric capture during the May half-term rush, reverting to passport stamps to clear the backlog. The suspension is expected to end before June, meaning full delays will return for peak summer.

**Lisbon and Milan** — Both have reported multi-hour queues and stranded passengers. Portugal has maintained strict enforcement, while Italy is experimenting with hybrid manual-digital processing during surge periods.

**Smaller airports offer relief.** Greece has implemented manual fallback processing at several islands. Switzerland allows up to six-hour pauses at specific border points when queues exceed thresholds.

## What NRIs Specifically Need to Know

**The 90/180 rule is now digitally enforced.** The EES automatically tracks your days in the Schengen zone. If you overstay — even by a day — the system flags it at exit and can trigger fines or future entry denials. NRIs who previously relied on fuzzy passport stamps to fudge a few days should be warned: the computer does not fudge.

**OCI card holders are not exempt.** An Overseas Citizen of India card grants unlimited entry to India. It grants exactly nothing in Europe. You are processed as a non-EU national regardless of your OCI status.

**Pre-register with the Frontex app.** The EU has launched a "Travel to Europe" mobile app that lets you pre-load your passport data and a facial scan up to 72 hours before arrival. Uptake has been dismal — the European Parliament noted that minimal adoption is worsening queues — but for NRIs willing to spend ten minutes on the app, it can meaningfully reduce kiosk time.

**Arrive four hours early.** The old two-hour buffer is no longer sufficient at major hubs. Paris and Malaga are officially recommending four hours for non-EU travelers.

**Skip the mega-hubs if you can.** Fly into Zurich (where suspension pauses are available), Athens (manual fallback at islands), or smaller Schengen airports in the Baltics or Scandinavia. Avoid Paris CDG and Lisbon during peak hours.

## The Summer Forecast

Aviation industry groups ACI Europe, Airlines for America, and IATA have jointly warned the European Commission that queues could double during peak summer — potentially reaching four to six hours at the busiest airports. The European Parliament has opened a formal question on whether the system should be revised before the high season.

Several countries are expected to invoke the emergency suspension clause, pausing biometric capture when processing times exceed threshold. But these pauses are limited to six hours and cannot be used as a permanent workaround.

The uncomfortable truth is that the EES will get better — three-year profiles mean returning travelers will eventually breeze through. But that "eventually" does not help the NRI family landing at CDG next Tuesday morning for a two-week vacation. For summer 2026, the advice is blunt: budget more time, expect less comfort, and do not assume your connecting flight will wait."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The World Cup Starts in Two Weeks — Here's the NRI Fan's Playbook for Getting There",
        "subheadline": "India did not qualify, but the Indian diaspora is everywhere the tournament is. From visa logistics to ticket scams to the DHS airport threat looming over New York, a practical guide for NRI fans heading to the 2026 FIFA World Cup.",
        "slug": make_slug("fifa-world-cup-2026-nri-fan-travel-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans are among the largest diaspora groups in every major World Cup host city — New York, Houston, Dallas, San Francisco, Los Angeles, Toronto. Many NRIs will attend as neutral fans or to support adopted teams, and the travel logistics are uniquely complex for those juggling US visas, Indian passports, or OCI status.",
        "tags": ["travel", "world-cup", "fifa", "soccer", "visa", "2026"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/sports/soccer/new-york-state-new-jersey-probing-fifa-world-cup-ticketing-practices-2026-05-22/"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/us-visitor-visa-rules-for-the-2026-fifa-world-cup.html"},
            {"name": "World Cup Guide", "url": "https://worldcupguide.ai/"},
            {"name": "iVisa", "url": "https://www.ivisa.com/blog/fifa-world-cup-2026-visa-guide"},
            {"name": "Fox 5 DC", "url": "https://www.fox5dc.com/sports/fifa-world-cup-2026-investigation-tickets"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34170128/pexels-photo-34170128.jpeg",
        "image_caption": "A packed stadium during FIFA World Cup qualifiers — scenes NRI fans across 16 host cities will experience starting June 11.",
        "body": """The 2026 FIFA World Cup kicks off on June 11 across 16 cities in the United States, Canada, and Mexico. India is not on the pitch. But the Indian diaspora is in every host city — and thousands of NRI fans are already planning to attend matches as neutrals, as adoptive supporters of Argentina or Germany or the host nations, or simply because this is the biggest sporting event to hit their backyard in a generation.

The tournament runs through July 19, when the final will be played at MetLife Stadium in East Rutherford, New Jersey. Getting there — and getting through the logistics — requires more planning than a typical sporting event. Here is what NRI fans need to know.

## Visa Realities: Three Countries, Three Sets of Rules

This is the first World Cup spread across three nations, and visa requirements differ for each:

**United States:** NRIs on valid H-1B, L-1, F-1, or green cards need no additional documentation. NRIs on Indian passports visiting specifically for the World Cup need a B-1/B-2 tourist visa. FIFA has arranged a FIFA PASS program that offers priority scheduling at US consulates for ticket holders — but appointment slots are nearly exhausted in India, and the standard B-1/B-2 wait time in Mumbai and Delhi has stretched to 60-plus days.

**Canada:** Toronto and Vancouver host group-stage matches. Indian passport holders need an Electronic Travel Authorization (eTA, $7 CAD) if they hold a valid US visa or Canadian visa. OCI cardholders still need the eTA. Processing is usually within minutes.

**Mexico:** Guadalajara, Monterrey, and Mexico City host matches. Indian passport holders with a valid US visa can enter Mexico without a separate Mexican visa for up to 180 days. This is the easiest of the three countries for NRIs to access.

## The Ticket Problem

The attorneys general of New York and New Jersey announced last week that they are investigating FIFA's ticketing practices following complaints that fans were misled about seat locations and faced sharply rising prices. "FIFA has turned buying a ticket to the World Cup into a gauntlet of confusion, fake scarcity, and impossibly high prices," said New Jersey AG Matthew Platkin.

For NRI fans, the practical advice is clear:

**Buy only through FIFA's official portal** at tickets.fifa.com. Resale through third parties is technically prohibited, though a secondary market exists on platforms like StubHub and Viagogo — at steep markups and with no guarantee of entry.

**Group-stage tickets** for less popular matches are the best value, starting around $50 for Category 3 seating at smaller venues. Quarterfinal and semifinal tickets start at $150-$250. The final at MetLife has face-value tickets north of $600, with resale prices already clearing $2,000.

**Beware scam listings.** FIFA's digital ticket system means physical tickets do not exist. Any listing offering a PDF or printout is fraudulent.

## The Airport Wildcard

As covered in our reporting this week, DHS Secretary Markwayne Mullin is threatening to pull customs processing from sanctuary city airports — a list that includes Newark, JFK, LaGuardia, SFO, LAX, and Chicago O'Hare. The final will be played twelve miles from Newark airport.

No action has been taken yet, and Transportation Secretary Sean Duffy has publicly opposed the plan. But the uncertainty alone is enough to warrant contingency planning. NRI fans flying internationally for matches in the New York area should consider arriving through non-sanctuary airports like Washington Dulles, Charlotte, or Atlanta and connecting domestically.

## City-by-City Highlights for NRI Fans

**New York/New Jersey (MetLife Stadium):** Nine matches including the final. Edison and Jersey City have some of the largest Indian populations outside India — finding desi food and community during the tournament will not be a problem. MetLife has no rail connection; plan for parking or buses from Secaucus Junction.

**Houston (NRG Stadium):** Eight matches. Houston's Hillcroft corridor — "Little India" — offers one of the best concentrations of Indian restaurants and shops in the US. The stadium is accessible by Metro Rail.

**Dallas (AT&T Stadium):** Eight matches. The DFW Indian community has grown rapidly, with Richardson and Plano as hubs. The stadium is in Arlington, roughly equidistant from Dallas and Fort Worth, with no public transit — car or rideshare only.

**San Francisco/Bay Area (Levi's Stadium):** Six matches. The epicenter of Indian American tech. Levi's Stadium in Santa Clara is a short Caltrain ride from San Francisco. But if DHS follows through on sanctuary city threats, SFO's international arrival processing could be at risk.

**Toronto:** Six matches at BMO Field. Canada's largest Indian diaspora — Brampton alone is 40% South Asian. Easy access via TTC subway.

## Practical Tips

**Book accommodation now.** Hotel rates in host cities have already doubled for match weekends. Airbnb is an option, though New York's short-term rental restrictions limit supply.

**Download the FIFA app.** Your ticket, match schedule, and stadium map live there. Without it, you cannot enter the venue.

**Plan two extra days.** The State Department recommends arriving 48 hours before your first match to account for travel disruptions, especially given the current aviation environment.

**Carry your documents.** Enhanced security at stadiums means passport or government-issued ID checks at entry. For NRIs on Indian passports, carry your passport and US visa to every match.

The World Cup has not been played in North America since 1994. For the Indian diaspora — now 4.4 million strong and embedded in every host metro — this is a once-in-a-generation home advantage. Use it."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
