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

article1_body = """India's largest IT exporters just lost ground in the one immigration channel they built their American business on — and the data shows the squeeze is no longer a forecast. It is here.

According to US Citizenship and Immigration Services figures current to March 31, 2026, the six biggest Indian IT services firms — Tata Consultancy Services, Cognizant, Infosys, HCL Technologies, Wipro and Tech Mahindra — were collectively approved for 11,041 H-1B visas. That is down roughly 40% from the previous year, when the same group took home about 18,469 approvals. For an industry whose onsite delivery model was effectively built on flying Indian engineers to client sites in New Jersey, Texas and the Bay Area, the contraction is structural, not seasonal.

## TCS falls, Infosys rises

The headline number hides a split. TCS, India's largest software exporter, saw the steepest decline in the cohort — down 3,242 from a year earlier to about 2,885 approvals. Infosys went the other way. The Bengaluru firm secured 3,195 approvals, the highest among the six, and was the only company in the group to post a year-on-year increase.

That divergence is not an accident of paperwork. It reflects two different bets on how to survive an American policy environment that has turned openly hostile to the visa. TCS chief executive K. Krithivasan has said the firm deployed "even fewer people than the number of approvals each year," describing a deliberate, multi-year reduction in dependency on visa-based talent. Cognizant chief Ravi Kumar has made similar noises, pointing to expanded local hiring and nearshore capacity built up over several years.

## The economics that broke the model

The forces pushing approvals down are stacking. A wage-weighted selection process now favors higher-paid registrations, choking off the entry-level, lower-wage roles that the staffing model historically relied on. Layered on top is the $100,000 fee on certain new H-1B petitions — a charge that, even after a federal judge in Massachusetts vacated the underlying proclamation on June 8, has left employers wary of building hiring plans around a benefit that may cost six figures or may not, depending on which court rules next.

"IT services companies are lowering their reliance on H-1B visas with the incremental $100,000 visa costs coupled with a wage-weighted selection process giving a preference to higher-wage talent," said Sushovon Nayak, lead IT analyst at Anand Rathi Institutional Equities. The likely result, he added, is that subcontractor costs climb as firms push more work offshore, with most onshore tasks handled by sub-contractors rather than visa-holding employees.

USCIS, for its part, frames the falling numbers as a win. In a May 22 post on X, the agency said declining registrations were "a clear sign that the days of abusing the program with mass, low-wage registrations are over."

## Why this matters to the diaspora

For Indian professionals, the retreat of the big six reshapes the most familiar on-ramp to America. For two decades, a job at TCS or Infosys was the default path: get hired in Bengaluru or Pune, get sponsored, land at a client site in the US, and begin the long climb toward a green card. That conveyor belt is narrowing fast. Fewer company-sponsored H-1Bs means more Indians will need to arrive through universities and the OPT route, or compete directly for the higher-wage roles the new lottery rewards — a tougher proposition for fresh graduates.

It also signals where the jobs are migrating. As deployment shifts to global capability centres and delivery hubs inside India, the career that once required relocating to Texas may increasingly be available in Hyderabad. For families weighing whether the American leg of an IT career still pays off, the math is changing — and the firms that built the diaspora's professional class in the US are quietly redrawing the map back toward home."""

