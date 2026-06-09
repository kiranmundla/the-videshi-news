#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-09 16:00 UTC run"""
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 1: FY 2027 Wage-Weighted H-1B Lottery
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

article1_body = """The H-1B lottery has always been a numbers game. For the first time this spring, the numbers were rigged — legally — in favour of the highest bidders.

In December 2025, the Department of Homeland Security finalised a rule replacing the traditional random H-1B cap lottery with a wage-weighted selection system. The change took effect on February 27, 2026, just in time for the FY 2027 cap season. Registration ran from March 4 to March 19. USCIS has since confirmed that the initial selection is complete, and notifications have gone out.

The mechanics are straightforward and brutal. Every H-1B registration is now tagged with a Department of Labor prevailing wage level — I through IV — based on the salary offered for the occupation and geographic area. A Level IV registration (the highest-paid tier) gets entered into the selection pool four times. Level III gets three entries. Level II, two. Level I — the entry-level tier where a plurality of Indian IT workers sit — gets exactly one.

## The math that matters

Under the old random lottery, every registration had an equal shot. If 400,000 people registered for 85,000 slots, your odds were roughly 21 per cent regardless of salary. Under the new system, a Level IV candidate's probability of selection is four times that of a Level I candidate in the same pool. The precise odds depend on the distribution of registrations across wage levels, but modelling by immigration attorneys suggests Level I selection rates could drop below 10 per cent while Level IV rates climb past 50 per cent.

This is not an accident. DHS estimated the rule would generate annual net benefits of roughly $472 million in its first year and nearly $2 billion annually by FY 2029 — primarily by shifting H-1B slots toward higher-paid positions. The estimated annual wage transfers from employers to workers: $3.4 billion by FY 2029.

## Where Indian workers fall

Three-quarters of all H-1B approvals go to Indian nationals. But India's share of the programme is not evenly distributed across wage levels. The outsourcing giants — Tata Consultancy Services, Infosys, Wipro, Cognizant — have historically filed a large volume of petitions at Level I and Level II wages. These are the positions hit hardest by the weighted system.

A software developer at an outsourcing firm in a mid-tier metro earning $75,000 — a respectable salary by most standards — might land at Level I or Level II for that occupation and geography. Under the old lottery, their odds were identical to a principal engineer at Google earning $350,000. That parity is gone.

Employers must now declare the wage level at registration, and USCIS has signalled it will deny or revoke petitions where it finds the stated wage level was inflated to game the system. The registration form requires the occupational code, work location, and corresponding wage level to match DOL data. Mismatches are audit triggers.

## The secondary squeeze

The wage-weighted lottery is not the only wage-related pressure. The Department of Labor proposed a separate rule in March 2026 that would raise all four prevailing wage floors — pushing Level I from the 17th to the 34th percentile, Level II from the 34th to the 52nd, and so on. If finalised, the minimum salary for a Level I H-1B position would jump by an estimated $14,000 per year on average. A position that currently qualifies at Level II might be reclassified to Level I under the higher thresholds, further depressing its lottery odds.

For Indian IT companies that built their American operations on volume staffing at competitive wages, the new system is an existential recalibration. The business model that sent tens of thousands of engineers to client sites across America depended on the lottery being blind to salary. It no longer is.

## What the diaspora should know

If you are an Indian professional whose employer is preparing an H-1B petition, the single most important variable is now the offered wage relative to the prevailing wage for your occupation and location. Negotiating a higher salary is no longer just about take-home pay — it directly determines your odds of staying in the country.

For those already in the queue, the FY 2027 season offers a preview of the new landscape. Immigration attorneys are advising clients to request their employer file at the highest defensible wage level. Some are recommending geographic arbitrage — the same occupation in a lower-cost metro may correspond to a higher wage level if the offered salary is unchanged.

The lottery was never fair. Now it is explicitly unfair in a new direction — one that rewards the already well-compensated and penalises the entry-level workers who, data suggests, are disproportionately Indian."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Odds Just Changed — Inside the First Wage-Weighted H-1B Lottery",
    "subheadline": "The FY 2027 cap season replaced random chance with a salary-tiered system that gives high earners four times the odds. For India's army of Level I and Level II workers, the arithmetic is unforgiving.",
    "slug": make_slug("fy2027-wage-weighted-h1b-lottery-indian-workers-odds"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Three-quarters of H-1B approvals go to Indian nationals, but India's outsourcing workforce is concentrated at lower wage levels — exactly the tiers penalised by the new weighted selection system. For the average Indian IT professional, the probability of winning the lottery has dropped significantly.",
    "tags": ["h1b", "uscis", "wage-weighted-lottery", "fy2027", "immigration", "indian-it"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "DHS Final Rule — Federal Register", "url": "https://www.govinfo.gov/content/pkg/FR-2025-09-24/pdf/2025-21540.pdf"},
        {"name": "Serotte Law — FY 2027 H-1B Lottery Analysis", "url": "https://serottelaw.com/the-fy-2027-h-1b-lottery-weighted-selection-based-on-wage-level/"},
        {"name": "Fragomen — Preparing for the FY 2027 H-1B Cap", "url": "https://www.fragomen.com/insights/united-states-preparing-for-the-fy-2027-h-1b-cap.html"},
        {"name": "Visa Lawyer Blog — H-1B Wage-Weighted Selection", "url": "https://www.visalawyerblog.com/"},
        {"name": "Reuters — H-1B Fee Ruling", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/2023_H-1B_admissions_by_place_of_birth.svg/1280px-2023_H-1B_admissions_by_place_of_birth.svg.png",
    "image_caption": "H-1B admissions by country of birth, with India dominating at roughly 75 per cent",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 2: DOL Prevailing Wage Hike + Project Firewall
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

article2_body = """The Department of Labor wants to redefine what counts as a fair wage for a foreign worker — and the new numbers could knock a generation of Indian H-1B applicants out of the programme entirely.

