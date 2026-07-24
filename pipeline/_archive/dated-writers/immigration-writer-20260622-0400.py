#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for cand in [Path.home()/".env.supabase", Path.home()/"workspace"/".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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
# ARTICLE 1 — July 2026 Visa Bulletin: EB-2 India Unavailable
# ---------------------------------------------------------------------------
body1 = """The July 2026 Visa Bulletin confirms what immigration lawyers had been bracing for since spring: EB-2 India is now marked **"Unavailable"** for the rest of the fiscal year, and the EB-1 and EB-5 categories that many Indians had quietly pivoted to are retrogressing too. For the largest single nationality in America's employment green-card queue, the final quarter of fiscal 2026 is shaping up to be the most contractionary month in years.

The Department of State exhausted EB-2 India's annual allotment on May 22. With no numbers left, the Final Action Date for the category simply disappears from the chart until the fiscal year resets on October 1. For the tens of thousands of Indian professionals sitting on approved I-140 petitions, it means adjustment-of-status applications cannot be approved — and no new ones can be filed in the Final Action column — for at least three months.

## What actually changed

The numbers tell the story bluntly. EB-2 India moved to "U" (Unavailable) from a Final Action Date of September 1, 2013 in June. EB-1 India retrogressed two months, sliding from December 15, 2022 back to October 15, 2022. And EB-5 Unreserved India is flagged by analysts as the single highest risk for retrogression or unavailability in the coming month.

For the Dates for Filing chart — the one that governs when you can submit an I-485 — EB-2 India and EB-3 India both held at January 15, 2015, unchanged from June. But USCIS has used the more restrictive Final Action Dates chart for employment-based adjustment filings for three consecutive months now, which means the filing chart's relatively generous dates are academic for anyone trying to lodge a fresh application.

## Why the dates moved forward, then snapped back

The cruel irony is that India's recent "progress" was never real. Former State Department official Charlie Oppenheim has described the forward movement Indian applicants saw between late 2025 and spring 2026 as "completely artificial" — a side effect of the administration's restrictive visa-processing policy toward 75 countries, which reduced demand elsewhere and freed up numbers that spilled over to India and China.

That spillover was always borrowed time. Once the policy ends, Oppenheim warns, there will be a "boomerang effect": Rest-of-World applicants will return to the front of the line with early priority dates, and India and China will again be squeezed under their low per-country caps. The pattern mirrors the post-COVID years, when employment-based limits temporarily ballooned to 281,000 in FY2022 before the inevitable corrective retrogression.

## What it means for the diaspora

If you are an Indian national on an H-1B with an approved I-140 and a priority date you thought was finally getting close, the practical upshot is patience — and vigilance. Your place in line is not lost; the visa numbers are simply gone until October. An I-485 already filed and pending continues to confer work authorization and advance parole on renewal, so day-to-day life does not change. What stops is the final approval.

The harder reality is structural. With EB-2 India sitting on a backlog that stretches more than a decade, "Unavailable" months are no longer anomalies — they are becoming a routine feature of the fiscal calendar's final quarter, when demand catches up to supply. Families weighing whether to switch employers, downgrade from EB-2 to EB-3 to chase a marginally better date, or hold steady should treat the October reset as the next genuine inflection point, not July or August.

For now, the advice from practitioners is unglamorous: keep your underlying H-1B status airtight, keep your I-140 priority date protected, and do not make irreversible career decisions on the strength of a date that the State Department itself describes as artificial.

## What's next

The August 2026 bulletin, due in mid-July, will reveal whether EB-1 India retrogresses further and whether EB-5 Unreserved India joins EB-2 in the "Unavailable" column. The real story, though, begins on October 1, when fiscal 2027 numbers become available and the queue lurches forward again — until the next annual limit runs dry."""

