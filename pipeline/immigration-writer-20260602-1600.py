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
        "headline": "No Card, No Job — The H-4 EAD Crisis Forcing Thousands of Indian Spouses Out of Work",
        "subheadline": "With automatic work permit extensions killed and processing times stretching past six months, H-1B spouses are turning to federal lawsuits as their only option to keep earning.",
        "slug": make_slug("h4-ead-crisis-mandamus-lawsuits-indian-spouses-work-permits"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The H-4 EAD crisis disproportionately affects Indian American families. An estimated 90% of H-4 spouses hold bachelor's degrees, nearly 60% have master's degrees, and two-thirds work in STEM fields. Most are women who followed their H-1B spouse to the United States and built professional careers. The elimination of automatic extensions means a six-month processing gap now equals six months of forced unemployment — no income, no career continuity, no leverage with employers. For dual-income Indian families in high-cost metros like the Bay Area, Seattle, and the New York tristate area, losing one salary is not an inconvenience. It is a financial emergency.",
        "tags": ["h4-ead", "h1b", "work-permit", "mandamus", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/preparing-for-ead-delays-a-guide-for-h-4-and-aos-applicants-on-mandamus/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-spouses-sue-over-end-to-automatic-work-permit-renewals-1"},
            {"name": "Berry Appleman & Leiden LLP", "url": "https://bal.com/"},
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/category/nonimmigrant-family/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "body": """The work permit that allowed Priya Sharma (name changed) to earn $145,000 a year as a data engineer in Seattle expired on February 28. Her renewal application, filed in September 2025, remains pending. She has not worked in three months. Her employer terminated her position after 30 days without valid authorization. Her H-1B husband's job is stable. Their mortgage is not.

Sharma's situation is not unusual. It is, by mid-2026, the default experience for tens of thousands of H-4 visa holders — the spouses, overwhelmingly wives, of H-1B workers who had been granted the right to work in the United States under a 2015 Obama-era regulation. That right still exists on paper. In practice, it has been hollowed out by a sequence of administrative decisions that have turned the H-4 Employment Authorization Document into something closer to a lottery ticket than a professional credential.

## The Safety Net That Vanished

For years, H-4 EAD holders had a cushion. If you filed your renewal on time, your work authorization automatically extended — first for 180 days under a 2017 rule, then for up to 540 days during the pandemic-era backlog surge. The extension was imperfect, but it kept people employed while USCIS ground through its queue.

In October 2025, the Department of Homeland Security killed the automatic extension for most categories, including H-4 and adjustment-of-status EAD holders. The justification was security — the same word that has been stapled to every restriction targeting legal immigration workers since 2017. The practical effect was immediate: once your card expires, you stop working. Period. No grace period. No bridge authorization. Your employer is legally required to suspend or terminate you.

The timing was especially brutal. A January 2023 settlement — born from the *Shergill v. Mayorkas* litigation — had forced USCIS to process H-4 EADs concurrently with H-1B petitions. When the primary worker's H-1B was approved under premium processing, the spouse's work permit often followed within 15 days. That settlement expired in January 2025. USCIS is no longer bound to bundle the applications. Some adjudicators still do. Many do not. Processing times for standalone H-4 EADs now stretch to five, six, seven months — or longer.

## The Math That Doesn't Work

Here is the arithmetic that traps H-4 families. You can file a renewal no earlier than 180 days before your EAD expires. USCIS processing times for standalone H-4 applications now routinely exceed 180 days. With no automatic extension, a gap is not a risk — it is a near-certainty.

Premium processing, the $2,805 fast-track option that resolves H-1B petitions within 15 business days, is not available for H-4 or EAD applications. USCIS expanded premium processing to F-1 student employment authorization in 2024 but has not extended it to H-4 dependents. The fastest workaround is to file the H-4 renewal together with the spouse's H-1B extension under premium processing and hope the adjudicator bundles them. Immigration attorneys report that this strategy works roughly half the time. The other half, the H-4 application is separated and parked in the regular processing queue.

## Mandamus: The $7,000 Last Resort

When administrative channels fail, a growing number of H-4 holders are turning to the federal courts. A mandamus lawsuit — formally a petition under the Administrative Procedure Act — asks a judge to compel USCIS to adjudicate a long-pending application. The cost typically runs $5,000 to $10,000 in legal fees. The government has 60 days to respond once served.

The mechanics are counterintuitive. Filing the lawsuit often resolves the case before any judge rules. USCIS attorneys, once served, frequently coordinate with the agency to approve the underlying application rather than defend the delay in court. Immigration attorney Steven Brown of Reddy Neumann Brown PC, whose firm has filed hundreds of mandamus cases, describes it as "one of the few tools that has successfully forced movement on delayed applications."

But mandamus is not universally accessible. Not every H-4 spouse can afford $7,000 in legal fees while already unemployed. Not every family is comfortable suing the federal government while their immigration status depends on that same government's goodwill. And not every delay meets the threshold courts consider "unreasonable" — though judges have increasingly recognized that even sub-year delays can cause severe harm when employment is at stake.

## Who Bears the Cost

The demographics tell the story the policy debates often obscure. According to data compiled by Berry Appleman & Leiden LLP, 90 percent of H-4 spouses hold a bachelor's degree. Nearly 60 percent have a master's. Two-thirds of H-4 EAD holders work in STEM fields. The overwhelming majority are women — a point underscored by 60 members of Congress who, in a letter to the incoming Biden administration in 2021, described the affected population as "mostly women of color."

These are not marginal workers. They are software engineers, data scientists, product managers, biomedical researchers, and financial analysts. When they are forced out of work, their employers lose institutional knowledge that cannot be easily replaced. The workers themselves face résumé gaps that carry a lasting professional penalty, particularly in technology and finance where continuous employment is a proxy for competence.

## What Comes Next

The legal landscape is unstable. Bloomberg Law reported in January 2026 that a group of H-1B spouses filed a class-action lawsuit challenging the end of automatic extensions, arguing that DHS cited national security as a pretext for what amounts to economic punishment. The plaintiffs contend that DHS has continuous vetting programs that render point-in-time EAD adjudication unnecessary for security purposes. The case is pending.

Meanwhile, immigration advocacy groups are pushing USCIS to extend premium processing to H-4 and AOS EAD categories — a change that would, more than any single reform, reduce the practical harm. USCIS has acknowledged the demand but has not committed to a timeline.

For Indian families navigating the system today, the advice from every immigration attorney is the same: file at the earliest possible moment, bundle with premium H-1B filings, and if you can afford it, have a mandamus attorney on speed dial. The system, as currently configured, does not work without litigation as a backstop. That is not a bug report. It is the operating specification."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your LinkedIn Is Now Evidence — Six Months of Social Media Vetting and the Permanent Damage to Indian Visa Processing",
        "subheadline": "Since December 2025, every H-1B and H-4 applicant at a US consulate has had their social media reviewed before an interview. The result: 40 percent fewer appointments, months-long delays, and a surveillance regime that is not going away.",
        "slug": make_slug("social-media-vetting-h1b-india-consulate-six-month-damage"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India is the world's largest source of H-1B visa holders, and Indian consulates — Mumbai, Hyderabad, Chennai, New Delhi, Kolkata — process more H-1B and H-4 interviews than any other country. The social media vetting policy hit Indian applicants harder than anyone else by sheer volume. An estimated 7,500 appointments were affected in the first week alone at just three Indian consulates. For the Indian diaspora, this is not an abstract policy change: it is the reason your cousin's H-1B stamping got bumped to March, why your colleague cannot travel home for a family emergency, and why IT services firms are rerouting employees to Singapore and Bangkok consulates at additional cost.",
        "tags": ["social-media-vetting", "h1b", "h4", "india-consulate", "uscis", "visa-interview", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Boundless", "url": "https://www.boundless.com/immigration-resources/u-s-consulates-cancel-h-1b-and-h-4-visa-appointments-as-new-social-media-review-begins/"},
            {"name": "VisaHQ", "url": "https://www.visahq.com/discussion/expanded-social-media-vetting-delays-h-1b-visa-interviews-forcing-reschedules-into-2026"},
            {"name": "Shumaker Loop & Kendrick LLP", "url": "https://www.shumaker.com/client-alert-us-consular-posts-rescheduling-h1b-and-h4-visa-appointments-following-department-of-states-online-presence-review/"},
            {"name": "Greenberg Traurig", "url": "https://gtlaw-insidebusinessimmigration.com/category/india/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/16229745/pexels-photo-16229745.jpeg",
        "body": """On December 10, 2025, the US Embassy in India sent a terse email to thousands of H-1B and H-4 visa applicants: do not show up for your interview. Your appointment has been cancelled. A new date will follow.

No explanation was offered beyond "operational constraints." The real reason arrived five days later, when the State Department's expanded social media vetting policy went live on December 15. Every H-1B worker and every H-4 dependent applying for a visa stamp at a US consulate would now have their social media profiles reviewed before an interview could proceed. The policy had previously applied only to students and exchange visitors. It now covered the largest work-visa category in the American immigration system.

Six months later, the disruption has not ended. It has calcified into a permanent feature of Indian visa processing.

## The December Shock

The scale of the initial cancellation was staggering. Immigration law firm Fragomen estimated that nearly 7,500 appointments were affected in Mumbai, Chennai, and Hyderabad alone during the first two weeks. Applicants who had booked December interviews — many of them timed around year-end India visits to see family — received rescheduled dates in March 2026, a full three months later.

The consulates were blunt about the reason. Shumaker, Loop & Kendrick LLP, a national law firm, documented in a December 15 client alert that "consular posts have reported that, as they implement the online presence review for H-1B/H-4 cases, they must reduce daily interview capacity to complete the new vetting." The State Department directed all applicants to make their social media accounts — Facebook, Instagram, X, LinkedIn, TikTok, YouTube — publicly viewable before their interview.

Consular officers were now authorized to review posts, photos, connections, and professional histories. The stated purpose: to identify inconsistencies between online profiles and visa application details, flag national security or public safety concerns, and assess content that could affect visa eligibility. In practice, this meant that every applicant's digital footprint became part of the adjudication file.

## Forty Percent Fewer Slots

The operational impact was immediate and severe. VisaHQ, a visa facilitation firm, reported that daily interview capacity dropped by as much as 40 percent at Mumbai and Hyderabad — the two highest-volume consulates for H-1B stamping in the world. The math is straightforward: if a consular officer must spend 15 to 20 minutes reviewing an applicant's social media before a 5-minute interview, the number of interviews per day drops by roughly half.

Six months into the policy, the backlog has not cleared. Consulates have not restored pre-December capacity. Appointment wait times for H-1B stamping at Indian posts remain 60 to 120 days longer than they were in November 2025. The bottleneck is structural — there are not enough consular officers trained in the new vetting protocol, and the State Department has not authorized additional hires to compensate for the reduced throughput.

IT services firms — Infosys, Wipro, TCS, HCLTech, and the dozens of mid-tier staffing companies that collectively deploy tens of thousands of H-1B workers — have adapted by rerouting employees to consulates in Singapore, Bangkok, and other posts with shorter backlogs. This works, but it costs. A round-trip flight to Singapore, a hotel stay, and the risk of a different consulate applying different standards add $2,000 to $5,000 per employee per stamping trip. For a company with 500 employees needing consular stamps in a given quarter, the aggregate cost is material.

## The Compliance Burden

For individual applicants, the policy creates a new category of pre-interview anxiety. Immigration attorneys advise clients to audit every social media account months before their appointment. The checklist is exhaustive: remove or explain any posts that could be read as inconsistent with the visa application, ensure that LinkedIn job titles match the H-1B petition's job description exactly, verify that location tags and travel posts align with I-94 entry and exit records, and check that no post could be construed as unauthorized employment or immigration fraud.

The guidance from consulates is deliberately broad. The State Department has not published a list of specific social media red flags. Consular officers have discretion to weigh any content they find relevant. This ambiguity is the point — it allows maximum screening latitude while offering applicants no clear standard to meet. Immigration attorney James Hollis, who first publicly confirmed the cancellations on LinkedIn, noted that the vagueness "leaves applicants in a position where they cannot fully prepare because they don't know what the officer will focus on."

For H-4 dependents, the burden is particularly absurd. Many H-4 holders are not working and have minimal professional social media footprints. They are still subject to the same review. Their appointments are still reduced by the same capacity constraints. Their stamping delays are identical to their H-1B spouse's.

## NASSCOM Pushed Back. Nobody Listened.

NASSCOM, the Indian IT industry's primary lobbying body, formally requested a phased implementation of the social media vetting policy in December 2025, arguing that the abrupt rollout would cause economic fallout for both American and Indian companies. The State Department did not modify the timeline. The policy went into effect on December 15 as planned.

The diplomatic channel has been equally unproductive. India's External Affairs Ministry raised the consular delays in bilateral discussions, but the US position has been consistent: the social media review is a national security measure, not a trade barrier, and it will apply uniformly to all applicants regardless of nationality. The fact that Indians constitute the largest affected population is, in the State Department's framing, a demographic coincidence rather than a policy choice.

## The New Normal

What has emerged over six months is not a temporary disruption. It is a recalibration of the visa stamping process that assumes social media review is a permanent component of consular adjudication. The State Department has shown no interest in rolling back the policy, streamlining the review process, or increasing consular capacity to restore pre-December throughput.

For Indian H-1B workers, the practical implications are clear. International travel now requires three to four months of lead time for visa stamping, compared to two to four weeks before December 2025. Emergency travel — a parent's illness, a family crisis — is no longer compatible with a stamped visa. Workers whose visas expire must choose between staying in the United States without traveling or accepting a months-long gap before they can re-enter.

Major US tech companies have already advised H-1B employees to avoid international travel unless absolutely necessary. The advice is pragmatic but corrosive: it tells skilled workers that the system designed to facilitate their employment now actively discourages them from leaving the country. For a workforce that overwhelmingly maintains deep family ties in India — parents to visit, weddings to attend, children to introduce to grandparents — the message lands hard.

The social media vetting policy will not appear on any list of visa denials or deportation orders. It does not revoke anyone's status. It simply makes every interaction with the consular system slower, more anxious, and more expensive. Six months in, that is enough to reshape how an entire generation of Indian tech workers thinks about their relationship with the United States."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
