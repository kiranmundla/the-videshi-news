#!/usr/bin/env python3
"""Immigration writer — 2026-07-13 01:00 PT run. Two articles."""

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
        "headline": "Two Hundred Investigations and Counting. Inside the Machine That Could Dismantle Indian IT in America",
        "subheadline": "Project Firewall has given the Department of Labor powers it has never used before. Indian consulting firms and Big Tech employers are the primary targets.",
        "slug": make_slug("project-firewall-dol-200-investigations-h1b-indian-it"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian IT consulting firms — Cognizant, Infosys, TCS, Wipro and hundreds of smaller staffing companies — dominate H-1B usage and third-party placements, making them the primary targets of an enforcement apparatus that has never been this aggressive.",
        "tags": ["h1b", "project-firewall", "dol", "immigration-enforcement", "indian-it", "uscis", "compliance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/labor-department-expands-h-1b-oversight-tests-enforcement-power"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/employers-see-spike-in-labor-department-immigration-enforcement"},
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/politics/trump-admin-launches-first-major-h-1b-visa-fraud-investigation"},
            {"name": "Milwaukee Journal Sentinel", "url": "https://www.jsonline.com/story/news/politics/2025/07/11/jd-vance-targets-h-1b-visas-at-milwaukee-anti-fraud-event/84805289007/"},
            {"name": "New York Post", "url": "https://nypost.com/2025/07/09/us-news/vance-labor-watchdog-launch-immigration-fraud-probe-to-protect-american-jobs/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_5.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_5.jpg",
        "image_caption": "The Frances Perkins Building, headquarters of the US Department of Labor in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """For most of the H-1B program's existence, the Department of Labor's enforcement of it was reactive. A worker filed a complaint. An investigator looked into it. If the paperwork checked out, the case closed. If it didn't, there was a fine and everyone moved on.

That era is over.

Under an initiative called Project Firewall, the DOL is now pursuing roughly 200 active investigations into employers who use the H-1B visa program — a 48 percent increase in caseload since the project launched last year. The probe targets violations across the tech, healthcare, manufacturing, and education sectors, with a particular focus on companies that place H-1B workers at third-party client sites and those where foreign workers make up at least half the workforce.

What makes Firewall different from anything the DOL has done before is not the number of investigations. It is the authority behind them.

## The Secretary Signs Off

Labor Secretary Lori Chavez-DeRemer has personally authorized at least one investigation under a provision of the H-1B Reform Act of 2004 that had never previously been invoked. Known as "secretary-certified compliance reviews," these probes do not require a complaint from a worker or a competitor. They need only "reasonable cause" or a "credible source" to initiate.

"The big difference here is there doesn't need to be a complaint," said Beth Carlson, a partner at Faegre Drinker Biddle & Reath LLP. "The investigations that will come from secretarial certified compliance reviews will be broader in scope than complaint-driven investigations."

The shift from complaint-driven to proactive enforcement is not academic. Under the old system, investigators were generally limited to examining the specific worker or job named in the complaint. A 2015 Eighth Circuit ruling in *Greater Missouri Medical Pro-Care Providers v. Perez* held that the DOL had overstepped by expanding a single-employee complaint into a company-wide investigation. Project Firewall appears designed to sidestep that precedent entirely by using the secretary-certified route, which is not constrained by the scope of any individual allegation.

## What Investigators Are Looking For

Immigration attorneys say the DOL's investigators are zeroing in on the public access file that employers must maintain for every H-1B worker. That file includes the labor condition application — a document that the DOL must approve before a company can even petition for a foreign worker.

Investigators are checking whether workers are being paid what their LCA promised and whether their actual job matches the description filed with the government. Discrepancies — even technical ones — can lead to monetary penalties or debarment from the program.

"They're not focusing on just drugs and thugs anymore," said immigration attorney Kevin Andrews. "They're looking for hyper-technical violations." The government's new AI contracts, he added, are bringing "an extra level of seriousness" to the enforcement effort.

The DOL is not working alone. USCIS has ramped up in-person site visits to workplaces over the past year through its Fraud Detection and National Security directorate. The Equal Employment Opportunity Commission, meanwhile, has begun targeting alleged national origin discrimination against American workers by companies that favor H-1B holders.

## Companies Are Scrambling

The enforcement wave has triggered something many immigration attorneys say they have never seen: companies voluntarily auditing their H-1B documentation before the government shows up.

"Many companies are seriously investing for the first time in self-audits of documentation filed with the DOL as part of the H-1B hiring process," a DOL spokesperson confirmed. The agency has also seen a "significant uptick" in the number of external complaints filed — suggesting that current and former employees are more willing to report concerns in an environment where the government is visibly cracking down.

For Indian IT consulting firms, the exposure is acute. Companies like Cognizant, Infosys, TCS, and Wipro — along with hundreds of smaller staffing firms — operate the third-party placement model that Firewall is built to scrutinize. These firms sponsor H-1B workers who then work at client sites, sometimes hundreds of miles from the employer's own office. The DOL has historically found the highest rates of wage and documentation violations in exactly this arrangement.

Cognizant has already been named in the current probe. Labor Department Inspector General Anthony D'Esposito told Fox Business that his office had received whistleblower reports about "some of the biggest companies," singling out the New Jersey-based IT firm. Cognizant has not responded to requests for comment.

## What This Means for Indian Workers

The immediate risk is not to the Indian professionals working on H-1B visas — most of whom are filing compliant paperwork and earning legitimate wages. The risk is to the employers who sponsor them.

If a company is found to have violated LCA requirements or misrepresented job descriptions, it can be fined, debarred from the H-1B program, or referred to other agencies for criminal investigation. A debarred employer means its H-1B workers must find a new sponsor or leave the country. For workers in the middle of a green card application — a process that can take a decade or more for Indian nationals — a change of employer can reset years of waiting.

Immigration attorney John Pallasch, who ran the DOL's Employment and Training Administration during Trump's first term, urged a different approach. "With any significant policy shift like this, one would hope to see the government engaging with stakeholders and identifying how they can come into compliance instead of playing a game of gotcha," he said.

For the roughly 73 percent of H-1B holders who are Indian nationals, the message is clear: your employer's compliance file now matters as much as your own immigration paperwork. If it hasn't been audited recently, it should be."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Day 1 CPT Was the Last Escape Route for H-1B Lottery Losers. The Government Is Sealing It Shut",
        "subheadline": "Thousands of Indian tech workers who missed the H-1B lottery relied on re-enrolling in a master's program to keep working legally. A proposed DHS rule would make that impossible.",
        "slug": make_slug("day-1-cpt-crackdown-h1b-lottery-indian-tech-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian graduates in AI, machine learning, and software engineering — who form the largest share of H-1B lottery applicants — have used Day 1 CPT as their primary fallback after lottery rejections. Closing this pathway while simultaneously restricting OPT and ending Duration of Status leaves tens of thousands with no legal way to keep working in the United States.",
        "tags": ["day-1-cpt", "h1b-lottery", "f1-visa", "opt", "student-visa", "indian-students", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/07/11/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/h-1bs-opt-and-h-4-visas-whats-changing-for-indians-under-trumps-immigration-plan"},
            {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/national/us-h-1b-visa-rules-may-tighten-green-card-exemptions-limited-135096117.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport with visa stamps — the document at the center of sweeping US immigration changes",
        "image_attribution": "Pexels",
        "body": """Here is how the system has worked for years: You graduate from an American university with a master's degree. You enter the H-1B lottery. You lose. You enter again. You lose again. After your OPT or STEM OPT expires, you enroll in another master's program at a university that offers Curricular Practical Training from day one — known as "Day 1 CPT" — and you keep working legally while you try the lottery a third, fourth, or fifth time.

It is not elegant. It is not cheap. But for tens of thousands of Indian tech workers stuck in the H-1B lottery's statistical purgatory, Day 1 CPT has been the last legal mechanism to stay in the country and continue working in jobs that American employers desperately need filled.

The Department of Homeland Security is about to take it away.

## What the Proposed Rule Would Do

On May 5, 2026, DHS proposed eliminating "Duration of Status" for F-1 student visa holders and replacing it with a fixed admission period of up to four years. That change, which the existing Videshi coverage has documented, is sweeping on its own. But buried in the same regulatory agenda is a provision that strikes directly at Day 1 CPT: students who already hold a master's degree would face severe restrictions on enrolling in a second one purely for work authorization purposes.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" said Danielle Goldman, co-founder and CEO of Build, an immigration tech company, in an analysis published this week.

The logic is blunt. DHS views Day 1 CPT as an end-run around the H-1B cap. The proposed rule would require students seeking extensions beyond their fixed stay to apply formally through USCIS — a process that is slower, more expensive, and far less predictable than the current system where universities administer most status changes.

## The Cascade Effect

Day 1 CPT was already the fallback of last resort. What makes its closure devastating is the timing. Every other pathway out of H-1B lottery failure is being restricted simultaneously:

**STEM OPT**: A separate DHS proposal, expected in February 2027, would restrict the two-year STEM OPT extension and tighten Curricular Practical Training requirements. STEM OPT currently lets graduates work for up to three years after graduation — long enough to try the H-1B lottery three times.

**Grace period**: The proposed rules would cut the post-status grace period from 60 days to 30, halving the window that workers have to find another visa option or sponsorship after their current status expires.

**H-4 EAD**: A final rule expected this month would end the automatic extension of Employment Authorization Documents for H-4 visa holders — predominantly Indian spouses of H-1B workers. Even those who file renewal applications within the 180-day window could temporarily lose work authorization if USCIS processing is delayed.

**EB-2 unavailability**: The July 2026 visa bulletin declared the EB-2 category — the primary green card pathway for Indian professionals with advanced degrees — completely unavailable until the fiscal year resets on October 1.

The result is a system where an Indian graduate who misses the H-1B lottery has, for the first time in decades, no reliable legal pathway to remain employed in the United States.

## The AI Talent Drain Nobody Is Talking About

Goldman warned that the impact extends well beyond individual workers. Indian nationals make up a substantial share of the US talent pool in artificial intelligence, machine learning, data science, and software engineering. Companies that have relied on a steady supply of Indian technical talent — retaining them through OPT, Day 1 CPT, and repeated H-1B lottery attempts — will face a hard choice.

"There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," Goldman said. "The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions."

The "creative solutions" are narrowing too. Cap-exempt H-1B positions at universities and research institutions are one option, but DHS is proposing to tighten those exemptions as well. O-1 visas for individuals with "extraordinary ability" remain available, but the evidentiary bar is high and the processing times unpredictable.

## India Has Noticed

The proposed changes have drawn diplomatic attention. India's External Affairs Minister S. Jaishankar raised concerns about the potential impact of the new regulations on Indian nationals during a May meeting with US Secretary of State Marco Rubio. Rubio acknowledged that the changes "could lead to temporary difficulties and create tensions during the transition," but maintained that the reforms are not aimed specifically at India.

That reassurance rings hollow for the 360,000 Indian students currently enrolled in American universities, a number that made India the single largest source of international students in the 2024-25 academic year. For the thousands among them who are watching the H-1B lottery odds and calculating their backup plans, the math is about to change fundamentally.

The proposed regulations could take effect as early as August, after a period of public consultation. None have been finalized. But the signal is unmistakable: the era of serial re-enrollment as an immigration strategy is ending, and no replacement is being offered."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
