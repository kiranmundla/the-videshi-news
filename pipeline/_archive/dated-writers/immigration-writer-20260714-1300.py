#!/usr/bin/env python3
"""Immigration writer — 2026-07-14 13:00 PT run"""
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
    # ─────────────────────────────────────────────────────────────
    # ARTICLE 1: Duration of Status Rule + Indian Student Pipeline
    # ─────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "The Rule That Could Put an Expiration Date on Every Indian Student Visa in America",
        "subheadline": "A DHS regulation ending open-ended student admissions has cleared internal review and is headed for the Federal Register. Indian enrollment is already falling. The economic stakes run into hundreds of billions.",
        "slug": make_slug("dhs-duration-of-status-rule-indian-students-enrollment-decline"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the largest F-1 visa population in the US and the primary feeder into the H-1B and green card pipelines — this rule threatens the entire pathway that brings Indian professionals to America.",
        "tags": ["f1-visa", "student-visa", "duration-of-status", "indian-students", "uscis", "stem", "opt"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Peterson Institute for International Economics (PIIE)", "url": "https://www.piie.com/"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/international-student-crackdown-blows-a-wisconsin-sized-hole-in-us-economy-analysis-shows-12013372"},
            {"name": "ICEF Monitor", "url": "https://monitor.icef.com/"},
            {"name": "Mondaq / Foley & Lardner", "url": "https://www.mondaq.com/"},
            {"name": "Collegedunia / India Parliament Data", "url": "https://collegedunia.com/"},
            {"name": "Inside Higher Ed", "url": "https://www.insidehighered.com/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972963/pexels-photo-7972963.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "College students studying together on a university campus bench",
        "image_attribution": "Pexels",
        "body": """For decades, international students entering the United States on F-1 visas have been admitted for "duration of status" — a bureaucratic phrase that meant, in practice, that they could stay as long as they remained enrolled in their programme and kept their paperwork current. No fixed end date stamped on the I-94. No clock ticking toward a hard deadline. The system trusted universities to police compliance, and for the most part, it worked.

That arrangement is about to end.

## The Rule

On May 5, 2026, the Department of Homeland Security submitted a final rule to the Office of Management and Budget that would replace the open-ended "duration of status" framework with fixed admission periods — capped at four years for most students or the length of their academic programme, whichever is shorter. Once OMB completes its review, the rule will be published in the Federal Register and take effect 60 days later.

The changes go well beyond a new stamp on a form. Under the proposed framework, any student who needs additional time — to finish a dissertation, change programmes, or complete post-graduation Optional Practical Training — would need to file a formal extension of stay application with USCIS, pay processing fees, and submit to biometric screening. The F-1 grace period after programme completion would shrink from 60 days to 30. Graduate students would be barred from switching programmes. Lateral transfers — moving to a different institution at the same academic level — would face new restrictions.

The authority over a student's status, in other words, would shift from the campus international students office to the federal immigration bureaucracy.

## The Pipeline Under Pressure

The rule lands on a pipeline that is already cracking.

Indian student enrollment in American universities fell 6.9 percent between February 2025 and February 2026, dropping from 378,787 to 352,644, according to data the Indian government's Ministry of External Affairs presented to the Rajya Sabha. The decline is not an anomaly. During the summer of 2025, Indian students received 63 percent fewer F-1 visas than in the same period the previous year — the largest drop among any major sending country — after a series of policy changes including mandatory social media vetting, the end of third-country visa stamping, and a brief pause on student visa interviews.

Across all nationalities, new international student enrollment in the United States dropped 17 percent in the 2025-26 academic year, according to an IIE survey of 828 institutions. Ninety-six percent of those schools cited visa delays and denials as the primary reason.

Universities have scrambled to respond. Conditional admissions, deferred start dates, and online bridge programmes have become standard tools for holding cohorts together while the visa system catches up. Deferrals increased by 39 percent compared to the prior year. Some institutions are offering spring or late-start options that would have been unthinkable a few years ago.

## The Economic Argument

A recent analysis from the Peterson Institute for International Economics tried to quantify the cost. PIIE researchers Michael Clemens, Amy Nice of Cornell, and Jeremy Neufeld of the Institute for Progress found that the cumulative effect of the administration's restrictions on international students could reduce annual GDP by $240 billion to $481 billion within a decade — a loss roughly the size of Wisconsin's economy.

The logic is straightforward. Thirty-five percent of doctoral-level STEM workers in the United States are foreign-born and U.S.-trained. If the student pipeline narrows, the workforce shrinks with it. And history offers no precedent for domestic workers filling the gap.

"In comparable past episodes, neither foreign-trained workers from abroad nor U.S.-born students stepped in to fill the gap," Clemens wrote. "We see no reason this time will be different."

## What It Means for Indian Families

For Indian students and their families, the stakes are not abstract. The F-1 visa is the entry point for a sequence that defines careers: student visa, Optional Practical Training, H-1B petition, and eventually — after years or decades in the employment-based backlog — a green card. Tightening the first link does not just reduce enrollment. It reduces the entire flow of Indian professionals into the American economy.

Danielle Goldman, co-founder of immigration advisory firm Build, warned that the Duration of Status rule would hit Indian students especially hard. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" she said — a reference to the Day 1 CPT programmes that have served as a lifeline for H-1B lottery losers.

The practical advice from immigration attorneys is blunt: if you are currently in the US on an F-1 visa, get your paperwork in order now. If you are planning to come, build contingency plans that do not depend on a single country's immigration system. Canada, Australia, Germany, and the UK are all actively recruiting from the same talent pool that the United States is squeezing.

The rule is not yet published. But the review is complete, the text is final, and the clock is running."""
    },

    # ─────────────────────────────────────────────────────────────
    # ARTICLE 2: The Cumulative Cost of Being an Indian Immigrant
    # ─────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "The Compounding Cost of Staying. What a Year of Policy Changes Has Done to Indian Immigrants' Wallets",
        "subheadline": "New visa fees, a mortgage ban, tripled court costs, a visa integrity surcharge, and now a crackdown on lending. A year's worth of policy changes has made being an Indian immigrant in America measurably more expensive.",
        "slug": make_slug("cumulative-cost-indian-immigrant-fees-mortgage-ban-policy"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders and green card applicants are bearing the brunt of a year-long accumulation of new fees, lending restrictions, and financial penalties that make staying in America materially costlier than it was 18 months ago.",
        "tags": ["immigration-fees", "h1b", "mortgage", "fha", "visa-integrity-fee", "uscis", "obbba", "green-card"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/"},
            {"name": "American Immigration Council", "url": "https://www.americanimmigrationcouncil.org/"},
            {"name": "Littler Mendelson", "url": "https://www.littler.com/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "BAL Immigration News", "url": "https://www.bal.com/"},
            {"name": "New York Post", "url": "https://nypost.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hand holding an open passport with various visa stamps",
        "image_attribution": "Pexels",
        "body": """Consider a composite portrait. An Indian software engineer in her mid-thirties, seven years into an H-1B stint in the Bay Area. Her I-140 is approved, her priority date is somewhere around 2019, and her EB-2 green card is — as of the July 2026 Visa Bulletin — unavailable for the remainder of the fiscal year. She has a mortgage application pending, a child born in California, and a visa stamping appointment that was recently rescheduled to early 2027.

She is not unusual. She is typical. And over the past twelve months, the cost of her immigration status has risen in ways that no single headline captured.

## The Fee Stack

The One Big Beautiful Bill Act, signed on July 4, 2025, introduced a new fee architecture for the immigration system. Some of the charges affect asylum seekers and TPS holders more directly, but the structural shift touches employment-based applicants too. The visa integrity and fraud prevention fee — $250 per year for most visa holders — went into effect in the current fiscal year. For a family of three on H-1B and H-4 status, that is $750 annually, on top of existing filing costs.

USCIS also adjusted its broader fee schedule for FY 2026 with inflation-linked increases mandated by the same law. Premium processing — the $2,805 charge that many employers pay for faster H-1B adjudication — now runs to the employer's timeline rather than the worker's. But when it comes to EAD renewals for H-4 dependent spouses, the cost and processing uncertainty fall on the family.

Then there is the immigration court system. The Executive Office for Immigration Review tripled its appeal filing fee to $975 earlier this year. For someone contesting a visa denial or deportation order, that is a steep gatekeeping charge before a single argument is heard.

## The Mortgage Wall

In May 2025, the Department of Housing and Urban Development stopped non-permanent residents — including H-1B visa holders — from being eligible for FHA-insured mortgages. The rule removed a pathway that Indian professionals in high-cost housing markets had used for years to buy homes with lower down payments.

Conventional mortgages remain available, but lenders have grown cautious. Earlier this month, three federal banking regulators issued guidance warning financial institutions to reassess lending risk tied to borrowers on temporary immigration status. The message was not subtle: lending to immigrants carries regulatory risk that banks may not wish to bear.

For Indian H-1B holders who had already started building lives — buying homes, enrolling children in schools, joining communities — the guidance creates a new layer of financial friction. A mortgage is not just a financial product. It is an anchor, and the government is quietly loosening it.

## The Stamping Trap

Every consular appointment is now a calculated risk. The end of domestic visa revalidation means that any trip to India for a family wedding, a parent's illness, or a child's introduction to grandparents requires a visa stamping appointment at a US consulate. Those appointments in India are booked into 2027. The mandatory social media vetting introduced in December 2025 added roughly 20 minutes per case file, but the staffing has not kept pace.

Indian professionals who travel home face a real possibility of being stranded — unable to return to their jobs, their mortgages, their children's schools — for months. Many have stopped traveling altogether. The emotional cost of that calculation does not appear on any government fee schedule, but it is as real as any dollar figure.

## The Invisible Tax

None of these individual policy changes is unprecedented. Visa fees rise. Mortgage rules shift. Court costs increase. What is unusual is the velocity and the direction. In the space of twelve months, the financial and practical cost of maintaining an Indian immigrant's life in America has increased across almost every dimension simultaneously.

The $250 visa integrity fee. The $975 court appeal fee. The FHA mortgage ban. The banking guidance discouraging immigrant lending. The consular stamping backlog. The H-4 EAD processing uncertainty. The $100,000 H-1B fee that a federal judge struck down in June but that the administration has signalled it will pursue through other channels. Each item, taken alone, is manageable. Stacked together, they amount to what immigration attorneys have started calling a "soft deterrence" — a system of accumulated friction designed to make staying in America incrementally less attractive without ever formally revoking a visa.

## The Calculation

The question Indian professionals are asking is no longer whether they can afford to immigrate. It is whether they can afford to stay.

Canada's Express Entry draws happen every two weeks. The UK's Graduate Route Visa offers two years of post-degree work authorisation without lottery anxiety. Germany's EU Blue Card programme is actively targeting Indian engineers. Australia's SkillSelect system rewards qualifications and experience with a clear pathway to permanent residency.

None of these systems are frictionless. But none of them have spent the past year adding friction, either.

For the Indian engineer in the Bay Area — the one with the approved I-140 and the unavailable EB-2 date — the arithmetic is getting harder to justify. Not because any single policy change is a deal-breaker. Because the sum of them is starting to look like one."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
