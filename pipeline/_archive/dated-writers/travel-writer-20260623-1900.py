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
        "headline": "The UK's Travel Permit Is Now Mandatory — and Which One You Need Depends on Which Passport You Carry",
        "subheadline": "Since February, no one boards a UK-bound flight without digital permission. For the diaspora, the rule splits sharply by passport: US and Canadian citizens need a £20 ETA, but an Indian passport still means a full visa.",
        "slug": make_slug("uk-eta-mandatory-nri-indian-passport-us-citizen-visa-split"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "A US- or Canadian-citizen NRI flying to London now needs only a £20 ETA, but a green-card holder or visiting parent on an Indian passport still needs a full UK visitor visa — and the difference trips up mixed-status families every summer.",
        "tags": ["travel", "visa", "uk", "eta", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "GOV.UK — ETA enforcement", "url": "https://www.gov.uk/guidance/apply-for-an-electronic-travel-authorisation-eta"},
            {"name": "Reuters — UK to enforce travel permit", "url": "https://www.reuters.com/world/uk/uk-enforce-travel-permit-requirement-foreign-visitors-2026-02-25/"},
            {"name": "Home Office ETA factsheet (April 2026)", "url": "https://homeofficemedia.blog.gov.uk/electronic-travel-authorisation-eta-factsheet-april-2026/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A traveler holds a passport at an international airport departures hall",
        "image_attribution": "Pexels",
        "body": """Britain has quietly closed the era of showing up at the airport with just a passport and a return ticket. Since **25 February 2026**, the UK's Electronic Travel Authorisation (ETA) has been enforced at every port of entry, and airlines now check for it before letting anyone board. No ETA, no eVisa, no boarding pass — the carrier turns you away at the gate, not the border.

For the Indian diaspora, the change is less about whether you can go and more about *which document you need* — and that answer depends entirely on the passport in your hand.

## Two passports, two rulebooks

If you are a **US or Canadian citizen** — which describes a large and growing share of NRIs — the UK now requires you to hold an ETA before you fly. It costs **£20** (raised from £16 in April), is applied for through the official UK ETA app or GOV.UK, and most approvals come back automatically within minutes. The Home Office still advises allowing up to three working days for the small share of applications that get pulled for extra checks. Once granted, the ETA links electronically to your passport and is good for **multiple trips of up to six months each, over two years** or until the passport expires, whichever comes first.

If you carry an **Indian passport**, the ETA is not for you. India is not on the UK's visa-waiver list, so Indian nationals still need a full **Standard Visitor visa** — the same application, biometrics appointment, and fee that applied before. The ETA scheme changes nothing for the green-card holder visiting family in London, or for the parents flying in from Hyderabad for a grandchild's graduation. They need the visa, and they need it well in advance.

## The mixed-status family trap

This split is exactly where diaspora families get caught. A typical summer itinerary — US-citizen parents, a US-citizen teenager, and a visiting grandparent on an Indian passport, all flying London together — now involves two completely different paperwork tracks. The citizens knock out their ETAs on a phone in ten minutes; the grandparent needs a visa appointment that can take weeks in peak season. Booking the flights first and sorting documents later is how people end up rebooking.

There is a second catch that surprises even seasoned travelers: **transit**. If your routing connects through the UK and you pass through UK passport control, you need an ETA (or a visa, depending on passport) even if you never leave the airport area. Travelers transiting airside through Heathrow or Manchester without clearing immigration do not currently need one — but that exemption is narrow, and the safer assumption on any UK connection is that you need permission to travel.

## What to do before you book

- **US/Canadian-citizen NRIs:** Apply for the ETA through the official UK ETA app — not a third-party site that charges a markup. Do it a few days before travel, especially in summer. Remember it is tied to your passport; renew the passport and you need a fresh ETA.
- **Indian-passport holders:** Treat the UK like any other visa country. Start the Standard Visitor visa process early — weeks, not days — and don't assume the new digital scheme shortcuts anything for you.
- **Families:** Sort the visiting relative's visa *first*. It is the long pole. The ETAs can wait until the week of travel.

## The bigger picture

The UK is not an outlier. The EU's own ETIAS digital permission is due to roll out later in 2026, which means US- and Canadian-citizen NRIs will soon need a similar pre-clearance for Schengen Europe too. The age of the spontaneous transatlantic hop is ending for everyone who isn't a citizen of the destination. For diaspora travelers juggling multiple passports across one family, the practical lesson is simple: the cheapest part of any UK trip is now the flight deal, and the part that will actually derail you is the document you forgot somebody needed.

The good news is that for the ETA crowd, compliance is genuinely a ten-minute task on a phone. The trap is assuming everyone in the family lives under the same rule. They don't — and the airline gate is an expensive place to find that out."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your US Visa Is Also a Mexico and Caribbean Visa — the Beach Trip the Diaspora Keeps Overlooking",
        "subheadline": "Indian passport holders with a valid US visa or green card can skip the Mexican visa line entirely and stay up to 180 days. The same logic unlocks a string of Caribbean islands — and it's the easiest summer escape NRIs aren't taking.",
        "slug": make_slug("mexico-caribbean-visa-free-us-visa-green-card-nri-summer-beach"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "An Indian passport ranks 80th in the world, but paired with a US visa or green card it quietly unlocks Mexico for 180 days visa-free — turning Cancún and Tulum into a long-weekend trip for the diaspora instead of a paperwork ordeal.",
        "tags": ["travel", "mexico", "caribbean", "visa", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Government of Mexico — visa exemption notice", "url": "https://consulmex.sre.gob.mx/washington/index.php/ligavisos/15-informacion/156-visas-espanol"},
            {"name": "Visa policy of Mexico — Wikipedia", "url": "https://en.wikipedia.org/wiki/Visa_policy_of_Mexico"},
            {"name": "Henley Passport Index 2026 — India", "url": "https://www.henleyglobal.com/passport-index"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12174627/pexels-photo-12174627.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A beach on Mexico's Caribbean coast near Tulum on the Yucatán Peninsula",
        "image_attribution": "Pexels",
        "body": """The Indian passport sits at 80th on the 2026 Henley index, with visa-free or visa-on-arrival access to 55 destinations. That number undersells what a diaspora traveler can actually do, because it ignores the single most powerful travel document many NRIs already carry: a **valid US visa or green card**.

Pair an Indian passport with that, and one of the world's great beach coastlines opens up without a single trip to a consulate.

## The rule that does the work

Mexico does not require Indian citizens to obtain a Mexican visa **if they hold a valid, unexpired visa or permanent-residence document from the United States, Canada, the UK, Japan, or any Schengen country**. The Mexican government's own consular notice spells it out: present the valid foreign visa together with your passport, and you enter for tourism, business, or transit for up to **180 days**.

For the Indian diaspora in America, that covers the obvious cases — a B1/B2 visitor visa, an H-1B or L-1 work visa, an F-1 student visa, or a green card all qualify. The visa simply has to be valid on the day you travel. There is no separate Mexican application, no bank-statement packet, no consular appointment. You fill in the FMM tourist form (often bundled into your airfare) and get your entry stamp at the airport.

This is the trip the diaspora keeps overlooking. Cancún, the Riviera Maya, Tulum, Mexico City, and Oaxaca are three to five hours from most US hubs, cost a fraction of a long-haul fare, and — for the visa-holding NRI — involve roughly the same paperwork as flying to Florida.

## The student-visa angle most people get wrong

There's an extra wrinkle that matters for the large Indian student population in the US. F-1 and J-1 students can use a short trip to Mexico, Canada, or the adjacent Caribbean islands (under 30 days) to **re-enter the US on an expired visa stamp** under automatic visa revalidation — provided they keep valid status, carry a current I-20 or DS-2019 with a travel signature, and an I-94. It is a genuinely useful provision, but it is narrow: it does not apply if you visit any other country on the same trip, and students from a handful of restricted nationalities are excluded. Indian students qualify, but the rules reward reading the fine print before booking.

## The Caribbean extension

The same "valid US visa unlocks the door" logic stretches across much of the Caribbean and Central America, where many nations waive their visa for holders of US, Canadian, UK, or Schengen visas. And separately from any foreign-visa trick, the Indian passport *on its own* already gets visa-free or visa-on-arrival entry to a surprising run of islands: Barbados, Dominica, Grenada, Jamaica, Trinidad and Tobago, St. Vincent and the Grenadines, the British Virgin Islands, and Montserrat among them. Stack the two, and a diaspora family has a deep menu of warm-water options that never touch a consulate.

## Before you go

- **Check expiry, not category.** The visa or green card must be valid on your travel date. An expired US visa — even with a valid I-94 — does not trigger the Mexican exemption (the student re-entry rule above is a separate US provision, not a Mexican one).
- **Carry the physical proof.** Bring the passport with the visa stamp, or the green card itself. Airlines and Mexican immigration will ask to see it.
- **Mind the FMM.** Stays of seven days or longer trigger a small tourist-card fee (around US$32); shorter visits are typically free. It's a permit, not a visa.
- **Match destinations to documents.** Each Caribbean nation sets its own terms — confirm whether it's your Indian passport or your US visa doing the work before you book.

The takeaway for the diaspora is almost embarrassingly simple. The visa you stood in line for at the US consulate is doing double duty. It's a work permit, a study permit — and, most summers go to waste forgetting it, a passport to a 180-day beach holiday."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Planning the Great American Road Trip This Summer? Here's Which National Parks Make You Reserve a Spot — and Which Don't",
        "subheadline": "Glacier just scrapped its timed-entry system, Yellowstone needs no reservation at all, but Rocky Mountain still gates you by the hour. A diaspora family's guide to the 2026 rules — including the new free-entry days that now exclude tourists.",
        "slug": make_slug("us-national-parks-2026-timed-entry-reservations-nri-family-road-trip"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "The multi-generational summer road trip is a diaspora staple, but 2026's patchwork of park reservation rules — and a new policy limiting free-entry days to US citizens and residents — can derail a trip planned from a relative's WhatsApp itinerary.",
        "tags": ["travel", "usa", "national-parks", "road-trip", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "National Park Service — Summer 2026 access plans", "url": "https://www.nps.gov/orgs/1207/summer-2026-access.htm"},
            {"name": "Rocky Mountain NP — Timed Entry Reservations", "url": "https://www.recreation.gov/timed-entry/10086910"},
            {"name": "Glacier NP — Going-to-the-Sun Road", "url": "https://www.nps.gov/glac/index.htm"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28367799/pexels-photo-28367799.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A mountain road winding through Glacier National Park, Montana",
        "image_attribution": "Pexels",
        "body": """The multi-generational summer road trip — kids in the back, grandparents flown in from India, a cooler of theplas, and a loop through the West's marquee national parks — is about as diaspora a tradition as exists in America. The catch in 2026 is that "just show up at the gate" no longer works the same way at every park, and the rules changed *again* this year. Here's the map.

## The parks that gate you by reservation

**Rocky Mountain National Park** remains the strictest of the headliners. From **22 May through mid-October 2026**, a timed-entry reservation is required to enter during peak daytime hours — and that applies to the whole park, including outlying spots like Lily Lake, Longs Peak, and Lumpy Ridge. There are two tiers: a plain "Timed Entry" permit and a "Timed Entry + Bear Lake Road" permit for the most popular corridor. Both are booked on Recreation.gov, and the prime slots vanish fast. If Rocky is on your itinerary, book it the moment your dates are firm.

## The parks that loosened up

The headline reversal this year is **Glacier National Park** in Montana. After five summers of requiring a timed-entry reservation to drive the spectacular Going-to-the-Sun Road, the park **scrapped the timed-entry system for 2026**. The road opened to vehicles on 22 June, and instead of reservations, Glacier is managing crowds through new parking and traffic rules at Logan Pass. Note the vehicle size limits — anything over 21 feet long or 8 feet wide is barred on the alpine stretch between Avalanche and Rising Sun, which matters if you rented a large RV for the family.

**Arches National Park** in Utah will **not** run a timed-entry system in 2026 either; the advice there is simply to arrive early or after hours (it's a dark-sky park, and evening visits are encouraged). **Yellowstone** has never required an entry reservation and still doesn't — you just need an entrance pass. But campgrounds and lodging inside Yellowstone book out months ahead, so the reservation you actually need is for a bed, not the gate.

For the big four the Park Service flagged this summer — Arches, Glacier, Rocky, and Yosemite — the through-line is that each park sets its own approach, and parking-capacity closures can still happen on the busiest days even where no reservation is required.

## The change that catches international visitors

Two policy shifts this year hit diaspora travelers specifically. First, the National Park Service rewrote its **fee-free day calendar**: Martin Luther King Jr. Day and Juneteenth are out; added in their place are a July 3–5 Independence Day window, the 25 August NPS birthday, and several others. Second — and this is the one to flag for visiting relatives — **starting in 2026, free-admission days apply only to US citizens and residents.** A grandparent visiting on an Indian passport and a tourist visa will pay the entrance fee even on a designated free day. For most trips the smart move is the **America the Beautiful annual pass** ($80), which covers a carload regardless of citizenship and pays for itself in three or four parks.

## A diaspora family's checklist

- **Book Rocky Mountain timed entry the day your dates lock.** It's the one most likely to sell out from under you.
- **Skip the Glacier reservation panic** — there isn't one in 2026 — but check vehicle-size limits if you've rented anything big.
- **Reserve lodging and campgrounds early everywhere**, especially inside Yellowstone and Yosemite. The gate may be open; the beds are not.
- **Buy the $80 annual pass** rather than counting on free days, since those no longer apply to international visitors traveling with you.
- **Build in patience.** Even reservation-free parks throttle parking at peak hours. Early-morning arrivals beat the closures.

The romance of the open American road is intact — but in 2026 the planning happens on Recreation.gov weeks before anyone gets in the car. For a family coordinating flights from India, school-out dates, and a rented minivan, the reservation calendar is now as much a part of the trip as the route itself."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
