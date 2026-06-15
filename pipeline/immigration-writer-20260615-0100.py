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

article1_body = """The math is blunt. From July 1, a tourist or business visitor who needs a U.S. visa can pay an extra $750 to leap to the front of the interview queue and land an appointment within ten business days. The base application fee of $185 still applies, bringing the cost of jumping the line to roughly $935 before a single document is reviewed.

The State Department published the temporary rule in the Federal Register on June 9. It frames the charge as an "optional premium addition" for B-1 and B-2 applicants, available at a limited number of consular posts that will be named on travel.state.gov before the program launches. The pilot runs through December 31, and the department expects around 25,705 takers a year, generating close to $19.3m. Officials are candid that the fee buys speed, not certainty: it "will not expedite any processing steps, including any time needed for administrative processing," and it does not improve anyone's odds of actually being approved.

## Why The Timing Is Not An Accident

The rule arrives as the FIFA World Cup pulls more than a million foreign visitors toward American stadiums, with the Los Angeles Olympics two years behind it. Wait times for visitor-visa interviews have ballooned under tighter screening — stretching to 16 months in Abu Dhabi while sitting under a month in Istanbul. Washington's answer is not to add interview capacity but to sell a faster lane to those who can afford it.

## What It Means For Indian Families

For the Indian diaspora, this is less abstract than it sounds. The single most common reason an NRI parent or sibling applies for a B-1/B-2 is to attend a wedding, help with a newborn, or simply visit children who have built lives in Sunnyvale or Edison. Indian consular posts have long carried some of the world's heaviest visitor-visa backlogs, and a months-long wait for an interview slot has quietly forced families to miss births, graduations, and funerals.

The $750 lane changes the calculus for those events that cannot be rescheduled. A grandmother who needs to be in California for a birth in eight weeks now has a paid path to an appointment — if her consulate is among the chosen posts. But the attorney quoted in early coverage put the obvious objection plainly: $750 is "a lot of money in this country" and "an exorbitant amount in many of the countries where people are applying." For a family of four, the premium alone runs to $3,000 on top of the standard fees.

There is a quieter sting for the diaspora specifically. The fee creates a two-tier system in which the well-off NRI sponsor can effectively buy a parent's seat at a wedding while a working-class family waits out the standard queue. It formalizes, in dollars, a gap that the visa system was never supposed to price.

## The Fine Print Worth Reading Twice

A few details matter before anyone reaches for a credit card. The pilot is capped — the department says expedited slots will be limited to a percentage of each post's overall interviewing capacity, which is partly why it argues regular applicants will not be pushed further back. The list of participating posts had not been released as of the rule's publication, so there is no guarantee that the consulates in New Delhi, Mumbai, Chennai, Hyderabad, or Kolkata will offer it at all. And the no-cost humanitarian and urgent-travel expedite routes still exist; a genuine medical emergency does not require the $750.

For NRIs, the practical advice is unglamorous: watch travel.state.gov for the post list before July 1, do not pay the premium until your consulate is confirmed as a participating site, and remember that the fee accelerates the appointment, not the approval. If your case lands in administrative processing — the 221(g) limbo that has snared a growing share of Indian applicants — the $750 buys nothing at all.

The broader pattern is hard to miss. Between the $250 visa integrity fee, the $15,000 overstay bonds for some countries, and now a $750 line-jumping charge, the cost of legally visiting the United States is climbing in $250 increments. For a diaspora whose family ties run through a consular interview window, the price of a hug is going up."""

