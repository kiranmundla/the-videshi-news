#!/usr/bin/env python3
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

article1_body = """India's place in the green-card queue has long been measured in decades. The July 2026 Visa Bulletin, released by the State Department on June 16, just added a fresh indignity: the one category that was supposed to be the express lane, EB-1, has gone into reverse for Indian-born applicants.

## The Numbers

EB-1 covers the so-called priority workers — multinational executives, outstanding researchers, and the "extraordinary ability" cases that immigration lawyers spend careers building. For most of the world, the category is **current**, meaning a green card is available the moment the paperwork clears. For India, the cutoff date has now **retrogressed to October 15, 2022**, sliding backward from where it stood a month earlier.

China's EB-1 date, by contrast, nudged *forward* to June 1, 2023. So the bulletin tells two different stories depending on where you were born — a reminder that the per-country caps, not merit, govern the wait.

The damage does not stop at the top preference. EB-2 India, the advanced-degree category that the bulk of Indian H-1B engineers eventually file under, has been marked **"unavailable"** for July. That word is not jargon for "slow." It means no EB-2 India applications can be approved or filed under the final-action chart until the category reopens, presumably when the new fiscal year resets visa numbers in October.

The only crumb of good news sits in EB-3, the skilled-worker rung below EB-2, where India's date advanced to January 1, 2014. That is still an eleven-year wait, but it is movement in a bulletin otherwise defined by walls going up.

## Why This Lands Hard on Indian Americans

For an Indian professional on an H-1B, EB-1 was the emergency exit. When the EB-2 backlog ballooned past a decade, immigration lawyers increasingly steered high-flyers toward EB-1A (extraordinary ability) or EB-1C (multinational managers), precisely because those categories had stayed current or near-current for India while the lower preferences calcified. That escape route just narrowed.

The retrogression also creates a cruel bit of timing for anyone mid-process. A person who filed an EB-1 adjustment expecting an imminent approval now waits behind a date nearly four years in the past. Job changes, promotions, and the simple act of leaving the country become fraught all over again, because an unapproved adjustment ties a worker to their employer and their physical presence in the U.S.

There is a structural reason this keeps happening, and it is worth saying plainly: the United States issues a fixed number of employment green cards each year, and no single country may take more than seven percent without others leaving numbers unused. Indians, who file the largest share of skilled petitions, are mathematically guaranteed to wait the longest. Retrogression is what happens when demand for a category outruns the annual supply faster than expected — often because USCIS approved a wave of cases and the visa numbers ran dry.

## What's Next

The practical read: the fiscal year ends September 30, and visa numbers reset October 1. Categories marked "unavailable" or freshly retrogressed typically spring back to life — sometimes generously — in the October bulletin, as a new annual allotment becomes available. Lawyers expect EB-2 India and EB-1 India to recover at least part of the lost ground then.

Until then, the advice from practitioners is unglamorous: file what you can while dates are favorable elsewhere, keep H-1B status airtight, and do not bank on a category staying current. For a community that has learned to plan its life in priority-date increments, the July bulletin is one more lesson that the only constant is the backlog itself.
"""

