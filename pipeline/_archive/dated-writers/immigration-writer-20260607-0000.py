#!/usr/bin/env python3
"""Immigration writer – 2026-06-07 00:00 UTC run.

Two fresh articles:
1. FinCEN banking advisory – 18 red flags turn banks into immigration enforcers
2. DHS proposes ending Duration of Status for F-1 students
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

# ──────────────────────────────────────────────────────────────
# ARTICLE 1: FinCEN banking advisory
# ──────────────────────────────────────────────────────────────

article1_body = """The U.S. Treasury Department has turned the nation's banks into a new front line of immigration enforcement. On June 6, the Financial Crimes Enforcement Network — the Treasury bureau known as FinCEN — published a 12-page advisory listing 18 red flags that financial institutions should watch for when processing accounts tied to unauthorised workers. The advisory directs banks to file suspicious activity reports and, where warranted, to refer cases directly to Immigration and Customs Enforcement.

The advisory carries out a May 19 executive order signed by President Donald Trump that pulled the banking system into the broader crackdown on immigration. That order directed bank regulators to look for signs that people without legal status are opening accounts, obtaining loans, or using credit cards. The FinCEN advisory translates that directive into operational guidance.

## $2.5 Billion in Suspicious Activity

The numbers are large. Banks reported more than $2.5 billion in suspicious activity from payroll tax-fraud schemes in 2025 alone, according to Treasury. The advisory zeroes in on a specific pattern: an employer hires a labour broker, the broker sets up a shell company under a generic name, opens a bank account with a foreign passport or Individual Taxpayer Identification Number (ITIN), deposits checks for phantom services, and then cashes out or writes dozens of small checks to pay workers off the books. The employer dodges every payroll tax.

Among the 18 red flags: a self-described "labourer" who opens an ITIN account and receives floods of checks from multiple companies; a construction or staffing firm that earns large revenue but reports almost no payroll; any company under two years old with no online footprint. FinCEN cautioned that no single red flag proves guilt and that customers' personal characteristics should not create automatic risk — a nod to fair-lending rules that protect legitimate ITIN holders.

## The Collateral Damage for Legal Immigrants

The advisory is aimed squarely at illegal employment schemes. But its ripple effects will reach far beyond that target.

Thousands of H-4 dependent spouses — overwhelmingly Indian women married to H-1B workers — use ITINs because they are not eligible for Social Security numbers unless they hold a valid Employment Authorization Document. Under heightened scrutiny, their routine banking activity — opening savings accounts, applying for credit cards, making household purchases — could trigger additional reviews.

The advisory lands alongside a series of other financial restrictions that have reshaped how immigrants interact with the American banking system. In May 2025, the Department of Housing and Urban Development barred non-permanent residents, including H-1B holders, from accessing FHA-insured mortgages. Data from John Burns Research and Consulting shows FHA loan volume for non-permanent residents collapsed from 6 percent in April 2025 to virtually zero by late summer.

Separately, the Consumer Financial Protection Bureau has reportedly instructed lenders to verify immigration status before approving mortgages — a step that adds bureaucratic friction and delays for H-1B holders who have been paying taxes and building credit for years.

## Why This Matters to Indian Americans

Indian nationals hold roughly three-quarters of all H-1B visas approved in any given year. Their families — spouses on H-4 visas, children aging through the system — are disproportionately exposed to every new layer of financial scrutiny.

The practical effect is a tightening loop. You cannot get an FHA mortgage. Your bank may flag your ITIN account. Your spouse's EAD renewal is pending for months while USCIS processing times stretch to 19.5 months for I-765 applications. And the same administration that imposed the $100,000 fee on new H-1B petitions — effectively pricing out mid-tier sponsors — is now enlisting your bank as a compliance checkpoint.

Treasury Secretary Scott Bessent framed the advisory as a matter of fiscal integrity. "This administration will not allow illegal aliens to abuse financial institutions to steal billions of dollars from hardworking American taxpayers," he said.

For the hundreds of thousands of Indian professionals who are neither illegal nor abusing anything — who are waiting in a green card backlog that now exceeds 627,000 people from India alone, according to Brookings — the message is harder to parse. Their banks are watching. The question is whether anyone in Washington is watching the distinction between the workers the system invited and the ones it didn't.

