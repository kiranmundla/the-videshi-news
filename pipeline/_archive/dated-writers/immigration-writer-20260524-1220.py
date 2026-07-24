#!/usr/bin/env python3
"""Immigration writer for The Videshi — 2026-05-24 batch."""
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


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: USCIS Adjustment of Status Policy Memo
# ─────────────────────────────────────────────────────────────

art1_body = """The new USCIS policy memorandum PM-602-0199, released on May 22, is the most consequential immigration policy shift for Indian professionals in years. It reframes adjustment of status — the process by which a temporary visa holder applies for a green card without leaving the country — as "an extraordinary act of administrative grace" rather than a routine procedural step.

For the roughly 300,000 Indian nationals waiting in employment-based green card queues, many of whom have spent a decade or more on H-1B visas building careers and families in the United States, this is not an abstract policy debate. It is a direct threat to the only immigration pathway most of them know.

## What the Memo Actually Says

The memo instructs USCIS officers to apply heightened discretionary scrutiny to every I-485 (adjustment of status) application. Officers must now weigh a list of negative factors — including any conduct "inconsistent with the purpose of the visa," prior immigration violations, and failure to depart as originally planned. To overcome these factors, applicants must demonstrate "unusual or even outstanding" positive equities: deep family ties, long employment history, U.S. citizen children, home ownership, and community roots.

The key distinction: the memo does not abolish adjustment of status. It makes it harder to get approved. Immigration attorney David Yurkofsky, who published a detailed legal analysis the same day, called the characterization of AOS as "administrative grace" legally wrong. "Adjustment of Status is not a favour bestowed by bureaucrats. It is the law. INA Section 245. Written by Congress," he wrote. "A policy memo written on a government keyboard does not erase fifty years of statutory law."

## H-1B Holders Get a Carve-Out — Sort Of

There is one critical nuance the initial panic missed. The memo explicitly states that maintaining lawful status in a "dual-intent" visa category — which includes H-1B, L-1, O-1, and E-3 — is "not inconsistent with" applying for adjustment of status. This means H-1B holders retain a stronger legal footing than, say, F-1 students or B-1/B-2 visitors.

But the memo immediately undercuts that protection by adding: dual-intent status alone "is not sufficient, on its own, to warrant a favourable exercise of discretion." In practice, even H-1B holders will need to build a case showing why they deserve to adjust status domestically rather than processing through a consulate abroad.

## The Indian-Specific Calculus

For Indian nationals, the arithmetic is uniquely punishing. Employment-based green card backlogs for India already stretch decades — EB-2 India's final action date in the June 2026 Visa Bulletin retrogressed to September 2013, meaning applicants filed 13 years ago are only now becoming eligible. Unlike applicants from most other countries, Indians cannot simply "go home and apply" without risking years of additional delay.

A forced departure for consular processing interrupts employment, payroll, and project continuity. Immigration lawyers warn of an even darker scenario: anyone who has accumulated even inadvertent unlawful presence could trigger three-year or ten-year reentry bars upon departure — effectively locking them out of the country they have called home for a decade.

## What Happens Next

Over one million adjustment of status cases are currently pending, representing approximately $1.5 billion in filing fees USCIS has already collected. The agency is almost entirely fee-funded. As Yurkofsky noted, "The notion that it would simply cancel the process that finances its own operations defies basic institutional reality."

Legal challenges are expected. The memo provides no implementation timeline, no effective date, and no definition of "extraordinary circumstances." Courts have historically struck down attempts to nullify statutory provisions through internal policy memos.

For Indian H-1B holders, the practical advice from immigration attorneys is consistent: do not withdraw or abandon a pending I-485 application. Document everything — tax history, community ties, family circumstances, career progression. And consult a qualified immigration lawyer before making any decisions based on social media panic.

The memo is real, the tightening is real, and the anxiety is justified. But adjustment of status is not dead. It is harder."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "USCIS Declares Green Card Applications an 'Extraordinary Act of Grace' — What Indian H-1B Holders Need to Know",
    "subheadline": "A new policy memo rewrites the rules for adjusting immigration status from inside the United States. For the hundreds of thousands of Indians in employment-based queues, the ground just shifted.",
    "slug": make_slug("uscis-adjustment-of-status-memo-indian-h1b"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals hold 71% of H-1B visas and face the longest green card backlogs of any nationality. This memo directly threatens their ability to remain in the US while their applications process — a wait that already stretches 10-15 years for EB-2 India.",
    "tags": ["h1b", "uscis", "green-card", "adjustment-of-status", "immigration-policy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS Official Press Release", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"},
        {"name": "VisaVerge Analysis", "url": "https://www.visaverge.com/news/zoho-founder-sridhar-vembu-urges-indian-visa-holders-to-come-home-after-green-card-rule-tightening/"},
        {"name": "David Yurkofsky Legal Analysis (LinkedIn)", "url": "https://www.linkedin.com/pulse/stop-panic-david-yurkofsky-8yeoe"},
        {"name": "Manifest Law Breakdown (NewsPoint)", "url": "https://www.newspointapp.com/english/tech/immigration-law-firm-explains-changes-in-green-card-rules-for-h1-b-l-1-f-1-opt-visa-holders-heres-full-breakdown-of-uscis-memo-toi/articleshow/145048208774e4d51e5001be394116ceaf4a12d7"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────────────────────
# ARTICLE 2: H-1B FY2027 Registrations Drop 38.5%
# ─────────────────────────────────────────────────────────────

art2_body = """The numbers tell a stark story. H-1B visa registrations for fiscal year 2027 plummeted 38.5 per cent, from 343,981 to just 211,600 — the steepest single-year decline since the programme's creation. USCIS announced the figures on May 22, alongside data showing a dramatic compositional shift: 71.5 per cent of selected applicants now hold a US master's degree or higher, up from 57 per cent the previous year. Only 17.7 per cent of selected registrations fell in the lowest wage category.

