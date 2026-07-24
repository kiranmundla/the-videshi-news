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

art1_body = """A misplaced signature has never been a great way to lose a job offer, a house, and a decade of accrued green-card seniority. From July 10, it could be.

That is the date a new USCIS rule takes effect, handing officers far broader authority to reject H-1B petitions and green-card filings outright when a signature is judged "deficient." Until now, a stray initial, a digital scrawl, or a stamp where a wet-ink autograph belonged would usually trigger a Request for Evidence — an annoying but survivable delay that let the employer fix the error and refile. After July 10, the same slip can draw an immediate denial.

## What Actually Changes

The rule narrows what counts as an acceptable signature to two forms: a handwritten original, or an authorized electronic signature applied through a sanctioned process. Anything else — a typed name, a photocopied signature block, a digital image pasted into a PDF, an autopen — risks being treated as no signature at all.

That sounds like housekeeping. It is not. Under the prior regime, USCIS treated most signature problems as curable. Officers were expected to issue an RFE and give petitioners a window to respond. The new posture flips the default: a deficient signature becomes a basis for denial rather than a request to fix. For a category of filing that now routinely carries five- and six-figure costs, the margin for clerical error has collapsed.

## Why Indians Feel It First

Indian professionals are the largest single bloc in the H-1B pipeline — by recent counts, around 71% of approved petitions — and they dominate the employment-based green-card backlog. They are also the population most likely to be filing through large employers and outsourcing firms, where petitions move in bulk and signatures are gathered through templated workflows. Those high-volume processes are exactly where a non-compliant electronic signature can slip in unnoticed across hundreds of cases at once.

The timing compounds the risk. The new rule lands in the middle of an unusually expensive and treacherous filing season: a wage-weighted selection system that replaced the lottery, a $100,000 fee fight winding through the courts, a May memo recasting adjustment of status as a discretionary "grace," and the June 30 deadline to file H-1B petitions for workers meant to start on October 1. An applicant who clears the wage threshold, pays the fee, and beats the deadline can still be sunk by a signature their employer's HR portal generated incorrectly.

## The Cost of a Denial Is No Longer Just Delay

Under the RFE model, a botched signature cost time. Under the denial model, it can cost status. For someone on an expiring H-1B, a denied extension does not pause the clock — it can end work authorization and start the countdown on the 60-day grace period. For a green-card applicant deep in the EB-2 or EB-3 queue, a denied filing can mean losing a place in line that took years to earn, with no guarantee the priority date survives a refile.

Immigration attorneys are already advising employers to audit their signature workflows before the deadline — to confirm that whatever e-signature platform they use produces an "authorized" signature under the new standard, and to default to wet ink where there is any doubt. For petitions filed close to July 10, lawyers are urging a belt-and-suspenders approach: handwritten signatures, scanned at full resolution, with no autopen anywhere in the chain.

## What to Watch

The practical question is how aggressively officers apply the new discretion. A narrow reading — reserving denials for genuinely absent or fraudulent signatures — would make the rule a formality. A broad reading, in which any unfamiliar e-signature format draws a denial, would turn a procedural footnote into one of the season's most consequential traps.

USCIS has framed the change, like much else this year, as restoring integrity and reducing administrative burden. For the Indian engineer whose extension is bundled into a corporate batch filing, the burden has simply moved: from the agency that once asked for a correction, to the applicant who now has one chance to get it right."""

