#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

body1 = """The Trump administration told a federal appeals court last week that its $100,000 H-1B fee is not a tax, it is a border-control measure, and that every day the fee goes uncollected lets in foreign workers the President has already decided should stay out. The argument is the government's opening move in a fight that will decide whether the most expensive line item in the history of the H-1B program survives the summer.

Here is where things actually stand, because the timeline has been whiplash-inducing. On June 8, Judge Leo Sorokin of the federal district court in Massachusetts struck the fee down entirely, siding with 20 Democratic-led states. He ruled that Proclamation 10973 — President Trump's September 2025 order attaching a $100,000 charge to new H-1B petitions requiring consular processing — was an unauthorized tax that only Congress can levy, and that the agency guidance implementing it violated the Administrative Procedure Act. Crucially, he vacated the policy nationwide, not just for the states that sued.

Then it un-happened. On June 12, the same judge paused his own ruling to give the U.S. Court of Appeals for the First Circuit room to weigh in. The government filed its appeal and, by the June 18 deadline, asked the appeals court to keep the fee enforceable while the case proceeds. The practical upshot for right now: USCIS may continue demanding the $100,000 payment on qualifying petitions. The reprieve was real for four days and then evaporated.

## What the government is arguing

In its First Circuit filing, the Department of Homeland Security made two claims. First, the fee is not a tax at all but a regulatory condition on entry, squarely within the President's authority under 8 U.S.C. § 1182(f) to bar foreign nationals whose presence he deems detrimental. Second, even if a court decides it is a tax, the President could impose it anyway. DHS also leaned on urgency: "Every day that passes more aliens can petition and enter the country," it warned, and unwinding those approvals later would be messy.

The states' case is only one of at least three. Parallel suits are pending in the D.C. Circuit and the Northern District of California. With different courts capable of reaching different conclusions, immigration lawyers increasingly expect the question to land at the Supreme Court — which means the uncertainty Indian workers are living under is not a passing storm but the forecast for the next year or more.

## Why this lands hardest on Indians

Indians receive roughly 70% of approved H-1B visas, so any change to the program's price tag is, functionally, an India story. But the $100,000 fee has a narrower bite than the headline suggests, and the distinction matters enormously for families doing the math.

The fee applies to *new* petitions for beneficiaries who are outside the United States and need consular processing — the classic case of an Indian engineer being hired from Bengaluru or Hyderabad and brought over for the first time. DHS has clarified it does not apply to change-of-status filings, extensions, or change-of-employer petitions for people already in the country. So an H-1B holder already in Texas renewing status is not writing a six-figure check. A fresh graduate in India waiting on a first-time petition very much could be — or rather, their employer could be, and many simply will not.

That divide is quietly reshaping who gets hired. For an employer, $100,000 is a rational reason to prefer a candidate already on American soil — an OPT student, an L-1 transfer, someone changing status — over an equally qualified candidate in India. The fee does not just tax entry; it tilts the entire hiring funnel toward people who are already here, and away from the pipeline that has historically pulled talent directly out of Indian campuses and IT firms.

For the American Association of Physicians of Indian Origin, the stakes are starker still. Its members argued the fee would have gutted hiring of international medical graduates at rural and safety-net hospitals, where Indian-trained doctors fill chronic vacancies. The group cheered Sorokin's ruling — and is now watching the appeal with the same anxiety as everyone else.

## What to watch

The next domino is the First Circuit's decision on the government's stay request. If the court grants it, the fee stays collectable through the full appeal. If it denies the stay, the fee likely goes dark again until a higher court resolves the split. Either way, employers planning first-time petitions out of India should budget for the fee and assume volatility. The only safe prediction is that this is not over."""