# ---------------------------------------------------------------------------
# ARTICLE 2 — $100,000 H-1B fee struck down, now on appeal
# ---------------------------------------------------------------------------
body2 = """The $100,000 fee that turned the H-1B visa from a routine corporate expense into a six-figure gamble has been struck down — for now. A federal judge in Boston vacated the charge on June 8, calling it an unlawful tax that President Trump had no authority to impose without Congress. Four days later he paused his own ruling while the government appeals, leaving Indian professionals and the companies that hire them in a familiar place: legally vindicated, practically uncertain.

For the diaspora that supplies nearly three-quarters of all H-1B recipients, the stakes are hard to overstate. The fee, announced last September through Presidential Proclamation 10973, applied to new petitions requiring consular processing — including, the White House confirmed, the entire 2026 lottery. At a stroke it priced out exactly the early-career Indian engineers, doctors and researchers the program was built to admit.

## What the judge ruled

US District Judge Leo Sorokin, an Obama appointee, concluded that the $100,000 charge "imposes a tax on H-1B petitions without the requisite delegation by Congress." The substance of the payment, he wrote, "reveal[s] that it is a tax, regardless of what the payment is called." He found the proclamation violated both the separation of powers and the Administrative Procedure Act, having been implemented in an "arbitrary and capricious" manner.

Sorokin leaned on the Supreme Court's February decision striking down Trump's emergency-powers tariffs. If the president could not levy tariffs under a national-emergency statute, the logic ran, he likewise could not levy a six-figure visa tax under immigration law. The ruling came in a suit brought by California and 19 other Democratic-led states, who argued the fee would gut hospitals, universities and tech firms that depend on skilled foreign labor.

## A split among the courts

Here is where it gets messy. Sorokin's decision directly contradicts a December 23 ruling by Judge Beryl Howell in Washington, D.C. — also an Obama appointee — who found the fee justified by "a straightforward reading of congressional statutes giving the President broad authority to regulate entry." Howell was weighing a challenge from the U.S. Chamber of Commerce; a third suit, filed by religious and labor groups, is pending in San Francisco.

Three lawsuits, three circuits, and now the real possibility of conflicting appellate rulings — the kind of split that tends to end up at the Supreme Court. On June 12 Sorokin agreed to stay his own order pending the First Circuit's decision on the government's motion. The Department of Homeland Security told the appeals court in Boston that the fee "isn't a tax" and should keep being enforced, warning that "every day that passes more aliens can petition and enter the country."

## What it means for the diaspora

For Indian H-1B aspirants, the immediate question is whether the fee is being collected right now. With Sorokin's stay in place, the legal landscape remains unsettled, and employers are getting conflicting signals depending on which court they look to. The numbers suggest the fee already did its damage as a deterrent: USCIS had received only 85 payments of the $100,000 charge as of February 15 — a vanishing fraction of normal H-1B volume, evidence that most employers simply stopped filing.

That chilling effect is the part that should worry the diaspora most. Even if the fee is ultimately killed, a year of uncertainty has taught employers to treat H-1B sponsorship of junior Indian talent as a liability. Some have shifted to cap-exempt routes through universities and nonprofits; others are quietly steering hiring to offices in Canada, India or the UK.

For the Indian professional already in the US on an H-1B, the fee never applied — it targets new petitions, not renewals or extensions, and does not block current visa holders from traveling. But for the student finishing a master's and praying for a lottery selection, the difference between a $5,000 filing and a $100,000 one is the difference between a career in America and a flight home.

## What's next

The First Circuit will rule on whether to lift Sorokin's stay; the D.C. and Ninth Circuits will weigh the parallel cases. The fee is currently scheduled to expire in September 2026 regardless of the litigation — but in an administration that has shown a taste for replacing struck-down rules with new ones, few in the diaspora are betting on a quiet sunset."""

