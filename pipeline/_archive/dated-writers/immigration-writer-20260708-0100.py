#!/usr/bin/env python3
"""Immigration writer — July 8, 2026 01:00 PDT run."""

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

# ─────────────────────────────────────────────────────────
# ARTICLE 1: The Consular Notification Trap
# ─────────────────────────────────────────────────────────

article1_body = """Your H-1B petition came back approved. The I-797 notice is sitting in your inbox, and your employer's HR department has already updated your start date. There is just one line at the bottom of the approval that changes everything: *Consular notification required.*

Those three words mean USCIS has approved the job and the worker — but it does not believe you maintained valid immigration status inside the United States. You cannot activate the visa from where you are. You must leave the country, fly to India, schedule an appointment at a U.S. consulate, sit for an interview, and get a fresh H-1B stamp in your passport before you can re-enter and start working.

## A Quiet Trend Becoming a Loud Problem

Immigration attorneys across the country are reporting a sharp increase in H-1B approvals arriving with consular notification flags. The pattern typically looks the same: a worker is laid off, files a change of status to B-2 (tourist visa) to bridge the gap, then finds a new employer who files a new H-1B petition. USCIS questions the B-2 change of status — sometimes denying the I-539 outright, sometimes just noting that the worker's maintenance of status is uncertain — and issues the H-1B approval with the consular notification condition attached.

"In my 15 years of practice, I've never seen a more treacherous time to port from one H-1B job to another," immigration attorney Loren Locke of Locke Immigration Law said in a recent analysis. The scenario he described is one that thousands of Indian tech workers now face: an approved petition that exists only on paper until they can get stamped at a consulate halfway around the world.

## Why India Makes This Uniquely Painful

For Indian nationals, the consular notification is not merely an inconvenience. It is a potential career-ending delay.

U.S. consulates in India have been operating under severe backlogs since the State Department implemented its Online Presence Review policy in late 2025, which requires officers to examine the social media profiles and digital footprints of every H-1B and H-4 applicant. The result was mass rescheduling of visa appointments across Hyderabad, Chennai, Mumbai, and New Delhi — interviews originally scheduled for December 2025 were pushed to March, April, and even June 2026.

As of mid-2026, most Indian consulates are booking H-1B interview slots 10 to 12 months in advance. For a worker who receives a consular notification today, the realistic timeline to get stamped and re-enter the U.S. stretches well into 2027.

MIT's International Scholars Office issued a stark advisory: any H-1B holder with an expired visa who travels for stamping is "putting themselves at risk of being stranded abroad for four to six months." The advisory urged H-1B employees to consult with immigration counsel before any international travel.

## The Employer's Impossible Calculus

The burden does not fall on the worker alone. The employer who filed the H-1B petition now faces a question that has no good answer: wait a year for someone who has not started yet, or withdraw the offer and hire domestically?

If the petition was filed as a new cap-subject H-1B, the employer may also be on the hook for the $100,000 supplemental fee that took effect in September 2025 — a fee that a federal judge in Boston ruled unlawful in June 2026 but that remains in effect in at least one circuit pending appeal. Paying six figures for a worker who cannot show up for months is a hard sell to any CFO.

The practical result is that some employers are quietly rescinding offers when they see the consular notification flag. Others are keeping the position open but asking the worker to work remotely from India — a workaround that raises its own thicket of tax, employment law, and export control issues.

## The Layoff-to-Limbo Pipeline

The workers most vulnerable to the consular notification trap are the same ones who were already in the most precarious position: those who lost their jobs in the ongoing wave of tech layoffs.

When Microsoft cut 4,800 positions last week, every H-1B holder among them started a 60-day clock — find a new employer willing to file an H-1B transfer or leave the country. Many will find sponsors. But if their change of status during the gap period draws USCIS scrutiny, the approval they worked so hard to secure could come with a consular notification that sends them back to India for months.

The chain reaction is brutal. A layoff leads to a status gap. The gap leads to a B-2 bridge. The bridge leads to a consular notification. The notification leads to a year-long wait at an Indian consulate. And the wait leads to a job that may no longer exist when the stamp finally arrives.

## What You Can Do

Immigration attorneys recommend several steps for H-1B workers navigating this landscape:

**Avoid status gaps if possible.** If you are laid off, the 60-day grace period is your window. Filing a new H-1B transfer petition immediately — before your status formally expires — reduces the risk of a consular notification flag.

**Do not withdraw a pending B-2 prematurely.** If you have filed a change of status to B-2, withdrawing it before a new H-1B is filed can leave you without any valid status argument.

**Consider premium processing.** The 15-day premium processing option for H-1B petitions, while expensive, gives you an answer before your status situation deteriorates further.

**Talk to a lawyer before travelling.** If your H-1B comes back with a consular notification, do not book a flight to India without understanding the full timeline. Consulate wait times, administrative processing, and the social media review can extend the process far beyond the interview itself.

For the thousands of Indian tech workers whose American careers depend on a stamp in a passport, the message from USCIS is clear: an approval is not the end of the process. It may only be the beginning of a much longer one."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your H-1B Got Approved. Good Luck Actually Using It",
    "subheadline": "USCIS is increasingly flagging H-1B approvals with 'consular notification' — forcing Indian workers to fly home for visa stamping at consulates backed up 10 to 12 months. An approved petition no longer means you can work.",
    "slug": make_slug("h1b-approved-consular-notification-trap-indian-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers who lose jobs and change status face a unique trap: approved petitions that require consular stamping in India, where wait times now exceed 10 months due to social media vetting requirements.",
    "tags": ["h1b", "uscis", "consular-notification", "visa-stamping", "india-consulate", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Locke Immigration Law", "url": "https://lockeimmigration.com"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/stricter-vetting-slower-processing-how-new-immigration-form-changes-are-reshaping-2026-07-07/"},
        {"name": "MIT International Scholars Office", "url": "https://iso.mit.edu"},
        {"name": "Baker McKenzie InsightPlus", "url": "https://insightplus.bakermckenzie.com"},
        {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/US_Embassy_New_Delhi.jpg/1280px-US_Embassy_New_Delhi.jpg",
    "image_caption": "The U.S. Embassy in New Delhi, where H-1B visa applicants face wait times stretching beyond 10 months",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ─────────────────────────────────────────────────────────
# ARTICLE 2: Canada Recruiting Indian Students
# ─────────────────────────────────────────────────────────

article2_body = """For two decades, the calculus was simple. An ambitious Indian student with strong test scores and family savings would choose an American university, survive two winters in the Midwest, land an OPT position at a tech company, enter the H-1B lottery, and — with luck and patience measured in years — settle permanently. It was not easy, but the pathway was legible.

