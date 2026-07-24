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

# ---------------------------------------------------------------------------
# ARTICLE 1 — USCIS adjustment-of-status memo (file from home country)
# ---------------------------------------------------------------------------
art1_body = """The green card has always been the prize at the end of the H-1B marathon. A new policy memo from U.S. Citizenship and Immigration Services, issued Friday, just made the last lap a great deal more uncertain — and for Indians, who hold the longest waits of anyone, the timing could hardly be worse.

The memo reframes a routine step that hundreds of thousands of skilled workers count on. Adjustment of status — the process by which someone already living legally in the United States converts to permanent residency without leaving — will now be treated as "an extraordinary form of relief," granted only in limited cases. The default, USCIS says, is that applicants must instead return to their home country and complete the immigrant visa through a U.S. consulate abroad.

https://x.com/USCIS

"From now on, an alien who is in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances," agency spokesman Zach Kahler said in a statement, describing the change as a return "to the original intent of the law."

### What actually changed

For decades, the system has worked the other way around. A worker on an H-1B whose priority date became current would file Form I-485 and adjust status from inside the country, often without a single trip abroad. Consular processing — flying home, sitting for an interview, waiting for a stamp — was the path for those outside the United States, not those already in it.

The memo does not repeal the statute that allows adjustment of status; only Congress can do that. What it changes is how officers exercise discretion. They are now directed to treat in-country adjustment as the exception and to weigh "all relevant factors" case by case. In a follow-up clarification, Kahler said applicants who provide an "economic benefit" or serve the "national interest" could still complete processing inside the country. Nobody yet knows how those terms will be defined, who decides, or how consistently.

### Why this lands hardest on Indians

The cruelty of the change is in the arithmetic. Indians dominate the employment-based green card backlog — a queue of more than 1.8 million people in which an EB-2 or EB-3 applicant from India can wait decades. Many of those workers have spent ten or fifteen years building lives here: mortgages, U.S.-born children, careers anchored to a single sponsoring employer.

Telling that population to "go home to apply" is not a minor procedural tweak. It means surrendering the certainty of adjusting from within for the gamble of a consular interview in Mumbai, Hyderabad or Delhi — the same consulates already booking appointments 10 to 12 months out, where wait times in Kolkata have stretched to 126 days for routine stamping. A worker who leaves to file abroad could be stranded for months, their U.S. job and H-1B status hanging on a slot that may not materialize.

There is a second trap. Once outside the country, an applicant who has accrued any unlawful presence — even inadvertently — can be hit with three- or ten-year reentry bars that simply do not apply to those who stay and adjust inside the United States. Adjustment of status was, in part, designed to shield long-resident workers from exactly that risk. Stripping it away as the default reintroduces a danger most Indian families thought they had left behind.

### The fine print, and what to watch

For now, this is guidance, not a regulation that has gone through notice and comment — which makes it both faster to deploy and more vulnerable to legal challenge. Immigration attorneys are already questioning whether USCIS can narrow a statutory benefit by memo, and litigation is likely.

The practical advice from practitioners is blunt: anyone with a current priority date and a pending or imminent I-485 should talk to a lawyer before making travel plans, and file from within the country while that door is demonstrably still open. The "extraordinary circumstances" carve-out and the "economic benefit" exception will be tested in the coming weeks, and how USCIS field offices apply them — generously or grudgingly — will determine whether this memo is a paperwork nuisance or a wall.

For the Indian diaspora, it is one more reminder that in 2026 the rules of permanence keep moving, and the people with the most to lose are the ones who have waited the longest."""

