#!/usr/bin/env python3
"""
Immigration writer — 2026-06-30 01:00 PDT
Two articles:
1. USCIS backlog reaches 11.6 million cases
2. H-4 EAD processing crisis
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
        "headline": "Eleven Million Cases and Counting. The Green Card Machine Cannot Keep Up",
        "subheadline": "The USCIS backlog has tripled in a decade. For Indians in the employment-based queue, the agency that decides their future can barely process its own paperwork.",
        "slug": make_slug("uscis-backlog-11-million-cases-processing-crisis-indian-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian green card applicants face a compounding nightmare: not only are visa numbers unavailable for EB-2 India through September 2026, but USCIS processing delays add years to every step of an already decades-long queue.",
        "tags": ["uscis", "green-card", "backlog", "processing-times", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "American Immigration Council", "url": "https://americanimmigrationcouncil.org"},
            {"name": "Manifest Law — USCIS Processing Times June 2026", "url": "https://manifestlaw.com"},
            {"name": "Alonso & Alonso Law — Processing Times 2026", "url": "https://alonsoandalonsolaw.com"},
            {"name": "WR Immigration — EB-2 India Analysis", "url": "https://wolfsdorf.com"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": """The number that should alarm every Indian professional waiting for a green card is not a priority date or a visa bulletin cutoff. It is 11.6 million — the total pending cases sitting in USCIS's pipeline as of the most recent quarter for which data are available.

That figure, drawn from the American Immigration Council's new interactive dashboard, represents a tripling of the agency's backlog over the past decade. In the first quarter of fiscal year 2016, USCIS had roughly 3.5 million pending cases. By the fourth quarter of fiscal year 2025, that number had ballooned to 11.6 million. And the trajectory is still climbing.

## The numbers behind the dysfunction

Current USCIS processing times, updated in June 2026, tell a story of institutional overload:

- **I-485 (Employment-based Adjustment of Status):** 9 to 35 months
- **I-140 (Immigrant Petition for Alien Worker):** 2.5 to 25.5 months for regular processing
- **PERM Labor Certification (Department of Labor):** 483 days for analyst review
- **I-765 (Employment Authorization Document):** 1 to 19.5 months
- **I-131 (Advance Parole travel document):** 16 to 22 months
- **N-400 (Naturalization):** 8 to 13 months

Premium processing — available for I-140 and I-129 petitions — now costs $2,965, up from previous levels. For a 15-business-day guarantee, employers are paying more than ever. For everything else, there is no expedited option. You wait.

The efficiency ratio — a measure of how many cases USCIS completes relative to new filings — hit a record low of 0.66 during the second quarter of fiscal year 2021. That quarter alone, the agency received 2.6 million applications but processed only 1.7 million, adding nearly 867,000 cases to the backlog in three months.

By the end of the Biden administration, clearing the backlog at prevailing processing capacity would have taken 9.4 months. Under the current administration, the situation has worsened: an additional 2 million cases accumulated in 2025, and at the most recent processing rate, it would take 13.8 months to clear the pile — if no new applications were filed at all.

## Why this hits Indian applicants hardest

For most immigrants, the USCIS backlog is an inconvenience. For Indian nationals in the employment-based queue, it is a compounding catastrophe.

Consider the timeline facing someone starting the green card process today. A PERM labour certification takes 483 days. An I-140 petition takes up to 25.5 months at regular processing. An I-485 adjustment of status takes 9 to 35 months — but can only be filed when a visa number becomes available.

And the visa numbers are not available. EB-2 India has been marked "Unavailable" since the Department of State confirmed the fiscal year 2026 annual limit was exhausted. EB-1 India retrogressed to October 15, 2022. EB-3 India crawled forward to January 1, 2014 — meaning applicants with priority dates after that remain frozen.

The practical effect is stacking: a PERM that takes 16 months, an I-140 that takes two years, and then a wait of potentially a decade or more for a visa number. Each step adds its own processing delay to a queue that was already measured in decades.

WR Immigration, a firm specialising in employment-based cases, noted that worldwide demand for employment-based visas has surged, meaning the "spillover" numbers that once gave India occasional forward movement have all but disappeared. "Retrogressions and periods of unavailability are likely to become more common," the firm wrote. "Many applicants may face waits measured not merely in years, but potentially decades."

## The feedback loop

There is a deeper structural problem. USCIS is funded primarily through application fees, not congressional appropriations. When backlogs grow, the agency raises fees to hire more staff. But higher fees deter some applicants, reducing revenue, which constrains hiring. Meanwhile, policy shifts — from adjustment-of-status restrictions to the push toward consular processing — redirect workload without adding capacity.

The American Immigration Council's analysis found that completions began falling behind new filings in 2020 and 2021, driven by a combination of pandemic disruption and policy changes under the first Trump administration that "severely limited the agency's capacity and efficiency." The Biden administration made progress but never fully caught up. Now, with the second Trump administration introducing additional restrictions and deprioritising certain case types, the gap is widening again.

## What it means for you

If you are an Indian national with an approved I-140 and a priority date that might become current in the next few years, the backlog means your actual green card could arrive years after your visa number becomes available. Even ancillary benefits — the Employment Authorization Document, Advance Parole, the ability to change employers under AC21 — require their own USCIS processing timelines of months to over a year.

