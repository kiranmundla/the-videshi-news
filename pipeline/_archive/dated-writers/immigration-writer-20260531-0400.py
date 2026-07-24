#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-31 04:00 UTC run"""
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

# ─────────────────────────────────────────────
# ARTICLE 1
# ─────────────────────────────────────────────

art1_body = """The USCIS memo declaring adjustment of status an "extraordinary form of relief" was announced on May 21. Within nine days, adjudicators were already acting on it — and the evidence requests they are sending to applicants reveal exactly how the government plans to decide who stays and who goes.

CNN has obtained a Request for Evidence (RFE) issued to a pending adjustment-of-status applicant that lays out roughly a dozen factors the adjudicator may weigh in the applicant's favor. Among them: hardship to the applicant's family if their case is denied, evidence of value or service to their community, and fluency or proficiency in English. The checklist reads less like an immigration standard and more like a citizenship exam administered at the wrong stage of the process.

## The Backpedal That Wasn't

The timeline tells a story the administration would probably prefer to edit. On May 21, USCIS announced that anyone on a temporary visa seeking a green card should generally return home and apply through consular processing abroad. The language was blunt: adjustment of status was a "loophole" that let immigrants "slip into the shadows."

By May 28, the Department of Homeland Security was walking it back. A DHS spokesperson told the Washington Examiner the memo "reaffirms existing discretionary powers" and "does not impact existing green card holders at all." USCIS spokesman Zach Kahler framed the reversal as a return to the "original intent of the law."

But immigration attorneys are not buying the soft landing. "They want it to be arbitrary and capricious," said Jim Hacking, an immigration attorney. "They want people to be scared, and they want people to leave the US voluntarily."

## What the Law Actually Says

The legal foundation matters here, because USCIS is trying to frame a 74-year-old statutory right as an administrative favor. Congress first authorized adjustment of status in 1952. It has amended the relevant provisions of the Immigration and Nationality Act more than 20 times since — including the 1990 reauthorization that explicitly allowed H-1B and L-1 visa holders to pursue permanent residency without jeopardizing their temporary status.

"When Congress amends and betters a law 20 times, it's hard to call that a loophole," said Charles Kuck, an Atlanta-based immigration attorney, in an interview with CNN. "It is the law, and the law will continue to allow for adjustment of status for individuals who otherwise qualify inside the United States."

Kuck estimates there are roughly a million pending adjustment-of-status applications in the system. Retroactively forcing those applicants to leave and restart through consular processing would be logistically impossible and legally indefensible. "No judge upholds that — none," he said.

## Why Indian Applicants Face the Sharpest Edge

For most nationalities, the adjustment-of-status process is a relatively contained chapter — file, wait, get approved. For Indians on employment-based green card tracks, it is a decade-long commitment. EB-2 India's priority date is currently stuck in 2013. EB-3 is barely better. That means Indian professionals who filed their I-485 years ago are now being asked to prove they meet a dozen subjective factors just to keep the application they have been nursing for a decade.

The "economic benefit or national interest" standard that USCIS has outlined for allowing in-country processing is deliberately vague. A senior engineer at Google almost certainly qualifies. A mid-level developer at a consulting firm in Columbus? A pharmacist in a suburban Walgreens? Nobody knows — including the adjudicators.

The chilling effect is already measurable. Technology workers were among the most vocal critics of the memo when it was announced, and immigration attorneys report a surge in inquiries from Indian professionals weighing whether to abandon their pending I-485 applications and pursue permanent residency in Canada, Germany, or the EU instead.

"We have options, and we're fighting really hard to stay in the US and contribute economically," one research scientist with a pending green card application told CNN. "But if that's not a possibility, we are competitive in other markets, and we'll have no other choice but to take our family elsewhere."

## What to Do Now

For Indian H-1B holders with pending I-485 applications, the practical advice from immigration attorneys is remarkably consistent: do nothing drastic. The memo is a policy change, not a law change. It will almost certainly be challenged in federal court. In the meantime, build a record of your contributions — community involvement, economic impact, professional achievements — because the new RFE checklist makes clear that USCIS will want to see receipts."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The 12-Factor Test USCIS Is Already Using to Decide Who Gets to Stay",
    "subheadline": "Adjudicators are sending evidence requests on pending green card applications — asking about English proficiency, community service, and family hardship. Immigration attorneys say it's designed to scare people into leaving.",
    "slug": make_slug("uscis-12-factor-rfe-test-aos-green-card-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders with pending I-485 applications — many filed a decade ago due to EB-2/EB-3 backlogs — are now being asked to prove subjective factors like community service and English proficiency just to keep applications alive. The vague 'economic benefit' standard creates a two-tier system where Big Tech employees likely pass but mid-size company workers face uncertainty.",
    "tags": ["uscis", "green-card", "adjustment-of-status", "h1b", "i-485", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/05/30/politics/trump-green-card-messaging"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/doj-asserts-trump-authority-in-h-1b-visa-fee-case-has-few-limits"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/immigration/green-card-changes-may-force-applicants-to-leave-country"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/us-sees-green-card-rule-shift-raises-concerns-for-foreign-students-and-skilled-workers/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7009478/pexels-photo-7009478.jpeg",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2
# ─────────────────────────────────────────────

art2_body = """Somewhere in America right now, an Indian graduate with a master's degree in computer science is sitting at a kitchen table, refreshing a job portal for the 1,501st time. Their OPT clock is ticking. Their H-1B lottery odds are 35 percent. And the pipeline that was supposed to carry them from campus to career to green card is coming apart at every joint.

