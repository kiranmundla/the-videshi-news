#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

# ----------------------------------------------------------------------------
# ARTICLE 1 — The $100,000 fee's messy afterlife: three circuits, no clean answer
# ----------------------------------------------------------------------------
body1 = """A Boston judge handed H-1B employers a win this month. He did not hand them certainty.

On June 8, U.S. District Judge Leo Sorokin vacated President Trump's $100,000 fee on new H-1B petitions, ruling that the charge amounted to an unauthorized tax that Congress never approved. "The Court finds that the Policy imposes a tax on H-1B petitions without the requisite delegation by Congress," he wrote. The vacatur was universal — it lifted the fee for every employer in the country, not just the 20 Democratic-led states that sued. For the Indian engineers who make up roughly three-quarters of H-1B approvals, it read like a reprieve.

The trouble is that Sorokin's ruling is one of three lawsuits pulling in different directions, and the Trump administration has already said it will appeal.

## Three courthouses, three answers

The legal map is now genuinely contradictory. In December, a federal judge in Washington, D.C., **upheld** the fee, finding it fell within the president's broad power to restrict the entry of foreign nationals. The U.S. Chamber of Commerce and the Association of American Universities appealed that loss, and the D.C. Circuit fast-tracked the case. Then came Sorokin's opposite ruling in Massachusetts. A third suit, filed in San Francisco by religious and labor groups, is still working its way through the Northern District of California.

That sets up the possibility of split decisions across three federal appellate circuits — the D.C. Circuit, the First Circuit, and eventually the Ninth. When circuits split, the dispute tends to climb toward the Supreme Court. None of this resolves quickly.

## What it means if you are Indian and waiting

The practical takeaway for diaspora workers is less cheerful than the headline. The fee, as written, was scheduled to expire on September 20, 2026 regardless of any court ruling — though the administration can extend it. So even a permanent legal victory may only matter for petitions filed in a narrow window, unless the policy returns in a new form.

And the fee was already doing its work before any judge ruled. DHS Secretary Markwayne Mullin told a Senate subcommittee in June that of roughly 286,000 H-1B applicants in fiscal 2026, more than 200,000 had paid the $100,000 charge — buying faster processing of about 15 days, against 7.5 months for everyone else. An earlier government filing had counted just 85 payments by mid-February. Read together, those numbers tell a story of deep-pocketed employers swallowing the cost while smaller sponsors, universities and staffing firms balked.

For an Indian worker, the employer's wallet is the variable that matters. A large tech company can absorb $100,000; a mid-tier consultancy often cannot. That is why the fee, even while contested, has been quietly reshaping which Indians get sponsored and by whom.

## The carve-outs already in play

The litigation has not been uniformly grim. A separate ruling spared H-1B physician applicants from the fee — a relief the American Association of Physicians of Indian Origin publicly welcomed, noting that International Medical Graduates, many of them Indian, staff rural and safety-net hospitals that could never have paid the surcharge. Cap-exempt employers such as universities and nonprofit research institutions sit in a similar zone of partial protection.

What no one can offer is a clean prediction. Immigration lawyers are advising employers to keep filing without assuming the fee is dead, because an appellate court could reinstate it, stay Sorokin's order, or let the policy lapse on its own in September only to see a successor rule appear.

## What's next

Watch three dates and one decision. The September 20 expiry; the D.C. Circuit's ruling on the Chamber's appeal; the government's promised appeal of Sorokin's order; and any move to extend or re-issue the fee. For Indian H-1B holders, the safest assumption is the least satisfying one: the $100,000 question is not settled, and a courtroom win in Boston does not mean the bill is gone for good."""