article2_body = """If you are an Indian professional with an immigration filing pending at USCIS, the price of skipping the line just went up. As of March 1, 2026, the agency's premium processing fees — the surcharge that buys a guaranteed 15-business-day adjudication — rose across nearly every category that matters to skilled workers and students.

The increase is modest in percentage terms but lands on the exact forms Indian nationals file most. For Form I-129, the petition covering H-1B, L-1, O-1, TN and E-3 workers, the premium fee climbed from $2,805 to $2,965. The same $2,965 now applies to Form I-140, the employment-based immigrant petition that underpins EB-1, EB-2 and EB-3 green card cases. For students, Form I-765 — used for OPT and STEM OPT work authorization — rose from $1,685 to $1,780, and Form I-539, the change-of-status application for F, J and M visas, went from $1,965 to $2,075.

## Inflation, by the rulebook

USCIS is not hiding the rationale. The Department of Homeland Security is permitted to adjust premium processing fees every two years to track inflation, and the agency says this round reflects price changes between June 2023 and June 2025. The standard filing fees are untouched; only the optional fast-track surcharge moved. Revenue from the increase, USCIS says, will fund premium processing operations, improve adjudications and chip away at backlogs.

## Why "optional" is becoming "essential"

On paper, premium processing is a choice. In practice, the slowdown in regular adjudications is turning it into a near-necessity for many Indian filers. The agency officially lists change-of-status petitions at roughly 4.5 months, but practitioners report actual waits of eight months or longer. By contrast, a premium filing must be decided within 15 business days.

For an H-1B worker whose start date hinges on an approval, or a STEM graduate whose OPT clock is ticking before a job offer evaporates, that gap between "official" and "actual" processing time is the whole ballgame. Employers increasingly build the premium fee into the budget by default, because the alternative — a candidate sitting in limbo for the better part of a year — is worse.

## The cumulative bite

Taken alone, a $160 bump on an H-1B petition is noise. The problem for Indian families is that it rarely arrives alone. A typical immigration journey now stacks fee on fee: the $215 H-1B registration charge, the petition itself, premium processing to avoid the backlog, an I-140 for the green card, and I-539 or I-765 filings for a spouse on H-4 or a child aging toward 21. Each is individually defensible as an inflation adjustment. Together, they push the cost of staying legally in the US steadily higher — at the very moment other policy moves, from the wage-weighted lottery to the on-again, off-again $100,000 fee, are already straining the diaspora's budgets and nerves.

## What to do about it

The practical takeaways are unglamorous but real. Anyone with a filing in the next several months should confirm their attorney or employer is using the current fee schedule — a Form I-907 postmarked on or after March 1 with the old amount risks rejection, which can mean losing weeks. Workers eligible to keep working on a pending extension, amendment or transfer petition generally can do so without premium processing, so the surcharge is not always worth paying. And for students, timing the OPT application well before a job start date remains the cheapest insurance of all against a system where the regular line keeps getting longer.

For a community that files more of these petitions than any other nationality, the message is consistent with everything else coming out of Washington this year: the paperwork still works, but it costs more, takes longer, and rewards those who plan early."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Giants Just Lost 40% of Their H-1Bs in a Year — and TCS Took the Worst of It",
        "subheadline": "New USCIS data shows approvals for the big six Indian outsourcers fell to 11,041, with Infosys the lone gainer as the onsite model that built the diaspora's careers quietly unwinds.",
        "slug": make_slug("indian-it-firms-h1b-approvals-40-percent-drop-tcs-infosys-fy2026"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The TCS-or-Infosys job that sponsored a generation of Indians into America is shrinking fast, pushing the next wave toward universities, OPT, and higher-wage roles — or toward jobs that now stay in India.",
        "tags": ["h1b", "tcs", "infosys", "indian-it", "uscis", "offshoring"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint — Top IT firms' H-1B visas slump 40%, TCS worst hit while Infosys gains", "url": "https://www.livemint.com/companies/it-u-h-1b-visas-green-card-immigration-tcs-infosys-cognizant-green-cards-hiring-11779598845829.html"},
            {"name": "USCIS (statement on X, May 22 2026)", "url": "https://www.uscis.gov/"},
            {"name": "Policy Circle — H-1B visa fee hike forces Indian IT to recalibrate US strategy", "url": "https://www.policycircle.org/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9870227/pexels-photo-9870227.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A person signing official documents, illustrating the H-1B petition paperwork at the heart of Indian IT's US hiring model.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Skipping the USCIS Line Just Got Pricier — and Indians File More of These Petitions Than Anyone",
        "subheadline": "Premium processing fees rose on March 1 across H-1B, green card, OPT and H-4 filings. As regular adjudications stretch past eight months, the 'optional' fast track is becoming a default cost.",
        "slug": make_slug("uscis-premium-processing-fee-increase-h1b-opt-green-card-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals file the most H-1B, I-140 and OPT petitions of any group, so a fee schedule that quietly rewards paying to skip a backlog hits diaspora families hardest — and stacks on top of every other 2026 cost increase.",
        "tags": ["uscis", "premium-processing", "h1b", "opt", "green-card", "fees"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "USCIS — To Increase Premium Processing Fees", "url": "https://www.uscis.gov/forms/all-forms/how-do-i-request-premium-processing"},
            {"name": "Ogletree Deakins — USCIS Premium Processing Fees Will Increase on March 1, 2026", "url": "https://ogletree.com/"},
            {"name": "Mint — US hikes premium processing fees for H-1B, E-1, E-2 and other categories", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/236556/pexels-photo-236556.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A grand American courthouse with the US flag, evoking the federal machinery that sets and reviews USCIS fees.",
        "image_attribution": "Pexels",
        "body": article2_body
    }
]

for art in articles:
    try:
        wc = len(art["body"].split())
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
