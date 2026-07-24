#!/usr/bin/env python3
"""Immigration writer for The Videshi — 2026-06-29 09:00 run.

Two articles:
1. Day 1 CPT green card denials: USCIS retroactively denying I-485s for old Day 1 CPT use
2. July 2026 Visa Bulletin deep analysis: EB-2 India shut down, EB-1 retrogressed
"""

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


# ── Article 1: Day 1 CPT Green Card Denials ──────────────────────────────

article1_body = """If you used a Day 1 CPT programme to keep working in America after your OPT expired, USCIS may already be looking at your file. And it may not like what it finds.

Immigration attorneys across the country report a sharp rise in Requests for Evidence and outright denials on I-485 adjustment-of-status applications — not for anything applicants did last month, but for decisions they made in 2018 or 2019. The common thread: a transition from post-completion Optional Practical Training into a Day 1 Curricular Practical Training graduate programme, often at the same employer, often without so much as a weekend break between the two.

## The Pattern USCIS Is Flagging

The typical case looks like this. An Indian student finishes a master's degree at a reputable university, takes 12 months of OPT, then enrols in another graduate programme that offers Day 1 CPT — allowing continued full-time employment while nominally pursuing a second degree. Years later, the worker's employer sponsors an EB-2 or EB-3 green card. The I-140 is approved. The I-485 is filed. Then the denial arrives.

USCIS is now pulling complete SEVIS enrolment histories before adjudicating I-485 applications. The agency's position: switching directly from post-completion OPT into a Day 1 CPT programme, without a genuine academic break, constitutes a failure to maintain F-1 status. The reasoning is that the second degree was pursued not for education but for work authorisation — violating the "primary purpose" requirement of the student visa.

According to VisaVerge, RFE rates on I-485 filings with this specific fact pattern now exceed 40 percent, compared with roughly 12 percent for adjustment cases broadly. That is not a rounding error. It is a targeted enforcement operation.

## The Legal Trap: INA Section 245(c)(2)

The consequences extend well beyond a denied green card application. Under Section 245(c)(2) of the Immigration and Nationality Act, anyone who engaged in unauthorised employment or failed to continuously maintain lawful status is barred from adjusting status inside the United States. USCIS is applying this provision retroactively to Day 1 CPT cases, arguing that the period between OPT and CPT — when the agency now says the applicant was out of status — constitutes unauthorised employment.

For denied applicants, the options narrow dramatically. Many are told their only path forward is consular processing abroad. But departing the United States after accruing unlawful presence can trigger a three-year or ten-year re-entry bar, depending on the duration. It is a legal Catch-22 that turns a seven-year-old academic decision into a potential exile.

Not every Day 1 CPT case triggers a denial. Students who enrolled in a CPT programme from the outset, without a prior OPT period, are faring better. So are those who took a genuine academic break — a full semester off — between OPT and the new enrolment. The denials cluster around one specific fact pattern: OPT expiring on a Friday and CPT starting the following Monday at the same employer, with the same job duties.

## The Broader Cross-Check

Day 1 CPT scrutiny is part of a wider shift in how USCIS, the State Department, and the Department of Labor now share data. Adjudicators cross-reference SEVIS records with state tax withholding, W-2 addresses, I-9 E-Verify data, and — since December 2025 — public social media accounts that H-1B and H-4 applicants are required to make visible during adjudication.

An Instagram post advertising a photography side business. A LinkedIn profile listing freelance consulting. A DoorDash delivery gig during an F-1 programme. Any of these can now surface during a green card interview as evidence of unauthorised employment — even if the post is years old.

The operational shift started in late 2024, accelerated through 2025, and is now standard practice at most USCIS service centres and consular posts. Workers who relied on the assumption that old paperwork gaps would never surface are the ones most exposed in 2026.

## What You Should Do Now

Immigration attorneys recommend five specific steps for anyone in this fact pattern:

1. **Pull your SEVIS record** before filing I-485. Any OPT-to-Day-1-CPT transition after 2018 needs a legal review and a memo of law addressing the 245(c)(2) risk.

2. **Audit your work history** against every I-20 and CPT authorisation letter. Gaps between authorised employment periods are exactly what USCIS is searching for.

3. **Review your social media footprint** for the last five years. Remove business profiles, booking links, and freelance listings that contradict your petition employment. Consular officers are checking.

4. **Document everything.** Keep pay stubs, client assignment letters, I-9 records, and class schedules for the full residency period.

5. **Do not wait for the RFE.** Respond proactively with your SEVIS record, LCA history, and a clear timeline. Surprises at the interview stage are the hardest to recover from.

## Why This Matters to Indian Americans

Indians make up the single largest cohort of Day 1 CPT users. Many are mid-career software engineers, data scientists, and AI researchers who used CPT as a bridge during years of H-1B lottery rejections — a rational response to a system that offers 85,000 annual slots for hundreds of thousands of applicants. That these same professionals now face green card denials for a programme their universities administered and USCIS implicitly tolerated for years is not lost on the community.

The message from Washington is clear: the government now has the tools to look backward, and it is using them."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "You Used Day 1 CPT in 2019. USCIS Just Found Out",
    "subheadline": "Immigration attorneys report a 40 percent RFE rate on green card applications from workers who transitioned from OPT to Day 1 CPT years ago. The agency is pulling SEVIS records, cross-checking tax filings, and scanning Instagram.",
    "slug": make_slug("day-1-cpt-green-card-denials-uscis-sevis-cross-check"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians are the largest cohort of Day 1 CPT users, and mid-career tech professionals who used CPT as a bridge during H-1B lottery rejections now face retroactive green card denials for decisions made years ago.",
    "tags": ["day-1-cpt", "uscis", "green-card", "i-485", "f-1", "opt", "immigration-enforcement"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/day-1-cpt-h-1b-location-instagram-unauthorized-work-2026/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/alerts"},
        {"name": "Ahluwalia Law", "url": "https://ahluwalialaw.com/f1-opt-changes-2026/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ── Article 2: July 2026 Visa Bulletin Deep Analysis ─────────────────────

article2_body = """The July 2026 Visa Bulletin is out, and for the roughly 700,000 Indians waiting in the employment-based green card queue, the numbers read like a door slamming shut.

