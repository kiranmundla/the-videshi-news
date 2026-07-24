#!/usr/bin/env python3
"""Immigration writer — July 8, 2026, 0700 PT run.

Two articles:
1. DOL Inspector General launches first major H-1B/PERM fraud investigation
2. Inside Project Firewall: the AI-powered enforcement machine targeting H-1B employers
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

articles = [
    # ── ARTICLE 1 ──────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "The DOL Just Launched Its Biggest H-1B Fraud Probe. Dozens of Subpoenas Are Already Out",
        "subheadline": "The Labor Department's Inspector General announced a sweeping investigation into H-1B and PERM visa abuse, the administration's first major fraud case targeting the programs that bring hundreds of thousands of Indian workers to America.",
        "slug": make_slug("dol-inspector-general-h1b-perm-fraud-probe-subpoenas"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold roughly 70 percent of all H-1B visas and dominate PERM green card filings — any fraud crackdown on these programs disproportionately affects the Indian diaspora's path to work and residency in America.",
        "tags": ["h1b", "perm", "fraud", "dol", "project-firewall", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "FOX Business", "url": "https://www.foxbusiness.com/politics/trump-admin-launches-its-first-major-h-1b-visa-fraud-investigation"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/financial-accounting/employers-see-spike-in-labor-department-immigration-enforcement"},
            {"name": "U.S. Department of Labor", "url": "https://www.dol.gov/newsroom/releases/osec/osec20250919"},
            {"name": "Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1531366/us-department-of-labor-launches-project-firewall"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_8.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_8.jpg",
        "image_caption": "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """The Department of Labor's Inspector General has opened the Trump administration's first major fraud investigation into the H-1B and PERM visa programs, targeting alleged visa abuse, labour trafficking, and the displacement of American workers.

Inspector General Anthony D'Esposito announced the probe on FOX Business on Wednesday morning, calling it the latest escalation in the administration's anti-fraud campaign. He said investigators have already begun issuing dozens of subpoenas.

"This is another example where fraud is fueling violent crime," D'Esposito said. "Much of the visa and the human trafficking that we see when it comes to this foreign labour is tied to cartels, is tied to transnational gangs."

The announcement came hours before Vice President JD Vance was scheduled to headline a nationwide fraud initiative event in Milwaukee, underscoring the political priority the administration has placed on enforcement.

## What the investigation covers

The probe targets both the H-1B programme, which allows roughly 85,000 new foreign workers into the United States each year, and the PERM labour certification process, the mandatory first step for most employer-sponsored green cards. Together, these two programmes form the backbone of the immigration pipeline that brings Indian IT professionals, engineers, and healthcare workers to America.

The PERM angle is particularly significant. While H-1B enforcement has intensified for months, a dedicated fraud investigation into the labour certification process is new. PERM applications require employers to prove they could not find a qualified American worker — a process that immigration attorneys have long acknowledged is ripe for manipulation.

## Project Firewall: the enforcement foundation

The investigation does not exist in a vacuum. It builds on Project Firewall, the DOL's H-1B enforcement initiative launched in September 2025, which has already produced a 48 per cent increase in the agency's caseload of H-1B investigations, according to a DOL official cited by Bloomberg Law.

Under Project Firewall, the Labour Secretary has personally certified the initiation of investigations for the first time in the department's history — a previously unused authority that allows probes to be launched without an outside complaint. The initiative coordinates enforcement across multiple agencies: the DOL's Wage and Hour Division, the Department of Justice Civil Rights Division, the Equal Employment Opportunity Commission, and U.S. Citizenship and Immigration Services.

Immigration attorneys say their clients are experiencing a dramatic shift in enforcement intensity. Companies are receiving unannounced site visits from both DHS and DOL investigators, sometimes triggered every time they file a new H-1B petition. The scope of requests has broadened from individual employee records to company-wide immigration and payroll documentation.

"They're not focusing on just drugs and thugs anymore," immigration attorney Kevin Andrews told Bloomberg Law. "They're looking for hyper-technical violations."

## AI-powered enforcement changes the game

The government is also deploying artificial intelligence to cross-reference filings across agencies. DHS has contracted with Palantir Technologies to boost its enforcement capabilities, and USCIS has altered its Form I-129 this year to collect granular data about job requirements — education levels, years of experience, technical skills, and supervisory responsibilities.