article2_body = """For two decades, the ritual was the same: an H-1B holder whose visa stamp had expired could not simply renew it from a desk in San Jose. They had to fly to a U.S. consulate abroad — usually back in India — book a slot months out, sit for an interview, and pray nothing flagged them into administrative processing. A routine renewal could cost weeks of work and the gnawing fear of being stuck outside the country. That ritual is about to get a reprieve.

## What Was Announced

The State Department will relaunch its **domestic visa renewal pilot in December**, and this time the program is being built with India squarely in mind. Julie Stufft, Deputy Assistant Secretary of State for Visa Services, said the department will process roughly **20,000 visa renewals** over an initial three-month window for H-1B holders already inside the United States.

"The vast majority of those will be Indian nationals living in the US, and we will expand as it goes on," Stufft said, framing the move as a direct response to wait times in India that still stretch to six, eight, even twelve months for an appointment. "That is not what we need, and not indicative of how we view India."

The plan traces back to a commitment in the U.S.-India joint statement and was flagged by Prime Minister Modi in his address to the diaspora at the Ronald Reagan Building. A Federal Register notice — the formal trigger that spells out eligibility and steps — is expected shortly.

## How It Will Work

If the pilot mirrors the 2024 version, the mechanics will be straightforward and entirely by mail. Eligible applicants log on to the State Department's domestic-renewal portal, confirm eligibility, complete a DS-160, pay the standard $205 machine-readable visa fee, and ship their passport and supporting documents — Form I-797 approval notice and I-94 record — to the department by courier. No interview, no consulate, no flight.

The catch is the fine print on eligibility. The earlier pilot was limited to applicants whose prior H-1B visa was issued by Mission India within a narrow date band, who qualified for an interview-interview waiver, who had submitted ten fingerprints in a previous application, and who held an approved, unexpired petition. Dependents on H-4 visas were **not** covered last time — a significant limitation for families. Whether December's version widens the aperture on either count will be the detail Indian applicants scrutinize first.

## Why It Matters to the Diaspora

Indians are the single largest group of skilled workers in the United States and account for more than 70 percent of approved H-1B petitions. They are also the population most punished by the current system, because a renewal trip "home" means competing for the same scarce consular slots that have backlogged for a year.

Stateside renewal removes the most stressful variable in an H-1B holder's calendar: the international trip whose timing is hostage to an appointment calendar they do not control. For someone with young kids, an aging parent in India, or a job that frowns on month-long absences, the ability to renew by mail is not a convenience — it is the difference between traveling freely and staying grounded for years.

There is also a quieter benefit. Every renewal handled domestically frees up a consular slot in India for a first-time applicant — a student, a visitor, a new worker — who *must* appear in person. Stufft made that logic explicit: shifting renewals stateside lets missions in India "concentrate on new applicants."

## What's Next

Watch for the Federal Register notice, which will define the eligibility window and confirm whether H-4 dependents are finally included. The pilot is capped at 20,000 and is explicitly a test run; if it clears without security or logistical hiccups, the department has signaled it intends to expand. For a community that has long treated the visa-stamping trip as an unavoidable tax on building a life in America, December cannot come soon enough.
"""

