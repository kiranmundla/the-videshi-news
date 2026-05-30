#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-30 16:00 UTC batch"""
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

# Verify images before using
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except Exception:
        return False

# Image URLs
img1 = "https://images.pexels.com/photos/6803542/pexels-photo-6803542.jpeg"
img2 = "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg"

for url in [img1, img2]:
    if not verify_image(url):
        print(f"⚠️  Image verification failed: {url}")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "110,000 and Counting — The 2026 Tech Layoff Wave Is Pushing Indian H-1B Workers to the Edge",
        "subheadline": "Meta, Amazon, Oracle, and LinkedIn are cutting thousands. For Indian professionals on H-1B visas, each pink slip triggers a 60-day countdown that now runs into a wall of closed doors.",
        "slug": make_slug("tech-layoffs-h1b-60-day-clock-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold roughly three-quarters of all H-1B visas. Every tech layoff disproportionately hits Indian workers, who face both the 60-day grace period and a green card backlog stretching decades. The convergence of mass layoffs, a $100K sponsorship fee, and a new AOS memo closing in-country adjustment means there may be no viable path left for thousands.",
        "tags": ["h1b", "layoffs", "tech", "visa", "60-day-grace-period", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://storyboard18.com/brand-marketing/60-days-or-leave-us-tech-layoffs-put-indian-h-1b-workers-under-pressure-63440.htm"},
            {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/en/topic/international/2026/may/21/h-1b-layoffs-leave-indian-tech-workers-in-us-with-60-days-to-find-new-job-963861"},
            {"name": "Layoffs.fyi", "url": "https://layoffs.fyi"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-29/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img1,
        "body": """The numbers are no longer abstract. According to data tracked by Layoffs.fyi, more than 110,000 technology workers across 144 companies have lost their jobs in 2026. Meta alone has cut roughly 8,000 positions while simultaneously redirecting 7,000 employees toward artificial intelligence projects. Amazon, Oracle, and LinkedIn have carried out their own rounds. For American workers, a layoff is a career disruption. For Indian professionals on H-1B visas — who account for approximately three-quarters of all H-1B holders — it is something closer to an existential event.

## The 60-Day Countdown

Under current U.S. immigration rules, an H-1B worker who loses their job has exactly 60 days to find a new employer willing to sponsor their visa, change to a different immigration status, or leave the country. The clock starts ticking the day after the last paycheck clears.

For someone who has spent a decade building a life in America — with children enrolled in school, a mortgage, and a green card application that may not be adjudicated for another 15 years — 60 days is not a runway. It is a forced march.

"You spend 10 years building a life. And now you have 60 days to sell your house, to sell your car, to get your kids out of school, and leave the country," immigration attorney Sophie Alcorn told Marketplace, describing the experience of laid-off H-1B holders she has represented.

## The Escape Routes Are Closing

In previous layoff cycles, the standard playbook was relatively straightforward: file a B-1 or B-2 change-of-status application to buy time, or find another employer and transfer the H-1B. Both options are now significantly harder.

Immigration attorney Rajiv Khanna told the Economic Times that his practice has seen "a significant spike in RFEs and Notices of Intent to Deny on B-1/B-2 change-of-status applications filed by laid-off H-1B workers." The message from USCIS adjudicators appears clear: the visitor visa is no longer a reliable pressure valve.

Meanwhile, the $100,000 fee that President Trump imposed on new H-1B petitions last September has effectively frozen the sponsorship pipeline. As of February 2026, only 85 companies had paid the fee, according to a government court filing. The companies that once absorbed displaced H-1B talent — mid-tier consulting firms, staffing agencies, growth-stage startups — simply cannot afford $100,000 per hire on top of existing legal and compliance costs.

## The AOS Memo Closes the Last Door

For Indian workers who held out hope of converting to permanent residency through adjustment of status, a May 21 USCIS policy memorandum has added a new layer of risk. The agency announced it would grant in-country green card adjustments "only in extraordinary circumstances," effectively pushing applicants toward consular processing abroad.

The catch is brutal in its simplicity. If an AOS application is denied and the applicant has no valid underlying nonimmigrant status — which is precisely the situation a laid-off H-1B worker faces after the grace period expires — they begin accruing unlawful presence. Departing the country after more than 180 days of unlawful presence triggers a three-year or ten-year inadmissibility bar. The door does not just close; it locks from the outside.

## What Changed This Time

Tech layoffs are not new. The 2022-2023 cycle saw similar devastation at Meta, Twitter, and Stripe. But the policy environment surrounding those cuts was qualitatively different. The 60-day grace period existed alongside a functional AOS system, a reasonable H-1B fee structure, and B-2 applications that were routinely approved. All four safety nets have been weakened simultaneously.

The result is what immigration attorneys are privately calling a "triple squeeze": laid-off workers face a shortened practical grace period (thanks to increased RFEs), an impossibly expensive sponsorship market (thanks to the $100,000 fee), and a greencard pathway that now requires leaving the country (thanks to the AOS memo).

## The Human Geography

The impact extends well beyond immigration law. Indian tech workers in the Bay Area, Seattle, Austin, and the New York metro hold mortgages, pay property taxes, volunteer at their children's schools, and contribute to local economies. A family facing the 60-day clock must simultaneously navigate job interviews, visa paperwork, school withdrawal, property sales, and the emotional weight of explaining to a teenager why they have to leave the country they have lived in since preschool.

A presidential advisory panel has recommended extending the grace period from 60 to 180 days — a proposal that has not been adopted. For the more than 110,000 workers who have already received their notices in 2026, the recommendation is academic.

The tech industry built its workforce on the promise that it could recruit the best talent from anywhere in the world. The promise was always conditional. For Indian H-1B holders navigating 2026, the conditions have become impossible to meet."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Green Card Trap Nobody Explained — How a Denied I-485 Could Lock You Out of America for a Decade",
        "subheadline": "USCIS's new adjustment-of-status memo doesn't just raise the bar for in-country green cards. For applicants who get denied and lack valid status, it triggers an inadmissibility bar that could keep them from returning for three to ten years.",
        "slug": make_slug("aos-denial-catch-22-inadmissibility-bar-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals are uniquely exposed to this trap. With EB-2 India now unavailable until October 2026 and green card wait times stretching past 10 years, many Indian H-1B workers have pending I-485 applications. If denied under the new 'extraordinary circumstances' standard and they lack valid H-1B status, they face a Catch-22: stay and accrue unlawful presence, or leave and trigger a multi-year bar on re-entry.",
        "tags": ["green-card", "i-485", "aos", "uscis", "inadmissibility-bar", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/employer-applicant-advisory-in-depth-analysis-and-faqs-of-uscis-policy-memorandum-on-i-485-adjustment-of-status-discretion-and-consular-processing-pm-602-0199/"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/05/28/uscis-green-card-announcement-what-to-know/84626113007/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/immigration/3441507/green-card-changes-force-applicants-leave-country/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/trump-administration-ends-us-based-green-cards-for-temporary-visa-holders"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": img2,
        "body": """The headlines about USCIS Policy Memorandum PM-602-0199 have focused on the big picture: in-country green card adjustments will now be reserved for "extraordinary circumstances." Applicants should expect to be routed through consular processing abroad. The shift is dramatic. But the real danger is in the fine print — specifically, what happens when an adjustment-of-status application is denied.

Immigration attorneys who have parsed the memo line by line are flagging a consequence that most applicants have not yet processed. For Indian workers on H-1B visas with pending I-485 applications, a denial does not simply mean starting over. It can mean being locked out of the United States for three to ten years.

## The Mechanism

The logic works like a trap with three stages.

**Stage one:** An H-1B worker files an I-485 adjustment-of-status application while living and working in the United States. Under the previous standard, this was routine for dual-intent visa holders. The application was typically approved if the applicant had a valid priority date, a clean record, and an employer willing to sponsor.

**Stage two:** Under the new memo, the USCIS officer evaluates whether the applicant meets the threshold for "extraordinary circumstances." The memo instructs adjudicators to weigh positive factors (U.S. citizen children, homeownership, community ties, stable employment) against negative ones (status violations, gaps in employment, past overstays). If the balance tips negative, the application is denied.

**Stage three:** Here is where it becomes dangerous. If the applicant's underlying nonimmigrant status — their H-1B, for instance — has expired or been revoked (as happens automatically when an employer terminates the position), the denial of the I-485 strips away any remaining lawful presence. The applicant immediately begins accruing unlawful presence.

Under Section 212(a)(9)(B) of the Immigration and Nationality Act, an individual who accrues more than 180 days of unlawful presence and then departs the U.S. triggers a three-year inadmissibility bar. More than a year of unlawful presence triggers a ten-year bar. The applicant cannot return — not on a tourist visa, not on a new H-1B, not through consular processing — until the bar expires.

## Why This Hits Indian Workers Hardest

The Catch-22 is especially acute for Indian nationals because of the structural realities of the EB-2 and EB-3 backlogs. Indian workers routinely wait 10 to 15 years or longer for a green card. During that time, they cycle through H-1B renewals, which depend on continuous employment with a sponsoring employer.

A worker who is laid off during this period — and in 2026, more than 110,000 tech workers have lost their jobs — may lose their H-1B status before their I-485 is adjudicated. If the I-485 is then denied under the new "extraordinary circumstances" standard, they have no valid status to fall back on.

The Capitol Immigration Law Group, in a detailed advisory published last week, spelled out the risk: "If denied, the applicant loses their pending AOS status. If they do not have an underlying valid nonimmigrant status (like H-1B), they begin accruing unlawful presence and may be placed in removal proceedings."

Worse, the Supreme Court has limited judicial review of discretionary immigration decisions. The memo's own language describes adjustment of status as an act of "administrative grace" — not a right. Appeals will be extraordinarily difficult.

## The Consular Processing Paradox

The supposed alternative — consular processing through a U.S. embassy abroad — carries its own contradictions.

The State Department has imposed travel restrictions affecting dozens of countries. Consular processing at Indian embassies is notoriously backlogged, with wait times for visa appointments stretching months. If an applicant who was denied AOS in the U.S. triggers the inadmissibility bar by leaving, they cannot process their green card from abroad either — not until the bar expires.

"The overall uncertainty is likely to discourage applicants, employers, and families from pursuing adjustment of status or taking risks with immigration filings," the American Immigration Council said in its formal response to the new policy.

## What the Memo Actually Protects

Not everything in PM-602-0199 is hostile. The memo explicitly states that applying for adjustment of status is not inconsistent with maintaining nonimmigrant status in a dual-intent category. H-1B, O-1, and L-1 holders retain this protection. Officers are instructed to weigh positive equities including U.S. citizen children, established employment, and the practical reality that consular processing is backlogged.

Immigration attorney and LinkedIn commentator who authored a widely shared "Stop the PANIC" analysis noted that people are "confusing 'higher scrutiny' with 'the entire legal pathway no longer exists.' Those are not the same thing."

That distinction is legally correct. But the practical effect for an Indian worker who has been laid off, lost their H-1B status, and faces an I-485 denial is indistinguishable from the pathway ceasing to exist.

## What to Do Now

Immigration attorneys are recommending several concrete steps for Indian workers with pending green card applications:

**Maintain valid H-1B status at all costs.** If laid off, prioritize finding a new sponsor and filing an H-1B transfer within the 60-day grace period. An active H-1B provides the safety net that prevents the inadmissibility trap from triggering.

**Document positive equities proactively.** The memo instructs officers to consider community ties, property ownership, tax compliance, and family integration. Applicants should compile evidence of these factors now, before any interview or RFE.

**Consult an immigration attorney before the I-485 interview.** The new framework gives adjudicators significant discretion. Understanding how your specific case maps to the memo's factors is no longer optional.

**Do not withdraw a pending I-485 without legal advice.** Withdrawal itself can have immigration consequences, and the timing matters for unlawful presence calculations.

The green card backlog for Indian nationals was already the longest in the world. PM-602-0199 did not create that problem. But it has introduced a new risk that transforms a bureaucratic delay into a potential decade-long exile."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
