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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Skip the Visa Line for $750: Washington Puts a Price Tag on the Appointment Itself",
        "subheadline": "From July 1, a six-month pilot lets B1/B2 applicants buy a guaranteed interview within 10 business days — but the slot is all the money buys, and India may not even make the list.",
        "slug": make_slug("us-expedited-visa-interview-750-fee-pilot-b1-b2-india-appointment"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indians who routinely wait close to a year for a US visitor-visa slot, a paid fast lane is tempting — but it only buys a faster interview, not a faster decision, and Washington has not yet said whether India's overstretched posts are in the trial.",
        "tags": ["us-visa", "b1-b2", "visa-appointment", "consular", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inc. / Fast Company", "url": "https://www.inc.com/maria-jose-gutierrez-chavez/a-major-us-travel-rule-change-starts-july-1-with-a-750-price.html"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/us-to-offer-faster-visa-appointments-within-10-days-for-an-additional-fee"},
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport held open at a US visa application desk, the document at the centre of every consular appointment.",
        "image_attribution": "Pexels",
        "body": """The United States has found a new thing to sell: your place in the queue.

From July 1, the State Department will run a six-month pilot that lets applicants for B1 and B2 visitor visas pay an extra $750 to lock in an interview appointment within 10 business days. Stacked on top of the standard $185 application fee, the all-in cost comes to $935 — roughly four times what a visa interview costs today. The trial runs through December 31, after which officials will decide whether to keep it, change it, or quietly let it die.

For most of the world this is a curiosity. For Indians, it lands on the single rawest nerve in the whole visa system: the wait for an appointment.

## The wait, not the visa, is the wall

Indians have spent the past three years staring at appointment calendars that stretch past the horizon. Visitor-visa wait times at Indian posts have repeatedly run close to a year, and the dropbox interview-waiver channel — long the escape hatch that spared experienced travellers a fresh interview — has been narrowing, pushing even toddlers and retirees back into the in-person queue. A grandparent trying to reach a daughter's delivery, a father hoping to attend a graduation, an engineer with a fortnight's notice for a client meeting: for all of them the binding constraint has never been the $185. It has been the months.

That is exactly what the pilot targets. The State Department's own framing is unusually candid: the fee, it says, will "reduce the strain on consular resources by bypassing both the requirement for the applicant to justify his or her need for an expedited interview appointment and the requirement that consular staff review each expedited request." Translation: rather than have officers adjudicate who deserves an emergency slot, Washington will let the market sort it out. Pay the premium, skip the justification.

## What $750 does not buy

Here is the catch, and it is a large one. The money buys an interview, not an outcome. Background checks, administrative processing, and the final yes-or-no will run on exactly the same timeline as before. An applicant can reach the window in 10 business days and still wait weeks in "administrative review" — or be refused outright under Section 214(b) for failing to prove non-immigrant intent. The $750 is non-refundable, and a refusal does not return it.

This matters more for Indian applicants than most, because Indian visitor-visa refusals are not rare, and a fast-tracked interview does nothing to strengthen a weak case. For families with genuine emergencies and the means to pay, the pilot is a real gift. For everyone else it risks becoming a regressive toll — a system in which the speed of seeing an American official is openly indexed to the size of one's wallet.

## And India may not even be in it

The most important detail is the one Washington has so far withheld. The list of participating embassies and consulates has not been published, and there is no guarantee that India's missions — among the most backlogged on earth — are included at launch. A pilot designed to relieve consular strain might sensibly start where strain is worst; it might equally start somewhere quieter to test the plumbing. Until the State Department names the posts, Indian applicants should treat the $750 lane as a possibility, not a plan.

## What to do before July 1

A few practical notes for the diaspora. First, watch for the post list rather than the headline; the programme is meaningless to you if Mumbai, Delhi, Chennai, Hyderabad and Kolkata are not on it. Second, remember that the existing applicant-requested expedite route — free, but requiring you to document genuine urgency to a consular manager — is not going away, and remains the better option for those with a documented emergency and no spare $750. Third, do not mistake speed for safety: if your case is borderline on ties to India or purpose of travel, paying to be interviewed sooner only brings the refusal forward.

For a community that has learned to plan trips home around a visa calendar rather than a family calendar, the pilot is a telling sign of the times. The American door is not exactly opening wider. It is simply adding an express turnstile — and charging admission.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Laid Off on H-1B? USCIS Says You Can Job-Hunt on a Tourist Visa. Lawyers Say Don't Bet On It",
        "subheadline": "As AI-driven cuts sweep Meta, Amazon and Oracle, the official 60-day grace-period playbook collides with a quiet rise in denials for the very pathway it recommends.",
        "slug": make_slug("h1b-layoff-60-day-grace-b2-job-search-scrutiny-indians-tech-cuts"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the largest share of H-1B visas and dominate the tech ranks being thinned by AI restructuring, so the gap between USCIS's reassuring guidance and immigration lawyers' warnings about B-2 'visitor' filings hits Indian families squarely.",
        "tags": ["h1b", "layoffs", "60-day-grace", "b2-visa", "uscis", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com/us-allows-applying-for-jobs-even-on-temporary-visa/"},
            {"name": "People Matters", "url": "https://www.peoplematters.in/news/talent-management/indian-h-1b-workers-caught-in-fresh-wave-of-meta-amazon-tech-layoffs"},
            {"name": "Lexology", "url": "https://www.lexology.com/library/detail.aspx?g=h1b-notices-to-appear-grace-period"},
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061949/pexels-photo-8061949.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US visa application and passport on a desk — the paperwork that decides whether a laid-off worker can stay.",
        "image_attribution": "Pexels",
        "body": """When the layoff email arrives, the first thing an Indian engineer on an H-1B counts is not severance weeks. It is days. Sixty of them.

That is the discretionary grace period US immigration rules grant most work-visa holders after a job ends — 60 days, or until the I-94 expires, whichever comes first, to find a new sponsor, change status, or leave. With AI-driven restructuring thinning the ranks at Meta, Amazon, Oracle and LinkedIn — Layoffs.fyi counts more than 110,000 tech job losses across some 144 companies this year — that clock is now ticking for thousands of Indian families at once. They hold the largest share of H-1B visas, which means they sit at the centre of every cut.

## The official line is reassuring

US Citizenship and Immigration Services has been at pains to remind laid-off workers that 60 days is not a dead end. Its guidance, reiterated in a public note, lists four ways to extend an authorised stay if you act inside the window: file to change your non-immigrant status, file to adjust status, request a "compelling circumstances" work permit, or become the beneficiary of a non-frivolous petition from a new employer. And — the line that travels fastest in WhatsApp groups — the agency says you may look for a job and sit interviews while in B-1 or B-2 visitor status. "Searching for employment and interviewing for a position are permissible B-1 or B-2 activities," USCIS has stated.

For a worker with a mortgage in Bellevue, a spouse on H-4 and a child in third grade, switching to a six-month B-2 to buy time looks like the sensible move. It is also the move immigration lawyers are increasingly nervous about.

## The practice is anything but

Attorneys report a rising tide of Requests for Evidence, Notices of Intent to Deny, and outright refusals on exactly these layoff-driven B-2 filings. Some adjudicators now take the position that job-hunting is not a permissible visitor activity at all — squarely contradicting the agency's own public guidance. Worse, a few officers have argued that filing a later H-1B petition is itself evidence that the original B-2 request lacked genuine visitor intent, even though US law has long allowed people's plans to change and intent is supposed to be judged at the moment of filing.

The risk does not stop at a denied application. In a trend that began last year and has not reversed, some laid-off H-1B holders have been issued Notices to Appear — the document that opens removal proceedings — despite being inside the 60-day grace period. The grace period is discretionary, and USCIS may shorten or eliminate it. For Indian workers, who are over-represented among the laid off and under-protected by decades-long green-card backlogs that a job loss can wipe clean, the margin for a misstep has narrowed to almost nothing.

## How the grace period actually works

A few facts worth burning into memory. The 60 days run from your last day of employment, not the last day of severance pay — so a generous package that keeps money flowing for sixteen weeks does nothing to slow the immigration clock. An H-1B transfer must be filed, not merely promised; an offer letter buys no time. Premium processing can turn a transfer around in roughly 15 business days, which is why speed matters more than waiting for the "perfect" role. And working — paid or unpaid, freelance or favour — outside an approved petition can permanently poison future filings.

## What this means for Indian families

The cruel arithmetic is that the people best placed to use the official escape routes are often the worst placed to absorb a denial. A US citizen can pause and job-hunt slowly. An Indian H-1B holder cannot; a single miscalculation can convert a layoff into unlawful presence, an NTA, and years of future-visa trouble.

The practical playbook for now: treat the 60-day clock as starting the day after termination, not later; line up an H-1B transfer and file it with premium processing rather than relying on a B-2 stopgap; if you must change to visitor status, document a genuine temporary purpose, proof of funds and an intent to depart, and assume an officer will read it sceptically; and speak to an immigration attorney in the first week, not the seventh.

USCIS says the door stays open for 60 days. The fine print, written by adjudicators rather than press notes, increasingly says: prove it.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora's Quiet Backstop Was the Courts. The Supreme Court Just Showed Its Limits",
        "subheadline": "Two 6-3 rulings on June 25 handed the executive sweeping deference on immigration — a warning for Indians who have been counting on judges to undo the $100,000 H-1B fee and the rest.",
        "slug": make_slug("supreme-court-june-25-immigration-deference-diaspora-courts-backstop-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian visa holders have watched courts strike down the $100,000 H-1B fee and block a database flagging naturalised citizens; a Supreme Court now granting the executive broad immigration power signals the judicial safety net they have relied on is thinner than it looked.",
        "tags": ["supreme-court", "immigration-law", "executive-power", "h1b", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/25/supreme-court-tps-haiti-syria-trump/"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/25/supreme-court-asylum-arrived-united-states-border/"},
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/United_States_Supreme_Court_Building_on_a_Clear_Day.jpg/1280px-United_States_Supreme_Court_Building_on_a_Clear_Day.jpg",
        "image_caption": "The United States Supreme Court building in Washington, where two 6-3 immigration rulings landed on June 25.",
        "image_attribution": "Wikimedia Commons",
        "body": """For two years the Indian diaspora has had a comforting story to tell itself about American immigration policy: whatever the executive breaks, the courts will fix.

The story had evidence behind it. This month a federal judge in Massachusetts struck down President Trump's $100,000 fee on new H-1B petitions, calling it an unlawful tax. Another court blocked a database that had been flagging naturalised citizens — many of them Indian — as suspected non-voters. Student visas cancelled en masse last year were largely reinstated after more than a hundred lawsuits. Each ruling reinforced the same reassuring lesson: the system has guardrails, and the guardrails hold.

On June 25, the Supreme Court complicated that story.

## Two rulings, one direction

In a pair of 6-3 decisions, the Court handed the administration broad latitude over who may enter the country and who may stay. In one, it held that an asylum seeker standing on the Mexican side of the border has not "arrived in" the United States and is therefore not entitled to inspection or to apply for asylum until physically crossing — a reading that lets the government turn people back before they reach American soil. In the other, the Court allowed the administration to immediately end Temporary Protected Status for hundreds of thousands of Haitians and several thousand Syrians, with Justice Elena Kagan dissenting from the majority's conclusion that the affected migrants could be "put on the next plane."

Neither case is about Indians. No meaningful number of Indian nationals relies on TPS or arrives via the southern border. But the diaspora should read these rulings less for their facts than for their posture — because the posture is what governs the cases that do touch Indians.

## Why posture matters more than facts

Both decisions rest on deference: the principle that courts should give the President wide room on immigration and foreign affairs, and should be slow to second-guess executive judgement. In the TPS case the majority went further, accepting the government's argument that the statute bars judicial review of "any determination" about whether migrants may live and work in the country. That is a remarkably broad shield, and it is precisely the kind of reasoning the administration will reach for when defending its harder-edged measures aimed at skilled workers.

Consider what is currently in the courts or headed there. The $100,000 H-1B fee, struck down at the district level, is being appealed — and the government will argue the President's proclamation power deserves deference. A rule ending "duration of status" for F-1 students has cleared its final regulatory hurdle and will be litigated. New limits on green-card adjustment, expanded social-media vetting of visa applicants, and the narrowing of interview waivers all rest on executive discretion. A Supreme Court that has just twice told lower courts to stand back is not an obvious friend to challengers in any of them.

## The thinner net

This does not mean the diaspora's legal wins will be reversed; appellate timelines are long and many cases turn on statutory text rather than deference. But it does mean the assumption that the judiciary is a reliable backstop deserves re-examination. The lower courts that delivered the diaspora's recent victories sit beneath a Supreme Court increasingly inclined to credit the executive's account of its own powers. A favourable district ruling — on the H-1B fee, say — is a reprieve, not a guarantee.

For Indians making real decisions, the practical takeaway is about hedging, not panic. Treat court rulings in your favour as provisional until they survive appeal. Do not time a major filing, a job change, or a return ticket around a single judge's order that the government is contesting. Keep documentation of status meticulous, because the climate that produces deferential rulings also produces aggressive enforcement. And weigh seriously the alternatives the community is already exploring — Canadian permanent residency, cap-exempt and O-1 routes, the EB-1A pivot — not as defeatism but as diversification.

The American legal system remains the diaspora's best recourse, and a far better one than most immigrants anywhere enjoy. But June 25 was a reminder that recourse has a ceiling. The courts can slow the executive. On the evidence of this week, they are increasingly disinclined to stop it.
"""
    },
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nInserted {len(inserted)}/{len(articles)} articles:")
for h in inserted:
    print(f"  - {h}")