article3_body = """USCIS just handed international students a tool they have wanted for years, and for once it is not buried in a fee hike or a tightening rule. The agency has **expanded premium processing to F-1 OPT and STEM OPT applications** — meaning students can now pay to put their work-authorization request on a 30-day clock instead of waiting out the open-ended limbo that has wrecked job offers and start dates.

## The Change

Premium processing has long existed for H-1B and certain green-card petitions: pay an extra fee, and USCIS commits to acting within a set window. Until now, the Form I-765 that authorizes Optional Practical Training and the STEM OPT extension sat outside that system, subject only to standard processing times that have ballooned in 2026.

Under the new policy, eligible applicants can file **Form I-907** — the premium-processing request — alongside or after their I-765, and USCIS has **30 days to act**. Filing can be done online through a my.uscis.gov account or on paper. Applicants who already filed a paper I-765 can link it to an online account and request premium service after the fact, using the access code on their USCIS notice.

There is an important asterisk. The 30-day clock does not start when USCIS receives the I-907; it starts when the agency decides it has received "all prerequisites for adjudication." If a Request for Evidence or a Notice of Intent to Deny goes out, the clock resets once the student responds. In practice, that means premium processing caps the *normal* wait, but a case with complications can still run long.

## Why Students Have Been Desperate for This

OPT is the bridge. For the typical Indian graduate, it is the 12 months of work authorization (36 with the STEM extension) that turns a degree into a job, builds the résumé, and buys the time to clear an H-1B lottery. Lose that window, and the whole American plan can collapse.

The problem in 2026 has been timing. OPT cannot legally begin until the EAD card is in hand, and a student whose program ends in May with a job starting in July needs the card to arrive in that gap. Standard processing stretched well past it. The trade publication *Inside Higher Ed* reported the case of an F-1 graduate from a top MBA program whose major-tech employer had already pushed his start date once while waiting on OPT approval — and was not sure it would do so again. That story is common enough to be a genre.

A guaranteed 30-day window changes the math. A student can now file, pay for speed, and give an employer a defensible date — instead of shrugging and hoping the card shows up before the offer evaporates.

## The Diaspora Angle

Indians are the largest cohort of international students in the United States, and they lean heavily into exactly the STEM fields the OPT extension was built for. When processing times balloon, Indian students absorb the hit disproportionately, both because of their numbers and because the H-1B sponsorship many of them chase depends on already being employed during OPT.

It is also a rare piece of good news in a year that has otherwise been brutal for student visas — a proposed end to "Duration of Status," a sharp drop in F-1 issuances, and ICE scrutiny of OPT worksites. Premium processing does not undo any of that. But it does hand students one lever they can actually pull: pay for certainty on the single deadline that decides whether a job offer survives.

## What to Watch

USCIS has signaled this is one phase of a broader premium-processing expansion, with change-of-status cases on Form I-539 — students switching into or out of F-1 and J-1 status — slated next. For now, the advice from advisers is to budget for the I-907 fee if a start date is tight, file early, and respond instantly to any RFE, because the clock only protects a clean case. In a system that mostly forces students to wait, the ability to buy back a month is worth knowing about.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's One Green-Card Express Lane Just Went Into Reverse",
        "subheadline": "The July 2026 Visa Bulletin pushes EB-1 India backward to October 2022 and marks EB-2 India 'unavailable' — closing the escape route that lawyers used to skip the decade-long EB-2 wall.",
        "slug": make_slug("eb1-india-retrogression-eb2-unavailable-july-2026-visa-bulletin"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "EB-1 was the emergency exit Indian H-1B workers used to bypass the decade-plus EB-2 backlog; its retrogression to October 2022 narrows the last fast lane for Indian-born green-card applicants.",
        "tags": ["green-card", "visa-bulletin", "eb1", "eb2", "india-backlog", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Murthy Law Firm — July 2026 Visa Bulletin", "url": "https://www.murthy.com/2026/06/16/july-2026-visa-bulletin/"},
            {"name": "U.S. Department of State — Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
            {"name": "USCIS — Adjustment of Status Filing Charts", "url": "https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/adjustment-of-status-filing-charts-from-the-visa-bulletin"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32642490/pexels-photo-32642490.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A U.S. passport and travel documents on a table, representing the employment green-card process",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "No More Flying to Mumbai for a Visa Stamp: Stateside H-1B Renewals Return in December",
        "subheadline": "The State Department will process about 20,000 domestic H-1B visa renewals starting in December, and officials say the vast majority will go to Indian nationals already living in the US.",
        "slug": make_slug("domestic-h1b-visa-renewal-pilot-december-2026-india-stateside-stamping"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold over 70% of approved H-1B petitions and face year-long appointment waits in India; stateside renewal lets them skip the international stamping trip entirely.",
        "tags": ["h1b", "visa-stamping", "domestic-renewal", "state-department", "india", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye — US to launch new plan for work visas in December", "url": "https://theindianeye.com/"},
            {"name": "Fragomen — Domestic Visa Renewal Pilot FAQ", "url": "https://www.fragomen.com/insights/the-state-departments-domestic-visa-renewal-pilot.html"},
            {"name": "U.S. Department of State — Domestic Visa Renewal", "url": "https://travel.state.gov/content/travel/en/us-visas/employment/domestic-renewal.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hand holding an open passport filled with travel and visa stamps",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Will Now Let Students Pay to Speed Up OPT — and That Saves Job Offers",
        "subheadline": "Premium processing has been extended to F-1 OPT and STEM OPT work-authorization filings, putting USCIS on a 30-day clock for the cards that decide whether a graduate's job survives.",
        "slug": make_slug("uscis-premium-processing-opt-stem-opt-f1-students-india-30-day"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest cohort of international students and lean into STEM OPT; a guaranteed 30-day processing window protects the work-authorization timing that decides whether their first US job offer holds.",
        "tags": ["opt", "stem-opt", "f1-visa", "premium-processing", "uscis", "students", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — USCIS Expands Premium Processing to F-1 OPT and STEM OPT", "url": "https://www.fragomen.com/insights/uscis-expands-premium-processing-eligibility-to-certain-f-1-opt-and-stem-opt-applications.html"},
            {"name": "Inside Higher Ed — Intl. Students Still in Limbo", "url": "https://www.insidehighered.com/"},
            {"name": "USCIS — Optional Practical Training (OPT) for F-1 Students", "url": "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/optional-practical-training-opt-for-f-1-students"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972735/pexels-photo-7972735.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "University graduates holding diplomas at a commencement ceremony",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   [{art['slug']}] words={wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
