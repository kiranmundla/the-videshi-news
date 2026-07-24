#!/usr/bin/env python3
"""Immigration writer – 2026-07-10 07:00 PT run (batch b). Three articles."""

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

# ─────────────────────────────────────────────────────────────
# ARTICLE 1: H-4 EAD Automatic Extension Ending
# ─────────────────────────────────────────────────────────────

art1_body = """The Department of Homeland Security is expected to finalise a rule later this month that would end the automatic extension of Employment Authorisation Documents for H-4 visa holders. For roughly one hundred thousand Indian spouses who depend on that provision to keep working while their renewals crawl through the system, the timing could not be worse.

The automatic extension was a bureaucratic pressure valve. It allowed H-4 EAD holders to continue working for up to 180 days beyond their document's expiry date, provided a timely renewal application was on file. USCIS processing, however, routinely stretches to five to seven months — and in some service centres, closer to a year. The automatic extension bridged that gap. Without it, a properly filed renewal that takes eight months to adjudicate means eight months without legal work authorisation.

## The Arithmetic of a Work Gap

H-4 EAD holders can submit renewal applications no earlier than 180 days before expiry. If USCIS takes seven months to process the renewal — a conservative estimate given current backlogs — that leaves a minimum 30-day employment gap even for applicants who file at the earliest possible date. For the many cases that take longer, gaps of three to six months are realistic.

The financial arithmetic is brutal. Indian H-1B households in major tech corridors — the Bay Area, Seattle, the Research Triangle — carry mortgage and childcare obligations calibrated to dual incomes. A sudden loss of the second earner's income does not merely inconvenience. It destabilises.

Employers face their own headaches. Under I-9 rules, a worker whose employment authorisation lapses must stop working immediately. There is no grace period, no workaround, no employer discretion. Companies that allow an unauthorised worker to continue face penalties. The result: even model employees with spotless records and pending renewals will be sent home until USCIS acts.

## Why This Hits Indian Families Hardest

Indians constitute the overwhelming majority of H-4 EAD holders. The programme exists specifically for spouses of H-1B workers whose employers have started the green card process — a category dominated by Indian nationals stuck in the EB-2 and EB-3 backlogs that now stretch decades. For many of these families, the H-4 EAD was the one concession that made the interminable green card wait bearable.

The rule change lands in an environment already hostile to dependent visa holders. The Trump administration's first-term attempt to rescind H-4 EAD eligibility altogether was blocked in court. This latest move achieves a softer version of the same outcome: it does not eliminate the work permit, but it ensures that administrative delays — delays the government itself creates — will periodically strip away the right to use it.

A lawsuit filed by affected families alleges DHS implemented the change without adequate public consultation. Their lawyers argue the policy penalises people who are fully compliant with immigration law but caught in processing backlogs they did not create and cannot control.

## What Families Should Do Now

Immigration attorneys are advising H-4 EAD holders to file renewals at the absolute earliest opportunity — 180 days before expiry, not a day later. Families should build emergency savings sufficient to cover at least six months of single-income living. Employers with H-4 EAD workers on staff should audit expiry dates immediately and develop contingency plans for potential work gaps.

The deeper question is whether USCIS will accelerate processing to match its own new timeline. Early signs are not encouraging. The agency's own Ombudsman recently identified H-1B extension delays as the agency's biggest operational problem. Adding tens of thousands of H-4 EAD renewals to a system already struggling to keep pace is unlikely to speed things up.

For the hundred thousand Indian spouses watching this rule take shape, the message is clear: your work permit still exists, but the government has removed the one mechanism that kept it functional."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Spouse's Work Permit Expires This Month. The Government Just Killed the Safety Net",
    "subheadline": "DHS is finalising a rule that ends automatic EAD extensions for H-4 visa holders — leaving roughly one hundred thousand Indian spouses facing employment gaps of up to six months while renewals sit in the USCIS queue.",
    "slug": make_slug("h4-ead-automatic-extension-ending-indian-spouses-work-gap"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian spouses on H-4 visas — the largest group of H-4 EAD holders — will disproportionately bear the burden of employment gaps created by the loss of automatic extensions, threatening the dual-income stability that sustains families trapped in decade-long green card backlogs.",
    "tags": ["h4-ead", "uscis", "immigration", "h1b", "work-permit", "green-card-backlog", "indian-spouses"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/why-1-lakh-indian-h-4-visa-holders-could-face-job-disruptions-in-the-us"},
        {"name": "The 420", "url": "https://the420.in/immigrant-families-face-fresh-uncertainty-in-the-us-as-automatic-work-permit-extension-is-scrapped/"},
        {"name": "Khandelwal Law", "url": "https://khandelwalaw.com/h-4-visa-ead-latest-news/"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/stricter-vetting-slower-processing-how-new-immigration-form-changes-are-reshaping-2026-07-06/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: F-1 Student Visa Duration of Status Rule
# ─────────────────────────────────────────────────────────────

art2_body = """For three decades, international students in the United States have operated under a simple bargain: maintain your status, follow the rules, and you can stay as long as your programme requires. The Department of Homeland Security is about to rewrite that deal. The final rule eliminating "Duration of Status" for F-1 student visas was submitted to the Office of Management and Budget on May 5 and could be published in the Federal Register within weeks. Once it appears, students have 60 days before the most significant procedural shift in international education in a generation takes effect.