article2_body = """Most of the attention on America's rising visa costs has gone to the headline-grabbing numbers — the $100,000 H-1B proclamation, the $1m "Trump Gold Card." A quieter charge will touch far more Indian families, and many of them do not yet know it exists. It is called the Visa Integrity Fee, it costs at least $250 per person, and it applies to nearly every nonimmigrant visa issued at a U.S. consulate.

The fee was created by the One Big Beautiful Bill Act, signed in July 2025, and took effect for visas issued on or after October 1, 2025. It sits on top of the existing $185 application fee and the various reciprocity and machine-readable-visa charges already in place. It rises annually with inflation. And critically, the law gives the Department of Homeland Security discretion to set it even higher.

## Who Pays, And When

The fee covers most temporary categories processed abroad: B-1/B-2 business and tourist visas, F and M student visas, J exchange visitor visas, and the H, L, O, and P work and performance categories. Visa Waiver Program travelers — largely Western Europe, Japan, Australia — are exempt because they do not need a visa. Canadians and certain diplomatic categories are also outside it. Indians are not. India has never been part of the Visa Waiver Program, which means virtually every Indian national entering on a nonimmigrant visa is now in scope.

There is one piece of good news buried in the structure. Unlike most visa fees, the integrity fee is collected only when a visa is actually issued, not when you apply. If a consular officer denies the application, there is no $250 charge — the applicant never reaches the issuance stage where it is collected. That is a meaningful protection in a year when refusal rates have climbed.

## The Refund That Almost Nobody Will See

The fee is billed as "refundable," and that word is doing a lot of work. In theory, a traveler who obeys every term of the visa — departing on time or properly extending or adjusting status within the visa's validity — can claim the $250 back after the visa expires. In practice, the hurdles are steep. Refunds can be requested only after the visa expires, not after a given trip ends. For a B-2 visitor visa valid up to ten years, that means the $250 stays tied up for a decade. The claimant must prove compliance with passport stamps, I-94 records, and travel itineraries. As of April 2026, DHS had not finalized the refund mechanism, no waivers existed, and there was no evidence anyone had actually been repaid.

For honest travelers, in other words, this is functionally a $250 surcharge with a refund promise that may take ten years to test.

## Why It Lands Hard On The Diaspora

Consider the typical NRI scenario. An Indian-American software engineer in Texas invites both parents to visit for six months to help with a new baby. Two B-2 visas now carry an extra $500 in integrity fees, recoverable — maybe — only after the ten-year visas expire and only if every entry and exit is documented. Multiply that across the millions of family visits that bind the diaspora to relatives back home, and the cumulative cost is enormous.

There is a subtler point for those changing status inside the United States. The fee attaches to visa issuance, not to a change of status. An F-1 student who converts to H-1B while remaining in the country receives an I-797 approval notice, not a new visa stamp, and therefore owes no integrity fee. But the moment that same person travels abroad — to attend a wedding in Delhi, say — and applies for an H-1B stamp to re-enter, the $250 applies. For a diaspora that travels home often, the fee is effectively a tax on visiting family.

## What To Do Now

The practical steps are simple. Budget the $250 per person into any visa plan and do not be surprised when it appears at issuance. Keep every DS-160 confirmation, payment receipt, passport stamp, and I-94 record — the refund, if it ever materializes, will demand them. And weigh the travel-versus-stay tradeoff for anyone mid-status-change: leaving the country to stamp a visa now carries a price it did not before. The integrity fee will not stop anyone from coming. It just makes the trip quietly more expensive every year."""

