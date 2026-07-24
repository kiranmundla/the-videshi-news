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
        "headline": "Etihad Is Ordering Widebody Jets and Restoring Full Capacity — Here's What That Means for NRIs Routing Through Abu Dhabi",
        "subheadline": "The Abu Dhabi carrier expects to fly 8% more than pre-war levels by mid-June, has ordered double-digit widebody aircraft, and now offers lie-flat business class on every Mumbai and Delhi flight.",
        "slug": make_slug("etihad-widebody-expansion-abu-dhabi-nri-india"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Etihad serves 11 Indian cities and is a critical transit hub for NRIs connecting to the US, UK, and Europe via Abu Dhabi. The capacity restoration and premium cabin upgrades directly improve the quality and reliability of one of the most popular routing options for Indian Americans flying home.",
        "tags": ["travel", "airlines", "etihad", "abu-dhabi", "india-flights", "widebody"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/etihad-airways-orders-widebody-planes-sees-return-pre-war-capacity-june-2026-06-07/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3369101-etihad-airways-expands-fleet-amid-growing-demand"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/etihad-airways-to-lift-capacity-above-pre-war-levels-finalize-new-widebody-order/"},
            {"name": "Travelobiz", "url": "https://www.travelobiz.com/etihad-adds-lie-flat-seats-on-all-mumbai-and-new-delhi-flights-from-may-2026/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Abu_Dhabi_%28UAE%29%2C_Zayed_International_Airport%2C_Terminal_A_%2803%29.jpg/1280px-Abu_Dhabi_%28UAE%29%2C_Zayed_International_Airport%2C_Terminal_A_%2803%29.jpg",
        "image_caption": "Abu Dhabi's Zayed International Airport Terminal A, Etihad's expanding global hub",
        "image_attribution": "Wikimedia Commons",
        "body": """For months, the question hanging over every NRI who routes through Abu Dhabi has been simple: when will things get back to normal? The answer, according to Etihad CEO Antonoaldo Neves, is now.

Speaking at the IATA annual meeting in Rio de Janeiro on June 7, Neves confirmed that Etihad expects to be flying approximately 8% more capacity than it did before the Iran conflict by June 15. The carrier is also finalizing a new order for widebody aircraft "in the double digits," he told Reuters — a bet on long-haul demand that signals the airline sees this recovery as durable, not temporary.

## From 63% to 108%

The numbers tell the story of how fast things have moved. In early April, Etihad was operating at roughly 63% of its pre-war schedule — about 212 daily flights compared to 334 before the U.S.-Israeli war with Iran disrupted Middle Eastern airspace in late February. Abu Dhabi fared better than Dubai during the conflict, absorbing far less direct operational damage, and that geographic luck has accelerated the carrier's comeback.

The airline had already ordered 32 Airbus widebodies in November 2025 and posted a record AED 2.6 billion (roughly $700 million) profit for 2025, with an 8.4% net margin — more than double the global airline industry average. Fitch upgraded its credit to AA- with a stable outlook. Neves is now doubling down, prioritizing full planes over cost cuts.

"The biggest cost we have is an empty plane," he said. "So the way I cut cost is I don't have empty planes."

## What This Means on India Routes

For the 3+ million Indian Americans who rely on Gulf carriers as their primary routing option to India, Etihad's expansion has immediate implications.

Since May 1, every Etihad flight between Abu Dhabi and Mumbai, and Abu Dhabi and New Delhi, now features lie-flat business class seats. Both cities are served four times daily — two flights on the airline's new Airbus A321LR narrowbodies (which still offer full lie-flat business) and two on widebody aircraft including the Boeing 787, 777, and Airbus A350.

That's a material upgrade. Until recently, some India flights used narrowbody configurations without premium flat beds, forcing business class passengers into angled seats on eight-hour overnight flights. The change means every premium passenger on these routes now gets a consistent product — direct aisle access, fully flat beds, and upgraded dining — regardless of which of the four daily flights they book.

Etihad currently serves 11 destinations across India: Delhi, Mumbai, Bengaluru, Hyderabad, Ahmedabad, Chennai, Kochi, Kolkata, Thiruvananthapuram, Kozhikode, and Jaipur. Passengers connecting onward to London, Paris, Zurich, Geneva, New York, or Toronto through Abu Dhabi also benefit from the premium consistency across their entire journey.

## The Competitive Picture

Etihad's aggressive posture comes while Emirates, its larger neighbor, is still operating at roughly 75% of pre-war capacity. Qatar Airways has reintroduced selected international services but is scaling carefully. Air Arabia, the Sharjah-based budget carrier, resumed flights to Indian cities from UAE hubs in early June after its own operational suspension.

The broader backdrop is brutal. IATA slashed its 2026 industry profit forecast from $41 billion to $23 billion on June 8, citing the fuel shock from the Iran war. The industry's fuel bill is expected to hit $350 billion this year, up from $252 billion in 2025. Spirit Airlines collapsed in May — the first airline casualty of the conflict. IATA Director General Willie Walsh warned that more bankruptcies are likely.

Against that landscape, Etihad's expansion is a statement. The carrier has no public shareholders to answer to and no debt to service after repaying AED 2.2 billion in sukuk last October. It can afford to grow while competitors retrench.

## The NRI Takeaway

If you've been avoiding Abu Dhabi connections because of conflict-era uncertainty, the data suggests it's time to reconsider. Capacity is back, premium cabins are upgraded across the India network, and the airline's financial position is among the strongest in global aviation.

The one caveat: fares through Gulf hubs remain elevated. IATA expects airfares to stay high as capacity stays tighter than pre-war norms across the industry. NRIs booking summer or Diwali travel should lock in Abu Dhabi routings sooner rather than later — especially for business class, where the upgraded product will drive demand higher than the old configuration ever did."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Went Digital With OCI Cards — and 14 Million Overseas Indians Need to Pay Attention",
        "subheadline": "The Citizenship Amendment Rules 2026, effective May 1, replace paper applications with a fully electronic OCI system, introduce e-OCI cards stored on your phone, and tighten dual-passport rules for children.",
        "slug": make_slug("india-eoci-digital-card-citizenship-rules-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The OCI card is the single most important travel document for Indian Americans with foreign passports. The shift to e-OCI, mandatory biometric consent, and tightened dual-passport rules directly affect how every OCI-holding NRI in the US travels to and from India.",
        "tags": ["travel", "oci", "visa", "india", "nri", "immigration", "digital"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/news/india/mha-overhauls-citizenship-rules-moves-oci-applications-to-digital-platform-full-details-here-11746028024131.html"},
            {"name": "Indian Eagle", "url": "https://www.indianeagle.com/travelbeats/india-launches-digital-e-oci-know-benefits-and-how-to-apply/"},
            {"name": "VisaHQ", "url": "https://www.visahq.com/india/"},
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/government-notifies-citizenship-rules-2026-shifts-oci-applications-online/"},
            {"name": "SCC Online", "url": "https://www.scconline.com/post/2026/05/07/citizenship-amendment-rules-2026-oci-registration/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "image_caption": "An open passport with travel stamps at an airport immigration counter",
        "image_attribution": "Pexels",
        "body": """If you hold an OCI card and haven't checked the Indian government's immigration portal lately, you're behind. On April 30, India notified the Citizenship (Amendment) Rules 2026, and since May 1, the entire Overseas Citizen of India system has gone digital. The changes are the most significant overhaul of the OCI program since its inception in 2005 — and for the estimated 14 million OCI cardholders worldwide, including roughly 4.5 million in the United States, the practical implications are substantial.

## What Changed

The headline shift: all OCI applications — new registrations, renewals, re-issuances, and renunciations — must now be filed electronically through a single portal at ociservices.gov.in. Paper applications are dead. Duplicate document submissions are eliminated. And for the first time, India is issuing electronic OCI cards (e-OCI) that can be stored in a mobile wallet alongside your physical booklet.

The Home Ministry says digital processing should cut the median approval time from 60 days to roughly 15 days once the new back-office workflow is fully scaled. For NRIs who have endured months-long waits for passport-linked re-issuances — often timed badly against planned India trips — that alone would be transformative.

## The Five Changes That Matter Most

**1. e-OCI Cards Are Here**

New applicants will receive e-OCI registration on priority. Existing physical OCI cardholders will be migrated to the electronic version in phases, likely during their next re-issuance. The physical booklet remains valid even after the digital upgrade. But a word of caution from travel professionals: carry the physical card when flying until international airlines — particularly European and American carriers — update their staff training on the new system.

**2. Mandatory Biometric Consent**

Every OCI applicant must now sign a consent form opting into India's Fast Track Immigration Programme, agreeing to the collection of biometric information during registration. This data will be used for future fast-track immigration processing at Indian airports. It's opt-in in name only — the consent form is a required part of the application.

**3. No More Old Passport Requirement**

Previously, OCI cardholders who renewed their foreign passport had to carry both their current passport and the old one (whose number appeared on the OCI card) when entering India. That requirement is gone. You now need only your OCI card and your current passport. Immigration officers should have the updated guidance, though seasoned NRI travelers will want to carry the old passport for a few more months as a backup until the change is fully absorbed at every port of entry.

**4. Dual-Passport Rules Tightened for Minors**

Parents who hold both Indian and foreign passports for their children face a new restriction: a minor cannot hold an Indian passport and a foreign passport simultaneously. Families must choose one. This closes a loophole that previously allowed some families to blur their children's citizenship status, but it also creates an immediate compliance burden for NRI families who have been operating in a gray area.

**5. Online Appeals Process**

If your OCI application is rejected, you now have a formal right to challenge the decision. Appeals go to an authority "one rank higher" than the official who made the original decision, and applicants have a guaranteed right to be heard before a final ruling. It's a small but meaningful procedural safeguard.

## The Fee Landscape

OCI fees were revised effective April 1, 2026. A fresh OCI application now costs USD $275 (or ₹15,000 within India). Re-issuance tied to a passport renewal is USD $25 — a manageable cost given how frequently NRIs cycle through passport renewals. The online passport-linking update remains free.

For the many NRI families managing OCI cards for multiple family members, the cumulative cost of fresh applications adds up. A family of four applying from the US is looking at $1,100 in consular fees before VFS Global service charges.

## What You Should Do Now

If you have a pending OCI re-issuance because of a passport renewal, file it now through the new portal. The digital system is expected to process faster than the old paper pipeline, and getting ahead of the inevitable surge as awareness spreads is worth the effort.

If your children hold both an Indian passport and a foreign passport, consult with your immigration attorney about which to retain. The grace period for this situation is not well-defined in the new rules.

If you travel to India frequently, start the process of getting your biometric data into the system. The Fast Track Immigration Programme — which currently operates at major Indian airports — will become increasingly integrated with the e-OCI registry, and early registrants will likely see smoother entries as the system matures.

The physical OCI booklet isn't going away tomorrow. But the direction is clear: India wants its diaspora credentialed digitally, tracked biometrically, and processed electronically. For NRIs who have spent decades navigating a system built on paper forms, courier services, and consulate appointments, this is a genuine step forward — provided the execution matches the ambition."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
