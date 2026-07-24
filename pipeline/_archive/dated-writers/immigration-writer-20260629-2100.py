#!/usr/bin/env python3
"""
Immigration writer – 2026-06-29 21:00 PT
Two articles:
  1. FY2027 H-1B filing deadline (June 30)
  2. USCIS consular processing shift – AOS now 'extraordinary relief'
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──────────────────────────────────────────────────────────
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

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ═══════════════════════════════════════════════════════════════════════
# Article 1: FY2027 H-1B Filing Deadline
# ═══════════════════════════════════════════════════════════════════════

article1_body = """Tomorrow is June 30. For thousands of Indian tech workers, it is the last day their employers can file an H-1B petition for fiscal year 2027 — the first cohort selected under Washington's new wage-weighted lottery. Miss it, and the next shot is a full year away.

The filing window opened on April 1, after USCIS ran its revamped selection process in March. For the first time, the agency weighted registrations by the Department of Labour's prevailing wage levels: a Wage Level IV registration received four entries in the lottery pool; a Wage Level I registration received one. The change was designed to favour higher-paid, more experienced workers. Early data suggests it worked — entry-level positions saw their selection odds roughly halve compared with the old random draw.

## The new paperwork gauntlet

Employers who got selection notices are contending with a substantially revised Form I-129, the petition for a nonimmigrant worker, dated February 27, 2026. The new edition demands more granular detail about the offered position, including the Standard Occupational Classification code and supporting evidence for the wage level claimed during registration. Any mismatch between what was declared in March and what appears in the June petition is an invitation for a Request for Evidence — or an outright denial.

USCIS has made clear that only the 02/27/26 edition of the form will be accepted. Petitions submitted on older versions are rejected on arrival.

## The $100,000 question

Then there is the fee. In September 2025, the Trump administration imposed a $100,000 surcharge on new H-1B petitions processed through consulates. A federal judge in Boston struck down the fee in June 2026, calling it an unlawful tax that Congress never authorised. But the government has continued collecting it while it evaluates whether to appeal. Immigration attorneys report that petitions filed without the payment are being held or returned, even after the ruling.

For Indian IT services firms — Infosys, TCS, Wipro, HCL — the fee's impact is muted by years of strategic retreat from H-1B dependency. Between 2017 and 2025, the number of Indian employees on H-1B visas at these four companies fell from 34,507 to 17,997, a decline of nearly half. Crisil estimates the fee would shave just 10–20 basis points off operating margins, with 30–70 per cent of the cost passed through to clients in renegotiated contracts.

But for smaller employers — hospitals sponsoring a single foreign-trained physician, startups that cannot absorb six-figure visa costs — the arithmetic is different. Several immigration attorneys have reported clients abandoning petitions rather than paying a fee that a court has already declared illegal.

## What happens after tomorrow

Employers who file by the deadline will wait for USCIS adjudication over the summer. Approved beneficiaries can begin working in H-1B status on October 1. Those who miss the window have no recourse until the FY2028 registration period opens, likely in March 2027.

If USCIS does not receive enough petitions to fill the 85,000-visa cap from the initial lottery, it may conduct subsequent selections. But given the volume of registrations in recent years — more than 340,000 eligible registrations for FY2026 — a second lottery is unlikely.

## Why this matters to Indian Americans

Indians account for roughly 72 per cent of all H-1B visas issued. The wage-weighted system reshapes who among them gets through. Senior engineers and architects at Level III and IV wages now have meaningfully better odds than a fresh graduate on an entry-level offer. For the thousands of Indian students who completed master's degrees at American universities this spring, the narrowing path is not abstract — it is the difference between staying and leaving.

The filing deadline is mechanical, a date on a calendar. But behind every petition submitted tomorrow is a person whose ability to remain in the country, build a career, and eventually pursue a green card depends on a single envelope reaching a USCIS service centre before the clock runs out.

