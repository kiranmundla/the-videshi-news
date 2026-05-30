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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "122 Days to Lock In Your Green Card at $800,000 — The EB-5 Deadline Nobody's Talking About",
        "subheadline": "The September 30 grandfathering cutoff is the most important date on the Indian investor immigration calendar. After that, the price goes up, the protection goes away, and the backlog gets worse.",
        "slug": make_slug("eb5-september-deadline-indian-investors-grandfathering"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals stuck in 15+ year EB-2/EB-3 green card backlogs have increasingly turned to EB-5 as an alternative pathway. The September 30, 2026 grandfathering deadline is critical — filing before it locks in current program rules even if Congress changes or fails to renew the Regional Center Program. With the AOS memo restricting adjustment of status, EB-5's concurrent filing benefit (available in reserved categories) is one of the last ways to get a work permit and travel authorization while waiting for a green card.",
        "tags": ["eb-5", "green-card", "indian-investors", "immigration", "deadline"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/indian-eb5-visa-retrogression-warning-may-2026/"},
            {"name": "Financial Express / LCR Capital", "url": "https://www.lcrcapital.com/financial-express-eb-5-investor-visa-applicants-deadline/"},
            {"name": "ManaTelugu", "url": "https://manatelugu.com/eb-5-investors-urged-to-watch-september-2026-deadline/"},
            {"name": "Golden Gate Global", "url": "https://www.3gfund.com/eb-5-visa-update-2026-2027/"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/despite-eb-5-retrogression-for-indian-nationals-eb-5-regional-center-program-provides-a-promising-pathway.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg",
        "body": """September 30, 2026. That is 122 days from now. It is the date by which anyone considering the EB-5 investor visa should have their petition filed — or accept that the rules of the game may change beneath them.

The EB-5 Reform and Integrity Act of 2022, which reauthorised the Regional Center Program and set today's investment thresholds, includes a statutory grandfathering provision. File your I-526E petition on or before September 30, 2026, and your application is protected under current law even if Congress alters, fails to extend, or lets the program lapse after 2027. File after that date, and you are exposed to whatever political winds blow through Capitol Hill next.

Immigration attorneys at firms including Davies & Associates, CSG Law, and LCR Capital have been flagging this deadline since early May. Their message is uniform: this is not theoretical risk. The EB-5 program has operated on temporary legislative extensions since 1993. Every renewal cycle brings uncertainty, and the current authorisation runs through September 2027. Grandfathering is the only insurance policy available.

## The Numbers That Matter

The minimum investment stands at $800,000 for projects in targeted employment areas — rural zones, high-unemployment areas, and infrastructure projects — and $1,050,000 for standard investments. Starting January 2027, inflation adjustments will push these figures higher. Filing before September locks in the current price.

But the real draw for Indian nationals is not the investment amount. It is the timeline.

EB-2 India priority dates have retrogressed to September 2013 in the June 2026 Visa Bulletin. EB-3 India sits at January 2014. That translates to wait times exceeding 12 to 15 years for skilled professionals who filed employment-based petitions today. The EB-5 program, by contrast, still offers reserved categories — rural, high-unemployment, and infrastructure — that remain current for Indian applicants. No backlog. No waiting.

## The Concurrent Filing Advantage

This is where EB-5 becomes more than just an investment. Under the 2022 reforms, eligible investors already in the United States can file Form I-526E (the EB-5 petition), Form I-485 (adjustment of status), Form I-765 (work permit), and Form I-131 (travel authorisation) simultaneously. That means an investor in a current reserved category can receive a work permit and advance parole within 8 to 10 months of filing — without being tied to any single employer.

For an H-1B holder who has spent a decade waiting for a green card, chained to one employer by the terms of their visa sponsorship, that kind of flexibility is transformative.

There is a wrinkle, however. The USCIS Policy Memorandum PM-602-0199, issued on May 22, declared adjustment of status an "extraordinary act of administrative grace." Immigration attorneys are still parsing whether this memo will affect EB-5 concurrent filers differently from employment-based applicants. The early consensus is that EB-5 investors in current reserved categories should still qualify, but the guidance introduces discretionary review that did not exist before.

## The Unreserved Category Is Already Backlogged

Not every EB-5 lane is open. The Unreserved category for Indian nationals has a priority date of May 1, 2022, and immigration attorneys predict further retrogression as early as the next Visa Bulletin. If the Unreserved category retrogresses significantly, Indian investors in that lane lose the concurrent filing advantage entirely — they would need to wait years before filing I-485.

The strategic calculus is clear: invest through a reserved category (rural, high-unemployment, or infrastructure) before September 30. That combination — reserved category plus pre-deadline filing — provides the maximum protection and the fastest path to a green card.

## What $800,000 Actually Buys

The investment must create at least 10 full-time jobs for US workers. Most investors go through USCIS-approved Regional Centers, where funds are pooled into large-scale projects — real estate developments, healthcare facilities, infrastructure builds. The investor does not manage the project. Returns are typically modest; the green card is the product.

For an Indian family earning $200,000 to $400,000 in combined household income — common among mid-career H-1B professionals in tech hubs like the Bay Area, Seattle, and the Northeast corridor — $800,000 represents a significant but not impossible commitment. Some immigration attorneys report clients liquidating portions of India-based real estate holdings or drawing on family resources to meet the threshold.

## The Quiet Surge

EB-5 filings from Indian nationals have surged over the past 18 months. The combination of EB-2 retrogression, the $100,000 H-1B fee, the weighted lottery proposal, H-4 EAD uncertainty, and now the AOS memo has pushed professionals who once considered EB-5 a "rich person's visa" to reconsider. When every other pathway narrows simultaneously, spending $800,000 to skip a 15-year queue starts to look less like extravagance and more like arithmetic.

September 30 is not a soft suggestion. It is a hard statutory cutoff with real consequences. The 122-day clock is running."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Signed a Social Security Deal with Britain. It Still Doesn't Have One with America.",
        "subheadline": "Indian professionals in the US pay billions into Social Security and Medicare every year. Most will never see a dollar back. A new agreement with the UK shows what a deal could look like — and why Washington has never offered one.",
        "slug": make_slug("india-uk-social-security-us-totalization-gap-diaspora"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B workers in the US pay 6.2% of their salary into Social Security and 1.45% into Medicare — taxes their employers match — yet most will return to India before accumulating the 40 quarters (10 years) needed to claim benefits. Without a US-India totalization agreement, these contributions are effectively a tax with no return. The new India-UK deal, which eliminates dual contributions for temporary workers, throws this gap into sharp relief. For a mid-career Indian engineer earning $150,000, the annual combined FICA contribution (employee + employer) exceeds $22,000 — money that subsidises American retirees while building no safety net for the worker or their family.",
        "tags": ["social-security", "totalization", "india-uk", "h1b", "fica-taxes", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Ministry of External Affairs, India", "url": "https://www.mea.gov.in/press-releases.htm?dtl/38865/Signing+of+Agreement+on+Social+Security"},
            {"name": "KPMG GMS Flash Alert 2026-039", "url": "https://assets.kpmg.com/content/dam/kpmg/us/pdf/2026/02/tnf-india-feb18-2026.pdf"},
            {"name": "WTW Advisory", "url": "https://www.wtwco.com/en-gb/insights/2026/03/united-kingdom-social-security-agreement-with-india"},
            {"name": "IRS Totalization Agreements", "url": "https://www.irs.gov/government-entities/federal-state-local-governments/totalization-agreements"},
            {"name": "Social Security Administration Actuarial Note 164", "url": "https://www.ssa.gov/oact/pubs/TotNote_2025-02-10.pdf"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6928879/pexels-photo-6928879.jpeg",
        "body": """On February 10, 2026, India and the United Kingdom signed a bilateral Social Security Agreement at New Delhi. Foreign Secretary Vikram Misri signed for India; British High Commissioner Lindy Cameron signed for Britain. The agreement, negotiated as part of the India-UK Comprehensive Economic and Trade Agreement signed in July 2025, eliminates dual social security contributions for employees on temporary assignments of up to 36 months.

The deal is straightforward: an Indian software engineer sent to London by TCS or Infosys will no longer pay into both India's Employees' Provident Fund and Britain's National Insurance system simultaneously. Their home country coverage continues. Their employer saves roughly £500 per employee per year in redundant contributions. The worker does not lose benefits.

India now has bilateral social security agreements with 22 countries, including Germany, France, Japan, South Korea, Australia, Canada, and the Netherlands. The list covers most major destinations for Indian professionals on temporary assignments.

The United States is not on it.

## The $22,000 Question

Every Indian national working in America on an H-1B visa pays Federal Insurance Contributions Act taxes. The employee contributes 6.2% of earnings to Social Security and 1.45% to Medicare. The employer matches both. For a software engineer earning $150,000 — a typical mid-career salary in the Bay Area or Seattle — the combined annual FICA contribution is approximately $22,950. That money funds retirement benefits, disability insurance, and Medicare for American workers and retirees.

To claim Social Security retirement benefits, a worker needs 40 quarters of coverage — essentially 10 years of qualifying employment. An H-1B visa is initially granted for three years and can be extended to six. Extensions beyond six years are possible under the American Competitiveness in the Twenty-First Century Act for workers with approved I-140 petitions or pending labour certifications, but these extensions do not change the fundamental timeline problem.

The average Indian H-1B worker who arrives at age 27 or 28 and returns to India after 8 or 9 years — whether by choice, because of a layoff, or because the green card queue proved insurmountable — leaves with 32 to 36 quarters. Four to eight quarters short. Every dollar contributed to Social Security and Medicare is gone.

## Where the Money Goes

The Social Security Administration's own actuarial notes confirm the asymmetry. The US has signed totalization agreements with 30 countries — mostly European, plus Australia, Canada, Japan, South Korea, and Chile. These agreements allow workers to combine coverage credits across both systems, so someone who works 7 years in the US and 5 in a partner country can claim proportional benefits from both.

India is not among those 30 countries. Neither is China, which faces a similar dynamic with its large H-1B population. But India's absence is more striking given the scale of the workforce: Indian nationals received 72.3% of all H-1B visas in fiscal year 2023, and approximately 283,000 Indians currently hold H-1B status. At an average salary of $120,000, the collective annual FICA contribution from Indian H-1B holders and their employers exceeds $5.2 billion.

Some of that money will eventually fund benefits for workers who obtain green cards and remain in the US long enough to vest. But for the substantial share who return — pushed out by backlogs, layoffs, or policy hostility — the contributions are a one-way transfer.

## Why No Deal Exists

The absence of a US-India totalization agreement is not for lack of trying. Indian industry bodies, including NASSCOM and the Confederation of Indian Industry, have raised the issue in bilateral trade discussions for over a decade. The structural obstacle is cost asymmetry: the US sends relatively few workers to India on temporary assignments, while India sends hundreds of thousands to the US. A totalization agreement would reduce FICA revenue flowing into the Social Security Trust Fund at a time when the fund's trustees project depletion of reserves by the mid-2030s.

There is also a procedural barrier. Under Section 233 of the Social Security Act, the President must submit any proposed totalization agreement to Congress, along with an actuarial analysis of the financial impact. Either chamber can block it with a resolution of disapproval within 60 session days. Given the current political environment around immigration — a $100,000 H-1B fee, a 38% collapse in H-1B registrations, and an adjustment-of-status memo that tells green card applicants to leave the country — the appetite for an agreement that could be characterised as "sending American Social Security money to India" is approximately zero.

## What the UK Deal Reveals

The India-UK agreement is limited in scope. It covers only social security contributions, not benefit aggregation or pension portability. An Indian worker in London for two years will continue paying into India's EPF rather than Britain's National Insurance. When they return, their Indian coverage is uninterrupted. That is all.

But even this modest arrangement highlights what Indian professionals in America do not have: the basic assurance that their compulsory payroll contributions are building something for them. In the UK, an Indian worker on a 36-month assignment keeps their Indian coverage. In the US, an Indian worker on a six-year H-1B pays into a system designed to pay out over a 40-year career, knowing they are statistically unlikely to stay long enough to collect.

The India-UK CETA is expected to take effect in the first half of 2026, with the social security provision implemented simultaneously. For the estimated 65,000 Indian nationals working in Britain on temporary visas, that means immediate relief from dual contributions and administrative clarity about which country's system applies.

For the 283,000 Indians on H-1B visas in America, the timeline for comparable relief remains what it has been for the past two decades: indefinite."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
