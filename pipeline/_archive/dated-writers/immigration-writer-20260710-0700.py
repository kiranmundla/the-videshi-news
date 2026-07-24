#!/usr/bin/env python3
"""Immigration writer — 2026-07-10 07:00 PT run. Three articles."""

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


# ─────────────────────────────────────────────
# Article 1: H-4 EAD Work Permit Cliff
# ─────────────────────────────────────────────
art1_body = """The timing could not be worse. Just as the Trump administration ratchets up enforcement against H-1B fraud and tightens rules for employer-dependent firms, a quieter regulatory shift is bearing down on the people those visa holders live with — their spouses.

The Department of Homeland Security is expected to finalise a rule later this month that would formally end the automatic extension of Employment Authorisation Documents for H-4 visa holders. The policy change, first signalled in October 2025, could disrupt the working lives of roughly 100,000 people — the overwhelming majority of them Indian women married to H-1B professionals.

## The 180-day trap

Under the current framework, H-4 EAD holders may file for renewal no earlier than 180 days before their work permit expires. That window was designed to be generous. In practice, it is anything but. USCIS processing times for EAD renewals routinely stretch to eight or twelve months. In some cases, applicants have waited over a year.

Until recently, that gap was bridged by an automatic extension provision: if you filed your renewal on time, your existing work authorisation continued while USCIS adjudicated. DHS scrapped that safety net in October 2025, citing national security and enhanced vetting. The result is a structural mismatch — applicants who do everything right still face months of forced unemployment while their paperwork sits in a queue.

## A lawsuit, and its limits

Seven Indian-origin H-4 spouses filed suit in the US District Court for the Central District of California on 8 January 2026, arguing that DHS acted arbitrarily and bypassed required notice-and-comment procedures under the Administrative Procedure Act. The case, *Doe v. US Department of Homeland Security*, contends that the government's stated security rationale is pretextual — DHS already operates continuous vetting programmes that screen individuals without requiring a point-in-time work permit adjudication.

USCIS has not budged. A spokesperson connected the rollback to the administration's broader immigration crackdown, stating that automatic renewals "posed a security risk that allowed bad actors to continue to work in this country." Attorneys for the plaintiffs call that framing "embarrassingly obvious" in its true intent: making life harder for people legally present in the United States.

The court could issue a preliminary injunction, pausing the rule while litigation proceeds. Or it could let it stand. Early signals will come from the briefing schedule, but for thousands of families the uncertainty is already acute.

## What this means for dual-income Indian households

The Cato Institute estimates that 92 per cent of initial H-4 EAD applicants between 2015 and 2019 were born in India. Ninety per cent hold a bachelor's degree or higher; 41 per cent hold a graduate degree. These are not unskilled dependents waiting out a visa cycle. They are software engineers, data scientists, product managers, healthcare professionals, and — in a handful of celebrated cases — startup founders.

The Department of Labor reports that H-4 EAD holders have launched businesses ranging from luxury home remodelling to cancer immunotherapy research. Their income is rarely discretionary. In high-cost metros like the San Francisco Bay Area, Seattle, and the New York tri-state region — where H-1B employment concentrates — a second salary is not a luxury. It covers mortgages, childcare, and the private school tuition that many families choose while waiting years, sometimes decades, for a green card.

Strip that income away and the arithmetic changes fast. Bloomberg Law has documented cases of families losing health insurance, pulling children from school, and defaulting on housing costs — not because they violated any immigration rule, but because the government's own processing backlog outlasted its own grace period.

## The broader pattern

The H-4 EAD rollback does not exist in isolation. It arrives alongside a regulatory agenda that includes higher fees for H-1B extensions, a proposed crackdown on third-party placements, increased wage floors, and a DOL-led fraud investigation backed by dozens of subpoenas. Taken together, the message to Indian families in the United States is unmistakable: every link in the chain — worker, spouse, student — is now under scrutiny.

For the roughly 100,000 H-4 spouses watching their EAD expiry dates approach, the question is not whether the government has the right to vet them. It is whether a processing system that cannot keep up with its own deadlines should be allowed to punish the people caught in the gap."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "One Hundred Thousand Indian Spouses Could Lose Their Work Permits This Month. The Government Calls It a Security Measure",
    "subheadline": "DHS is finalising a rule that ends automatic work-permit extensions for H-4 visa holders. With USCIS renewals taking up to a year, the math does not work.",
    "slug": make_slug("h4-ead-work-permit-cliff-indian-spouses-uscis"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Roughly 92% of H-4 EAD holders are Indian-born, mostly women professionals whose income supports dual-earner households waiting years for green cards in high-cost US metros.",
    "tags": ["h4-ead", "uscis", "immigration", "work-permit", "indian-spouses", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/why-1-lakh-indian-h-4-visa-holders-could-face-job-disruptions-in-the-us"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-spouses-sue-over-end-to-automatic-work-permit-renewals-1"},
        {"name": "VisaVerge", "url": "https://visaverge.com/immigration-news/h-4-spouses-challenge-dhs-rule-ending-automatic-ead-extensions/"},
        {"name": "BW People", "url": "https://bwpeople.in/article/us-work-permit-rule-change-worries-indian-professionals"},
        {"name": "Cato Institute", "url": "https://www.cato.org/blog/h-4-employment-authorization"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8837769/pexels-photo-8837769.jpeg",
    "image_caption": "A professional woman works at her laptop in a modern office setting",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}

# ─────────────────────────────────────────────
# Article 2: Duration of Status Ending for Students
# ─────────────────────────────────────────────
art2_body = """For more than thirty years, international students in the United States have been admitted for "duration of status" — a legal term that, in practice, meant you could stay as long as your programme required and your university vouched for you. No fixed end date on your I-94. No mid-programme filing with USCIS. Your Designated School Official handled extensions, transfers, and changes of academic level.