Community reports from international students and recent graduates paint a picture of a job market that has stopped responding. Some students report submitting more than 1,500 applications without receiving a single callback. Not a single rejection with feedback. Not a phone screen. Just silence — while a 90-day unemployment clock counts down toward the end of their legal status in the United States.

## The Numbers Behind the Silence

The Optional Practical Training program allows international students to work in the US for up to 12 months after graduation, with a 24-month extension for STEM degree holders. For Indian students — who constitute roughly 25 percent of all foreign graduates in the US — OPT has historically been the bridge between a degree and an H-1B petition.

But that bridge is buckling. In fiscal year 2026, USCIS received 343,981 eligible H-1B registrations and selected only 120,141 — a selection rate of approximately 35 percent. For the Indian graduates who make it through OPT only to lose the H-1B lottery, the options narrow fast: find another employer willing to re-register, switch to another visa category, or leave.

The unemployment limits compound the pressure. Standard OPT holders face a 90-day cumulative unemployment cap. STEM OPT holders get 150 days — generous on paper, punishing in a market where 1,500 applications yield zero responses. A student who crosses the limit falls out of F-1 status entirely, potentially triggering inadmissibility bars that make returning to the US exponentially harder.

## Why Employers Are Backing Away

The collapse is not just a demand problem. Employers are retreating from H-1B sponsorship at a pace that would have been unthinkable five years ago. The reasons stack up: the $100,000 fee on new H-1B petitions makes sponsorship cost-prohibitive for all but the largest firms. Mandatory social-media screening, expanded in December 2025, has slowed consular processing to a crawl, with some H-1B and H-4 appointments in India pushed out by 90 to 120 days. And the proposed "Fairness for High-Skilled American Act" — backed by USCIS Director Joseph Edlow — seeks to eliminate OPT entirely, arguing that the program gives foreign graduates an unfair advantage over Americans.

For Indian IT services firms, which have historically been among the largest H-1B users, the calculus has already shifted. Tata Consultancy Services, Infosys, and Cognizant have all accelerated local US hiring while scaling back visa-dependent deployments. Nasscom, the Indian IT industry body, maintains that H-1B workers now represent less than one percent of the total employee base of the top 10 Indian IT firms. But that statistic obscures the pipeline effect: every senior engineer who arrived on an H-1B a decade ago started as exactly the kind of OPT graduate who is now being shut out.

## The Enrollment Signal Nobody Can Ignore

The pipeline has a leading indicator, and it is flashing red. Data from the Student and Exchange Visitor Information System shows that active Indian student enrollment in the US dropped by nearly 28 percent year-over-year in 2025. The decline reversed years of consistent growth and coincided with tighter visa regulations, ad-hoc deportation reports, and rising tuition costs.

The enrollment drop matters because it is self-reinforcing. Fewer Indian students means fewer OPT workers, which means fewer H-1B petitions, which means fewer future green card applicants from India. The pipeline does not just slow — it shrinks at every stage simultaneously.

Universities are beginning to feel the revenue impact. International students, who pay full out-of-state tuition at most public universities, represent a significant revenue stream. A sustained decline in Indian enrollment — India has been the second-largest source country for international students after China — would force budget adjustments at precisely the institutions that depend most on that income.

## What This Means for the Next Generation

For the Indian family in Hyderabad or Pune weighing whether to send a child to an American university, the value proposition has fundamentally changed. A US master's degree used to come with a built-in career trajectory: OPT for experience, H-1B for employment, green card for permanence. Each stage was uncertain, but the pipeline existed and it worked often enough to justify the investment.

Today, the pipeline's every joint is under attack — from the $100,000 H-1B fee to the OPT elimination bill to the adjustment-of-status crackdown. The question Indian families are asking is no longer "which US university?" but "which country?" Canada's Express Entry system processes permanent residency in under six months. Germany's EU Blue Card offers a pathway in 21 months. Australia has expanded its Global Talent visa. The competition for Indian talent is real, and the US is losing it one kitchen table at a time."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "1,500 Applications, Zero Callbacks — Inside the Collapse of the OPT Pipeline",
    "subheadline": "Indian graduates are submitting thousands of job applications into the void while their work authorization clocks tick toward zero. The bridge between a US degree and an H-1B petition is breaking at every joint.",
    "slug": make_slug("opt-pipeline-collapse-indian-graduates-zero-callbacks"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians constitute 25% of all foreign graduates in the US. OPT has been the critical bridge between an Indian student's degree and an H-1B petition. With employer sponsorship retreating, the $100K fee deterring new petitions, and OPT elimination bills gaining traction, the entire model that brought generations of Indian engineers to Silicon Valley is under existential threat.",
    "tags": ["opt", "stem-opt", "f1-visa", "h1b", "indian-students", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "ainvest", "url": "https://www.ainvest.com/news/h-1b-opt-programs-under-fire-job-seekers-report-zero-callbacks/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/national/28-fall-in-indian-students-headed-to-us-in-fy25/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/us-sees-green-card-rule-shift-raises-concerns-for-foreign-students-and-skilled-workers/"},
        {"name": "Fakhouri Global Immigration", "url": "https://fakhouryglobal.com/fgi-update-this-weeks-summary/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/9829485/pexels-photo-9829485.jpeg",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