# ----------------------------------------------------------------------------
# ARTICLE 2 — USCIS: go home to get your green card
# ----------------------------------------------------------------------------
body2 = """For decades, the deal was simple: if you lived in the United States lawfully and your green card number came up, you filed your paperwork with USCIS and finished the process without leaving. That deal is now, officially, the exception rather than the rule.

In a policy memo issued late last week and reiterated on Friday, U.S. Citizenship and Immigration Services declared that adjustment of status — the procedure that lets someone already in the country obtain permanent residency without going home — will be treated as "an extraordinary form of relief," granted only in limited cases. The default is now consular processing: leave the United States, travel to a U.S. embassy in your home country, and apply from there.

"Consistent with long-standing immigration law and immigration court decisions, aliens seeking adjustment of status must do so through consular processing via the Department of State outside of the country," the agency said. Spokesman Zach Kahler framed it as restoring "the original intent of the law," adding that students, workers and tourists "are expected to leave the US after their authorised stay ends."

## Why this lands hardest on Indians

No diaspora is more exposed. India-born applicants sit at the back of the world's longest employment-based green card queues — waits that analysts measure not in years but in decades for EB-2 and EB-3. For most, the question is still theoretical, because their priority dates are nowhere near current. But for the subset whose dates are current, or who qualify under faster-moving categories like EB-1 or the EB-2 National Interest Waiver, the shift is immediate and personal.

The memo's reach extends to families. Spouses and children on H-4 dependent visas — many of whom have lived in the U.S. for years, with kids in American schools — now face the prospect of returning to India for consular interviews, a process that can stretch from months to years depending on appointment backlogs and administrative processing. The result is the risk of family separation built directly into the paperwork.

## Discretion is the real bombshell

The harder edge is not the location of the interview but the discretion the memo hands adjudicators. Officers are directed to weigh conduct "inconsistent with the purpose of the visa" and may deny applications on discretionary grounds even when an applicant meets every statutory requirement.

Ajay Jain Bhutoria, a former member of the President's Advisory Commission on Asian Americans, put it bluntly on X: "Meeting statutory eligibility is no longer enough." He warned that H-1B, H-4, L-1, L-2, B-1 and B-2 holders face "aggressive scrutiny," and that even dual-intent visas like the H-1B are vulnerable, with officers "ordered to audit your entire US history — any minor status gap or unauthorised work means a denial."

## A softer footnote, and a harder reality

USCIS has left itself room. After backlash, the agency said in May it would allow exceptions for applications showing an "economic benefit or otherwise in the national interest" — though it declined to define either phrase, leaving applicants to guess whether they qualify. The agency also argues that pushing cases to consulates "frees up limited USCIS resources" for naturalizations and other work.

The timing compounds the pain. The June visa bulletin moved sharply against Indians: EB-2 India retrogressed 10.4 months to September 2013, and EB-1 India slid 3.5 months to December 2022. A worker who leaves the country for a consular interview now does so into a system offering no fixed timetable for return — and with priority dates moving backward, fewer can even reach the front of the line to test the new rules.

## What to do now

If your priority date is current or close, this is the memo to discuss with a lawyer before traveling. For everyone else in the backlog, it is a warning shot: the path to a green card that millions of Indians assumed they could walk without leaving home has narrowed, and the room for an officer to say no has widened."""

