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
        "headline": "Kill OPT, Kill the Pipeline — The Bill That Would End 200,000 Indian Graduates' American Dream",
        "subheadline": "Rep. Paul Gosar's Fairness for High-Skilled Americans Act would terminate the entire Optional Practical Training program, severing the pathway that hundreds of thousands of Indian students depend on to transition from classroom to cubicle.",
        "slug": make_slug("gosar-opt-termination-bill-indian-graduates-pipeline"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the largest national group using OPT and STEM OPT, accounting for roughly 40% of participants. The program is the critical bridge between graduating from a U.S. university and entering the H-1B lottery. Without it, the entire F-1 to H-1B pipeline collapses for Indian graduates, many of whose families have invested six-figure sums in American education.",
        "tags": ["opt", "stem-opt", "f1-visa", "h1b", "congress", "gosar", "immigration-reform"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Rep. Paul Gosar Official Website", "url": "https://gosar.house.gov"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "Arizona Republic Letters", "url": "https://www.azcentral.com"},
            {"name": "Forbes / DHS Regulatory Agenda", "url": "https://www.forbes.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "body": """The Optional Practical Training program has never been authorized by Congress. That fact has bothered Rep. Paul Gosar of Arizona for years. Now, with his Fairness for High-Skilled Americans Act (H.R. 2315) gaining fresh traction in a Capitol already hostile to immigration, the program that serves as the connective tissue between American campuses and American offices could be ripped out entirely.

## What OPT Actually Does

OPT allows international students on F-1 visas to work in their field of study for up to 12 months after graduation. Students in STEM fields — science, technology, engineering, and mathematics — can extend that for an additional 24 months through STEM OPT, giving them up to three years of post-graduation work authorization. Roughly 250,000 students participate annually, and Indian nationals make up the largest single-country cohort.

For most Indian graduates, OPT is not a luxury. It is the only legal mechanism to work in the United States between graduation day and the H-1B lottery results the following spring. Without it, there is no transition period, no grace, no bridge — just a diploma and a departure date.

## Gosar's Case Against the Program

Gosar's argument is straightforward: OPT was created by bureaucratic fiat in 1992 and expanded by executive action under the Obama administration. Congress never voted on it. It functions, he contends, as a shadow guest-worker program that circumvents the H-1B cap Congress deliberately set.

The tax angle is the sharpest part of his pitch. Employers hiring OPT workers are exempt from paying FICA and Medicare payroll taxes — a 7.65% discount per employee that Gosar calls a "government-subsidized" incentive to hire foreign graduates over Americans. For a company employing 50 OPT workers at $80,000 each, that exemption saves roughly $306,000 annually in payroll taxes alone.

"Our government should not be incentivizing foreign employees over Americans," Gosar wrote in a December 2025 editorial for the Daily Signal, arguing that OPT "completely abandons young Americans who have spent years and tens of thousands of dollars pursuing careers in STEM."

## The Indian Student Calculus

The bill's impact would be asymmetric, and the asymmetry falls squarely on Indian graduates. Indians account for approximately 40% of all STEM OPT participants, dwarfing every other nationality. The pipeline is well-established: study at an accredited U.S. university, graduate with a STEM degree, work on OPT while applying for the H-1B lottery, and hope the numbers fall your way.

Without OPT, that pipeline evaporates. An Indian student graduating in May would have no authorization to work by June. The H-1B lottery results for the following fiscal year would not arrive until March or April — a ten-month gap with no legal way to stay employed. The practical effect: families that spent $150,000 or more on an American master's degree would watch their investment yield a diploma and a return flight.

Danielle Goldman, co-founder and CEO of immigration advisory firm Build, warned in a June 2 analysis that ending OPT would compound existing pressures. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," Goldman said, noting that foreign nationals constitute a substantial share of the U.S. AI talent pool.

## The Timing Could Not Be Worse

H.R. 2315 arrives at a moment when every other rung on the immigration ladder is being sawed off simultaneously. The H-1B lottery is now wage-weighted, disadvantaging recent graduates who earn entry-level salaries. The $100,000 H-1B petition fee targets workers being hired from abroad. DHS has proposed eliminating Duration of Status for F-1 students, replacing it with a fixed four-year admission period. USCIS has banned STEM OPT workers from third-party consulting placements. And the grace period after F-1 status ends may be cut from 60 to 30 days.

Each measure alone is survivable. Together, they form a sequence that looks less like reform and more like a deliberate dismantling of the student-to-worker pathway.

## What Happens Next

H.R. 2315 has not advanced to a floor vote, and terminating a program used by a quarter-million graduates annually would face industry opposition from the tech sector, universities, and business associations that rely on the OPT pipeline. But the bill does not need to pass to have an effect. Its existence signals legislative appetite, and that signal filters into the regulatory actions DHS is already pursuing.

For the Indian graduate contemplating an American master's program in fall 2027, the question is no longer whether the pathway will narrow. It is whether the pathway will exist at all. The answer, increasingly, depends on which bills die in committee and which ones don't — and the difference between the two has never felt more arbitrary."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The $250 Fee Nobody Noticed — How the One Big Beautiful Bill Is Bleeding Indian Visa Holders Dry",
        "subheadline": "Signed into law eleven months ago, the One Big Beautiful Bill Act added layers of new fees, ramped up PERM scrutiny, and funnelled $170 billion into enforcement. Indian H-1B workers and their employers are paying the cumulative price.",
        "slug": make_slug("obbba-visa-integrity-fee-perm-scrutiny-indian-h1b"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals file more H-1B petitions, PERM labor certifications, and I-485 applications than any other nationality. Every fee increase in the OBBBA hits this population disproportionately. The cumulative cost of the $100K H-1B proclamation fee, the new $250 Visa Integrity Fee, increased I-485 filing fees, and heightened PERM audit risk creates an immigration tax that falls heaviest on Indian workers and the mid-size companies that sponsor them.",
        "tags": ["obbba", "one-big-beautiful-bill", "visa-fees", "perm", "h1b", "i-485", "immigration-enforcement"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mondaq - Potential Immigration Impacts of the OBBBA", "url": "https://www.mondaq.com/unitedstates/work-visas/1650408/potential-immigration-impacts-of-the-one-big-beautiful-bill"},
            {"name": "Locke Immigration Law", "url": "https://blog.lockeimmigration.com/the-one-big-beautiful-bill-act-is-law-what-it-means-for-your-business-and-foreign-talent/"},
            {"name": "Experian Employer Services", "url": "https://www.experian.com"},
            {"name": "American Immigration Council", "url": "https://americanimmigrationcouncil.org"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6580465/pexels-photo-6580465.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "body": """When President Trump signed the One Big Beautiful Bill Act into law on July 4, 2025, the headlines focused on border walls and deportation funding. Eleven months later, the provisions quietly reshaping legal immigration are becoming impossible to ignore — particularly for the Indian workers who file more employment-based petitions than any other nationality.

## The Fee Stack

The OBBBA did not rewrite visa categories or change H-1B eligibility. What it did was build a fee structure that makes every step of the legal immigration process measurably more expensive.

The most overlooked addition: a $250 "Visa Integrity Fee" imposed on virtually all nonimmigrant visas obtained through U.S. consulates abroad. Every time an Indian H-1B worker gets a new visa stamp at the Chennai or Hyderabad consulate — a routine requirement after international travel — that is $250 on top of the existing visa application fee. For workers who travel to India annually to see family, the fee compounds year after year.

The I-485 adjustment of status application — the form that converts temporary status to a green card — rose from $1,225 to $1,500, a 22% increase. A new $24 fee attaches to every I-94 arrival record. Immigration court fees under the EOIR schedule jumped to $2,940 for adjustment cases, with annual inflation adjustments baked in by statute.

Layer these on top of the $100,000 H-1B petition fee imposed by presidential proclamation in September 2025, and the arithmetic becomes punishing. A mid-size IT consulting firm sponsoring ten new H-1B workers from India now faces a seven-figure immigration budget before a single employee writes a line of code.

## PERM Under the Microscope

The OBBBA's least-discussed provision may be its most consequential for Indian green card applicants. The law directs the Department of Labor to prioritize reviews of Permanent Labor Certification (PERM) applications that show discrepancies between job postings and actual duties, or that differ from prior filings.

For Indian nationals, PERM is not optional. It is the mandatory first step in the EB-2 and EB-3 green card process — a process that already takes decades due to per-country backlogs. The median PERM processing time has ballooned to over 500 days. Now, with DOL directed to flag inconsistencies, employers must ensure job descriptions are not merely accurate but forensically consistent across recruitment ads, internal job postings, and prior immigration filings.

The practical impact: immigration attorneys are advising clients to conduct internal audits of every PERM filing in the pipeline, comparing job descriptions across years of documentation. Any mismatch — a title change, a shift in required experience, even a difference in listed duties between a 2023 posting and a 2026 filing — could trigger a DOL audit that adds months to an already interminable process.

## The Enforcement Surge

The numbers behind the OBBBA's enforcement provisions are staggering. The law allocates over $170 billion through fiscal year 2029 to immigration enforcement, making ICE the largest federal law enforcement agency with $45 billion earmarked for detention facilities and expanded operations.

For employers, the downstream effect is more I-9 audits, more worksite inspections, and more Fraud Detection and National Security (FDNS) site visits. USCIS is now directed to standardize adjudication procedures and report trends in Requests for Evidence, which immigration lawyers interpret as a signal that RFE rates will climb.

Indian-heavy IT staffing and consulting firms face the highest exposure. These companies — which place H-1B workers at client sites across the country — are already under scrutiny from the USCIS FDNS unit. The OBBBA's expanded enforcement funding gives the agency more personnel and budget to conduct unannounced visits, review third-party placement arrangements, and audit employer-employee relationships.

## What the OBBBA Did Not Change

It is worth noting what the law left intact. H-1B visa caps remain unchanged. EB-1, EB-2, and EB-3 eligibility rules are the same. The employment authorization document (EAD) system, including the 540-day automatic extension for TPS and DACA holders, was preserved. Joint-employer liability provisions that appeared in earlier drafts were stripped from the final version.

The core architecture of employment-based immigration survived. But the cost of navigating that architecture — in dollars, in time, in compliance burden — has risen sharply.

## The Cumulative Weight

What makes the OBBBA significant for Indian workers is not any single provision but the cumulative effect. The $100,000 H-1B fee. The $250 Visa Integrity Fee. The 22% I-485 increase. The doubled prevailing wage floor from DOL. The heightened PERM scrutiny. The expanded I-9 audit capacity. The USCIS policy memo treating adjustment of status as "extraordinary relief" rather than routine procedure.

No single measure is a wall. But stack them together, and they form something that functions like one — not a barrier to entry, but a barrier to staying. The Indian worker who arrived on an H-1B in 2020 and filed a PERM in 2022 is now facing a 2040 green card timeline, a fee structure that did not exist when they started the process, and an adjudication environment that treats their application as an act of administrative grace rather than the culmination of a decade-long legal process.

Loren Locke, a former U.S. Foreign Service Officer who adjudicated thousands of visa applications, summarized the shift: "The One Big Beautiful Bill is not an overhaul of employment visa rules. Instead, it's an enforcement-and-fee-focused law that will make navigating the existing system more expensive and potentially slower."

For the hundreds of thousands of Indian nationals inside that system, "potentially slower" barely covers it."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