In March 2026, the DOL published a proposed rule that would raise all four tiers of the prevailing wage system used to set minimum salaries for H-1B, H-1B1, E-3, and PERM labour certification positions. The changes are not incremental. They are structural.

## What the numbers look like

The DOL's prevailing wage framework assigns each sponsored position a level from I to IV based on the occupation, geographic area, and the worker's experience. Current thresholds are calibrated to wage distribution percentiles from the Occupational Employment and Wage Statistics survey:

- **Level I** (entry): currently 17th percentile → proposed 34th percentile
- **Level II** (qualified): currently 34th percentile → proposed 52nd percentile
- **Level III** (experienced): currently 50th percentile → proposed 70th percentile
- **Level IV** (fully competent): currently 67th percentile → proposed 88th percentile

The DOL estimates an average increase of approximately $14,000 per year per sponsored position. In high-cost metros like San Francisco, New York, and Seattle — where Indian tech workers are concentrated — the actual increase could be $20,000 to $30,000 for software engineering roles.

## The compounding problem

This proposed wage floor hike does not exist in isolation. It arrives alongside the new wage-weighted H-1B lottery system that took effect in February 2026, which gives higher-wage registrations more entries in the selection pool. The interaction between these two policies creates a compounding disadvantage for positions at the lower end of the pay scale.

Consider a junior data analyst position in Dallas. Under current prevailing wages, an employer offering $68,000 might qualify at Level II. Under the proposed rule, the same salary would fall to Level I — not only raising the employer's costs but also halving the position's odds in the weighted lottery. The employer faces a choice: pay significantly more or accept drastically lower odds of winning a visa.

For Indian IT staffing firms, which sponsor thousands of H-1B workers annually at competitive but not extravagant salaries, the combined impact is severe. A position that was viable at Level II under the old wage floors and the old random lottery could become functionally unsponsorable under the new floors and the new weighted selection.

## Project Firewall

