#!/usr/bin/env python3
"""NRI World writer — July 1, 2026 run.

Articles:
1. India's e-OCI Card launch eliminates the physical booklet for 5M+ holders
2. An Indian Summer festival in Leicester turns 15
"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

# ── Article 1 ──────────────────────────────────────────────────────────────────
art1_body = """\
For millions of overseas Indians, the Overseas Citizen of India card has long been one of the most useful — and most maddening — documents in their lives. It grants lifelong visa-free travel to India, a handful of economic and educational rights, and the comforting fiction that New Delhi still considers you partly its own. What it also grants is a recurring bureaucratic headache: physical booklets that must be reissued every time you renew your passport before age 20 or after 50, applications submitted in duplicate, months-long processing windows, and the nagging fear that losing the thing means starting over.

On Monday, Home Minister Amit Shah put that particular species of paperwork on a path toward extinction. Launching the e-OCI Card alongside the FCRA 2.0 Portal in New Delhi, Shah announced a fully digital system under which applicants can complete the entire OCI lifecycle online — from initial registration and document upload to downloading the approved card on a phone. Existing cardholders can obtain an e-OCI in most cases without filing a fresh application or presenting themselves in person.

## What changes for cardholders

The most consequential shift is the elimination of the physical booklet reissue requirement. Under the old rules, OCI holders had to obtain a new booklet every time a new passport was issued before they turned 20, and once more after 50 — a process that could take weeks, required mailing documents to a consulate, and occasionally went wrong in ways that left people stranded at immigration counters.

Under the new arrangement, the booklet reissue is gone. Once an OCI registration is active, the cardholder's registration number becomes permanent and unique. Passport updates still need to be filed — the holder has three months from the date a new passport is issued to upload the details on the portal — but the OCI itself is now a digital record, not a physical document. A fine of $25 applies for late updates, a compliance stick that Delhi clearly hopes will keep its database current without requiring the old paper shuffle.

The system integrates with India's Immigration, Visa & Foreigners Registration & Tracking (IVFRT) 2.0 platform, the same infrastructure powering automated e-gates at major Indian airports. The promise is faster immigration clearance: real-time verification of OCI status against passport data, no more thumbing through booklet pages at the counter.

## A long road to digital

The overhaul did not happen overnight. The Citizenship (Amendment) Rules, 2026, notified on April 30, laid the legal groundwork by mandating that all OCI applications — registration, reissuance, transfer, renunciation — be filed electronically through the designated portal. The rules introduced the concept of the e-OCI alongside the traditional physical card, with both recorded under a revised Form XXIX in a centralised electronic register.

A revamped OCI portal had been launched as far back as May 2025, but it was largely a user-interface refresh over the same creaking 2013-era backend. The June 30 launch represents the deeper transformation: end-to-end digitisation, Aadhaar-based authentication, e-Sign facilities, and OCR-based document analysis, all hosted on MeghRaj, the government cloud.

Prime Minister Narendra Modi, responding to Shah on X, called the launch "a major step forward in boosting citizen-friendly digital governance." Whether that is premature triumphalism or a reasonable assessment will depend on execution. India's track record with government portals is mixed — the existing OCI system was plagued by crashes, cryptic error messages, and processing backlogs that drove applicants to WhatsApp community groups for troubleshooting tips.

## What it means for the diaspora

For the estimated 5 million-plus OCI cardholders scattered across more than 200 countries, the e-OCI is less a revolution than the end of an avoidable indignity. The old system asked people who had already proven their Indian heritage — and paid handsomely for the privilege — to keep proving it, in person, on paper, repeatedly.

The new system, if it works as advertised, eliminates the single most common source of frustration: the consular visit for a booklet reissue that no other country's equivalent travel document requires. It also removes the risk of losing or damaging the physical card, a problem that — in pre-digital India — had no good solution short of starting the entire application from scratch.

None of this changes the fundamental bargain of the OCI card. Holders still cannot vote, own agricultural land, or hold certain government positions. What they get is smoother re-entry to a country they left but never quite let go of — and now, at least, they can carry the proof in their pocket rather than a filing cabinet.
"""

art1_sources = json.dumps([
    {"name": "India Education Diary", "url": "https://indiaeducationdiary.in/union-home-minister-amit-shah-launches-fcra-2-0-portal-and-e-oci-card/"},
    {"name": "Nagaland Post", "url": "https://www.nagalandpost.com/index.php/shah-launches-new-version-of-fcra-portal-and-e-oci-card/"},
    {"name": "The Indian Eye", "url": "https://www.theindianeye.com/2026/06/india-launches-feature-rich-user-friendly-oci-portal-for-5-million-oci-cardholders/"},
    {"name": "Fragomen", "url": "https://www.fragomen.com/insights/india-new-oci-rules-bring-broader-eligibility-but-stricter-compliance-measures.html"},
])

# ── Article 2 ──────────────────────────────────────────────────────────────────
art2_body = """\
Leicester is the sort of English city that would confuse anyone relying on outdated mental maps of Britain. A quarter of its population traces its roots to South Asia — the largest concentration outside London — and its cultural calendar reflects that weight. This week, the city's flagship South Asian arts festival, An Indian Summer, opens its 15th edition with five days of theatre, dance, live music, puppetry, film, and visual arts spread across venues from the medieval Leicester Cathedral to the modernist Attenborough Arts Centre.

