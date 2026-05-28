#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-27 17:00 PDT batch."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── Article 1: Gold Card Visa Flop ──────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "338 Applications, One Approval — Trump's Gold Card Is the Most Expensive Rejection Letter in Immigration History",
        "subheadline": "The $1 million pay-to-play visa was supposed to replace the EB-5 and attract the world's richest immigrants. Seven months in, it has produced exactly one green card.",
        "slug": make_slug("trump-gold-card-one-approval-indian-investors-eb5"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Wealthy Indian families weighing the Gold Card against the EB-5 are choosing neither — and the math explains why.",
        "tags": ["gold-card", "eb-5", "investor-visa", "immigration", "trump"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Polymarket Gold Card Tracker", "url": "https://polymarket.com"},
            {"name": "Manifest Law", "url": "https://manifestlaw.com/blog/trump-gold-card-explained/"},
            {"name": "GG2.net", "url": "https://www.gg2.net"},
            {"name": "Wikipedia - Trump Gold Card", "url": "https://en.wikipedia.org/wiki/Trump_Gold_Card"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7221576/pexels-photo-7221576.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Seven months after President Trump launched the Gold Card visa program with a promise to attract "the best and brightest," the numbers tell a different story. Of 338 people who submitted applications, 165 paid the non-refundable $15,000 processing fee. Exactly one has been approved.

The Gold Card, formalized through Executive Order 14351 in September 2025 and opened for applications in December, offers a straightforward proposition: pay $1 million to the Department of Commerce, skip the evidence requirements for an EB-1 or EB-2 green card, and get expedited processing. Corporations can sponsor employees for $2 million. Each additional family member costs another $1 million plus another $15,000 fee.

Commerce Secretary Howard Lutnick predicted the program would raise over $100 billion. Through late May 2026, it has generated roughly $2.5 million in processing fees and exactly $1 million in actual contributions.

## The Indian Investor Calculation

For wealthy Indians eyeing American residency, the Gold Card arithmetic is brutal. A family of four — two parents, two children — would need $4 million in non-refundable contributions plus $60,000 in processing fees. The money is classified as a "gift," meaning it is not tax-deductible and generates no return. Compare that to the EB-5, which requires an $800,000 investment in a job-creating project — money that, at least in theory, comes back.

The Gold Card also offers no escape from the per-country backlog. Because it operates within existing EB-1 and EB-2 visa quotas — no new numbers were created — Indian applicants still face the same priority date queues. An Indian national who pays $1 million for a Gold Card petition approval could still wait years for a visa number to become available.

"The program is essentially asking people to pay a million dollars for the privilege of waiting in the same line," said one Bay Area immigration attorney who advises Indian tech executives. "The EB-5 at least creates an investment. The Gold Card creates a receipt."

## Why the EB-5 Still Wins

Indian EB-5 filings surged 400% after the 2022 Reform and Integrity Act created reserved visa categories — rural, high-unemployment, and infrastructure projects — with their own separate queues. An Indian investor putting $800,000 into a rural TEA project can potentially sidestep the crushing EB-5 unreserved backlog (currently stuck at May 2022 for India).

The Gold Card offers no such structural advantage. It feeds into the same EB-1/EB-2 pipeline where India-born applicants already face decade-long waits.

There is one scenario where the Gold Card makes sense: an applicant from a country with no backlog who wants a green card faster than the standard EB-1 evidence-gathering process. For someone born in Canada or Brazil with a million dollars to spare, the math works differently. For Indians, it does not.

## The Platinum Card Nobody Asked For

Adding to the confusion, the administration has floated a "Platinum Card" tier requiring a $5 million contribution. It would allow holders to spend up to 270 days per year in the U.S. without being subject to U.S. taxation on non-U.S. income. No further details have been released.

Immigration attorneys note that the Platinum Card would essentially recreate a benefit that already exists through careful structuring of nonimmigrant visa status and tax residency planning — but at a price point that makes the Gold Card look like a bargain.

## What It Means for NRIs

The Gold Card program's failure tells a story about what wealthy immigrants actually want. They do not want to make gifts to the U.S. government. They want predictability: a clear timeline, a recoverable investment, and a path that does not dead-end at per-country caps.

For Indian families with the resources to consider a $1 million immigration expenditure, the options remain what they were before the Gold Card existed: EB-5 through a reserved category, EB-1A with legitimate extraordinary ability evidence, or the National Interest Waiver — though NIW approval rates have cratered to 35% this year.

The Gold Card was supposed to simplify the choice. Instead, it added a very expensive wrong answer to the multiple-choice test."""
    },

    # ── Article 2: EB-2 India Retrogression ─────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-2 India Just Lost Ten Months of Progress Overnight — And the State Department Says It Could Get Worse",
        "subheadline": "The June 2026 Visa Bulletin pushed the EB-2 India priority date from July 2014 back to September 2013. For thousands of Indian professionals, cases that were finally moving forward have stopped cold.",
        "slug": make_slug("eb2-india-retrogression-june-visa-bulletin-ten-months"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders who filed I-485 adjustment applications in April and May 2026 now face paused cases and uncertain timelines through at least October.",
        "tags": ["eb-2", "visa-bulletin", "retrogression", "green-card", "india-backlog"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "State Department June 2026 Visa Bulletin", "url": "https://travel.state.gov"},
            {"name": "ImmiOne Retrogression Analysis", "url": "https://immione.com/june-2026-visa-bulletin-analysis-predictions/"},
            {"name": "USCIS Adjustment of Status Filing Charts", "url": "https://www.uscis.gov"},
            {"name": "Immigration Boston Analysis", "url": "https://immigrationboston.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The State Department's June 2026 Visa Bulletin, released May 13, delivered the kind of number that makes immigration attorneys reach for their phones. The EB-2 India Final Action Date — the cutoff that determines which green card applications can be approved — retrogressed by more than ten months, moving from July 15, 2014 back to September 1, 2013.

That is not a typo. Ten months of accumulated progress, erased in a single bulletin.

The EB-1 India category also took a hit, retrogressing 107 days to December 15, 2022. But the EB-2 move is the one reverberating through Indian professional communities across the country, because EB-2 is where the vast majority of Indian H-1B holders file their green card petitions.

## What Actually Happened

Every month, the State Department publishes the Visa Bulletin to regulate how many green cards get processed. When demand in a category exceeds the available visa numbers, the department pulls the priority date backward — a retrogression — to slow approvals to match supply.

The June bulletin's EB-2 India retrogression was not gradual. It was a cliff. Anyone with a priority date between September 1, 2013 and July 15, 2014 who had filed an I-485 adjustment of status application in recent months now has a paused case. Their application remains pending — EAD work permits and Advance Parole travel documents stay valid — but final green card approval is frozen until the priority date becomes current again.

The structural cause is familiar: per-country caps limit any single nation to roughly 7% of employment-based green cards, regardless of demand. India accounts for the largest share of EB-2 petitions by a wide margin, creating a backlog that the State Department periodically throttles through retrogression.

## The State Department's Warning

What makes the June bulletin especially unsettling is the language in Section E, where the State Department issues forward guidance. The department warned that "further retrogressions in these categories, or making the categories unavailable, may be necessary before the fiscal year ends on September 30, 2026."

"Unavailable" is the nuclear option in visa bulletin terminology. It means zero approvals in that category for the remainder of the fiscal year. The last time EB-2 India went unavailable mid-year, it took months after the October 1 fiscal year reset for meaningful forward movement to resume.

Immigration analysts are tracking three scenarios for the remaining four months of FY 2026:

**Best case**: June dates hold through September. EB-2 India stays at September 1, 2013, and the October 1 reset brings modest forward movement with FY 2027 allocations.

**Likely case**: EB-2 India retrogresses further into 2013, or briefly goes unavailable in August or September. The October reset then restores availability at significantly retrogressed dates.

**Worst case**: Both EB-1 India and EB-2 India go unavailable before September 30. All I-485 adjudications in those categories freeze for weeks.

## The EB-3 Escape Valve

One small bright spot: EB-3 India advanced modestly to December 15, 2013. For applicants whose priority dates fall in the narrow window where EB-3 is current but EB-2 is not, downgrading from EB-2 to EB-3 — a process called "porting" — may allow their cases to continue processing.

This is not a painless trade. EB-3 has its own backlog, and downgrading resets certain clock assumptions. But for someone whose EB-2 case just went from "almost approved" to "indefinitely paused," the calculation shifts.

## What Indian Professionals Should Do Now

Immigration attorneys advise three immediate steps:

**Check your priority date band.** If your EB-2 India priority date falls between September 1, 2013 and July 15, 2014, your I-485 final adjudication is paused. Your EAD and AP remain valid through their expiration dates.

**Talk to your employer's immigration counsel.** Corporate immigration teams should be sending proactive communications to affected employees. If yours has not, ask. Confirm that your EAD and AP renewals will proceed on their normal schedule regardless of the visa retrogression.

**Model the worst case.** If EB-2 India goes unavailable before September 30, plan for a multi-month freeze on final approvals. That does not mean you lose your place in line, but it does mean your timeline just got longer.

The June bulletin is a reminder of what every Indian green card applicant already knows: the system was not designed for the volume of talent India sends to the United States. Until Congress changes the per-country cap structure — and nothing in the current legislative environment suggests that is imminent — these retrogressions are not aberrations. They are the system working exactly as designed."""
    },

    # ── Article 3: EB-5 Regional Center Expiration ──────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "The EB-5 Clock Is Running Out — Four Months Until the Regional Center Program Expires and Nobody in Congress Is Talking About It",
        "subheadline": "The EB-5 Regional Center Program, the primary vehicle for Indian investor immigration, sunsets on September 30, 2026. Reauthorization is nowhere on the legislative calendar.",
        "slug": make_slug("eb5-regional-center-expiring-september-indian-investors"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian EB-5 investors who haven't filed their I-526 petitions by September 30 risk losing access to reserved visa categories that were their fastest path around the India backlog.",
        "tags": ["eb-5", "regional-center", "investor-visa", "immigration", "reauthorization"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AILA EB-5 Reauthorization Analysis", "url": "https://www.aila.org"},
            {"name": "IIUSA Regional Center Data", "url": "https://iiusa.org"},
            {"name": "Financial Express / LCR Capital", "url": "https://lcrcapital.com"},
            {"name": "EB5 BRICS - Indian Investor Trends", "url": "https://eb5brics.com"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1467589/pexels-photo-1467589.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The EB-5 Regional Center Program — the mechanism through which most Indian investors pursue American green cards — expires on September 30, 2026. Congress reauthorized it in March 2022 through the EB-5 Reform and Integrity Act, giving the program a five-year runway. That runway ends in four months, and there is no reauthorization bill on the floor, no markup scheduled, and no visible urgency on Capitol Hill.

This is not the first time the EB-5 program has faced an expiration cliff. Between 2015 and 2022, it was reauthorized through a series of short-term continuing resolutions, lapsing entirely for 20 months between June 2021 and March 2022. During that lapse, USCIS stopped processing Regional Center petitions, stranding thousands of investors mid-application.

The question Indian investors should be asking is not whether Congress will reauthorize the program eventually. It almost certainly will — the EB-5 has created over 85,000 American jobs and attracted $12 billion in foreign capital since 1990. The question is whether it will do so before the September 30 deadline or let it lapse again.

## Why the Regional Center Matters for Indians

The 2022 reforms created three reserved visa categories within EB-5: rural projects (20% of visas), high-unemployment areas (10%), and infrastructure projects (2%). These reserved categories have their own separate queues — meaning Indian investors who file through a rural or high-unemployment project can bypass the crushing unreserved EB-5 backlog, where India's Final Action Date sits at May 2022.

Indian EB-5 filings surged 400% after these reserved categories went live. For a Bangalore tech executive or a Mumbai industrialist with $800,000 to invest, the rural EB-5 path offered something no other category could: a green card timeline measured in years, not decades.

If the Regional Center Program lapses, those reserved categories go dark. Direct EB-5 investments — where the investor personally manages a business creating 10 jobs — remain available because they are authorized by statute, not the Regional Center provision. But most Indian investors use Regional Centers precisely because they do not want to run an American business. They want to invest in a vetted project, file their petition, and wait for their green card.

## The Grandfathering Question

The 2022 reauthorization included grandfathering provisions for investors who had already filed I-526 petitions before any future lapse. If you have a pending I-526 as of September 30, 2026, your case should continue processing regardless of what happens to the program.

But "should" carries a lot of weight in immigration law. During the 2021-2022 lapse, USCIS initially halted all Regional Center adjudications, even for petitions filed years earlier. It took litigation — the *Behring Regional Center v. Mayorkas* lawsuit — to clarify that the lapse did not retroactively invalidate pending cases.

Immigration attorneys are advising clients to file I-526 petitions before September 30 as an insurance policy, even if the investment project's full documentation is not complete. A pending petition creates a foothold that a post-lapse filing cannot.

## The Congressional Landscape

The EB-5 program's legislative fate is tangled in broader immigration politics. The "One Big Beautiful Bill" currently making its way through the Senate touches immigration only at the margins — primarily through fee increases and the H-1B $100,000 surcharge. It does not address EB-5 reauthorization.

A standalone EB-5 bill could move through the Commerce or Judiciary committees, but neither has signaled urgency. The program's natural constituency — real estate developers, regional economic development agencies, and immigration attorneys — has lobbied for long-term reauthorization through 2032, but that effort has not yet produced a vehicle bill.

The likeliest scenario, based on the program's own history, is a last-minute attachment to an appropriations bill or continuing resolution in September. That is cold comfort for an Indian investor trying to make a decision in June.

## What Indian Investors Should Do Now

**If you are already invested through a Regional Center**: Confirm with your immigration attorney that your I-526 petition is filed or will be filed before September 30. A pending petition is your best protection against a lapse.

**If you are considering an EB-5 investment**: The window to file through a Regional Center project — particularly a rural or high-unemployment reserved category — is closing. The application process takes weeks of due diligence, fund transfers, and documentation. Starting in August is probably too late.

**If you are weighing EB-5 against the Gold Card**: The Gold Card ($1 million, non-refundable gift, no investment return, same per-country backlog) is not a substitute for the EB-5 ($800,000, recoverable investment, potentially faster path through reserved categories). The Gold Card program has produced one approval in seven months. The EB-5, for all its complexity, has a decades-long track record.

The September 30 deadline is not theoretical. The last time Congress let the program lapse, Indian investors spent 20 months in limbo. The difference this time is that the 2022 reforms created reserved categories worth protecting — and a lapse would take them off the table at the exact moment Indian demand for them is at its peak."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
