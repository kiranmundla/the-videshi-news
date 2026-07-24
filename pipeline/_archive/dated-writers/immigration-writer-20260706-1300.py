#!/usr/bin/env python3
"""Immigration writer — July 6, 2026, 1:00 PM run."""
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
        "headline": "Your Spouse's Right to Work Is Under Review. DHS Has Had the Proposal for Six Months",
        "subheadline": "The H-4 EAD programme that lets spouses of H-1B workers earn a living is caught between a rescission proposal stuck at the White House and a Senate resolution fighting to keep it alive.",
        "slug": make_slug("h4-ead-rescission-omb-review-senate-sjres99-indian-spouses"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Nearly 100,000 H-4 EAD holders are Indian spouses trapped in green card backlogs. If the programme is rescinded, dual-income Indian households lose their second salary overnight — affecting mortgages, childcare, and retirement savings built over years of waiting.",
        "tags": ["h4-ead", "uscis", "immigration", "h1b", "green-card-backlog", "senate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/h-4-ead-rescission-proposal-remains-under-federal-review-dhs-confirms.html"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/senate-nears-vote-on-sjres-99-to-restore-employment-authorization-for-h-4-spouses/"},
            {"name": "Fragomen (Earlier Update)", "url": "https://www.fragomen.com/insights/proposed-h-4-ead-rescission-under-federal-review.html"},
            {"name": "Congressional Research Service", "url": "https://www.congress.gov/bill/119th-congress/senate-joint-resolution/99"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Exterior of a US Immigration and Customs Enforcement building",
        "image_attribution": "Pexels",
        "body": """For six months, the Department of Homeland Security has sat on a proposed rule that would kill the H-4 Employment Authorization Document programme — the provision that allows certain spouses of H-1B workers to hold jobs in the United States. And for six months, roughly 100,000 people, the vast majority of them Indian women, have waited to learn whether their right to work will survive the review.

DHS sent the proposal to the Office of Management and Budget in February 2026. Typically, OMB clears proposed rules within a few weeks, sometimes a couple of months. This one has not moved. In a recent court filing in *Save Jobs USA v. DHS*, the lawsuit that has dogged the programme since 2015, DHS confirmed that the rule "remains under review" and offered no projected publication date.

## What the proposal would do

The H-4 EAD programme, established under the Obama administration in 2015, lets spouses of H-1B workers apply for work authorisation under two conditions: the H-1B holder must have an approved I-140 immigrant petition, or must have received a one-year extension beyond the standard six-year H-1B limit. In practice, this means the programme overwhelmingly serves Indian families stuck in the EB-2 and EB-3 green card backlogs, where wait times stretch well past a decade.

Rescinding the programme would not merely inconvenience these families. It would eliminate the second income that covers mortgages, childcare, student loans, medical insurance, and retirement contributions — all obligations accumulated during years of lawful residence and lawful employment.

## The automatic extension problem

Even before the rescission proposal landed, the administration had already tightened the screws. On October 30, 2025, USCIS ended the 540-day automatic extension rule for Employment Authorization Documents. Under the previous system, an H-4 spouse who filed a timely EAD renewal could continue working for up to 540 days while USCIS processed the application. After October 30, that protection disappeared for new filings.

The result is a compliance nightmare. If USCIS cannot process a renewal before the existing card expires — and processing times routinely exceed six months — the spouse must stop working. No income. No gap-filling. Just a household that suddenly runs on one salary in an American city where one salary is rarely enough.

DHS argued the change was necessary to complete vetting and background checks before granting new work authorisation. Immigration attorneys counter that these are timely-filed renewals by people who already passed every screening the first time.

## The Senate's long-shot lifeline

In the other corner sits S.J.Res. 99, a Congressional Review Act resolution introduced by Senator Jacky Rosen in December 2025 and placed on the Senate Legislative Calendar in March 2026. The measure would overturn the October 2025 rule and restore automatic extensions for all 18 categories of EAD renewals, including H-4 spouses.

Senator Alex Padilla's office has framed the stakes bluntly: the October rule affects not just H-4 spouses but refugees, asylees, and TPS holders. The American Immigration Lawyers Association and the AFL-CIO have both urged passage, arguing that employment gaps punish people who followed every rule.

The resolution faces steep arithmetic. Even if the Senate passes it — requiring only a simple majority — the House must concur and the President must sign. A veto override is theoretically possible but politically improbable under an administration that made H-4 EAD rescission a regulatory priority.

## What Indian families should do now

Immigration law firm Fragomen advises eligible H-4 spouses to file for new or renewed EADs as soon as they qualify. Renewals can be submitted up to 180 days before the existing card expires. Families should coordinate the H-1B extension, H-4 extension, and H-4 EAD renewal into a single package to avoid cascading delays.

Three dates now govern every household budget: the H-1B worker's status expiration, the H-4 spouse's I-94 validity, and the EAD expiration date. Getting any one wrong can trigger an employment gap that no employer can fix after the fact.

The OMB review may yet stall the rescission indefinitely. The robust public response to the proposal — even before its text has been disclosed — appears to have contributed to the delay, according to DHS filings. But delay is not protection, and a court-ordered deadline in *Save Jobs* could force the government's hand.

For now, Indian families remain in the worst possible posture: unable to plan around a rule that hasn't been published, unable to rely on an automatic extension that no longer exists, and unable to count on a Senate resolution that hasn't reached the floor. The only actionable advice is the oldest advice in immigration law: file early, file correctly, and keep every receipt."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Rule That Ends 'Duration of Status' Just Landed at OMB. Indian Students Have Months, Not Years",
        "subheadline": "DHS submitted its final rule to eliminate the 30-year-old Duration of Status framework for F-1 students on May 5. If finalised, every international student in America will face fixed deadlines, USCIS filings, and biometric collection for the first time.",
        "slug": make_slug("f1-duration-of-status-elimination-omb-final-rule-indian-students"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the second-largest international student population in the US and the biggest users of STEM OPT. The D/S elimination would force hundreds of thousands to navigate USCIS extension filings, pay new fees, and risk falling out of status if processing backlogs hit — turning a university problem into an immigration enforcement problem.",
        "tags": ["f1-visa", "student-visa", "uscis", "immigration", "opt", "stem-opt", "duration-of-status"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/07/05/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "Washington University OISS", "url": "https://oiss.washu.edu/immigration/duration-of-status-dhs-proposed-changes/"},
            {"name": "Cornell International Services", "url": "https://international.globallearning.cornell.edu/guidance-dhs-proposes-end-duration-status"},
            {"name": "Yale OISS", "url": "https://oiss.yale.edu/news/dhs-proposes-to-replace-duration-of-status-with-fixed-periods-of-stay-for-f-j-nonimmigrants"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Students walking on a university campus sidewalk",
        "image_attribution": "Pexels",
        "body": """For more than three decades, international students entering the United States have been admitted for "duration of status" — a flexible arrangement that lets them stay as long as they maintain valid enrolment and comply with visa rules. No fixed expiry date stamped in the passport. No extension filings with the government. The university handled everything.

That era is about to end. On May 5, 2026, the Department of Homeland Security submitted its final rule to the Office of Management and Budget to eliminate the Duration of Status framework for F-1 and J-1 visa holders. Once OMB clears it and DHS publishes the final rule in the Federal Register, every international student in America will operate under a fundamentally different system.

## What changes

The proposed rule, first published in August 2025, replaces Duration of Status with a fixed admission period of up to four years. Students who need more time — to finish a degree, to pursue OPT or STEM OPT, to transfer, or to change educational levels — will be required to file Form I-539 with USCIS and pay the associated fees.

That filing requirement is the critical shift. Under the current system, a Designated School Official at the student's university can approve most changes: a programme extension, a transfer, a shift from a master's to a PhD. Under the new framework, those decisions move from campus international offices to USCIS adjudicators — a bureaucracy that currently takes months to process even routine petitions.

The rule also introduces several restrictions that have alarmed university administrators across the country:

**Graduate students cannot change programmes.** An F-1 student enrolled in a computer science PhD who wants to switch to data science — at the same university — would be barred from doing so under the proposed rule. No exceptions.

**No lateral or reverse matriculation.** A student who completes a master's degree cannot pursue another master's in a different field. A PhD student cannot step down to a master's programme. The trajectory must be upward or out.

**The grace period shrinks from 60 to 30 days.** Currently, F-1 students have 60 days after programme completion to prepare for departure, apply for OPT, or change status. The proposed rule cuts that in half.

**Biometric collection for extensions.** Every I-539 extension filing will require fingerprints, photographs, and signature collection — a process that can itself take weeks to schedule at USCIS Application Support Centres.

## Why Indian students are most exposed

Indians constitute the second-largest international student population in the United States, behind China. But they are the single largest group on STEM OPT — the 24-month post-graduation work extension that has become the primary pipeline from American universities to American tech companies.

Under Duration of Status, a student finishing a four-year engineering degree could seamlessly transition to 12 months of OPT and then 24 months of STEM OPT without touching USCIS. Under the new rule, that student would need to file an I-539 extension at the four-year mark, wait for USCIS approval, and only then begin post-graduation work authorisation.

The risk is not theoretical. USCIS processing times for I-539 applications currently average four to eight months. A student whose four-year admission expires in May and whose OPT doesn't start until June could fall out of status during the gap — even if every filing was submitted on time.

"The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," said Danielle Goldman, co-founder and CEO of Build, an immigration technology company.

## The pipeline at stake

The OPT-to-H-1B pipeline has been the primary legal pathway for Indian engineers, data scientists, and AI researchers to enter the American workforce. Anything that introduces friction into that pipeline — processing delays, filing fees, programme-change restrictions — pushes talent toward Canada, the UK, Germany, and Australia, all of which have streamlined their own skilled-migration systems in the past two years.

University administrators have been particularly vocal. Cornell, Yale, Carnegie Mellon, and Washington University have all published guidance urging students to submit public comments during the rulemaking process. The comment period for the proposed rule closed on September 29, 2025, and DHS is now working through what universities describe as a "substantial" volume of feedback.

## What happens next

The final rule is now at OMB, the last bureaucratic checkpoint before publication. OMB reviews typically take 30 to 90 days, though politically sensitive rules can sit longer — as the H-4 EAD rescission proposal demonstrates.

Once published, the rule takes effect on its stated date. There is no additional comment period for a final rule. Legal challenges are possible — universities and immigration advocacy groups have signalled interest — but a court injunction is not guaranteed.

For Indian students currently in the US, the immediate advice from international student offices is consistent: no action is required yet. The current D/S system remains in place until the final rule is published and its effective date arrives. But students planning to extend their programmes, change fields, or rely on OPT should understand that the rules governing those decisions are about to become slower, more expensive, and far less forgiving."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
