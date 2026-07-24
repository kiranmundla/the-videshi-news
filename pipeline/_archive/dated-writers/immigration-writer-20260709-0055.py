#!/usr/bin/env python3
"""Immigration writer — July 9, 2026, 00:55 AM PT run."""

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

# ─────────────────────────────────────────────────────────
# ARTICLE 1: EB-2 India Unavailable — July Visa Bulletin
# ─────────────────────────────────────────────────────────

article1_body = """The State Department's July 2026 visa bulletin did not merely disappoint Indian green card applicants. It slammed the door shut on the single most-used pathway to permanent residency and locked it until at least October.

EB-2 India — the employment-based second preference category that covers professionals with advanced degrees or exceptional ability — is now marked "Unavailable" for the remainder of fiscal year 2026. Every visa number allocated to Indian nationals in that category has been used. No adjustment of status applications can be approved. No immigrant visas can be issued. The next chance arrives on October 1, when the new fiscal year's numbers reset.

It is not just EB-2. The July bulletin delivered a triple blow across virtually every employment-based category for India.

## Three categories down, one barely breathing

EB-1 India, once the fastest lane for priority workers, retrogressed two months — from a final action date of December 15, 2022, back to October 15, 2022. The State Department's own commentary warns that further retrogression, or even complete unavailability, may follow if India's pro-rated EB-1 limit is exhausted before September 30. Self-petitioners under EB-1A and multinational managers under EB-1C should treat the current window as fragile.

EB-3 India, the skilled workers category, offered cold comfort. Its final action date inched forward from December 15, 2013, to January 1, 2014 — half a month of progress against a backlog that now stretches beyond twelve years. An Indian professional who filed their PERM labour certification in January 2014 is only now reaching the front of the approval queue.

EB-5 unreserved — the investor visa pathway outside the set-aside pools — also went unavailable for India, mirroring EB-2. The only green card pathway still showing "Current" for Indian nationals is the EB-5 set-aside categories: rural, high-unemployment, and infrastructure investments, each requiring a minimum $800,000 to $1,050,000 capital commitment.

## The October reset is not the rescue it sounds like

Immigration attorneys are already counselling clients to prepare documentation now so they can file the moment FY 2027 numbers become available. The State Department has signalled that EB-2 India's final action date will advance to at least the May 2026 level when October arrives. But there is a structural problem that no single reset can fix.

Worldwide demand from "Rest of World" applicants — those not subject to per-country caps — is now consuming virtually all available employment-based immigrant visa numbers. WR Immigration, a major business immigration firm, warned in a May advisory that India EB-2 and EB-3 categories are likely to see "extremely limited visa availability" in FY 2027 as well. The brief October bounce, in other words, may be followed by another freeze.

## What this means for Indian professionals

For the roughly 400,000 Indian nationals in the EB-2 pipeline, the practical implications are immediate. No green card approvals until at least October. No ability to change employers freely without jeopardising a pending case. Continued dependence on H-1B renewals, which themselves face heightened scrutiny under the current administration's fraud probes.

The EB-2-to-EB-3 "downgrade" strategy — long discussed in immigration circles as a workaround — is back on the table for beneficiaries whose EB-3 priority date is now current. But as VisaNation's legal team noted, this is a complex legal decision that depends on individual case posture, and it carries its own risks.

For those with a viable EB-1 pathway, the cross-category analysis becomes urgent. Filing an EB-1A self-petition, which does not require employer sponsorship, has surged among Indian professionals in recent months. But with EB-1 India itself under threat of unavailability, that window too may not stay open.

The July visa bulletin is the clearest signal yet that the employment-based green card system, built for an era when demand was more evenly distributed, cannot absorb the scale of Indian talent seeking permanent residency in the United States. The per-country cap — which limits India to roughly 7 per cent of employment-based visas despite contributing the overwhelming majority of applicants — remains the structural bottleneck. Legislation to eliminate or raise those caps has stalled repeatedly in Congress.

Until that changes, the math does not work. And for the hundreds of thousands of Indian professionals waiting, October 1 is not a solution. It is a reset button on a clock that keeps running out."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Eighty-Three Days of Nothing. The July Visa Bulletin Just Shut Down EB-2 India",
    "subheadline": "EB-2 unavailable. EB-1 retrogressing. EB-5 frozen. The July 2026 visa bulletin closed nearly every green card pathway for Indian professionals until at least October.",
    "slug": make_slug("eb2-india-unavailable-july-visa-bulletin-green-card-frozen"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Hundreds of thousands of Indian H-1B holders and their families face a complete freeze on green card approvals through September, with no guarantee the October reset will bring meaningful relief.",
    "tags": ["eb-2", "visa-bulletin", "green-card", "uscis", "immigration", "india", "eb-1", "eb-3", "eb-5", "per-country-cap"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "WR Immigration", "url": "https://wolfsdorf.com/united-states-eb-2-india-unavailable-through-september-30-2026/"},
        {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/news/2026/06/18/july-2026-visa-bulletin-uscis-continues-to-use-final-action-dates-for-eb-filings-causing-further-retrogression-for-india/"},
        {"name": "VisaNation Law Group", "url": "https://www.immi-usa.com/visa-bulletin/"},
        {"name": "BAL Immigration", "url": "https://bal.com/"},
        {"name": "U.S. Department of State Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Close-up of an open passport displaying various visa stamps",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────────────────
# ARTICLE 2: Social Security Totalization Gap
# ─────────────────────────────────────────────────────────

article2_body = """Every two weeks, a deduction labelled FICA appears on the pay stub of every Indian H-1B worker in the United States. It is 6.2 per cent of their salary, up to a ceiling of $168,600 in 2026, matched dollar for dollar by their employer. It funds Social Security — the federal pension system that pays retirement, disability, and survivor benefits to qualifying workers.

