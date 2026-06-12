#!/usr/bin/env python3
"""
Immigration article writer — 2026-06-12
Inserts 2 fresh immigration articles into Supabase with status='review'
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone

import requests

# ── Supabase credentials ──────────────────────────────────────────────
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

now_iso = datetime.now(timezone.utc).isoformat()

# ── Article 1: India Consulate Stamping Crisis ─────────────────────────

article1_body = """Every year, hundreds of thousands of Indian professionals in the United States renew their H-1B petitions without leaving their desks. The approval notice arrives by email. The paycheques continue. Life goes on — until they need to travel.

The catch is a document called the visa stamp, the physical foil placed inside a passport at a US consulate abroad. Without a current one, a worker whose petition is perfectly valid cannot re-enter the country after stepping outside it. And right now, getting that stamp at an Indian consulate has become an ordeal that immigration attorneys say is the worst they have seen in a decade.

## The Social Media Bottleneck

In December 2025, the State Department quietly expanded a policy requiring consular officers to review visa applicants' social media histories as part of the interview process. The directive, rooted in a Trump-era executive order first introduced in 2019 and later reinstated, applies to all nonimmigrant visa categories — including H-1B, L-1, and even B-1/B-2 tourist visas.

The operational consequence has been severe. Each interview now takes longer. Officers must cross-reference social media handles submitted on the DS-160 form against a database of flagged content. At high-volume posts like the US consulates in Hyderabad and Chennai — which together process more H-1B visa stamps than any other facilities in the world — the throughput has dropped sharply. Wait times that were already measured in weeks have ballooned to four to six months, according to immigration law firms tracking appointment availability.

"We are telling every client: do not leave the United States unless you absolutely have to," says one Bay Area immigration attorney who asked not to be named because several of her firm's cases are pending consular review. "If your passport stamp is expired, you are effectively grounded."

## No Domestic Escape Hatch

Until recently, there was a glimmer of hope. The State Department had been running a pilot programme allowing certain visa holders to renew their stamps domestically — without travelling abroad. The programme, which covered H-1B and L-1 holders at select processing centres, was meant to ease exactly this kind of bottleneck.

That pilot ended in late 2025 and has not been renewed. The Biden-era initiative was always framed as temporary, and the current administration has shown no appetite for extending it. The result is a policy void: the one mechanism that could have relieved consular backlogs no longer exists, and nothing has replaced it.

## Trapped in Place

The practical effects are cascading through Indian American households in ways that rarely make headlines. A software engineer in Seattle whose mother is dying in Hyderabad cannot risk flying home because returning to the US would require a consular appointment she may not get for months. A consulting firm manager in Chicago has turned down a promotion that requires travel to a London office because transiting through any country outside the US would trigger the stamping requirement on return.

Third-country processing — once a popular workaround where Indians would get their stamps at consulates in Canada, Mexico, or Singapore — has also tightened. Several of these posts have restricted third-country national appointments, citing their own capacity constraints. Canada's consulate in Ottawa, previously a favourite for quick turnarounds, now shows H-1B wait times exceeding two months.

## The Numbers Behind the Backlog

India accounts for roughly 72 per cent of all H-1B visas issued globally. In fiscal year 2025, US consulates in India processed over 280,000 nonimmigrant work visa interviews. The social media vetting layer, applied to this volume, has created what attorneys describe as a structural mismatch between demand and processing capacity.

The State Department has not published official statistics on how much the vetting adds to each interview. But practitioners estimate the per-interview time has increased by 15 to 25 minutes — a figure that, multiplied across thousands of daily appointments, translates to tens of thousands of fewer slots per quarter.

## What Comes Next

Congress has shown little interest in addressing consular processing bottlenecks. The $750 "fast-pass" programme announced this week for B-1/B-2 tourist visas does not apply to employment-based categories. Immigration reform bills currently in committee focus on enforcement, fees, and lottery mechanics — not on the administrative machinery that determines whether someone with a valid work authorisation can actually get back into the country.

