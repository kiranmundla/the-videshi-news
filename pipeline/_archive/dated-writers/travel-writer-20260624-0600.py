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

# ---------------------------------------------------------------------------
body1 = """Air India's summer schedule is now in force, and for the diaspora it reads less like a timetable than a list of routes that quietly disappeared. Through August, the Tata-owned carrier has suspended its Delhi–Chicago nonstop outright, pulled the plug on Delhi–Newark and Mumbai–New York JFK, and thinned frequencies on the routes it kept. The cause is a familiar double squeeze: airspace over Iran and the wider Gulf remains hazardous after this spring's war, forcing longer, fuel-hungry reroutes, while jet fuel still costs roughly half again what it did a year ago.

## What actually changed on the US and Canada map

The North American cuts are the ones that sting for Indian Americans planning a summer trip home. Delhi–Chicago is gone until at least August. Delhi–Newark and Mumbai–New York JFK are suspended. Delhi–San Francisco drops from ten weekly flights to seven. On the Canadian side, Delhi–Toronto falls from ten weekly to five before returning to daily in August, and Delhi–Vancouver eases from seven to five.

It is not all subtraction. Air India has actually *boosted* Mumbai–Newark from three weekly flights to daily, and Delhi–New York JFK holds steady at seven a week. Read together, the moves push more US traffic through two surviving anchors — Delhi–JFK and a beefed-up Mumbai–Newark — while the airline lops off the thinner, money-losing sectors. Across its whole network the carrier insists it is still flying more than 1,200 international flights a month.

## Why fuel and airspace are doing the cutting

Fuel is the blunt instrument here. Aviation turbine fuel can run to 40% of an airline's operating costs, and the post-war spike has made ultra-long-haul sectors — exactly the kind that connect India to the US coasts — the first to tip from thin profit into loss. Air India spent weeks lobbying India's state oil marketers for relief on the "crack spread" formula that sets international fuel prices; those talks went nowhere, and the frequency cuts followed.

Airspace is the second blade. With Iranian, Iraqi and parts of Gulf airspace still treated as caution or no-go zones, flights between India and the West are detouring north or south, adding flying time, fuel burn and crew-rotation headaches to every rotation. A longer route on an already loss-making sector is the surest candidate for the chopping block.

## What it means for the diaspora this summer

For the roughly 5 million Indian Americans, the practical fallout is concentrated and avoidable if you plan around it. If you were counting on a one-leg Air India hop from Chicago, Newark or JFK out of Mumbai, that plan likely needs rebuilding. The cleanest remaining Air India nonstops to Delhi run from JFK and San Francisco; the strengthened Mumbai–Newark daily is the bright spot for the tri-state's large Maharashtrian and Gujarati communities.

Everyone else is looking at one of three workarounds. Connect over a Gulf hub on Emirates, Etihad or Qatar — though those carriers are wrestling with the same airspace mess and intermittent delays. Route through Europe on a Star Alliance or SkyTeam itinerary. Or fly United's own nonstops where they still operate. Whichever you pick, the booking math has shifted: nonstop fares on India routes are running well above last year, and the gap between a nonstop and a one-stop ticket has widened enough that many families are swallowing the extra connection to save money.

Two pieces of housekeeping matter. First, if Air India cancelled a flight you were already booked on, you are owed a re-accommodation, a free date change, or a full refund — the airline has committed to all three, so do not accept a worse seat by default. Second, book early. With seats pulled from the market and demand into India holding firm through the monsoon and toward the autumn festival rush, the cheap inventory is thinning fast.

## What's next

Air India has framed every cut as temporary and tied to conditions it expects to ease. Delhi–Toronto is already pencilled in to return to daily service in August, a useful signal that the airline intends to restore rather than abandon North American capacity once fuel and airspace normalise. The wild card is the Gulf: if airspace reopens cleanly and crude retreats, frequencies could come back faster than the August timeline suggests. Until then, the diaspora's safest assumption is that the nonstop you remember from last summer may not be flying this one — so check the schedule before you check the fare."""

