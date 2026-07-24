#!/usr/bin/env python3
"""Immigration writer — 2 July 2026, 9pm PT run."""
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
# ARTICLE 1: USCIS 11.6 Million Case Backlog
# ──────────────────────────────────────────────

article1_body = """The number sits in a USCIS data dashboard like a monument to institutional paralysis: 11.6 million pending cases. It is the largest backlog in the agency's history, a 23 per cent jump over the end of fiscal year 2024, and it is getting worse.

For the roughly 1.5 million Indian-born immigrants tangled somewhere in America's employment-based visa queue, the figure is not abstract. It is the reason an H-4 EAD renewal that once took two months now takes seven. It is why a naturalization application that should clear in half a year sits untouched for fourteen months. It is the gap between a legal right and its practical reality.

## The numbers behind the freeze

USCIS completed just 2.5 million cases in the fourth quarter of FY2025 — a 22 per cent decrease compared to the same quarter the year before. Median processing time for a replacement green card (Form I-90) more than doubled, from 4.1 months at the end of FY2025 to 9.2 months by February 2026. Employment-based adjustment of status applications (I-485) now take between 9 and 35 months. Travel documents (I-131) average 16 to 22 months. Employment authorisation documents (I-765) range from 3 to 12 months, though some service centres report waits exceeding 19 months.

Premium processing fees rose on 1 March 2026, with the I-129 and I-140 fast-track now costing $2,965 — and even that guarantees only a 15-business-day review, not an approval.

## The FBI bottleneck

In late spring 2026, USCIS mandated enhanced FBI background checks for all pending green card and citizenship applications. The directive, reported by immigration attorneys nationwide, effectively paused final adjudications across the board. USCIS spokesman Zach Kahler called the delay "brief," but provided no timeline for resolution.

The freeze hit hardest in the I-485 pipeline — precisely where hundreds of thousands of Indian EB-2 and EB-3 applicants already face multi-decade waits. For someone who filed their I-485 in 2014 with a priority date from 2012, the enhanced check adds another layer of indefinite waiting atop a system already moving at geological speed.

## Lawmakers push back

In June 2026, a bipartisan group of House members led by Representative Seth Moulton sent a formal letter to USCIS demanding answers: how many cases are pending by form type, which policy changes since January 2025 have contributed to the slowdown, and what the agency plans to do about it.

The letter cited constituent complaints about applications languishing without even a receipt notice — meaning applicants could not prove to employers that they had a pending case, could not renew their driver's licences, and in some cases could not legally work despite having filed timely renewals.

USCIS has not publicly tied any single policy change to the backlog's growth. But immigration attorneys point to a confluence of factors: the switch to Final Action Dates (instead of Dates for Filing) for employment-based I-485 eligibility, the enhanced vetting requirements for H-1B and H-4 visa stamping at consulates, the new $100,000 H-1B fee generating thousands of RFEs, and a hiring freeze at the agency itself.

## What this means for Indian Americans

The backlog is not an equal-opportunity inconvenience. Per-country caps ensure that Indian nationals absorb a disproportionate share of the pain. The July 2026 Visa Bulletin made EB-2 India "unavailable" — no green cards in that category will be issued until at least October, when the new fiscal year begins. EB-1 India retrogressed to October 2022. EB-3 India crept forward to January 2014 — meaning applicants who filed a dozen years ago are only now approaching the front of the line.

For an Indian software engineer on an H-1B with an approved I-140 and a 2015 priority date, the math is punishing: the visa bulletin queue alone could stretch another decade, and now the agency processing the paperwork cannot keep up with its own caseload.

The 180-day automatic EAD extension — a lifeline for H-4 spouses whose work permits expire while renewals are pending — papers over the problem without solving it. An EAD that takes twelve months to renew means twelve months of anxiety, twelve months of employers questioning whether the authorisation is still valid, twelve months of a qualified professional's career held hostage by a receipt number.

## No quick fix

USCIS is a fee-funded agency. It does not receive regular congressional appropriations. When application volumes drop — as they have for certain categories under the current administration's restrictive posture — revenue drops, which means fewer adjudicators, which means longer waits, which means more complaints, which means more congressional inquiries that consume staff time. The feedback loop is structural.

The agency's own stabilisation act allows it to adjust premium processing fees for inflation every two years. But premium processing is a pressure valve, not a fix. It helps employers willing to pay $2,965 for a faster answer. It does nothing for the H-4 spouse filing an EAD renewal or the EB-2 applicant waiting for a visa number that may never come.

Until Congress either funds USCIS directly, eliminates per-country caps, or both, 11.6 million is not a peak. It is a plateau."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Eleven Million Cases and Counting. USCIS Cannot Process Its Own Workload",
    "subheadline": "The agency's backlog has hit a historic high, processing times have doubled, and enhanced FBI checks are freezing green card approvals. Indian applicants, already trapped in decade-long queues, are bearing the worst of it.",
    "slug": make_slug("uscis-backlog-11-million-cases-processing-freeze-india"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals face the worst of the USCIS backlog because per-country caps trap them in decade-long queues, while ballooning processing times for EADs, I-485s, and naturalization applications disrupt careers and family stability.",
    "tags": ["uscis", "backlog", "processing-times", "green-card", "h1b", "ead", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Clinch Law News", "url": "https://news.clinchlaw.com/uscis-mandates-enhanced-fbi-background-checks"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/uscis-backlog-2026-lawmakers-demand-answers-on-processing-delays/"},
        {"name": "Alonso & Alonso Law", "url": "https://alonsoandalonsolaw.com/uscis-processing-times-2026/"},
        {"name": "Manifest Law", "url": "https://manifestlaw.com/uscis-processing-times/"},
        {"name": "Atlas Legal", "url": "https://theatlaslegal.com/uscis-processing-times/"}
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

# ──────────────────────────────────────────────
# ARTICLE 2: Day 1 CPT Crackdown
# ──────────────────────────────────────────────

article2_body = """For years, it was the immigration system's open secret. An Indian engineer loses the H-1B lottery for the third time, enrols in a second master's programme at a university that authorises full-time Curricular Practical Training from day one, and keeps working at the same employer under a fresh student visa. Tens of thousands of professionals — overwhelmingly Indian — used the pathway. Now USCIS is pulling the rug, and it is reaching backward.

