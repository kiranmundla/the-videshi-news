#!/usr/bin/env python3
"""
Immigration writer — 2026-06-29 01:00 PDT
Two articles:
1. The full cost map of the OBBBA fee regime for Indian immigrants
2. The 60-day grace period being undermined by USCIS automation
"""
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
# ARTICLE 1: The OBBBA Fee Regime
# ─────────────────────────────────────────────

article1_body = """The paperwork hasn't changed. The forms still carry the same names — I-129, I-140, I-485, N-400 — that immigration attorneys have filed for decades. What has changed, in the span of six months, is what the government charges for each one.

Since the One Big Beautiful Bill Act became law in mid-2025, the Trump administration has layered new fees onto virtually every immigration touchpoint. Some arrived through the statute itself. Others followed through rulemaking, presidential proclamations, and proposed regulations that are still accepting public comment. Taken individually, each hike is framed as an inflation adjustment or a cost-recovery measure. Taken together, they amount to something more fundamental: the most expensive period in the history of legal American immigration.

## The OBBBA base layer

The reconciliation bill imposed a constellation of new charges, most of which took effect on January 1, 2026. A $250 Visa Integrity Fee is now tacked onto every nonimmigrant visa issued abroad — meaning an Indian engineer at the Chennai consulate pays it before stepping on a plane. A $24 fee applies to every Form I-94 arrival record. Asylum applications, historically free, now cost $100, with an additional $100 owed for each year the application sits unresolved. Temporary Protected Status applications jumped from $80 to $510. Employment Authorization Documents for asylum seekers, parolees, and TPS holders rose to $560 for initial issuance.

For anyone facing immigration court, the picture is bleaker. Appeals to the Board of Immigration Appeals now cost $1,030 — up from the $110 fee that held for years before the OBBBA raised it by statute. A motion to reopen or reconsider runs between $900 and $1,325, depending on the form and context. Fee waivers, which once shielded applicants who could demonstrate financial hardship, have been eliminated for most OBBBA-imposed charges. Congress wrote that prohibition directly into the law.

## Layer two: the N-400 proposal

On June 24, USCIS published a proposed rulemaking that would raise the cost of applying for naturalized citizenship from $760 to $1,330 on paper, or from $710 to $1,280 online — increases of 75 and 80 percent respectively. If a citizenship application is denied and the applicant wants a hearing, the fee for Form N-336 would rise from $830 to $1,475. Most fee waivers and reduced-rate options would be eliminated.

The proposal is not yet final. Public comments are open until August 24, and a final rule could follow weeks later. But for the roughly 100,000 Indian-born green card holders who naturalize each year, the message is unmistakable: file before the window closes.

## Layer three: the $100,000 question

The H-1B proclamation fee remains in legal limbo. A Massachusetts federal judge struck it down on June 8 as exceeding presidential authority. But the government obtained a temporary stay, and USCIS continued collecting the fee while the appeal heads to the First Circuit. As of late June, the government was expected to request a formal stay from the appellate court. If granted, the $100,000 surcharge will remain in force for months — possibly into 2027 — while the legal battle plays out.

For employers sponsoring new H-1B workers, the uncertainty is itself a cost. Several mid-sized IT consulting firms have paused new petition filings entirely, according to immigration attorneys, preferring to wait for clarity rather than risk a six-figure payment that may or may not be refunded.

## Layer four: premium processing inflation

Effective March 1, 2026, USCIS raised premium processing fees to reflect Consumer Price Index changes from June 2023 through June 2025. Premium processing — the $2,805 expedited adjudication service that guarantees a response within 15 business days — is one of the few ways to escape the agency's growing processing backlogs. Employers who once considered it optional now treat it as a cost of doing business.

## What it actually costs

Consider a single Indian software engineer on an H-1B visa, sponsored by an employer, pursuing the standard path to citizenship. Before the OBBBA, the rough out-of-pocket journey — covering filing fees, biometrics, medical exams, and legal costs — ran approximately $8,000 to $12,000 over 10 to 15 years. Today, the same journey looks roughly like this:

- H-1B petition and related fees (employer-paid, but often factored into compensation): $5,000–$8,000
- Visa Integrity Fee at consulate: $250
- I-94 arrival fee: $24
- Premium processing (increasingly standard): $2,805
- I-140 immigrant worker petition: $715
- I-485 adjustment of status: $1,440
- Medical exam and biometrics: $500–$800
- N-400 citizenship application (proposed): $1,330
- Legal fees across the journey: $5,000–$15,000

Total: roughly $17,000 to $30,000 per person — before the $100,000 H-1B fee. For a family of four (primary applicant, spouse on H-4, two children), the combined fees can exceed $40,000. With the $100,000 fee: north of $140,000.

These numbers exclude the green card backlog itself. An Indian-born EB-2 applicant who filed an I-140 today could wait 10 to 15 years for a visa number to become available. During that wait, H-1B renewals, H-4 EAD renewals, and premium processing fees recur. Some attorneys estimate the lifetime immigration cost for an Indian family at $50,000 to $60,000 — even without the proclamation fee.

## The diaspora math

For roughly 500,000 Indian nationals currently on H-1B visas and the 700,000-plus in the employment-based green card backlog, these fees are not abstract policy. They are household budget items, alongside mortgages, tuition payments, and remittances to family in India.

The cumulative effect is a system that was already expensive, made dramatically more so in a compressed period. Whether the fees constitute a barrier to entry or merely a cost of admission depends, as it always has, on which side of the counter you are standing on.

The public comment period for the N-400 fee proposal closes August 24. For those who are eligible and have been deferring, the arithmetic is straightforward: file now, or pay more later."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Receipt That Never Ends. Every Fee Washington Has Added to Your Immigration File",
    "subheadline": "Since the One Big Beautiful Bill Act became law, the government has layered new charges onto virtually every immigration form. For an Indian family of four, the total path from H-1B to citizenship now runs north of $40,000 — before the $100,000 fee.",
    "slug": make_slug("obbba-immigration-fee-map-indian-family-cost"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians are the largest H-1B cohort and the longest-waiting green card applicants — the cumulative fee burden falls disproportionately on families who may spend 10-15 years in the pipeline, paying recurring costs at every step.",
    "tags": ["obbba", "immigration-fees", "uscis", "h1b", "green-card", "citizenship", "n-400"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS – FY 2026 Inflation Adjustment", "url": "https://www.uscis.gov/newsroom/alerts/uscis-announces-fy-2026-inflation-increase-for-certain-immigration-related-fees"},
        {"name": "USA TODAY – New Trump plan would hike US citizenship fees by 80%", "url": "https://www.usatoday.com/story/news/politics/2026/06/24/uscis-citizenship-fee-increase/77089341007/"},
        {"name": "Federal Register – Inflation Adjustment to HR-1 Immigration Fees", "url": "https://www.federalregister.gov/documents/2026/01/03/2025-30743/inflation-adjustment-to-hr-1-immigration-fees"},
        {"name": "Mondaq – One Big Beautiful Round-Up: What Employers Need to Know", "url": "https://www.lexology.com/library/detail.aspx?g=bf5e5c00-6d83-4f7c-9e1b-1de73bc7bb61"},
        {"name": "WR Immigration – Court Reinstates $100K H-1B Fee Pending Appeal", "url": "https://wolfsdorf.com/court-temporarily-reinstates-uscis-authority-to-collect-100000-h-1b-consular-processing-fee-pending-appeal/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Jamaica, Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ─────────────────────────────────────────────
# ARTICLE 2: The 60-Day Grace Period Under Siege
# ─────────────────────────────────────────────

article2_body = """When Ravi — a name changed for privacy — was laid off from a mid-sized cloud infrastructure company in San Jose in May, he did what immigration attorneys tell every H-1B worker to do: file a transfer petition with a new employer as fast as possible. He found a job offer within three weeks. His lawyer filed the H-1B transfer on Day 22 of the 60-day grace period. It was denied.

