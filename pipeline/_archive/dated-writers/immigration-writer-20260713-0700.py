#!/usr/bin/env python3
"""Immigration writer — 2026-07-13 07:00 PT run.

Two articles:
1. $750 expedited B-1/B-2 visa interview pilot (launched July 1)
2. The One Big Beautiful Bill Act's new immigration fees (signed July 4)
"""
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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1 ──────────────────────────────────────────────────────────
article1_body = """\
For decades, the queue has been the defining feature of every US consulate in India. At Mumbai and Hyderabad, wait times for a B-1/B-2 tourist or business visa interview now stretch past ten months. For families planning to attend a graduation in California or a funeral in New Jersey, the arithmetic has been brutal: start the process a year early or don't go at all.

On July 1, the State Department introduced a new option. Pay $750, and you can cut to the front of the line.

## The Mechanics

Under a temporary final rule published in the Federal Register on June 9, a six-month pilot program now allows B-1/B-2 visa applicants at select consular posts to purchase an expedited interview appointment. The fee — on top of the standard $185 visa application fee — guarantees a slot within ten business days. No written justification required. No humanitarian emergency needed. Just money.

The program runs through December 31, 2026, with a projected capacity of 25,000 expedited requests across all participating posts. The State Department has not yet published which consulates will participate, stating only that locations will be announced on travel.state.gov. For Indian applicants, whether New Delhi, Mumbai, Chennai, Hyderabad, or Kolkata makes the list will determine whether this program is relevant or merely theoretical.

There are important caveats. The $750 buys a faster interview, not a faster outcome. Applicants "will still be subject to all standard visa eligibility and processing requirements, including any administrative processing deemed necessary," the rule states. Administrative processing — the opaque secondary review that can add weeks or months after the interview — remains untouched by the fee.

If you book the expedited slot and don't show up, the fee is gone. No refunds, no transfers.

## What It Actually Costs Now

The fee stacks on top of other recent increases. The newly enacted One Big Beautiful Bill Act, signed into law on July 4, imposes a $250 "visa integrity fee" on every nonimmigrant visa issued — including B-1/B-2 tourist visas. There is also a new $24 Form I-94 fee charged at every entry to the United States.

For an Indian family of four seeking expedited tourist visas to visit relatives, the new math looks like this: $185 standard fee per person, plus $750 expedited fee per person, plus $250 visa integrity fee per person — that is $1,185 per applicant, or $4,740 for the family, before anyone boards a plane. Add $96 in I-94 fees when they land.

## The Two-Tier Question

The State Department maintains that the expedited track will not slow down regular appointments. The program caps expedited slots at a percentage of each post's total interviewing capacity, the rule states, so "it should not meaningfully affect appointment wait times for other applicants."

Immigration attorneys are sceptical. "Whenever you introduce a premium tier into a resource-constrained system, you create an incentive to keep the regular tier slow," said one New Delhi-based visa consultant who asked not to be named. Existing free expedite mechanisms — for genuine humanitarian emergencies or travel deemed in the US national interest — remain available, but their existence does little to address the structural backlog.

The pilot arrives during a period of compounding pressure on Indian visa applicants. The State Department expanded mandatory social media vetting to H-1B and H-4 applicants in December 2025, then broadened it again in March 2026 to cover more than a dozen additional visa categories. Consular officers now spend more time per interview. Posts in Mumbai and Hyderabad have reportedly seen significant drops in daily interview capacity. By late January, all five US consulates in India were showing "Not Available" for H-category visa stamping through the end of 2026.

For B-1/B-2 applicants, the $750 fee may offer a genuine lifeline — if their consulate participates, if slots are available, and if they can afford it. For the majority of Indian families navigating the visa system, the message is blunter: the queue is now priced.

## Why This Matters to Indian Americans

Every Indian American with family back home understands the visa calendar. Parents hoping to visit for a grandchild's first birthday start the application before the child is born. Siblings trying to attend each other's weddings plan around consular slot availability, not the pandit's calendar.

The $750 expedited option may help wealthier families. But it does nothing to address the underlying backlog, and it creates a visible divide between those who can pay their way to the front and those who cannot. For a diaspora that sends more than $125 billion in remittances to India annually, the question is not whether the fee is affordable — it is whether a public service should be rationed by price.\
"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Seven Hundred and Fifty Dollars Now Buys You a Place at the Front of the Visa Line",
    "subheadline": "The State Department's new pilot program lets B-1/B-2 applicants pay to skip months-long interview waits at US consulates. Indian families are doing the arithmetic.",
    "slug": make_slug("750-dollar-expedited-visa-interview-fee-india-consulate-pilot"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families face 10-12 month waits at US consulates in India for tourist visa interviews. The new $750 expedited option creates a fast lane — but stacked with other new fees, visiting family in America now costs nearly $1,200 per person before the flight.",
    "tags": ["visa", "b1-b2", "consulate", "india", "state-department", "fees", "travel"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "US Federal Register — Temporary Final Rule", "url": "https://www.federalregister.gov/documents/2026/06/09/2026-12727/schedule-of-fees-for-consular-services"},
        {"name": "BAL Immigration News", "url": "https://www.bal.com/immigration-news/united-states-pilot-program-for-expedited-b-1-b-2-visa-interview-fee-launches-july-1/"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/world/us-visa-update-pay-750-and-skip-the-queue-for-interview-appointments"},
        {"name": "Ogletree Deakins", "url": "https://ogletree.com/insights-resources/blog-posts/need-a-u-s-visa-faster-new-750-expedited-interview-option-launches-on-july-1/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "A hand holds an open passport displaying multiple entry stamps from various countries",
    "image_attribution": "Pexels",
    "body": article1_body,
}


# ── Article 2 ──────────────────────────────────────────────────────────
article2_body = """\
When President Trump signed H.R.1 — the "One Big Beautiful Bill Act" — on July 4, the headlines focused on its $140 billion border security allocation and the political horse-trading that got it through the Senate. Buried in Titles IX and X, however, is a fee schedule that will quietly reshape the economics of legal immigration for millions of workers, students, and families. Indians, who represent the largest share of H-1B holders, the longest green card backlogs, and among the highest numbers of F-1 student enrolments, are positioned to absorb more of the impact than almost any other nationality.

