#!/usr/bin/env python3
"""Immigration writer — 2026-07-05 13:00 PT run.
Two fresh articles for The Videshi immigration vertical.
"""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── ARTICLE 1 ──────────────────────────────────────────────────────────────────
art1_body = """The Supreme Court has made international travel riskier for millions of green card holders — and Indian Americans, who fly to India more often than almost any other immigrant group, are squarely in the crosshairs.

In a 6–3 ruling on June 23 in *Blanche v. Lau*, Justice Clarence Thomas wrote for the majority that border officers do not need clear and convincing evidence of a crime at the moment a lawful permanent resident re-enters the United States to reclassify them from "admitted" to "paroled." The government can rely on evidence gathered later — including a conviction that occurs months or years after re-entry — to justify the reclassification retroactively.

The practical consequence is severe. A green card holder reclassified as a parolee loses the legal protections that ordinarily shield returning residents. The burden of proof in any removal proceeding shifts against them. Their physical green card can be confiscated at the airport. In some cases, they face mandatory detention with no right to a bond hearing.

## What happened in the case

Muk Choi Lau, a longtime lawful permanent resident originally from China, travelled abroad while a criminal charge — trademark counterfeiting — was pending against him. When he returned to the United States, a Customs and Border Protection officer paroled him in rather than admitting him, citing the pending charge. A conviction followed roughly a year later, resulting in a sentence of probation. The government then used that post-entry conviction to justify the original reclassification and seek his removal.

The Second Circuit had ruled that border officers needed clear and convincing evidence of a crime at the moment of re-entry. The Supreme Court reversed, holding that no such evidentiary standard applies at the border.

## Why this matters for Indian Americans

The ruling affects all 12.8 million lawful permanent residents in the United States, but its practical bite falls hardest on communities that travel internationally with regularity. Indian Americans are among the most frequent transatlantic travellers, flying to India for family weddings, festivals, elder care, and business. Many hold green cards for years — sometimes decades — while waiting in the employment-based backlog that currently stretches past 2013 for EB-2 India.

Immigration attorneys are already warning clients with any criminal history, however minor, to think carefully before booking flights. The definition of "crime involving moral turpitude" in immigration law is notoriously broad and can include offences that carry no jail time under state law — a shoplifting charge from a decade ago, a disorderly conduct plea, even certain traffic violations depending on the jurisdiction.

"I don't understand why the border officer suddenly has so much power to deprive a person who has a green card based on a suspicion or even an indictment when the statute seems to require conviction," Justice Ketanji Brown Jackson said during oral arguments in April.

The ruling also limits judicial review. The majority held that the decision to parole a returning resident is discretionary and largely unreviewable by federal courts, a position that immigration advocates say strips away a critical safeguard.

## The broader pattern

*Blanche v. Lau* is one of several immigration victories the administration secured at the Supreme Court in the final weeks of the term. On June 25, the court ruled 6–3 that the administration can terminate Temporary Protected Status for roughly 350,000 Haitians and 6,000 Syrians. On June 30, it upheld birthright citizenship in a 6–3 ruling that went against the administration. The net effect is a judiciary that is giving the executive branch wide latitude on enforcement while drawing firm lines on constitutional fundamentals.

For Indian green card holders, the immediate takeaway is concrete: if you have any criminal history — even an old, resolved, or minor matter — consult an immigration attorney before your next trip to India. The rules at the border have changed, and the margin for error has narrowed considerably.

Sources:
- Supreme Court opinion, *Blanche v. Lau* (June 23, 2026)
- Klasko Immigration Law Partners, July 2026 immigration update
- Just Security, "The Supreme Court Case Affecting 12 Million Green Card Holders"
- Washington Examiner, "Trump's immigration winning streak at Supreme Court" (June 29, 2026)"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Green Card No Longer Guarantees Re-Entry. The Supreme Court Made Sure of That",
    "subheadline": "A 6–3 ruling lets border officers reclassify returning residents as parolees based on evidence that did not exist when they landed. Twelve million green card holders just lost a layer of protection.",
    "slug": make_slug("scotus-blanche-lau-green-card-reentry-risk-indian-americans"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian green card holders who travel frequently to India for family or business now face heightened re-entry risk if they have any criminal history, even minor or resolved charges.",
    "tags": ["green-card", "supreme-court", "blanche-v-lau", "reentry", "deportation", "indian-americans"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Supreme Court of the United States", "url": "https://www.supremecourt.gov/opinions/25pdf/24-1132_p86b.pdf"},
        {"name": "Klasko Immigration Law Partners", "url": "https://www.klaskolaw.com/july-2026/"},
        {"name": "Just Security", "url": "https://www.justsecurity.org/109469/the-supreme-court-case-affecting-12-million-green-card-holders/"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/immigration/3415809/trump-immigration-winning-streak-supreme-court/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
    "image_caption": "The United States Supreme Court building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ── ARTICLE 2 ──────────────────────────────────────────────────────────────────
art2_body = """Seven hundred and fifty dollars. That is what the State Department now charges to skip the line for a U.S. visitor visa interview — on top of the standard $185 application fee.

