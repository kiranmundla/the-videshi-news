#!/usr/bin/env python3
"""Immigration writer — 2026-05-27 01:09 PDT run"""
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


# ── Article 1 ──────────────────────────────────────────────────────────────

art1_body = """The H-1B lottery as Indian professionals knew it — a mass random draw where sheer volume of registrations mattered more than the quality of the job offer — is finished. In its place sits a wage-weighted selection system that just posted its first full-cycle numbers, and the results are stark.

USCIS reported that properly submitted H-1B registrations for Fiscal Year 2027 fell to 211,600 from 343,981 in the prior cycle — a drop of 38.5 percent. The agency celebrated the decline on X, calling it proof that "the days of abusing the program with mass, low-wage registrations are over."

## The new math

Two structural changes drove the collapse. First, the beneficiary-centric selection process finalized in 2024 eliminated the old advantage of having multiple employers register the same worker. Under the previous system, a single beneficiary registered by five companies effectively got five lottery tickets. That incentive is gone.

Second — and more consequential — DHS introduced wage-based weighting for FY 2027. Jobs classified at Wage Level IV now receive four entries in the selection pool. Level III gets three. Level II gets two. Level I — the lowest-paid roles — gets one. The lottery still exists in name, but the dice are loaded toward higher-paying positions.

The results bear this out. A record 71.5 percent of selected applicants held a U.S. master's degree or higher, up from 57 percent the previous year. Only 17.7 percent of selected registrations fell in the lowest wage category.

## What this means for Indian professionals

Indians account for roughly 71 percent of all approved H-1B applications. The community sits squarely at the center of this shift, and the impact will cut differently depending on where you stand.

For Indian engineers and researchers at major tech firms — the Googles, Microsofts, and Apples paying Level III and IV wages — the math actually improves. A smaller registration pool combined with wage weighting means their employers' petitions carry more weight than before.

The pain falls elsewhere. Indian IT consulting and staffing firms that built their business models around high-volume, lower-wage registrations face a structural reckoning. Under the old random lottery, filing 500 registrations at Level I wages was a viable strategy. Under wage weighting, those same 500 registrations carry the statistical weight of 125 Level IV filings.

Entry-level positions present a particular problem. Many Indian graduates of U.S. master's programs start in roles that fall into lower wage bands, especially outside expensive coastal metros. A freshly minted MS in computer science taking a $85,000 job in Raleigh or Austin may find their registration carries less weight than a mid-career engineer's $175,000 role in San Jose — even though both hold the same degree.

## The STEM OPT squeeze

International students on F-1 visas using Optional Practical Training — the work authorization bridge between graduation and H-1B filing — face a tighter corridor. STEM OPT can buy time, and cap-exempt H-1B positions at universities and research institutions remain outside the annual lottery. But the old assumption that completing a U.S. degree created a reliable on-ramp to H-1B status no longer holds.

Students considering the next cycle need early answers from employers on sponsorship intent and, critically, on expected wage level. A company that plans to file at Level I is making a materially weaker bet than one filing at Level III.

## The consulting model under pressure

Staffing and consulting companies face a second layer of exposure even after selection. Winning a place in the lottery no longer carries much value if the employer cannot convert that registration into an approvable petition backed by consistent documentation, a defensible job offer, and a clear client arrangement.

USCIS can still issue Requests for Evidence, deny petitions, or revoke approvals if the filing record does not support the case. In the current enforcement climate, post-selection scrutiny matters almost as much as selection itself.

## What to do now

The FY 2027 data reads less like a planning statistic than a signal that the H-1B program's center of gravity has permanently shifted. Indian professionals and the families investing in their U.S. education need to recalibrate.

Those not selected still have options: remaining OPT or STEM OPT time, cap-exempt positions, O-1 extraordinary ability petitions, or L-1 intracompany transfers. Some may find that the calculus now favors exploring opportunities in Canada, the UK, or Germany rather than treating the H-1B as the sole path forward.

The program remains open. But it is no longer the same program. Wage level, employer credibility, and documentation strength now determine the outcome as much as the draw itself."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The H-1B Lottery Is Dead — Registrations Crash 38.5% as Wage-Based Selection Reshapes Who Gets In",
    "subheadline": "USCIS data shows a smaller, richer applicant pool — and Indian IT consulting firms are taking the hardest hit.",
    "slug": make_slug("h1b-lottery-dead-wage-selection-registrations-crash"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians account for 71% of H-1B approvals and are disproportionately affected by the shift from random selection to wage weighting. Entry-level Indian engineers and IT consulting firms face structural disadvantages under the new system.",
    "tags": ["h1b", "uscis", "wage-based-selection", "immigration", "lottery"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/h-1b-lottery-shifts-in-fiscal-year-2027-favoring-us-masters-degree-holders/"},
        {"name": "TelecomLive", "url": "https://telecomlive.in/web/2026/05/25/h-1b-visa-registrations-drop-38-5-in-fy-2027/"},
        {"name": "TelecomLive (Attorney Analysis)", "url": "https://telecomlive.in/web/2026/05/23/38-5-drop-in-h-1b-registrations-for-fy-2027-immigration-attorney-says-numbers-were-like-this-10-years-ago/"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/headlines/h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
    "body": art1_body,
}


# ── Article 2 ──────────────────────────────────────────────────────────────

art2_body = """The Department of Labor's proposed overhaul of H-1B prevailing wages was billed as a landmark reform. Raise the floor, protect American workers, end the wage-suppression critique that has dogged the visa program for decades. A new analysis suggests the rule may accomplish none of those things — and may not survive legal challenge either.