For Indian tech workers — who account for roughly 71 per cent of all approved H-1B applications — these numbers represent the most significant recalibration of America's skilled-worker pipeline in a generation.

## What Drove the Drop

Three forces converged. First, the Trump administration's September 2025 executive order imposing a $100,000 fee on H-1B applications not accompanied by a payment to the government raised the cost of speculative or low-wage filings dramatically. Companies that previously submitted dozens of registrations for entry-level roles — particularly IT staffing firms — found the economics suddenly unworkable.

Second, USCIS shifted to a beneficiary-centric registration system that prevents the same person from being registered multiple times by different employers. The old system incentivised mass filings; the new one doesn't.

Third, the broader wage-weighted selection rules now actively favour higher-paid applicants. The combination of higher fees and wage-based selection has effectively killed the business model of filing large volumes of registrations for lower-wage positions and hoping a few get picked.

## Winners and Losers in the Indian Community

The impact is not uniform across the Indian diaspora. Indian professionals with advanced US degrees — the IIT-to-Stanford-to-Google pipeline — are, paradoxically, better positioned than ever. With nearly three-quarters of selections going to master's and PhD holders, a computer science graduate from a US university earning $150,000 at a major tech company has excellent odds.

The squeeze falls hardest on a different cohort: mid-career professionals brought in by Indian IT services firms at relatively lower wage levels. Companies like Infosys, TCS, and Wipro historically accounted for a significant share of H-1B registrations. The $100,000 fee and wage-weighted selection have forced these companies to rethink which roles justify US placement versus remote delivery from India.

For Indian students currently in the US on F-1 visas completing OPT or STEM OPT, the picture is mixed. Those with advanced degrees from US universities are now the programme's primary beneficiaries. Those with bachelor's degrees competing for spots face considerably longer odds than a year ago.

## The Staffing Industry Reckoning

USCIS framed the decline as evidence that "the days of abusing the programme with mass, low-wage registrations are over." The agency explicitly contrasted the current data with what it called "the low-wage and low-skilled foreign labour pipeline approved under Biden administration policies."

Immigration hardliners wanted more. Mark Krikorian, executive director of the Center for Immigration Studies, wrote on X that the changes were "all good, in the sense of being less bad" but argued the only real solution was "to abolish the H-1B programme altogether."

The staffing industry, predictably, sees it differently. Outsourcing firms argue they provide essential workforce flexibility, particularly for companies that cannot fill every mid-level technical role at Silicon Valley salaries. The 38.5 per cent drop suggests many of those arguments are no longer surviving the registration stage.

## What This Means Going Forward

For Indian professionals planning a US career, the message from the FY2027 data is blunt: the H-1B is increasingly a programme for highly educated, well-paid workers at established companies. The path through a US graduate degree into direct employment at a major firm remains viable — arguably more so than before, given reduced competition.

The path through an IT services firm at a Level 1 or Level 2 wage? That door is closing fast.