EB-2 India: Unavailable. Not retrogressed. Not moved backward. Simply gone — marked with the letter "U," meaning no immigrant visa numbers will be issued in this category for the remainder of the fiscal year. EB-5 Unreserved India joins it in the same column. EB-1 India retreated two months to October 15, 2022. And EB-3 India, the workhorse category for most Indian tech professionals, advanced by exactly half a month — to January 1, 2014. If your priority date is after that, you are still waiting for a visa number that reflects a filing date from more than twelve years ago.

## What 'Unavailable' Actually Means

When the Department of State marks a category "U," it is different from ordinary retrogression. In a retrogressed category, a final action date still exists — applicants with priority dates earlier than that cutoff can still receive approvals. "Unavailable" means there is no cutoff at all. The pro-rated annual limit for India in EB-2 has been exhausted for fiscal year 2026. No green cards will be approved in this category until the new fiscal year begins on October 1, 2026.

The State Department confirmed this explicitly in a May 22 announcement, and the July bulletin makes it official. Even applicants with priority dates from 2012 or 2013 — people who have been waiting more than a decade — cannot receive final green card approval until the numbers reset in the autumn.

For the practical purposes of an Indian professional on an H-1B visa, this means: if you were in the EB-2 pipeline and your I-485 was pending, it will sit untouched through the summer. If you were about to file, you cannot.

## The Full July Picture for India

| Category | Final Action Date | Change from June |
|----------|------------------|------------------|
| EB-1 | October 15, 2022 | Retrogressed 2 months |
| EB-2 | Unavailable | Was September 1, 2013 |
| EB-3 | January 1, 2014 | Advanced 0.5 months |
| EB-5 Unreserved | Unavailable | Was current in early FY |
| EB-5 Set-Asides (Rural, High Unemployment, Infrastructure) | Current | No change |

USCIS has also confirmed it will continue using the Final Action Dates chart — not the more generous Dates for Filing chart — for employment-based adjustment of status applications in July. This decision, which began in May 2026 and has now persisted for three consecutive months, further restricts who can file. Under the Dates for Filing chart, more applicants would be eligible to submit I-485s and obtain interim benefits like work authorisation (EAD) and travel permits (Advance Parole). By requiring Final Action Dates, USCIS has effectively narrowed the filing window.

## EB-1: The 'Priority Worker' Category Feels Anything But

