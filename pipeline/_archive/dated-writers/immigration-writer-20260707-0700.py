#!/usr/bin/env python3
"""
Immigration writer — July 7, 2026 (07:00 PDT run)
3 articles: IT outsourcers H-1B crash, Indian doctors healthcare angle, FY2027 wage-weighted lottery
"""
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
    # ── ARTICLE 1: IT Outsourcers H-1B Crash ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Eleven Thousand Visas for Six Companies. Indian IT Outsourcers Just Lost 40 Per Cent of Their H-1B Approvals",
        "subheadline": "TCS shed more than 3,200 approvals in a single year. Infosys was the only firm in the group that gained. The shift is structural, not cyclical — and it is reshaping how Indian engineers reach American offices.",
        "slug": make_slug("indian-it-outsourcers-h1b-approvals-crash-40-percent-tcs-infosys"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Hundreds of thousands of Indian tech professionals rely on outsourcer-sponsored H-1Bs to work onsite in the US. This collapse in approvals shrinks the pipeline that has defined Indian professional migration for two decades.",
        "tags": ["h1b", "tcs", "infosys", "wipro", "it-outsourcing", "immigration", "visa-approvals"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/top-it-firms-h-1b-visas-slump-40-tcs-worst-hit-while-infosys-gains-11748498937905.html"},
            {"name": "People Matters", "url": "https://www.peoplematters.in/article/immigration-and-work-permits/tcs-wipro-tech-mahindra-hit-hard-as-h-1b-approvals-fall-sharply-in-fy26-44890"},
            {"name": "Nearshore Americas", "url": "https://nearshoreamericas.com/indian-it-firms-see-70-drop-in-new-h-1b-visas/"},
            {"name": "USCIS", "url": "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Software developers working together in a modern tech office",
        "image_attribution": "Pexels",
        "body": """The numbers arrived without ceremony — buried in US Citizenship and Immigration Services data, surfaced by analysts at Moneycontrol, and confirmed by the firms themselves in quarterly calls. India's six largest IT services companies received 11,041 H-1B visa approvals in the fiscal year ending March 2026. A year earlier, the same group held 18,469. That is a 40 per cent decline, the steepest single-year drop in at least a decade.

The companies are Tata Consultancy Services, Infosys, Cognizant, HCL Technologies, Wipro, and Tech Mahindra — firms that collectively employ nearly two million people and generate the majority of India's $250 billion technology export revenue.

## TCS Worst Hit, Infosys the Outlier

TCS absorbed the heaviest blow. Its approvals fell by 3,242 to roughly 2,885 — a decline that would have been unthinkable five years ago, when the Mumbai-based firm routinely secured more than 5,000 annual visas. Wipro, HCL, and Tech Mahindra each reported significant drops as well.

Infosys was the lone exception. The Bengaluru-based company secured 3,195 approvals, the highest among the six, and the only firm to show a year-over-year increase. Analysts attribute this partly to Infosys's shift toward higher-value digital transformation work, which commands salaries more aligned with the new regulatory environment.

## Three Forces Behind the Crash

The decline is not the product of a single policy. Three forces converged:

**The $100,000 fee.** President Trump's September 2025 proclamation imposed a $100,000 payment on new H-1B petitions. Although a federal judge struck down the fee in June, calling it an unlawful tax, the fee was in effect for most of the FY2026 petition cycle. For outsourcers filing hundreds of petitions annually, the aggregate cost was prohibitive. TCS chief executive K. Krithivasan acknowledged the firm had deployed "fewer people than the number of approvals each year."

**The wage-weighted selection rule.** A DHS final rule, effective February 2026, replaces the random H-1B lottery with a system that gives greater weight to higher-paid workers. This directly disadvantages the outsourcer model, which has historically relied on deploying mid-level engineers at prevailing — not premium — wages. Entry-level positions that once cleared the lottery now face structural disadvantage.

**Local hiring and AI.** All six firms have accelerated local hiring in the United States, partly in response to regulatory pressure, partly because generative AI is reshaping the traditional onsite-offshore delivery model. As Cognizant CEO Ravi Kumar put it, the company has "significantly reduced the dependency on visas, while increasing local hiring and our nearshore capacity."

## The New H-1B Sponsors Are Not Indian

While outsourcers retreated, a different cohort advanced. Amazon, Meta, Microsoft, and Google now occupy all four top spots for new H-1B approvals — a space historically dominated by Indian firms. AI laboratories are joining them. OpenAI filed 76 H-1B petitions in FY2025, up from 11 in FY2021. Anthropic backed 41 applications.

The shift is directional: American tech giants are doubling down on bringing Indian engineers onsite to scale AI products, even as the outsourcing firms that first built the India-to-America talent pipeline pull back.

## What This Means for Indian Professionals

For the Indian engineer hoping to work onsite in the United States, the path through an outsourcer is narrowing. The combined effect of higher fees, wage-weighted selection, and reduced corporate appetite for visa sponsorship means fewer seats on the plane.

The alternatives are not obvious. Direct hiring by US tech firms remains fiercely competitive. The O-1 visa, designed for individuals of "extraordinary ability," is not a mass pathway. Canada, the UK, Germany, and Australia are recruiting aggressively — but none offers the compensation or career trajectory that made American H-1Bs the gold standard.

For two decades, Indian IT outsourcers were the conveyor belt that moved hundreds of thousands of engineers from Bangalore and Hyderabad to offices in New Jersey and Texas. That conveyor belt has not stopped, but it is running at 60 per cent of its former speed — and the gap is not closing.

The firms themselves are adjusting. The question is whether the Indian professionals who built careers on the promise of an American posting can adjust with them."""
    },

    # ── ARTICLE 2: Indian Doctors in Rural America ──
    {
        "id": str(uuid.uuid4()),
        "headline": "One in Four Doctors in Rural America Trained Abroad. The Immigration Crackdown Is Coming for Them Too",
        "subheadline": "Indian-origin physicians make up a quarter of the US physician workforce. In high-poverty counties, H-1B doctors account for 2 per cent of all practising physicians — nearly double the urban rate. Hospitals are already freezing applications.",
        "slug": make_slug("indian-doctors-rural-america-h1b-fee-healthcare-crisis"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Thousands of Indian-origin physicians practise in underserved American communities on H-1B and J-1 visas. The $100K fee and processing delays threaten to cut off the pipeline that keeps rural hospitals staffed — and that many Indian medical graduates depend on for their American careers.",
        "tags": ["h1b", "indian-doctors", "healthcare", "rural-hospitals", "immigration", "aapi", "physicians"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/17/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"},
            {"name": "Medscape", "url": "https://www.medscape.com/viewarticle/rural-high-poverty-areas-rely-most-docs-h-1b-visas-2025a10001gm"},
            {"name": "Medscape", "url": "https://www.medscape.com/viewarticle/5-things-doctors-should-know-about-h-1b-visa-changes-2025a1000c8g"},
            {"name": "JAMA", "url": "https://jamanetwork.com/journals/jama/fullarticle/2829131"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7579824/pexels-photo-7579824.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "A doctor examining a patient in a clinical setting",
        "image_attribution": "Pexels",
        "body": """The immigration debate in the United States is overwhelmingly framed as a technology story — H-1B lottery numbers, Silicon Valley sponsorships, Indian IT outsourcers. But there is a quieter crisis unfolding in hospital corridors and rural clinics across the country, and Indian-origin physicians are at its centre.

International Medical Graduates — physicians trained outside the United States and Canada — make up approximately 25 per cent of the American physician workforce. They provide care to nearly one in every six patients nationwide. In rural and underserved areas, that share climbs to 40 per cent. In some small towns, IMGs constitute one in three — or even one in two — practising doctors.

A substantial proportion of these physicians are of Indian origin. And the same immigration machinery that is squeezing tech workers is now threatening the pipeline that keeps rural America's healthcare system functioning.

## The Numbers That Should Alarm You

A study published in JAMA, analysing 11,080 physicians on H-1B visas during fiscal year 2023-2024, found that H-1B doctors make up 2.0 per cent of the physician workforce in the highest-poverty counties — nearly double the 0.54 per cent in the lowest-poverty counties. Rural counties had 1.6 per cent H-1B physician density, compared with 0.95 per cent in urban areas.

"In some communities, they make up 1 in 4, 1 in 3, or even 1 in 2 doctors," said Michael Liu, a clinical fellow at Beth Israel Deaconess Medical Center and Brigham and Women's Hospital in Boston, who co-authored the study. "Creating barriers to these visas could result in considerable access issues for patients."

The concentration is not accidental. IMGs gravitate toward specialties with the most acute shortages — internal medicine, geriatrics, nephrology, endocrinology, and infectious disease — and toward the geographies that American-trained physicians tend to avoid.

## The $100,000 Fee That Froze a Pipeline

When President Trump imposed a $100,000 fee on new H-1B petitions in September 2025, the impact was immediate in healthcare. Citizens Memorial Health Care, a system serving 130,000 residents across eight rural counties in southwest Missouri, froze its application process entirely.

"Recruitment of physicians in rural areas is extremely difficult," Donna Shelby, the system's director of physician recruitment, told Medscape. The system's 86-bed hospital employs seven physicians who came through the J-1 visa waiver programme — including interventional cardiologists from Pakistan and India — and transitions them to H-1B status. At $100,000 per petition, that transition became financially impossible for a rural hospital operating on thin margins.

A federal judge struck down the fee in June, ruling that the executive branch had levied an unauthorised tax. The American Association of Physicians of Indian Origin called the ruling "a healthcare victory, not a political victory."

"This ruling restores fairness and stability to a system that thousands of international physicians depend upon," said AAPI President Dr. Amit Chakrabarty. "Many hospitals would have struggled to absorb such a financial burden. The consequences would have been immediate — fewer physicians, longer wait times, and reduced access to care."

But the reprieve may be temporary. The Trump administration has signalled it will appeal, and the fee remains in effect in at least one federal circuit.

## The J-1 Waiver Delays Nobody Is Talking About

Beyond the fee, a separate bottleneck is quietly strangling the physician pipeline. The Department of Health and Human Services processes J-1 visa waiver applications for doctors willing to practise in designated shortage areas. These waivers allow international medical graduates to skip the mandatory two-year return to their home country and transition directly to US practice.

Processing has slowed dramatically. Immigration attorneys report that hundreds of applications are stalled, and physicians face a July 30 deadline to advance their cases to USCIS. If they miss it, their employers would need to file new H-1B petitions — at the $100,000 fee, if reinstated.

"Why would HHS want to take a programme that is working — a programme that places hundreds of US-trained international physicians in highly underserved parts of the country every year — and slow-walk it into nonexistence?" said Jennifer Minear, a Virginia-based health workforce immigration lawyer. "How does that serve the public health?"

## The Diaspora Dimension

For Indian medical graduates, the American pathway has long been a defining aspiration. The route — medical school in India, USMLE examinations, US residency, J-1 waiver or H-1B sponsorship — produces thousands of practising physicians each year. More than half of internal medicine trainees in the United States are IMGs, many of them Indian.

These physicians serve where others will not. They staff ICUs in rural Missouri, run nephrology clinics in Appalachian Kentucky, and anchor emergency departments in towns where the nearest alternative hospital is an hour's drive away.

The immigration crackdown was not designed with them in mind. The $100,000 fee was aimed at tech outsourcers flooding the H-1B lottery. The social media vetting rules were designed to flag security risks. The processing delays are the predictable consequence of an overwhelmed bureaucracy.

But the blunt instruments of immigration enforcement do not distinguish between a Wipro consultant in New Jersey and a cardiologist in rural Missouri. Both hold the same visa. Both are caught in the same machinery.

For Indian Americans in healthcare, the stakes are not abstract. The pipeline that brought their own physicians to America — that staffs the clinics their families visit — is under pressure from every direction. And unlike the tech sector, healthcare does not have the luxury of moving the work offshore.

When a rural hospital cannot hire a physician, the patients do not get rerouted to a server in Bangalore. They drive an extra hour, or they stop seeking care altogether."""
    },

    # ── ARTICLE 3: FY2027 Wage-Weighted Lottery ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Lottery Is No Longer Random. What the Wage-Weighted Selection Means for Indian Workers",
        "subheadline": "DHS replaced the random draw with a system that ranks applicants by salary. The rule took effect in February and will govern the FY2027 cap season. For Indian professionals at every career stage, the calculus has changed.",
        "slug": make_slug("h1b-wage-weighted-lottery-fy2027-indian-workers-salary-selection"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals receive roughly three-quarters of all H-1B approvals. A wage-weighted system structurally favours senior roles at premium salaries — disadvantaging the entry-level and mid-career Indian professionals who have historically dominated the lottery pool.",
        "tags": ["h1b", "lottery", "wage-weighted", "fy2027", "immigration", "uscis", "dhs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/news-releases/dhs-changes-process-for-awarding-h-1b-work-visas-to-better-protect-american-workers"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/stricter-vetting-slower-processing-how-new-immigration-form-changes-are--pracin-2026-07-06/"},
            {"name": "Computerworld", "url": "https://www.computerworld.com/article/3989371/cios-get-temporary-relief-as-us-court-blocks-100000-h-1b-fee.html"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/us-lawmakers-intensify-push-against-h-1b-visas-is-2026-its-death-knell-11749800780508.html"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in New York",
        "image_attribution": "Wikimedia Commons",
        "body": """For 25 years, the H-1B visa selection process operated on a simple principle: if more petitions arrived than the 85,000 annual cap allowed, a computer picked the winners at random. Every valid registration had the same probability. A junior developer at an outsourcing firm and a senior AI researcher at Google stood on equal footing in the lottery.

That era ended on 27 February 2026.

A Department of Homeland Security final rule, published in December 2025, replaced the random lottery with a weighted selection process that gives greater probability to petitions for higher-paid workers. The rule is now in effect and will govern the FY2027 H-1B cap registration season — the first cycle where salary, not luck, determines who gets through the door.

## How the Weighted System Works

The mechanics are straightforward in principle, consequential in practice. When more registrations are received than the cap allows, USCIS will rank them using a system that assigns higher selection probability to petitions offering wages at the upper end of the prevailing wage scale for the occupation and geographic area.

A petition at Level IV wages (the top of the prevailing wage range) will have a meaningfully higher chance of selection than one at Level I (the entry-level floor). The exact weighting formula has not been published as a simple multiplier — DHS described it as a system that "increases the probability" for higher-paid roles — but the directional impact is unambiguous.

"The existing random selection process of H-1B registrations was exploited and abused by US employers who were primarily seeking to import foreign workers at lower wages than they would pay American workers," USCIS spokesperson Matthew Tragesser said when announcing the rule. "The new weighted selection will better serve Congress' intent for the H-1B programme."

## Who Wins, Who Loses

The winners are clear: senior professionals with specialised skills commanding premium compensation. Principal engineers at major tech firms, experienced physicians, seasoned data scientists — anyone whose offer letter places them at or near the top of the prevailing wage distribution.

The losers are equally clear, and disproportionately Indian.

Indian nationals receive approximately 72 per cent of all H-1B approvals. A substantial share of those approvals historically went to entry-level and mid-career professionals deployed by IT services firms at Level I and Level II wages. Under the old random system, these petitions had equal lottery odds. Under the new weighted system, they face structurally lower selection probabilities.

The impact compounds with the $100,000 fee (currently blocked but under appeal) and the 40 per cent drop in outsourcer approvals. Together, these three forces — higher fees, fewer corporate sponsors, lower lottery odds — are constricting the entry-level pipeline that has defined Indian professional migration to the United States.

## The Entry-Level Squeeze

Consider a typical scenario. A fresh Indian engineering graduate receives an offer from a mid-size US technology firm at $85,000 — a competitive salary by any measure, but one that places the position at Level I or Level II in many metropolitan areas. Under the old system, this petition had the same lottery odds as a $250,000 offer from a FAANG company. Under the new system, the higher-paid petition is more likely to be selected.

This is by design. The stated rationale is to ensure the limited H-1B cap is allocated to workers who command market-rate or premium compensation, rather than to firms using the programme to access cheaper labour. The policy makes economic sense in aggregate.

But for the individual — the 26-year-old from Hyderabad who cleared the GRE, earned a master's degree from a US university, survived two years of OPT, and is now applying for an H-1B through a legitimate employer at a legitimate salary — the change feels less like reform and more like a door closing.

## What Indian Professionals Should Know

**Salary negotiation matters more than ever.** Under the old system, the H-1B lottery was a pure gamble. Under the new system, a higher salary directly improves selection odds. Applicants should negotiate compensation aggressively, and employers should understand that underpaying an H-1B candidate now carries an immigration cost, not just a retention cost.

**The master's cap still exists.** The 20,000 additional visas reserved for US advanced degree holders operate under the same weighted system, but the smaller pool and higher average salaries of master's degree holders may partially offset the wage disadvantage for recent graduates.

**Alternative pathways are narrowing simultaneously.** The O-1 visa requires "extraordinary ability" — a high bar for most professionals. The L-1 intracompany transfer is under increased scrutiny. OPT and STEM OPT remain functional but face their own regulatory threats. There is no easy lateral move.

**The FY2027 cycle is the first real test.** Registration numbers for the FY2027 cap season will be the first data point showing whether the weighted system actually shifts the composition of the H-1B pool. USCIS reported that registrations have already fallen from prior years — a signal that some employers are self-selecting out rather than competing in a system that disadvantages their wage profiles.

## The Structural Shift

The wage-weighted lottery is not an isolated policy. It is the centrepiece of a broader realignment of the H-1B programme away from volume-based outsourcing and toward high-value, high-compensation sponsorship. Combined with the $100,000 fee, the prevailing wage overhaul at the Department of Labour, and the four Congressional bills targeting the programme, the message is consistent: the era of the H-1B as a mass employment pathway is ending.

For Indian professionals, this demands a strategic recalibration. The advice from immigration attorneys is blunt: invest in skills that command premium compensation, target employers willing to pay at Level III or Level IV wages, and develop contingency plans that do not depend on a single visa lottery.

The lottery is no longer random. For the first time, the H-1B system is explicitly telling applicants: your salary is your ticket. For Indian workers at every career stage, the stakes of that message are enormous."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