*Sources: New York Post, Reuters, Associated Press, Brookings Institution*"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Bank Is Watching — FinCEN Just Handed 18 Red Flags to Every Lender in America",
    "subheadline": "A new Treasury advisory turns financial institutions into immigration enforcement checkpoints. The targets are illegal payroll schemes — but the fallout will reach every ITIN-holding immigrant family in the country.",
    "slug": make_slug("fincen-18-red-flags-banks-immigration-enforcement-itin"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "H-4 spouses who use ITINs, H-1B workers already locked out of FHA mortgages, and families navigating a banking system increasingly enlisted as an immigration checkpoint — Indian Americans sit at the intersection of every new financial restriction.",
    "tags": ["fincen", "treasury", "banking", "itin", "h1b", "h4", "immigration-enforcement"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "New York Post", "url": "https://nypost.com/2026/06/05/business/treasury-dept-moves-to-crack-down-on-illegal-immigrant-labor-urging-banks-to-report-red-flags/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Associated Press", "url": "https://apnews.com/"},
        {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/The_Treasury_Department_North_side_20240601.jpg/1280px-The_Treasury_Department_North_side_20240601.jpg",
    "image_caption": "The U.S. Treasury Department building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": article1_body,
}

# ──────────────────────────────────────────────────────────────
# ARTICLE 2: DHS proposes ending Duration of Status for F-1
# ──────────────────────────────────────────────────────────────

article2_body = """For decades, international students in the United States have operated under a simple framework: stay enrolled, stay legal. The "Duration of Status" system meant that as long as an F-1 visa holder remained a full-time student in good standing, their authorised stay had no fixed expiration date. The clock stopped when they graduated, not when a calendar date arrived.

That framework is about to end. On May 5, the Department of Homeland Security published a proposed rule that would replace Duration of Status with fixed admission periods of up to four years. Any student needing to stay beyond that window — to complete a doctorate, finish a clinical rotation, or pursue post-graduation work through Optional Practical Training — would need to apply to USCIS for a formal extension, compete with the agency's notoriously long processing queues, and hope for approval before their authorised stay expires.

## What the Rule Actually Does

The proposal has three core components. First, the elimination of Duration of Status itself — a structural change that transforms every F-1 student from an indefinite-stay authorised learner into a time-limited visitor who must periodically reapply for permission to remain. Second, a reduction in the post-completion grace period from 60 days to 30 days, cutting in half the window students have to secure a new visa category or leave the country after their programme ends. Third, a requirement that extensions beyond four years go through USCIS rather than being handled by the student's university, adding a federal bureaucratic step to what was previously a campus-level process.

"The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," said Danielle Goldman, co-founder and CEO of immigration advisory firm Build.

## The Day-1 CPT Bottleneck

The rule's impact on Day-1 Curricular Practical Training programmes — a lifeline for thousands of Indian graduates who fail the H-1B lottery — could be severe. Under the current system, a graduate who loses the lottery can enrol in another academic programme and immediately begin working under CPT authorisation. It is a legal workaround, but a functional one.

Under the proposed framework, Goldman warned, that path narrows dramatically. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" she said.

The timing is not coincidental. USCIS data shows that the FY2027 H-1B lottery cap was hit on March 31, 2026 — just 25 days after applications opened. Of the 343,981 eligible registrations, only 120,141 were selected. For the roughly 224,000 who were not, the options are shrinking.

## The Numbers Tell the Story

The proposed rule arrives as international student enrolment is already in free fall. The Institute of International Education's Fall 2025 snapshot found a 17 percent drop in new international enrolments across more than 825 U.S. colleges and universities. About 96 percent of schools with declines cited visa issues as the leading cause.

Indian students have been hit hardest. Data from the Student and Exchange Visitor Information System shows a 28 percent year-on-year decline in active Indian students by March 2025. The count dropped sharply from 348,446 in July 2024 to 255,447 by August — the month that typically coincides with the fall admission cycle — and has not recovered.

Brookings projects a 29 percent decline in F-1 visa issuances for calendar year 2025, based on reported data through the first eight months. That decline would mark the steepest drop in student visa issuances in at least two decades.

## The Talent Pipeline Fracture

The downstream effects are already visible. Forty percent of initial H-1B approvals each year go to former F-1 visa holders. Three-quarters of employment-based green cards are issued to people already present in the United States on temporary visas. When the student pipeline contracts, the work visa pipeline follows, and the green card pipeline narrows behind it.

Goldman warned the consequences extend beyond immigration. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said. Foreign nationals make up a substantial share of the U.S. AI talent pool, and firms already struggling with the $100,000 H-1B petition fee will face further constraints on their ability to recruit.

For Indian families who have invested lakhs in American master's degrees — many betting on a path from F-1 to OPT to H-1B to green card — the proposed rule rewrites the calculus. The path is still there, but the margins for error have collapsed to 30 days.

*Sources: The Indian Eye, Brookings Institution, Institute of International Education, USCIS*"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Four Years and You're Out — DHS Wants to End Open-Ended Student Visas for Good",
    "subheadline": "A proposed rule would replace the decades-old Duration of Status framework with fixed four-year admission periods, slash grace periods in half, and force every F-1 extension through USCIS — at a time when Indian student enrolment has already dropped 28 percent.",
    "slug": make_slug("dhs-duration-of-status-f1-student-visa-four-year-limit"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students — the largest F-1 cohort and the biggest H-1B lottery applicant pool — face the sharpest impact from a rule that narrows Day-1 CPT, cuts grace periods, and adds USCIS bottlenecks to a pipeline already buckling under 28 percent enrolment declines.",
    "tags": ["f1-visa", "duration-of-status", "international-students", "opt", "cpt", "dhs", "indian-students"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
        {"name": "Institute of International Education", "url": "https://www.iie.org/"},
        {"name": "USCIS", "url": "https://www.uscis.gov/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7713182/pexels-photo-7713182.jpeg",
    "image_caption": "International graduates in academic dress at a U.S. university commencement ceremony",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": article2_body,
}

# ──────────────────────────────────────────────────────────────
# Insert articles
# ──────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