The denial letter, which his attorney shared with the immigration law blog Herman Legal Group, said Ravi was "not maintaining valid nonimmigrant status" at the time of filing. His former employer had submitted an H-1B withdrawal to USCIS during the grace period — a routine notification — and the agency's system appears to have treated it as an instant termination of status. The 60-day grace period, which federal regulations guarantee as a window for exactly this kind of action, was overridden.

Ravi's case is not isolated. Immigration attorneys across the country are reporting a pattern of H-1B transfer denials involving workers who filed well within the grace period but whose former employers withdrew the original H-1B petition before a new one was adjudicated.

## What the law actually says

The 60-day grace period is codified in federal regulation. Under 8 CFR 214.1(l)(2), H-1B holders whose employment ends — whether through layoff, resignation, or termination — may remain lawfully in the United States for up to 60 consecutive days, or until their I-94 expires, whichever comes first. During this window, they may file to transfer their H-1B to a new employer, change to a different visa status, or prepare to depart.

The regulation does not condition the grace period on the former employer refraining from withdrawing the H-1B petition. Withdrawal is a routine administrative step — employers file it to stop their own ongoing obligations — and it has historically been understood as distinct from the worker's immigration status during the grace period.

But immigration attorney Richard Herman, whose firm has documented multiple such denials in 2025 and 2026, says USCIS adjudication systems appear to be conflating the two events. "When the old employer files a withdrawal, the system flags the worker as out of status immediately," Herman told clients in a published advisory. "The grace period regulation is being overridden by what appears to be an automated process."

## The real-world window

The regulatory grace period is "up to" 60 days. In practice, immigration lawyers say the functional window is now closer to 10 to 20 days for many workers — and shrinking.

Several factors compress the timeline. Labor Condition Applications, which employers must file with the Department of Labor before submitting an H-1B transfer, now face longer processing times due to heightened prevailing-wage scrutiny. Employers are also more cautious about sponsoring transfers, wary of the regulatory complexity and potential $100,000 fee exposure for new petitions.

