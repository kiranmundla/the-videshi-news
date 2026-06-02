#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-02 00:00 UTC run"""
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

# Verify images return 200 with image content-type and > 5KB
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except Exception:
        return False

img1 = "https://images.pexels.com/photos/6580465/pexels-photo-6580465.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img2 = "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

for url in [img1, img2]:
    if not verify_image(url):
        print(f"⚠️ Image failed verification: {url}")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Seventy-Two Billion Dollars for ICE — The Bill That Broke the Senate Is Back on Track",
        "subheadline": "Trump's 'anti-weaponization' fund nearly sank the biggest immigration enforcement package in a generation. On Monday, the White House blinked.",
        "slug": make_slug("72-billion-ice-reconciliation-anti-weaponization-fund-senate"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The $72 billion reconciliation package funds ICE and Border Patrol through 2029 — meaning more worksite audits, more visa overstay enforcement, and a harder environment for anyone in the US immigration system. For Indian H-1B holders, the expanded enforcement apparatus raises the stakes on every status transition, every employer change, and every gap between visa types.",
        "tags": ["immigration-enforcement", "reconciliation", "ice-funding", "senate", "anti-weaponization"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/trumps-weaponization-fund-put-hold-after-fierce-opposition-congress-2026-06-01/"},
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/trump-admin-backs-off-controversial-2b-fund-clearing-path-gop-restart-agenda"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/01/politics/gop-lawmakers-doj-anti-weaponization-fund/index.html"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/05/30/irs-weaponization-fund-talks-gumming-up-works-immigration-enforcement-funding/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img1,
        "body": """The United States Senate returned from Memorial Day recess on Monday to find what it left behind: a $72 billion immigration enforcement bill, a furious Republican caucus, and a White House that had finally decided to stop picking this particular fight.

The Department of Justice announced it would comply with a Virginia federal court order halting the nearly $1.8 billion "anti-weaponization" fund — a settlement-turned-slush-fund that had, until Monday, single-handedly frozen the largest immigration enforcement funding package in recent memory. Senate Majority Leader John Thune made it plain: the fund needed to die before the reconciliation bill could live.

## What the $72 Billion Buys

The budget reconciliation package allocates more than $30.7 billion to Immigration and Customs Enforcement, $22.6 billion to Customs and Border Protection, and $2.5 billion in Department of Homeland Security appropriations — all extended through fiscal year 2029. That is not a one-year budget bump. It is a structural expansion of the enforcement apparatus that will outlast this administration.

For perspective: ICE's entire FY2025 budget was roughly $9.5 billion. This package more than triples annual enforcement spending and locks it in for three years.

## How a $1.8 Billion Fund Killed a $72 Billion Bill

The story of how the package stalled is almost farcical. The DOJ's "anti-weaponization" fund — born from a legal settlement resolving Trump's $10 billion lawsuit against the IRS over his leaked tax returns — was meant to compensate people who claimed government persecution. But senators quickly realized the fund could pay out to people convicted of assaulting police officers during the January 6, 2021, Capitol breach.

The Republican caucus erupted. Senator Ted Cruz described a closed-door meeting with acting Attorney General Todd Blanche as "angry," with "at least half" of the 45 senators present "blasting" him. Former GOP leader Mitch McConnell called the fund "utterly stupid, morally wrong."

The Senate had planned to stay late on May 21 to vote. Instead, leadership canceled votes and sent everyone home for recess. Trump's June 1 deadline passed without action.

## Why Indian Americans Should Pay Attention

The immediate political drama is Washington-internal. The downstream effects are not.

More than $30 billion for ICE means expanded worksite enforcement operations — precisely the kind of audits that have historically swept up Indian IT consulting firms. It means more resources for visa overstay investigations, at a time when USCIS is already using a 12-factor discretionary test on adjustment of status applications. It means more detention capacity, more agents, and more infrastructure for the kind of enforcement environment that makes every H-1B transfer, every I-485 interview, and every consular appointment feel higher-stakes.

The package also contains no provisions for legal immigration reform. No green card backlog relief. No H-1B modernization. No recapture of unused visa numbers. The $72 billion flows exclusively to enforcement, border infrastructure, and detention.

For the roughly 400,000 Indian nationals in the EB-2 and EB-3 green card backlog, the message is unmistakable: the government is spending generational money on enforcement while their applications age into their second decade.

## What Happens Next

With the anti-weaponization fund sidelined — temporarily, the White House insists — the Senate can restart the reconciliation process this week. Democrats plan to force votes on amendments targeting the fund, putting swing-state Republicans on the record. Senator Chuck Schumer promised "no escape hatch."

The bill's passage is now considered likely, though not guaranteed. If it clears the Senate, reconciliation with the House version follows. The enforcement money could start flowing within weeks of final passage.

For Indian Americans navigating the immigration system: the funding environment is about to get significantly more aggressive. Plan accordingly."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Gate Just Closed — EB-2 India Is Frozen Until October and USCIS Won't Let You Use the Filing Dates",
        "subheadline": "June's visa bulletin delivers a double blow: Final Action Dates mandatory for all employment-based filings, and EB-2 India's annual quota is exhausted four months early.",
        "slug": make_slug("eb2-india-frozen-final-action-dates-june-visa-bulletin"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the tens of thousands of Indian tech workers with EB-2 priority dates from 2013 or earlier, June's visa bulletin is a concrete reminder of how the per-country cap system works in practice: your slot was filled months ago, the gate is shut, and the only thing to do is wait for October 1.",
        "tags": ["visa-bulletin", "eb2-india", "green-card-backlog", "uscis", "final-action-dates"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-and-priority-dates/adjustment-of-status-filing-charts-from-the-visa-bulletin"},
            {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/news/2026/05/26/eb-2-india-per-country-limit-reached-for-fy-2026-visa-issuance-and-approvals-paused-through-september-30/"},
            {"name": "Department of State Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
            {"name": "Berry Appleman & Leiden", "url": "https://bal.com/immigration-news/visa-bulletin-update-final-action-dates-to-be-used-for-employment-based-applicants-in-june/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img2,
        "body": """Two things happened this month that, together, form the most restrictive employment-based green card environment Indian nationals have faced all fiscal year. The first: USCIS confirmed that for June 2026, all employment-based adjustment of status filers must use the Final Action Dates chart — not the more generous Dates for Filing chart. The second: the State Department formally announced that EB-2 India's per-country allocation for fiscal year 2026 has been fully exhausted, with no new approvals possible until October 1.

If you are an Indian national with a pending I-485 in the EB-2 category, your case is frozen. Not delayed. Frozen.

## The Numbers That Matter

The June 2026 Visa Bulletin sets the following Final Action Dates for India:

- **EB-1**: December 15, 2022
- **EB-2**: September 1, 2013 (functionally irrelevant — quota exhausted)
- **EB-3**: December 15, 2013
- **EB-3 Other Workers**: December 15, 2013

Had USCIS allowed the Dates for Filing chart, Indian EB-2 and EB-3 applicants with priority dates before January 15, 2015 could have submitted I-485 applications to at least secure a place in the queue and obtain interim benefits — employment authorization documents and advance parole. That option is off the table.

This is the sixth time this fiscal year USCIS has mandated Final Action Dates for employment-based filings. The agency briefly used Dates for Filing earlier in the year, but that window has closed decisively.

## What EB-2 India Exhaustion Actually Means

The Immigration and Nationality Act caps employment-based immigration at 140,000 visas annually, with no single country eligible for more than 7 percent — roughly 9,800 visas. India's EB-2 demand dwarfs that figure by orders of magnitude.

With the quota hit, here is what happens until September 30:

**No consular immigrant visa issuance.** U.S. embassies and consulates in India will not issue EB-2 immigrant visas for the remainder of the fiscal year.

**No I-485 approvals.** USCIS cannot approve pending adjustment of status applications in EB-2 India, regardless of how complete the file is or whether an interview has already occurred.

**Filing still accepted — in theory.** USCIS says it will continue to accept new EB-2 India I-485 filings that are current under the bulletin. But "accepted" means the application sits in a drawer until October. No approval. No interview scheduling. No forward motion.

## The 13-Year Wait Embedded in the Date

The EB-2 India Final Action Date of September 1, 2013 means that only applicants whose PERM labor certification or I-140 petition was filed before that date are even theoretically eligible for green card approval. An applicant who filed in September 2013 has been waiting 13 years — and they are the lucky ones at the front of the line.

Behind them, the queue stretches for years. An Indian national who filed an EB-2 petition in 2020 is looking at a wait that most immigration attorneys privately estimate at 15 to 25 additional years under current law.

## The Strategic Calculus

For Indian applicants stuck in the EB-2 pipeline, several options are being weighed:

**EB-2 to EB-3 downgrade:** The EB-3 India Final Action Date (December 15, 2013) is actually ahead of EB-2 in some scenarios, and the category is not yet exhausted for FY2026. Some attorneys are advising clients with flexible job requirements to file new PERM applications in EB-3 — trading a "higher" preference category for actual forward movement.

**EB-1A self-petition:** The extraordinary ability category remains current for India at December 15, 2022 — nearly a decade ahead of EB-2. The gold rush toward EB-1A filings continues, though the bar for approval remains high and RFE rates are climbing.

**Wait for October:** The fiscal year resets on October 1, 2026. Fresh EB-2 numbers will be allocated and the queue will resume. The July 2026 Visa Bulletin, expected in mid-June, will indicate how the State Department plans to manage the restart.

## The Bigger Picture

June's double restriction — mandatory Final Action Dates plus EB-2 exhaustion — is not an anomaly. It is the system working exactly as Congress designed it in 1990, when per-country caps were set and India's tech workforce was a fraction of its current size. The 7 percent cap was written for a world where no single country would dominate employment-based immigration demand. That world no longer exists.

Until Congress acts — through legislation like the EAGLE Act, the Fairness for High-Skilled Immigrants Act, or any bill that eliminates or raises per-country caps — the annual cycle will repeat: forward movement in early fiscal year, exhaustion by spring, freeze through September, reset in October.

For Indian Americans in the green card queue, June is the cruelest month. October is four months away."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