# ---------------------------------------------------------------------------
# ARTICLE 3 — Domestic H-1B visa renewal pilot, India-focused
# ---------------------------------------------------------------------------
body3 = """For two decades, an H-1B worker in the United States who needed a fresh visa stamp faced the same dreary ritual: book a consular appointment back in India, fly home, and pray the wait time — currently running six to twelve months — did not strand them abroad. The State Department now says that era is ending, at least for a lucky first batch. A domestic visa renewal pilot will let certain H-1B holders restamp their visas without leaving the country, and officials are openly framing it as a gift to the Indian diaspora.

"Because Indians are the largest skilled group of workers in the United States, we hope that India will benefit quite a bit from this program," Julie Stufft, the Deputy Assistant Secretary of State for Visa Services, said in confirming the plan. The pilot will issue 20,000 visas over a three-month window beginning in December, and "the vast majority of those will be Indian nationals living in the US."

## How the pilot works

Stateside visa renewals were discontinued in 2004; this program revives them on a deliberately narrow scale. The Department published a Federal Register notice (Public Notice 12235) laying out tight eligibility rules, and the constraints matter as much as the headline number.

To qualify in the first tranche, an applicant must be renewing an H-1B visa specifically — H-4 dependents and holders of L-1, O-1, E-3 and H-1B1 visas are excluded from the pilot. The prior visa must have been issued either by a US consulate in India between February 1, 2021 and September 30, 2021, or by Mission Canada between January 1, 2020 and April 1, 2023. Applicants must be interview-waiver (drop-box) eligible, must have submitted ten fingerprints with a previous application, must hold an approved and unexpired H-1B petition, and must currently be maintaining H-1B status in the US.

In other words: this is a pilot in the truest sense — a controlled experiment with a small, clearly defined cohort, not a general reopening of stateside stamping. But Stufft has signaled it will "expand as it goes on," and the Department designed it precisely so it can scale without new regulations.

## Why it matters to the diaspora

Anyone who has lived the H-1B life knows the specific dread this program is meant to kill. A visa stamp expires while you are perfectly legal inside the US, your status intact — but the moment you travel internationally, you cannot return without a fresh stamp, and the only place to get one is a consulate abroad with a months-long queue. Workers have skipped weddings, funerals and the births of relatives' children rather than risk getting stuck in Hyderabad waiting for an appointment.

The wait times Stufft cited — "six, eight, and twelve months" — are not abstractions. They have meant Indian professionals declining overseas assignments, families postponing trips home for years, and employers losing key staff to administrative limbo. Domestic renewal removes the single most disruptive logistical hazard of holding an H-1B.

It also reflects a rare patch of warmth in the US-India immigration relationship. The plan was referenced in the joint statement during PM Modi's recent US visit and announced by Modi himself during his address to the diaspora at the Ronald Reagan Centre — a piece of immigration plumbing elevated to a symbol of bilateral goodwill, and welcomed accordingly by the Indian-American community.

## The catch

The eligibility window is the sting. By restricting the pilot to visas issued in India during a roughly eight-month stretch in 2021, the Department has excluded the vast majority of current H-1B holders, whose stamps were issued in other years or other countries. For most of the diaspora, December's program will be something to watch rather than to use.

The promise is in the trajectory. If the 20,000-visa pilot runs smoothly, the obvious next step is to widen the date ranges, add H-4 dependents — the spouses, overwhelmingly women, whose own renewal trips compound the family's disruption — and eventually fold in other visa classes. Stufft has all but promised that expansion.

## What's next

The State Department says a further Federal Register notice will spell out exactly who can apply in the first tranche and how. Indian H-1B holders should check whether their visa issuance date and consulate fall within the narrow eligibility window, confirm their drop-box eligibility, and watch for the application instructions before December. For the diaspora, it is a small door — but the first one to open inward in a long time."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "July Visa Bulletin Slams the Door: EB-2 India Now \u201cUnavailable\u201d",
        "subheadline": "EB-2 India has run out of green-card numbers for the rest of fiscal 2026, EB-1 India is retrogressing, and EB-5 is on the watchlist \u2014 the harshest month of the year for Indians in the queue.",
        "slug": make_slug("july-2026-visa-bulletin-eb2-india-unavailable"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals dominate the employment-based green-card backlog, so the July bulletin\u2019s EB-2 \u201cUnavailable\u201d status and EB-1 retrogression directly stall the permanent-residency plans of tens of thousands of H-1B professionals.",
        "tags": ["visa-bulletin", "green-card", "eb2-india", "eb1-india", "eb5", "immigration", "backlog"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Capitol Immigration Law Group \u2014 July 2026 Visa Bulletin Analysis", "url": "https://www.cilawgroup.com/news/july-2026-visa-bulletin/"},
            {"name": "VisaVerge \u2014 July 2026 Visa Bulletin: Complete Analysis & Forecast", "url": "https://www.visaverge.com/news/july-2026-visa-bulletin-complete-analysis-forecast/"},
            {"name": "WR Immigration \u2014 India EB-2/EB-3 Movement (Charlie Oppenheim)", "url": "https://wolfsdorf.com/india-eb-2-and-eb-3-visa-bulletin-movement/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An open passport displaying visa stamps and travel pages",
        "image_attribution": "Pexels",
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Court Kills Trump\u2019s $100,000 H-1B Fee \u2014 Then Hits Pause",
        "subheadline": "A Boston judge vacated the six-figure visa charge as an unlawful tax, but stayed his own order days later as the government appeals, leaving Indian tech workers in legal limbo.",
        "slug": make_slug("trump-100000-h1b-fee-struck-down-appeal"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians receive nearly three-quarters of all H-1B visas, so the fate of the $100,000 fee \u2014 struck down, stayed, and now on appeal \u2014 determines whether early-career Indian professionals can still realistically be sponsored to work in America.",
        "tags": ["h1b", "h1b-fee", "uscis", "immigration", "trump", "litigation", "tech-workers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Tax \u2014 DHS Says Trump H-1B Fee Isn\u2019t a Tax, Should Continue on Appeal", "url": "https://news.bloombergtax.com/daily-tax-report/dhs-says-trump-h-1b-fee-isnt-a-tax-should-continue-on-appeal"},
            {"name": "Associated Press / Montana Public Radio \u2014 Federal judge strikes down Trump\u2019s $100,000 H-1B fee", "url": "https://www.mtpr.org/2026-06-08/federal-judge-strikes-down-trumps-100000-fee-on-new-h-1b-visas"},
            {"name": "Reason \u2014 Trump\u2019s $100,000 H-1B visa fee is an unconstitutional tax, a federal judge rules", "url": "https://reason.com/2026/06/09/trumps-100000-h-1b-visa-fee-is-an-unconstitutional-tax/"}
        ]),
        "score_total": 86,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17630959/pexels-photo-17630959.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Interior of an American courthouse",
        "image_attribution": "Pexels",
        "body": body2,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "No More Flying Home: H-1B Visa Renewals Return to US Soil in December",
        "subheadline": "A State Department pilot will let 20,000 H-1B holders \u2014 mostly Indians \u2014 restamp their visas without leaving the country, reviving a process scrapped in 2004.",
        "slug": make_slug("h1b-domestic-visa-renewal-pilot-december-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B workers have long had to fly back to India and wait months for a visa stamp; the December domestic-renewal pilot is explicitly aimed at them, sparing the first 20,000 the disruption of an overseas consular trip.",
        "tags": ["h1b", "visa-renewal", "state-department", "immigration", "consular-processing", "india-us"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE \u2014 US to launch new plan for work visas in December, likely to benefit Indians most", "url": "https://www.theindianeye.com/us-to-launch-new-plan-for-work-visas-in-december/"},
            {"name": "Tafapolsky & Smith LLP \u2014 State Department Formally Announces Pilot Program for Renewal of H-1B Visas Within the US", "url": "https://www.tandslaw.com/state-department-formally-announces-pilot-program-renewal-h-1b-visas/"},
            {"name": "EY \u2014 US Department of State to launch domestic visa renewal pilot program", "url": "https://www.ey.com/en_gl/technical/tax-alerts/us-department-of-state-to-launch-domestic-visa-renewal-pilot-program"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1058959/pexels-photo-1058959.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport and travel bag in an airport setting",
        "image_attribution": "Pexels",
        "body": body3,
    },
]

# word-count sanity
for a in articles:
    wc = len(a["body"].split())
    print(f"  [{wc} words] {a['headline']}")
print("---")

ok = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"\u2705 {art['slug']}")
        ok += 1
    except Exception as e:
        print(f"\u274c {art['slug']}: {e}")
print(f"\nInserted {ok}/{len(articles)} articles.")
