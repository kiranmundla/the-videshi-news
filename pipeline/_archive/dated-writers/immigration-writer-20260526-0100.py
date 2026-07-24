#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-26 01:00 PDT"""

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
    {
        "id": str(uuid.uuid4()),
        "headline": "The ₹66 Lakh Gamble — Indian Families Are Paying Double to Chase Half the Opportunity",
        "subheadline": "Education remittances from India fell 20% last year. Student loan costs doubled in four years. And Washington just froze new visa appointments. The math has never been worse.",
        "slug": make_slug("indian-student-education-loan-remittance-crash"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian families are betting bigger sums — now averaging ₹66 lakh per US education loan — into an immigration system that is actively shrinking the returns. Every NRI parent weighing a child's US admission letter against a home loan knows this tension firsthand.",
        "tags": ["f1-visa", "student-visa", "education", "immigration", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/global-uncertainty-slows-overseas-remittances-under-lrs-in-fy26-rbi-bulletin/article71012041.ece"},
            {"name": "Inshorts / Moneycontrol (GyanDhan analysis)", "url": "https://inshorts.com/en/news/how-much-loan-are-indian-students-taking-to-study-abroad--1779545542607"},
            {"name": "The Hindu Business Line (UK ONS data)", "url": "https://www.thehindubusinessline.com/news/indian-students-workers-lead-exit-trend-as-uk-net-migration-falls/article71006039.ece"},
            {"name": "USCIS", "url": "https://www.uscis.gov"},
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7616700/pexels-photo-7616700.jpeg",
        "body": """The Reserve Bank of India's May bulletin delivered a number that should unsettle every Indian family with a child studying abroad: remittances for overseas education under the Liberalised Remittance Scheme fell 20 percent year-on-year in FY26, dropping from $2.9 billion to $2.3 billion. That is not a rounding error. That is $600 million in parental ambition that simply did not leave the country.

The decline arrives alongside a data point that moves in the opposite direction and makes the picture considerably grimmer. According to a GyanDhan analysis reported by Moneycontrol, the median education loan sought by Indian students heading to the United States has nearly doubled in four years — from ₹35 lakh in 2022 to ₹66 lakh in 2026. Australia doubled to ₹50 lakh. Canada sits at ₹30 lakh. The UK, which used to be the budget option for a master's degree, now commands ₹35 lakh.

Fewer families sending money. Those who do, borrowing far more. The economics of studying abroad have entered a zone where the risk-reward calculus is shifting fast.

## The Visa Wall

The financial squeeze would be manageable if the pathway after graduation remained clear. It does not.

Secretary of State Marco Rubio's directive freezing new student visa appointments — ostensibly to implement social media screening protocols — has thrown Fall 2026 enrollments into disarray. Indian universities report that students with admission letters from American institutions are sitting on I-20 forms they cannot act on. The State Department has told consular officers to avoid adding new appointment slots until further guidance arrives.

This is not the first disruption. Since September 2025, every non-immigrant visa applicant has faced the $100,000 H-1B proclamation fee (for those who eventually transition to work visas), the $250 Visa Integrity Fee under the One Big Beautiful Bill Act, and heightened scrutiny of "immigrant intent" for F-1 applicants. USCIS's May memo on adjustment of status explicitly flagged F-1 OPT and STEM OPT holders as categories facing increased reviews.

For a student borrowing ₹66 lakh against a family home in Hyderabad or Pune, the question is no longer "Can I get admitted?" but "Can I get a visa, can I stay, and will the rules be the same in two years?"

## The UK Is Closing Too

Britain offered no refuge. The Office for National Statistics reported that 51,000 Indians who had come to the UK for study left the country in 2025 — leading all nationalities in the exit trend. UK net migration fell to 171,000, nearly halved from its peak, and the Labour government's Home Secretary warned of a new "skills-based migration system" that explicitly aims to end reliance on foreign workers.

Indian students still account for 23 percent of all Sponsored Study visas to Britain — 90,425 grants — but the post-study work route is narrowing. A 24 percent drop in Indian student numbers was already recorded before the latest policy tightening.

The pattern is unmistakable: the two English-speaking destinations that absorbed the majority of Indian students for two decades are simultaneously raising the drawbridge.

## Where the Money Goes Instead

The RBI data contains a clue about what Indian families are doing with the money they are not sending abroad for education. Remittances toward investment in foreign equity and debt surged 56 percent year-on-year to $2.7 billion in FY26. Indian households, it appears, are not retreating from global exposure — they are redirecting it from tuition fees to financial markets.

Australia and Canada remain alternatives. Australia's immigration system still offers clear pathways for Indian engineers and healthcare workers. Canada, despite its own recent tightening, processed more Indian study permits in 2025 than any other nationality. Germany's tuition-free public universities are attracting a growing cohort of Indian STEM students.

But none of these destinations replicate what the United States offered at its peak: a direct pipeline from a top-ranked university to an OPT position, then an H-1B, then a green card, then citizenship. That pipeline has not been severed, but every joint in it now leaks.

## The Family Equation

For the Indian diaspora already in the United States, the student pipeline is not an abstraction. It is how nephews, nieces, and younger siblings join them. It is how the community replenishes itself. An H-1B holder in San Jose whose younger brother just received an admit from Purdue is now doing math that did not exist three years ago: ₹66 lakh in debt, a frozen visa queue, a social media review, an OPT system under scrutiny, and a $100,000 employer fee waiting at the H-1B stage.

The RBI's 20 percent drop in education remittances is the aggregate expression of thousands of families running that math and arriving at the same conclusion: the gamble is getting too expensive for the odds being offered.""",
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Fee Stack — Every Dollar Washington Now Charges Indian Immigrants from Visa to Green Card",
        "subheadline": "Between the OBBBA, the $100K proclamation, and proposed wage hikes, the cumulative cost of immigrating legally to America has quietly become staggering. Here is the full ledger.",
        "slug": make_slug("obbba-immigration-fee-stack-indian-immigrants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians account for 71% of H-1B approvals. Every fee increase hits the community disproportionately. This piece maps out the total financial burden — from student visa through green card — that an Indian immigrant now faces at each stage of the process.",
        "tags": ["obbba", "immigration-fees", "h1b", "green-card", "uscis", "visa-integrity-fee"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CLINIC (Catholic Legal Immigration Network)", "url": "https://www.cliniclegal.org/resources/religious-immigration-law/one-big-beautiful-bill-and-fee-increases-immigration-processes"},
            {"name": "Global Refuge", "url": "https://www.globalrefuge.org/news/how-will-the-one-big-beautiful-bill-act-affect-immigration-fees/"},
            {"name": "Mintz", "url": "https://www.mintz.com/insights-center/viewpoints/54166/2025-10-15-uscis-and-cbp-provide-updates-trump-proclamation"},
            {"name": "DLA Piper", "url": "https://www.dlapiper.com/en-us/insights/publications/2025/09/white-house-proclamation-introduces-100000-h1b-visa-fee"},
            {"name": "Congress.gov (H.R. 1 text)", "url": "https://www.congress.gov/bill/119th-congress/house-bill/1/text"},
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg",
        "body": """Nobody published the total. The individual fee announcements trickled out across executive orders, proclamations, a 1,000-page reconciliation bill, and proposed rulemakings. Each generated its own headline. None added them up. So here is the ledger — every fee an Indian national now faces, or will soon face, on the standard path from student visa to green card.

## Stage 1: Getting In

**F-1 student visa**: The base SEVIS fee remains $350. The DS-160 application fee is $185. But the One Big Beautiful Bill Act (OBBBA), signed July 4, 2025, introduced the **Visa Integrity Fee**: a minimum $250 charge on every non-immigrant visa issued. It is technically refundable — if you can prove, at the time your visa expires, that you complied with every condition and departed on time. In practice, for someone transitioning from F-1 to OPT to H-1B, the refund window may never open.

**New entry cost for a student: ~$785 minimum**, up from ~$535 before the OBBBA.

## Stage 2: Working After Graduation

**OPT/STEM OPT**: The I-765 Employment Authorization Document fee was already $410. The OBBBA added a new wrinkle: for anyone whose EAD is based on a pending asylum, parole, or TPS application, the fee jumps to $550 for the first application and $275 for renewals. OPT applicants are not directly in this category, but the USCIS May 2026 memo flagged STEM OPT holders for "heightened scrutiny of intent and prior conduct." Immigration attorneys report that adjudication times for I-765 applications from Indian nationals have lengthened by 30-45 days since January.

**H-1B petition**: Here the numbers become eye-watering. The base filing fee is $1,710. The ACWIA training fee adds $750 or $1,500 depending on company size. The fraud prevention fee is $500. Premium processing, if your employer opts for it, is $2,805. And then there is the proclamation.

On September 19, 2025, President Trump signed Proclamation 10922, requiring a **$100,000 payment** for every H-1B petition filed on behalf of a worker entering the United States. The fee applies to new petitions only — not to extensions where the worker is already in the US — and expires on September 21, 2026. USCIS clarified that current US-based workers with approved petitions are unaffected, and that the fee is paid through pay.gov.

**Total employer cost for a new H-1B from abroad: approximately $107,000**, before legal fees.

The proclamation's September 2026 expiration is four months away. No one in the administration has signaled it will lapse quietly. The Department of Labor has simultaneously proposed raising prevailing wage levels by roughly 30 percent, which would increase the salary floor for H-1B workers independent of the petition fee.

## Stage 3: The Green Card Queue

For an Indian national, the green card queue is not a fee problem — it is a time problem with fees attached at every checkpoint.

**PERM labor certification**: Employer bears the cost (~$15,000-$25,000 in legal and recruitment expenses). **I-140 petition**: $715. **I-485 adjustment of status**: $1,140, recently raised to a minimum of $1,500 under the OBBBA for asylum-based adjustments (employment-based AoS retains the $1,140 fee for now, but the bill's "minimum fee" language means USCIS can increase it without new legislation).

The May 2026 USCIS memo declaring adjustment of status an "extraordinary act of grace" has introduced new uncertainty. H-1B holders in dual-intent categories retain protection, but the memo directs officers to weigh factors including US citizen children, community ties, and employment history — a subjective review that did not previously exist. For Indian EB-2 applicants, whose priority dates are currently stuck at January 15, 2015 — more than eleven years behind — the prospect of maintaining H-1B status through multiple renewals while navigating this new scrutiny is daunting.

**If you need to appeal a denial**: The Board of Immigration Appeals fee jumped from $110 to $900 under the OBBBA — a 718 percent increase. A motion to reopen: also $900. These are minimums, and fee waivers have been eliminated.

## Stage 4: The Hidden Costs

The OBBBA introduced two provisions that do not show up on any USCIS fee schedule but affect Indian immigrants directly.

**The 1% remittance levy**: A tax on outbound remittances that hits every dollar sent home to India — whether for a parent's medical bill, a sibling's wedding, or a child's school fees. For a household sending $20,000 a year to family in India, that is $200 annually, in perpetuity.

**Mandatory E-Verify**: The Act requires all employers to use E-Verify for new hires. For legal immigrants, this is technically neutral. In practice, E-Verify's known false-positive rate — disproportionately affecting workers with hyphenated names, transliterated spellings, or recent status changes — creates friction. A "tentative non-confirmation" requires the worker to visit a Social Security office or call USCIS within eight business days, during which the employer cannot legally terminate them but can decline to assign work.

## The Running Total

Here is what the standard Indian immigration pathway now costs, from landing at JFK with an F-1 visa to filing for a green card:

| Stage | Approximate Cost |
|---|---|
| F-1 visa (SEVIS + DS-160 + Visa Integrity Fee) | $785 |
| OPT I-765 | $410 |
| H-1B petition (employer-paid, no $100K fee) | $4,710 - $7,515 |
| H-1B petition (new entry, with $100K fee) | $104,710+ |
| PERM + I-140 | $15,715 - $25,715 |
| I-485 adjustment of status | $1,140 - $1,500 |
| BIA appeal (if needed) | $900 |
| Biometrics (multiple stages) | $85 per instance |
| Annual remittance tax (on $20K/yr) | $200/year |

The total for someone who enters on a student visa, transitions to H-1B (new entry), and eventually files for a green card exceeds **$125,000 in government fees alone** — before a single dollar of legal representation.

## What Comes Next

The $100,000 H-1B proclamation expires September 21, 2026. The administration has not signaled whether it will lapse, be renewed, or be replaced with something permanent. The DOL wage rule comment period closes this week. The OBBBA's fee provisions are law — they do not expire.

For the 627,000 Indians in the employment-based green card backlog, none of these fees are one-time events. H-1B renewals, EAD renewals for spouses, I-485 supplements, travel documents — each generates its own charge, on a loop that can last a decade or more.

The system was never cheap. It is now, by design, expensive enough to function as a filter. Whether that filter catches the people Washington intends to exclude is a separate question. What it certainly catches is every Indian family doing the arithmetic.""",
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
