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
# ARTICLE 1 — $750 expedited B-1/B-2 appointment pilot
# ---------------------------------------------------------------------------
body1 = """For Indians who have spent the better part of a year staring at a "next available appointment" notice many months out, the U.S. State Department has a new offer: pay $750 and skip most of the line. The catch is who it is for — and who it leaves behind.

A Temporary Final Rule published in the Federal Register on June 9 creates a "Nonimmigrant Visa Appointment Expedite Fee" of $750, on top of the standard $185 application fee. Pay it, and an eligible applicant can secure an interview appointment within 10 business days at participating consular posts. The pilot runs from July 1 to December 31, 2026, and is capped — the State Department projects capacity for roughly 25,000 expedited requests across all participating posts worldwide.

## Who can use it — and who cannot

This is the line that matters for most NRIs: the fee is available only to **B-1 (business) and B-2 (tourist) visa applicants**. It does not apply to H-1B, L-1, or other petition-based work visas, and it does not apply to F-1 students. The participating posts have not yet been named; the department says it will publish the list on travel.state.gov before the July 1 launch.

So the Indian software engineer waiting 100-plus days for an H-1B stamping appointment in Hyderabad gets no relief here. The benefit flows to a different, larger group in the diaspora's orbit: **parents and relatives back in India** applying for visitor visas to attend a graduation, see a grandchild, or visit for a wedding. For that cohort, the math can be brutal. B-1/B-2 wait times in India have been among the worst in the world — running roughly five to seven and a half months for an appointment in New Delhi and Mumbai. A $750 fee that compresses that to ten business days is, for a family with a fixed event date, not an outrage but a lifeline.

## What the money does not buy

The State Department has been unusually blunt about the limits. The fee buys a faster appointment slot — nothing else. It does not expedite administrative processing, the security checks that routinely add weeks for some applicants. It does not waive any eligibility requirement. And it explicitly does not improve the odds of approval. An applicant can pay $750, attend the interview in ten days, and still be refused under Section 214(b) like anyone else.

There are no refunds. An applicant who pays the expedite fee and then misses or cancels the appointment forfeits the $750. Applicants must still complete the DS-160, pay the regular fee, and then, if expedited slots are available at their post, pay the $750 within a short hold window to lock it in.

## The diaspora calculus

For Indian Americans, the pilot lands as a mixed signal. On one hand, it is a tacit admission that the system is broken: the consulates in India are buckling under demand with no staffing increase, and Washington's answer is a premium lane rather than more interview windows. Critics will note that this monetizes the dysfunction — those who can pay move up, those who cannot keep waiting.

On the other hand, it is genuinely useful for a specific, recurring NRI headache. The summer travel season, the wedding season, and the 2026 FIFA World Cup matches hosted across U.S. cities are all converging, and the timing of the pilot is no accident. A family in Pune trying to get a parent to the U.S. for a July delivery now has a paid option that did not exist in May.

The open questions are practical. Will any Indian posts make the participating list, given that they are exactly where the pressure is highest? How many of the 25,000 global slots will reach India? And will a six-month "pilot" quietly become permanent infrastructure — a two-tier consular system where the base service is a half-year wait and the real service costs $935 all-in?

For now, the advice for diaspora families is narrow but concrete: if you have relatives applying for a visitor visa with a hard date this fall, watch travel.state.gov in late June for the post list, keep the DS-160 ready, and be prepared to move fast when the expedite window appears."""

