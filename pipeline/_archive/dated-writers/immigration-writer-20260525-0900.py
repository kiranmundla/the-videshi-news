#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-25 09:00 PDT"""
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
        "headline": "Congress Wants to Exempt Doctors From the $100,000 H-1B Fee — Here's What Indian Healthcare Workers Need to Know",
        "subheadline": "A bipartisan group of lawmakers is pushing DHS to waive Trump's punishing visa surcharge for medical professionals, arguing it is gutting an already-thin healthcare pipeline in rural America.",
        "slug": make_slug("bipartisan-bill-100k-h1b-fee-waiver-healthcare-doctors"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-born physicians make up the single largest group of international medical graduates practising in the United States. Thousands work on H-1B visas in hospitals, clinics, and research institutions — particularly in rural and underserved areas where American-trained doctors are scarce. The $100,000 fee threatens to choke off the pipeline that keeps these facilities staffed, and any exemption would directly benefit the Indian medical diaspora.",
        "tags": ["h1b", "healthcare", "100k-fee", "immigration", "indian-doctors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Physicians Practice", "url": "https://www.physicianspractice.com/view/lawmakers-mgma-urge-dhs-to-exempt-health-care-from-100-000-h-1b-fee"},
            {"name": "MGMA", "url": "https://www.mgma.com"},
            {"name": "USCIS Guidance on $100K Fee", "url": "https://www.uscis.gov"},
            {"name": "American Immigration Council", "url": "https://www.americanimmigrationcouncil.org"},
            {"name": "White House Proclamation (Sept 19, 2025)", "url": "https://www.whitehouse.gov"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/127873/pexels-photo-127873.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """When President Trump signed a proclamation last September slapping a $100,000 surcharge on new H-1B petitions, the stated target was wage-suppressing outsourcing firms. But the blast radius, it turns out, includes the people who keep Americans alive.

A bipartisan, bicameral group of lawmakers — led by Representatives Yvette D. Clarke (D-NY) and Michael Lawler (R-NY) — has written to DHS Secretary Kristi Noem demanding that healthcare employers be exempted from the fee. The Medical Group Management Association (MGMA) backed the request, warning that the surcharge could leave "critical positions unfilled" and push some hospitals "to their financial brink."

## How the Fee Works

The $100,000 payment applies to *new* H-1B petitions where the beneficiary is outside the United States and does not already hold a valid H-1B visa. Renewals and in-country status changes are exempt. The DHS secretary can also grant waivers on national-interest grounds — but so far, no blanket healthcare exemption exists.

Employers must pay via pay.gov before filing. If the payment or a valid exception claim is missing, USCIS will deny the petition outright. No second chances, no request for evidence — just a rejection.

## Why Healthcare is Different

The lawmakers' argument is straightforward: American hospitals cannot function without international medical graduates. According to the Association of American Medical Colleges, roughly 25 percent of all practising physicians in the US completed their medical training abroad. For certain specialities — internal medicine, psychiatry, pathology — the share is even higher.

Indian-born doctors are the largest single national group within that cohort. They are disproportionately concentrated in exactly the places American medical graduates tend to avoid: rural clinics, community health centres, Veterans Affairs hospitals, and underserved urban systems where patient loads are heavy and pay is modest.

A $100,000 surcharge on top of standard filing fees, legal costs, and premium processing charges makes the economics of sponsoring an international doctor almost prohibitive for a 12-bed rural hospital in West Virginia or a Federally Qualified Health Centre in Mississippi. These are not organisations with deep pockets.

## The Diaspora Pipeline Under Threat

For Indian medical graduates, the path to practising in the United States is already gruelling. The sequence — USMLE Steps 1, 2, and 3, followed by a residency match, followed by J-1 or H-1B sponsorship, followed by years in the green card backlog — can span a decade or more. The $100,000 fee adds a new barrier at the sponsorship stage, precisely when candidates are most vulnerable to being dropped in favour of a domestic hire who costs nothing extra to onboard.

MGMA warned that the fee could redirect international talent to Canada, the UK, and Australia — countries that have been actively courting Indian-trained physicians with streamlined visa pathways and shorter permanent residency timelines. India's own healthcare system, chronically short-staffed, would prefer its doctors stay home. The competition for Indian medical talent, in other words, is global, and America just made itself less competitive.

## What Happens Next

The lawmakers' letter asks DHS to issue a formal exemption. Separately, a bipartisan House bill would codify the waiver for doctors and nurses into statute, insulating it from future executive action. Neither path is guaranteed — the administration has shown little appetite for carving out exceptions to its immigration framework.

For Indian healthcare workers already in the US on H-1B visas, the immediate impact is limited: the fee does not apply to renewals or those already holding valid H-1B status. But for the next generation — the residents finishing training this year, the specialists being recruited from Indian medical colleges — the $100,000 wall is real and rising.

The irony is hard to miss. At a moment when America's clinician shortage is projected to reach 124,000 by 2034, Washington is simultaneously begging for more doctors and pricing out the ones willing to come."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Department of Labor Wants to Raise H-1B Minimum Wages by 30% — And the Comment Window Closes Tomorrow",
        "subheadline": "A proposed rule would push entry-level H-1B salary floors to nearly $98,000, threatening the economics of mid-size employers and reshaping who can afford to sponsor foreign workers.",
        "slug": make_slug("dol-h1b-wage-hike-30-percent-comment-deadline"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold an estimated 71 percent of all approved H-1B visas. A 30 percent wage floor increase would hit Indian IT workers hardest — particularly those at mid-tier consulting firms and startups where current salaries fall below the proposed thresholds. For H-1B holders already in the system, the new floors could complicate renewals and transfers. For those still in India hoping to come over, the pool of employers willing to sponsor at these wage levels shrinks dramatically.",
        "tags": ["h1b", "wages", "dol", "immigration", "prevailing-wage"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "National Times Media", "url": "https://nationaltimesmedia.com/us-plans-major-h-1b-wage-increase-new-proposal-could-raise-hiring-costs-for-foreign-workers/"},
            {"name": "Department of Labor", "url": "https://www.dol.gov"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries/article71011264.ece"},
            {"name": "USCIS FY2027 H-1B Data", "url": "https://www.uscis.gov"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The Department of Labor has proposed what amounts to the most significant overhaul of H-1B wage requirements in nearly two decades — and the window for public comment closes on May 26.

Under the draft framework, minimum salary benchmarks across all four prevailing wage levels would rise by roughly 30 percent. Entry-level H-1B positions (Level 1) would carry a floor of nearly $98,000 annually. Higher-tier categories could exceed $175,000, depending on occupation and metropolitan area. The revision would apply not only to H-1B visas but also to H-1B1, E-3, and permanent labor certification (PERM) programmes.

## Why Now

The administration's stated rationale is that the existing wage structure — last meaningfully updated under the Obama era — no longer reflects labour market realities. Officials argue that outdated salary floors have allowed some employers to sponsor foreign workers at below-market rates, undercutting domestic professionals.

This framing aligns with the broader thrust of the administration's immigration posture: the $100,000 surcharge on new H-1B petitions, the tightened adjustment-of-status rules, and USCIS's recent boast that FY2027 H-1B registrations fell 38.5 percent year-over-year. Taken together, Washington is engineering a smaller, more expensive, more elite H-1B programme — and the wage proposal is the regulatory muscle behind that vision.

## The Numbers That Matter

USCIS data released last week revealed that 71.5 percent of selected H-1B registrants for FY2027 hold a US master's degree or higher, up from 57 percent the prior year. Only 17.7 percent of selected registrations fell into the lowest wage category. The programme is already skewing toward higher-paid, more credentialed workers. The DOL's wage hike would accelerate that trend by making it mathematically impossible for many employers to sponsor at lower salary bands.

For Indian workers specifically, the stakes are enormous. Indians account for an estimated 71 percent of all approved H-1B applications. The median H-1B salary across all employers currently sits at roughly $123,500 according to OpenH1B data — above the proposed Level 1 floor but uncomfortably close to it for workers in lower-cost metros or earlier in their careers.

## Winners and Losers

**Winners**: Senior engineers, data scientists, and specialists at major tech companies already paying well above prevailing wage. Their employers can absorb the new floors without blinking. Indian workers with US advanced degrees, strong experience profiles, and positions at firms like Google, Microsoft, or Amazon are insulated.

**Losers**: Mid-tier IT consulting firms, healthcare staffing agencies, small startups, and university research labs. These employers often sponsor H-1B workers at Level 1 or Level 2 wages — not because they are exploiting workers, but because their revenue models, grant funding, or patient-care economics cannot support $98,000 entry-level salaries. A postdoctoral researcher at a state university or a staff physician at a rural clinic may suddenly become too expensive to sponsor.

Indian IT services companies — already reeling from the $100,000 petition fee and stricter lottery rules — would face yet another cost increase. For firms built on the model of deploying teams of H-1B consultants to client sites, the new wage floors could force a fundamental restructuring or a retreat from the US market entirely.

## The Timing Problem

The public comment period closes tomorrow, May 26. After that, the DOL will review submissions and could finalise the rule within months. Once effective, the new wage levels would apply to all new Labor Condition Applications — the foundational filing for any H-1B petition.

For H-1B holders currently employed, the immediate impact depends on when their next petition or extension is filed. Existing approved petitions are not retroactively affected. But anyone filing a transfer, extension, or amendment after the rule takes effect would need to meet the new salary thresholds or risk denial.

## What Indian Workers Should Do

First, check your current wage level against the proposed thresholds for your occupation and metro area. The DOL's proposed rule uses the Bureau of Labor Statistics' Occupational Employment and Wage Statistics (OEWS) survey as the baseline — your HR department or immigration attorney should be able to map your position.

Second, if your salary falls below the proposed Level 1 floor, start the conversation with your employer now. A proactive salary adjustment is far better than a petition denial six months from now.

Third, if you have opinions on the proposal, submit a public comment before the deadline. The DOL is required to consider substantive comments, and industry groups have been effective in pushing back on wage rules in the past — similar proposals during Trump's first term were ultimately withdrawn after legal challenges.

The trajectory is clear. The H-1B programme of 2020 — high-volume, broad-access, moderate-cost — is being replaced by something narrower and steeper. Whether that serves American workers, Indian professionals, or anyone at all is the question the DOL is supposed to be answering. The comment window for that answer closes in less than 24 hours."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Published: {art['headline']}")
        print(f"   Slug: {art['slug']}")
    except Exception as e:
        print(f"❌ Failed: {art['slug']}: {e}")