That data directly aligns with the criteria the DOL uses to calculate prevailing wages. With AI-powered interagency coordination, any discrepancy between what an employer told USCIS on a visa petition and what the DOL has on file for wage calculations is now flagged automatically.

Immigration attorney Brian Coughlin of Fisher Phillips described the development as "potentially catastrophic" for companies. "Employers and lawyers need to understand that what used to be a lot of disparate filings made for an individual over the course of years is now all going to be one cohesive narrative that needs to work together," he said.

## Why Indian workers should pay attention

Indian nationals account for approximately 72 per cent of all H-1B approvals and dominate the PERM green card queue. The enforcement crackdown, while aimed at employers, has direct consequences for workers whose visa status depends on their employer's compliance.

The data tells a story of an industry already adapting. Between 2017 and 2025, the number of Indian employees on H-1B visas at the four largest Indian IT firms — TCS, Infosys, Wipro, and HCL Technologies — nearly halved, from 34,507 to 17,997, according to USCIS data cited by Crisil Intelligence. That is a compound annual decline of nine per cent.

But thousands of Indian workers remain on H-1B visas at these and other firms. An employer found in violation of programme rules faces back wages, civil fines, and debarment from the H-1B programme — consequences that could leave sponsored workers scrambling for new employers within their 60-day grace period.

The DOL has also proposed new prevailing wage levels that would boost salary requirements for H-1B workers, adding another compliance hurdle. For Indian IT consulting firms that have historically relied on competitive labour costs, the cumulative effect of higher fees, stricter enforcement, and rising wage floors is reshaping the economics of doing business in America.

## What happens next

The investigation is in its early stages, with subpoenas just beginning to go out. Immigration attorneys expect enforcement actions — including potential debarments — to intensify in the second half of the year.

"A lot of this is just kicking off," said Jorge Lopez, chair of the Global Mobility & Immigration Practice Group at Littler Mendelson.

For the hundreds of thousands of Indian professionals whose careers depend on the H-1B and green card pipeline, the message from Washington is unambiguous: every filing, every job description, every wage declaration is now under scrutiny."""
    },

    # ── ARTICLE 2 ──────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "An AI Is Now Reading Every H-1B Filing You Ever Made. The Government Just Connected the Dots",
        "subheadline": "Palantir-powered data analysis, cross-agency information sharing, and redesigned immigration forms have turned the H-1B compliance landscape into a unified surveillance system — and immigration lawyers say most employers are not ready.",
        "slug": make_slug("ai-h1b-enforcement-palantir-project-firewall-compliance"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals on H-1B visas are most exposed to the new AI-powered enforcement system, which can flag discrepancies in filings spanning years of employment — making their continued work authorisation dependent on their employer's historical compliance record.",
        "tags": ["h1b", "palantir", "ai", "enforcement", "uscis", "project-firewall", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/financial-accounting/employers-see-spike-in-labor-department-immigration-enforcement"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/united-states-dol-intensifies-enforcement-of-h-1b-wage-rules.html"},
            {"name": "Jeelani Law Firm", "url": "https://jeelani-law.com/inside-project-firewall-how-employers-can-prepare-for-h-1b-compliance-site-visits/"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/stricter-vetting-slower-processing-how-new-immigration-form-changes-are-2026-07-06/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5473956/pexels-photo-5473956.jpeg",
        "image_caption": "Digital silhouette with binary code overlay representing AI-powered data surveillance",
        "image_attribution": "Pexels",
        "body": """For years, the federal government's immigration enforcement operated in silos. The Department of Labor checked wages. USCIS reviewed petitions. The State Department processed visa stamps. Each agency had its own records, its own systems, its own blind spots. An employer could file slightly different job descriptions with different agencies and nobody would notice.

That era is over.

Through a combination of Palantir's AI-powered analytics, redesigned immigration forms, and unprecedented interagency data sharing, the federal government has built what immigration attorneys are calling the most comprehensive H-1B enforcement infrastructure in the programme's history. And most employers, lawyers say, have not yet grasped what that means.

## How the system works

The architecture rests on three pillars.

First, USCIS redesigned Form I-129 — the petition that every H-1B employer files — to collect far more granular data than before. The updated form now asks about specific job requirements: education levels, years of experience, technical skills, supervisory responsibilities, and reporting structures. These questions did not exist on the form a year ago.