# ---------------------------------------------------------------------------
# ARTICLE 2 — FY2027 H-1B: demand collapsed, odds jumped
# ---------------------------------------------------------------------------
body2 = """Here is a sentence almost nobody in the Indian tech diaspora expected to read in 2026: the H-1B lottery just got dramatically easier to win. For the FY2027 cap season, immigration firms are reporting selection rates above 50% — with some employers seeing 65% or higher — against the roughly 35% the government reported a year earlier and the 26% trough of FY2024. The coin flip, for once, is landing in applicants' favor. The reasons it did are not entirely good news.

## The numbers behind the relief

Registrations have fallen off a cliff from their peak. In FY2024, USCIS drowned in nearly 781,000 registrations, many of them duplicate filings gaming the odds. After the agency switched to a beneficiary-centric system that allows only one entry per person, the flood receded — to about 359,000 for FY2026 and, by most estimates, into the 200,000–250,000 range for FY2027.

Fewer registrations chasing the same 85,000 visas mechanically improves everyone's chances. Fragomen, one of the largest corporate immigration firms, said it saw average selection rates above 50% this cycle. That is the highest in the program's modern history.

## Why demand fell

Three forces hollowed out the registration pile, and all three matter to Indian applicants.

First, the **$100,000 supplemental fee** on certain new H-1B petitions, announced in September 2025, scared off the highest-volume filers. IT staffing and consulting firms — many of them India-linked — that once registered tens of thousands of workers abroad slashed their filings rather than face a six-figure bill per case. (A federal judge in Boston vacated that fee on June 8, but the resulting legal whiplash across multiple appellate circuits left employers planning conservatively during the registration window.)

Second, the **wage-weighted selection rule**, effective February 27, changed who bothers to register. Under the new system, a registration gets one to four lottery entries based on its Department of Labor wage level. Entry-level Level I roles — where most fresh Indian graduates on OPT land — get a single entry and roughly a 15% chance, down from the old 30%. Employers stopped registering low-wage, entry-level candidates they knew were now long shots.

Third, **broader tech-sector retrenchment**. Hiring freezes and layoffs across the industry simply reduced the number of new sponsorships companies wanted to file.

## The catch for Indian applicants

A 50%-plus headline selection rate hides a sharp redistribution. The improvement is concentrated at the top of the wage scale. A senior engineer registered at Level IV now enjoys odds north of 60%; the new graduate at Level I is still looking at roughly one chance in seven. The Penn Wharton Budget Model projected the rule would cut Level I's share of selections from 27% to 14% — and that India's overall share of selections would fall by about two percentage points.

In other words: the lottery is easier to win if you are experienced and well paid, and harder if you are young and just out of a U.S. master's program — which describes a very large slice of the Indian diaspora pipeline. The 1.43 lakh Indian students on OPT and STEM OPT who registered this year are disproportionately in exactly the Level I–II bracket that the new math punishes.

## What it means going forward

For Indian professionals plotting an American career, the takeaway is strategic, not just statistical. The path now rewards moving up a wage level before registering — taking the role that pushes you from Level I to Level II or III can matter more than any single year's lottery luck. For employers, the lesson is that the days of mass-registering junior offshore staff are over; the economics now favor sponsoring fewer, higher-paid workers.

And the relief may be temporary. If the $100,000 fee stays vacated and demand rebounds, FY2028 registrations could climb again and selection rates could fall back toward the old norms. This year's unusually friendly odds are a product of a system in flux — a window that the savviest applicants will treat as exactly that."""