EB-1 India's retrogression to October 15, 2022 is particularly bitter. This category — reserved for individuals with extraordinary ability, outstanding professors and researchers, and multinational managers — has historically been the fastest-moving line for Indian applicants. As recently as early fiscal year 2026, EB-1 India was current, meaning anyone with an approved petition could file.

The two-month pullback from December 15, 2022 to October 15, 2022 signals that demand in this category has caught up with supply. The Capitol Immigration Law Group notes the contrast with China, where EB-1 advanced to June 1, 2023 and EB-3 saw solid forward movement. India and China are both subject to the seven-percent per-country cap, but India's larger applicant pool means the cap bites harder.

## The Artificial-Movement Theory

Former Department of State official Charlie Oppenheim has offered a sharply different reading of the visa bulletin's recent history. In his analysis, shared by WR Immigration, the EB-2 India forward movement earlier in fiscal year 2026 — from April 2013 in October to July 2014 by April — was "completely artificial," driven by the Trump administration's restrictions on visa processing for nationals of 75 countries under travel ban and related policies.

Those restrictions temporarily reduced demand from Rest of World applicants, freeing visa numbers that were then allocated to India. As Oppenheim warned, once the restrictions end, there will be a "boomerang effect" as the deferred applicants from those 75 countries re-enter the queue with early priority dates, pushing India back further.

The EB-2 unavailability in July may be the first tremor of that boomerang.

## What This Means for Your Green Card Timeline

If you hold an EB-2 India petition: your case is frozen until October 1 at the earliest. Use the intervening months to ensure every document in your file is current — employment letters, pay stubs, medical examinations (which expire after two years). If your I-140 is approved, consider whether EB-3 downgrade is viable; EB-3 India at January 1, 2014 is still moving, however glacially.

If you hold an EB-1 India petition with a priority date after October 15, 2022: watch the August and September bulletins closely. Further retrogression, or even unavailability, is possible before the fiscal year ends.

If you are considering EB-5: the unreserved category is unavailable for India, but the set-aside categories — Rural, High Unemployment, and Infrastructure — remain current with no cutoff date. This makes EB-5 set-asides the only employment-based category currently offering Indians a path to filing without a decade-long wait.

## The Structural Problem Remains

None of this is new in kind. What is new is the severity. India accounts for the largest share of employment-based green card demand, but the Immigration and Nationality Act caps each country at seven percent of the annual allocation — roughly 9,800 visas. The result: Indians wait decades while nationals of countries with lower demand face no backlog at all. Bills to eliminate or raise the per-country cap have been introduced in every recent Congress. None has passed.

The July visa bulletin does not create the crisis. It measures it. And for July 2026, the measurement is: EB-2, unavailable. EB-1, retreating. EB-3, twelve years behind. October is ninety-three days away."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "EB-2 India Is Shut Until October. The July Visa Bulletin Is a Wall",
    "subheadline": "The State Department has exhausted EB-2 India visa numbers for fiscal year 2026. EB-1 India retrogressed two months. EB-3 barely moved. For 700,000 Indians in the green card queue, the summer just got longer.",
    "slug": make_slug("july-2026-visa-bulletin-eb2-india-unavailable-eb1-retrogress"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With EB-2 India shut down until October, EB-1 retreating, and EB-3 stuck at a 2014 cutoff, hundreds of thousands of Indian tech professionals on H-1B visas face a frozen summer with no path to green card approval.",
    "tags": ["visa-bulletin", "eb-2", "eb-1", "eb-3", "green-card", "backlog", "india", "uscis"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration/july-2026-visa-bulletin-eb2-india-backlog-hits-limits/"},
        {"name": "Capitol Immigration Law Group", "url": "https://www.cilawgroup.com/news/2026/06/18/july-2026-visa-bulletin-uscis-continues-to-use-final-action-dates-for-eb-filings/"},
        {"name": "Shusterman Law", "url": "https://www.shusterman.com/visa-bulletin-july-2026/"},
        {"name": "WR Immigration / Charlie Oppenheim analysis", "url": "https://www.wolfsdorf.com/india-eb-2-and-eb-3-visa-bulletin-movement/"},
        {"name": "NRI to USA", "url": "https://nritousa.com/green-card-wait-time-india.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "A hand holding an open passport with various visa stamps",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ── Insert ────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
