#!/usr/bin/env python3
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
    {
        "id": str(uuid.uuid4()),
        "headline": "Thirty-Seven Percent — The Green Card 'Plan B' That Indian Professionals Trusted Is Now Harder Than the Path They Fled",
        "subheadline": "EB-2 National Interest Waiver denials have surged from 4 percent to 37 percent in three years, surpassing EB-1A rejection rates for the first time. For hundreds of thousands of Indians stuck in the employment-based backlog, the self-petition escape hatch is closing.",
        "slug": make_slug("niw-denial-rate-surpasses-eb1a-indian-green-card-plan-b-failing"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals with decade-long EB-2 green card waits have increasingly turned to NIW self-petitions as an employer-independent shortcut. With denial rates now exceeding EB-1A, this Plan B is failing precisely when they need it most.",
        "tags": ["niw", "eb-1a", "green-card", "uscis", "immigration", "eb-2"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS I-140 RADP Summary Tables", "url": "https://www.uscis.gov"},
            {"name": "Manifest Law", "url": "https://manifestlaw.com/blog/immigration/news/eb-2-niw-denials-now-outpace-eb-1a/"},
            {"name": "TryAlma EB-2 NIW Statistics", "url": "https://www.tryalma.com/learn/eb2-niw-visa-statistics"},
            {"name": "AILA Think Immigration", "url": "https://www.aila.org"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/955392/pexels-photo-955392.jpeg",
        "image_caption": "An immigration petition being signed — a familiar ritual for thousands of Indian professionals filing self-sponsored green card applications",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For years, the EB-2 National Interest Waiver was the whispered lifeline of Indian immigration forums. Skip the employer sponsorship. Skip the labor certification. File on your own merits, prove your work benefits America, and get a green card without waiting for your company's lawyers to move at their glacial pace.

It worked beautifully — until it didn't.

New data from U.S. Citizenship and Immigration Services shows that EB-2 NIW denial rates have climbed to 37.2 percent in the first quarter of fiscal year 2025. That is not a typo. The category that carried a 4.3 percent denial rate in fiscal year 2022 now rejects more than one in three petitions. For the first time in the modern history of employment-based immigration, the NIW — once considered the easier path — is now harder to get approved than the EB-1A extraordinary ability petition, which posted a 25.1 percent denial rate in the same period.

## The Numbers Tell the Story

The trajectory is stark:

- **FY 2022**: NIW denial rate of 4.3 percent; EB-1A at 23.2 percent
- **FY 2023**: NIW rises to 20.3 percent; EB-1A at 28.6 percent
- **FY 2024 Q4**: NIW hits 29.0 percent; EB-1A at 27.7 percent — the lines cross
- **FY 2025 Q1**: NIW reaches 37.2 percent; EB-1A drops to 25.1 percent

The overall NIW approval rate crashed to 43.3 percent in fiscal year 2024, down from above 90 percent for six consecutive years between 2018 and 2023. By the third quarter of fiscal year 2025, approval rates hit an all-time low of 54 percent. The category that once functioned as a near-automatic stamp has become a coin toss.

## Why USCIS Is Cracking Down

Three forces are driving the tightening.

**Volume overwhelmed the system.** USCIS received 63,549 EB-2 NIW petitions in fiscal year 2024, up from 22,049 just two years earlier — a 190 percent surge. The share of NIW filings within the EB-2 category doubled from 26 percent to 43 percent. Immigration attorneys say the flood of applications triggered a policy recalibration, with adjudicators applying far stricter scrutiny to manage the pipeline.

**The Dhanasar framework grew teeth.** Since the *Matter of Dhanasar* decision established a three-pronged test for NIW eligibility, officers have increasingly demanded granular evidence on each prong: that the proposed endeavor has substantial merit and national importance, that the applicant is well-positioned to advance it, and that waiving the job offer requirement benefits the United States on balance. Generic claims about working in technology or healthcare no longer clear the bar.

**Pending cases are piling up.** The share of NIW cases stuck in pending status exploded from 3.4 percent in fiscal year 2023 to nearly 39 percent in fiscal year 2024. Over 80,000 cases sat unresolved as of 2025. USCIS is receiving petitions faster than it can adjudicate them, and standard processing now takes 14 to 19 months — a 77 percent increase since 2023.

## What This Means for Indian Professionals

India is the second-largest source of NIW approvals, with 713 petitions approved in the first quarter of fiscal year 2025 — 15.1 percent of the total. But India also holds the longest wait from I-140 approval to actual green card issuance, with EB-2 priority dates still mired around July 2014 in the most recent visa bulletins. That means an Indian professional who files and wins a NIW today still faces a decade or more before holding a green card.

The calculus was supposed to be straightforward: file the NIW to lock in an early priority date, get the I-140 approved relatively easily, then wait out the backlog. That logic collapses when the approval itself becomes uncertain.

The irony cuts deep. Many Indian H-1B holders turned to NIW specifically because their employer-sponsored EB-2 PERM process — with its 483-day average processing time at the Department of Labor — was too slow and too dependent on keeping the same job. NIW offered independence. Now it offers a 37 percent chance of rejection.

## The EB-1A Pivot

Some immigration attorneys are advising clients to reconsider EB-1A, which requires demonstrating "extraordinary ability" through evidence such as major awards, high citation counts, published research, or significant original contributions. The EB-1A approval rate recovered to 74.9 percent in Q1 FY 2025, stabilizing at its historical mean. India posted 813 EB-1A approvals in the same quarter — actually more than its NIW approvals.

The dual-filing strategy — submitting both EB-1A and NIW petitions simultaneously — has become standard practice among immigration lawyers working with Indian tech professionals, researchers, and founders. Each petition is evaluated independently, and overlapping evidence can be used for both.

But EB-1A is no magic bullet. The standard remains high, and most mid-career software engineers or IT consultants on H-1B visas lack the publication record, awards, or demonstrable field-wide impact that EB-1A demands. For the vast majority of India's 627,000-strong green card queue, there is no easy alternative.

## The Bigger Picture

The NIW crackdown arrives at the worst possible moment. Indian professionals are simultaneously contending with the $100,000 H-1B fee, wage-weighted lottery changes that disadvantage younger workers, the PM-602 memo tightening adjustment-of-status standards, and a legislative push by Representative Chip Roy to eliminate the H-1B-to-green-card pathway entirely.

Each of these policies individually is manageable. Together, they form a system that is methodically closing every door that Indian immigration applicants have used for the past two decades. The NIW was supposed to be the one door that couldn't be shut, because it was self-sponsored and merit-based. USCIS just proved otherwise."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Machine Is Eating the Visa — AI Has Eliminated 123,000 Tech Jobs and Counting, and H-1B Workers Are First in Line",
        "subheadline": "Tech layoffs driven by artificial intelligence automation surpassed 123,000 by early summer 2026. For Indian H-1B holders, who make up 72 percent of visa recipients in the sector, each layoff triggers a 60-day deportation clock that no algorithm can pause.",
        "slug": make_slug("ai-eliminating-h1b-tech-jobs-123000-layoffs-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders dominate the tech workforce being automated away by AI. Unlike American workers who can take time to retool, H-1B holders face a 60-day deportation clock after layoffs — making AI-driven automation an existential immigration threat.",
        "tags": ["h1b", "ai", "tech-layoffs", "immigration", "indian-workers", "automation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post / Bloomberg", "url": "https://nypost.com"},
            {"name": "Layoffs.fyi", "url": "https://layoffs.fyi"},
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "BizzBuzz News", "url": "https://bizzbuzz.news"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20988575/pexels-photo-20988575.jpeg",
        "image_caption": "Empty cubicles in a tech office — a scene increasingly common as AI automation replaces skilled workers across Silicon Valley",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The layoff notice comes on a Tuesday. The algorithm that replaced you was deployed on a Monday. And the 60-day clock to find a new H-1B sponsor — or leave the country you have called home for a decade — starts ticking before the severance letter reaches your inbox.

By early summer 2026, more than 123,000 tech workers in the United States have lost their jobs, with artificial intelligence consistently cited as the primary driver of workforce reductions, according to tracking data from Layoffs.fyi and reporting by Bloomberg and the New York Post. Over 52,000 of those cuts came in the first three months of the year alone. November 2025 was the single worst month, with more than 200 companies eliminating over 51,000 positions.

For American workers, a layoff is a setback. For the estimated 730,000 H-1B visa holders in the country, it is a potential deportation event.

## The 72 Percent Problem

Indian nationals received over 72 percent of all H-1B visas between October 2022 and September 2023, according to USCIS data. They are overwhelmingly concentrated in the technology and professional services sectors that are bearing the brunt of AI-driven restructuring. When Amazon — the single largest H-1B sponsor with over 13,000 approvals in fiscal year 2025 — announces layoffs, the casualty list skews heavily Indian.

Immigration experts estimate that H-1B holders account for somewhere between 10 and 30 percent of those who have lost their jobs in the current wave. Under federal regulations, a laid-off H-1B worker has exactly 60 calendar days to secure a new employer willing to file a transfer petition. Failing that, the options narrow to switching to a different visa category, self-sponsoring a green card petition, or leaving the United States.

Sixty days is not much time in a normal job market. In a market where the very skillset that justified your visa — writing code, managing data pipelines, building enterprise software — is being automated away by the technology your former employer chose to deploy instead of keeping you, it is nearly impossible.

## AI Does Not Just Eliminate Jobs — It Eliminates Visa Justifications

Here is the part that immigration lawyers are only beginning to reckon with. The H-1B visa exists because an employer certifies that a "specialty occupation" requires the skills of the foreign worker and that no qualified American is available. When AI automates that specialty occupation out of existence, it does not merely eliminate the job. It eliminates the legal basis for the visa category itself.

Consider the mid-level software engineer who maintains legacy enterprise applications — the exact work that companies now hand to AI coding assistants. Or the data analyst whose reporting dashboards are replaced by natural-language query tools. Or the quality assurance engineer made redundant by AI-driven testing suites. Each of these roles has been bread-and-butter H-1B territory for Indian tech professionals. Each is now in the crosshairs of corporate AI adoption.

The Department of Labor's "Project Firewall," an AI-powered enforcement initiative that has already increased H-1B employer investigations by 48 percent, adds another layer of pressure. Companies that might once have been willing to sponsor a transfer petition for a laid-off worker are now less inclined to draw regulatory scrutiny by filing new H-1B petitions.

## The Indian IT Retreat

The structural shift is not limited to American tech companies. India's six largest IT services firms — TCS, Infosys, HCL Technologies, Wipro, Tech Mahindra, and LTIMindtree — have collectively reduced their H-1B filings by 46 percent over the past five years, according to USCIS data reviewed by BizzBuzz News. These outsourcing giants, once the backbone of the H-1B ecosystem, are pivoting to local American hiring, nearshore delivery centers in Mexico and Canada, and AI-driven automation that reduces the need for on-site personnel.

The $100,000 fee imposed on new H-1B petitions has accelerated this calculation. When a company can deploy an AI agent for a fraction of the cost of sponsoring a visa worker — and avoid the regulatory exposure that comes with H-1B compliance — the economic logic is unambiguous.

One North Texas builder told Bloomberg that South Asians once represented 70 percent of his company's home sales. By early 2026, that figure had fallen below 30 percent. In Collin County, the suburban epicenter of the Dallas-area housing boom fueled by Indian H-1B workers, home prices fell nearly 9 percent year-over-year — more than double the broader metro decline. The human geography of the H-1B program is literally being remapped.

## The Green Card Trap

The cruelest irony is that the workers most vulnerable to AI layoffs are often the ones deepest into the green card process. An Indian H-1B holder who has been in the United States for eight years, whose EB-2 priority date was filed in 2018, whose spouse holds an H-4 EAD, whose children attend American schools — this person does not simply "go back to India." Their entire life is anchored to a visa status that can be severed by a single corporate restructuring decision.

The Brookings Institution estimated in May 2026 that roughly 627,000 India-born individuals and their families are stuck in the green card backlog. Many of them are in precisely the mid-career tech positions that AI is now consuming. They cannot switch to a radically different field without jeopardizing their pending immigration case, and they cannot wait out the decade-long backlog if their current employer decides that a language model can do their job for less.

## What Comes Next

The convergence of AI automation, restrictive immigration policy, and a hostile regulatory environment is creating a scenario that no prior generation of Indian H-1B holders has faced. Previous downturns — the 2001 dot-com bust, the 2008 financial crisis, even the early pandemic layoffs — were cyclical. Companies cut, then rehired. The H-1B pipeline contracted, then expanded.

This time may be different. When the job itself ceases to exist, there is no rehiring cycle. When the visa justification evaporates alongside the job, the legal pathway does not reset. And when the government simultaneously raises the cost of entry to $100,000, weights the lottery against younger workers, and proposes legislation to cap H-1B visas at two years with no green card pathway, the message is difficult to misread.

Indian tech professionals are not just losing jobs. They are watching the structural conditions that made their American careers possible dissolve in real time — replaced, with brutal efficiency, by the very technology they helped build."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