# ---------------------------------------------------------------------------
# ARTICLE 3 — EB-2 India "Unavailable", EB-3 downgrade strategy
# ---------------------------------------------------------------------------
body3 = """When the State Department's July 2026 Visa Bulletin listed EB-2 India as "Unavailable," it dropped a word that means exactly what it sounds like: for the rest of this fiscal year, no India-born applicant in the second employment-based category can have a green card approved. The final action date did not retrogress by months — it vanished. But buried two rows down in the same chart is a quieter line that thousands of Indians are now studying closely: EB-3 India is still moving, and for some, that opens a door.

## What actually changed

In the June bulletin, EB-2 India had already retrogressed hard, to a September 1, 2013 cutoff. In July, it went to "Unavailable" — the category is shut for India-chargeable applicants because India's slice of the annual EB-2 numbers has effectively been used up. EB-1 India, meanwhile, sits at an October 15, 2022 final action date.

EB-3 (skilled workers and professionals) tells a different story. For India, the July EB-3 final action date stands at January 1, 2014, and — crucially — the Dates for Filing chart for EB-3 India is at January 15, 2015. That EB-3 filing date is actually *ahead* of where EB-2 India had been before it closed.

That inversion — EB-3 more favorable than EB-2 — is the setup for a maneuver Indian applicants have used before: the downgrade.

## The EB-3 downgrade, explained

Most Indians in the backlog were sponsored in EB-2 because their jobs required an advanced degree or its equivalent. But a worker can hold approved I-140 petitions in more than one category. If an employer files a second I-140 in EB-3 using the *same* PERM labor certification and the same priority date, the applicant keeps their original place in line — but now under EB-3's dates.

When EB-3 India's date is more current than EB-2 India's, that downgrade can mean the difference between being able to file (or keep) an adjustment-of-status application and being frozen out entirely. With EB-2 now "Unavailable" and EB-3 still showing a filing date in 2015, the downgrade is suddenly live for a meaningful group of India-born professionals whose priority dates fall in the 2013–2014 window.

## The fine print that matters

This is not a free lunch, and the diaspora's immigration lawyers are urging caution. A downgrade requires a new I-140 filing, which takes time and money, and EB-3 can itself retrogress — the bulletin's own notes warn that further movement, including categories going "Unavailable," is possible before the fiscal year ends on September 30. Charlie Oppenheim, the former State Department official whose forecasts the community treats as gospel, has repeatedly cautioned that recent India date movements are "artificial," propped up by a policy redirecting unused numbers from other countries, and that a "boomerang effect" of sharp corrective retrogression is likely once that policy lapses.

There is also the adjustment-of-status wrinkle: USCIS confirmed it will require the more restrictive Final Action Dates chart — not the more permissive Filing chart — for employment-based adjustment filings in the relevant window, which limits who can actually submit.

## Why this hits the Indian diaspora hardest

No group is more exposed to these mechanics than India-born professionals. Indians account for the overwhelming majority of the employment-based green card backlog — well over a million people, by most counts — and the per-country cap means they wait far longer than applicants from any other nation. A worker sponsored in 2013 may still be waiting in 2026, their children aging toward the 21-year cliff that strips dependent status, their job mobility frozen by a pending application that cannot move.

For that population, a single word in a monthly bulletin is not bureaucratic trivia — it is whether a decade-long wait inches forward or stalls again. The July bulletin's message is double-edged: EB-2's door is bolted shut for now, but EB-3's is still ajar. Whether to walk through it is a decision best made with a lawyer, a copy of your approved I-140, and a clear-eyed read of how quickly Washington's "artificial" generosity could reverse."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Pay $750, Skip the U.S. Visa Line — but Only if You're a Tourist, Not an H-1B",
        "subheadline": "A new State Department pilot offers a 10-day appointment for B-1/B-2 applicants. For NRI families bringing parents over this summer, it could be a lifeline; for work-visa holders, it offers nothing.",
        "slug": make_slug("us-750-expedite-fee-b1-b2-visa-appointment-pilot-nri-families"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The $750 fast-track only covers visitor visas, so it does nothing for Indians stuck in H-1B stamping backlogs — but it could rescue NRI families trying to bring parents and relatives to the US on a deadline this summer.",
        "tags": ["us visa", "b1 b2", "visa appointment", "state department", "nri", "consulate india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Immigration Analytics (Federal Register analysis)", "url": "https://www.immigration-analytics.com/state-department-launches-750-expedited-visa-interview-pilot/"},
            {"name": "BAL Immigration News", "url": "https://www.bal.com/bal-news/united-states-pilot-program-for-expedited-b-1-b-2-visa-interview-fee-launches-july-1/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/us-to-offer-750-premium-visa-service-for-faster-interview-appointments/"},
            {"name": "Skift", "url": "https://skift.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "An open passport displaying international travel and visa stamps.",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Lottery Just Got Easier to Win. For Indian Grads, There's a Catch",
        "subheadline": "FY2027 selection rates have jumped above 50% as registrations collapse — but the new wage-weighted math quietly steers the relief toward senior, higher-paid workers and away from fresh OPT graduates.",
        "slug": make_slug("h1b-fy2027-selection-rate-jumps-50-percent-demand-collapse-india-grads"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians make up roughly 71% of H-1B beneficiaries, so a sudden jump in selection odds is huge news — but the same rules that improved the odds disproportionately hurt the entry-level Indian graduates who dominate the OPT pipeline.",
        "tags": ["h1b", "h1b lottery", "fy2027", "uscis", "wage-weighted", "opt", "indian students"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen, Del Rey, Bernsen & Loewy", "url": "https://www.fragomen.com/insights/h-1b-cap-lottery-results-fy-2027-what-employers-should-do-now.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/100000-question-navigating-new-h-1b-lottery-system/"},
            {"name": "The Register", "url": "https://www.theregister.com/2025/05/h1b_registrations_dropped/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A software developer working at a dual-monitor coding setup.",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-2 India Just Hit 'Unavailable.' The Workaround Hiding One Row Below",
        "subheadline": "The July 2026 Visa Bulletin shut the second-preference green card door for India-born applicants — but EB-3's still-moving dates have revived an old downgrade strategy worth a hard look.",
        "slug": make_slug("eb2-india-unavailable-july-bulletin-eb3-downgrade-strategy-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the vast majority of the employment-based green card backlog, so when EB-2 India goes 'Unavailable' while EB-3 keeps inching forward, the downgrade maneuver can decide whether a decade-long wait moves at all.",
        "tags": ["green card", "visa bulletin", "eb-2", "eb-3", "india backlog", "i-140", "uscis"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Shusterman Immigration Law (July 2026 Visa Bulletin)", "url": "https://www.shusterman.com/visa-bulletin/"},
            {"name": "Ogletree Deakins / JDSupra", "url": "https://www.jdsupra.com/legalnews/uscis-requires-final-action-dates-for-employment-based-filings-june-2026/"},
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/visa-bulletin/"},
            {"name": "WR Immigration (Charlie Oppenheim analysis)", "url": "https://wolfsdorf.com/india-eb-2-eb-3-visa-bulletin-movement/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b0/United_States_Green_Card_%282023_edition%29.jpg",
        "image_caption": "A United States permanent resident card (green card), 2023 edition.",
        "image_attribution": "Wikimedia Commons",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    if wc < 400:
        print(f"⚠️ SKIP {art['slug']}: only {wc} words")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
