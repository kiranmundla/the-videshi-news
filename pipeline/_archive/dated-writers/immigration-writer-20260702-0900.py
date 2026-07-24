#!/usr/bin/env python3
"""Immigration writer — 2 July 2026, 0900 PT batch."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────────────────
# ARTICLE 1 — Indian IT H-1B approvals collapse 40%
# ──────────────────────────────────────────────────────

art1_body = """India's six largest IT services companies received 11,041 H-1B visas in the first half of the current US fiscal year — down 40 per cent from the 18,469 they were handed a year earlier. The numbers, drawn from official USCIS data compiled through 31 March 2026, mark the sharpest single-year contraction in more than a decade and confirm what the industry has been bracing for: the combination of a $100,000 filing surcharge and a new wage-weighted lottery is reshaping who gets to work in America.

Tata Consultancy Services absorbed the deepest cut. Its H-1B count fell by roughly 3,240 to about 2,885 — a decline of more than half. Infosys, by contrast, was the only major Indian outsourcer to gain ground, collecting 3,195 approvals and overtaking TCS for the first time in the cohort.

## The double squeeze

Two policy changes landed within months of each other and are now compounding.

The presidential proclamation signed in September 2025 imposed a one-time $100,000 payment on every new H-1B petition filed after 21 September. For a mid-tier IT firm deploying 500 first-time workers a year, that is $50 million in additional cost before a single engineer writes a line of code. A federal judge struck the fee down in late June, but the White House has appealed, and the Department of Justice says it will reinstate the surcharge.

Then, in December 2025, DHS finalised a wage-weighted selection rule effective February 2026. Under the old random lottery, every registered beneficiary had roughly equal odds of selection — around 30 per cent. The new system grants four entries to candidates offered Level IV wages and only one entry to Level I. Entry-level candidates — the category that historically dominated Indian IT filings — now face an estimated 15 per cent selection rate, half of what they had before.

USCIS itself called the shift deliberate. "This data is a clear sign that the days of abusing the program with mass, low-wage registrations are over," the agency posted on X on 22 May.

## A longer arc

The decline did not begin this year. Between 2017 and 2025, the number of Indian employees on H-1B visas at TCS, Infosys, Wipro and HCL Technologies nearly halved, falling from 34,507 to 17,997 — a negative compound annual growth rate of 9 per cent, according to Crisil Intelligence. The latest 40 per cent drop accelerates a trend that started when denial rates spiked to 24 per cent in 2018.

The industry's response has been structural. TCS has expanded offshore delivery and opened nearshore centres in Canada and Mexico. Cognizant CEO Ravi Kumar told analysts last October that the company has "significantly reduced the dependency on visas, while increasing local hiring and our nearshore capacity." TCS chief K. Krithivasan noted the firm deploys "fewer people than the number of approvals each year."

Crisil estimates the $100,000 fee will trim operating margins by 10 to 20 basis points, with companies passing 30 to 70 per cent of the cost to clients. But the deeper disruption is strategic: firms are re-engineering their delivery models to work around the visa constraint entirely.

## What it means for you

If you are an Indian professional on an H-1B at a services firm, the calculus has shifted. Companies that once filed hundreds of new petitions a year are now rationing slots for senior, higher-paid roles. Entry-level and early-career workers, particularly those on Optional Practical Training, face tougher odds in the lottery and greater competition for the shrinking pool of employer-sponsored slots.

The arithmetic is sobering. Analysts at Anand Rathi note that subcontractor costs will likely rise as firms shift more work offshore and reserve onsite positions for local hires or existing visa holders. The era of the large-scale, visa-dependent staffing pyramid is ending — and the numbers now prove it.

