#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-27 11:00 PDT batch"""

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


# ─────────────────────────────────────────────
# ARTICLE 1: Air India's $400M Cabin Overhaul
# ─────────────────────────────────────────────

article1_body = """Air India's fleet has been the butt of every NRI joke for two decades. Fraying seats, dead screens, lavatories that smell like 1997. The airline that once carried maharajas now carried mostly complaints.

That era is ending — fast. Air India has completed the first aircraft in a **$400 million retrofit programme** that will overhaul every widebody in its long-haul fleet, and the results are a genuine departure from everything NRIs have endured on the SFO–Delhi, JFK–Mumbai, and Newark–Bangalore corridors.

## The New Dreamliner Standard

In January 2026, Air India took delivery of its first factory-fresh Boeing 787-9 Dreamliner (registration VT-AWA) straight from Boeing's Everett production line in Washington state. This is the first of 20 new 787-9s — the opening salvo of the airline's record 470-aircraft order placed in 2023, the largest in commercial aviation history.

The new Dreamliner debuted on the Mumbai–Frankfurt route on February 1, and the interior is unrecognisable from the old Air India. Designed in collaboration with London-based JPA Design, the cabin trades the old two-class layout for a **modern three-class configuration** with 296 seats:

- **Business Class**: 30 Elevate Ascent private suites in a 1-2-1 reverse herringbone layout. Each suite has a sliding privacy door, a fully flat 79-inch bed, a 17-inch 4K QLED touchscreen, wireless charging, and a feature lamp etched in traditional *jaali* lattice patterns — a nod to Mughal heritage that actually works as a design element rather than kitsch.

- **Premium Economy**: 28 RECARO PL3530 seats in 2-3-2, with 38 inches of pitch, calf and leg rests, and 13.3-inch 4K screens. This class simply didn't exist on old Air India widebodies.

- **Economy**: 238 RECARO CL3710 seats in 3-3-3 with 31–32 inches of pitch, 11.6-inch 4K screens, and USB-C charging at every seat.

Every seat gets Bluetooth headphone pairing through the Thales AVANT Up entertainment system — the same platform used by Singapore Airlines and Cathay Pacific. And the cabin features 10 bespoke mood-lighting scenes inspired by ancient Indian *chakra* wellness traditions, developed with Tata Elxsi.

## The Retrofit: 26 Legacy Dreamliners Rebuilt

The factory-fresh jets are only half the story. Air India is simultaneously **retrofitting all 26 of its existing Boeing 787-8 Dreamliners** at Boeing's Modification Centre in Victorville, California. The first, VT-ANT, took 45 days and 12,825 manhours. Teams stripped the cabin to the bones — 475 metres of new fabric, 167 metres of synthetic leather, 169 metres of carpet, new galleys, new lavatories, a complete repaint requiring 646 litres of paint over 18 days.

The result matches the new 787-9 standard: same three-class configuration (20 Business suites, 25 Premium Economy, 205 Economy), same IFE system, same design language. For NRIs, this means the creaky old Dreamliner on your summer Delhi run will progressively be replaced by an aircraft that looks and feels brand new. Full 787 fleet rollout is expected by mid-2027.

The programme doesn't stop with Dreamliners. Air India will also retrofit **13 legacy Boeing 777-300ERs**, and its Airbus A350-900s — which already feature the new cabin — have been flying JFK and Newark routes since late 2024.

## Why NRIs Should Care (and What to Watch For)

The timing is bittersweet. Air India just posted a **record annual loss exceeding $2 billion**, battered by soaring jet fuel costs from the Iran conflict, Pakistan's airspace ban on Indian carriers (adding 60–90 minutes to every westbound flight), and a strong US dollar. The airline has cut 22% of domestic flights for June–August and trimmed international frequencies.

CEO Campbell Wilson, the Singaporean executive who architected the transformation under Tata ownership, announced he will depart within two months. His successor inherits a fleet that looks better than ever — and a balance sheet that looks worse.

For the 4.4 million Indian Americans who collectively account for billions in annual India–US airfare, the practical question is simple: **which routes get the new aircraft first?** The A350s are already on Delhi–JFK and Delhi–Newark. The new 787-9s are on Mumbai–Frankfurt and expanding. The retrofitted 787-8s will progressively replace the worst aircraft in the fleet.

Before booking your summer trip, check the aircraft type on your specific flight — Air India's booking system shows it. If it says "787-9" or "A350," you're getting the new product. If it still says "787-8" or "777-300ER" without a retrofit tag, manage expectations accordingly. The old Air India hasn't disappeared yet. But for the first time in a generation, it's actually disappearing."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Just Spent $400 Million Rebuilding Every Dreamliner — Here's What NRIs Will Actually Get",
    "subheadline": "New privacy-door business suites, 4K screens at every seat, and chakra-inspired mood lighting are rolling out across the fleet. But a record $2 billion loss and summer flight cuts cast a shadow over the transformation.",
    "slug": make_slug("air-india-400m-dreamliner-cabin-overhaul-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Air India's Dreamliners fly the exact corridors NRIs use most — SFO-DEL, JFK-BOM, EWR-BLR. The $400M retrofit means the notoriously mediocre cabin experience is being replaced with privacy-door suites and 4K screens, but the timing coincides with flight cuts and record losses that could affect service reliability.",
    "tags": ["travel", "airlines", "air-india", "aviation", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Aerospace Global News", "url": "https://aerospaceglobalnews.com/news/air-india-retrofitted-boeing-787-8-dreamliner-cabins/"},
        {"name": "Travel Daily Media", "url": "https://www.traveldailymedia.com/air-indias-b787-9-interiors-a-new-era-of-quiet-luxury-and-heritage-inspired-serenity-aloft/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/air-india-indigo-cut-domestic-capacity-new-indian-express-reports-2026-05-27/"},
        {"name": "The Points Guy", "url": "https://thepointsguy.com/news/air-india-a350-new-york-routes/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
    "body": article1_body
}


# ─────────────────────────────────────────────
# ARTICLE 2: India Ebola Travel Advisory
# ─────────────────────────────────────────────

article2_body = """India's health ministry issued a blunt directive on Sunday: avoid all non-essential travel to the Democratic Republic of Congo, Uganda, and South Sudan. The trigger is an Ebola outbreak that the World Health Organization declared a **Public Health Emergency of International Concern** on May 17 — its highest alarm level — and one that carries particular weight for Indian Americans with family, business, or transit ties to East Africa.