body2 = """The single most consequential work permit in the lives of tens of thousands of Indian women in America is caught between two regulations pulling in opposite directions — and this week the Department of Homeland Security told a court it has no idea when either will move.

The permit is the H-4 EAD, the employment authorization granted to spouses of H-1B workers who are stuck in the green card backlog. Created under the Obama administration in 2015, it lets the spouse of an H-1B holder work legally once that H-1B holder has an approved I-140 petition or has been extended past the six-year limit while waiting for permanent residency. Because Indians dominate the employment-based backlog, they dominate the H-4 EAD rolls — the overwhelming majority of these permits are held by Indian spouses, most of them women who have built careers, founded companies, and become primary or co-earners while their families wait out a green card queue that can stretch past a decade.

## Two rules, opposite directions

The first rule would kill it. DHS has sent the Office of Management and Budget a proposal to rescind the H-4 work-authorization program entirely. In a court filing this week in *Save Jobs USA v. DHS* — the long-running lawsuit by U.S. tech workers challenging the program — the department confirmed the rescission proposal is still under OMB review with, in its words, no projected publication date. The rule was submitted to OMB back in February. Proposals usually clear that review within a few months; this one has now sat for more than six, slowed by a flood of public input even before any details have been released.

The second rule would expand it. Separately, DHS has a draft regulation that would *extend* eligibility — letting H-4 spouses apply for work authorization when the H-1B's labor certification or I-140 was filed 365 or more days earlier and the worker is seeking a sixth-year-plus extension. A companion rule would give Australian E-3 and Chilean and Singaporean H-1B1 workers a 240-day work-authorization cushion they currently lack. Both are also stuck at OMB.

So the program is simultaneously being drafted out of existence and drafted into something broader, with neither version finalized and neither on a clock. For an Indian spouse renewing an EAD this month, that is the policy equivalent of being told the bridge ahead is both under construction and scheduled for demolition.

## What is actually true today

Cut through the noise and the operative facts are simple. The H-4 EAD program is fully in effect. Eligible spouses can still apply for new permits and renew existing ones. Nothing has been rescinded, because nothing has been published, because nothing has cleared OMB. Even if the rescission rule emerges tomorrow, it would not take effect on publication — it would trigger a public comment period of at least 30 to 60 days, followed by months of DHS reviewing those comments before any final rule. The same multi-month runway applies to the expansion rule.

There is also a quieter piece of good news buried in recent guidance: H-4 EAD holders are now eligible for automatic extensions of up to 180 days when they timely file a renewal, which closes the employment gaps that used to strand spouses for months while USCIS processed paperwork. E and L dependent spouses, meanwhile, are now treated as work-authorized incident to their status — no separate card required.

## Why Indian families should plan, not panic

The honest read for an Indian H-4 household is that the program is alive but politically radioactive, and the smart move is to use it while it works. Practically, that means filing renewals early to capture the 180-day automatic extension, keeping I-140 approval notices and extension paperwork organized, and treating any "H-4 EAD abolished" headline with skepticism until it carries a Federal Register citation and an effective date.

It also means watching the calendar at OMB more than the cable-news chyron. The real signal will not be a tweet or a court remark; it will be the day one of these rules actually clears review and publishes. Until then, the women who depend on this permit are working under a question mark — but they are still, legally and fully, working."""

