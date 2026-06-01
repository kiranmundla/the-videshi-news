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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty-Nine Days to File — The H-1B Deadline That Could Void Your Lottery Win",
        "subheadline": "FY2027 is the first H-1B cycle under the new wage-weighted lottery. If your employer was selected and hasn't filed the petition yet, the clock runs out on June 30.",
        "slug": make_slug("h1b-fy2027-filing-deadline-june-30-wage-weighted"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals account for roughly 72% of all H-1B approvals. The new wage-weighted system disproportionately affects entry-level Indian tech workers, with Level I selection odds halved to 15%. Employers who delay filing risk losing their selected registrations entirely — and for thousands of Indian workers, that means restarting the process next year or leaving the country.",
        "tags": ["h1b", "uscis", "fy2027", "wage-weighted-lottery", "filing-deadline"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations"},
            {"name": "Visa Lawyer Blog (Sapochnick)", "url": "https://www.visalawyerblog.com/uscis-completes-h1b-cap-selection-fy2027/"},
            {"name": "Mondaq (Wage-Weighted Selection)", "url": "https://www.mondaq.com/unitedstates/work-visas/1583474/wage-based-weighted-h-1b-selection-process-for-the-2026-lottery-implemented"},
            {"name": "Buchanan Ingersoll & Rooney PC", "url": "https://www.bipc.com/fy-2027-h-1b-cap-registration-opens-march-4-2026"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&w=800",
        "body": """The FY2027 H-1B cap season has entered its final stretch, and employers who secured a lottery selection back in March are now staring at a hard wall: **June 30, 2026**. Miss it, and the selected registration is voided — no extensions, no appeals, no second chances. The visa number gets recycled into a potential secondary lottery, and your sponsored worker starts the whole process over again in March 2027.

This matters more than usual because FY2027 is the inaugural cycle under the **wage-weighted selection system**, a fundamental redesign of how H-1B slots are allocated. The old random lottery is gone. In its place, USCIS now weights entries by the Department of Labor's prevailing wage level for the offered position. A Level IV role — the highest tier — gets four entries in the pool. Level I gets one.

## What the Numbers Actually Look Like

The selection probabilities under the new system are starkly different from the roughly 30% flat rate of prior years:

- **Level IV**: ~61% selection probability
- **Level III**: ~46%
- **Level II**: ~31%
- **Level I**: ~15%

For Indian IT services companies that historically sponsored large numbers of entry-level positions at Level I wages, the math has shifted dramatically. A role paying the 17th-percentile wage for its occupation and geography now has roughly half the odds of the old lottery. Senior roles paying at the 67th percentile or above have never had it this good.

## The Filing Gauntlet

Selected employers have a narrow window — April 1 through June 30 — to file the actual I-129 petition. The required edition of the form is the 02/27/26 revision, and USCIS will reject any petition submitted on an older version. Petitions must be filed either online through a USCIS organizational account or by paper to the designated Service Center listed on the registration selection notice.

The petition package must include:

- A certified Labor Condition Application (LCA) from the Department of Labor
- Form I-129, Petition for Nonimmigrant Worker (02/27/26 edition)
- A copy of the applicable registration selection notice
- Supporting documentation proving the specialty occupation and wage compliance

Here is where the wage-weighted system creates a new tripwire: **consistency between the registration and the petition is mandatory**. When the employer registered in March, they declared a specific OEWS wage level. The filed petition must demonstrate a salary consistent with that level. USCIS is actively cross-referencing the registration wage level, the LCA prevailing wage, and the actual offered compensation. Any mismatch — even an innocent one caused by a job reclassification between March and June — can trigger a denial.

## The $100,000 Shadow

Layered on top of the wage-weighted system is the $100,000 H-1B fee from Executive Order 14351, signed in September 2025. Employers must determine whether each beneficiary was in H-1B status, had a pending I-129, or was present in the U.S. on September 21, 2025. If the answer is no to all three, the six-figure payment — or an approved National Interest Exception — is required before USCIS will approve the petition.

Multiple lawsuits challenging the fee remain active, including *Chamber of Commerce v. DHS* in the District of Columbia. But the fee is in effect and enforced. Employers cannot rely on a future court ruling to retroactively save a petition filed without payment.

## What This Means for Indian H-1B Workers

Indian nationals represent the largest cohort of H-1B beneficiaries by a wide margin, consistently accounting for over 70% of approvals. The wage-weighted system has introduced a structural tilt away from the entry-level and consulting-tier positions that many Indian IT firms have historically sponsored.

But even for workers sponsored at Level II or Level III — the sweet spot for mid-career Indian engineers at product companies — the June 30 deadline is the immediate concern. Premium processing, available at $2,805 (or $2,965 as of March 2026 for certain categories), can speed adjudication to 15 business days. But the filing itself must happen before the deadline.

Workers whose employers were selected should confirm three things immediately: that the LCA has been certified, that the I-129 has been prepared on the correct form edition, and that the petition has been (or will be) submitted well before June 30. Waiting until the last week risks postal delays, lockbox processing backlogs, and the kind of administrative rejection that turns a won lottery ticket into a very expensive piece of paper.

The earliest start date for FY2027 H-1B employment is October 1, 2026. Between now and then, the only date that matters is June 30."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Twelve Million Cases and Counting — Congress Finally Asks Where the Money Went",
        "subheadline": "Eighteen Democratic lawmakers are demanding answers as USCIS backlogs swell by 2 million cases since January 2025, even as the agency collects record fee revenue.",
        "slug": make_slug("uscis-12-million-backlog-congress-moulton-letter"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals are the single largest group of employment-based immigration applicants. With I-485 processing running 11 to 31.5 months and no premium processing available, every week of added delay compounds the already decade-long green card wait. The congressional letter's core question — whether USCIS resources have been diverted from benefits processing to enforcement — directly affects the speed at which Indian workers get their EADs, travel documents, and green cards.",
        "tags": ["uscis", "backlog", "processing-times", "congress", "green-card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/uscis/uscis-faces-congressional-pressure-to-address-immigration-case-backlog/"},
            {"name": "Rep. Seth Moulton (press release)", "url": "https://moulton.house.gov/"},
            {"name": "USCIS Processing Times", "url": "https://egov.uscis.gov/processing-times/"},
            {"name": "Beyond Border Global (I-485 backlog analysis)", "url": "https://beyondborderglobal.com/blog/i-485-processing-delays-backlog-status/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8382083/pexels-photo-8382083.jpeg?auto=compress&cs=tinysrgb&w=800",
        "body": """The number is almost too large to process, which is fitting: the U.S. Citizenship and Immigration Services now has **nearly 12 million pending cases** in its pipeline, an increase of roughly 2 million since January 2025. That is not a metaphor. It is a bureaucratic reality that touches every green card applicant, every work permit renewal, every naturalization ceremony that hasn't happened yet.

Representative Seth Moulton of Massachusetts, joined by 17 other Democratic lawmakers, has sent a letter to DHS Secretary Markwayne Mullin and USCIS Director Joseph B. Edlow demanding a detailed accounting of how the agency reached this point — and what, exactly, it is doing with the record fee revenue it continues to collect.

## The Backlog, the Frontlog, and the Fog in Between

USCIS uses two terms that matter here. The **backlog** refers to cases that have exceeded their normal processing windows — applications that should have been decided months ago and weren't. The **frontlog** is the mass of newly filed cases waiting to enter active adjudication. Together, they form a queue so long that the distinction between "pending" and "stuck" has become academic for most applicants.

The lawmakers' letter zeroes in on a pointed question: if USCIS has been collecting more fee revenue and receiving additional congressional funding, why are processing times getting worse? The agency's own estimates, published weekly, tell the story:

| Form | Purpose | Current Processing Time | Fee (May 2026) |
|------|---------|------------------------|----------------|
| I-485 | Adjustment of Status | 8–14 months (NBC); up to 31.5 months (some centers) | $1,440 |
| I-765 | Employment Authorization | 3–7 months | $470–$520 |
| I-131 | Travel Document (Advance Parole) | 6–14 months | Varies |
| N-400 | Naturalization | 5–8 months | $710–$760 |

Those are median figures. The tails are longer. And critically, **premium processing does not exist for the I-485** — the form that determines whether you get a green card. There is no amount of money an applicant can pay to speed that decision.

## Follow the Money — and the Staff

The lawmakers' letter asks whether USCIS resources — staff, funds, or contracts — have been redirected since January 2025 to enforcement-related work or other DHS priorities outside the agency's core benefits-processing mission. This is the most consequential question in the letter.

USCIS is unusual among federal agencies in that it is almost entirely fee-funded. Applicants pay the bills. When an H-1B worker submits an I-485 and pays $1,440, that money is supposed to fund the adjudicator who reviews the case, the system that tracks it, and the infrastructure that delivers the decision. If those dollars are instead flowing to immigration enforcement operations — to FDNS site visits, to enhanced vetting protocols, to anything that is not processing the applications that generated the fees — then applicants are effectively funding their own delays.

The letter also asks USCIS to identify specific policy or procedural changes since January 2025 that have slowed adjudication. Revised intake procedures, added screening steps, new evidence rules, interview scheduling restrictions, staffing shifts between form types — any of these could explain why the inventory keeps growing even as the money keeps flowing.

## What This Means for the Indian Diaspora

For Indian-born applicants in the employment-based green card queue, the USCIS backlog is not an abstract policy concern. It is the difference between a 12-month I-485 adjudication and a 31-month one. It is the gap between getting an Employment Authorization Document in three months (allowing a job change or a spouse's ability to work) and waiting seven months for the same piece of paper.

Consider the compound effect. An Indian EB-2 applicant with a priority date of, say, July 2014 has already waited over a decade for their date to become current. When it finally does — and for June 2026, USCIS has directed all employment-based filers to use the **Final Action Dates chart**, making the EB-2 India cutoff July 15, 2014 — they file the I-485 and enter a new queue. The green card backlog doesn't end when your priority date becomes current. It just changes shape.

The processing time variation across service centers adds another layer of uncertainty. Nebraska Service Center typically handles employment-based I-485s in 11 to 16 months. Texas Service Center runs longer. The National Benefits Center, which handles many interview-required cases, can stretch to 31 months depending on field office scheduling. Applicants do not get to choose their service center.

## The Larger Pattern

The USCIS inventory has been growing for years, but the acceleration since early 2025 is notable. The agency processed 1.4 million green cards in fiscal year 2024 — a high-water mark. Yet pending cases continued to climb, suggesting that new filings are outpacing completions by a widening margin.

For the 18 lawmakers who signed the letter, the concern is structural: an agency that collects billions in fees from legal immigrants should not be delivering multi-year wait times for routine applications. For the Indian professionals who constitute the largest single national-origin group in the employment-based pipeline, the concern is more personal. Every additional month of I-485 processing is a month of restricted job mobility, a month of uncertainty about travel, a month of H-4 dependent spouses potentially unable to work.

The letter asks USCIS to respond by a specified deadline. Whether the agency provides a substantive answer — or a boilerplate acknowledgment — will say a great deal about whether the legal immigration system's plumbing is merely slow or fundamentally redirected."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
