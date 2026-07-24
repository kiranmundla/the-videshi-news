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

# ============================================================
# ARTICLE 1 — H-4 EAD rescission
# ============================================================
body1 = """The income that pays the second half of a Bay Area mortgage, the salary on the visa most people in the family forget the engineer's spouse even holds — that is what the Department of Homeland Security has now formally moved to take away.

In a court filing in *Save Jobs USA v. DHS*, the long-litigated challenge to the H-4 work-authorization program, DHS confirmed it has sent a proposed rule to rescind the program to the Office of Management and Budget for review. OMB clearance is the final gate before a rule is published in the Federal Register for public comment. The agency declined to disclose what the proposal actually says, including the one detail tens of thousands of families are desperate to know: whether spouses who already hold an Employment Authorization Document would keep it.

## What H-4 EAD is, and who holds it

The H-4 visa is the dependent status carried by the spouse of an H-1B worker. Since a 2015 rule, an H-4 spouse has been allowed to apply for work authorization — but only in a narrow window: the H-1B principal must already have an approved I-140 immigrant petition, or have crossed the six-year H-1B limit on the strength of a pending green card case. In other words, H-4 EAD is overwhelmingly a feature of the back half of the green card journey.

That makes it an almost entirely Indian story. Indians account for the overwhelming majority of the employment-based green card backlog, and therefore for the population stuck in exactly the limbo the H-4 EAD was built to soften. Government estimates over the years have pegged H-4 EAD holders at roughly 90,000-100,000 people, the large majority Indian women, many of them engineers, doctors, and managers in their own right who paused careers to follow a spouse to America.

## Why this is taking so long

The procedural history is its own kind of tell. DHS first signaled intent to kill the program years ago; the rule has been drafted, postponed, redrafted, and is now back before OMB. Proposed rules usually clear OMB in a few months. This one has lingered far longer, and immigration lawyers attribute the delay to the sheer volume of pushback — from employers, from advocacy groups, and from the OMB meetings that interested parties have requested in unusual numbers.

The practical takeaway for affected families is narrow but important: nothing has changed yet. Eligible H-4 spouses can still file new applications and renewals under the current rules. A proposed rule is not a final rule. Once published, it triggers a public-comment period, after which DHS must respond to comments and issue a final rule — a process that typically runs several months and is itself open to legal challenge.

## What an Indian family should actually do

For a household on the EB-2 or EB-3 India timeline, the rational move is to treat the EAD as a depreciating asset and act accordingly. If a spouse is eligible to file or renew now, filing now banks time under the existing rule. If a renewal is due in the next year, front-loading it removes one variable from a future that is about to get more uncertain.

The deeper math is brutal and familiar to anyone tracking the India backlog. EB-2 India sits more than a decade behind. The H-4 EAD was the device that let a family keep two incomes during that decade-plus wait. Removing it does not speed up a single green card; it simply converts a two-earner household into a one-earner household for the duration of the wait, while the mortgage, the tuition, and the cost of staying do not budge.

That is the quiet cost of this rule. It will not be measured in deportations or denials. It will be measured in resignation letters from women who did everything the system asked of them, and in the slow recalculation, in kitchens from Fremont to Frisco, of whether the wait is still worth it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Rule That Would Quietly End the Second Income in Tens of Thousands of Indian Households",
    "subheadline": "DHS has sent its proposal to rescind H-4 work permits to the White House budget office. For Indian families deep in the green card backlog, the second paycheck is now on a clock.",
    "slug": make_slug("h4-ead-rescission-omb-review-indian-spouses-work-permit"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "H-4 EAD holders are overwhelmingly Indian women married to H-1B workers stuck in the decade-long EB-2/EB-3 India green card backlog; rescinding the program would convert tens of thousands of two-income diaspora households into single-income ones with no change to their green card wait.",
    "tags": ["h4-ead", "h1b", "green-card", "uscis", "dhs", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fragomen — Proposed H-4 EAD Rescission Under Federal Review", "url": "https://www.fragomen.com/insights/proposed-h-4-ead-rescission-under-federal-review.html"},
        {"name": "Fragomen — H-4 EAD Rescission Proposal Remains Under Federal Review, DHS Confirms", "url": "https://www.fragomen.com/insights/h-4-ead-rescission-proposal-remains-under-federal-review-dhs-confirms.html"},
        {"name": "EY — USCIS announces significant changes to employment authorization for H-4, E and L dependent spouses", "url": "https://www.ey.com/en_gl/technical/tax-alerts"}
    ]),
    "score_total": 84,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/3784295/pexels-photo-3784295.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A professional working on a laptop; H-4 EAD holders are largely women in skilled jobs",
    "image_attribution": "Pexels",
    "body": body1,
}

# ============================================================
# ARTICLE 2 — Adjustment of Status now "extraordinary"
# ============================================================
body2 = """For decades, the last step of the American green card — filing Form I-485 from your couch in New Jersey rather than flying back to a consulate in Mumbai — was the boring part. You waited years for your priority date, then you filed, then you waited some more. A new USCIS policy memo has just made that final step the unpredictable one.