The change replaces the open-ended D/S framework — under which students receive an I-94 stamped simply "D/S" and remain in the country for as long as their programme lasts — with fixed admission periods capped at four years. Any student who needs longer, whether for a doctoral dissertation that runs behind schedule or a medical residency that extends beyond the initial timeline, would need to file a formal Extension of Stay application with USCIS, complete with updated documents, biometrics, fees, and proof of financial resources.

## Three Hundred and Sixty Thousand Indian Students

India is the largest source of international students in the United States. Around 3.6 lakh Indian students enrolled during the 2024-25 academic year, according to the Open Doors Report — nearly 31 per cent of all international students in the country. The proposed rule would affect every one of them.

The impact falls hardest on graduate students in STEM programmes, where Indian enrolment is concentrated. A computer science PhD that takes six years instead of the expected five would now require a formal USCIS extension rather than a simple I-20 update through the university. A medical resident whose fellowship adds an unexpected year would face the same bureaucratic hurdle. Each extension filing carries fees, processing delays, and the risk of denial.

The grace period after programme completion would also shrink from 60 days to 30 — halving the time graduates have to arrange departure, secure a change of status, or find an employer willing to sponsor an H-1B petition.

## The Day 1 CPT Escape Hatch Narrows Further

Perhaps the sharpest impact for Indian students is on what immigration lawyers call the Day 1 CPT pathway. Thousands of Indian tech workers who lose the H-1B lottery currently enrol in a second master's programme to maintain work authorisation through Curricular Practical Training while they try again.

The new rule would prohibit lateral or reverse matriculation — barring F-1 students from pursuing a programme at the same or lower educational level after completing one. For someone with a master's degree who needs to enrol in another master's programme to stay employed, the door closes.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" said Danielle Goldman, co-founder and CEO of Build, an immigration services firm.

## Universities Are Flying Blind

NAFSA, the leading international education association, expects the rule to retain most provisions from the August 2025 proposed version. But because the final text will not be available to the public until at least 24 hours before publication, universities trying to prepare for the September 2026 intake are working from the draft — a document that may have changed during the review process.

The administrative burden will shift from university international student offices, which currently manage most programme extensions through routine I-20 updates, to USCIS itself. Andrew Lyonsberg, a partner at McDermott Will & Schulte who has successfully appealed previous Trump administration immigration rules, has suggested the international education community begin documenting concrete harms in preparation for potential legal challenges under the "arbitrary and capricious" standard.

## What Students Should Do Now

Indian students currently in the US should confirm their programme end dates and plan extension timelines well in advance. Those applying for Fall 2026 admission should factor the new extension costs and uncertainty into their financial planning. Students relying on Day 1 CPT programmes as a backup should consult immigration counsel immediately — the landscape may shift dramatically once the final rule publishes.

Companies recruiting from American universities face a narrower pipeline. Goldman warned that employers in AI, machine learning, and data science — fields where foreign nationals make up a substantial portion of the talent pool — should preserve alternate visa strategies including O-1 and EB-based pathways.