body2 = """India has quietly rewired one of the diaspora's most-used documents. As of this spring, the Overseas Citizen of India card — the lifelong visa-free entry permit that some 4.5 million people of Indian origin carry — has gone fully digital. The Ministry of Home Affairs' Citizenship (Amendment) Rules, 2026 mandate that every new OCI registration, every passport update and every renunciation now run through the online portal at ociservices.gov.in, with applicants able to receive an electronic e-OCI record instead of, or alongside, the familiar booklet-and-sticker.

## What changed, and what didn't

The headline reassurance first: if you already hold a valid physical OCI card, you do not need to rush to convert it. Existing cards remain valid for travel. The digital shift bites only when you *do* something — apply fresh, update after a new passport, re-issue, or renounce. From that point on, the paper-in-duplicate era is over; Form XXVIII and its successors are filed electronically, and the government keeps the master record in a digital register.

The practical upside is real. No more couriering documents in duplicate to a consulate. Applications are trackable online. And because the record lives in a database, the long-promised tie-in to automated e-gates at major Indian airports finally has the back-end it needs. For a community that has spent years grumbling about OCI processing delays, a transparent, status-trackable pipeline is overdue.

## The fee print NRIs need to read

The convenience comes with a heftier price tag, revised on 1 April. A fresh e-OCI registration now costs USD 275 from outside India — up sharply — plus a USD 3 ICWF surcharge on every fee paid abroad and a roughly 1% card-processing charge. Re-issuance after your first post-20 passport is USD 25, a lost or damaged card runs USD 100, and a PIO-to-OCI conversion is USD 100.

The trap to avoid is the new late-update penalty. OCI holders aged 20 or younger must upload their new passport each time one is issued, and there is now a USD 25 penalty for missing the three-month window after receiving it. Update within three months and it is free; miss it and you pay. Reassuringly, there is no travel restriction in the gap between getting a new passport and recording it on the portal — so a delayed upload will not strand you at immigration, but it will cost you if you let it slide.

## Eligibility just widened — quietly

Folded into the same overhaul are eligibility changes that matter for diaspora families. Children born abroad to two Indian-national parents are now eligible for an OCI card; previously at least one parent had to be OCI-eligible. Foreign spouses of OCI holders or persons of Indian origin still qualify, though the marriage threshold has moved to two years from one, and the card is voided if the marriage dissolves.

There is also a notable opening for nationals of countries India had long excluded. Foreign nationals of Afghanistan, Bhutan, China, Iran, Nepal and Sri Lanka who meet the criteria can now apply for OCI — a real change for mixed-heritage families. Pakistan and Bangladesh nationals remain ineligible.

One firm new line concerns minors with dual documents: no minor may hold an Indian passport and a foreign passport at the same time. Parents applying for an Indian passport for a child must declare that no foreign passport is held, and surrender any existing one first. For families who had informally kept both "just in case," this closes the door.

## Why this matters to the diaspora

OCI is the document that lets the diaspora live, work and buy property in India indefinitely without a visa, and skip the FRRO registration that trips up ordinary foreign visitors. Anything that changes how it is issued ripples through millions of households planning trips, inheritances and retirements. The move to digital should, over time, mean faster turnarounds and fewer lost-in-the-mail horror stories. But the higher fees and the new penalty clock reward the organised and punish the procrastinator.

## What to do now

If your card is valid and your passport hasn't changed, do nothing. If you have a new passport, a baby born abroad, or a child whose card needs the post-20 update, start on the portal and mind the three-month window. And if you have been waiting to apply because the old paperwork felt daunting, the friction just dropped — even as the price went up."""

