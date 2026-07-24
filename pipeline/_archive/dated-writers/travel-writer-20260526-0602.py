#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-26 batch (2 articles)"""

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
# Article 1: Digital e-OCI Card
# ─────────────────────────────────────────────

article1_body = """India's Ministry of Home Affairs has done something that 4.7 million Overseas Citizens of India have been quietly wishing for: it killed the blue booklet.

The Citizenship (Amendment) Rules, 2026, notified on April 30 and effective May 1, introduced the e-OCI — a fully digital credential built around a unique QR code that replaces the physical OCI booklet as the primary identity document for overseas Indians. The system went live on May 18. If you are an OCI holder in the United States, Canada, the United Kingdom, or Australia, this changes how you interact with India on nearly every trip.

## What the e-OCI Actually Is

The e-OCI is not a PDF of your old card. It is an electronic registration maintained in a central digital register (Form XXX), with a certificate issued in Form XXIX. Each credential carries a QR code that immigration officials, banks, and other authorized institutions can scan for instant verification. No more thumbing through blue pages at the immigration counter while the line behind you grows.

Fresh applications are now entirely online through the [official OCI portal](https://ociservices.gov.in). No courier shipments, no duplicate document submissions, no wondering whether your papers made it from San Jose to the consulate in San Francisco. The fee for applications outside India is USD 275.

## Why NRIs Should Care Right Now

Three things matter immediately.

**First, airport immigration gets faster.** The e-OCI integrates with India's upgraded IVFRT 2.0 platform — the same system powering automated biometric e-gates at Delhi, Mumbai, Bangalore, and Hyderabad airports. OCI holders with the digital credential will eventually be able to use automated lanes instead of joining the manual immigration queue. For anyone who has spent 45 minutes watching families of twelve negotiate the Delhi T3 immigration counter, this is meaningful.

**Second, setting up UPI payments in India becomes dramatically easier.** The e-OCI serves as a verified identity document for Video KYC (V-CIP), which means overseas Indians can activate NRE/NRO accounts and link them to UPI payment apps without producing a physical identity document at a bank branch. You land in Mumbai, and by the time your Uber reaches Bandra, you can be paying for chai with Google Pay.

**Third, the paperwork tax on passport renewals drops to near zero.** Every OCI holder knows the drill: renew your US or Canadian passport, then update your OCI card with the new passport details. Under the old system, that meant forms, photocopies, courier envelopes, and a three-month processing window that somehow always coincided with your next India trip. Under the new rules, you update passport details online within three months of issuance. No physical documents. Processing is expected to fall below 15 working days once the system is fully ramped.

## What Happens to Your Existing Blue Booklet

Nothing, for now. Physical OCI booklets remain valid travel documents. The Ministry is not forcing an immediate replacement. Existing holders will transition to the digital system naturally — most likely when they next renew a foreign passport or hit a reissuance milestone. After age 20, only a single mandatory reissuance trigger remains, simplifying what used to be a repetitive cycle.

The e-OCI can also be synced to DigiLocker, India's official digital document wallet, for instant identity verification during domestic hotel check-ins and internal travel. One less document to carry.

## The Fine Print

Minors cannot simultaneously hold an Indian passport and a foreign passport under the revised rules. For parents managing OCI applications for US-born children, this clarification matters during passport renewals.

The six-month continuous residence requirement for applying within India has been removed. Foreign spouses visiting family on valid visas can now apply through the nearest FRRO without waiting out a residency clock.

## The Bigger Picture

India has been digitizing furiously — Aadhaar, DigiLocker, UPI, FASTag, e-Arrival Card. The e-OCI is the latest piece in a stack that, taken together, means an NRI visiting India in 2026 carries less paper than at any point in the country's history. The blue booklet served its purpose for twenty years. Its retirement was overdue.

For the estimated 1.3 million OCI holders in the United States alone, the practical impact is simple: fewer consulate visits, faster immigration lines, and one less thing to lose in transit."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Killed the Blue Booklet — What the New Digital e-OCI Card Means for 4.7 Million Overseas Indians",
    "subheadline": "The physical OCI card is being replaced by a QR-coded digital credential. Airport e-gates, paperless renewals, and instant UPI setup are now on the table for NRIs.",
    "slug": make_slug("india-digital-eoci-card-nri-qr-code-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "4.7 million OCI holders globally — 1.3M in the US alone — get faster immigration via IVFRT 2.0 e-gates, paperless passport-linked renewals, and instant UPI setup through Video KYC. No more couriering documents to consulates.",
    "tags": ["travel", "oci", "visa", "digital-identity", "india", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "India Policy Hub — 2026 Digital e-OCI Card Guide", "url": "https://indiapolicyhub.in/2026/05/25/digital-e-oci-card-nri-upi-guide"},
        {"name": "Government of India — OCI Services Portal", "url": "https://ociservices.gov.in"},
        {"name": "Gazette of India — Citizenship (Amendment) Rules 2026", "url": "https://egazette.gov.in"},
        {"name": "Visa Roots — e-OCI Launch Date", "url": "https://www.visaroots.in"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/278430/pexels-photo-278430.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": article1_body
}

# ─────────────────────────────────────────────
# Article 2: Gulf Carriers Recovery
# ─────────────────────────────────────────────

article2_body = """For most of the last three months, the question for NRIs booking India flights was binary: avoid the Gulf or accept the chaos. That calculation is starting to shift — slowly, unevenly, and with enough caveats to fill a departure board.