A temporary final rule published in the Federal Register on June 9 and effective since July 1 creates a six-month pilot programme allowing B-1 (business) and B-2 (tourist) visa applicants to purchase an expedited interview appointment within ten business days at participating consular posts. The programme runs through December 31, 2026.

The State Department says the fee is "an optional premium addition" offered "only to applicants at limited posts as published on travel.state.gov and in limited quantities." It does not guarantee a visa. It does not expedite processing, vetting, or administrative review. It buys one thing: a faster appointment slot.

## How it works

An applicant at a participating post pays $750 in addition to the standard $185 nonimmigrant visa application fee. If accepted, they receive an interview appointment within ten business days. Enhanced passport return options may also be available. Everything else — the interview itself, the security screening, any administrative processing — proceeds at normal speed.

The rule is explicit that paying the fee confers no advantage in the adjudication. A consular officer can still deny the visa on any ground. If administrative processing is triggered, the applicant waits just as long as anyone else.

The State Department timed the programme to coincide with the FIFA World Cup, which runs through July 19 in North American host cities, and anticipates demand from short-notice business travellers, families attending events, and tourists.

## The two-tier problem

Immigration attorneys have flagged the obvious equity concern. The pilot creates a pay-to-skip-the-line pathway that does not require applicants to demonstrate urgent circumstances — no medical emergency, no business necessity, no humanitarian reason. Anyone with $750 to spare can move to the front.

For Indian visa applicants, the context matters. Wait times for B-1/B-2 appointments at U.S. consulates in India have been among the longest in the world. Parents of H-1B holders trying to visit their children in the United States routinely wait months for an interview slot. The previous emergency appointment system at least required a justification — a family medical crisis, an imminent business deadline. The new programme replaces need with purchasing power.

Maggio Kattar, an immigration law firm in Washington, noted that the pilot "appears to create a separate, fee-based pathway to expedited B-1/B-2 visa appointments that does not require applicants to demonstrate urgent circumstances, such as significant business needs, medical emergencies, humanitarian issues, or other compelling reasons."

## What this means for NRI families

The visa appointment backlog at Indian consulates has been a persistent pain point for the diaspora. Elderly parents waiting six months to visit grandchildren in New Jersey. A sibling unable to attend a wedding in Houston. A business partner stuck in Bengaluru while a deal closes in San Francisco.

The $750 expedited fee offers a release valve, but only for those who can afford it. A retired schoolteacher in Lucknow earning ₹35,000 a month — roughly $420 — is unlikely to view $750 as "optional." The fee amounts to nearly two months of their income, layered on top of the $185 application fee, the DS-160 filing costs, and the round-trip fare to the nearest consulate city.

The programme also does nothing to address the underlying bottleneck. Consulate interview capacity in India has been constrained since December 2025, when the State Department began requiring enhanced social media vetting for all H-1B and H-4 visa applicants. That mandate reduced the number of interviews conducted per day, creating a cascading backlog that pushed some appointments into mid-2026.

The comment period for the temporary rule closes July 9. The State Department has indicated it may make the programme permanent if demand warrants it. For Indian families separated by visa wait times, the pilot offers a choice that was not previously available — but at a price that makes the existing inequality harder to ignore.

Sources:
- U.S. Department of State, Temporary Final Rule, Federal Register Vol. 91, No. 110 (June 9, 2026)
- Bloomberg Law, "US Offers Expedited Business, Tourist Visa Services for $750 Fee"
- Maggio Kattar LLP, analysis of expedited visa appointment rule
- Ogletree Deakins, "Need a U.S. Visa Faster? New $750 Expedited Interview Option Launches on July 1"
- Skift, "New $750 Fee Lets Travelers Jump the U.S. Visa Line"
- Livemint, 'US visa update: Pay $750 and skip the queue'"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Pay $750 and Skip the Line. The State Department Is Selling Faster Visa Appointments",
    "subheadline": "A new pilot programme lets B-1 and B-2 visa applicants buy an interview slot within ten days — no urgency required. For Indian families waiting months for consulate appointments, the price of convenience just went up.",
    "slug": make_slug("state-department-750-expedited-visa-appointment-indian-families"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families enduring months-long waits for U.S. visitor visa appointments can now pay $750 to skip the line — but the fee is nearly two months' income for a middle-class retiree in India.",
    "tags": ["visa", "b1-b2", "consulate", "state-department", "visitor-visa", "nri-families"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Federal Register", "url": "https://www.federalregister.gov/documents/2026/06/09/2026-12741/schedule-of-fees-for-consular-services"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/us-offers-expedited-business-tourist-visa-services-for-750-fee"},
        {"name": "Maggio Kattar LLP", "url": "https://maggio-kattar.com/"},
        {"name": "Ogletree Deakins", "url": "https://ogletree.com/insights-resources/blog-posts/need-a-u-s-visa-faster-new-750-expedited-interview-option-launches-on-july-1/"},
        {"name": "Skift", "url": "https://skift.com/2026/06/10/new-750-fee-lets-travelers-jump-the-u-s-visa-line/"},
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "An open passport displaying various travel visa stamps",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ── INSERT ──────────────────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