body3 = """The cheapest part of flying home to India this summer may be the ticket you didn't think to look for. With the nonstop and the one-stop fare now separated by a gulf wide enough to fund a second holiday, the diaspora's old reflex — pay the premium, avoid the layover — has stopped making financial sense for a lot of families. Understanding why means understanding what this spring's Gulf conflict did to the economics of long-haul flying.

## The 22% problem

Industry trackers put the increase on nonstop long-haul international fares at up to 22% above pre-conflict levels, and India routes sit squarely in the blast radius. Two forces stack on top of each other. Jet fuel still costs about 54% more than a year ago even after recent easing, and fuel can be 40% of an airline's running costs. Layer on the airspace problem — Iranian, Iraqi and parts of Gulf airspace remain hazardous, so India–West flights detour onto longer tracks that burn still more fuel — and the nonstop, the most fuel-intensive product an airline sells, is exactly where the surcharges land hardest.

The carriers have not been shy about passing it on. IndiGo layered fuel surcharges in two rounds this spring, adding up to ₹10,000 (about US$120) on a one-way Delhi-or-Mumbai-to-Gulf ticket. Air India applied a phased surcharge of US$4 to US$50 per sector. International economy fares were averaging around US$980 in early June — off a May peak but still more than 20% above the prior year.

## Why the multi-stop is back

Here is the twist the diaspora is rediscovering. When nonstops jumped 22%, the price gap to a one- or two-stop itinerary widened to somewhere between US$500 and US$2,000 a ticket. On a family of four flying SFO or JFK to India, that is the difference between an ordinary summer and an expensive one. So travellers are doing what they did a decade ago: routing through a hub.

The hubs themselves are in flux. Gulf giants — Emirates, Etihad, Qatar — are the natural connectors for India traffic, but they are absorbing the same airspace disruption, with intermittent cancellations and delays at Doha, Dubai and Abu Dhabi. European one-stops via a SkyTeam or Star Alliance carrier are an alternative, and Air India's own surviving network can still stitch a connection through Delhi or a strengthened Mumbai–Newark. The lesson is not "always connect" — it is that the nonstop premium is now large enough that connecting deserves a serious look, hub disruption and all.

## The timing lever most NRIs ignore

Price is not only about routing; it is about *when*. The conventional diaspora calendar — fly in June and July when the kids are off school — is the single most expensive window of the year, and it collides directly with the monsoon's flight-disruption season. The data is blunt about the alternative: the cheapest month to fly home in 2026 is September, the shoulder between the summer crush and the Diwali rush. Families who can flex even a few weeks past the school-holiday peak routinely save hundreds per seat.

For those locked into summer, two defensive moves help. Book early — airlines have pulled seats from the market and tightly controlled capacity, so the cheap inventory disappears faster than usual, and there is little prospect of a last-minute fare war while demand stays firm. And price the one-stop alongside the nonstop every single time; the habit of filtering for "nonstop only" is quietly costing diaspora travellers the most money this year.

## What's next

The pressure is structural, not permanent. If Gulf airspace reopens cleanly and crude retreats, the longer reroutes vanish and the fuel surcharges follow — analysts reckon even a 5% drop in fuel costs would meaningfully lift airline earnings, which tends to loosen fares. But carriers have little incentive to cut prices while planes fill at today's rates; as one consultant put it, if people will pay it, why give it back. For the diaspora, that means the savings this summer come from being flexible and contrarian — flying in September rather than July, and treating the layover not as a penalty but as the deal."""

