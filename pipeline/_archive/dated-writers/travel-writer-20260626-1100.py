#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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

article1_body = """Argentina quietly did something this week that almost no headline captured: it waved Indian passport holders in without a visa, provided they carry a valid US visa or green card. It is a small administrative change with an outsized message — the single most useful travel document an Indian American owns is often not the Indian passport, but the American visa stapled to its history.

For the roughly 4.5 million people of Indian origin in the United States — including the large share who travel on Indian passports while holding green cards or long-term US visas — this is the rule that quietly reshapes where a vacation can go. The Indian passport ranks modestly on mobility indices, but bolted to a US visa it unlocks a second, far longer list of destinations that skip the consulate entirely.

## What the US visa actually unlocks

The list is longer than most NRIs realize, and it spans three categories. The first is outright visa-free entry: Mexico (no separate visa for Indian nationals holding a valid US visa), Costa Rica, Panama, and Georgia among them. The second is visa-on-arrival, where the US visa is the qualifying document — the United Arab Emirates issues a 14-day visa on arrival to Indians with a US visa or green card, and the Bahamas, Bahrain, Oman and Qatar operate similar arrangements. The third is a streamlined e-visa, where the US document fast-tracks approval, as with Turkey.

Then there is the Caribbean, which for a Bay Area or tri-state family is the closest warm-water escape that does not require a fresh visa run. Bermuda allows 90 days on a valid US visa; Aruba, Curacao, St. Maarten and the Cayman Islands all admit Indian nationals carrying one. Jamaica, St. Kitts and Nevis, and the British Virgin Islands round out a roster that turns a long weekend into a passport-stamp collection without a single embassy appointment.

## Why this matters more than a new airline route

A new nonstop flight saves hours. A visa rule like this saves the thing NRIs guard most jealously: time off and the dread of the consular queue. The US B1/B2 interview backlog in India has stretched past 100 days at several posts, and the new $750 expedited-interview fee taking effect July 1 underscores how scarce appointment slots have become. Against that backdrop, the ability to fly somewhere without queuing for yet another visa is not a convenience — it is the whole trip.

The practical playbook is straightforward. Before booking, confirm three things: that the US visa is a multiple-entry type (most B1/B2 grants are), that it has the minimum remaining validity the destination demands (often three to six months), and, for a handful of countries such as Panama, that the visa has actually been used at least once to enter the United States. Green-card holders generally face the easiest path of all, since permanent residency is treated as the strongest proof of ties.

## The fine print that trips people up

Three traps recur. First, rules differ by passport-plus-visa combination: a Canada or UK visa unlocks a partly different list (the UK visa, for instance, opens Ireland and several British Overseas Territories), so the document you carry determines the map. Second, airline check-in staff at the US end occasionally misread these arrangements, so carrying a printout of the destination's official entry rule is worth the paper. Third, "visa-free" is not "condition-free" — onward tickets, proof of funds and accommodation bookings are frequently demanded on arrival.

For families planning a summer or winter break, the lesson is to stop thinking of the Indian passport as the ceiling. Pair it with the US visa already in hand, and Cancun, the Caribbean, Tbilisi and Dubai open up with nothing more than a flight booking. In a year when every consular line in India has only grown longer, the cheapest visa is the one you never have to apply for."""