*Sources: USCIS FY2027 Cap Announcements; Crisil Intelligence; Capitol Immigration Law Group; Lexology; SHRM*"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Tomorrow Is the Last Day to File an H-1B Petition for FY2027. The Rules Have Never Been Harder",
    "subheadline": "The first cohort selected under the wage-weighted lottery faces a revised form, a contested $100,000 fee, and a June 30 deadline that leaves no margin for error.",
    "slug": make_slug("fy2027-h1b-filing-deadline-june-30-wage-weighted"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 72% of H-1B visas. The new wage-weighted system favours senior roles over entry-level positions, reshaping who gets to stay — and every unfiled petition by tomorrow is a lost year.",
    "tags": ["h1b", "uscis", "fy2027", "wage-weighted-lottery", "immigration", "filing-deadline"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/alerts/fy-2027-h-1b-initial-registration-selection-process-completed"},
        {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/uscis-completes-fy-2027-h-1b-cap-lottery/"},
        {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/uscis-completes-h-1b-lottery"},
        {"name": "Crisil Intelligence via LiveMint", "url": "https://www.livemint.com/companies/news/after-trump-s-shock-move-companies-may-pass-30-70-of-h-1b-visa-fee-hike-to-clients-says-crisil-11727265340456.html"},
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/USCIS_HQ_Groundbreaking_Ceremony_%2838096356021%29.jpg/1280px-USCIS_HQ_Groundbreaking_Ceremony_%2838096356021%29.jpg",
    "image_caption": "USCIS headquarters groundbreaking ceremony in Camp Springs, Maryland",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ═══════════════════════════════════════════════════════════════════════
# Article 2: USCIS Consular Processing Shift — AOS is 'Extraordinary Relief'
# ═══════════════════════════════════════════════════════════════════════

article2_body = """For decades, the path from H-1B visa to green card ran through a single mechanism: adjustment of status. You stayed in the country, filed the paperwork, and waited — sometimes for years, sometimes for decades — while your life continued around you. Your children attended American schools. Your spouse, if fortunate, held an H-4 EAD and worked. You bought a house, paid taxes, coached Little League.

USCIS has now told you to go home.

## The policy shift

On May 22, 2026, USCIS issued policy memorandum PM-602-0199, reframing adjustment of status under Section 245 of the Immigration and Nationality Act as "an extraordinary form of relief" rather than a routine administrative procedure. The directive instructs adjudicating officers to treat in-country green card processing as the exception, not the rule. The default, going forward, is consular processing: leave the United States, travel to a U.S. embassy or consulate in your home country, and complete the immigrant visa application from there.

"We're returning to the original intent of the law," USCIS spokesperson Zach Kahler said. "An alien who is in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances."

The word "extraordinary" is doing enormous work in that sentence.

## The consulate bottleneck

For Indian nationals, "returning home to apply" collides with a logistical reality that the policy appears to ignore. U.S. consulates across India are running the longest visa interview wait times in the world. Hyderabad and Mumbai now report 9.5-month queues. New Delhi has climbed to 7.5 months. Even Chennai, the fastest major Indian post, sits at 5.5 months.

These delays predate the consular processing shift. They stem from expanded screening protocols — including the social media and digital footprint checks implemented in December 2025 — and from the sheer volume of Indian applicants at every visa category. Layering hundreds of thousands of green card applications onto an already overwhelmed consular infrastructure will not make the queues shorter.

## The family calculus

The practical consequences for Indian families are stark. Consider a senior software engineer in Seattle, fifteen years into an H-1B, with an approved I-140 and a priority date that just became current. Under the old system, she would file for adjustment of status, receive an EAD, and continue working while USCIS processed the application. Her spouse would retain H-4 EAD work authorisation. Their children would remain in school.

Under the new policy, she is expected to leave the country, book a consular interview in India — where the wait may stretch to nine months — and complete the process abroad. During that time, she cannot work in the United States. Her employer cannot hold her role indefinitely. Her spouse loses work authorisation. Her children face the prospect of an abrupt mid-year school transfer to India, or staying behind while one parent processes overseas.

USCIS has acknowledged that "economic benefit or otherwise in the national interest" may warrant exceptions, but the policy language does not define either standard. Immigration attorneys report that the exception criteria remain opaque and inconsistently applied across service centres.

## Timing is everything — and terrible

The consular processing mandate lands alongside the July 2026 Visa Bulletin, which delivered its own blow to Indian applicants. EB-2 India is marked "unavailable" — effectively shut until October, when the new fiscal year resets allocations. EB-1 India retrogressed by 3.5 months. Only EB-3 India moved forward, and only by a month.

For the estimated 700,000 Indian nationals in the employment-based green card backlog, the combination is a vice: even if you accept consular processing, there may be no visa number available when you arrive at the embassy.

## The legal challenge

Immigration attorneys are already exploring challenges. The memo's reclassification of adjustment of status as "extraordinary" relief contradicts decades of administrative practice and multiple Board of Immigration Appeals precedents that treated AOS as a standard pathway. Several law firms have signalled they will file suit if USCIS begins issuing blanket denials of adjustment applications.

"The statute says 'may' adjust status, not 'shall not,'" said one immigration attorney who requested anonymity because their firm has pending cases. "Rewriting that by policy memo, without notice-and-comment rulemaking, is the kind of thing courts have repeatedly struck down."

## Why this matters to Indian Americans

No community is more exposed to this shift than Indian H-1B holders. They face the longest green card backlogs in the world, the most congested consulates, and the greatest disruption from a policy that treats decades of lawful presence as irrelevant to the question of whether someone deserves to stay.

The adjustment of status process was never fast. For Indians, it was never even close to fast. But it allowed people to remain in the country they had built lives in while the bureaucracy ground forward. That continuity — imperfect, frustrating, maddeningly slow — is what USCIS has now classified as extraordinary.

*Sources: USCIS Policy Memorandum PM-602-0199; Greenspoon Marder; VisaVerge; The Indian Eye; AInvest; State Department Visa Bulletin*"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "USCIS Told Green Card Applicants to Go Home. The Consulate Queue Is Nine Months Long",
    "subheadline": "A policy memo reclassifies in-country green card processing as 'extraordinary relief.' For 700,000 Indians in the backlog, the alternative is a consulate system already buckling under record wait times.",
    "slug": make_slug("uscis-consular-processing-adjustment-status-extraordinary-india"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders face the world's longest green card backlog and the most congested consulates. Reclassifying in-country processing as 'extraordinary' forces them into a system already running 9.5-month queues.",
    "tags": ["green-card", "uscis", "adjustment-of-status", "consular-processing", "immigration", "india-backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS Policy Memo PM-602-0199", "url": "https://www.uscis.gov/policy-manual"},
        {"name": "Greenspoon Marder", "url": "https://www.gmlaw.com/resources/uscis-shifts-green-cards-to-consular-processing/"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/uscis-limits-adjustment-of-status-new-2026-policy-impact/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/29/us-asks-foreign-nationals-to-apply-for-green-cards-from-home-country/"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/longer-us-tourist-visa-queues-hyderabad-mumbai-and-new-delhi-face-delays/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/US_Embassy_New_Delhi.jpg/1280px-US_Embassy_New_Delhi.jpg",
    "image_caption": "The United States Embassy in New Delhi, India",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ── Insert ────────────────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