Immigration attorneys report a sharp rise in I-485 denials where USCIS has flagged applicants' old Day 1 CPT enrolment as evidence of unauthorised employment. The agency is pulling full SEVIS academic histories before adjudicating green card applications, and treating a transition from post-completion OPT into a Day 1 CPT programme at the same employer as a failure to maintain F-1 status. Under INA Section 245(c)(2), any period of unauthorised work bars an applicant from adjusting status inside the United States — even if their H-1B change of status was later approved without issue.

## The retroactive trap

The denials are reaching back years. An applicant who used Day 1 CPT in 2019, transitioned cleanly to H-1B in 2020, had an I-140 approved in 2022, and filed an I-485 when their priority date became current is now receiving a denial in 2026 based on the 2019 enrolment. The H-1B approval, which implicitly validated the applicant's status at the time, carries no weight in the I-485 adjudication.

"USCIS is essentially saying that your previous approvals don't matter," one immigration attorney told VisaVerge. "They are going back to the raw SEVIS data and making their own determination about whether your second degree was bona fide."

The agency has not issued a formal policy memo on Day 1 CPT. There is no new regulation. The shift is happening through adjudicator-level decisions — Notices of Intent to Deny and outright denials that cite the same statutory provision but leave applicants with little procedural clarity about how to respond.

## The Duration of Status axe

Simultaneously, the Department of Homeland Security is preparing to close the broader pathway that made Day 1 CPT possible. On 5 May 2026, DHS proposed eliminating the "Duration of Status" framework for F-1 student visas — the decades-old system under which international students could remain in the US as long as they maintained valid student status.