body3 = """For Indian students on F-1 visas, the summer of 2026 has turned a routine question — should I fly home to see family? — into a genuine risk calculation. The visa stamp in the passport, long treated as a settled fact, is no longer one, and the consequences of guessing wrong now run from a missed semester to a terminated work authorization.

The backdrop is a year of tightened student-visa machinery. Last summer, the State Department briefly suspended new F, J, and M visa appointments before resuming them under a regime of "comprehensive and thorough" vetting that requires applicants to make their social media profiles public. Consular officers were directed to screen for hostility toward the United States, and many applications now route into prolonged "administrative processing" under section 221(g) — a refusal-pending-review status with no fixed timeline. Indian students, who form one of the two largest international cohorts on American campuses, sit squarely in the path of all of it.

## The re-entry trap

The danger is not getting on the plane to India. It is getting back. An F-1 student who travels abroad after their visa stamp has expired must obtain a new visa at a U.S. consulate before returning — and consular wait times in India remain punishing, with interview slots at several posts booked many months out. A summer trip planned around a two-week stay can become an open-ended one if the appointment calendar or administrative processing does not cooperate, and the student misses the start of the fall term.

For students on Optional Practical Training, the math is more dangerous still. Immigration lawyers are warning OPT and STEM OPT workers that traveling with an expired visa stamp is a gamble that can cost the job itself. If you cannot secure a new visa to return, you may not be readmitted, and your OPT can be terminated outright — meaning you would not be able to come back until and unless you obtain an H-1B. There is also the quieter trap of the unemployment clock: F-1 students on initial OPT may accrue no more than 90 days of unemployment, and STEM OPT extends that to an aggregate of 150 days over the full period. Time spent stuck outside the country, unable to work, can burn down that allowance unless the travel falls within employer-authorized leave.

## A pre-departure checklist that actually matters

Before any Indian student or OPT worker books a flight this summer, a few checks are worth more than any reassurance:

- **Confirm your SEVIS record is "active"** with your school's designated official as close to departure as possible. A lapsed or terminated record can stop you at the gate.
- **Check the email tied to your most recent visa application** for any revocation notice. During last year's surge in student-visa revocations, some were issued with no email at all — so a clean inbox is reassuring but not conclusive.
- **Carry the full document set**: a valid I-20 with a current travel signature, proof of funding, enrollment verification, and for OPT, your EAD card plus a recent employment-verification letter and pay stubs. Without a valid job offer, an OPT student may not be readmitted.
- **Map the consular wait time** at the post you would use to renew, and assume administrative processing could add weeks with no warning.

## The honest calculus

None of this means an Indian student cannot go home. Students whose visa stamps remain valid for the duration of their trip face far lower risk, and family emergencies and milestones are not things to be governed entirely by immigration anxiety. But the calculus has shifted. The reasonable default for anyone on an expired stamp — and especially anyone on OPT with a job to protect — is to weigh whether the trip is worth the possibility of being locked out for a semester.

The deeper cost is not logistical, it is human: a generation of Indian students rationing visits home, skipping weddings and grandparents and graduations, because the bridge back to the life they have built in America has quietly become a one-way risk. The visa in the passport used to be permission to come and go. In the summer of 2026, it is closer to a bet."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Says the $100,000 H-1B Fee Isn't a Tax. The Appeals Court Will Decide if Indians Pay It",
        "subheadline": "DHS told the First Circuit the six-figure fee is a border control, not a levy — and for now USCIS can keep collecting it on first-time petitions out of India.",
        "slug": make_slug("h1b-100k-fee-first-circuit-appeal-not-a-tax-india-consular"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians receive roughly 70% of H-1B visas, and the $100,000 fee falls hardest on first-time petitions for candidates still in India — quietly tilting US hiring toward workers already on American soil.",
        "tags": ["h1b", "visa-fee", "first-circuit", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Tax — DHS Says Trump H-1B Fee Isn't a Tax", "url": "https://news.bloombergtax.com/daily-tax-report/dhs-says-trump-h-1b-fee-isnt-a-tax-should-continue-on-appeal"},
            {"name": "WR Immigration — Court Temporarily Reinstates $100,000 H-1B Fee Pending Appeal", "url": "https://wolfsdorf.com/court-temporarily-reinstates-uscis-authority-to-collect-100000-h-1b-consular-processing-fee-pending-appeal/"},
            {"name": "Ogletree Deakins — Trump Administration Appeals Ruling Striking Down $100,000 H-1B Fee", "url": "https://ogletree.com/insights-resources/blog-posts/trump-administration-appeals-ruling-striking-down-100000-h-1b-fee-requirement/"},
            {"name": "The Indian Eye — AAPI Applauds Court Ruling Blocking $100,000 H-1B Physician Visa Requirement", "url": "https://theindianeye.com/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1000740/pexels-photo-1000740.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A federal courthouse facade, where the fate of the $100,000 H-1B fee now rests on appeal.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Work Permit Indian Wives Depend On Is Being Drafted Out of Existence — and Expanded — at the Same Time",
        "subheadline": "DHS told a court this week the H-4 EAD rescission has no publication date, even as a separate rule to widen eligibility sits at the same desk. For now, nothing has changed.",
        "slug": make_slug("h4-ead-rescission-omb-no-timeline-expansion-rule-india-spouses"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The overwhelming majority of H-4 work permits are held by Indian spouses — mostly women — waiting out the green card backlog, so the program's tug-of-war directly determines whether they can keep working.",
        "tags": ["h4-ead", "dhs", "omb", "h1b", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — H-4 EAD Rescission Proposal Remains Under Federal Review, DHS Confirms", "url": "https://www.fragomen.com/insights/h-4-ead-rescission-proposal-remains-under-federal-review-dhs-confirms.html"},
            {"name": "Fragomen — Proposed Rules on Work Authorization for Certain H-1B Dependents and Others Expected to Advance", "url": "https://www.fragomen.com/insights/proposed-rules-on-work-authorization-for-certain-h-1b-dependents-and-others-expected-to-advance.html"},
            {"name": "Fragomen — DHS to Reconsider H-4 Employment Authorization Rule", "url": "https://www.fragomen.com/insights/dhs-to-reconsider-h-4-employment-authorization-rule.html"},
            {"name": "USCIS — Employment Authorization for Certain H-4 Dependent Spouses", "url": "https://www.uscis.gov/working-in-the-united-states/information-for-employers-and-employees/employment-authorization-for-certain-h-4-dependent-spouses"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3784295/pexels-photo-3784295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A professional works at her laptop — the kind of career the H-4 EAD makes possible for spouses of H-1B workers.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Should an Indian Student Fly Home This Summer? The Visa Stamp No Longer Guarantees a Way Back",
        "subheadline": "Tighter vetting, social-media screening and months-long consular waits have turned a routine trip into a risk calculation — and for OPT workers, a gamble with the job attached.",
        "slug": make_slug("f1-opt-students-summer-travel-india-visa-reentry-risk-2026"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are one of the two largest international cohorts on US campuses, and a botched summer trip home can now cost them a semester — or, for those on OPT, their work authorization and job.",
        "tags": ["f1-visa", "opt", "stem-opt", "students", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — 2026 International Travel Planning for F-1 Students", "url": "https://www.fragomen.com/insights/united-states-2026-international-travel-planning-for-f-1-students.html"},
            {"name": "University of Colorado Boulder ISSS — Resumption of F and J Visa Appointments", "url": "https://www.colorado.edu/isss/2025/06/19/june-19-2025-resumption-f-and-j-visa-appointments"},
            {"name": "The Indian Eye — Tighter student visa rules may impact Indians in US: Expert", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4173219/pexels-photo-4173219.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A traveler waits at an international airport departure area with passport in hand.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] word count: {wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