There is a catch. To qualify for any benefit at all, a worker must accumulate 40 credits, which roughly translates to ten years of covered employment. Leave the country with 39 credits and the answer is the same as leaving with four: nothing.

For Indian professionals on temporary work visas, this is not a theoretical concern. It is a structural trap built into the intersection of two systems — American payroll taxation and Indian immigration backlogs — that no one has fixed in over two decades of trying.

## The scale of the loss

An Indian-national H-1B worker earning $140,000 a year pays approximately $8,680 in employee-side Social Security taxes. The employer matches that amount, bringing the combined annual contribution to roughly $17,360. Over a seven-year stint — the typical duration for someone who enters on an H-1B and fails to secure a green card before the visa's six-year limit plus extensions — the combined contributions exceed $121,000.

If that worker leaves the US without reaching 40 credits, every dollar is forfeit. They cannot withdraw it. They cannot transfer it. They cannot combine it with pension credits earned in India.

NASSCOM, the Indian technology industry body, has estimated that Indian nationals and their employers collectively contribute approximately $4 billion per year to the US Social Security system. A substantial portion of that sum will never be returned as benefits.

## Why India has no totalization agreement

The mechanism that prevents this outcome for workers from 30 other countries is called a totalization agreement. These bilateral treaties do two things: they prevent dual taxation on payroll for short-term workers, and they allow workers to combine credits earned in both countries to qualify for either nation's pension.

The United States has active totalization agreements with countries including Australia, Canada, Germany, Japan, South Korea, and the United Kingdom. India is not on the list. Neither is China, though China's case is complicated by limited provisions under existing frameworks.

The gap is not for lack of effort. India has pursued a totalization agreement with the US for years. In 2025, as both countries prepared for bilateral trade agreement negotiations, the Hindu Business Line reported that India intended to push for a totalization pact alongside the BTA, framing it as a services-sector demand parallel to tariff discussions. US Treasury Secretary Scott Bessent acknowledged at the time that India was among the first countries likely to reach a trade deal.

But totalization and trade operate on different tracks. The Social Security Administration handles totalization agreements separately from trade negotiations, and the process involves actuarial analysis, legislative review, and bureaucratic coordination that can stretch for years. No formal agreement has materialised.

## The EB-2 freeze makes it worse

The timing could not be less favourable. With EB-2 India now unavailable through September 30, 2026, and the green card backlog stretching beyond a decade in every employment-based category, more Indian professionals are likely to exhaust their H-1B tenure without obtaining permanent residency.

Some will pivot to EB-1 self-petitions. Some will look to EB-5 investor visas. But a significant number will make the calculation that many before them have made: return to India, or move to a country — Canada, the UK, Germany, Australia — that offers a clearer path to residency.

Each one who leaves before the ten-year mark walks away from tens of thousands of dollars in Social Security contributions they will never see again. Those who do stay long enough to reach 40 credits face a different problem: the benefit they eventually receive may be reduced by the Windfall Elimination Provision, which cuts Social Security payments for workers who also receive a pension from employment not covered by Social Security — including Indian government service or EPF-eligible employment.

## What Indian professionals can do

Tax advisors and immigration attorneys suggest several strategies, none of them ideal. Workers close to the 40-credit threshold — say, at 36 or 37 credits — may be able to pick up remaining credits through short-term US-source self-employment, such as consulting for a US client through an LLC, provided they remain authorised to perform the work. A single calendar year that straddles a mid-year departure can still earn up to four credits if wages exceed $7,240.

For those further from the threshold, the options are limited. Indian Provident Fund contributions accumulate independently under the International Workers category for returning professionals, building an Indian pension that is separate from — and unaffected by — the lost US credits.

The absence of a totalization agreement is not a new grievance. But with every passing year of green card backlog, with every fiscal year that shuts down EB-2 India, and with every H-1B renewal that keeps workers in a holding pattern, the $4 billion annual cost grows harder to justify as anything other than a structural transfer of wealth from Indian workers to a pension system that was never designed for them."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "You Paid $120,000 in Social Security Taxes. India Has No Deal to Get Any of It Back",
    "subheadline": "Indian H-1B workers and their employers pour an estimated $4 billion a year into the US Social Security system. Without a totalization agreement, most of that money is gone for good.",
    "slug": make_slug("social-security-totalization-india-h1b-workers-lost"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Every Indian professional on an H-1B pays thousands in Social Security taxes each year with no guarantee of ever collecting. As green card backlogs force more workers to leave before ten years, the losses mount.",
    "tags": ["social-security", "totalization-agreement", "h1b", "india", "fica", "payroll-tax", "nasscom", "green-card", "bilateral-trade"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/india-hopes-to-pursue-social-security-pact-with-us-simultaneously-with-trade-deal/article69245267.ece"},
        {"name": "IRS — Totalization Agreements", "url": "https://www.irs.gov/individuals/international-taxpayers/totalization-agreements"},
        {"name": "Greenback Tax Services", "url": "https://www.greenbacktaxservices.com/knowledge-center/totalization-agreements/"},
        {"name": "CountryTaxCalc", "url": "https://www.countrytaxcalc.com/guides/india-to-usa-tax-guide"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0b/PD_social_security_card_2.png",
    "image_caption": "A US Social Security card, the document that represents the federal pension system Indian H-1B workers pay into",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}

# ─────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