# ---------------------------------------------------------------------------
# ARTICLE 2 — F-1 Duration of Status final rule clears OMB
# ---------------------------------------------------------------------------
art2_body = """The single most consequential rule for Indian students in America just cleared its last bureaucratic hurdle. The White House Office of Management and Budget has finished its review of a Department of Homeland Security regulation that would scrap "duration of status" for F-1 student visas — the open-ended framework that has, for forty years, let international students stay as long as they remain enrolled and compliant.

Clearing OMB is the final step before publication. The rule can now appear in the Federal Register at any time, and once it does, the way 360,000 Indian students manage their lives in the United States changes fundamentally.

### From open-ended to a four-year clock

Under the current system, an F-1 student is admitted for "duration of status" — shorthand for "however long your program legitimately takes." A PhD that runs six years, a master's that stretches because of a research delay, a transition into Optional Practical Training: all of it has happened without students having to re-petition the government for more time.

The new rule, as proposed last year, replaces that with a fixed admission period of up to four years. Anything beyond it — finishing a longer degree, starting OPT, even certain program changes — would require a formal extension application filed with USCIS. The exact contours of the final version are not yet public; the draft also barred undergraduates from switching majors or education levels in their first year and prohibited graduate students from changing programs at all.

### Why Indians are the most exposed cohort

Indians are now the largest group of international students in the United States, roughly 31 percent of the 1.1 million foreign students on American campuses, according to the latest Open Doors report. They are also concentrated in exactly the programs the four-year clock punishes: multi-year graduate degrees, doctoral research, and the OPT-to-H-1B pipeline that is the whole point of studying in America for many families who spend a fortune to send a child abroad.

Immigration attorney Rajiv S. Khanna has warned that the rule could create work-authorization gaps for students on OPT whose admission period expires while an extension sits pending at USCIS — even if they are holding a valid work permit. In plain terms: a graduate could be legally employed one day and, through no fault of their own, out of status the next, simply because a government queue ran long.

There is a sharper edge. Today, an F-1 student begins accruing "unlawful presence" only when USCIS or a judge formally finds a status violation. If the rule is finalized as drafted, the clock would start the moment the fixed admission period expires. Cross 180 days and a three-year reentry bar attaches; cross a year and it becomes ten. A paperwork delay could quietly convert a diligent student into someone barred from the country for a decade.

### The grace-period squeeze, stacked on top

The Duration of Status rule does not arrive in isolation. DHS has separately proposed cutting the post-graduation grace period for F-1 students from 60 days to 30 — halving the window in which a graduate must find an employer willing to sponsor an H-1B or pivot to another status. For Indian graduates who already face brutal odds in the H-1B lottery, a 30-day cliff leaves almost no room to maneuver. The "Day 1 CPT" workaround that some have used to stay enrolled and employed between lottery attempts would also narrow sharply if status becomes a fixed, USCIS-policed term.

### What students should do now

Nothing changes until the rule is published, and a transition period is likely. But the direction is set. Advisers are telling students to map their program end dates against any planned OPT or STEM OPT extensions, to file renewals as early as the rules allow rather than at the deadline, and to keep meticulous records of enrollment and status.

For a community that has treated an American degree as the surest on-ramp to a career and, eventually, a green card, the message is sobering. The on-ramp still exists — but it now comes with a meter running, and the penalty for a delay you did not cause has rarely been steeper."""