# ---------------------------------------------------------------------------
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Cut Its Chicago, Newark and Mumbai–JFK Nonstops for the Summer — Here's the US Map That's Left",
        "subheadline": "Airspace over the Gulf and stubbornly high jet fuel have forced Air India to suspend or thin its North American flights through August, just as the diaspora's trip-home season peaks.",
        "slug": make_slug("air-india-summer-2026-us-canada-route-cuts-chicago-newark-jfk-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Indian Americans planning summer trips home face suspended Air India nonstops from Chicago, Newark and Mumbai–JFK, leaving SFO, Delhi–JFK and a daily Mumbai–Newark as the main surviving links.",
        "tags": ["travel", "airlines", "air india", "flights", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Business News This Week — Air India rationalises international network", "url": "https://businessnewsthisweek.com/business/air-india-rationalises-international-route-network-through-august-2026/"},
            {"name": "Travelobiz — Air India flight cuts through August 2026", "url": "https://travelobiz.com/air-india-cuts-flights-across-us-europe-australia-asia/"},
            {"name": "The Hindu BusinessLine — Air India to suspend Chicago flights", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-looks-to-suspend-flights-to-key-foreign-destinations-such-as-chicago/"},
            {"name": "Reuters — Air India cuts international flights amid Middle East conflict", "url": "https://www.reuters.com/business/aerospace-defense/air-india-cut-international-flights-amid-middle-east-conflict-2026/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Boeing_777-337-ER%2C_Air_India_AN1735909.jpg",
        "image_caption": "An Air India Boeing 777-300ER, the aircraft type used on the carrier's long-haul North American routes.",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The OCI Card Just Went Fully Digital — and the New Fees and Penalty Clock Reward the Organised",
        "subheadline": "India's 2026 rules move every new OCI application, passport update and renunciation online, introduce an e-OCI record, and quietly widen who can hold the diaspora's lifelong India entry permit.",
        "slug": make_slug("india-e-oci-digital-card-2026-new-fees-eligibility-nri-portal"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "The 4.5 million OCI holders now apply, update and renew entirely online — existing cards stay valid, but new $275 fees, a late-update penalty, and broader eligibility change the calculus for diaspora families.",
        "tags": ["travel", "visa", "oci", "immigration", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Dainik Jagran English — MHA notifies OCI rule changes 2026", "url": "https://english.dainikjagranmpcg.com/national/mha-notifies-oci-rule-changes-2026-applications-fully-online"},
            {"name": "SCC Times — Citizenship (Amendment) Rules, 2026", "url": "https://www.scconline.com/blog/post/2026/citizenship-amendment-rules-2026-oci-registration/"},
            {"name": "Wego Travel Blog — India introduces e-OCI: a guide", "url": "https://blog.wego.com/india-e-oci-digital-system/"},
            {"name": "Fragomen — Overseas Citizen of India cardholder processes streamlined", "url": "https://www.fragomen.com/insights/overseas-citizen-of-india-cardholders-processes-streamlined.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Indian_Passport_2021_Edition.jpg",
        "image_caption": "An Indian passport; OCI cardholders carry their visa-free India entry status tied to their foreign passport.",
        "image_attribution": "Wikimedia Commons",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nonstop Fares Home to India Are Up 22% — and the Layover You've Been Avoiding Is Suddenly the Smart Buy",
        "subheadline": "Gulf airspace detours and pricey jet fuel have blown out the gap between nonstop and one-stop tickets, rewriting how the diaspora should book a trip home in 2026.",
        "slug": make_slug("india-flight-fares-2026-nonstop-22-percent-multistop-fuel-surcharge-nri"),
        "category": "travel",
        "vertical": "economy",
        "diaspora_angle": "With nonstop India fares up to 22% higher and one-stop tickets now $500–$2,000 cheaper, NRIs save most by pricing layovers and flying in September instead of the summer-holiday peak.",
        "tags": ["travel", "flights", "airfare", "fuel surcharge", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — airline ticket prices stay high despite fuel relief", "url": "https://www.travelandtourworld.com/news/article/united-states-airline-ticket-prices-high-fuel-relief-us-iran-deal/"},
            {"name": "CoinCentral — US airline fares still high despite jet fuel price drop", "url": "https://coincentral.com/us-airline-fares-still-high-despite-jet-fuel-price-drop/"},
            {"name": "Wego Travel Blog — why are flights so expensive in 2026", "url": "https://blog.wego.com/why-are-flights-so-expensive-2026/"},
            {"name": "Reuters — IndiGo, Air India cut June-July flights amid high jet fuel prices", "url": "https://www.reuters.com/business/aerospace-defense/indigo-air-india-cut-june-july-domestic-flights-2026/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12940608/pexels-photo-12940608.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An airport departure board; rising fuel and rerouting costs have widened the gap between nonstop and connecting fares.",
        "image_attribution": "Pexels",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