The festival, produced by the Leicester-based arts organisation Inspirate, has evolved considerably since its founding in 2011. What began as a modest effort to showcase South Asian culture in the East Midlands has grown into one of the UK's longest-running festivals of its kind, this year expanding into new venues including the Leicester Cathedral Gardens and the International Arts Centre. Many events are free.

## A programme built on crossover

The 2026 edition leans into the hyphenated identities that define diaspora life in Britain. Rather than presenting South Asian culture as a heritage exhibit — saris behind glass, tabla demonstrations for school groups — the programme centres contemporary work by South Asian artists living and making art in the UK.

The opening night at Attenborough Arts Centre features an Indian classical music concert presented in partnership with the University of Leicester, which has been the festival's sponsor since its inaugural year in 2012. The comedy night "An Asian Occasion" returns on July 2 at The Big Difference, assembling Asian comics from across the UK circuit. In Jubilee Square, DJ Aaron Hira — the festival's resident selector — blends contemporary and nostalgic South Asian rhythms through the weekend, turning the city centre into an open-air gathering spot.

The closing event on July 5 at Leicester Cathedral is characteristic of the festival's ambitions. Amrit Kaur, a sarangi player and vocalist, performs a set that threads Sikh musical heritage through jazz, blues, and soul — precisely the kind of cross-pollination that happens when a tradition takes root in foreign soil. Two short films follow: *Jaikur* by Kesha Raithatha and *Roots & Rivers* by Nupur Arts.

## Leicester's quiet claim

The festival's durability says something about Leicester itself. The city received one of the earliest waves of South Asian migration to Britain, primarily Gujaratis expelled from East Africa in the early 1970s. Unlike London, where diaspora communities are dispersed across boroughs, Leicester's South Asian population is concentrated enough to sustain institutions — temples, community centres, businesses, and now arts festivals — that in other cities would struggle for critical mass.

Jiten Anand, Inspirate's co-founder and executive director, has described the University of Leicester partnership as a "poetic moment," a return to the institution that gave the festival its first financial backing. "We would like to share a massive thank you to the University of Leicester and Attenborough Arts Centre for supporting An Indian Summer and providing the opportunity to engage with the many international students who are studying here," he said.

Andrew Fletcher, director of Attenborough Arts Centre, noted the festival's growth: "This year's programme promises to deliver an eclectic mix of outdoor theatre, dance, live music, film, visual arts and participatory experiences."

## Why it matters beyond Leicester

For the British Indian diaspora, festivals like An Indian Summer serve a function that no amount of Bollywood streaming or WhatsApp family groups can replicate. They create shared physical space — a city square with a DJ spinning desi beats on a Saturday afternoon, a cathedral hosting a sarangi concert on a Sunday evening — where cultural identity is not something to be explained or defended but simply lived.

The festival opens this week as the UK prepares for South Asian Heritage Month, which runs from July 18 through August 17. For Leicester, the timing is fitting. The city does not need a designated month to acknowledge its South Asian character. It has been living it for half a century.
"""

art2_sources = json.dumps([
    {"name": "University of Leicester", "url": "https://le.ac.uk/news/2026/june/an-indian-summer-2026"},
    {"name": "South Asian Heritage Trust", "url": "https://www.southasianheritage.org.uk/an-indian-summer-festival-2026/"},
    {"name": "Cool As Leicester", "url": "https://coolasleicester.co.uk/an-indian-summer-returns-to-leicester/"},
    {"name": "Eventbrite", "url": "https://www.eventbrite.com/e/full-cycle-still-turning-an-indian-summer-festival-tickets"},
])

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Killed the Physical OCI Booklet. Five Million Cardholders Can Finally Exhale.",
        "subheadline": "The new e-OCI card lets overseas Indians complete the entire OCI lifecycle on a phone — no consular visits, no duplicate paperwork, no reissue anxiety.",
        "slug": make_slug("india-eoci-card-digital-booklet-eliminated-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Eliminates the single biggest bureaucratic pain point for 5M+ OCI holders worldwide — the mandatory physical booklet reissue that required consular visits, mailed documents, and weeks of waiting every time a passport was renewed.",
        "tags": ["nri", "diaspora", "oci", "e-oci", "digital governance", "india", "amit shah"],
        "urgency": "high",
        "sources": art1_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Union_Minister_for_Home_Affairs.jpg",
        "image_caption": "Union Home Minister Amit Shah, who launched the e-OCI Card system in New Delhi",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body.strip(),
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Leicester's South Asian Arts Festival Turns Fifteen. The City Barely Notices — It Has Been Living This for Decades.",
        "subheadline": "An Indian Summer returns to Leicester Cathedral, Jubilee Square, and Attenborough Arts Centre this week with five days of theatre, music, film, and dance.",
        "slug": make_slug("an-indian-summer-leicester-festival-15th-south-asian-arts"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Highlights how Leicester's concentrated South Asian diaspora sustains a 15-year-old contemporary arts festival — a model for diaspora cultural institutions that create shared physical space for identity beyond streaming and WhatsApp groups.",
        "tags": ["nri", "diaspora", "uk", "leicester", "south asian arts", "festival", "culture"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18086354/pexels-photo-18086354.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A traditional South Asian dancer performs on stage in vibrant costume and accessories",
        "image_attribution": "Pexels",
        "body": art2_body.strip(),
    },
]

for art in articles:
    wc = len(art["body"].split())
    print(f"📝 {art['headline'][:70]}... ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"  ✅ {art['slug']}")
    except Exception as e:
        print(f"  ❌ {art['slug']}: {e}")
