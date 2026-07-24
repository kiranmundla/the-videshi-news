#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-05-30 18:00 UTC run."""
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
        "headline": "Air India's Maharaja Lounge Just Opened at SFO — and Bay Area NRIs Finally Have a Lounge Worth Arriving Early For",
        "subheadline": "The airline's first signature lounge outside India brings Vada Pav, Parle-G biscuits, and a speakeasy bar to the International Terminal. Here's what you need to know.",
        "slug": make_slug("air-india-maharaja-lounge-sfo-bay-area-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "SFO is the primary gateway for the 700,000+ Indian Americans in the Bay Area. Air India's new Maharaja Lounge — the carrier's first outside India — transforms the pre-flight experience on the SFO-Delhi route, the most heavily traveled NRI corridor on the West Coast. For NRIs who've endured generic contract lounges for years, this is Air India's clearest signal yet that it's investing in the diaspora routes that matter most.",
        "tags": ["travel", "airlines", "air-india", "airport-lounge", "sfo", "bay-area"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Air India Official Press Release", "url": "https://airindia.com/in/en/air-india-newsroom-press-releases/air-india-debuts-its-first-signature-maharaja-lounge-at-san-francisco-expanding-global-premium-offering.html"},
            {"name": "Live From A Lounge (Review)", "url": "https://livefromalounge.com/air-india-maharaja-lounge-san-francisco-international-airport-sfo/"},
            {"name": "The Points Guy", "url": "https://thepointsguy.com/news/air-india-maharaja-lounge-sfo/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-opens-first-overseas-maharaja-lounge-at-san-francisco-airport/article69622476.ece"},
            {"name": "India-West", "url": "https://www.indiawest.com/news/global_indian/air-india-opens-maharaja-lounge-at-san-francisco-airport/article_bda03210-3873-11f0-9c21-3b3f3e9c6e1e.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/San_Francisco_International_Airport_-_aerial_photo.jpg",
        "body": """Air India has been talking up its transformation for years. New planes, new livery, new seats — the usual airline-reinvention playbook. But the Maharaja Lounge at San Francisco International Airport, which opened to passengers on May 23, is the first time the airline's ambitions have been physically visible on American soil. And for the hundreds of thousands of Indian Americans who fly out of SFO each year, it changes the pre-flight calculus entirely.

## What You Walk Into

The lounge sits near Gate A1 in SFO's International Terminal, up one level from the main concourse. At 3,300 square feet with seating for about 80 guests, it's compact by global lounge standards — but the design punches well above its footprint.

Hirsch Bedner Associates, a hospitality design firm better known for five-star hotel interiors, built the space around what Air India calls "modern luxury with an Indian heart." The walls carry custom art installations made from upcycled Boeing 747 components — one piece repurposes engine parts into a lotus sculpture, another embeds semiconductor circuitry within recycled fuselage material, a nod to the tech corridor between Silicon Valley and Bengaluru. A Golden Gate Bridge artwork rendered in traditional Indian bindi art is the kind of design detail that rewards a second look.

The centrepiece is the Aviator's Bar, a speakeasy-style space paying homage to JRD Tata's 1932 inaugural flight. The ceiling mimics the propeller shaft of the original Puss Moth aircraft, and vintage Air India photographs line the walls — from the first Mumbai-London international flight in 1948 to the modern A350 fleet. The bar serves a signature gin cocktail called "Limitless" alongside a San Francisco-exclusive called the "Golden Gate." Kingfisher beer is on tap for those who want something familiar.

## The Food Is the Point

Most airport lounges treat food as an afterthought — reheated trays of something vaguely Mediterranean. The Maharaja Lounge takes the opposite approach. An Indian chef runs the kitchen, and the food is unapologetically spiced for the Indian palate.

Breakfast brings stuffed paranthas, Parsi akuri, and upma. Through the day, the menu rotates through vada pav, tokri chaat from Lucknow, chicken lollipops, and gajar halwa tarts. Main courses include chicken tikka masala and dal bukhara with naan. The chai comes with Parle-G biscuits and suji rusk — the kind of detail that turns a lounge visit into a homecoming before you've even boarded.

Air India has said it will keep the food genuinely spiced rather than toning it down for a broader audience. That commitment alone distinguishes it from every other airline lounge at SFO.

## Who Gets In

Access is limited to Air India First and Business Class passengers, Maharaja Club Platinum and Gold members, and eligible Star Alliance Gold members. The lounge also welcomes premium passengers on Star Alliance partner airlines — so if you're flying Singapore Airlines or United Polaris, you may qualify depending on your fare class.

A separate private section behind a "Private" sign serves First Class passengers exclusively, with seating for eight, à la carte dining, a premium whisky selection, and archival Air India artwork.

## Why It Matters to Bay Area NRIs

SFO is Air India's primary West Coast gateway. Before the Middle East-related cutbacks, the airline operated 17 weekly flights from San Francisco; it currently runs seven, all on the SFO-Delhi nonstop. That single route carries an outsized share of Bay Area's Indian American traffic — tech workers heading home for weddings, families making the annual Diwali pilgrimage, parents visiting children in Hyderabad and Bengaluru.

Until now, Air India passengers at SFO relied on generic contract lounges shared with dozens of airlines. The United Polaris Lounge recently tightened its access policies, excluding most partner airline passengers. The Maharaja Lounge fills that gap with something Air India passengers haven't had before: a branded, premium space designed specifically for them.

The lounge also signals what's coming next. Air India has hinted at new aircraft on the SFO route — it remains the carrier's monopoly nonstop to Delhi from the Bay Area — and the lounge is positioned as an investment in that future. Additional Maharaja Lounges are planned for Dubai and London Heathrow.

## The Bigger Picture

The Maharaja Lounge is the second in Air India's signature lounge series, following the flagship opening at Delhi's Terminal 3 in February 2026. Both were designed by HBA and share a consistent design language — the same nesting chairs with integrated power and lumbar support, the same Aviator's Bar concept, the same rotating Indian menu philosophy.

Air India CEO Campbell Wilson has framed the lounges as part of the airline's push to "introduce a new standard of travel experiences" in North America. For an airline that lost more than $2 billion last fiscal year, investing in premium ground infrastructure is a bet that the transformation will stick — and that the diaspora routes, where loyalty runs deepest, are worth fighting for.

For Bay Area NRIs who have spent years in contract lounges eating bland sandwiches before a 16-hour flight home, a lounge with properly spiced dal and Parle-G biscuits might be the most convincing proof yet that Air India's reinvention is real."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Flying to India This Summer? The Paper Arrival Card Is Dead — Here's What Replaced It",
        "subheadline": "India's mandatory e-Arrival Card went fully digital in April 2026. NRIs who don't fill it out before landing could face longer queues at immigration.",
        "slug": make_slug("india-e-arrival-card-mandatory-nri-guide-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "While Indian passport holders are exempt from the e-Arrival Card (they use separate immigration lanes), their non-Indian family members, OCI card holders traveling on foreign passports, and visiting friends are all affected. With peak NRI summer travel season starting, the timing couldn't be more relevant — families heading to India in June-August need to ensure every foreign-passport holder in their group has submitted the form 72 hours before arrival.",
        "tags": ["travel", "india", "immigration", "visa", "nri", "e-arrival-card"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelObiz", "url": "https://travelobiz.com/travelling-to-india-e-arrival-card-becomes-mandatory-from-april-2026/"},
            {"name": "Bureau of Immigration, India", "url": "https://indianvisaonline.gov.in/earrival/"},
            {"name": "Consulate General of India, St. Petersburg", "url": "https://cgispburg.gov.in/"},
            {"name": "Travel Noire", "url": "https://travelnoire.com/india-e-arrival-card-guide"},
            {"name": "Connecting Travel", "url": "https://connectingtravel.com/news/india-simplifies-entry-for-gcc-travellers-with-new-e-card"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32060712/pexels-photo-32060712.jpeg",
        "body": """If you're flying to India this summer and haven't heard of the e-Arrival Card, you're about to have a problem at immigration.

India's Bureau of Immigration quietly retired the paper disembarkation card — that crumpled form flight attendants used to hand out with landing cards and pens — and replaced it with a mandatory digital version. The e-Arrival Card has been available since October 2025, but as of April 1, 2026, paper forms are no longer accepted at Delhi's Indira Gandhi International Airport. Other major airports are following suit.

For NRI families heading to India during the June-August peak season, this is the kind of small bureaucratic change that can turn a 20-minute immigration queue into an hour-long ordeal if you're caught unaware.

## Who Needs to Fill It Out

The e-Arrival Card applies to **all foreign nationals** entering India — regardless of visa type. That includes tourists, business visitors, students, medical travellers, and conference attendees.

**Indian passport holders are exempt.** If you're an NRI travelling on an Indian passport, you clear immigration through separate lanes and don't need the form. But here's where it gets relevant for diaspora families: your American-born children travelling on US passports, your spouse on a foreign passport, your visiting in-laws from Canada, your college friend flying in from London — anyone entering India on a non-Indian passport must submit the form.

OCI card holders who travel on foreign passports are also covered. The OCI card facilitates your visa-free entry, but the e-Arrival Card is a separate immigration data requirement. Don't assume your OCI exempts you from this.

## What It Asks

The form is straightforward and mirrors the information that was on the old paper card:

- Full name, nationality, passport number
- Date and port of arrival in India
- Purpose of visit (tourism, business, medical, employment, etc.)
- Countries visited in the last six days
- Address in India during the stay
- Email address and phone number
- Emergency contact details

The key difference from the paper version: it must be submitted **up to 72 hours before arrival** via the official portal at [indianvisaonline.gov.in/earrival](https://indianvisaonline.gov.in/earrival) or through the "Indian Visa Su-Swagatam" mobile app, available on both Android and iOS.

Once submitted, travellers receive a digital copy they can show at immigration if asked. No documents need to be uploaded — the form is purely informational. It takes about five minutes to complete.

## Why India Made This Change

The Bureau of Immigration frames it as a modernisation move: fewer paper forms, shorter queues, faster processing. India is following a well-worn path — the UK, Singapore, Thailand, Taiwan, and Indonesia all already use similar digital entry systems.

The practical reality is that immigration counters at Delhi, Mumbai, and Bengaluru airports have been congested for years, especially during peak NRI travel windows. The paper form was an analogue bottleneck in an increasingly digital airport experience. Eliminating it and collecting data in advance allows immigration officers to pre-screen arrivals and spend less time at the counter.

Delhi Airport (DIAL) has described the new system as "a seamless, paperless arrival experience for foreign travellers," adding that passengers should "submit the form and breeze through immigration."

## What Happens If You Don't Submit It

India hasn't published a hard policy on denial of entry for non-submission — after all, immigration officers have discretion. But passengers who arrive without a completed e-Arrival Card should expect to be directed to a separate queue where they'll fill out the form on-site, likely on an airport kiosk or their phone. During peak hours in monsoon season, that could mean significant additional wait time.

Emirates, which operates dozens of weekly flights to India, has already issued advisories to passengers that "those who do not submit the e-Arrival Card in advance may face longer waiting times at immigration."

## The NRI Summer Checklist

With the busiest India travel season about to begin, here's the practical takeaway:

**Before you fly:**
1. Visit [indianvisaonline.gov.in/earrival](https://indianvisaonline.gov.in/earrival) or download the Indian Visa Su-Swagatam app
2. Complete the form for every family member travelling on a non-Indian passport
3. Submit it within 72 hours of your arrival — not departure, arrival
4. Save the digital confirmation on your phone
5. Indian passport holders can skip this step entirely

**Common mistakes to avoid:**
- Assuming your OCI card covers you (it doesn't exempt you from the e-Arrival Card)
- Forgetting to fill it out for children on US/UK/Canadian passports
- Waiting until you're on the plane — airport Wi-Fi at the arrival gate is not guaranteed

## The Broader Context

India has been steadily digitising its travel infrastructure. The Fast-Track Immigration Trusted Traveller Programme (FTI-TTP) is now live at 31 airports for Indian passport holders. The Digi Yatra biometric boarding system is expanding. And the new e-Arrival Card slots into a broader strategy to reduce friction at India's increasingly busy international terminals.

For NRIs, these changes are a net positive — faster immigration, less paperwork, more predictable airport experiences. But they do require staying current on the rules. The paper form your parents filled out for decades is gone. Five minutes on a website before you fly is the new cost of entry."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
