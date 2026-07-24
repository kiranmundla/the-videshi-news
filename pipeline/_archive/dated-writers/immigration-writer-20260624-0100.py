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

articles = [
{
    "id": str(uuid.uuid4()),
    "headline": "The Government Just Told a Court It Wants to Reconsider H-4 Work Permits. 90,000 Indian Spouses Are Listening.",
    "subheadline": "DHS has asked for six more months to decide the fate of the H-4 EAD rule. The program survives for now — but Washington has signaled it may move to restrict or end it.",
    "slug": make_slug("h4-ead-dhs-reconsider-save-jobs-usa-indian-spouses-work-permit"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The H-4 EAD lets tens of thousands of spouses of Indian H-1B workers — overwhelmingly women — hold jobs while the family waits out a green-card backlog that can run two decades; its loss would cut household incomes and careers across the diaspora.",
    "tags": ["h4-ead", "uscis", "dhs", "h1b", "green-card", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fragomen — DHS to Reconsider H-4 Employment Authorization Rule", "url": "https://www.fragomen.com/insights/dhs-to-reconsider-h-4-employment-authorization-rule.html"},
        {"name": "EY — USCIS changes to H-4, E, and L dependent spouse employment authorization", "url": "https://www.ey.com/en_gl/technical/tax-alerts"},
        {"name": "Perkins Coie — Relaxing of EAD Extension Policies for E, H-4, and L Dependent Spouses", "url": "https://perkinscoie.com/insights"}
    ]),
    "score_total": 84,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/3784295/pexels-photo-3784295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A professional works at a laptop; the H-4 EAD allows certain spouses of H-1B workers to be employed in the United States.",
    "image_attribution": "Pexels",
    "body": """The H-4 work permit has been the immigration program that Washington keeps threatening but never quite kills. This week it came closer to the edge again.

In a motion filed with the U.S. Court of Appeals for the D.C. Circuit, the Department of Homeland Security told the court it intends to "review and reconsider" the regulation that lets certain spouses of H-1B workers apply for an Employment Authorization Document, or EAD. The agency asked for an additional six months to settle its position. Crucially, DHS also flagged that it may publish a new proposed rule in the coming months — one that could "limit or terminate" the program altogether.

For now, nothing changes. Qualifying H-4 spouses can still file for new permits and renewals. But the signal is unambiguous, and the people who read it most carefully are Indian.

## What the H-4 EAD Actually Does

The rule, created by the Obama administration in 2015, is narrow by design. An H-4 spouse can work only if the H-1B principal (1) has an approved Form I-140 immigrant worker petition, or (2) has secured a one-year extension of H-1B status beyond the statutory six-year cap under the American Competitiveness in the Twenty-First Century Act, based on a filed labor certification or I-140. H-4 children get nothing. Eligibility, in other words, is a downstream benefit of being stuck in the green-card line.

That is exactly why the program is so Indian. The qualifying conditions — an approved I-140, a sixth-year H-1B extension — are the hallmarks of someone trapped in the EB-2 or EB-3 backlog, which for India-born applicants now stretches past a decade and, by some estimates, well beyond. Government and advocacy tallies have long put the number of H-4 EAD holders in the range of 90,000 or more, the overwhelming majority of them women from India.

## The Case Behind the Filing

The vehicle for all this is *Save Jobs USA v. DHS*, a long-running lawsuit brought by a group of U.S. technology workers who argue the agency had no authority to let H-4 spouses work. A district court dismissed the suit; the plaintiffs appealed. In February, the administration asked the court to pause the appeal while it reconsidered its own regulation. This week's filing extends that pause and makes the intent plainer: DHS wants room to rewrite, restrict, or scrap the rule on its own terms rather than have a court do it.

If DHS does move to terminate the program, it would most likely have to go through formal rulemaking — a notice-and-comment process that takes months and invites public feedback. That is cold comfort to a household trying to plan a mortgage payment, but it matters: a rule killed by regulation can be fought, commented on, and litigated, whereas the uncertainty itself is the immediate damage.

## Why This Lands Hard on Indian Households

Consider the math of a typical Indian H-1B family. The principal earns a tech salary; the spouse, often equally credentialed, took an H-4 dependent status to come along. Before 2015, that spouse simply could not work — a decade of professional life on hold while the priority date crept forward. The H-4 EAD turned that dead time into a second income, a career, and in many cases a small business with its own employees.

Strip the permit away and the household reverts to a single income precisely when the cost of staying in the line is rising on every other front — a $100,000 H-1B fee that was struck down but is being appealed, a 75% jump in the citizenship application fee, premium-processing increases, and the elimination of the visa-interview dropbox in India. Each measure is survivable alone. Stacked, they push families toward the same calculation a growing number are already making: that the American green-card queue may not be worth the wait.

## What to Watch

The next real signal will be a proposed rule in the Federal Register. If it appears, the comment period becomes the diaspora's main lever — and immigration lawyers are already urging affected families to be ready to file substantive comments documenting what the program means to them. Until then, the advice is unglamorous but sound: renew early, keep the underlying I-140 and H-1B extension paperwork airtight, and do not assume the permit in hand will be the one you can count on next year.

The H-4 EAD has survived every previous attempt to end it. The difference this time is that the government is no longer waiting for a court to act."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "The Green Card Memo Has a Loophole Most Indians Missed: It May Not Touch H-1B Holders At All",
    "subheadline": "USCIS's 'extraordinary relief' memo on adjustment of status spooked the diaspora. Read closely, the dual-intent carve-out it leaves for H-1B and L-1 workers changes the picture.",
    "slug": make_slug("adjustment-of-status-memo-dual-intent-h1b-l1-carveout-indians-green-card"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians are the largest group filing employment-based green cards from inside the U.S. via adjustment of status; whether the new 'extraordinary relief' standard applies to dual-intent H-1B and L-1 holders decides whether a million-plus people can finish the process without leaving the country.",
    "tags": ["adjustment-of-status", "uscis", "green-card", "h1b", "dual-intent", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Nolo — 2026 Immigration Legal Updates: Is Adjustment of Status Dead?", "url": "https://www.nolo.com/legal-encyclopedia/immigration-law-updates"},
        {"name": "Smal Immigration Law Office — Analysis of the USCIS AOS policy memo", "url": "https://www.law-visa-usa.com/"},
        {"name": "Global Net News — USCIS Clarifies Green Card Application Policy for H-1B Holders", "url": "https://globalnet.news/"}
    ]),
    "score_total": 82,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8061949/pexels-photo-8061949.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An applicant reviews immigration paperwork; adjustment of status is the route most Indians use to finalize a green card from inside the U.S.",
    "image_attribution": "Pexels",
    "body": """When USCIS declared in late May that adjustment of status — the process by which immigrants already in the United States get a green card without leaving — would henceforth be treated as "extraordinary discretionary relief," the diaspora reacted the way it always does: with a collective stomach drop. The implication seemed plain. Apply from home, or don't apply at all.

A month on, with the lawyers having read the actual text rather than the headlines, a more precise and far more important reading has emerged. The memo may leave the people most worried about it — H-1B and L-1 workers from India — largely where they were.

## What the Memo Says

The May 22 policy memorandum reframes Section 245 adjustment of status as "a matter of discretion and administrative grace," not a routine entitlement, and reminds officers that it is "not designed to supersede the regular consular processing of immigrant visas." USCIS spokesman Zach Kahler said the agency was "returning to the original intent of the law," and that an alien who "wants a Green Card must return to their home country to apply, except in extraordinary circumstances." No effective date was attached, which led practitioners to assume it applies to pending cases as well as new ones.

That is the language that set off the panic. Roughly 820,000 people apply for green cards through adjustment of status each year. For Indians on H-1B and L-1 visas — who wait years, sometimes well over a decade, for a priority date to become current — being told to decamp mid-process would mean uprooting children, selling homes, and gambling on a consular interview abroad.

## The Carve-Out Hiding in Plain Sight

Here is the part the early coverage skipped. The memo itself signals that the new posture may be "less applicable" to dual-intent nonimmigrant categories — precisely H-1B, L-1, and their H-4 and L-2 dependents.

Dual intent is the doctrine, settled in U.S. immigration law for decades, that a person can lawfully hold a temporary work visa and simultaneously intend to become a permanent resident. It is the entire legal reason an H-1B holder can buy a house and file an I-485 without torpedoing their status. The memo does not erase it. As one immigration analysis put it, applying for adjustment of status is "not inconsistent" with maintaining H-1B or L-1 status, so the "extraordinary relief" framing sits awkwardly against that long-standing concept.

USCIS effectively confirmed the softer reading on May 26, when Kahler clarified that applicants "who present applications that provide an economic benefit or otherwise are in the national interest will likely be able to continue on their current path." For the median Indian H-1B engineer with an approved I-140 and a U.S. employer attesting to their role, that is a description of the typical case, not an exotic exception.

## The Catch

None of this is a guarantee, and that is the honest part of the story. The memo cautions that maintaining dual-intent status alone is "not sufficient" to warrant a favorable exercise of discretion. Officers must still weigh each case — and adjustment has always, technically, been discretionary. What has changed is the framing officers are told to start from, and the explicit instruction to consider whether circumstances are "extraordinary."

In practice, that means the burden of persuasion shifts. An H-1B holder filing to adjust will want a record that does the talking: an approved I-140, evidence of the role's economic and national-interest value, clean status history, U.S. tax filings, community ties. The applicants most exposed are not the dual-intent worker but those on single-intent visas — tourists, students, certain exchange visitors — for whom the "leave and apply abroad" default now bites hardest.

## What Indians Should Do

First, don't liquidate your life over a headline. The dual-intent carve-out is real, and the agency's own clarification points toward continuity for mainstream employment-based cases. Second, build the file as if you'll need to prove your worth, because under the new framing you might. Third, watch for litigation: a memo with no effective date and a contested legal theory is a near-certain target for challenge, and the courts have already shown this year that they will strike administration immigration measures they read as overreach.

The green-card process for Indians remains slow, crowded, and politically exposed. But the door that seemed to slam in May turns out to have a gap — and for the dual-intent majority, that gap is wide enough to keep planning around."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "The Quiet Fee Increases Are Back: Premium Processing Now Costs Indians More at Every Step",
    "subheadline": "No proclamation, no court fight — just a routine inflation adjustment that quietly raised the price of speed on H-1B, green-card, and OPT filings to nearly $3,000.",
    "slug": make_slug("premium-processing-fee-increase-i907-h1b-i140-opt-indians-2026"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians lean on premium processing more than any other group — to lock in H-1B starts, race I-140s against a shifting visa bulletin, and keep OPT work authorization from lapsing — so a fee that climbs every two years is a recurring tax on the diaspora's most time-sensitive filings.",
    "tags": ["premium-processing", "i-907", "uscis", "h1b", "opt", "fees", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "USCIS — USCIS to Increase Premium Processing Fees", "url": "https://www.uscis.gov/newsroom/news-releases"},
        {"name": "Ogletree Deakins — USCIS Premium Processing Fees Will Increase on March 1, 2026", "url": "https://ogletree.com/insights/"},
        {"name": "Penn Global — USCIS Premium Processing Fee Increase Effective March 1, 2026", "url": "https://global.upenn.edu/"}
    ]),
    "score_total": 70,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32642490/pexels-photo-32642490.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A U.S. passport; premium processing fees apply to employment and work-authorization petitions central to the immigrant pipeline.",
    "image_attribution": "Pexels",
    "body": """The immigration measures that make headlines come with proclamations and courtroom drama. The ones that actually drain Indian bank accounts tend to arrive as a line in the Federal Register. The latest premium-processing fee increase is firmly in the second category — and it is worth understanding precisely because nobody is shouting about it.

Under a final rule that took effect March 1, 2026, the Form I-907 premium-processing fees rose across the board to reflect inflation between June 2023 and June 2025. The increases are modest per filing but they hit exactly the forms Indians file most, and they compound against every other cost the diaspora is now absorbing.

## The New Numbers

The adjustments, authorized under the USCIS Stabilization Act and pegged to a 5.72% rise in the Consumer Price Index, break down like this:

- **Form I-129 (H-1B, L-1, O-1, TN, E-3 and most other classifications): $2,965**, up from $2,805 — an extra $160.
- **Form I-140 (employment-based immigrant petitions): $2,965**, up from $2,805 — an extra $160.
- **Form I-539 (extend/change status for F, J, M categories): $2,075**, up from $1,965 — an extra $110.
- **Form I-765 (employment authorization, including OPT and STEM OPT): $1,780**, up from $1,685 — an extra $95.

Premium processing buys a 15-calendar-day adjudication window — approval, denial, or a request for evidence. It is optional, it sits on top of the base filing fee, and it cannot be waived. Any I-907 postmarked on or after March 1 must include the new amount, or the filing is rejected and returned.

## Why Indians Pay This More Than Anyone

Premium processing is, in effect, a tax on urgency — and the Indian immigration journey is defined by urgency at every turn.

Start with the H-1B. A selected beneficiary often needs an approval in hand before an October 1 start date, or to switch employers without a gap. Premium processing on the I-129 is the standard insurance policy, and at $2,965 it is now pricier.

Then the I-140. For an India-born worker in the EB-2 or EB-3 line, the priority date is everything, and the visa bulletin moves — and retrogresses — without warning. The June 2026 bulletin pushed EB-2 India back more than ten months and EB-1 India back three and a half. When a category lurches, the race is to get the I-140 approved before a filing window slams shut, and premium processing is how you win that race.

Finally OPT and STEM OPT. The I-765 premium-processing tier exists because a delayed EAD can mean a recent graduate loses a job offer or falls out of status. Indian students — the largest international cohort in the U.S. — file these in volume, and for them $1,780 to avoid a lapse is less a luxury than a necessity.

## The Stacking Problem

Taken alone, a $95-to-$160 bump is a rounding error against a tech salary. The problem is that it never arrives alone. A single Indian family moving through the system this year may face the increased I-129 premium fee, the increased I-140 premium fee, a 75% jump in the naturalization application fee now under proposal, the elimination of the visa-interview dropbox that forces a trip to a consulate in India, and the lingering threat of the $100,000 H-1B surcharge that a court struck down but the government is appealing. Premium processing is one tile in a widening mosaic of cost.

And unlike the dramatic measures, this one is structural. The Stabilization Act directs DHS to revisit premium fees every two years to keep pace with inflation. That means the increase is not a one-off but a ratchet — expect another adjustment in 2028, and again after that, regardless of who controls the agency.

## The Takeaway

There is no fighting this one in court; it is doing exactly what Congress authorized. The practical response is planning. Budget premium processing into the true cost of each filing rather than treating it as an afterthought. Time I-140 and I-907 submissions around the visa bulletin so you pay for speed only when speed buys you something. And recognize the pattern for what it is: the loud immigration fights grab the attention, but it is the quiet, automatic, inflation-indexed fees that the diaspora will keep paying, predictably, every two years."""
}
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