art2_body = """For a decade, the advice handed to Indians stuck in the green-card queue had a reliable escape clause: if EB-2 stalls, downgrade to EB-3. This month, that escape clause is the only thing still moving.

The July 2026 Visa Bulletin made EB-2 India "Unavailable" — not retrogressed, not slowed, but closed, with no immigrant visas issued in the category through September 30. EB-1 India, long the premium fast lane for managers and the genuinely exceptional, retrogressed to October 15, 2022. Yet buried in the same bulletin, EB-3 India crept forward to a final action date of January 1, 2014. A nudge of roughly two weeks. In a year of walls going up, it is the only door that opened at all.

## The Mechanics of a Downgrade

EB-2 covers advanced-degree professionals; EB-3 covers skilled workers and professionals with a bachelor's. EB-2 is, on paper, the higher category — and for years it moved faster for Indians, which is why so many filed there. When the categories invert, as they have now, an applicant with an approved or pending EB-2 petition can have their employer file a second I-140 in EB-3, keeping the original priority date. That date is the asset; the category is just the lane it travels in.

So when EB-3 India holds a January 2014 final action date and EB-2 India shows a blank, an applicant whose priority date sits in, say, late 2013 can suddenly file or approve an adjustment under EB-3 that is flatly impossible under EB-2. The downgrade is not a gimmick. For a sliver of the backlog, it is the difference between a green card this year and another indefinite wait.

## Why This Is a Trap as Much as an Opportunity

The catch is that EB-3 India's progress is fragile, and the people who track these numbers say it is also artificial. Former State Department visa chief Charlie Oppenheim has argued that recent India movement is being propped up by an administration policy that suppressed demand from 75 other countries, freeing up otherwise-unused numbers for India and China. When that policy ends — and no one knows when — he warns of a "boomerang effect": the suppressed demand returns, lands at the front of the line with early priority dates, and India snaps back to its punishing per-country limits.

In plain terms: the EB-3 window that looks open today could slam shut, and the applicants who downgraded could find themselves no better off, having paid for a second petition to chase a date that evaporates. The State Department has itself flagged that further retrogressions, or more categories going "Unavailable," may be necessary before the fiscal year ends.

## What It Means for the Diaspora

For the hundreds of thousands of Indians warehoused in the employment-based backlog — many of them software engineers, doctors, and researchers who have lived, worked, and paid taxes in the United States for fifteen years or more — the July bulletin is a study in cruel arithmetic. The "better" categories are frozen or sliding backward. The only forward motion is in the category most people were told to graduate out of.

The decision facing applicants is whether to downgrade now and grab a possible filing window, or hold in EB-2 and bet that fiscal year 2027, beginning October 1, brings fresh numbers and a reset. Immigration lawyers are split, precisely because the movement is policy-driven rather than demand-driven, and policy can change with a memo.

## The Bigger Picture

The downgrade play exists only because the system is broken in a specific, Indian-shaped way. Per-country caps written into 1990s law mean a nation supplying the bulk of America's high-skilled tech workforce receives the same 7% slice as countries sending a handful. Until Congress touches those caps — and a diaspora delegation spent last week on Capitol Hill asking it to — Indians will keep gaming the categories against one another, downgrading, upgrading, and downgrading again, in a queue that for many will outlast the visas that put them in it."""