That pathway is now breaking apart, one policy change at a time. And Canada, which has spent years building an alternative, is making sure Indian students know it.

## "The Best Time to Apply"

In a statement that would have been unremarkable five years ago but lands differently in 2026, Canadian High Commissioner to India Chris Cooter described the current moment as the best time for Indian students to apply to Canadian institutions. Current application volumes, he said, remain well below Canada's 2026 intake capacity.

The timing of the message is no accident. It arrives as the United States has systematically raised every barrier between an Indian student and a career in America.

## The Numbers That Changed the Calculation

The scale of the American pullback is visible in a single data point: F-1 visa issuances to Indian nationals fell 78 per cent in the summer of 2025, according to U.S. State Department data analysed by ICEF Monitor. That is not a rounding error or a seasonal blip. It is a structural collapse in the pipeline that fed hundreds of thousands of Indian students into American universities and, eventually, into American companies.

The causes are layered. Mandatory in-person interviews — with no dropbox or age-based exemptions — have created months-long backlogs at Indian consulates. The new social media vetting requirement means that even approved applicants face extended administrative processing. And the uncertainty hanging over the OPT programme, which allows graduates to work in their field of study for up to three years after earning a STEM degree, has made the return on a $60,000-to-$100,000 American education harder to justify.

## Duration of Status: The Rule That Would Change Everything

On May 5, 2026, the Department of Homeland Security proposed eliminating the "Duration of Status" framework for F-1 student visas. Under the current system, international students can remain in the United States as long as they maintain their student status. The proposed rule would replace that with a fixed admission period of up to four years, after which students would need USCIS approval to remain — even if their programme is not yet complete.

Danielle Goldman, co-founder and CEO of immigration platform Build, called the change transformative. "The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," she said.

The implications cascade. Students who fail the H-1B lottery — which, under the new wage-weighted selection system, now favours higher-paid applicants — would lose access to the Day 1 CPT programmes that many have relied on as a fallback. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" Goldman warned.

The grace period after a student's status ends would also shrink, from 60 days to 30, leaving even less time to find sponsorship or arrange alternative visa options.

## What Canada Built While America Was Closing

Canada's pitch to Indian students is not just about being less hostile. The country has spent a decade building immigration infrastructure designed to convert students into permanent residents.

The Post-Graduation Work Permit programme gives graduates of Canadian institutions work permits lasting up to three years — no lottery, no employer sponsorship required at the initial stage. Express Entry, Canada's points-based permanent residence system, awards additional points for Canadian education and work experience, creating a predictable pathway from student to resident that the American system has never offered.

Ottawa did impose its own restrictions in recent years, capping international student visas and tightening rules around predatory institutions. But the reforms were designed to protect institutional quality, not to reduce the number of qualified applicants. The cap has not been reached for 2026.

The United Kingdom, Germany, and Australia have made similar plays. Britain's Graduate Route visa offers two years of post-study work rights. Germany charges negligible tuition at public universities. Australia's post-study work visa extends up to six years for PhD holders.

## The Talent Equation

The stakes extend beyond individual careers. International students — led by Indians — contribute an estimated $33 billion annually to the U.S. economy, according to NAFSA. They account for a disproportionate share of the American AI and machine learning talent pool. Every student who chooses Toronto or Waterloo over Stanford or Georgia Tech takes that economic contribution with them.

Goldman was blunt about the downstream effects. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said. "The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions."

For the Indian student weighing options in the summer of 2026, the American dream has not disappeared. But it now comes with a price tag — measured in fees, uncertainty, and years of bureaucratic limbo — that Canada and its peers are determined to undercut."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Canada Just Made Its Pitch to Indian Students. The Numbers Suggest They Are Listening",
    "subheadline": "F-1 visa grants to Indian nationals fell 78 per cent in a single summer. With the Duration of Status rule under threat and OPT's future uncertain, Canada's High Commissioner says now is the best time to apply.",
    "slug": make_slug("canada-recruits-indian-students-us-f1-visa-collapse"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families spending $60,000-$100,000 on American degrees face a broken F-1 to H-1B pipeline — while Canada offers a predictable path from student to permanent resident with no lottery and no six-figure fees.",
    "tags": ["f1-visa", "indian-students", "canada", "opt", "duration-of-status", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/canada-visa-alert-why-indian-students-should-apply-now/"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com"},
        {"name": "The Indian Eye", "url": "https://www.theindianeye.com"},
        {"name": "Build (Danielle Goldman)", "url": "https://www.build.co"},
        {"name": "NAFSA", "url": "https://www.nafsa.org"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Students walking on a university campus — a scene that Indian families are increasingly picturing in Toronto and Waterloo rather than Boston and Austin",
    "image_attribution": "Pexels",
    "body": article2_body
}

# ─────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