*Sources: USCIS official data via Livemint; Crisil Intelligence; Anand Rathi Institutional Equities; HR.com; Collegedunia*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian IT's H-1B Count Just Fell 40 Per Cent. The Staffing Pyramid Is Crumbling",
    "subheadline": "TCS approvals halved, Infosys was the lone gainer, and the wage-weighted lottery is squeezing entry-level Indian workers out of the programme.",
    "slug": make_slug("indian-it-h1b-approvals-40-percent-decline-wage-weighted"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals at IT services firms face sharply lower odds of H-1B selection, especially in entry-level and early-career roles. The shift to higher-wage preferences and $100K fees means fewer sponsored slots and more competition for the dwindling onsite positions.",
    "tags": ["h1b", "indian-it", "tcs", "infosys", "wage-weighted-lottery", "uscis", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/companies/it-u-h-1b-visas-green-card-immigration-tcs-infosys-cognizant-green-cards-hiring-11779598845829.html"},
        {"name": "Crisil Intelligence", "url": "https://www.livemint.com/companies/news/after-trumps-shock-move-companies-may-pass-30-70-of-h-1b-visa-fee-hike-to-clients-says-crisil-11727259098006.html"},
        {"name": "HR.com", "url": "https://hr.com"},
        {"name": "Collegedunia", "url": "https://collegedunia.com/usa/article/h1b-fy2027-indian-opt-students-uscis-march-31"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "An open passport displaying travel visa stamps at an airport",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ──────────────────────────────────────────────────────
# ARTICLE 2 — DHS EB-5 proposed rule overhaul
# ──────────────────────────────────────────────────────

art2_body = """The Department of Homeland Security dropped a 358-page proposed rule on 1 July that would rewrite the operating manual for America's investor green card programme. The regulation, published under RIN 1615-AC94, codifies key provisions of the EB-5 Reform and Integrity Act of 2022 and targets compliance at regional centres — the pooled investment vehicles that channel most EB-5 capital into job-creating projects.

The timing is pointed. The July 2026 Visa Bulletin, released two weeks earlier, marked EB-5 unreserved visas for India as "Unavailable" — meaning no new investor green cards can be issued to Indian nationals in that category until the fiscal year resets on 1 October. The proposed rule does not fix that bottleneck. It makes the programme harder and more expensive to use.

## What the rule changes

The proposed regulation runs to 358 pages and addresses several areas:

**Investment thresholds.** The rule would raise minimum investment amounts for certain projects. Current minimums sit at $1.05 million for standard investments and $800,000 for targeted employment areas (TEAs), which include rural zones and areas with unemployment at 150 per cent of the national average. The exact new figures are buried in the regulation's economic analysis, but DHS has signalled that the adjustments are designed to reflect "existing and future economic realities."

**Regional centre compliance.** This is the rule's centre of gravity. Regional centres — the entities that allow multiple investors to pool their capital into large enterprises — will face stricter oversight. The EB-5 Reform Act of 2022 reauthorised the regional centre programme through September 2027 but imposed new integrity requirements that DHS has been slow to codify. The proposed rule finally does so, setting adjudication timelines: 180 days for a regional centre application, 90 days for a TEA investment, and 240 days for an investor petition or conditions-removal request.

**Fee structure.** DHS proposes fees calibrated to recover the full cost of processing, in line with the Reform Act's mandate. The agency has framed these as necessary to hit the statutory target of completing adjudications within the timelines above.

## Why Indians should care

India has quietly become one of the EB-5 programme's fastest-growing source countries, and for a specific reason: the green card backlog. An Indian national in the EB-2 employment category faces a wait measured in decades — the July visa bulletin shows the category as completely unavailable. EB-1A and NIW self-petition routes have seen approval rates fall as volume surges. The EB-5, requiring capital rather than employer sponsorship, has been an escape hatch for professionals with savings or family resources.

That hatch is now narrower on both ends. The visa bulletin has shut the front door for the rest of the fiscal year. The proposed rule, if finalised, will raise the cost and compliance burden of walking through it.

For prospective investors already mid-process, the practical concern is timing. The rule is a proposal, not a final regulation — a public comment period will follow. But Indian applicants who were planning to file in FY 2027, which begins in October, now face uncertainty about whether the current investment thresholds will hold.

## The regional centre question

Regional centres have been the dominant pathway for Indian EB-5 investors, in part because they allow passive investment. An investor does not need to manage a business directly — they invest in a centre-administered project that demonstrates job creation through an economic model. The centres, in turn, market to Indian professionals in the US on H-1B or L-1 visas who can self-fund or draw on family resources.

The proposed rule tightens oversight of exactly this channel. Stricter compliance requirements for centres could reduce the number of active programmes, concentrate capital into fewer, larger operators, and push processing costs higher for individual investors.

Bloomberg Law reports that DHS released the proposal as investors and regional centre operators push back against what they see as regulatory drift since the 2022 Reform Act. The agency, for its part, frames the rule as overdue housekeeping — codifying statutory provisions that have been enforced informally or not at all.

## What happens next

The proposed rule enters a public comment period, after which DHS will publish a final regulation. Given the 358-page scope, finalisation could take six to twelve months. The regional centre programme's authorisation expires on 30 September 2027, adding a hard deadline to the rulemaking calendar.

For Indian investors watching both the visa bulletin and the regulatory pipeline, the message is consistent: the EB-5 remains theoretically available, but every quarter brings new cost, new complexity, and no movement on the backlog that drove demand in the first place.

*Sources: Bloomberg Law; Federal Register (RIN 1615-AC94); Capitol Immigration Law Group; VisaVerge; USCIS EB-5 Q&A*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "DHS Wants to Rewrite the EB-5 Rulebook. Indian Investors Are Running Out of Options",
    "subheadline": "A 358-page proposed rule released on 1 July would raise investment minimums and tighten compliance for regional centres — just as EB-5 visas for India ran dry.",
    "slug": make_slug("dhs-eb5-proposed-rule-compliance-indian-investors"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals stuck in the EB-2/EB-3 green card backlog have increasingly turned to EB-5 investor visas as an alternative. The proposed rule raises costs and adds compliance hurdles to the programme at the exact moment when EB-5 unreserved visas for India have been exhausted.",
    "tags": ["eb5", "investor-visa", "green-card", "dhs", "regional-center", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/dhs-proposed-rule-tackles-compliance-for-investor-visa-program"},
        {"name": "Federal Register", "url": "https://public-inspection.federalregister.gov"},
        {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/news/2026/06/18/july-2026-visa-bulletin-uscis-continues-to-use-final-action-dates-for-eb-filings-causing-further-retrogression-for-india/"},
        {"name": "VisaVerge", "url": "https://visaverge.com/immigration-news/july-2026-visa-bulletin-eb-2-india-backlog-hits-limits/"},
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33785777/pexels-photo-33785777.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A smartphone displaying financial market data next to a US passport and dollar bills",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ──────────────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