article3_body = """For the roughly 85,000 people whose H-1B registrations were selected back in March, a far less publicized deadline is now bearing down: June 30. That is the last day employers can file the full FY2027 H-1B petition for a selected beneficiary. Miss it, and the selection — the golden ticket pulled from a pool of hundreds of thousands — simply expires, unused.

USCIS confirmed on March 31 that it had received enough registrations to hit the cap of 65,000 regular visas plus the 20,000 master's-cap exemption. Selected employers were notified and given a filing window of at least 90 days, opening April 1. As that window closes at the end of this month, immigration lawyers are issuing the same reminder they issue every year, with unusual urgency this season: selection is not status. As one attorney put it, being picked "merely authorizes the employer to file" — the petition still has to be filed on time, on the correct form, and ultimately approved before anyone can work.

## The Form Trap

This year carries a procedural landmine. Beginning April 1, USCIS will only accept the 02/27/26 edition of Form I-129, the petition for a nonimmigrant worker. Petitions submitted on an older edition are rejected outright — and a rejection after June 30 means there is no time to refile. For the Indian beneficiaries who make up the overwhelming majority of the H-1B pool, a clerical slip on the form edition can erase a year of waiting as cleanly as a denial.

## The First Live Wage-Weighted Lottery

FY2027 is also the first cycle run under the new wage-weighted selection system, and the results are only now becoming visible in who got picked. Under the rule, the offered salary directly shapes the odds: a registration at Wage Level I (entry-level) gets one entry in the lottery, Level II gets two, Level III three, and Level IV — the highest tier — four. Higher-paid roles were, by design, far more likely to be selected.

For Indian H-1B aspirants, this is a structural shift, not a tweak. The traditional pipeline — a fresh graduate hired at an entry-level wage by a large IT services or consulting firm — sits squarely at Wage Level I, the tier now least likely to win. The model that brought a generation of Indian engineers to the United States through high-volume, lower-wage sponsorship is being quietly squeezed out of the lottery itself. Mid-career and senior Indian professionals at product companies, who command Level III and IV salaries, now hold a meaningful edge over the recent graduate they might once have competed with on equal footing.

## What Selected Beneficiaries Should Be Doing Right Now

If you are an Indian national whose registration was selected, the next two weeks are not the time to assume your employer has it handled. Confirm three things directly with your immigration team. First, that the petition is being filed on the 02/27/26 I-129 edition. Second, that it will be received — not merely mailed — within the window on your specific selection notice, since the period runs from the date on that notice, not a universal cutoff. Third, whether your case is subject to the $100,000 supplemental fee from the September 2025 proclamation. That fee applies when the beneficiary is outside the United States and must be paid after selection but before filing; it does not apply to those already in the U.S. who have maintained lawful status. For an Indian engineer currently on OPT inside the country, that distinction is the difference between a routine filing and a six-figure problem.

## The Bigger Picture For The Diaspora

Even a clean, on-time, approved petition confers nothing before October 1 — employment under an FY2027 H-1B cannot begin earlier. And approval is no longer the formality it once was, with USCIS scrutinizing whether the role qualifies as a specialty occupation, whether the employer-employee relationship is genuine, and whether the beneficiary held lawful status throughout.

Stack the wage-weighted lottery on top of the $100,000 consular fee, the proposed prevailing-wage hike, and an EB-2 India backlog that has just run out of numbers for the year, and the message to the Indian diaspora is consistent. The H-1B is still the front door to America for skilled Indians — but the door is narrower, pricier, and tilted toward those who already earn the most. For the thousands holding a selection notice right now, none of that matters as much as one date. File by June 30, or the ticket is worthless."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Pay $750 to Skip the Visa Line — Washington Just Put a Price on the Family Visit",
        "subheadline": "A new State Department pilot lets B-1/B-2 applicants buy an interview within ten business days. For NRIs whose parents wait months for a slot, speed now has a fee — and it does nothing for your odds of approval.",
        "slug": make_slug("750-dollar-expedited-b1-b2-visa-interview-pilot-nri-families"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian consulates carry some of the world's longest visitor-visa waits, so the new $750 expedited lane directly shapes whether NRI parents and relatives can make it to weddings, births, and funerals on time.",
        "tags": ["b1-b2-visa", "state-department", "visa-fee", "consulate", "nri-travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/story/travel/news/2026/06/10/750-fee-fast-track-us-visa/"},
            {"name": "Federal Register (Department of State)", "url": "https://www.federalregister.gov/documents/2026/06/09/schedule-of-fees-for-consular-services-visa-and-citizenship-services-fee-changes"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/us-to-offer-750-premium-visa-service-for-faster-interview-appointments/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/state-department-750-fee-fast-track-visa-interviews/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33500646/pexels-photo-33500646.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A U.S. Embassy sign on a street, where visitor-visa applicants line up for interview appointments.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The $250 Fee Almost No NRI Family Knows About — and It Hits Every Parent's Visit",
        "subheadline": "The Visa Integrity Fee quietly took effect last October on nearly every nonimmigrant visa issued at a consulate. It is 'refundable' on paper, but the refund may take a decade to test — if it ever arrives at all.",
        "slug": make_slug("250-dollar-visa-integrity-fee-nri-families-refund-explained"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India has never been in the Visa Waiver Program, so virtually every Indian national entering on a B, F, J, H, or L visa now pays the $250 Visa Integrity Fee — a hidden surcharge on the family visits that bind the diaspora to relatives back home.",
        "tags": ["visa-integrity-fee", "obbba", "visa-fee", "b2-visa", "nri-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/us-immigration/u-s-visa-integrity-fee-2026-costs-and-refund-rules-explained/"},
            {"name": "KPMG GMS Flash Alert", "url": "https://kpmg.com/us/en/taxnewsflash/news/2025/07/united-states-visa-integrity-fee-introduced.html"},
            {"name": "Lexology / Manifest Law", "url": "https://www.manifestlaw.com/blog/new-us-visa-integrity-fee-explained"},
            {"name": "AFAR", "url": "https://www.afar.com/magazine/us-visa-integrity-fee-for-foreign-visitors"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32269243/pexels-photo-32269243.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "U.S. dollar bills alongside a passport, illustrating the rising out-of-pocket cost of a U.S. visa.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "June 30 Is the Deadline That Voids Your H-1B Lottery Win — and Most Winners Are Indian",
        "subheadline": "Selection was the easy part. Employers must file the full FY2027 petition by month's end, on the exact right form, or the ticket expires. And this year's first wage-weighted lottery has quietly tilted against the entry-level graduate.",
        "slug": make_slug("h1b-fy2027-june-30-filing-deadline-wage-weighted-lottery-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals make up the overwhelming majority of H-1B selections, so the June 30 filing cutoff, the mandatory 02/27/26 I-129 form edition, and the new wage-weighted odds all land hardest on Indian engineers — especially recent graduates at entry-level wages.",
        "tags": ["h1b", "uscis", "fy2027", "wage-weighted-lottery", "i-129"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/uscis-completes-h-1b-lottery"},
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/alerts/fy-2027-h-1b-initial-registration-selection-process-completed"},
            {"name": "Lexology", "url": "https://www.lexology.com/library/detail.aspx?g=uscis-opens-fy-2027-h-1b-cap-registration-key-updates-for-employers"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A software developer at a dual-monitor setup, the kind of specialty role most H-1B petitions are filed for.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   words: {wc} | {art['headline'][:50]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
