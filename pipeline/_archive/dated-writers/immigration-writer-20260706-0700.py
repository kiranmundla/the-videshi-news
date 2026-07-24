#!/usr/bin/env python3
"""Immigration writer — 2026-07-06 07:00 PDT run."""
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

# ─────────────────────────────────────────────
# ARTICLE 1: India EB-5 Investor Visa Cap Hit
# ─────────────────────────────────────────────

article1_body = """The United States has shut the door on one more green card pathway for Indians. The Department of State confirmed that all EB-5 unreserved immigrant visas allocated to Indian nationals for fiscal year 2026 have been used up. No more will be issued until October 1, when the new fiscal year begins.

The announcement, effective June 5, means Indian investors who have put up $800,000 to $1,050,000 in qualifying American projects — and waited years for their petitions to be processed — cannot receive final green card approval until the annual allocation resets.

It is not a small group. India is now the second-largest source of EB-5 investors after China, accounting for roughly 22 per cent of all EB-5 petitions filed globally between April 2022 and July 2025.

## Three doors closed at once

The EB-5 freeze arrives alongside two other closures that have left Indian applicants locked out of nearly every employment-based green card category simultaneously. The July 2026 Visa Bulletin shows:

- **EB-2 India**: marked "U" for unavailable — no visas for the rest of the fiscal year
- **EB-1 India**: retrogressed two months, with a cutoff date of October 15, 2022
- **EB-5 India (unreserved)**: marked "U" — exhausted as of June 5

Only EB-3 India saw any forward movement — advancing about two weeks to a cutoff date of January 1, 2014. That means an Indian EB-3 applicant whose case was filed in early 2014 is only now becoming eligible for final processing. The wait is more than twelve years.

## What it means for Indian investors

For applicants inside the United States, pending I-485 adjustment of status applications remain alive but frozen. Background checks and processing may continue, but the green card itself cannot be issued without an available visa number.

"It means all available visa numbers for this specific group have been used," Joseph Barnett of WR Immigration told EB5Investors.com.

The immediate disruption is sharpest for families. Spouses and children on the investor's case are tied to the principal applicant's category. A delay of several months can complicate school enrollment, housing decisions, work authorisation, and dependent visa status.

Children approaching their 21st birthday face the gravest risk. The Child Status Protection Act offers some relief, but its timing rules are technical. A family that expected a near-term green card decision may now need to review whether a child remains protected through the wait.

## The reserved category escape hatch

Not every EB-5 route is blocked. The reserved set-aside categories — rural area projects, high-unemployment area projects, and infrastructure projects — remain current for Indian nationals.

"The EB-5 reserved categories remain current, and there have been no warnings in prior visa bulletins this year that reserved categories will become unavailable," Dennis Tristani of Tristani Law noted.

Oliver Yang from Reid & Wise said this development "underscores the significant volume of Indian investors already in the unreserved visa pipeline" and reinforces the importance of reserved categories, "particularly rural projects, which continue to enjoy separate visa allocations."

That distinction now carries real strategic weight. An investor in a reserved project may still have a path forward, while an investor in the unreserved pool faces a wait for the fiscal year reset.

## The grandfathering deadline

A separate clock is ticking. The EB-5 Reform and Integrity Act of 2022 includes a grandfather clause: petitions filed on or before September 30, 2026 are protected even if the programme's authorisation expires. That deadline has driven a rush of new filings, further pressuring an already oversubscribed system.

## The broader pattern

Indian professionals who have spent years waiting in EB-2 or EB-3 employment-based backlogs have increasingly viewed the EB-5 investor programme as an alternative route — one that does not depend on an employer's sponsorship. The current freeze shows that EB-5 can offer a different path, but not one free from the per-country caps that have bottlenecked every other employment category.

For the Indian diaspora, the arithmetic is blunt: whether you wait in line as a software engineer, a doctor, or an investor with a million dollars, the per-country visa cap treats you the same. The queue moves when the calendar turns to October."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Invest a Million Dollars and Still Wait. India's EB-5 Investor Visa Just Hit a Wall",
    "subheadline": "India exhausted its EB-5 unreserved visa allocation for FY 2026 in June — joining EB-2 and EB-1 in a near-total lockout of employment-based green cards for Indian nationals.",
    "slug": make_slug("eb5-india-investor-visa-cap-exhausted-fy2026"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals who viewed the EB-5 investor visa as an escape from decades-long EB-2 and EB-3 green card backlogs now face the same per-country caps that trapped them in the first place.",
    "tags": ["eb5", "investor-visa", "green-card", "india", "visa-bulletin", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "BAL Immigration News", "url": "https://www.bal.com/immigration-news/united-states-eb-5-unreserved-visa-limit-met-for-india/"},
        {"name": "EB5Investors.com", "url": "https://www.eb5investors.com/blog/india-exhausts-eb-5-unreserved-visa-cap-what-investors-must-do-before-october/"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/indian-eb-5-unreserved-visa-numbers-hit-pause-through-fy-2026-blocking-green-cards/"},
        {"name": "Envoy Global", "url": "https://www.envoyglobal.com/resources/immigration-news/india-eb-5-unreserved-visa-cap-reached-for-fy-2026"},
        {"name": "BAL — July 2026 Visa Bulletin", "url": "https://www.bal.com/immigration-news/united-states-july-2026-visa-bulletin-most-employment-based-categories-advance-with-exceptions-for-indias-final-action-dates/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b0/United_States_Green_Card_%282023_edition%29.jpg",
    "image_caption": "A United States Permanent Resident Card, the document at the centre of the EB-5 investor visa programme",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2: DS-160 / Social Media Vetting — Employer Impact
# ─────────────────────────────────────────────

article2_body = """Corporate America has a new immigration headache, and it has nothing to do with the lottery. The expanding regime of social media vetting, device searches, and post-visa screening is creating operational chaos for employers who rely on foreign-born talent — and Indian workers are bearing the brunt of it.

