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

delta_body = """Delta Air Lines is coming back to India, and it is doing so by renting the one thing it has never had here: a domestic network. On June 18, Delta, Air France-KLM and Virgin Atlantic signed a memorandum of understanding with IndiGo, India's largest carrier, that pairs the SkyTeam transatlantic machine with the airline that flies roughly 60% of India's domestic seats. Delta also confirmed it will resume nonstop service between Atlanta and Delhi, subject to government approval, with a start date to be announced later. It would be Delta's first flight to India since it dropped New York–Mumbai in 2020.

For the U.S. diaspora, this is less about the single Atlanta route and more about what sits behind it. The deal is built around codesharing: IndiGo's "6E" code will go on the long-haul flights the three SkyTeam partners operate from India to Amsterdam, Paris, Manchester and London Heathrow, and the partners will sell IndiGo's onward flights to more than 75 Indian cities. Once the commercial contracts and regulatory steps clear, a family in Atlanta or Detroit will be able to book one ticket to Kochi, Ahmedabad, Pune or Jaipur with aligned baggage rules, instead of stitching together a Gulf carrier and a separate domestic hop.

**The Gulf-carrier problem this is meant to solve**

For two decades, the U.S.–India market has effectively been run out of Doha, Dubai and Abu Dhabi. Emirates, Qatar Airways and Etihad built their entire model on one-stop service that drops NRIs into a dozen Indian cities, and Delta — with no Indian feed of its own — simply could not compete for the Hyderabad or Kochi passenger. The Jet Airways partnership that was supposed to fix that collapsed in 2019 when the airline went under.

IndiGo is the more durable bet. It is the only Indian carrier with a genuinely national network, and it has spent the past two years repositioning from a domestic budget airline into an international one: business-class cabins, six wet-leased Boeing 787s, and a firm order for 30 Airbus A350-900s with options for 70 more. As those widebodies arrive, the cooperation with Delta, Air France-KLM and Virgin Atlantic is meant to deepen into coordinated schedules, shared loyalty benefits and baggage interlining.

**What the diaspora actually gets — and when**

The honest answer on the Atlanta–Delhi flight is "not yet." Delta will operate it on its own metal, but it has not named a launch date, and the route still needs clearance. The retirement of its Boeing 777-200LRs and the closure of Russian airspace to U.S. carriers — which forces longer southern routings — are part of why a direct U.S.–India flight has been hard for American airlines to sustain. Industry analysts note Delta will not make Atlanta–Delhi work on local Atlanta demand alone; it is banking on double-connecting traffic feeding in over its hub.

The codeshare layer, by contrast, is the part that will reach the most NRIs first. The expectation is that IndiGo's code lands on the SkyTeam carriers' India–Europe flights, with through-ticketing and aligned baggage, before any new metal flies. For the roughly 5.4 million people of Indian origin in the United States, the practical upshot is a third credible way home — alongside the Gulf hubs and Air India's own expanding U.S. network — and crucially, one routed through Amsterdam, Paris or London rather than the Middle East.

There are caveats worth keeping. KLM's new Amsterdam–Hyderabad route, launched in September 2025, already shows the template, with Air France-KLM selling IndiGo flights to two dozen points beyond Hyderabad. But service standards differ across Delta, Air France, KLM and Virgin even within the existing joint venture, so a "consistent experience" across a four-airline patchwork is aspirational for now. And every piece of this — the codeshares, the Atlanta route, the loyalty tie-ups — is explicitly subject to regulatory approval.

**What to watch**

For NRIs planning trips over the next year, the signal to track is when IndiGo's code actually appears on Delta, KLM, Air France and Virgin Atlantic flights, and when Delta puts a date on Atlanta–Delhi. Until then, the Gulf carriers and Air India remain the workhorses of the route. But the direction of travel is clear: the U.S.–India market, long dominated by the Gulf, is being pulled back toward the transatlantic alliances — and IndiGo has made itself the partner everyone wants."""