The wage proposals are enforcement, not just policy. The DOL has simultaneously launched "Project Firewall," an initiative specifically targeting alleged employer abuse of the H-1B and PERM systems. The programme focuses on verifying that employers actually pay the wages they commit to on Labour Condition Applications and that job postings for PERM certifications reflect genuine hiring efforts rather than pro-forma advertisements.

Immigration attorneys report that DOL audits of PERM applications have increased notably in 2026. Employers who file at Level I wages for positions that arguably require Level II experience are facing more frequent challenges. The days of filing a PERM for a "Software Developer I" at the 17th percentile wage while the actual role demands three to five years of specialised experience appear to be ending.

## What this means for the green card queue

The prevailing wage change does not only affect H-1B petitions. It directly impacts PERM labour certifications — the first step in the EB-2 and EB-3 green card process. Higher prevailing wages mean higher certified salaries on PERM applications, which can create problems if the offered wage was set years earlier (PERM processing times now exceed 500 days in many cases). An employer who filed a PERM at what was then a compliant Level II wage may find the position reclassified by the time adjudication occurs.

For Indian nationals already in the EB-2 and EB-3 queues — some with priority dates stretching back a decade — a midstream wage reclassification could force a new PERM filing, resetting the clock entirely.

## The industry response

The proposed rule is in its comment period, and industry groups including the U.S. Chamber of Commerce and NASSCOM are expected to file objections. The argument is straightforward: artificially inflating wage floors beyond market rates does not protect American workers; it makes it prohibitively expensive to hire anyone, foreign or domestic, in positions where the labour market has already set a price.

But the political headwinds are strong. The Trump administration has framed every H-1B restriction as a defence of American workers, and the DOL's own estimates suggest the rule would transfer billions in additional wages from employers to workers over its implementation period. Opposing a rule that nominally raises wages is politically awkward, even when the real effect is to eliminate positions rather than enrich them.

For the Indian professional navigating this system, the message is clear: the floor is rising, the lottery is tilted, and the enforcement machinery is watching. The window for entry-level H-1B sponsorship at modest wages — the pathway that built a generation of Indian-American careers — is closing faster than any single court ruling or legislative proposal could achieve alone."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Fourteen Thousand Dollars More Per Position — The Wage Hike That Could Price India Out of H-1B",
    "subheadline": "The Department of Labor wants to raise every prevailing wage tier by double-digit percentiles. Combined with the new wage-weighted lottery, the economics of sponsoring entry-level Indian workers are collapsing.",
    "slug": make_slug("dol-prevailing-wage-hike-h1b-indian-workers-perm"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian IT outsourcing firms and startups that sponsor H-1B workers at competitive wages face a compounding squeeze: higher minimum salaries plus a lottery that penalises lower-wage positions. For Indian professionals in the PERM green card queue, a midstream wage reclassification could reset years of waiting.",
    "tags": ["h1b", "dol", "prevailing-wage", "perm", "green-card", "immigration", "indian-it"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "DOL Proposed Rule — Prevailing Wage Methodology", "url": "https://oguz.law/h1b-2027-updates/"},
        {"name": "Daily Caller — University Seeks H-1B English Teacher", "url": "https://dailycaller.com/2026/06/08/university-seeks-immigrant-teach-english-h1b/"},
        {"name": "New York Post — Dallas H-1B Housing Impact", "url": "https://nypost.com/2026/06/06/president-trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-way-down/"},
        {"name": "Visa Lawyer Blog — H-1B Wage Level Analysis", "url": "https://www.visalawyerblog.com/"},
        {"name": "DHS Final Rule — Wage-Weighted Selection", "url": "https://www.govinfo.gov/content/pkg/FR-2025-09-24/pdf/2025-21540.pdf"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Approved_employment_based_immigrant_petitions_awaiting_visa_availability_%28INDIA%29.png/1280px-Approved_employment_based_immigrant_petitions_awaiting_visa_availability_%28INDIA%29.png",
    "image_caption": "Approved employment-based immigrant petitions awaiting visa availability for India",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