A Reuters analysis published Monday laid bare what immigration attorneys and HR departments have been grappling with for months: the cumulative effect of DS-160 form changes, consular social media reviews, and border device searches is not just slowing visa processing. It is reshaping how companies hire, how they manage international travel, and how they communicate risk to their own employees.

## Stranded in India

The most visceral example emerged last winter. After the State Department implemented new social media vetting guidelines, U.S. consulates in India abruptly rescheduled visa stamping appointments from November and December to March and beyond. H-1B and H-4 visa holders who had travelled home for the holidays found themselves unable to return to their jobs for months.

"This caused many foreign-national employees who had traveled home for the holidays to be stuck in India for months, unable to return to their jobs in the U.S.," Reuters reported, citing incidents first documented by The Washington Post.

The disruption was not a one-off. Indian consulates are now booking visa interview slots 10 to 12 months in advance, according to recent U.S. Embassy communications. For an H-1B worker who needs to leave the country for a family emergency, the return trip is no longer a matter of weeks. It is a matter of quarters.

## The compliance trap

The DS-160 nonimmigrant visa application form now requires applicants to disclose social media handles across multiple platforms. Consular officers review that content before issuing or renewing a visa. The U.S. Embassy in India recently posted a reminder that screening continues even after a visa is granted — and that visas can be revoked at any time based on new information.

For employers, this creates a compliance minefield. What if an employee inadvertently omits a closed social media account — an old Facebook profile, a dormant Twitter handle — and the government later discovers it? The omission could be treated as a material misrepresentation, potentially jeopardising the employee's status and the company's petition.

"We use all available information in our visa screening and vetting to identify visa applicants who are inadmissible to the United States, including those who pose a threat to U.S. national security," the U.S. Embassy in India stated.

## The border search problem

Foreign nationals entering the United States are also increasingly subject to electronic device searches — laptops, phones, tablets — by Customs and Border Protection officers at ports of entry. While such searches fall within existing border authority, their rising frequency is alarming employers.

During these stops, CBP officers may ask travellers to unlock their devices, allowing direct review of social media activity, email, photos, and files. For companies whose employees carry proprietary data, trade secrets, or privileged communications on their devices, this creates a direct tension between immigration compliance and data security.

Reuters noted that HR leaders should consider proactive strategies: warning employees about heightened scrutiny before international travel, especially around holidays when foreign-national workers frequently visit family; developing device policies for border crossings; and auditing whether employees' social media activity could trigger visa complications.

## The Indian dimension

Indians dominate the H-1B programme — they receive roughly 72 per cent of all H-1B visas issued annually. That makes them disproportionately exposed to every new layer of vetting, every consular delay, and every border search policy.

The practical calculation for an Indian H-1B worker considering a trip home now involves a risk matrix that did not exist five years ago: Will the consulate reschedule my stamping appointment? Will my social media pass review? Will CBP search my laptop at re-entry? Will my employer's project survive if I am stuck abroad for three months?

Companies are adapting. Some have become more cautious about hiring international graduates, knowing that their employees' ability to travel freely is no longer guaranteed. Others are seeking alternative immigration solutions — cap-exempt H-1B programmes, O-1 visas for high achievers, or simply relocating roles to offices outside the United States.

"The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions," Danielle Goldman, co-founder and CEO of Build, told The Indian Eye.

## The quiet shift

What makes this moment different from previous immigration crackdowns is the target. The vetting regime is not aimed at undocumented workers or border crossers. It is aimed at legal visa holders — people who filed paperwork, paid fees, passed interviews, and received stamps in their passports. The message to corporate America is that sponsoring a foreign worker no longer ends at the petition approval. It extends to monitoring, advising, and managing risk across every international trip, every social media post, and every border encounter.

For the Indian diaspora, the shift is personal. The same worker who built a career at a Fortune 500 company, paid American taxes for a decade, and waited patiently in the green card line now needs to think twice before visiting ageing parents in Mumbai. That is not a policy detail. It is a lived reality for hundreds of thousands of families."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Employer Cannot Fix This Either. Social Media Vetting Is Now Corporate America's Problem",
    "subheadline": "A Reuters analysis details how DS-160 form changes, consular social media reviews, and border device searches are creating operational chaos for companies that depend on Indian H-1B talent.",
    "slug": make_slug("social-media-vetting-corporate-immigration-crisis-employer"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers — 72 per cent of all H-1B visas — are disproportionately exposed to every new vetting layer, and their employers are now bearing the operational cost of travel disruptions, compliance risks, and talent loss.",
    "tags": ["h1b", "social-media-vetting", "ds-160", "employer", "cbp", "visa-stamping", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/stricter-vetting-slower-processing-how-new-immigration-form-changes-are--pracin-2026-07-06/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "US Embassy in India", "url": "https://theindianeye.com/2026/07/05/us-embassy-in-india-warns-visa-holders-that-visa-screening-continues-even-after-visa-is-granted/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A person reviewing an opened passport — a routine task that now carries new risks for H-1B visa holders",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}

# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