visa_body = """A U.S. visa stamped in your passport is no longer the end of the screening — it is the beginning. The U.S. Embassy in India spelled that out bluntly on June 14, posting on X that "U.S. visa screening does not stop after a visa is issued. We continuously check visa holders to ensure they follow all U.S. laws and immigration rules — and we will revoke their visas and deport them if they don't." For the millions of Indians on student, work and visitor visas, the message is that the document is a privilege subject to continuous review, not a settled right.

The warning was the latest in a string of advisories from the Embassy over four weeks, and it lands on a community that holds a disproportionate share of U.S. non-immigrant visas. Indians make up the largest cohort of H-1B workers and one of the largest groups of international students in the country. The Embassy's language was pointed at exactly those categories — F-1 students, J-1 exchange visitors, H-1B workers and B-1/B-2 visitors — and it listed the kinds of conduct that can now trigger revocation: overstaying, working without authorization, drug use, skipping classes without notifying the school, and in some readings even participation in protests.

**Continuous vetting, in plain terms**

What has changed is not the law but the posture. The State Department has made clear it is using "all available information" to vet visa holders on an ongoing basis, not just at the consular window. That builds on a rule, announced last month, requiring applicants for F, M and J visas to set all their personal social media accounts to "public" so consular officers can review them. Since 2019, applicants have already had to list every social media handle used in the past five years on the DS-160 form, and they certify that information is accurate when they sign.

The screening expansion has had visible operational fallout in India. Consulates in Chennai, Hyderabad, Mumbai and New Delhi have been rescheduling H-1B and H-4 interviews months later — in some cases from mid-December into April — to absorb the extra vetting workload. New applicants are being booked as far as 10 to 12 months out. A separate policy shift now pushes most applicants to apply in their country of citizenship or residence, closing the old workaround of grabbing a faster appointment at a third-country consulate.

**India is not banned — but it is not exempt from scrutiny**

It is worth stating clearly what this is not. India is not on the 2026 travel-ban lists; the Embassy has confirmed it continues to process B-1/B-2, H-1B and F-1 applications across all categories. The Presidential Proclamation restricting entry from dozens of countries, and the immigrant-visa pause affecting others, do not include India. The U.S. still treats India as a high-cooperation partner.

But "not banned" is not the same as "unaffected." The continuous-vetting regime applies to everyone, and Indians — by sheer volume of visas held — feel it most. The practical risk for a diaspora family is no longer just getting the visa; it is staying inside the lines for the full duration of the stay, because a problem can now surface long after the stamp.

**What NRIs and their families should do**

A few concrete steps follow from the advisories. Students should treat full-time enrollment and school reporting requirements as non-negotiable, and notify their designated school official before any change in status or course load. Workers on H-1B should keep their employment consistent with the terms of the petition. Anyone applying should assume their public social media footprint will be read, and that private settings on an F, M or J application can now be a problem in themselves. And families planning visits or interviews should build in long lead times — booking appointments close to a year out is now realistic, and confirmed slots can still be moved.

The underlying shift is cultural as much as procedural. For a generation of NRIs who grew up treating the U.S. visa as a finish line, the Embassy is asking them to think of it as a standing condition — one the U.S. government has now said, repeatedly, it intends to keep checking."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Delta Is Coming Back to India by Renting IndiGo's Map — and the Diaspora's Route Home Is Shifting Off the Gulf",
        "subheadline": "A four-airline pact with IndiGo, Air France-KLM and Virgin Atlantic — plus a planned Atlanta-Delhi nonstop — gives NRIs a transatlantic way home that bypasses Dubai and Doha.",
        "slug": make_slug("delta-indigo-skyteam-partnership-atlanta-delhi-nri-route"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The IndiGo codeshare gives the 5.4 million Indian Americans a third credible way home, routing onward flights to 75+ Indian cities through Amsterdam, Paris and London instead of the Gulf hubs that have long dominated the US-India market.",
        "tags": ["travel", "airlines", "delta", "indigo", "us-india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/delta-air-lines-returns-to-india-with-indigo-led-global-partnership/"},
            {"name": "Delta News Hub", "url": "https://news.delta.com/"},
            {"name": "View from the Wing", "url": "https://viewfromthewing.com/"},
            {"name": "AirlineGeeks", "url": "https://airlinegeeks.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/IndiGo_VT-IJB_A320neo_Mumbai_Apr22_R16_05934.jpg/1280px-IndiGo_VT-IJB_A320neo_Mumbai_Apr22_R16_05934.jpg",
        "image_caption": "An IndiGo Airbus A320neo at Mumbai; IndiGo's domestic network anchors the new Delta-led partnership.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": delta_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Visa Stamp Isn't the Finish Line Anymore: US Embassy Tells Indians Screening Never Stops",
        "subheadline": "Washington's continuous-vetting posture lands hardest on the diaspora that holds the most US student and work visas — and the rules now follow you for the whole stay.",
        "slug": make_slug("us-embassy-india-continuous-visa-screening-warning-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the largest share of US H-1B and student visas, so the State Department's continuous-vetting posture - and the social-media and interview-delay rules behind it - affects more NRI families than any other community.",
        "tags": ["travel", "visa", "immigration", "us-india", "students"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/us-embassy-in-india-warns-visa-holders-that-visa-screening-continues-even-after-visa-is-granted/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/"},
            {"name": "Fisher Phillips", "url": "https://www.fisherphillips.com/"},
            {"name": "Mondaq / Greenberg Traurig", "url": "https://www.mondaq.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/United_States_Passport_Visa_Pages.jpg/1280px-United_States_Passport_Visa_Pages.jpg",
        "image_caption": "Visa pages inside a United States passport; US screening of visa holders now continues after issuance.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": visa_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