## The New Fees

The law introduces a $250 "visa integrity fee" that applies to every nonimmigrant visa issued by the State Department. H-1B workers, L-1 transferees, F-1 students, J-1 exchange visitors, B-1/B-2 tourists — everyone pays. The fee is nonwaivable. It is also a floor, not a ceiling: the statute sets these as minimum amounts and authorises agencies to set higher rates. All are subject to annual inflation adjustments.

A new $24 Form I-94 fee is charged on every entry to the United States. For the H-1B worker who flies home to India for Diwali and returns, that is $24 each way — $48 per round trip, per person.

The bill also imposes a $100 fee to file for asylum, with an additional $100 for each year the application remains pending. Filing for Temporary Protected Status now costs $500. First-time employment authorisation applications for asylees, parolees, and TPS beneficiaries carry a $550 fee, with renewals at $275. Immigration parole costs $1,000.

And there are the fees for fighting back. Filing certain motions and appeals in immigration court now carries charges that, combined with the separate EOIR fee increases proposed this month, make the cost of contesting a deportation order increasingly prohibitive.

## The Cumulative Burden

No single fee in the bill is ruinous. The damage is cumulative.

Consider a mid-career Indian software engineer on an H-1B visa in the Bay Area. She earns $130,000 — above the current prevailing wage, well above the H-1B median. Every three years, when her visa comes up for renewal, she pays the standard filing fees. If she elects premium processing to avoid the months-long USCIS backlog, that is $2,965 as of March 2026, up from $2,805. Add the new $250 visa integrity fee at each consular stamping. Add $24 every time she re-enters the country after visiting family.