Second, that data now maps directly onto the criteria the DOL uses to calculate prevailing wages. The DOL classifies H-1B positions into four wage levels based on complexity and experience requirements. If an employer tells USCIS on the I-129 that a role requires ten years of experience and a master's degree, but the Labour Condition Application filed with the DOL classifies the same position at a Level 1 (entry-level) wage, the discrepancy is no longer buried in two separate filing systems. It is flagged.

Third, DHS has contracted with Palantir Technologies — the data analytics firm already embedded across defence and intelligence agencies — to bring AI-powered cross-referencing to immigration enforcement. The technology can pull together every filing an employer has ever made on behalf of a worker and construct what one immigration attorney called "one cohesive narrative."

"It seems pretty obvious that they're going to start looking holistically at anything the government's ever received on behalf of a worker to find ways they can poke holes in it," said Brian Coughlin, an immigration attorney with Fisher Phillips.

## What site visits look like now

The enforcement is not just digital. Immigration attorneys report that site visits by DHS's Fraud Detection and National Security Directorate officers have become both more frequent and more detailed.

Historically, site visit officers were primarily interested in a straightforward question: is the H-1B worker physically present at the work site performing the duties listed on their petition? The visit was quick. The questions were simple.

Now, officers are asking supervisors detailed questions about what qualifications a position requires, what the worker actually does day to day, and how the role fits within the company's hierarchy. Those answers are then compared against the employer's petition filings.

"No one can be prepared for it other than to understand that they shouldn't just casually answer questions when it comes to minimum requirements or really anything else," Coughlin said. "It's better to slow it down and look at the filing that was submitted to make sure that the government's getting the correct information and a consistent message."

Nandini Nair, an immigration attorney with A.Y. Strauss who represents clients in the IT consulting sector, told Bloomberg Law that some companies are receiving site visits every time they file a new H-1B petition. What typically begins as an inquiry about one employee quickly broadens to requests for the immigration and payroll records of all employees.

"The scope has increased tremendously," she said.

## The consulting model under pressure

The enforcement shift hits Indian IT consulting firms hardest. These companies — including TCS, Infosys, Wipro, HCL, and dozens of smaller staffing firms — have traditionally placed H-1B workers at client sites, sometimes rotating them across projects with different job duties and locations.

Each change in work location requires an amended Labour Condition Application. Each material change in job duties requires a new USCIS petition. In practice, many of these amendments were filed late or not at all, particularly for workers who shifted to remote arrangements during and after the pandemic. Reuters reported that M&A due diligence routinely surfaces H-1B workers who have been working from states not covered by their original LCAs.

Under the old enforcement regime, these were technical violations that rarely drew attention. Under Project Firewall's AI-powered approach, they are now discoverable at scale.

The financial exposure compounds quickly. LCAs are geographically specific to metropolitan statistical areas, each with its own prevailing wage requirement. A worker in San Francisco classified under a New York LCA could trigger back-wage obligations calculated at the higher of the two prevailing wages, multiplied across every pay period since the mismatch began.

## The proposed wage rule adds another layer

The DOL has separately rolled out a proposed rule that would increase prevailing wage levels for H-1B workers, effectively raising the salary floor for sponsored positions. If finalised, the rule would make it more expensive to sponsor foreign workers and would also create a new compliance surface — employers would need to reassess whether their existing H-1B workers meet the updated wage thresholds.

Immigration attorneys say the combined effect of enforcement intensification and wage increases is already changing employer behaviour.

"There's a second, third, fourth look at whether they actually want to be engaging with a foreign national sponsorship," Nair said.

## What H-1B workers need to know

The enforcement campaign targets employers, not workers. But the consequences flow downhill. A worker whose employer is debarred from the H-1B programme, or whose petition is revoked after a site visit reveals discrepancies, enters the 60-day grace period — a window that is functionally impossible for many workers to navigate, particularly those also waiting in the green card backlog.

Immigration attorneys recommend that H-1B workers take several practical steps: review a copy of their approved petition to understand what job duties and qualifications are listed; ensure their actual work aligns with the petition description; and avoid casually answering investigator questions about role requirements without first consulting the petition.

The government has made its position clear. Every H-1B filing is now part of a single, searchable record. The question for employers and the workers who depend on them is whether their filings tell a consistent story — because an AI is now reading every page."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