The rule is not yet in effect. But the regulatory machinery is moving, and the 60-day clock starts the moment it hits the Federal Register."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Four Years. That Is How Long Indian Students Will Get to Finish Their American Degree",
    "subheadline": "The final rule replacing Duration of Status with fixed admission periods for F-1 visas is at OMB. When it publishes, 3.6 lakh Indian students face a fundamentally different immigration framework — and the Day 1 CPT safety net all but disappears.",
    "slug": make_slug("f1-duration-of-status-fixed-period-indian-students-omb"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "India sends more students to the US than any other country. The D/S rule change would force them into a rigid fixed-period system with expensive USCIS extensions, narrow the Day 1 CPT pathway that thousands of Indian tech workers depend on, and shrink the post-graduation grace period that enables the H-1B transition.",
    "tags": ["f1-visa", "duration-of-status", "indian-students", "uscis", "immigration", "opt", "day-1-cpt", "stem"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/07/09/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/06/us-to-end-duration-of-status-for-f-j-and-i-visas/"},
        {"name": "Washington University OISS", "url": "https://oiss.washu.edu/duration-of-status-dhs-proposed-changes/"},
        {"name": "Berardi Immigration Law", "url": "https://berardiimmigrationlaw.com/dhs-proposed-rule-end-of-duration-of-status-for-f-1-j-1/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7713182/pexels-photo-7713182.jpeg",
    "image_caption": "Graduates celebrating in caps and gowns on a university campus",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 3: Third-Party Placement Rule — August Proposal
# ─────────────────────────────────────────────────────────────

art3_body = """The Trump administration is preparing an August proposal that would tighten H-1B rules for third-party client placements — the staffing and consulting model that forms the backbone of Indian IT operations in the United States. If finalised, the rule would require employers to prove genuine employer-employee relationships, verify specialty occupation duties at client sites, and maintain detailed assignment records. Companies with past violations would face heightened scrutiny.

For firms like Infosys, TCS, Wipro, Cognizant, and HCL Technologies — whose business model depends on placing Indian IT workers at American corporate client sites — the proposal strikes at the heart of their US operations. The client-site model has been a target of regulatory scepticism for years, but this rule would formalise restrictions that previously existed only as informal USCIS adjudication patterns.

## What the Rule Would Require

The proposal demands that employers demonstrate a bona fide employer-employee relationship with H-1B workers placed at third-party worksites. That sounds simple. In practice, it means employers would need to show they control the worker's day-to-day tasks, provide tools and direction, and bear the financial risk of the engagement — even when the worker sits at a client's desk, uses the client's systems, and reports to a client manager.

Companies would also need to verify that the specialty occupation duties described in the H-1B petition are actually being performed at the client site. This creates a documentary burden that goes beyond filing the petition: employers must maintain ongoing records proving the work matches the visa's terms throughout the placement.

For firms with past violations — and several major Indian IT firms have faced USCIS scrutiny, site visits, and Requests for Evidence at elevated rates — the rule adds another layer. Heightened scrutiny means more frequent audits, more detailed documentation demands, and a lower threshold for denial.

## The Business Model Under Pressure

The Indian IT staffing model works because of arbitrage: recruiting engineers in India at Indian salary expectations, placing them at American client sites at rates below what a locally hired American engineer would command, and capturing the spread. The model is legal. It is also precisely the pattern that critics — including Vice President JD Vance, who last week launched a major H-1B fraud probe — describe as "undercutting American workers."

The numbers tell the story of erosion. Indian IT outsourcers saw their H-1B approvals drop 40 per cent in recent data, a trend this publication reported earlier this week. TCS, Infosys, and their peers are already losing share of the H-1B pool to direct employers like Google, Amazon, and Meta who hire workers into permanent roles rather than rotating them across client sites.

The August proposal would accelerate that shift. A staffing firm that cannot prove it — rather than its client — controls the worker's daily activities risks having its petitions denied. A company that cannot maintain assignment records for hundreds of consultants scattered across dozens of client sites risks systemic compliance failure.

## The Fee Stack Compounds the Pain

The third-party placement rule arrives alongside an escalating cost structure. As of this month, H-1B dependent employers — those where visa holders constitute more than half the US workforce — must pay an additional $4,000 for extension petitions. The One Big Beautiful Bill Act's $250 visa integrity fee applies to all nonimmigrant visa holders. Prevailing wage requirements are being raised. The $100,000 H-1B fee, struck down by a federal judge in June, was reinstated on appeal within days and remains in legal limbo.

For an Indian IT firm extending an H-1B worker at a client site, the combined cost of fees, compliance documentation, and legal counsel now substantially exceeds what it was even two years ago. At some point, the economics tip — and either the client site model contracts, or the work moves offshore.

## What This Means for Workers

For the individual Indian IT consultant on an H-1B, the proposal creates a new category of risk. If your employer cannot satisfy the enhanced employer-employee test, your petition may be denied at renewal. If your client site assignment changes and your employer fails to update records promptly, you may find yourself out of status through no fault of your own.

Immigration attorneys are advising H-1B workers at consulting firms to request copies of their petition documents, understand what duties are described in their H-1B filing, and confirm that their actual work matches the filing. Workers whose daily tasks differ substantially from their petition — a common reality in fluid consulting engagements — should flag the discrepancy with counsel before USCIS does.

The August proposal will undergo a period of public consultation before any final rule is issued. Indian IT industry bodies and immigration advocacy groups are expected to mount vigorous opposition. But the regulatory direction is unmistakable: the era of placing an H-1B worker at a client desk with minimal documentation and hoping USCIS does not look too closely is ending."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Client-Site Model That Built Indian IT in America Just Got an Expiry Date",
    "subheadline": "An August proposal would require consulting firms to prove genuine employer-employee relationships at third-party worksites — a rule aimed squarely at the staffing model that Infosys, TCS, and their peers depend on for their US operations.",
    "slug": make_slug("third-party-placement-rule-indian-it-consulting-h1b-august"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Hundreds of thousands of Indian IT professionals work in the US on H-1B visas through the third-party placement model. The proposed rule threatens the visa pipeline that brought many of them here and could force a structural shift in how Indian consulting firms operate on American soil.",
    "tags": ["h1b", "third-party-placement", "indian-it", "consulting", "infosys", "tcs", "uscis", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/why-1-lakh-indian-h-4-visa-holders-could-face-job-disruptions-in-the-us"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-visa-fees-legal-whiplash-demands-employers-preparation"},
        {"name": "BAL Immigration News", "url": "https://www.bal.com/insights/united-states-congress-passes-reconciliation-bill-major-immigration-provisions/"},
        {"name": "NY Post", "url": "https://nypost.com/2025/07/09/opinion/work-visa-fraud-costs-america-big-hail-the-trump-teams-crackdown/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1181404/pexels-photo-1181404.jpeg",
    "image_caption": "A diverse team of professionals working in a modern office setting",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