The combination of fewer total registrations and higher qualitative bars means fewer Indians will enter the H-1B pipeline each year. But those who do will, on average, earn more, hold higher degrees, and work at companies willing to pay a premium for their talent. Whether that makes the programme fairer or simply more exclusionary depends on which end of the Indian tech diaspora you sit on."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "H-1B Registrations Plunge 38.5% as Washington Reshapes America's Skilled-Worker Pipeline",
    "subheadline": "Fiscal year 2027 data reveals the steepest drop in H-1B lottery registrations ever recorded. Indian IT workers — 71% of the programme — face the sharpest reckoning.",
    "slug": make_slug("h1b-registrations-drop-fy2027-indian-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 71% of all approved H-1B visas. The registration drop and shift toward higher wages directly reshapes career planning for hundreds of thousands of Indian tech professionals, from fresh graduates on OPT to mid-career workers at IT services firms.",
    "tags": ["h1b", "uscis", "h1b-lottery", "it-services", "indian-tech-workers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries/article71011264.ece"},
        {"name": "VisaVerge - H-1B FY2027 Analysis", "url": "https://www.visaverge.com/news/h-1b-2026-fy-2027-lottery-registrations-drop/"},
        {"name": "USCIS Official Statement (via Gulte)", "url": "https://www.gulte.com/trends/202651/tough-times-ahead-for-h-1b-hopefuls"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────────────────────
# ARTICLE 3: EB-2 India Retrogression + Vembu "Come Home"
# ─────────────────────────────────────────────────────────────

art3_body = """When Zoho founder Sridhar Vembu posted "Please come home" on X last Friday, he was not making a general philosophical point about the Indian diaspora. He was responding to a week that delivered a one-two punch to every Indian professional waiting for a US green card: a USCIS memo restricting domestic adjustment of status, followed by a June 2026 Visa Bulletin that moved EB-2 India backward by more than ten months.

The EB-2 final action date for India retrogressed to September 1, 2013 — a 10.4-month step backward. EB-1 India, which covers priority workers and those with extraordinary ability, also retrogressed by 3.5 months to December 15, 2022. The sole bright spot, EB-3 India, inched forward by a single month to December 15, 2013.

For anyone unfamiliar with visa bulletin arithmetic: if you are an Indian national whose EB-2 priority date is after September 2013, your green card application cannot move forward until the final action date reaches your date. People who filed in 2014 are now watching the queue move in the wrong direction.

## The Double Bind

What makes this week different from the usual monthly bulletin disappointment is the simultaneous USCIS policy change on adjustment of status. Until now, Indians in the EB-2 and EB-3 backlog could at least file their I-485 applications and receive work authorisation (EAD) and travel documents (advance parole) while they waited. This allowed them to change jobs, start businesses, and travel internationally — all while their green card applications sat in line.

The new USCIS memo, PM-602-0199, declares adjustment of status an "extraordinary form of relief" and pushes applicants toward consular processing abroad. For Indian professionals who have been in the US for a decade or more, this creates an impossible calculus: leave the country for consular processing and risk triggering reentry bars, employment gaps, and multi-year delays — or stay and face heightened scrutiny on an I-485 that may take another decade to reach final adjudication.

Immigration attorneys note that long-tenured H-1B holders with US citizen children, established careers, and deep community ties have strong equities under the memo's own framework. But "strong equities" and "guaranteed approval" are not the same thing when adjudicating officers are being instructed to treat every case as exceptional rather than routine.

## Vembu's Calculated Appeal

Sridhar Vembu is not a random commentator. As the founder and CEO of Zoho, he runs a $1 billion software company headquartered in Chennai that competes directly with US tech firms. He has long argued that India's technology ecosystem can absorb the talent currently flowing to Silicon Valley — and that the flow should reverse.

"Even if you feel it is hardship and sacrifice, self-respect should dictate your course," he wrote. "Let's make Bharat proud."

The message landed differently depending on where you sit. For Indians who have spent their prime career years building American companies while stuck in a green card queue that predates their children's births, "come home" can feel dismissive of the real economic and personal costs of uprooting a life. For others — particularly younger professionals weighing whether to enter the US immigration system at all — it reads as practical advice: India's startup ecosystem now offers real alternatives, and the US path has never been more uncertain.

## The Numbers Behind the Frustration

The scale of the Indian green card backlog defies easy comprehension. By recent estimates, over 400,000 Indian nationals are waiting in employment-based queues, with total wait times exceeding 80 years for new EB-2 applicants based on current movement rates. These are not unskilled workers — they are software engineers, data scientists, product managers, and medical researchers who have already been vetted, employed, and tax-paying for years.

The retrogression means some applicants who had expected to reach the front of the line this year are now pushed back to 2027 or beyond. Meanwhile, their H-1B status requires employer sponsorship, their spouses' H-4 EAD work permits remain under legal threat, and their children risk "ageing out" of dependent status at 21 — potentially requiring them to enter the immigration queue independently or leave the country.

## No Easy Answers

The honest assessment is this: the combination of visa bulletin retrogression, tightened AOS rules, and elevated H-1B fees has made the American immigration system harder for Indians than at any point in recent memory. Congress has shown no appetite for addressing employment-based backlogs. The courts may strike down the AOS memo, but litigation takes years.

Vembu's "come home" is one answer. It is not the only one. But the question he's asking — whether the US immigration system still offers a rational return on a decade of patience — has never been harder to answer with confidence."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "EB-2 India Slides Backward as Zoho's Vembu Tells Indians: 'Come Home'",
    "subheadline": "The June visa bulletin retrogressed EB-2 India by ten months. Combined with the USCIS adjustment of status crackdown, it marks the toughest week for Indian green card seekers in years.",
    "slug": make_slug("eb2-india-retrogression-vembu-come-home"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Over 400,000 Indian nationals are stuck in employment-based green card queues stretching 80+ years. This week's visa bulletin retrogression and AOS policy change together represent the most significant deterioration of their immigration outlook in recent memory.",
    "tags": ["green-card", "eb2", "visa-bulletin", "sridhar-vembu", "reverse-brain-drain", "immigration-backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge - Vembu & AOS Impact", "url": "https://www.visaverge.com/news/zoho-founder-sridhar-vembu-urges-indian-visa-holders-to-come-home-after-green-card-rule-tightening/"},
        {"name": "State Department Visa Bulletin (via VisaVerge)", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries/article71011264.ece"},
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/30782813/pexels-photo-30782813.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