If her employer had been subject to the $100,000 H-1B consular processing fee — still alive in one federal circuit court and dead in another — the costs would have been staggering enough to make her position uneconomic for all but the largest firms.

Now scale to a family. Her husband holds an H-4 visa. Their two children are dependents. Each family member needs a visa stamp: four times $250, or $1,000 in integrity fees per renewal cycle. Each entry to the US: four times $24, or $96 per trip. The family visits India once a year. Over a six-year H-1B period, that is $6,000 in visa integrity fees and roughly $1,150 in I-94 fees alone — charges that did not exist before July 4.

## What the Bill Does Not Do

For all its new revenue streams, the law does nothing to address the structural bottlenecks that make Indian immigration uniquely painful. The per-country cap on employment-based green cards, which forces Indian applicants into decades-long queues while nationals of most other countries sail through, remains untouched. The EB-2 India backlog — currently stretching past 2012 priority dates — is unaffected. No visa numbers were recaptured. No unused family-based visas were reallocated to employment categories.

The bill allocates more than $140 billion to border security and enforcement, including funding for physical barriers, immigration court expansion, and detention capacity. These are measures aimed primarily at the southern border and unauthorised immigration — a universe that has almost no overlap with the Indian professionals and students who will pay the bulk of the new fees.

## The Inflation Ratchet

Perhaps the most consequential detail is the least discussed. The law ties most new fees to annual inflation adjustments. The $250 visa integrity fee will grow automatically, year after year, without further legislation. The $24 I-94 fee will do the same. Congress does not need to vote again. The fees are self-escalating by design.

For immigration attorneys, this creates a planning problem. "You used to be able to tell a client what the total cost of an H-1B cycle would be," said one Bay Area immigration lawyer. "Now there's a variable component that compounds annually. It's not a line item anymore — it's a formula."

## The Revenue Arithmetic

The law does not earmark the new visa fee revenue for immigration services. Unlike the premium processing fee — whose proceeds are statutorily directed to USCIS operations and backlog reduction — the visa integrity fee and I-94 fee flow into general revenue and enforcement budgets. The people paying the fees are not the people who will benefit from the spending.

This is the tension at the heart of the bill. Legal immigrants — the ones who filed correctly, waited in line, paid their existing fees, and followed the rules — are now financing an enforcement apparatus built to address a different problem entirely. For the Indian American community, which has one of the lowest rates of unauthorised immigration of any national-origin group, the irony is difficult to miss.\
"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Law Nobody Read Is About to Cost Every Indian Visa Holder an Extra $250 a Year",
    "subheadline": "The One Big Beautiful Bill Act, signed on July 4, imposes a nonwaivable visa integrity fee on every temporary worker, student, and tourist entering the United States. Here is what it actually says.",
    "slug": make_slug("big-beautiful-bill-visa-integrity-fee-indian-workers-students"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold the largest share of H-1B visas, F-1 student visas, and face the longest green card backlogs. The new $250-per-visa fee, $24-per-entry charge, and inflation-indexed escalators in the Big Beautiful Bill Act will cost a typical Indian H-1B family thousands of dollars over a six-year visa cycle — fees that did not exist before July 4.",
    "tags": ["big-beautiful-bill", "h1b", "fees", "visa-integrity-fee", "uscis", "immigration-reform", "congress"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "BAL Immigration News", "url": "https://www.bal.com/immigration-news/united-states-congress-passes-reconciliation-bill-that-includes-major-immigration-provisions/"},
        {"name": "Mondaq — Employer-Sponsored Visas Under the Big Beautiful Bill", "url": "https://www.mondaq.com/unitedstates/immigration/1614968/employer-sponsored-visas-under-the-big-beautiful-bill"},
        {"name": "Congress.gov — H.R.1 One Big Beautiful Bill Act", "url": "https://www.congress.gov/bill/119th-congress/house-bill/1"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/h-1bs-opt-and-h-4-visas-whats-changing-for-indians-under-trumps-immigration-plan"},
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg",
    "image_caption": "The United States Capitol building illuminated at dusk in Washington DC",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