On May 22, the Gulf's three largest carriers — Emirates, Etihad, and Qatar Airways — operated a combined 1,063 flights. That is up from 901 on May 14 and a fraction of their pre-crisis volumes, but the trajectory matters. Emirates alone flew 472 flights that day. On May 19, it managed 436. Etihad ran 258 on the same day. Qatar Airways, which was hit hardest by airspace restrictions, clocked 357.

These numbers sound abstract until you remember that before the US-Iran conflict shut down Gulf airspace in late February, Dubai alone processed over 1,200 Emirates departures daily.

## What Is Actually Flying

The European Union Aviation Safety Agency extended its conflict zone advisory through May 27, requiring operators to completely avoid the airspace of Iran, Iraq, and Lebanon at all altitudes. Caution — not avoidance — applies in Bahrain, Israel, Jordan, Kuwait, Qatar, Oman, the UAE, and Saudi Arabia. Eleven countries in the region remain under some form of advisory.

The practical effect: Gulf carriers are operating, but on rerouted paths. Emirates flies south through Oman before turning east or west, adding 60 to 90 minutes on some India-bound sectors. The old SFO-DXB-DEL routing that took 20 hours now stretches closer to 22. JFK-DXB-BOM runs similarly longer.

Kuwait International Airport completed repairs to Terminal 1 and will gradually resume Arab and international flights from June 1. Emirates is rolling out its brand-new, 569-seat A380 — the one with the $5 billion premium economy retrofit — to six routes: Bangkok from late June, Düsseldorf and Mauritius in July and August, Denpasar from September, Manchester in October, and London Gatwick from December.

## The Hormuz Variable

Everything hinges on the Strait of Hormuz. Oil prices fell nearly 7% on May 26 after reports that the US and Iran are close to signing a 14-point memorandum of understanding involving a 60-day ceasefire extension. Under the proposed terms, Iran would clear mines from the strait within 30 days, reopen it without tolls, and allow ships to pass freely. The US would lift its naval blockade and issue partial sanctions waivers.

The deal is outlined but unsigned. Both sides disagree on what the MOU actually says. Iran's Foreign Ministry called Trump's characterization of the agreement "incomplete and inconsistent with reality." But oil markets are already pricing in optimism — Brent crude dropped to $96.30 a barrel, down from triple-digit highs.

For NRI flyers, Hormuz reopening would mean three things: jet fuel prices drop, Gulf airspace restrictions ease, and the Dubai hub regains its central routing advantage. The fare premium on Gulf-routed flights — which has run $200 to $400 above pre-crisis levels — would narrow.

## Should You Book Through Dubai Now?

The honest answer: it depends on your risk tolerance and your travel dates.

**If you are flying before July**, the Gulf carriers are operating but still rerouted. Expect longer flight times. The EASA advisory will likely be renewed past May 27 unless the Iran deal materializes. European and Far East routings (Air France via Paris, SWISS via Zurich, Cathay Pacific via Hong Kong) remain more predictable.

**If you are flying August or later**, the odds improve. A signed ceasefire deal could restore Gulf airspace within 60 days of agreement. Emirates' A380 deployments suggest the airline is planning for a second-half recovery. The carrier has not added these routes to lose money on rerouted operations.

**If you are booking for Diwali season** (October-November), Dubai routing is worth considering again — but buy flexible tickets. A collapse in negotiations would send oil and airfares right back up.

## The Bigger Shift

The three-month Gulf disruption has permanently changed how some NRIs think about routing. Air France added India connectivity through Paris CDG. SWISS launched direct Zurich-Bengaluru service. Cathay Pacific and Singapore Airlines picked up displaced demand across Asia. These carriers will not simply disappear when Dubai recovers.

The Gulf hub model — where Emirates, Etihad, and Qatar Airways served as the default connector between North America and India — is being stress-tested. It will survive, but it may no longer be the only answer.

For the 4.8 million Indian-born residents of the United States, the most-flown international corridor in their lives is getting more competitive. That is, eventually, good news — even if the path there has been anything but smooth."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Gulf Carriers Hit 1,063 Flights in a Day as Dubai Slowly Climbs Back — What NRIs Should Know Before Rebooking",
    "subheadline": "Emirates, Etihad, and Qatar Airways are flying again, but at a fraction of pre-crisis capacity. The Hormuz deal could change everything — or collapse. Here is what matters for your next India ticket.",
    "slug": make_slug("gulf-carriers-recovery-dubai-nri-flights-hormuz"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Dubai was the default connection point for NRI India flights. With Gulf carriers at ~40% of pre-crisis capacity and a Hormuz deal pending, NRIs face a booking calculus between Gulf hubs, European alternatives, and Far East routings — with fare premiums of $200-400 still in play.",
    "tags": ["travel", "airlines", "emirates", "gulf", "dubai", "iran", "hormuz", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel Extra — Gulf Carriers Operate 1,063 Flights", "url": "https://www.travelextra.ie/updated-gulf-airline-flights/"},
        {"name": "Reuters — Oil Tumbles Nearly 7% on US-Iran Deal Hopes", "url": "https://www.reuters.com"},
        {"name": "Axios — Proposed US-Iran Deal Involves Hormuz Reopening", "url": "https://www.axios.com"},
        {"name": "Simple Flying — Emirates New A380 Routes", "url": "https://simpleflying.com"},
        {"name": "Travel and Tour World — Kuwait Airport Reopening", "url": "https://www.travelandtourworld.com"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/20594766/pexels-photo-20594766.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
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