The system that promises permanence is itself impermanent: shifting rules, rising fees, and a machinery that processes at a pace no engineer would call acceptable. Eleven million cases. Thirteen months to clear them. And every quarter, the pile grows."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Her Degree Is From Stanford. Her Work Permit Says 'Pending'",
        "subheadline": "More than 90 per cent of H-4 EAD holders are Indian. Renewal processing now takes five to seven months. For thousands of families, the gap between permits is a gap between paycheques.",
        "slug": make_slug("h4-ead-renewal-crisis-indian-families-work-permit-gap"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Over 90 per cent of H-4 EAD recipients are Indian nationals, mostly women with advanced degrees who paused careers to accompany H-1B spouses. Processing delays of five to seven months force them into involuntary unemployment and threaten family finances.",
        "tags": ["h4-ead", "h1b", "immigration", "work-permit", "indian-families"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Cato Institute — Immigration Reform: H-4 Work Permanent", "url": "https://www.cato.org/blog/immigration-reform-make-h-4-visa-holders-permission-work-permanent"},
            {"name": "Khandelwa Law — H-4 Visa EAD Latest News", "url": "https://khandelwalaw.com"},
            {"name": "VisaVerge — Supreme Court Preserves H-4 EAD Rights", "url": "https://visaverge.com"},
            {"name": "Observer Research Foundation — H-4 Work Authorisation", "url": "https://orfonline.org"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/USCIS_EAD_card.jpg/1280px-USCIS_EAD_card.jpg",
        "image_caption": "A USCIS Employment Authorization Document card",
        "image_attribution": "Wikimedia Commons",
        "body": """She has a master's degree. She held a senior position at a Fortune 500 company before she moved to the United States to join her husband on his H-1B visa. She is legally present, legally married, and legally authorised to work — in theory. In practice, she has been waiting five months for USCIS to renew a small plastic card that says she can.

The Employment Authorization Document, or EAD, issued to certain H-4 visa holders is one of the quietest lifelines in the American immigration system. It allows spouses of H-1B workers — those who have an approved I-140 immigrant petition or an H-1B extension beyond the standard six-year limit — to hold a job while their family waits in the green card queue. Over 120,000 H-4 visa holders have received these cards since the programme began in 2015. Roughly 90,000 are currently employed. And over 90 per cent of them are from India.

## The renewal trap

The problem is not eligibility. It is timing. Under current USCIS processing timelines, H-4 EAD renewals take five to seven months. That window can stretch longer depending on the service centre handling the case and the security screenings introduced in late 2025.

For the person waiting, those months translate directly into lost income. Employers face I-9 verification challenges when a work permit lapses mid-employment. Some employers place the worker on unpaid leave. Others terminate the position outright, unwilling to hold a role open for half a year with no guaranteed resolution.

"It's not uncommon for cases to remain pending for five to seven months," immigration attorneys note. "That window can vary by service centre, workload, and the new security screenings."

Families that relied on two incomes to cover rent, childcare, and car payments in cities like San Jose, Seattle, or Dallas suddenly find themselves operating on one. Many H-4 EAD holders are women who left careers in India to join their spouses. The work permit was the mechanism that allowed them to rebuild professionally in America. Its expiration — even temporary, even bureaucratic — dismantles that structure entirely.

## A right that nearly wasn't

The H-4 EAD programme has never been secure. Created by the Obama administration in 2015, it was immediately challenged by Save Jobs USA, a group of American IT workers who argued that the Department of Homeland Security had exceeded its statutory authority. The first Trump administration announced its intention to repeal the rule in 2017 but could never produce sufficient justification. Biden withdrew the proposed repeal in 2021.

The most recent legal threat came when Save Jobs USA asked the Supreme Court to review the D.C. Circuit's 2024 decision affirming DHS's authority to grant employment authorisation to qualifying H-4 spouses. The Court declined to hear the case, leaving the programme intact.

But "intact" and "functional" are not the same thing.

VisaVerge's analysis found that Indian families have been most affected: Indians account for over 71 per cent of H-1B visa holders, and many H-4 spouses are women who paused careers when they moved to the United States. The math is straightforward — the programme exists because of the green card backlog. If EB-2 India applicants could get their green cards in two years, their spouses would have permanent work authorisation. Instead, families wait a decade or more, and the stopgap work permit must be renewed, re-adjudicated, and re-approved at intervals that USCIS cannot reliably meet.

## The case for permanence

The Cato Institute, a libertarian think tank not typically associated with expansive immigration advocacy, published a policy brief arguing that H-4 work authorisation should be made permanent by statute.

The argument is practical, not sentimental. H-4 EAD holders work in technology, healthcare, finance, consulting, and academia. Their earnings support local economies, generate tax revenue, and reduce the financial strain on families already bearing the costs of the green card process — PERM applications, I-140 filings, attorney fees, and now premium processing at $2,965 per petition.

Making the work permit permanent would eliminate the renewal cycle entirely. It would remove the five-to-seven-month processing gap, the I-9 compliance headaches for employers, and the annual anxiety for families who have done nothing wrong except wait in a queue the government created.

## What families face now

Congress shows no appetite for legislative reform on H-4 work authorisation. The programme exists entirely through executive regulation, which means it can be weakened, delayed, or de facto suspended through processing slowdowns alone. No political appointee needs to sign a repeal order. The backlog does the work.

For Indian families on H-1B visas, the H-4 EAD is the difference between a household with two working professionals and one with a single earner. It is the difference between a spouse who builds an American career and one who watches her credentials atrophy. And right now, that difference rests on a renewal application sitting in a pile at a USCIS service centre, somewhere between five months old and seven months away from a decision.

The Supreme Court said DHS can issue the card. USCIS just cannot seem to process it on time."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