art3_body = """The Indians who saw the EB-2 wall coming had a plan. Some had pivoted to EB-1, the "extraordinary ability" and multinational-manager fast lane. Others had written six-figure checks into EB-5, the investor visa that promised to skip the employment backlog entirely. The July 2026 Visa Bulletin closed both of those exits in a single page.

EB-2 India going "Unavailable" was the headline most people expected. Less noticed, and arguably more telling, was what happened to the categories that were supposed to be the way around it. EB-1 India retrogressed to October 15, 2022 — a backward jump that pushes the bar earlier and locks out applicants who had counted on the premium category staying ahead of the pack. And EB-5 unreserved India, the investor route, was declared exhausted for the rest of fiscal year 2026.

## When the Side Doors Close Too

The logic of the backlog has always been that money or exceptional credentials could buy a way past the wait. EB-1 rewards the genuinely outstanding — award-winning researchers, executives, athletes. EB-5 rewards capital: invest the required sum in a qualifying U.S. enterprise, create the jobs, and historically jump much of the line. Both were pressure-release valves for a community that knew EB-2 and EB-3 were measured in decades.

This month both valves are shut. EB-5 unreserved India hit its annual limit and went unavailable, meaning no immigrant visas or final approvals in that lane until the fiscal year resets on October 1. EB-1 India did not merely stall; it moved backward, so even applicants who thought their 2022 priority date was safe now find themselves on the wrong side of the cutoff.

## The One Lane Still Open

Tellingly, the EB-5 set-aside categories — rural, high-unemployment, and infrastructure projects, carved out under the program's 2022 overhaul — remained current for India. Those reserved buckets were designed precisely to stay available when the main investor pool fills, and they are now among the very few employment-based options offering immediate movement for Indian nationals. For investors with the means and appetite, the message is blunt: the unreserved route is closed, but the targeted set-asides still work.

That is cold comfort to the EB-1 professional who does not have a half-million dollars to redirect, or to the EB-2 holder who was eyeing an upgrade that has now retreated out of reach.

## Why It Lands So Hard on Indians

The set-aside detail aside, the broader story is that "Rest of World" demand is now consuming nearly all available employment-based numbers, leaving India's pro-rated slice exhausted across multiple categories at once. Analysts expect EB-2 and EB-3 India to see extremely limited movement in fiscal year 2027 as well. The fast lanes were the diaspora's hedge against exactly this scenario — and the hedge failed in the same month the main route did.

For Indian Americans, the cumulative effect is a system where every employment-based path is either frozen, retrogressing, or open only to those who can write a large enough check into a specific kind of project. The doctors, engineers, and founders who built careers on the assumption that merit or money would eventually clear the line are discovering that this year, for India, almost nothing clears it.

## What's Next

The reset on October 1 is the next real inflection point, when fiscal year 2027 numbers become available and categories that went dark can, in theory, reopen. But the same forces — surging worldwide demand, rigid per-country caps, and an administration reshaping discretion at every step — will still be in place. The structural fix everyone in the backlog actually needs lives in Congress, in the per-country caps that determine why a nation supplying most of America's high-skilled tech talent is treated, for visa math, like any other. Until that changes, the side doors will keep closing as fast as applicants find them."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Bad Signature Used to Mean a Delay. After July 10, It Can Mean a Denial",
        "subheadline": "A new USCIS rule lets officers reject H-1B and green-card filings outright over a 'deficient' signature, scrapping the second chance an RFE once offered — in the most expensive filing season on record.",
        "slug": make_slug("uscis-signature-rule-july-10-deficient-denial-h1b-green-card-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians file the bulk of H-1B petitions and dominate the green-card backlog, often through high-volume corporate workflows where a non-compliant e-signature can now sink a case outright instead of drawing a fixable RFE.",
        "tags": ["h1b", "uscis", "green-card", "signature-rule", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge — H-1B Visa Rules 2026", "url": "https://www.visaverge.com/news/state-dept-official-says-h-1b-visa-rules-are-global-not-targeted-at-india/"},
            {"name": "USCIS Newsroom", "url": "https://www.uscis.gov/newsroom"},
            {"name": "USA Today — How Trump's immigration policies hurt legal immigration", "url": "https://www.usatoday.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8730991/pexels-photo-8730991.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Hands signing documents at a desk in a business setting",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-2 India Is Dark. The Only Green-Card Lane Still Moving Is the One Everyone Was Told to Leave",
        "subheadline": "With EB-2 India unavailable and EB-1 retrogressing, the July visa bulletin leaves EB-3 — and the old downgrade play — as the lone path inching forward. Analysts warn it is a fragile, policy-driven window.",
        "slug": make_slug("eb3-downgrade-india-july-2026-visa-bulletin-eb2-unavailable-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Hundreds of thousands of Indians warehoused in the employment-based green-card backlog must now decide whether to downgrade from EB-2 to EB-3 to grab a rare filing window, or hold and risk the 'boomerang' when artificial movement reverses.",
        "tags": ["green-card", "eb2", "eb3", "visa-bulletin", "backlog", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Capitol Immigration Law Group — July 2026 Visa Bulletin", "url": "https://cilawgroup.com/"},
            {"name": "WR Immigration — EB-2 India Unavailable Through September 30, 2026", "url": "https://wolfsdorf.com/"},
            {"name": "VisaVerge — July 2026 Visa Bulletin: EB-2 India Backlog Hits Limits", "url": "https://www.visaverge.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b0/United_States_Green_Card_%282023_edition%29.jpg",
        "image_caption": "A United States permanent resident card, 2023 edition",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indians Built Escape Routes Around the Green-Card Backlog. The July Bulletin Closed Them All at Once",
        "subheadline": "EB-1 retrogressed and EB-5 unreserved India went unavailable in the same month EB-2 went dark — shutting the merit and money fast lanes the diaspora used to bypass the wait. Only the EB-5 set-asides remain open.",
        "slug": make_slug("eb1-retrogression-eb5-unreserved-india-unavailable-july-2026-fast-lanes-closed"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals and investors who hedged against the EB-2 wall by pivoting to EB-1 or EB-5 now find both routes frozen the same month, leaving only the EB-5 rural and infrastructure set-asides as a still-current path to a green card.",
        "tags": ["green-card", "eb1", "eb5", "visa-bulletin", "investor-visa", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VisaVerge — July 2026 Visa Bulletin: EB-2 India Backlog Hits Limits", "url": "https://www.visaverge.com/"},
            {"name": "WR Immigration — June 2026 Visa Bulletin: Sharp Retrogression for India EB-1 and EB-2", "url": "https://wolfsdorf.com/"},
            {"name": "Capitol Immigration Law Group — July 2026 Visa Bulletin", "url": "https://cilawgroup.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center on Jamaica Avenue in New York",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": art3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
