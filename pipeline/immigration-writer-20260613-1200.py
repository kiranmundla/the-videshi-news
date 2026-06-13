#!/usr/bin/env python3
"""Videshi Immigration News Writer — June 13, 2026 batch"""
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
        "headline": "The Green Card Queue Is Shrinking — What 62,000 Indian Workers Need to Know",
        "subheadline": "New USCIS inventory data shows India's EB-1 backlog posted its steepest single-month drop on record, EB-2 has declined for seven straight months, and the first 2015 priority dates have entered the system.",
        "slug": make_slug("green-card-queue-shrinking-uscis-i485-inventory-india-eb1-eb2"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the roughly 62,000 Indian nationals with pending I-485 applications across EB-1, EB-2, and EB-3, this data is the first sustained evidence that the queue is actually moving — not just in the visa bulletin's theoretical dates, but in the physical inventory of cases USCIS is processing.",
        "tags": ["green-card", "eb-1", "eb-2", "eb-3", "uscis", "i-485", "visa-bulletin", "backlog"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS Immigration and Citizenship Data", "url": "https://www.uscis.gov/tools/reports-and-studies/immigration-and-citizenship-data"},
            {"name": "Green Card Clock", "url": "https://greencardclock.com/blog/uscis-eb-i485-inventory-april-2026"},
            {"name": "Manifest Law — EB-1 Priority Date for India June 2026", "url": "https://manifestlaw.com/what-is-the-current-eb-1-priority-date-for-india/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hand holds an open passport with visa stamps — a familiar sight for Indian workers navigating the US immigration system",
        "image_attribution": "Pexels",
        "body": """On June 10, USCIS quietly published its employment-based I-485 pending inventory as of April 3, 2026 — the third batch of backlog data to land in a single week. Buried in the spreadsheets is something that the doom-scrolling immigration forums have largely missed: the queue is actually getting smaller.

India EB-1, the category used by researchers, multinational executives, and self-petitioning professionals claiming extraordinary ability, dropped by 1,475 cases in a single month — from 22,325 to 20,850. That is the steepest one-month decline in USCIS's entire published data series for any India employment-based category.

India EB-2, the workhorse category that covers most H-1B-to-green-card transitions, fell to 25,780 pending cases, down 471 from March. It has now declined every month since October 2025 — seven consecutive months — with the total dropping from 28,365 to 25,780 over that stretch.

And for the first time, five cases with a 2015 priority date appeared in the India EB-2 report. Five cases is a tiny number, and that is not an accident. It means the filing date has crossed into calendar year 2015, but only barely.

## What the numbers actually mean

| Category | March 2026 | April 2026 | Change |
|---|---|---|---|
| India EB-1 | 22,325 | 20,850 | −1,475 |
| India EB-2 | 26,251 | 25,780 | −471 |
| India EB-3 | 16,699 | 16,084 | −615 |
| **Total India EB** | **65,275** | **62,714** | **−2,561** |

The worldwide employment-based I-485 pending inventory fell to 172,701, down 1,247 from March's 173,948. India accounts for the majority of that decline.

A closer look at the EB-1 numbers tells a revealing story. The drop was concentrated almost entirely in the 2022 priority date cohort, which shrank from 11,645 to 9,060 — a reduction of 2,585 cases. The 2023 cohort, by contrast, grew from 6,741 to 8,221, adding 1,480 new filers. The pattern is consistent with the final action date actively clearing 2022 cases faster than new 2023 filers are entering the system.

## The 2014 wall and the 2015 milestone

For EB-2 India, the dominant feature remains the 2014 cohort: 17,421 cases, up 537 from March. This is not a contradiction with the overall decline. The filing date has covered all of 2014 for months, meaning anyone with a 2014 priority date who is ready to file can do so. New filers keep entering. But the final action date is still moving through 2013, so almost no 2014 cases are being approved yet. The 2013 cohort, by contrast, lost 924 cases this month as approvals cleared it.

Think of it as a waiting room with the entry door open and the exit door still closed. The five 2015 cases that appeared for the first time are standing just inside the entrance, watching the 17,421 people with 2014 dates who got there first.

For anyone with a priority date later in 2015 — or 2016, or 2017 — the filing date has not reached those months yet. Your case is not in this report. The real gate is the 2014 wall. When it thins, the filing date will push further into 2015 and more of that cohort will enter the queue.

## Why this matters to you

Pending inventory is a stock, not a wait time. It tells you how many cases are in front of you, not when you will be approved. The monthly visa bulletin, which controls the final action dates, is still the ultimate gatekeeper. And the June 2026 bulletin was not kind: EB-1 India's final action date retrogressed to December 15, 2022, and EB-2 India was marked "Unavailable" — meaning no new green cards are being issued in that category this month.

So the queue is shrinking, but the exit is temporarily blocked. That is a strange combination, and it is worth understanding the mechanics. Cases drop out of the pending inventory for several reasons: approvals, denials, withdrawals, and administrative closures. The EB-1 decline looks approval-driven, given the concentration in the 2022 cohort that aligns with recent final action date movement. The EB-2 decline, with the category marked unavailable, likely reflects a mix of withdrawals, re-categorisations, and people abandoning applications.

For the roughly 62,000 Indian nationals still in this queue, the sustained downward trend is the first structural signal that the system is processing faster than it is accumulating. Whether that holds depends on two things: the pace of new EB-1A and NIW filings (which have surged in recent years as Indians seek alternatives to the EB-2 backlog), and whether USCIS can maintain its current adjudication throughput under political and budgetary pressure.

The data does not tell you when your green card will arrive. But for the first time in years, it tells you the line is getting shorter."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Made the NIW a Coin Flip — What Indian Professionals Need to Know",
        "subheadline": "National Interest Waiver approval rates have cratered from 96 per cent to 55 per cent in three years, with the most recent quarter at 35.7 per cent. The alternative green card route that thousands of Indians adopted is now the hardest it has ever been.",
        "slug": make_slug("niw-approval-rate-collapse-uscis-indian-professionals"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The NIW became the favoured escape route for Indian professionals stuck in the EB-2 backlog — a way to self-petition without employer sponsorship and skip the PERM labor certification. With approval rates now below 56 per cent and still falling, thousands of Indians who filed or are preparing to file face a fundamentally different bet.",
        "tags": ["niw", "eb-1a", "green-card", "uscis", "immigration", "indian-professionals"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "LexBlog — What Recent USCIS Data Means for EB-2 NIW, EB-1A Petitioners", "url": "https://www.lexblog.com/2026/06/11/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners/"},
            {"name": "USCIS Immigration and Citizenship Data — I-140 Adjudications", "url": "https://www.uscis.gov/tools/reports-and-studies/immigration-and-citizenship-data"},
            {"name": "Colombo & Hurd — Strategic Path to Green Cards for Indian Professionals", "url": "https://colombohurdlaw.com/"},
            {"name": "PACER — Mukherji v. Miller, D. Neb. Jan. 28, 2026", "url": "https://www.pacermonitor.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8112126/pexels-photo-8112126.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A lawyer reviews immigration petition paperwork at a desk — the kind of meticulous case-building that NIW applicants now need more than ever",
        "image_attribution": "Pexels",
        "body": """Three years ago, the EB-2 National Interest Waiver was the closest thing to a cheat code in the American immigration system. File a self-petition, skip the employer-sponsored PERM labor certification, argue that your work benefits the United States, and walk away with an approval rate north of 96 per cent. For Indian professionals trapped in a green card backlog measured in decades, the NIW was liberation theology.

That era is over.

USCIS Form I-140 adjudication data through the fourth quarter of fiscal year 2025, analysed in a detailed June 11 review by immigration law practitioners, confirms a collapse that has been building for three years. The NIW approval rate fell to 55.2 per cent for the full fiscal year — and to 35.7 per cent in the fourth quarter alone. That is not a rounding error or a blip. It is a structural shift in how USCIS evaluates these petitions.

## The numbers

| Fiscal Year | NIW Approval Rate |
|---|---|
| FY2022 | ~96% |
| FY2023 | ~80% |
| FY2024 | ~71% |
| FY2025 (full year) | 55.2% |
| FY2025 Q4 | 35.7% |

The EB-1A Extraordinary Ability category, which requires a higher evidentiary bar but offers faster visa availability for Indian nationals, held up better — 66.9 per cent for FY2025, down from a historical range of 70 to 75 per cent. The O-1 nonimmigrant extraordinary ability visa remains above 90 per cent.

## What changed

The short answer: USCIS started reading the petitions more carefully.

The legal framework for NIW cases has not changed. It still rests on *Matter of Dhanasar*, the 2016 precedent decision that established a three-prong test: the petitioner's proposed endeavour has substantial merit and national importance, the petitioner is well positioned to advance the endeavour, and it would be beneficial to the United States to waive the job offer requirement.

What has changed is how rigorously adjudicators apply that framework. During the pandemic years, filing volumes were lower, case backlogs were being cleared, and the approval rate reflected a combination of strong cases and light scrutiny. As NIW surged in popularity — particularly among Indian tech professionals seeking to bypass the EB-2 backlog — USCIS began applying the *Dhanasar* framework with considerably more rigour.

Adjudicators are now placing weight on measurable, demonstrated US impact rather than forward-looking potential or broad sector-wide claims. Saying "my work in machine learning benefits the United States" is no longer enough. You need to show that your specific contributions have been adopted, cited, deployed at scale, or recognised by entities beyond your employer.

Healthcare, core STEM, and national-security-adjacent fields continue to fare well. But the days of filing a generic NIW with a handful of recommendation letters and expecting an approval are finished.

## The Mukherji case

There is one bright spot for petitioners, though it comes from the courts rather than from USCIS itself.

In *Mukherji v. Miller*, decided on January 28, 2026, a federal district court in Nebraska questioned whether USCIS had properly adopted its two-step "final merits" analysis for EB-1A cases. The agency conceded the petitioner met five of the ten extraordinary ability criteria. The court ordered the petition approved.

The decision is limited to that one case, and USCIS has not changed its guidance. But it represents a notable development: a federal judge pushing back on the agency's practice of acknowledging that a petitioner meets multiple criteria and then denying the case anyway on a subjective "final merits" assessment. For anyone who has received a denial that reads like the adjudicator conceded the evidence and then denied the case on vibes, *Mukherji* may provide an additional argument on appeal or in federal court.

## What Indian professionals should do

The practical implications are significant. For the thousands of Indians who viewed the NIW as a reliable alternative to the EB-2 employer-sponsored route, the calculus has changed. Here is what the data suggests:

**Dual filing is now essential, not optional.** Individuals who may qualify for both EB-1A and NIW should consider filing both petitions concurrently. This creates multiple shots at approval and preserves flexibility. If both are approved, you can pursue permanent residence through whichever category offers more favourable visa availability. Given that EB-1 India's final action date (December 15, 2022) is years ahead of EB-2 India (currently unavailable), dual filing has a strategic visa-availability advantage on top of the redundancy benefit.

**Evidence quality now determines outcomes.** Independent corroboration, verifiable metrics, and a clearly articulated US benefit distinguish approved petitions from denied ones. Generic recommendation letters, self-serving claims of impact, and broad descriptions of your field are not sufficient. You need third-party evidence: citations, adoption by other organisations, media coverage, government or industry uptake, measurable outcomes.

**PERM is not dead.** For professionals whose work does not produce the kind of independently verifiable impact that NIW and EB-1A demand, the employer-sponsored PERM-based EB-2 or EB-3 route remains available. It is slower, requires employer cooperation, and feeds into the backlog. But with NIW at 35.7 per cent in the most recent quarter, "slower but reliable" has a different ring to it than it did when NIW was a 96 per cent lock.

**Timing matters more than it used to.** The approval rate has declined every year for four consecutive years. There is no public indication that it will reverse. If you are building a case, the evidence you assemble now will face tougher scrutiny than it would have a year ago. Front-load the preparation: get your citations counted, your independent letters secured, your impact documented, and your endeavour framed narrowly before you file.

The NIW was never supposed to be easy. It was supposed to be reserved for people whose work genuinely benefits the United States in ways that justify waiving the normal requirements. For a few years, USCIS forgot that. Now they have remembered."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
