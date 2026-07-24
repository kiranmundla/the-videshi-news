#!/usr/bin/env python3
"""Immigration writer — July 9, 2026 morning run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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


# ──────────────────────────────────────────────
# ARTICLE 1: $750 Expedited Visa Interview Fee
# ──────────────────────────────────────────────

art1_body = """The State Department has introduced a new fee that lets visitors skip the visa interview queue — for a price. As of July 1, applicants for B-1 business and B-2 tourist visas can pay $750 on top of the standard $185 application fee to secure an interview appointment within ten business days.

Under normal circumstances, applicants at U.S. consulates — particularly those in India — can wait weeks or months for a standard interview slot. At several Indian posts, the backlog for non-immigrant visa appointments has stretched beyond ten months. The new fee is designed to relieve that pressure, at least for those who can afford it.

## How It Works

The program operates through a temporary final rule published in the Federal Register on June 9. Applicants first submit their DS-160 application, pay the standard $185 MRV fee, and schedule a regular interview. If they want to jump the queue, they indicate interest in an expedited slot. Available appointments within the next ten business days appear on screen. The applicant then has a five-to-ten-minute window to pay the $750 fee and lock in the appointment. Miss that window, and the slot goes to the next person.

The State Department has been explicit about what the fee does not buy. It does not expedite processing. It does not guarantee visa issuance. It does not waive administrative processing or security checks. An applicant who pays $750 and fails to attend the interview forfeits the fee entirely — no refunds.

## A Pilot With Limits

The program runs through December 31, 2026, with a projected cap of 25,000 expedited requests across all participating posts. Which consulates and embassies will offer the service remains unclear — the Bureau of Consular Affairs has said it will announce participating locations on travel.state.gov, but has not yet done so.

Existing no-cost mechanisms for expedited appointments remain in place. Consular managers can still fast-track interviews for humanitarian reasons or urgent travel deemed in the U.S. national interest without charging a fee.

## The Diaspora Calculation

For Indian families, the arithmetic is straightforward but unsettling. A parent in Hyderabad trying to visit a child in New Jersey for a graduation might otherwise wait until 2027 for a routine B-2 interview. The $750 fee — on top of the $185 application cost, a potential visa issuance fee, flights, and accommodation — could total well over $1,500 before they even know whether they will be admitted.

The timing is pointed. The FIFA World Cup is underway across North America, driving a surge in visitor visa demand globally. The State Department has framed the pilot as a response to that demand. But immigration attorneys note the fee effectively creates a two-tier system: one queue for applicants who can pay, another for everyone else.

For Indian professionals on H-1B or L-1 visas whose parents routinely apply for B-2 visitor visas, the fee adds another financial layer to an already expensive immigration landscape. It does not touch the employment-based visa backlogs or the consular stamping delays that have left thousands stranded. It is, in the State Department's own framing, a "premium addition" — an optional fast pass for those willing and able to pay.