## The Outbreak: Bundibugyo Strain, No Vaccine

This is not the more familiar Zaire species of Ebola that ravaged West Africa in 2014. The current outbreak involves the **Bundibugyo virus**, a rarer species first identified in western Uganda in 2007. It causes the same severe viral haemorrhagic fever — but unlike the Zaire strain, there is no approved vaccine and no specific treatment.

As of May 21, the DRC alone has recorded **746 suspected cases and 176 deaths**. Combined with Uganda, where imported cases have surfaced in Kampala, there are 85 laboratory-confirmed cases and 10 confirmed deaths. South Sudan has been flagged as a high-risk zone for cross-border transmission. The Africa Centre for Disease Control and Prevention has declared the situation a public health emergency of continental security.

The mortality rate exceeds 20%, and the virus spreads through direct contact with blood, body fluids, or contaminated surfaces. A planned global summit in India was cancelled outright because of the outbreak — an indication of how seriously New Delhi is taking the risk.

## What's Changed at Indian Airports

India has not recorded a single case. But the Ministry of Health is not waiting for one. Enhanced surveillance protocols have been activated at all international entry points, with specific focus on travellers arriving from DRC, Uganda, South Sudan, and transit hubs that connect to the outbreak zone.

The measures include:

- **Thermal screening** and mandatory self-declaration health forms for passengers arriving from affected regions
- Strengthened quarantine protocols and hospital readiness plans across all states
- Standard operating procedures distributed to every state and union territory health department
- Specific readiness escalation in **Andhra Pradesh, Tamil Nadu, and Kerala**, states with significant international transit traffic