For the worker, a missed deadline — or a denial — triggers immediate consequences. Lawful presence ends. Any pending change-of-status applications are abandoned. H-4 dependent spouses lose their status simultaneously, and those with H-4 Employment Authorization Documents lose their work permits. Children in school remain enrolled but face uncertain legal footing.

## The B-2 fallback is closing

Previously, laid-off H-1B workers could file to change status to B-2 (tourist visa) as a stopgap — preserving lawful presence while searching for a new sponsor. This route always carried risk: B-2 holders cannot work, and the change-of-status petition could take months to adjudicate.

Now the route is narrower. In September 2025, the State Department eliminated most interview waivers for nonimmigrant visa applicants, tightening B-1/B-2 renewal procedures. USCIS has reportedly increased scrutiny of B-2 change-of-status requests from former H-1B holders, particularly those with pending I-140 petitions — viewing the B-2 filing as an intent indicator that may conflict with immigrant intent.

At the same time, DHS is in the final stages of a rulemaking that would rescind the H-4 EAD program — the work authorization that allows spouses of H-1B holders with approved I-140 petitions to work. If the rule is finalized, dual-income Indian households on H-1B/H-4 arrangements would lose a critical financial lifeline during any period of job disruption.

## The layoff math

The numbers are stark. According to Layoffs.fyi, more than 110,000 technology workers have lost jobs in 2026. Indians consistently account for the majority of H-1B approvals — roughly 72 percent in recent years — meaning they are disproportionately represented in any wave of tech-sector layoffs.

Oracle's June announcement of 21,000 job cuts was the largest single action, but the pattern is industry-wide. Meta, Amazon, and LinkedIn have all reduced headcount this year as companies restructure around artificial intelligence. For workers whose immigration status is tethered to a single employer, these are not just career setbacks. They are existential crises with a 60-day — or perhaps zero-day — clock.

## What to do

Immigration attorneys recommend several immediate steps for H-1B workers who lose their jobs:

**File the B-2 change-of-status application on Day 1.** Even if a new H-1B transfer is imminent, the B-2 filing preserves lawful presence as a backstop. Do not wait.

**Ask the former employer to delay the H-1B withdrawal.** The withdrawal is the trigger that appears to cause USCIS system flags. If the employer agrees to hold the withdrawal until a transfer is filed, the worker may avoid the automated denial.

**File the H-1B transfer with premium processing.** The $2,805 premium processing fee guarantees a response within 15 business days. In this context, it is not an optional convenience — it is the difference between adjudication within the grace period and a filing that goes unanswered until it is too late.

**Do not travel internationally.** Leaving the United States during the grace period or while a change-of-status application is pending terminates the application. The worker would need to re-enter on a valid visa, which may require a consular appointment — and consular wait times in India are now measured in months.

**Consult an attorney immediately.** The cases being denied involve technical procedural issues that generic guidance cannot address. Specific denial patterns suggest that USCIS is applying an interpretation that may be challengeable — but only if the response is timely and precise.

The 60-day grace period was designed as a humane buffer in a system that ties immigration status to employment. Whether it still functions as one depends on which side of the automation you land on."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "You Have 60 Days. USCIS Automation May Give You Zero",
    "subheadline": "Immigration attorneys are reporting a pattern of H-1B transfer denials for workers who filed within the 60-day grace period. The trigger: employer withdrawals that USCIS systems treat as instant status termination.",
    "slug": make_slug("h1b-60-day-grace-period-uscis-denial-automation"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 72 percent of H-1B visas and are disproportionately affected by tech layoffs. When the 60-day grace period stops working, entire families — spouses on H-4 EADs, children in American schools — face sudden legal limbo.",
    "tags": ["h1b", "grace-period", "uscis", "layoffs", "tech-workers", "h4-ead", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Herman Legal Group – USCIS Denying H-1B Transfers in 60-Day Grace Period", "url": "https://lawfirm4immigrants.com/terminated-h-1b-uscis-denying-transfers-60-day-grace/"},
        {"name": "Layoffs.fyi – 2026 Tech Layoff Tracker", "url": "https://layoffs.fyi/"},
        {"name": "Herman Legal Group – Lost Your H-1B Job? What to Do", "url": "https://lawfirm4immigrants.com/lost-h1b-job-what-to-do-60-day-grace-period/"},
        {"name": "Madhyamam – H-1B Layoffs Leave Workers With 60 Days", "url": "https://madhyamamonline.com/en-us/business/h-1b-layoffs-leave-indian-tech-workers-in-us-with-60-days-to-find-new-job-1259746"},
        {"name": "USCIS – Grace Period Guidance", "url": "https://www.uscis.gov/working-in-the-united-states/temporary-workers/h-1b-specialty-occupations-and-fashion-models/options-for-nonimmigrant-workers-following-termination-of-employment"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/3778952/pexels-photo-3778952.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A professional stares at a laptop, facing the uncertainty that follows a sudden layoff",
    "image_attribution": "Pexels",
    "body": article2_body,
}

# ─────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