article2_body = """For 17 years, there was no nonstop flight between Scandinavia and India. That gap closed this month: SAS, the flag carrier of Denmark, Norway and Sweden, has returned to India with a year-round Copenhagen–Mumbai service, five flights a week on an Airbus A330. It is a route built for Scandinavian business travelers — but read the timetable closely and it is just as much a play for the North American diaspora.

The flights are deliberately scheduled to dovetail with SAS's transatlantic network. SK969 leaves Copenhagen in the early afternoon and lands in Mumbai after midnight; the return SK970 departs Mumbai at dawn and is back in Copenhagen by late morning. SAS says those times are tuned to connect smoothly with New York, Boston and Toronto — three of the densest Indian-American and Indo-Canadian markets on the eastern seaboard.

## A third way to fly home

For an NRI in the tri-state area or greater Boston, the India trip has long meant a binary choice: an Air India or United nonstop that sells out and prices up around festivals, or a Gulf-hub one-stop through Dubai, Doha or Abu Dhabi that adds hours and a desert layover. Copenhagen now offers a northern alternative — a single, civilized European connection in a compact airport, on a route that is brand new and therefore not yet baked into everyone's booking habits.

That novelty is the opportunity. New routes typically launch with introductory fares and empty middle seats while they build a customer base, and a five-a-week frequency means SAS is courting demand rather than rationing it. For travelers who have watched the JFK–Mumbai and Newark–Mumbai nonstops climb past $1,500 in peak season — and who saw American Airlines stretch its JFK–Delhi flight to 17 hours to skirt closed Russian airspace — a fresh one-stop through a friendly European hub is worth pricing out.

## Why Copenhagen, and why now

The route is a bet on Mumbai's pull. India's financial capital, home to more than 20 million people, anchors the country's corporate and entertainment economy, and Scandinavian companies have deepened their India ties over the past decade. But the diaspora math is just as compelling: Copenhagen is a Star Alliance-adjacent gateway with onward reach across the Nordics and into North America, and SAS's recent pivot toward the SkyTeam orbit has reshaped how its connections knit together.

For the Mumbai-origin traveler, the appeal runs in reverse too. A parent visiting family in Boston, or a student heading to a university in the US Northeast, now has a same-airline path through Copenhagen instead of a self-transfer through a crowded Gulf terminal. Single-airline routings matter most when something goes wrong: a missed connection on one ticket is the airline's problem, not the passenger's.

## What to weigh before booking

Three caveats apply. First, this is a one-stop, not a nonstop — total travel time will exceed the 15-or-so hours of a direct Mumbai–US flight, so it competes on price and comfort, not raw speed. Second, the A330's hard product is solid but not the newest cabin in the sky; travelers chasing lie-flat luxury should compare it against Gulf carriers' premium offerings. Third, five-weekly service means less day-to-day flexibility than a daily flight, so rebooking after a disruption can mean a longer wait.

Still, the broader signal is what diaspora travelers should note. A year of route cuts — Air India trimming its Chicago, Newark and Mumbai–JFK nonstops for the summer, IndiGo pulling back from Southeast Asian airspace — has made the India–West map feel like it is shrinking. SAS's return cuts the other way. Every new European gateway that times its flights for New York, Boston and Toronto is one more lever the diaspora can pull when the nonstops are full or overpriced. For the family booking a Diwali trip this autumn, Copenhagen is suddenly worth a look."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Your US Visa Just Unlocked Argentina — and 40 Other Countries Most NRIs Forget They Can Enter",
        "subheadline": "Argentina's new visa-free entry for Indians holding a US visa is the latest reminder that an NRI's most powerful travel document isn't the passport — it's the American visa stapled to it.",
        "slug": make_slug("us-visa-unlocks-40-countries-argentina-mexico-caribbean-indians-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Most Indian Americans travel on Indian passports while holding US visas or green cards — a combination that opens visa-free or visa-on-arrival entry to 40+ countries, sidestepping India's months-long consular queues entirely.",
        "tags": ["travel", "visa", "us-visa", "caribbean", "mexico", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia — Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"},
            {"name": "Wise — Visa on Arrival for Indians 2026", "url": "https://wise.com/us/blog/visa-on-arrival-for-indians"},
            {"name": "The Daily Jagran — 40+ Countries Indians Can Visit With a US Visa", "url": "https://www.thedailyjagran.com/lifestyle/list-of-40-countries-indians-can-visit-with-a-valid-us-visa-no-extra-visa-needed"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7235804/pexels-photo-7235804.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=900&w=1600",
        "image_caption": "A world map, compass and passport pages stamped with travel and visa marks, including a Buenos Aires departure stamp.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "SAS Just Reopened the Scandinavia–India Air Bridge After 17 Years — and Timed It for New York, Boston and Toronto",
        "subheadline": "The new Copenhagen–Mumbai nonstop is built for Scandinavian business, but its connection times reveal a quieter target: the North American diaspora hunting a third way home.",
        "slug": make_slug("sas-copenhagen-mumbai-route-india-return-nyc-boston-toronto-diaspora-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "SAS's revived Copenhagen–Mumbai route is scheduled to connect with New York, Boston and Toronto — giving East Coast and Canadian NRIs a fresh, single-airline one-stop alternative to sold-out US nonstops and crowded Gulf hubs.",
        "tags": ["travel", "airlines", "sas", "mumbai", "diaspora", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SAS Group — SAS launches new route between Copenhagen and Mumbai", "url": "https://www.sasgroup.net/newsroom/press-releases/2025/sas-launches-new-route-between-copenhagen-and-mumbai/"},
            {"name": "AirlineGeeks — SAS Launching First Route to India in 17 Years", "url": "https://airlinegeeks.com/2025/06/26/sas-launching-first-route-to-india-in-17-years/"},
            {"name": "CAPA Centre for Aviation — SAS summer 2026 international services", "url": "https://centreforaviation.com/news/sas-to-launch-nine-international-services-from-copenhagen-stockholm-and-oslo-in-summer-2026"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/LN-RKR_-_Airbus_A330-343_-_Scandinavian_Airlines_%2843853541840%29.jpg/1280px-LN-RKR_-_Airbus_A330-343_-_Scandinavian_Airlines_%2843853541840%29.jpg",
        "image_caption": "A Scandinavian Airlines (SAS) Airbus A330-343, the aircraft type operating the new Copenhagen–Mumbai route.",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  words: {wc} | {art['headline'][:60]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
