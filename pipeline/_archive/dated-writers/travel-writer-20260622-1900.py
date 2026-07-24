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
        "headline": "India Is About to Make Its Tourist Visa Last a Year With Unlimited Entries \u2014 a Gift for the OCI-less Spouse",
        "subheadline": "New e-Visa rules would stretch the e-Tourist Visa to 12 months and drop the entry cap, easing the paperwork grind for mixed-status NRI families who shuttle between the US and India.",
        "slug": make_slug("india-evisa-liberalization-one-year-multiple-entry-nri-spouse-oci"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Foreign-passport spouses and grown children of NRIs who don't qualify for an OCI card currently re-apply for an India e-Visa every trip; a one-year, multiple-entry tourist visa removes that repeat cost and wait for families who go back often.",
        "tags": ["travel", "visa", "india", "e-visa", "nri", "oci"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/electronic-visa-rules-for-tourists-and-business-visitors-to-be-relaxed.html"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/india-e-tourist-visa/"},
            {"name": "Consulate General of India, New York", "url": "https://indiainnewyork.gov.in"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An open passport filled with international travel stamps at an airport.",
        "image_attribution": "Pexels",
        "body": """India's Ministry of Tourism and Ministry of Home Affairs have signed off on a set of relaxed e-Visa rules that, once they reach the application portal, will reshape how the foreign-passport relatives of Indian Americans visit the country. The headline change: the e-Tourist Visa will be granted for **up to one year**, up from the current 60 days, and it will allow **multiple entries** instead of just two.

For the diaspora, this is not abstract. It speaks directly to a quiet logistical headache in mixed-status families.

## What is actually changing

Under the new framework, the e-Tourist Visa stretches from a 60-day document to a 12-month one, with the two-entry cap lifted entirely. Travelers still cannot overstay their per-visit consecutive limit \u2014 180 days for US, UK, Japanese and Canadian nationals, 90 days for most others \u2014 but they can now come and go across a full year on a single approval.

The e-Business Visa gets a parallel upgrade: its consecutive-stay window grows to 180 days from 60, and it becomes usable multiple times in a calendar year rather than the old three-visit ceiling.

There is an important caveat. As of the announcement, the changes had **not yet been implemented in the online portal**, and the government has not given a start date. The policy is approved; the plumbing is not switched on. Anyone applying today still gets the existing terms.

## Why this lands squarely on the diaspora

The Overseas Citizen of India (OCI) card already solves the repeat-visa problem \u2014 for people who qualify for it. The gap is in the rest of the household.

A US-born spouse who never took Indian citizenship, an American son-in-law, the adult children of naturalized parents who let their own claim lapse \u2014 these travelers are not OCI-eligible and must apply for an India tourist visa every time the family flies back. Under today's rules, a 60-day, two-entry e-Visa often means a fresh application for each trip home, each with its own fee, photo upload and 24-to-72-hour processing wait.

A one-year, multiple-entry tourist visa collapses that into a single annual filing. A family that goes to India for a winter wedding, returns for a summer visit, and dips back for a parent's medical emergency would, under the new rules, do it all on one approval. For the roughly 5 million people of Indian origin in the United States \u2014 many in exactly these blended-citizenship households \u2014 that is real money and real friction removed.

## The fee math still favors frequent flyers

Even before this change, India's e-Tourist Visa fee schedule rewarded people who travel often. The current structure runs **$25 for a 30-day visa** (July to March), dropping to **$10 in the April-to-June off-season**, **$40 for a one-year visa**, and **$80 to $200 for a five-year visa** depending on nationality.

The five-year e-Tourist Visa, already on the books, remains the better deal for diaspora families who know they will keep coming back \u2014 it survives passport-stamp pages and avoids annual re-filing altogether. The newly liberalized one-year visa slots in neatly for those who want flexibility without committing to the longer document, or who are testing how often they will realistically return.

## What to do now

The practical advice is to wait and watch the portal rather than rush. Because the rules are approved but not live, applying today simply gets you the old 60-day terms. Travelers with trips booked in the next few weeks should apply as usual; those with flexible plans later in the year may want to hold until the longer validity appears at indianvisaonline.gov.in.

Two standing reminders survive the change. The passport must carry at least six months of validity from the date of arrival and two blank pages, and the e-Visa application should only ever be filed on the official government site \u2014 the consulates repeatedly warn against agents who promise "express" approvals for a fee.

It is a modest bureaucratic tweak on paper. But for the American relatives who marry, are born into, or grow up around Indian families, it removes one of the last recurring hassles of going home.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is Quietly Wiring India to Nairobi, Jakarta and the Caucasus \u2014 174 New Weekly Flights by September",
        "subheadline": "India's largest airline is adding six international destinations across Africa, Southeast Asia and Central Asia, opening one-stop paths home that the diaspora has long had to cobble together through the Gulf.",
        "slug": make_slug("indigo-six-new-international-destinations-nairobi-jakarta-caucasus-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Indians settled in East Africa and the new wave of NRIs vacationing in Central Asia gain direct IndiGo links to Mumbai and Delhi, cutting out the Gulf-hub layovers that have defined those journeys for decades.",
        "tags": ["travel", "airlines", "indigo", "india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Airways Magazine", "url": "https://www.airwaysmag.com/legacy-posts/indigo-international-expansion-plans"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/indigo-indias-largest-airline-international-destinations-domestic-destinations-amsterdam-manchester-network-flights/amp-11748594837719.html"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1280px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo, the narrowbody jet powering the airline's short- and medium-haul international push.",
        "image_attribution": "Wikimedia Commons",
        "body": """While the aviation press has fixated on IndiGo's headline-grabbing leap into Europe \u2014 Manchester, Amsterdam, London \u2014 India's largest carrier has been quietly stitching together a second, less glamorous web of routes that may matter more to specific corners of the diaspora. Between June and September, IndiGo is adding **six new international destinations** and roughly **174 new weekly flights**, reaching into East Africa, Southeast Asia and the Caucasus.

These are not vanity routes. Each one targets a real travel pattern that, until now, has run through a Gulf connection.

## Where the new flights go

From **Mumbai**, IndiGo will launch direct service to **Nairobi, Kenya** and **Jakarta, Indonesia** in late July and early August. From **Delhi**, August brings new links to **Tbilisi, Georgia** (three times a week) and **Baku, Azerbaijan** (four times a week). September adds **Tashkent, Uzbekistan** (four times a week) and **Almaty, Kazakhstan** (three times a week).

Final schedules and ticket sales open as regulatory approvals clear, the airline said. The flying will lean on IndiGo's single-aisle fleet and its growing roster of wet-leased widebodies, the same playbook powering its longer European pushes.

## The East Africa angle is the sleeper story

India and East Africa share one of the world's oldest diaspora ties. Kenya, Tanzania and Uganda are home to long-established communities of Indian origin \u2014 families that have lived there for generations and still travel back to Gujarat, Punjab and Goa for weddings, funerals and roots trips.

For decades that journey has meant a layover in Dubai, Doha or Addis Ababa. A nonstop **Mumbai-Nairobi** link gives the East African Indian community, and the Indian expatriates working across Kenya's tech and trade sectors, a direct artery to the homeland's commercial capital. It also opens a cleaner path for Indian Americans with relatives split between the US and East Africa, who currently triangulate through multiple hubs.

## Central Asia is chasing a new diaspora travel trend

The Tbilisi, Baku, Tashkent and Almaty additions track a different phenomenon: the explosion of Indian leisure travel to the Caucasus and Central Asia. These destinations have become budget-friendly, visa-light alternatives to Europe for a young, increasingly mobile Indian middle class \u2014 Georgia and Azerbaijan in particular have seen double-digit growth in Indian arrivals.

For the US-based diaspora, the relevance is indirect but real. Many Indian Americans now route family vacations through India, tacking on a short regional trip \u2014 and a direct Delhi-Almaty or Delhi-Tbilisi flight turns a complicated multi-stop itinerary into a simple add-on. The same hubs feed onward connections for relatives traveling between the US, India and the energy-sector economies of Central Asia, where a growing number of Indian engineers and oil-and-gas professionals are posted.

There is a visa logic underneath the route map, too. Georgia waives its visa requirement for Indians holding a valid US, UK, Schengen or GCC visa or residence permit, and Azerbaijan and the Central Asian states run quick, cheap e-Visa systems. That means a green-card-holding NRI can clear the entry hurdle for these destinations with paperwork they already carry \u2014 making a same-trip detour from India genuinely frictionless rather than a fresh bureaucratic project.

## Jakarta plugs a Southeast Asia gap

The **Mumbai-Jakarta** route fills an obvious hole. Indonesia is a major business and leisure market for Indians, and direct capacity between the two countries has lagged demand. For the diaspora professional shuttling between US tech offices, an Indian base and Southeast Asian operations, more nonstop options out of Mumbai shorten an already-punishing travel calendar.

## What it signals

Taken together, the six routes show IndiGo doing what Air India's pullback on some international flying has left open: aggressively claiming the medium-haul international market with narrowbody and wet-leased jets. The carrier has said it intends to push its international destination count toward 50, and these additions are the connective tissue, not the showpiece.

For NRIs, the lesson is to watch the second tier of route announcements as closely as the marquee Europe and US news. The flight that actually fixes your trip home may be the unglamorous one to Nairobi or Almaty, not the one to Heathrow.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"\u2705 {art['slug']}")
    except Exception as e:
        print(f"\u274c {art['slug']}: {e}")