On May 21, USCIS issued Policy Memorandum PM-602-0199, reframing adjustment of status — the process of getting a green card while physically inside the United States — as an "extraordinary discretionary benefit" rather than a routine entitlement. The agency's public statement was blunt: "From now on, an alien who is in the U.S. temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances."

## What changed, in plain terms

Nothing in the statute changed. What changed is how officers are told to read it. The memo instructs adjudicators to treat consular processing abroad as the "normal" route Congress expects, and adjustment of status as a bypass that requires a favorable exercise of discretion — even when the applicant meets every legal requirement on paper.

Officers are directed to weigh a "totality of the circumstances," balancing negative factors (a prior overstay, unauthorized work, a lapse in status, anything inconsistent with the original visa's purpose) against positive ones (long U.S. residence, family ties, steady employment, economic contribution). Immigration lawyers reading the memo at firms like Greenberg Traurig and others have flagged the same alarming feature: it appears effective immediately, sweeping in cases already pending, with little transition time.

## Why this lands hardest on Indians

Two structural facts make this an Indian story before it is anyone else's.

First, the employment-based green card backlog. Because EB-2 and EB-3 India run more than a decade behind, an Indian worker frequently files the I-140 immigrant petition years before a green card number is available, then adjusts status from within the U.S. once their date is current. That worker has, by definition, spent many years on H-1B and H-4 status — accumulating exactly the kind of long, complicated immigration history that a "totality of the circumstances" review can pick apart.

Second, the consular alternative is no relief at all. The memo's implied answer — "just do consular processing instead" — means flying to a U.S. consulate in India, where wait times for appointments have run six to twelve months, and where any gap, any old status question, can strand a worker outside the country away from job and family. For a family with a mortgage and a child in an American school, "go process abroad" is not a procedural footnote. It is a months-long separation with no guaranteed return date.

## The crucial distinction to hold onto

The new discretion applies only at the adjustment-of-status stage — the I-485. It does not touch the PERM labor certification or the I-140 immigrant petition, which are still adjudicated under their existing standards. An approved I-140 is not suddenly at risk. The exposure is at the final filing, and it is sharpest for anyone with a blemish in their history: an old overstay, a period of unauthorized work, a stretch out of status during a job change.

## What to do about it

The honest advice from the immigration bar is to stop treating the green card finish line as automatic. Anyone with a complicated history should map it out with counsel before filing, document the positive equities — years of tax-paying employment, U.S.-citizen children, community ties — and assume an officer will now look for reasons to say no rather than reasons to say yes.

The deeper irony is hard to miss. The cohort most affected is the most documented, most vetted, most economically productive group of immigrants the system has: Indian professionals who waited a decade by the rules. The memo asks them, at the very end of that decade, to prove all over again that they deserve to stay."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "USCIS Just Made the Last Step of the Green Card the Riskiest One",
    "subheadline": "A new policy memo reframes filing for a green card from inside the U.S. as an 'extraordinary' favor rather than a right — and the Indians who waited a decade by the rules are the most exposed.",
    "slug": make_slug("uscis-adjustment-of-status-discretionary-memo-india-green-card"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians dominate the EB-2/EB-3 green card backlog and almost always adjust status from inside the U.S. after a decade-plus wait; treating that final I-485 step as a discretionary 'extraordinary' benefit puts the most-vetted, longest-waiting diaspora professionals at fresh risk of denial or forced consular processing abroad.",
    "tags": ["green-card", "adjustment-of-status", "i-485", "uscis", "eb2-india", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS — Will Grant 'Adjustment of Status' Only in Extraordinary Circumstances", "url": "https://www.uscis.gov/newsroom/news-releases"},
        {"name": "Lexology — USCIS Adopts Stricter Discretionary Review Standard for Green Card Applications Filed in the United States", "url": "https://www.lexology.com/"},
        {"name": "Greenberg Traurig — New USCIS Policy Memorandum Addresses Adjustment of Status Adjudications", "url": "https://www.gtlaw.com/en/insights"}
    ]),
    "score_total": 85,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8175097/pexels-photo-8175097.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A U.S. government building flying the American flag; USCIS reframed in-country green card filing as discretionary",
    "image_attribution": "Pexels",
    "body": body2,
}

