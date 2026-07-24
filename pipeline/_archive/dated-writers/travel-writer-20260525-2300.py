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
        "headline": "Britain's Immigration Squeeze Is Pushing Indians Out — and the Numbers Are Stark",
        "subheadline": "ILR fees are up 25 percent, the salary threshold has jumped to £41,000, and Indian student enrollment has crashed by 76 percent. The UK's toughest immigration year in a decade is reshaping the diaspora's calculus.",
        "slug": make_slug("uk-immigration-squeeze-indians-ilr-fees-students"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The UK is home to 1.8 million people of Indian origin — the largest ethnic minority in Britain. These policy changes hit NRI families planning to settle, students weighing UK versus US or Canada, and anyone holding a Tier 2 or Skilled Worker visa. For Indian Americans with relatives in London, Birmingham, or Leicester, the practical question is whether the UK path still makes financial sense.",
        "tags": ["travel", "visa", "uk", "immigration", "students", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NBot Indian Diaspora Pulse", "url": "https://nbot.ai/curator/xr35rc6r/highlights/uk-digital-status-rollout-2026"},
            {"name": "UK Home Office Immigration Rules", "url": "https://www.gov.uk/government/publications/immigration-rules-changes"},
            {"name": "HESA Student Data", "url": "https://www.hesa.ac.uk/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5428705/pexels-photo-5428705.jpeg",
        "body": """The United Kingdom has spent 2026 methodically raising the drawbridge on immigration — and Indian nationals are absorbing more of the impact than almost any other group.

Starting April 8, the Home Office hiked Indefinite Leave to Remain (ILR) application fees by between 6 and 25 percent, depending on the visa category. A skilled worker applying for permanent settlement now pays upward of £2,885 — before the mandatory Immigration Health Surcharge, which itself rose to £1,035 per year in 2024 and shows no sign of retreating. For a family of four applying together, the total outlay for ILR alone can exceed £15,000.

## The Salary Wall

The more consequential change is the salary threshold. The minimum earning requirement for a Skilled Worker visa now sits at £41,000 — a figure that prices out a significant slice of the Indian workforce in the UK, particularly in hospitality, care, retail, and lower-tier tech roles. When the threshold was £26,200 just two years ago, it was achievable for recent graduates finding their footing. At £41,000, it is a filter that favors established professionals and explicitly discourages early-career immigration.

The government frames this as protecting British workers from wage undercutting. The practical effect for Indians — who comprised the largest group of Skilled Worker visa holders in 2024 and 2025 — is that fewer people qualify, and those who do face longer waits and steeper fees.

## The Student Collapse

The most dramatic number is the one nobody in Westminster seems eager to discuss in full: Indian student enrollment at UK universities has fallen 76 percent from its recent peak.

The causes are layered. The post-study work visa was shortened. Dependant visa rules were tightened, making it nearly impossible for spouses of students to work in the UK. Universities that once ran aggressive recruitment campaigns in Delhi, Mumbai, and Hyderabad are now reporting half-empty international cohorts. Refusal rates for student visa applications from India have climbed, with June seeing some of the highest rejection numbers in years.

For NRI families in the United States weighing whether to send children to the UK for university, the message is increasingly clear: the welcome mat has been pulled. Canada — despite its own recent international student cap — and Australia remain more predictable destinations. American universities, while expensive, at least come with the familiarity of a system NRIs already navigate.

## eVisas and the Digital Shift

Layered on top of the fee and threshold changes is the UK's ongoing eVisa rollout, which replaces physical immigration stamps and biometric residence permits with a digital status tied to a passport number. The Home Office has been urging all visa holders to create a UKVI account and link their status before physical documents become invalid.

The eVisa itself is not the problem — most NRIs are comfortable with digital documentation. The issue is timing. The rollout has overlapped with the fee hikes and policy tightening, creating a bureaucratic fog where applicants are simultaneously trying to convert their status, pay increased fees, and meet higher salary thresholds. Immigration lawyers in London report a surge in consultations from Indian clients confused about which process to prioritize.

## The Political Undercurrent

There is a harder edge to this, too. Reform UK and its leader Nigel Farage have made abolishing ILR entirely a policy plank, arguing that permanent settlement should be replaced with renewable permits. In Harrow — a London borough with one of the UK's largest Indian populations — a recent survey showed 13 percent support for scrapping ILR, a number that is small but not negligible in a community that has historically viewed settlement as the goal of the immigration journey.

Local elections in Scotland saw Q Manivannan, a Tamil-origin candidate, win a council seat — a reminder that the Indian diaspora in the UK is not merely a passive recipient of policy but an increasingly active political force. Whether that political energy translates into pushback against restrictive immigration policy remains an open question.

## What This Means for NRIs

For Indian Americans with family connections in the UK, these changes are not abstract. A sibling on a Skilled Worker visa who earned £35,000 a year ago was on track for settlement; today, they do not meet the threshold. A nephew considering a master's at a Russell Group university now faces a system that is both more expensive and less welcoming than it was 18 months ago.

The practical advice is straightforward: anyone in the NRI extended family considering a UK immigration path should run updated numbers with an OISC-registered immigration adviser. The fees, thresholds, and rules have all moved — and they have all moved in one direction."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Paris Pivot: Why NRIs Are Quietly Rerouting Through Europe Instead of Dubai",
        "subheadline": "The Iran conflict upended Gulf routing. Now Air France, KLM, and Asian carriers are filling the gap — and for NRIs flying between the US and India, Paris CDG is becoming the hub that Dubai used to be.",
        "slug": make_slug("paris-pivot-nri-rerouting-europe-hub-air-france"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the 4.4 million Indian Americans who fly to India regularly, the Gulf hub model — connecting through Dubai, Doha, or Abu Dhabi on Emirates, Qatar Airways, or Etihad — has been the default for a decade. The Iran conflict has disrupted that calculus, and European hubs like Paris CDG and Amsterdam Schiphol are emerging as viable alternatives with competitive fares and better schedule reliability.",
        "tags": ["travel", "airlines", "air-france", "nri", "flights", "europe", "routing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel Man Today", "url": "https://travelmantoday.com/air-france-india-flights-2026-indians/"},
            {"name": "CNN Travel", "url": "https://www.cnn.com/2026/05/22/travel/us-travel-decline-tourism/index.html"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/v7lmod2vey86/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32380084/pexels-photo-32380084.jpeg",
        "body": """For years, the NRI flight to India followed a familiar pattern: drive to SFO, JFK, or ORD, board an Emirates or Qatar Airways flight, kill six hours in a gleaming Gulf lounge, and land in Delhi or Mumbai feeling like the journey was at least comfortable, if not short. Dubai International and Hamad International in Doha were not just layover airports — they were the connective tissue of the Indian American travel experience.

The Iran conflict changed that. Restricted airspace over the Persian Gulf and parts of the Middle East has forced airlines to reroute, adding flight time and burning more fuel. The effects have rippled across the industry: higher fares, schedule unpredictability, and a 61 percent drop in international revenue passenger kilometers through the Gulf corridor in March 2026 alone, according to Indian aviation data from Livemint.

Into this gap, European hubs are making an aggressive play — and NRIs are starting to notice.

## Air France's India Push

Air France has been quietly expanding its India connectivity through Paris Charles de Gaulle throughout 2026. The airline now operates robust schedules from Delhi, Mumbai, Bangalore, and Chennai through CDG, offering onward connections to virtually all of Europe, plus North America, South America, and Africa via the SkyTeam alliance.

For an NRI in Dallas or Philadelphia, the math is worth running. A DFW-CDG-BLR itinerary on Air France or a PHL-AMS-DEL routing on KLM can be price-competitive with the Gulf carriers — particularly now that fuel surcharges on Middle East routings have spiked. Business class fares through Paris have been running 10 to 15 percent cheaper than equivalent Emirates routings on several key city pairs this spring.

The transit experience at CDG has improved meaningfully, too. Terminal 2E — where most India flights operate — offers a smoother connection flow than it did even two years ago, with dedicated SkyTeam lounges and faster minimum connection times.

## The Asian Carrier Surge

It is not just European airlines filling the gap. A broader shift is underway: Asian carriers are surging on European routes precisely because travelers are avoiding Middle Eastern hubs.

Airlines like Singapore Airlines, Cathay Pacific, and ANA have seen increased demand for their Europe-Asia services. For NRIs, this creates an interesting three-way comparison. Flying SFO-SIN-DEL on Singapore Airlines avoids the Middle East entirely and offers some of the best long-haul service in the industry. The tradeoff is longer total journey time — typically 20 to 24 hours versus 18 to 20 through a Gulf hub — but with better schedule reliability in the current environment.

The carriers that are losing are the Gulf trio. Emirates, Qatar Airways, and Etihad are not sitting idle — Emirates has announced a $5 billion cabin retrofit program for its A380 fleet — but their geographic advantage has become a geographic liability. When the shortest path between two points runs through a conflict zone, the shortest path stops being the fastest.

## What NRIs Should Actually Do

The practical upshot for anyone booking India travel this summer or fall:

**Run the comparison.** Google Flights and Kayak now show routing options that would have been buried two years ago. A JFK-CDG-BOM itinerary that once looked like a detour may now be faster door-to-door than JFK-DXB-BOM on a rerouted Emirates flight.

**Check SkyTeam partners.** Air France, KLM, Delta, and their SkyTeam partners pool frequent flyer miles. If you have Delta SkyMiles — and many NRIs do — you can redeem them on Air France metal to India. Award availability through Paris has been better than through the Gulf carriers this spring.

**Consider Amsterdam.** KLM's Schiphol hub is one of Europe's most efficient for connections. AMS-DEL and AMS-BOM services are well-timed for US East Coast connections, and the airport's single-terminal design means shorter layovers.

**Do not write off the Gulf entirely.** Qatar Airways' Doha hub is less affected by airspace restrictions than Dubai, and the airline's business class product remains among the best globally. But price and schedule it against European options before defaulting to what you have always booked.

## The Bigger Picture

The Iran conflict has accelerated a structural shift that was already underway. India-Europe air connectivity was growing before the Gulf disruption — Air India's nonstop routes to London, Frankfurt, and Milan were expanding, and SWISS just launched Zurich-Bengaluru. The conflict simply made European routing competitive on the one metric Gulf carriers owned: price.

For the Indian American traveler who flies to India once or twice a year, the era of the automatic Dubai booking is over. The replacement is not a single alternative but a wider set of options — Paris, Amsterdam, London, Frankfurt, Singapore, Tokyo — each with tradeoffs worth evaluating. The days of loyalty to a single hub are probably done."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