That era is ending. On 5 May 2026, the Department of Homeland Security submitted a final rule to the Office of Management and Budget that would replace duration of status with a fixed admission period capped at four years for F-1 and J-1 visa holders. If finalised as proposed, the rule could take effect as early as September — just in time for the fall semester.

## What changes, and why it matters

Under the new framework, every international student will receive a hard end date on their Form I-94. Anyone whose programme runs longer than four years — doctoral candidates, medical residents, students who change majors or take authorised breaks — must file Form I-539 with USCIS, submit biometrics, pay a filing fee, and prove continued eligibility. The authority to approve extensions would shift entirely from university administrators to federal immigration officers.

The implications scale with programme length. A two-year MBA student might never feel the difference. A PhD candidate in computational biology — a programme that typically runs five to eight years — would face at least one mid-programme USCIS filing, with all the discretionary uncertainty that entails. A denial could end a research career that took years to build.

Reddy Neumann Brown, an immigration law firm that advises universities, calls it "the most consequential change to student visas in three decades." NAFSA, the Association of International Educators, warned in an April webinar that institutions should prepare for the rule to land before the fall intake.

## India's outsized exposure

India is the largest source country for international students in the United States. Around 360,000 Indian students enrolled during the 2024-25 academic year, accounting for nearly 31 per cent of all international enrolment, according to the Open Doors Report. Many are in STEM fields — engineering, computer science, data science — where programme timelines are long and post-graduation employment pathways like OPT and STEM OPT are critical career stepping stones.

The proposed rule does not merely add paperwork. It alters the risk calculus for families investing $50,000 to $80,000 per year in a US education. A fixed-period visa introduces the possibility of administrative disruption at the worst possible moment: between qualifying exams and dissertation defence, between graduation and the start of OPT employment, between one degree and the next.

Danielle Goldman, CEO of Build and a longtime observer of immigration talent pipelines, told The Indian Eye that the rule would "fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training." Students who once handled extensions through their university's international office will now navigate USCIS queues — the same agency that takes eight to twelve months to process a work permit renewal.