# ============================================================
# ARTICLE 3 — B-1/B-2 job-search trap after layoff
# ============================================================
body3 = """When the layoff notices swept through the tech sector, the standard survival playbook for an H-1B worker had a familiar fallback: if you can't find a new sponsor inside the 60-day grace period, switch to a B-2 visitor status to "wind down your affairs" and keep job-hunting while you stay legal. USCIS has quietly pulled that ladder up.

As of March 31, 2026, USCIS archived the guidance page titled "Options for Nonimmigrant Workers Following Termination of Employment" — the page that explicitly stated job searching and attending interviews were permissible activities on B-1/B-2 visitor status. Adjudicators now treat that archived guidance as no longer controlling, and the consequences are showing up in real cases.

## The new trap

According to immigration attorneys tracking adjudications, USCIS has begun characterizing an open-ended job search as an impermissible *primary purpose* for being in the country on a B-2 visa. Requests for the standard six-month visitor stay are being challenged as excessive when the stated reason involves "exploring employment opportunities." Requests for Evidence increasingly assert that searching for work, interviewing, and accepting a job are inconsistent with visitor classification.

The most dangerous move is a retroactive one. In some cases, USCIS has used a *later* H-1B petition — filed by a new employer after a worker switched to B-2 — as evidence that the worker lied about their intentions when they filed the B-2 change of status in the first place. In other words, finding a job and getting sponsored, the very outcome the worker was hoping for, is being turned into proof of a "preconceived intent" to work all along. A successful job hunt becomes evidence of an earlier misrepresentation.

## Why the lawyers say this overreaches

The immigration bar's counter-argument is grounded in the statute itself. INA 101(a)(15)(B) defines a visitor as someone here temporarily for business or pleasure and specifically bars those coming "for the purpose of performing skilled or unskilled labor." The operative prohibition, lawyers note, is performing labor — not seeking it. Searching for a job is not employment. Interviewing is not employment. Performing services for wages is employment. The statutory line has always sat at compensated work, not at the intent to look for it.

There is also a conflation problem. The 60-day grace period — which lets a terminated H-1B worker remain in H-1B status while seeking a new job and filing a petition — is a different animal from B-2 status. The grace period activity happens *while still in H-1B classification*. Switching to B-2 requests a different lawful status entirely. Adjudicators appear to be blurring the two.

## Why this is an Indian story

Indian nationals make up roughly three-quarters of the H-1B workforce, which means they make up the bulk of anyone laid off from an H-1B job. For a worker on the green card treadmill — often years deep into an EB-2 India wait, with an approved I-140 and a U.S.-born child — leaving the country to "reset" is not a clean option. The B-2 bridge was how thousands of Indian professionals stayed legal between jobs without abandoning a decade of accrued green card progress.

Removing that bridge sharpens an already cruel timeline. A laid-off Indian worker now has a hard 60-day window in H-1B status to find a new sponsor and get a petition filed. Miss it, and the safe options narrow to leaving the country — which, for someone mid-green-card, can mean surrendering years of waiting and a forced consular gamble abroad.

## The practical read

The takeaway is not that switching to B-2 after a layoff is impossible — it is that it has become legally treacherous and should not be attempted without counsel. Workers who do file should be scrupulous about stating a genuine visitor purpose, avoid framing the stay around job-hunting, and understand that a subsequent H-1B filing may be read backward against them. The cleaner strategies — porting an approved I-140, lining up a concurrent H-1B transfer before the grace period runs, or using a spouse's status where available — now matter more than ever.

The broader signal is unmistakable. Each of these moves, taken alone, is a technical adjustment. Taken together — the discretionary green card memo, the H-4 EAD rescission, and now the closing of the B-2 off-ramp — they describe a system steadily removing the soft landings that made a long, lawful Indian immigration journey survivable."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "USCIS Quietly Closed the Visa Off-Ramp Laid-Off H-1B Workers Relied On",
    "subheadline": "The guidance that let terminated tech workers job-hunt on a visitor visa is gone — and finding a new job is now being used as evidence you lied to get the visa.",
    "slug": make_slug("uscis-b2-job-search-trap-laid-off-h1b-workers-india"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians are roughly three-quarters of H-1B holders and thus the bulk of laid-off tech workers; archiving the guidance that allowed job-hunting on B-1/B-2 status strips away the bridge that let mid-green-card Indian professionals stay legal between jobs without abandoning a decade of EB-2 India progress.",
    "tags": ["h1b", "b2-visa", "layoffs", "uscis", "change-of-status", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Mondaq — H-1B To B-1/B-2 Change Of Status After Termination: What Workers, Employers Should Know", "url": "https://www.mondaq.com/unitedstates/work-visas"},
        {"name": "Reddy Neumann Brown PC — Is USCIS Setting a Trap for H-1B Workers Filing B-1/B-2 After Termination?", "url": "https://www.rnlawgroup.com/"},
        {"name": "USCIS — Change My Nonimmigrant Status", "url": "https://www.uscis.gov/visit-the-united-states/change-my-nonimmigrant-status"}
    ]),
    "score_total": 82,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/9870223/pexels-photo-9870223.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A business handshake over documents; a new job offer can now be read against a worker's prior visitor-visa filing",
    "image_attribution": "Pexels",
    "body": body3,
}

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"OK  {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