A Forbes report published this week concluded that the DOL's proposed rule to increase prevailing wages for H-1B holders is "likely unlawful." Separately, critics from the restrictionist side argue the increases do not go nearly far enough. The result: a rule that has managed to unite its opponents without satisfying anyone.

## The 34th-percentile problem

At the center of the controversy is the prevailing wage structure. The DOL divides wages into four levels. For years, Level I — the entry point where many H-1B petitions are filed — was set at roughly the 17th percentile. That meant employers could legally pay an H-1B worker less than what more than 80 percent of American workers in the same occupation and location were already earning.

The proposed rule would raise Level I to around the 34th percentile. On paper, that looks like a meaningful jump. In practice, it means employers would still be permitted to pay H-1B workers below what two-thirds of their American peers earn — with full government approval.

As Kevin Lynn, executive director of the Institute for Sound Public Policy, wrote in an analysis for the Daily Caller: "Any wage floor set below the median mathematically guarantees that H-1B workers will cost less than the typical American in the same role. The 34th percentile does not represent a reasonable compromise. It represents a built-in discount written into federal regulation."

## The dollar gap in real cities

The numbers get sharper at the local level. Bloomberg reported that under the proposed rules, an entry-level software engineer in San Francisco would need to earn at least $162,000 annually. In New York, the floor rises to $132,000. In Dallas, $113,000.

Those figures sound high until you compare them to what senior engineers in those markets actually earn. In San Jose, where the median software engineer salary runs roughly $140,000, the proposed Level I floor would still allow employers to bring in H-1B workers at $95,000 — a $45,000 discount on the going rate. Multiply that across hundreds of positions at a single company and the labor-cost arbitrage becomes enormous.

The tiered structure creates its own perverse incentive. Level II wages currently sit at roughly the 34th percentile. Raising Level I to that same threshold means companies will simply reclassify more positions into the revised Level I category while continuing to pay below market rates. The labels change; the economics don't.

## The legal question

From the other direction, the Forbes analysis raises a different problem entirely. The report argues the DOL may have exceeded its statutory authority in setting the new wage floors, making the rule vulnerable to challenge in federal court.

No business has yet filed a lawsuit. But immigration attorneys say the legal landscape is shifting. The rule went into effect on February 27, 2026, and applied to the FY 2027 H-1B lottery cycle that began on March 4. If a court strikes it down — or enjoins enforcement — companies and workers would face yet another mid-cycle policy reversal.

Jonathan Grode, an immigration attorney at Green & Spiegel, told Forbes that the "constant barrage of negative news and regulation on the H-1B front is having an effect." Top talent now looks to Germany, Canada, and other countries actively courting skilled workers.

## Why this matters to Indian professionals

Indians hold approximately 71 percent of all approved H-1B visas. Every percentage point shift in prevailing wages directly affects their paychecks, their employers' willingness to sponsor, and their path to permanent residency.

For mid-career Indian engineers at major tech firms, the wage floors may pose little practical change — their compensation already exceeds the proposed thresholds. The impact concentrates on two groups: entry-level workers fresh out of U.S. graduate programs taking their first industry roles, and employees at IT consulting and staffing firms where margins depend on the spread between the client billing rate and the worker's salary.

If the rule stands, some employers may stop sponsoring positions they can no longer staff profitably. If it falls in court, workers face the whiplash of another policy reversal. Either way, the 400,000-plus H-1B holders currently in the U.S. are caught between a wage floor that critics call inadequate and a regulatory framework that lawyers call legally fragile.

## The waiting game

The comment period has closed. A final rule could arrive late this year or early next. In the meantime, employers are already adjusting their H-1B strategies — filing fewer petitions, targeting higher-wage roles, and in some cases relocating positions to offices in India, Canada, or Europe rather than navigating the uncertainty.

For the Indian engineer sitting in Sunnyvale with a pending I-140 and a mortgage, the prevailing wage debate is not an abstraction. It is the arithmetic that determines whether their employer keeps sponsoring their green card — or decides the numbers no longer work."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The H-1B Wage Rule That Was Supposed to Protect American Workers May Be Protecting No One",
    "subheadline": "A new report calls it likely unlawful. Critics say it still allows a built-in discount. Indian workers are caught in between.",
    "slug": make_slug("h1b-wage-rule-dol-legal-challenge-34th-percentile"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 71% of H-1B visas. The prevailing wage rule directly affects their compensation, employer willingness to sponsor, and the viability of the IT consulting model that employs hundreds of thousands of Indian workers.",
    "tags": ["h1b", "prevailing-wage", "dol", "immigration", "wages"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Forbes (via Employment Law Information Network)", "url": "https://www.elinfonet.com/tag/forbes/"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/05/22/trumps-labor-department-h1-b-visas-prevailing-wage-rule/"},
        {"name": "WebProNews / Fortune Workforce Innovation Summit", "url": "https://www.webpronews.com/trumps-visa-squeeze-leaves-tech-talent-stranded-and-forces-companies-to-rethink-retention/"},
        {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"}
    ]),
    "score_total": 76,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7876740/pexels-photo-7876740.jpeg",
    "body": art2_body,
}


# ── Publish ────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