Union health secretary Punya Salila Srivastava chaired a high-level review with health secretaries of all states, emphasising coordinated domestic surveillance and rapid reporting.

## Why This Matters to the Indian Diaspora

East Africa is home to one of the oldest and most commercially active Indian diaspora communities in the world. Uganda alone has roughly **30,000 people of Indian origin**, many of them descendants of railway-era migrants — a community that was expelled by Idi Amin in 1972 and has substantially rebuilt since. Kenya hosts an Indian-origin population exceeding 100,000, concentrated in Nairobi and Mombasa. Across the broader East African region, Indian business interests span IT services, manufacturing, pharmaceuticals, and commodity trading.

For NRIs in the United States, the connections are layered:

- **Direct business travel**: Indian Americans with operations in Kampala, Nairobi, or Kinshasa face immediate disruption. The advisory doesn't ban travel outright, but insurance coverage becomes complicated when a government advisory is in effect.

- **Transit routing**: Addis Ababa (Ethiopian Airlines' hub) and Nairobi (Kenya Airways) are major transit points for India-bound NRIs coming from southern and central Africa. While these hubs aren't under advisory themselves, connecting flights through Kampala or eastern DRC airspace may trigger additional screening on arrival in India.

- **Family ties**: The Indian-origin community in East Africa maintains active ties to Gujarat, Punjab, and Kerala. A family emergency in Kampala now carries a genuine health risk dimension that didn't exist three months ago.

## What NRIs Should Do Right Now

**If you have upcoming travel to DRC, Uganda, or South Sudan**: Postpone unless absolutely essential. There is no vaccine for the Bundibugyo strain, and healthcare infrastructure in the outbreak zone is under severe strain.

**If you're transiting through East African hubs**: Check whether your routing passes through affected areas. Ethiopian Airlines, Kenya Airways, and RwandAir connections are generally not under advisory, but expect enhanced screening if you've been in an affected country within the preceding 21 days (the Ebola incubation period).

**If you're arriving in India from anywhere in Africa**: Carry documentation of your itinerary. Self-declaration forms at Indian airports now ask specifically about travel to DRC, Uganda, and South Sudan. Thermal screening is standard, and symptomatic travellers — fever, body aches, unexplained bleeding — will be isolated for assessment.

**Review your travel insurance**: Most standard policies exclude travel to regions under government advisory. If you must travel, confirm your insurer's position in writing before departure.

The Indian government's advisory is open-ended — "until further notice." With no vaccine in the pipeline for the Bundibugyo strain and case counts still climbing, NRIs with East Africa connections should plan for this disruption to last months, not weeks."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Told Its Citizens to Avoid East Africa — What NRIs with Ties to Uganda and Congo Need to Know",
    "subheadline": "A Bundibugyo Ebola outbreak with no vaccine has triggered India's travel advisory and airport-level screening. For the Indian diaspora in East Africa and NRIs who transit through the region, the disruption could last months.",
    "slug": make_slug("india-ebola-advisory-east-africa-nri-uganda-congo"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "East Africa hosts one of the world's oldest Indian diaspora communities — 30K+ in Uganda, 100K+ in Kenya. NRI business interests, family ties, and transit routing through Addis Ababa and Nairobi all face disruption from India's open-ended Ebola travel advisory.",
    "tags": ["travel", "ebola", "health", "east-africa", "nri", "travel-advisory"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/india-advises-against-travel-drc-uganda-south-sudan-amid-ebola-emergency-who-bundibugyo-ebola-species-11779595207217.html"},
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/india-issues-travel-advisory-amid-growing-ebola-virus-concerns/"},
        {"name": "Curly Tales", "url": "https://www.curlytales.com/india-advises-citizens-avoid-travel-congo-uganda-south-sudan-ebola/"},
        {"name": "World Health Organization", "url": "https://www.who.int/emergencies/diseases/ebola"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32223420/pexels-photo-32223420.jpeg",
    "body": article2_body
}


# ─────────────────────────────────────────────
# Publish
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