# ---------------------------------------------------------------------------
# ARTICLE 3 — End of automatic EAD extensions
# ---------------------------------------------------------------------------
art3_body = """For the spouses of H-1B workers, the asylum-pending, and the long line of Indians inching through the green card backlog, the work permit is not a convenience — it is the difference between a paycheck and a pink slip. In 2026, that document has quietly become a great deal more fragile, and many of the people who depend on it have not noticed until it is nearly too late.

The change that matters most is the unwinding of automatic extensions. For years, when a holder of an Employment Authorization Document filed a timely renewal, federal rules granted an automatic extension — most recently up to 540 days — so the worker could keep their job while USCIS processed the paperwork. That cushion is being stripped away across a number of categories, and validity periods for some classifications have been cut to as little as 18 months.

### The expiration gap

Without an automatic extension, the math is unforgiving. If your card expires before the renewal is approved, you are not authorized to work — full stop. Even with a timely-filed renewal sitting at USCIS, an expired card means an employer must re-verify your eligibility, and if they cannot, they are legally required to pull you off the job.

"This is not a technicality," the NPZ Law Group warned clients this week. "We have seen clients lose income and employers face compliance headaches because a renewal was filed on time but USCIS processing ran long."

The agency's own production has not helped. USCIS has confirmed delays in physically issuing both EADs and green cards, blaming system maintenance at its primary card-production facility and telling applicants to expect an extra two to three weeks beyond normal times — on top of adjudication queues that already run long.

### Who in the diaspora this hits

Three groups of Indians feel this most acutely.

First, H-4 spouses. Tens of thousands of them — overwhelmingly Indian women married to H-1B holders — work in the United States on H-4 EADs. The category has been under existential threat for years, with a rescission rule sitting at OMB and no clear timeline. Layer the loss of automatic extensions on top of that uncertainty, and a single processing delay can knock a household down to one income overnight.

Second, the backlogged green card applicants. Indians with approved I-140 petitions and pending adjustment-of-status applications rely on EADs and advance parole to work and travel during waits that stretch a decade or more. Each renewal cycle is now a fresh chance to fall into the expiration gap.

Third, anyone whose status is already precarious. The asylum-based EAD has essentially been shut to new applicants after processing times blew past 1,200 days, and a proposed rule still open for comment would add criminal-history bars and biometrics requirements for several humanitarian categories.

### The cruel irony

All of this lands at the same moment a White House advisory commission on Asian American, Native Hawaiian and Pacific Islander affairs has recommended the opposite approach — urging USCIS to grant EADs and travel documents to anyone with an approved EB-1, EB-2 or EB-3 petition who has waited five or more years in the backlog, whether or not they have filed for adjustment of status. The recommendation, championed by commissioner Ajay Bhutoria, is a tacit admission that the backlog has trapped skilled Indians in jobs and positions far below their potential, breeding exactly the insecurity the EAD was meant to relieve.

But a commission recommendation is not a rule. What is actually in force in 2026 cuts the other way: shorter validity, no automatic extensions, slower card production.

### The practical takeaway

Immigration lawyers have converged on one piece of advice that costs nothing: file early. Know your exact expiration date, file the renewal at the first moment regulations allow rather than waiting for the final 90-day window, and do not assume an old automatic-extension rule still covers your category — many no longer do.

For a diaspora that has organized its financial life around the quiet reliability of a plastic work card, 2026 is a year to treat that card as anything but reliable. The paycheck now depends on a deadline most people did not know had moved."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Just Told Green-Card Seekers to Go Home to Apply. Indians Wait the Longest to Hear It",
        "subheadline": "A new policy memo reclasses in-country adjustment of status as 'extraordinary relief,' pushing applicants toward consular processing abroad — and reopening reentry-bar risks Indian families thought were behind them.",
        "slug": make_slug("uscis-adjustment-status-extraordinary-relief-consular-processing-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians dominate the 1.8-million-strong employment green card backlog, so a memo pushing applicants to file from home consulates already booked a year out hits them hardest — and revives three- and ten-year reentry bars that adjustment of status was designed to avoid.",
        "tags": ["green card", "uscis", "adjustment of status", "consular processing", "h1b", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye — US asks foreign nationals to apply for Green Cards from home country", "url": "https://theindianeye.com/"},
            {"name": "The Hindu BusinessLine — New USCIS policy could force H-1Bs seeking Green Cards to apply from home countries", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Livemint — US embassy alerts H-1B, H-4 applicants amid visa renewal delays", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center, where in-country immigration filings are processed",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Open-Ended Student Visa Is Ending. India's 360,000 Students Are the Most Exposed",
        "subheadline": "A DHS rule replacing F-1 'duration of status' with a fixed four-year clock has cleared the White House and can be published any day — putting graduate degrees, OPT, and a decade-long reentry bar all on the same timer.",
        "slug": make_slug("f1-duration-of-status-final-rule-omb-four-year-india-students-opt"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are now 31% of all international students in the US and cluster in the multi-year graduate programs and OPT pipeline the four-year admission clock punishes — a pending-extension delay could trigger unlawful presence and a three- or ten-year reentry bar through no fault of the student.",
        "tags": ["f1 visa", "duration of status", "opt", "students", "dhs", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law — Rule Limiting Foreign Students in US Cleared by White House", "url": "https://news.bloomberglaw.com/"},
            {"name": "NAICU — Regulations Clear OMB, Await Final Publication", "url": "https://www.naicu.edu/"},
            {"name": "USA Today / The Indian Eye — Flexibility for international students likely to be curbed", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International students walking on a university campus",
        "image_attribution": "Pexels",
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Work Permit Indians Quietly Depend On Just Got a Lot More Fragile",
        "subheadline": "USCIS is unwinding the automatic EAD extension and cutting validity periods, even as card production slows — leaving H-4 spouses and backlogged green-card applicants one processing delay away from losing the right to work.",
        "slug": make_slug("ead-automatic-extension-ends-validity-cut-h4-spouses-india-backlog"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "H-4 spouses (overwhelmingly Indian women) and Indians stuck in the decade-long green card backlog rely on EADs to work; ending automatic extensions and slowing card production means a single USCIS delay can cut a household to one income overnight.",
        "tags": ["ead", "h4 ead", "work permit", "uscis", "green card backlog", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NPZ Law Group / VisaServe — What EAD Holders Need to Know in 2026", "url": "https://www.visaserve.com/"},
            {"name": "Fragomen — USCIS Confirms Delays in Issuance of EADs and Green Cards", "url": "https://www.fragomen.com/"},
            {"name": "LatestLY — White House Commission Recommends EAD at Early Stage of Green Card Process", "url": "https://www.latestly.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/USCIS_EAD_card.jpg/1280px-USCIS_EAD_card.jpg",
        "image_caption": "A USCIS-issued Employment Authorization Document (work permit)",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"-- {art['slug']} :: {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