The department has said it will evaluate the pilot's results before deciding whether to continue, expand, or adjust the fee. For now, the message to visa applicants worldwide is clear: the queue has a price."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Pay $750 to Skip the Queue. The State Department Just Put a Price on Visa Interviews",
    "subheadline": "A new pilot program lets B-1 and B-2 visa applicants buy expedited interview appointments at select consulates — but it does not guarantee approval, and participating posts have not been announced.",
    "slug": make_slug("state-department-750-expedited-visa-interview-fee-pilot"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families visiting relatives in the US face some of the longest consulate wait times in the world — this fee creates a pay-to-play fast lane that does not touch the underlying backlog.",
    "tags": ["visa", "b1-b2", "consulate", "state-department", "visa-interview", "immigration-fees"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "U.S. Federal Register — Temporary Final Rule", "url": "https://www.federalregister.gov/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/news/world/us-visa-update-pay-750-and-skip-the-queue-for-interview-appointments-who-can-apply-whats-the-process-know-here-11781090214611.html"},
        {"name": "BAL Immigration Law", "url": "https://www.bal.com/"},
        {"name": "EB-5 Insights", "url": "https://eb5insights.com/"},
        {"name": "Skift", "url": "https://skift.com/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33500646/pexels-photo-33500646.jpeg",
    "image_caption": "The entrance sign of the U.S. Embassy in New York City",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}


# ──────────────────────────────────────────────────────────
# ARTICLE 2: USCIS Reclassifies Adjustment of Status
# ──────────────────────────────────────────────────────────

art2_body = """For decades, the playbook was simple. An Indian engineer on an H-1B visa whose employer sponsored a green card would file for adjustment of status — a process handled entirely within the United States, without leaving the country. USCIS would process the I-485 application, schedule an interview at a local field office, and eventually mail the card. The applicant never had to set foot in a consulate abroad.

That assumption is now in question.

On May 22, USCIS issued Policy Memorandum PM-602-0199, declaring that adjustment of status under Section 245 of the Immigration and Nationality Act is "a matter of discretion and administrative grace" — an "extraordinary form of relief" rather than a default pathway. The agency directed its officers to evaluate each application on a case-by-case basis and to treat consular processing at a U.S. embassy abroad as the standard route to a green card.

## What Changed

The policy does not eliminate adjustment of status as a legal option. The statute that authorises it remains intact. But the memo instructs USCIS officers to weigh positive and negative factors before granting it, elevating the discretionary bar significantly. In practice, this means an officer could deny an adjustment application not because the applicant is ineligible, but because the officer decides the applicant should have processed through a consulate instead.

USCIS spokesperson Zach Kahler framed the shift as a return to "the original intent of the law." Temporary visa holders — students, workers, tourists — are expected to leave the country when their authorised stay ends, he said. Those who want permanent residency should apply from their home country, "except in extraordinary circumstances."

The memo lists no effective date, which immigration attorneys interpret as immediate. More alarming to practitioners: it appears to apply retroactively to applications already filed and pending.

## The Scale of Disruption

The numbers are staggering. Hundreds of thousands of pending I-485 applications sit in USCIS backlogs, many filed by Indian nationals in the EB-2 and EB-3 employment-based categories. These applicants chose adjustment of status specifically because it allowed them to remain in the United States, continue working, and avoid the risks of consular processing — where a single administrative processing flag could strand them abroad for months.

Now, any of those applications could theoretically be denied on discretionary grounds and referred to consular processing. For an Indian EB-2 applicant whose priority date has finally become current after a decade-long wait, the prospect of being told to fly to New Delhi or Mumbai for an interview at a consulate already booked into 2027 is not hypothetical. It is the new default position.

## Compounding Crises

The timing amplifies the damage. U.S. consulates in India have been in crisis since December 2025, when the State Department began mandatory social media vetting for employment-based visa categories. Interview slots at Hyderabad, Chennai, Mumbai, and New Delhi were pushed out by six months or more. Many applicants who travelled to India for routine visa stamping found themselves stranded, unable to return to their U.S. jobs.

Layering a consular processing requirement on top of this backlog creates a compounding problem. Applicants who leave the United States for consular processing risk losing their jobs if the interview is delayed. Those who stay and file for adjustment of status risk denial under the new discretionary standard.

Immigration law firm Greenspoon Marder noted that the memo "elevates the discretionary bar" in ways that could make adjustment "unpredictable and no longer a strong, default option." Parisa Karaahmet of Fragomen told USA Today that the memo applies to "any person seeking adjustment of status" — not just certain visa categories.

## What It Means for Indian Families

For the Indian professional who has lived in the United States for fifteen years, raised children here, paid taxes, and patiently waited through the EB-2 India backlog, this policy shift is not an abstraction. It is a directive that the path they were counting on — adjusting status without leaving the country — may no longer be available to them as a matter of course.

The legal challenges are almost certain to follow. But until courts weigh in, the memo stands as policy. USCIS officers are now instructed to treat every adjustment application as a request for extraordinary relief — and to consider whether the applicant should have gone home instead."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "USCIS Says Your Green Card Application Is Now 'Extraordinary Relief.' That Word Does the Heavy Lifting",
    "subheadline": "A policy memo reclassifies adjustment of status from a routine pathway to a discretionary favour, potentially forcing hundreds of thousands of applicants — many of them Indian — to leave the country and apply from abroad.",
    "slug": make_slug("uscis-adjustment-of-status-extraordinary-relief-consular"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders have relied on adjustment of status for decades to avoid the consular processing gauntlet — this memo threatens that pathway at the worst possible time, with consulate backlogs in India stretching into 2027.",
    "tags": ["green-card", "adjustment-of-status", "uscis", "consular-processing", "eb2", "eb3", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS Policy Memorandum PM-602-0199", "url": "https://www.uscis.gov/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/"},
        {"name": "Greenspoon Marder", "url": "https://www.gmlaw.com/"},
        {"name": "Barnes & Thornburg", "url": "https://www.btlaw.com/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/24/us-asks-foreign-nationals-to-apply-for-green-cards-from-home-country/"},
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Jamaica, Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
