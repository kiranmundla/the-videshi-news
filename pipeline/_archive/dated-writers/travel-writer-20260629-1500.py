#!/usr/bin/env python3
"""Travel writer — 2026-06-29 15:00 PT run. Two articles."""

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

# ── Article 1 ───────────────────────────────────────────────────────────────

art1_body = """Air India Express will launch direct flights from Guwahati to Dubai on August 4 and to Abu Dhabi on August 7, making it the first airline to connect Northeast India with the Gulf in a single hop. The move opens a corridor that hundreds of thousands of Assamese, Manipuri, Naga, and Meghalayan workers and students in the UAE have needed for years — and that NRI families booking connecting tickets through Delhi or Kolkata have long overpaid for.

## The Route Details

The Guwahati–Dubai service will operate every Tuesday. Flight IX departs Guwahati at 12:25 pm and touches down in Dubai at 4:10 pm local time — a roughly six-hour westbound leg. The return leaves Dubai at 5:10 pm and lands back in Guwahati just past midnight. The Abu Dhabi service, every Friday, departs Guwahati at 11:30 am, arriving at 3:15 pm, with the return leg landing in Assam by 11:30 pm.

Bookings are already live on the Air India Express website and app. Launch fares start around ₹25,045 one-way for the Abu Dhabi route in August — competitive with indirect routings through Delhi on a full-service carrier, once you factor in the layover time and the second boarding pass.

## Why This Matters to NRIs

Guwahati is the gateway to all eight northeastern states, and Air India Express already operates roughly 120 weekly flights from the airport — more than from most metros. But until now, every international connection required a backtrack to Delhi, Kolkata, or Mumbai. For the estimated 350,000-plus northeasterners living and working in the UAE — in construction, hospitality, healthcare, and retail — the absence of a direct link meant 18- to 24-hour journeys, missed connections during monsoon delays, and fares that climbed steeply during Bihu and Durga Puja season.

The new routes also feed a growing tourist flow in the opposite direction. Assam Chief Minister Himanta Biswa Sarma, who announced the flights on X, noted that Guwahati now has direct international connectivity to four countries: the UAE, Thailand, Singapore, and Bhutan. "My next goal is to commence direct services to Vietnam," he added. The EU's recent decision to lift restrictive travel advisories for Assam is expected to further boost inbound tourism to the region.

## Northeast India's Quiet Aviation Boom

The Guwahati flights are part of a broader Air India Express push into the northeast. The carrier now operates more than 290 weekly flights from four northeastern airports — Guwahati, Dibrugarh, Dimapur, and Imphal. Its 'Tales of India' livery programme features regional art forms on aircraft tails, including Assam's Gamosa and Jaapi motifs, Nagaland's Tsüngkotepsü, and Manipur's Moirang Phee.

Air India's CEO Campbell Wilson, speaking separately about the group's expansion plans, said June marked the airline's strongest-ever operational month, with on-time performance hitting 86 per cent overall and a record 90 per cent on domestic routes. Air India Express will also become the first airline to operate an international passenger flight from the new Navi Mumbai airport next month — to Abu Dhabi — and will add Pune–Amritsar and first-ever Guwahati–Gulf services in August.

## What to Know Before You Book

NRIs planning to use the new Guwahati–Dubai route for a Bihu-season trip home should note that the service operates only once a week in each direction. That means limited flexibility if plans change, and fares are likely to spike during the October–November festive window. For families splitting time between the Gulf and Assam, the Friday Abu Dhabi service lines up well with a weekend departure from the UAE, landing back in India the same night.

The northeast has long been India's most under-connected region internationally. With Guwahati now linked to two of the Gulf's biggest hubs, and Imphal and Dibrugarh growing their domestic networks, the corridor is finally catching up to the diaspora that has been waiting for it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Northeast India Finally Gets a Direct Gulf Link — Air India Express to Fly Guwahati to Dubai and Abu Dhabi from August",
    "subheadline": "The first-ever nonstop services between Assam and the UAE open a corridor that hundreds of thousands of northeastern workers in the Gulf have needed for years.",
    "slug": make_slug("guwahati-dubai-abu-dhabi-air-india-express-northeast-gulf-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "An estimated 350,000-plus northeasterners in the UAE have had to backtrack through Delhi or Kolkata for every trip home — the new direct link cuts travel time from 18-24 hours to roughly six.",
    "tags": ["travel", "airlines", "air-india-express", "northeast-india", "gulf", "uae", "dubai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/air-india-express-announces-first-direct-flights-from-guwahati-to-dubai-and-abu-dhabi"},
        {"name": "UAE Vartha", "url": "https://english.uaevartha.com/air-india-express-links-northeast-to-gulf-with-historic-guwahati-uae-direct-flights/"},
        {"name": "IANS via IANSLive", "url": "https://ianslive.in/air-india-may-increase-foreign-flights-as-gulf-crisis-eases"},
        {"name": "Air India Express (booking page)", "url": "https://flights.airindiaexpress.com/guwahati-to-abu-dhabi-flight"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Lokpriya_Gopinath_Bordoloi_International_Airport.jpg/1280px-Lokpriya_Gopinath_Bordoloi_International_Airport.jpg",
    "image_caption": "Lokpriya Gopinath Bordoloi International Airport in Guwahati, the gateway to Northeast India",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ── Article 2 ───────────────────────────────────────────────────────────────

art2_body = """India has launched a fully redesigned OCI portal and, alongside it, a set of rule changes that every NRI with an Overseas Citizen of India card — or planning to get one — needs to understand. The revamped platform at ociservices.gov.in replaces a system that had not been meaningfully updated since 2013, and the new Citizenship Amendment Rules of 2026, notified on April 30, bring the biggest overhaul to OCI procedures in more than a decade.