The proposed rule would replace Duration of Status with a fixed admission period of up to four years. Any extension beyond that — for continued studies, OPT, or STEM OPT — would require a formal application to USCIS, shifting the burden from universities (which currently manage student status through SEVIS) to the federal agency already drowning in an 11.6 million case backlog.

The proposal also cuts the post-programme grace period from 60 days to 30, halving the window a graduate has to find an employer willing to sponsor an H-1B petition or secure another legal pathway.

## Why Indians are disproportionately exposed

Indian nationals accounted for roughly 30 per cent of all international students in the United States before the current decline. They dominated the STEM OPT extension programme, which allows an additional two years of work authorisation in science, technology, engineering, and maths fields. And they were, by far, the largest group using Day 1 CPT as a bridge between failed H-1B lottery attempts and eventual employer-sponsored green cards.

The H-1B lottery itself has become hostile ground. The weighted selection system introduced for FY2027 favours higher-paid positions, which sounds meritocratic until you consider that Indian IT services firms — TCS, Infosys, Wipro — have seen new H-1B approvals plummet 40 per cent in a single year, with entry-level IT roles effectively priced out. The $100,000 supplemental fee, though temporarily blocked by a federal judge, looms as a further barrier.

Danielle Goldman, co-founder and CEO of immigration advisory firm Build, put it bluntly: "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working.'"

She warned that thousands of Indian professionals in AI, machine learning, and data science face uncertainty if Day 1 CPT disappears and no alternative pathway fills the gap.

## The strategic calculation

The crackdown creates an impossible arithmetic for Indian graduates. The F-1 visa rejection rate for Indian students hit 61 per cent in 2025 — a ten-year high. Those who do get in face a shrinking set of post-graduation options. OPT provides one year of work authorisation (three for STEM fields), but after that, the only legal route to continued employment is an H-1B — a lottery with roughly 25 per cent odds that gets worse every year for Level 1 and Level 2 wage positions.

Day 1 CPT was the unofficial safety net. It kept skilled workers in the US labour force, kept their employers staffed, and kept the immigration system from having to confront its own structural failures. Without it, the question is not academic: what happens to a 28-year-old Indian software engineer with a US master's degree, two years of STEM OPT experience at a Fortune 500 company, and no H-1B selection after three tries?

The answer, increasingly, is that they leave. Or they never come in the first place.

Companies are already adapting. Goldman noted that employers may shift to cap-exempt H-1B programmes at universities and research institutions, or to O-1 visas for workers who can demonstrate "extraordinary ability." But those are narrow channels, and they do not replace the volume that CPT absorbed.

"The companies will either struggle because they won't have the talent," Goldman said, "or they will have to get creative and find alternate solutions."

For the Indian diaspora, the Day 1 CPT crackdown is not an isolated enforcement action. It is another brick in a wall that is being built, methodically, around every pathway that once made the American immigration system navigable for skilled workers from a single, oversubscribed country."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "USCIS Is Denying Green Cards Over Old Day 1 CPT Enrolments. The Safety Net Is Gone",
    "subheadline": "The agency is pulling decade-old student records to reject adjustment-of-status applications, while DHS prepares to kill the Duration of Status framework entirely. Indian graduates are running out of legal pathways.",
    "slug": make_slug("day-1-cpt-green-card-denial-duration-of-status-india"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals are the largest group affected by the Day 1 CPT crackdown because they dominate STEM OPT and H-1B lottery participation; the retroactive green card denials and proposed Duration of Status elimination threaten tens of thousands of Indian professionals and graduates.",
    "tags": ["day-1-cpt", "f1-visa", "green-card", "uscis", "h1b", "opt", "duration-of-status", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/day-1-cpt-nightmare-uscis-denies-green-cards-in-2026/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/proposed-us-student-visa-changes-could-hit-indian-graduates"},
        {"name": "Niskanen Center", "url": "https://www.niskanencenter.org/reforming-the-international-student-work-authorization-programs/"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/04/visa-rejections-climb-in-the-us-for-international-students-from-key-markets-including-india/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7972735/pexels-photo-7972735.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "University graduates holding diplomas during a commencement ceremony",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}

# ──────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