## The OPT question

A separate proposal expected in early 2027 would introduce further changes to the Optional Practical Training programme. OPT currently allows graduates to work in the US for up to twelve months in a job related to their field of study; STEM graduates get an additional twenty-four months. Together, the two pathways provide up to three years of post-graduation work experience — time that many Indian graduates use to find an H-1B sponsor or build a US career track.

Details of the OPT changes remain scarce, but the direction is clear. The administration has consistently signalled its view that student visas are overstayed and underpoliced. Replacing duration of status with a fixed period is the structural foundation; the OPT revision would tighten the post-graduation off-ramp.

## The competitive pressure

Canada has not been subtle about its ambitions. Ottawa's recruitment of Indian students has intensified as the US tightens its terms, and enrolment data suggests the pitch is working. For Indian families weighing a six-figure investment in foreign education, the question is no longer just which university offers the best programme. It is which country's immigration system will let you finish it.

The proposed rule applies retroactively to students already in the US on F-1 visas. For the 360,000 Indian students currently enrolled, September may bring a new set of deadlines they did not sign up for."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Duration of Status Is Dead. Three Hundred and Sixty Thousand Indian Students Will Feel It First",
    "subheadline": "DHS is replacing the decades-old system with fixed four-year visas. PhD candidates, OPT applicants, and anyone whose programme runs long will now answer to USCIS, not their university.",
    "slug": make_slug("duration-of-status-dead-fixed-period-student-visa-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "India is the largest source of international students in the US at 31% of all enrolment. The shift from university-managed extensions to USCIS-adjudicated ones adds cost, delay, and administrative risk to every Indian family's education investment.",
    "tags": ["f1-visa", "student-visa", "duration-of-status", "uscis", "indian-students", "opt"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/06/us-to-end-duration-of-status-for-f-j-and-i-visas/"},
        {"name": "Reddy Neumann Brown PC", "url": "https://rnlawgroup.com/dhs-proposes-to-replace-duration-of-status/"},
        {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/dhs-proposes-fixed-terms-for-f-j-and-i-nonimmigrant-visas"},
        {"name": "Yale OISS", "url": "https://oiss.yale.edu/news/dhs-proposes-to-replace-duration-of-status"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/35487002/pexels-photo-35487002.jpeg",
    "image_caption": "International students celebrate graduation outside a university building",
    "image_attribution": "Pexels",
    "body": art2_body.strip(),
}

# ─────────────────────────────────────────────
# Article 3: Third-Party Placement Crackdown
# ─────────────────────────────────────────────
art3_body = """The Indian IT consulting model — send an engineer to Bangalore for training, fly them to the United States on an H-1B, park them at a Fortune 500 client's office for three years — has been one of the most durable business architectures in global technology services. Tata Consultancy Services, Infosys, Wipro, and HCLTech built a combined $100 billion-plus industry on it. It survived the 2008 financial crisis, a pandemic, and two rounds of Trump-era regulatory tightening.

It may not survive the next one.

## The August proposal

The administration plans to publish a proposed rule in August that would impose new requirements on employers who place H-1B workers at third-party client sites. The measure, reported by Kably in the Times of India and confirmed in DHS regulatory agendas, targets the core mechanism of the consulting model: the separation between the company that holds the visa and the company that directs the work.

Under the proposal, employers must demonstrate a "genuine employer-employee relationship" with the H-1B worker throughout the placement. They must verify that the duties performed at the client site qualify as a specialty occupation. They must maintain detailed assignment records — not in a general sense, but with the specificity that USCIS adjudicators can audit: exact job duties, signed client contracts, work orders, and documentation proving the role requires the degree the worker holds.

Firms with past compliance violations will face heightened scrutiny. Because this is a proposed rule, it will undergo public consultation before any final decision. But the direction is unambiguous.

## Why this time is different

Third-party placement restrictions are not new. USCIS toughened its documentation requirements in 2018, demanding end-client letters, detailed itineraries, and corroborating evidence for every off-site assignment. That round stung Indian IT firms, but they adapted — hiring more US-based workers, restructuring contracts, and investing in onshore delivery centres.

The August proposal goes further. It arrives in the context of a broader enforcement apparatus: the DOL Inspector General has launched a major H-1B and PERM fraud investigation backed by dozens of subpoenas. Cognizant has been named in a whistleblower-driven probe. The Department of Labor is separately drafting rules to raise prevailing wage floors for H-1B workers and green card petitions, which would increase the cost floor for entry-level sponsored positions.

And starting this month, H-1B-dependent employers — those with more than 50 staff where visa holders constitute over half the workforce — must pay an additional $4,000 for every H-1B extension petition and $4,500 for L-1 extensions. These fees previously applied only to initial stays or employer changes.

Stack these measures and the arithmetic of the body-shop model changes fundamentally. Higher per-worker costs. Steeper documentation burdens. Greater audit exposure. And a regulatory environment where the burden of proof has shifted from "show us you filed the paperwork" to "prove every placement is real, every day, at every site."

## The diaspora fallout

The impact extends well beyond Tata and Infosys. Hundreds of thousands of Indian engineers currently working at client sites across the United States — at banks, insurance companies, healthcare systems, and technology firms — hold H-1B visas sponsored by consulting and staffing companies. If their employer cannot satisfy the new documentation standard, the visa petition itself could be denied or revoked.

For those workers, a denial does not just mean a job loss. It triggers a 60-day grace period to find a new sponsor, transfer to another visa category, or leave the country. Workers deep into the green card backlog — EB-2 India applicants who have waited a decade or more — would lose their place in line if they depart.

Indian IT industry associations are expected to lobby aggressively during the public comment period. In previous rounds, Nasscom and individual firms have argued that client-site placements fill genuine skill gaps and that the US economy benefits from the arrangement. The administration has shown little interest in that argument.

## What comes next

The August proposal is exactly that — a proposal. Public consultation could soften the final rule or delay it. But the regulatory trend line has been consistent: each iteration adds cost, documentation, and risk to the consulting placement model. For Indian IT firms that have spent two decades optimising that model, the question is no longer whether to adapt. It is how fast."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Body-Shop Model Has an Expiration Date. August's Rule Will Force Indian IT to Prove Every Placement",
    "subheadline": "A proposed rule would require consulting firms to document genuine employer-employee relationships at every client site. Combined with new fees and fraud probes, the economics of third-party H-1B placements are under existential pressure.",
    "slug": make_slug("third-party-placement-rule-indian-it-consulting-h1b"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Hundreds of thousands of Indian engineers work at US client sites on H-1B visas sponsored by consulting firms. A denial under the new documentation standard could end their green card wait and trigger a 60-day departure clock.",
    "tags": ["h1b", "third-party-placement", "indian-it", "consulting", "uscis", "tcs", "infosys"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/why-1-lakh-indian-h-4-visa-holders-could-face-job-disruptions-in-the-us"},
        {"name": "Times of India (via Kably)", "url": "https://timesofindia.indiatimes.com/nri/us-canada-news/h-1b-visa-holders-brace-for-sweeping-changes-as-trump-administration-rolls-out-regulatory-blitz/articleshow/122444521.cms"},
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/uscis-toughens-requirements-for-third-party-placement-of-h-1b-employees.html"},
        {"name": "Bhaskar English", "url": "https://bhaskarenglish.in/national-international/us-probes-indian-it-firm-cognizant-over-h-1b-visa-fraud/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8353769/pexels-photo-8353769.jpeg",
    "image_caption": "Professionals collaborate at a corporate office desk with computers and documents",
    "image_attribution": "Pexels",
    "body": art3_body.strip(),
}

# ─────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