For the estimated 600,000-plus Indian nationals currently working in the US on H-1B visas, the message is clear: your petition may be approved, your employer may want you, and your taxes may be paid — but if your passport stamp has expired, America's front door is, for now, effectively closed."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Consulate Stamping Crisis Is Trapping H-1B Workers Inside the United States",
    "subheadline": "Social media vetting has pushed visa stamp wait times at Indian consulates to six months. With the domestic renewal pilot dead, hundreds of thousands of workers cannot risk leaving the country.",
    "body": article1_body.strip(),
    "category": "immigration",
    "vertical": "immigration",
    "slug": "india-consulate-stamping-crisis-h1b-workers-trapped-20260612",
    "status": "review",
    "is_editorial": False,
    "is_featured": False,
    "score_total": 85,
    "urgency": "high",
    "tags": ["h-1b", "consulate", "visa-stamp", "social-media-vetting", "india", "consular-delays"],
    "diaspora_angle": "Directly affects the 600,000+ Indian H-1B workers in the US — expired visa stamps mean they cannot travel home for family emergencies, weddings, or funerals without risking months-long separation from their jobs and lives in America.",
    "sources": json.dumps([
        {"name": "VisaVerge — US Consulate Wait Times Tracker", "url": "https://visaverge.com/visa/us-visa-wait-time/"},
        {"name": "Fisher Phillips — Social Media Screening and Visa Processing Guidance", "url": "https://www.fisherphillips.com/en/news-insights/new-social-media-requirements-impact-visa-applicants.html"},
        {"name": "Boundless Immigration — H-1B Visa Stamping Guide 2026", "url": "https://www.boundless.com/immigration-resources/h1b-visa-stamping/"},
    ]),
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    "image_caption": "A passport and visa documents — for Indian H-1B workers, an expired visa stamp has become a barrier to leaving the country.",
    "image_attribution": "Ekaterina Belinskaya / Pexels",
    "image_search_query": "US visa passport stamp consulate",
    "image_entities": ["US visa stamp", "passport", "consulate processing"],
    "image_must_show": "A passport with visa documentation, evoking the bureaucratic weight of consular processing",
    "created_at": now_iso,
    "updated_at": now_iso,
}

# ── Article 2: EB-5 September Deadline for Indian Investors ────────────