# ----------------------------------------------------------------------------
# ARTICLE 3 — Yes you can job-hunt on a visitor visa. No, you can't start working.
# ----------------------------------------------------------------------------
body3 = """Amid a stream of bad immigration news, USCIS offered the diaspora a rare clarification this week — and, predictably, half the internet read it wrong.

In a series of posts, the agency confirmed that foreign nationals in B-1 or B-2 status — the business and tourist visitor categories — may legally search for a job and attend interviews while in the United States. "Searching for employment and interviewing for a position are permissible B-1 or B-2 activities," USCIS said. For laid-off tech workers and visitors weighing a move to the U.S., that sounds like an open door.

It is a door with a turnstile.

## The line between looking and working

The clarification rests on a distinction that immigration law has always drawn but that workers under stress often blur. Section 101(a)(15)(B) of the Immigration and Nationality Act defines B-1/B-2 status as temporary visits for business or pleasure — and explicitly bars admission "for the purpose of performing skilled or unskilled labor." Interviewing, networking and accepting an offer fall on the permissible side. Actually starting the job does not.

Before any new employment begins, USCIS said, "a petition and request for a change of status from B-1 or B-2 to an employment-authorized status must be approved, and the new status must take effect." If that change-of-status request is denied, or if the new petition requires consular notification, "the individual must depart the US and be admitted in an employment-authorized classification before beginning the new employment."

Translation: you can find the job here, but you may have to leave to legally start it.

## Why Indians should read the fine print

This matters disproportionately to Indian nationals for one reason — the H-1B layoff cycle. When an Indian tech worker loses a job, the clock starts on a 60-day grace period to find a new sponsor or change status. Some workers switch to B-2 status as a bridge while they hunt, and USCIS's clarification confirms that hunting itself is legal in that posture.

But lawyers are warning that the agency's broader 2026 posture cuts against complacency. Filing a Form I-539 to change from H-1B to B-2 within the grace period preserves authorized stay while the application is pending — but it does not guarantee approval. If the I-539 is denied after the grace period lapses, the worker can be treated as having fallen out of status, and unlawful presence begins to accrue, with consequences for re-entry and future benefits.

There is a subtler trap, too. Adjudicators have begun treating job-seeking activity as potential evidence of "preconceived intent" — the idea that a visitor secretly meant to work all along when they entered. The statute hasn't changed; USCIS's willingness to scrutinize has. Applicants are being told to build a clean legal argument for the change of status at the time of filing, in anticipation of Requests for Evidence.

## The practical playbook

For an Indian visitor or a between-jobs H-1B holder, the week's guidance nets out to a few rules. Interview freely — it is permitted. Do not begin any work, paid or unpaid, until a change of status is approved and in effect. File any I-539 well within your authorized stay, not at the edge of it. And assume that a change from visitor to worker status inside the country is harder to win in 2026 than it was even a year ago, with consular processing abroad increasingly the fallback the government prefers.

It is, in the end, a small piece of good news wrapped in a large caution. The right to look for work on a visitor visa was never really in doubt. The right to convert that search into a job, without leaving, is the part getting harder — and that is the part that decides whether an Indian professional gets to stay."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "An H-1B Win in Boston, an Appeal in Washington: Why the $100,000 Fee Fight Isn't Over",
        "subheadline": "A judge vacated Trump's six-figure H-1B charge nationwide. With three lawsuits in three circuits and a government appeal pending, Indian workers shouldn't bank the reprieve yet.",
        "slug": make_slug("h1b-100k-fee-three-circuits-appeal-sorokin-uncertainty-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians receive roughly three-quarters of H-1B visas, so whether the $100,000 fee survives appeal directly determines which Indian workers get sponsored and by which employers.",
        "tags": ["h1b", "uscis", "100k-fee", "immigration", "courts", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/trumps-100-000-h-1b-visa-application-fee-rejected-by-judge"},
            {"name": "Associated Press / Montana Public Radio", "url": "https://www.mtpr.org/2026-06-08/federal-judge-strikes-down-trumps-100000-fee-on-new-h-1b-visas"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/over-2-lakh-applicants-paid-for-faster-h-1b-visa-processing-in-fy2026-dhs-says/article69000000.ece"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36869355/pexels-photo-36869355.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A courthouse colonnade; federal courts in three circuits are now split over Trump's $100,000 H-1B fee",
        "image_attribution": "Pexels",
        "published_at": now,
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS to Green-Card Seekers: Go Home to Apply. For Indians, Home Is a Decade Away",
        "subheadline": "A new policy memo makes adjusting status inside the U.S. an 'extraordinary' exception and the default a consular interview abroad — with broad new discretion for officers to say no.",
        "slug": make_slug("uscis-adjustment-status-extraordinary-consular-processing-h4-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the longest employment-based green card backlogs in the world; forcing applicants and their H-4 families to process abroad risks months of family separation and adds officer discretion that can sink a qualified case.",
        "tags": ["uscis", "green-card", "adjustment-of-status", "consular-processing", "h4", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/us-asks-foreign-nationals-to-apply-for-green-cards-from-home-country/"},
            {"name": "Nolo - 2026 Immigration Legal Updates", "url": "https://www.nolo.com/legal-encyclopedia/2026-immigration-legal-updates.html"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/uscis-limits-adjustment-of-status-new-2026-policy-impact/"},
            {"name": "USCIS", "url": "https://www.uscis.gov/"}
        ]),
        "score_total": 86,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center; the agency now treats in-country adjustment of status as 'extraordinary' relief",
        "image_attribution": "Wikimedia Commons",
        "published_at": now,
        "body": body2,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Says You Can Job-Hunt on a Tourist Visa. Starting the Job Is the Hard Part",
        "subheadline": "The agency confirmed that interviewing while in B-1/B-2 status is legal — but converting that search into actual work, without leaving the country, has quietly gotten harder in 2026.",
        "slug": make_slug("uscis-b1-b2-tourist-visa-job-search-change-of-status-india-h1b"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Laid-off Indian H-1B workers often switch to B-2 status to job-hunt during their 60-day grace period; the clarification confirms searching is legal, but tightening change-of-status scrutiny decides whether they can stay.",
        "tags": ["uscis", "b1-b2", "visitor-visa", "change-of-status", "h1b", "layoffs", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/us-allows-applying-for-jobs-even-on-temporary-visa/"},
            {"name": "Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/h-1b-to-b-1b-2-change-of-status-after-termination"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/one-can-apply-for-job-give-interviews-while-on-tourist-or-business-visa-in-us-federal-agency/article00000000.ece"},
            {"name": "USCIS B-1 Temporary Business Visitor", "url": "https://www.uscis.gov/working-in-the-united-states/temporary-visitors-for-business/b-1-temporary-business-visitor"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A U.S. visa application with passport; USCIS says job interviews are allowed on visitor visas but work requires an approved status change",
        "image_attribution": "Pexels",
        "published_at": now,
        "body": body3,
    },
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words, score {art['score_total']})")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