## What's New on the Portal

The old OCI portal was a relic — clunky navigation, no application tracking, and a form-filling experience that made even seasoned NRIs reach for a migration agent. The new system, announced by the Ministry of Home Affairs, introduces features that most government portals should have had years ago: auto-fill of profile details, a dashboard showing completed and in-progress applications, integrated online payments for those filing through Foreigners Regional Registration Offices, and an in-built image cropping tool so you no longer need third-party software to resize your passport photo.

More substantively, the portal now supports **e-OCI** — an electronic OCI card that can be issued alongside or instead of the traditional physical card. All records will be maintained digitally, and applicants can track every stage of their submission online. The system processes roughly 2,000 applications a day across more than 180 Indian missions and 12 FRROs, and the upgrade is meant to reduce the processing delays that have frustrated the 5 million-plus OCI cardholders worldwide.

## The $25 Fine You Can't Ignore

Buried in the new Citizenship Amendment Rules is a compliance requirement that catches many NRIs off guard. If you renew your foreign passport — as happens routinely for US, Canadian, British, and Australian citizens — you now have **three months** from the date of the new passport's issuance to update those details on the OCI portal. Miss the window, and you face a fine of $25 (or equivalent in local currency).

It sounds small. But the fine is a marker of a broader shift: India is tightening its digital oversight of OCI holders, and non-compliance could complicate future immigration processing. The updated rules also link OCI data to India's biometric verification systems, paving the way for faster **e-gate** immigration processing at Indian airports — real-time matching of your passport and OCI data so you clear immigration in seconds rather than minutes.

## No Dual Passports for Minors

A key clarification addresses a long-standing grey area. Under the new rules, no minor can hold both an Indian passport and a foreign passport simultaneously. For NRI families who have navigated the ambiguity of dual documentation for their children — particularly those born abroad who were registered for both an Indian and a foreign passport before renouncing Indian citizenship — the rule draws a hard line.

The practical implication: if your child holds an Indian passport and you have obtained (or plan to obtain) foreign citizenship for them, the Indian passport must be surrendered before the foreign passport is used for travel to India. An OCI card then becomes the standard document for the child's India access.

## Broader Eligibility, Tighter Controls

The rule changes are not all restrictive. The six-month residency requirement for OCI registration has been dropped — eligible foreign nationals with a valid long-term visa and the required documents can now apply soon after arriving in India, rather than waiting half a year. Fifth- and sixth-generation Indian-origin Tamils in Sri Lanka are now eligible for OCI cards, extending a benefit previously limited to fourth-generation descendants.

## What NRIs Should Do Now

For the 4.7 million OCI cardholders — and the tens of thousands who apply each year — the action items are straightforward. First, log into the new portal and verify that your profile and passport details are current. Second, if you have renewed your foreign passport in the last three months, update it immediately to avoid the fine. Third, if you have been waiting on a physical OCI card, check whether the e-OCI option is available for your mission — it may arrive faster.

The OCI programme was always meant to be a bridge between India and its diaspora. The new portal and rules bring the plumbing closer to that promise — faster processing, digital-first documentation, and airport e-gates that actually work. The trade-off is tighter compliance. For most NRIs, that is a deal worth taking."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Revamped OCI Portal Is Live — and There's a $25 Fine Every NRI Should Know About",
    "subheadline": "The biggest overhaul to OCI procedures in a decade brings e-OCI cards, digital-first applications, and a new penalty for NRIs who don't update their passport details within three months.",
    "slug": make_slug("india-oci-portal-revamp-fine-eoci-nri-rules"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "More than 5 million OCI cardholders worldwide — including the vast majority of Indian Americans — are affected by the new $25 fine for late passport updates and should verify their portal profiles immediately.",
    "tags": ["travel", "oci", "immigration", "nri", "passport", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/india-launches-feature-rich-user-friendly-oci-portal-for-5-million-oci-cardholders/"},
        {"name": "Fragomen Immigration", "url": "https://www.fragomen.com/insights/india-new-oci-rules-bring-broader-eligibility-but-stricter-compliance-measures.html"},
        {"name": "Mondaq (RPV Legal)", "url": "https://www.mondaq.com/india/citizenship-amendment-rules-2026"},
        {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com/national/mha-notifies-oci-rule-changes-2026-applications-fully-online"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Indian_Passport_03.jpg/1280px-Indian_Passport_03.jpg",
    "image_caption": "An Indian passport — the document at the centre of the OCI programme's new digital overhaul",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ── Insert ──────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        resp = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