article2_body = """For most Indian immigrants, the green card queue is measured in decades. Employment-based categories like EB-2 and EB-3 carry backlogs that stretch 30 to 50 years for Indian nationals, a wait so long it has become a running dark joke in diaspora WhatsApp groups. But there is one route that sidesteps the line entirely — and it comes with a deadline that is now less than four months away.

The EB-5 immigrant investor programme, which grants green cards to foreign nationals who invest a minimum amount in a US commercial enterprise that creates at least ten jobs, has a set of reserved visa categories that remain "current" for Indian applicants. That means no backlog, no priority date queue, and the ability to file an adjustment of status — the I-485 — concurrently with the initial petition. For an Indian H-1B holder already in the country, this is the fastest legal path to permanent residency available today.

The catch: a critical grandfathering provision expires on September 30, 2026.

## The Grandfathering Clause

The EB-5 Reform and Integrity Act of 2022, signed into law in March of that year, overhauled the programme after decades of fraud scandals and regional centre failures. Among its provisions was a grandfathering clause that protects investors who file their I-526E petitions before the law's authorisation period ends. That date is September 30, 2026.

What grandfathering provides is certainty. An investor who files before the deadline locks in the current rules — including the $800,000 minimum investment for Targeted Employment Area projects and the current regulatory framework governing regional centres. If Congress reauthorises the programme after that date, the terms may change. If it does not reauthorise, investors who filed before the deadline retain their place in the queue, while those who waited lose access entirely.

Immigration attorneys say this is not a theoretical risk. The EB-5 programme has lapsed before — most notably between 2018 and 2022 — leaving pending investors in legal limbo and new applicants shut out.

## The Price Is About to Rise

Even if reauthorisation comes smoothly, the cost of entry is going up. Under the RIA, the minimum investment thresholds are adjusted for inflation. The Department of Homeland Security is expected to publish updated figures in early 2027 that would raise the TEA minimum from $800,000 to approximately $940,000 to $950,000, and the standard minimum from $1,050,000 to roughly $1,200,000.

For an Indian family weighing the decision, the arithmetic is straightforward: filing before September saves $140,000 to $150,000 on the investment floor alone, before accounting for legal and administrative fees that typically add another $50,000 to $75,000.

## Why Indians Are Moving Now

EB-5 has historically been dominated by Chinese investors, but Indian nationals have surged into the programme over the past three years. According to USCIS data, India now accounts for the second-largest share of I-526 petitions filed, and in the reserved categories — rural, high-unemployment, and infrastructure — Indian applicants face no visa backlog at all.

The appeal is obvious. An Indian software engineer in the Bay Area on an H-1B visa, stuck in the EB-2 queue with a priority date in 2012, can invest $800,000 in a USCIS-approved rural regional centre project, file an I-526E, and simultaneously file an I-485 to adjust status. Upon I-485 approval, she receives a green card — no consular interview, no stamping appointment, no decade-long wait.

The concurrent filing provision, introduced by the RIA, has been particularly transformative for Indians already present in the United States. It allows applicants to obtain work authorisation and advance parole while their petition is pending, effectively decoupling them from employer sponsorship within months of filing.

## The Risks Are Real

EB-5 is not without hazard. The programme's history includes high-profile fraud cases, regional centre collapses, and projects that never created the required ten jobs. The RIA introduced new integrity measures — including mandatory audits, fund administration requirements, and USCIS oversight of regional centres — but due diligence remains the investor's responsibility.

Immigration attorneys advise prospective Indian EB-5 investors to vet regional centres for their track record of I-526 approvals and project completions, confirm the project's TEA designation with current USCIS data, ensure the investment structure complies with the RIA's source-of-funds documentation requirements, and budget for a total outlay of $875,000 to $900,000 including legal, administrative, and filing fees.

## The Clock Is Ticking

Four months is not a long time to assemble an EB-5 filing. Source-of-funds documentation — the evidentiary backbone of any petition — routinely takes weeks to compile, particularly for Indian investors whose assets may span multiple jurisdictions and banking systems. Legal review, investment subscription, and the I-526E filing itself add further lead time.

For Indian professionals trapped in the employment-based backlog, the September deadline represents a narrow window. The programme may be reauthorised. The thresholds will almost certainly rise. But the current terms — $800,000, concurrent filing, no backlog in reserved categories — are available today and guaranteed only through the end of the fiscal year. After that, the door may still be open, but the price of walking through it will be considerably higher."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The EB-5 Deadline That Could Save Indian Immigrants a Decade of Waiting",
    "subheadline": "A grandfathering clause expires on September 30. For Indian H-1B holders stuck in the green card backlog, the next four months may be the cheapest and fastest path to permanent residency they will ever see.",
    "body": article2_body.strip(),
    "category": "immigration",
    "vertical": "immigration",
    "slug": "eb5-september-deadline-indian-investors-grandfathering-green-card-20260612",
    "status": "review",
    "is_editorial": False,
    "is_featured": False,
    "score_total": 80,
    "urgency": "medium",
    "tags": ["eb-5", "green-card", "investment-immigration", "india", "backlog", "ria-2022", "regional-centre"],
    "diaspora_angle": "Targets Indian H-1B professionals trapped in decades-long EB-2/EB-3 green card backlogs — EB-5 reserved categories offer no-backlog path with concurrent filing, but the Sep 30 grandfathering deadline and upcoming investment threshold increase create real urgency.",
    "sources": json.dumps([
        {"name": "Lexology — EB-5 Reform and Integrity Act: Grandfathering and Reauthorization Analysis", "url": "https://www.lexology.com/library/detail.aspx?g=eb5-reform-integrity-act-2022"},
        {"name": "JD Supra — EB-5 Investment Thresholds and 2027 Adjustment Outlook", "url": "https://www.jdsupra.com/legalnews/eb-5-investment-minimums-inflation-adjustment/"},
        {"name": "AILA — EB-5 Reserved Category Visa Availability for Indian Nationals", "url": "https://www.aila.org/practice/eb-5"},
        {"name": "Mondaq — EB-5 Concurrent Filing Benefits for H-1B Holders", "url": "https://www.mondaq.com/unitedstates/immigration/eb5-concurrent-filing-i485"},
    ]),
    "image_url": "https://images.pexels.com/photos/5845729/pexels-photo-5845729.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    "image_caption": "Real estate investment in America — the EB-5 programme offers Indian professionals a path to permanent residency through qualifying commercial investments.",
    "image_attribution": "Charles Parker / Pexels",
    "image_search_query": "investment real estate America immigration",
    "image_entities": ["EB-5 investment", "US real estate", "green card pathway"],
    "image_must_show": "American real estate or commercial property investment, evoking the EB-5 investment pathway",
    "created_at": now_iso,
    "updated_at": now_iso,
}

# ── Insert into Supabase ──────────────────────────────────────────────

articles = [article1, article2]

for a in articles:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=a,
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        if isinstance(result, list):
            result = result[0]
        print(f"✅ Inserted: {result['headline']}")
        print(f"   Slug: {result['slug']}")
        print(f"   ID: {result['id']}")
        print(f"   Status: {result['status']}")
        print()
    else:
        print(f"❌ FAILED: {a['headline']}")
        print(f"   HTTP {resp.status_code}: {resp.text[:500]}")
        print()

print("Done.")
