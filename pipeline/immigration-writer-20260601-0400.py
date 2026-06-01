#!/usr/bin/env python3
"""Immigration writer — 2026-06-01 04:00 UTC run."""

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

# ─── ARTICLE 1 ────────────────────────────────────────────────────────────────

article1_body = """The United Kingdom just told millions of immigrants that five years of good behaviour is no longer enough to call Britain home. Under the proposed "earned settlement" framework — the most radical overhaul of UK permanent residency rules in a generation — the qualifying period for Indefinite Leave to Remain (ILR) will double from five years to ten. For lower-skilled workers, it could stretch to fifteen. For anyone who has ever claimed public benefits, add another five on top. Arrive irregularly, and you are looking at twenty.

The Immigration Law Practitioners' Association, in a briefing released earlier this year, called the proposals "largely without precedent" among comparable countries. They are not exaggerating. In the European Union, long-term residency comes after five years. In Canada, permanent residence can arrive from the outset for skilled workers. In Australia, roughly half of those who obtain permanent residence do so immediately. Even Switzerland — not exactly famous for its open-door enthusiasm — caps its standard requirement at ten years. The UK is proposing to out-Swiss the Swiss.

## What the New Model Actually Demands

The old system was bracingly simple: stay five years on a qualifying visa, pass a Life in the UK test, demonstrate B1 English, and you were in. The earned settlement model replaces this with a points-based assessment of "contribution" — a word that does a lot of heavy lifting in the 42-page consultation document.

Under the proposed framework, the ten-year baseline can be reduced for those earning above £50,270 annually for three consecutive years. High earners who sustain that threshold could still reach settlement in five years. But the calculus flips for everyone else. Those on salaries below the median face the full decade. Workers in lower-skilled roles — including care workers, the very people Britain spent the pandemic calling heroes — could wait fifteen years.

The English language requirement is tightening from B1 to B2, effective from March 2027. Visa fees rose 6 to 25 per cent in April 2026. And dependants will no longer automatically qualify for ILR alongside the main applicant; they must meet their own qualifying period independently.

A petition opposing the change on the UK Parliament website has gathered 232,000 signatures. The government's response, issued in December 2025, was conspicuously non-committal: "No decision has been taken on this point."

## Why Indian Families in Britain Should Be Paying Attention

The numbers tell a story of rapid retreat. Indian student enrolments in UK universities have dropped 76 per cent, according to data tracked by Indian Diaspora Pulse. Net migration from India fell 82 per cent. Post-study work visas — the two-year Graduate Route that made Britain attractive to Indian students — will be cut to 18 months from January 2027. Universities now face requirements to maintain 95 per cent enrolment and under 5 per cent refusal rates or risk losing their sponsor licence.

For the estimated 150,000 Indians on Skilled Worker visas in the UK, the earned settlement proposal lands like a contract renegotiation after you have already signed. Many moved to Britain under the explicit promise of a five-year path to permanence. Changing the terms retroactively — and the consultation document does propose applying the new rules to people already in the UK — raises questions of basic fairness that the government has not yet answered.

## The Political Climate Is Getting Worse

Into this policy upheaval has walked Rupert Lowe, the former Reform UK MP who launched his own far-right offshoot, Restore Britain, after being expelled from Nigel Farage's party. Last week, Lowe posted on X: "I don't believe we should import millions of Pakistanis and Indians to do jobs that unemployed Brits should be doing. If that makes me a racist, then so be it."

The post went viral, boosted by reposts from Elon Musk. Restore Britain won ten local council seats in Norfolk earlier this month. Lowe's candidate is polling at 7 per cent in the upcoming Makerfield by-election — enough to split the right-wing vote and reshape outcomes.

The data undercuts Lowe's premise entirely. According to the Migration Observatory at Oxford, Indian and Nigerian nationals saw the sharpest employment increases in the UK between 2021 and 2025 — but they are concentrated in sectors with chronic staffing shortages. A quarter of jobs held by non-EU nationals are in health and care, precisely the sector the Home Office added to visa eligibility because it could not fill vacancies domestically. In Lowe's own constituency of Great Yarmouth, there are exactly 786 residents of Indian origin — less than 1 per cent of the population.

## The NRI Calculus

For Indian professionals weighing their options, Britain was supposed to be the sensible alternative. Canada tightened its immigration streams. Australia raised its salary thresholds. The United States imposed a $100,000 H-1B fee. Britain, with its post-Brexit demand for skilled workers and a relatively straightforward five-year ILR path, looked like the pragmatic choice.

That calculation is now obsolete. A ten-year wait for settlement, rising fees, shrinking post-study routes, and a political climate in which "Indians taking British jobs" is a campaign slogan — these are not the conditions under which families build permanent lives.

The consultation closed in February 2026. The government is "analysing responses." Implementation is expected from April 2026. For those already on the clock, the question is not whether to worry. It is whether to start looking at the fine print on their return tickets."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Ten Years to Belong — Britain Just Doubled the Wait for Permanent Residency",
    "subheadline": "The UK's 'earned settlement' overhaul would make it the hardest major economy in which to settle permanently. Indian workers and students are already heading for the exits.",
    "slug": make_slug("uk-earned-settlement-ilr-ten-years-indian-diaspora"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Roughly 150,000 Indians hold UK Skilled Worker visas under a five-year ILR promise now being retroactively rewritten. Indian student enrolments have collapsed 76%. For NRIs who picked Britain as the 'safe alternative' to Trump's America, the doors are closing on both sides of the Atlantic.",
    "tags": ["uk-immigration", "ilr", "earned-settlement", "indian-students", "skilled-worker-visa", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Davidson Morris - UK Law Firm", "url": "https://www.davidsonmorris.com/earned-settlement-uk/"},
        {"name": "UK Parliament E-Petitions", "url": "https://commonslibrary.parliament.uk/e-petitions-relating-to-indefinite-leave-to-remain/"},
        {"name": "ILPA Briefing", "url": "https://www.ein.org.uk/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/law-order/3375871-uk-far-right-leader-sparks-outrage-anti-immigrant-remarks"},
        {"name": "Migration Observatory, University of Oxford", "url": "https://migrationobservatory.ox.ac.uk/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/5209879/pexels-photo-5209879.jpeg",
    "body": article1_body
}

# ─── ARTICLE 2 ────────────────────────────────────────────────────────────────

article2_body = """For a decade, the H-1B lottery was simple arithmetic. Every registration got one ticket. Your odds were the same whether you were a Level I junior analyst at a staffing firm or a Level IV principal engineer at Google. The system was blind to salary, seniority, and, in the eyes of its critics, blind to merit.

That era ended on 27 February 2026, when the Department of Homeland Security's weighted selection rule took effect. The FY2027 lottery — the first under the new system — is now complete, and the numbers confirm what immigration attorneys feared: the game has fundamentally changed, and the players most affected are Indian.

## How the New Lottery Works

The mechanics are straightforward but the consequences are not. Under the weighted selection rule, finalised on 23 December 2025, each H-1B registration is assigned to one of four wage levels based on the Occupational Employment and Wage Statistics (OEWS) data for the relevant job and metropolitan area. The weight assigned determines how many times that registration enters the selection pool:

- **Level IV** (top quartile wages): entered four times
- **Level III** (above median): entered three times
- **Level II** (median): entered two times
- **Level I** (entry-level): entered one time

A Level IV registration is four times more likely to be selected than a Level I. USCIS's own projections, published alongside the final rule, estimated a **48.33 per cent reduction** in Level I selections and a **106.69 per cent increase** in Level IV selections compared to the old random system.

The rule also requires registrants to select the relevant Standard Occupational Classification (SOC) code for the offered position, anchoring the wage level to a specific job category and geography. A software developer in San Francisco earning $95,000 might be Level I; the same salary in Des Moines could be Level II. Geography now determines lottery odds.

## Who Loses

The answer, in aggregate, is Indian nationals — particularly those sponsored by IT services companies and staffing firms.

The six largest Indian IT employers — TCS, Infosys, HCL Technologies, Wipro, Tech Mahindra, and LTIMindtree — have already reduced their H-1B filings by 46 per cent over five years, according to USCIS data. But the workers they do sponsor tend to cluster at Level I and Level II wages. Under the old lottery, that did not matter. Under the new one, it halves or quarters their chances.

The American Hospital Association flagged a parallel concern in a letter to USCIS Director Joseph Edlow: 67 per cent of H-1B workers in healthcare occupations — pharmacists, technicians, physicians, therapists — are paid Level I and Level II wages, while only 2.3 per cent earn Level IV. The weighted system effectively punishes sectors where the prevailing wage structure runs lower, regardless of the skill required.

Combined with the 38 per cent collapse in FY2027 registrations — down from 553,000 to roughly 343,000 — the pipeline is being squeezed from both ends. Fewer people are entering the lottery, and those who do at lower wage levels are far less likely to be selected.

## The Math for a Typical Indian Applicant

Consider Priya, a hypothetical software engineer in her late twenties on OPT in Dallas. Her employer offers $82,000 — a competitive salary for a junior role in North Texas, but Level I on the OEWS scale for her SOC code. Under the old lottery, she had roughly a 35 per cent chance of selection. Under the weighted system, her single-entry odds drop to something closer to 18 per cent.

Her colleague Rahul, a principal architect at the same company earning $195,000 — Level IV — enters the pool four times. His effective selection rate is well above 70 per cent.

The system does not discriminate by nationality. But when 72 per cent of H-1B recipients are Indian nationals, and when the Indian applicant pool skews younger and earlier-career than any other nationality, the demographic impact is lopsided by design.

## What Employers Are Doing

The response is bifurcating. Large tech companies — Amazon, Google, Microsoft, Meta — can absorb the system because their H-1B sponsorships tend to be at Level III and IV wages. The weighted lottery is, for them, a competitive advantage: it increases the odds for the very employees they want.

IT services firms and mid-sized companies face a different calculus. Many are accelerating their shift to offshore delivery, nearshore centres in Canada and Latin America, and L-1 intracompany transfers that bypass the lottery entirely. Others are exploring O-1A extraordinary ability visas for senior staff, though that path requires substantially more documentation and a narrower definition of eligibility.

A growing number of employers are simply raising salaries for H-1B positions to push them into Level III territory. The DOL's proposed prevailing wage increase — which would set the floor at the 34th percentile rather than the current 17th — would, if finalised, push even more positions into higher wage levels by default.

## The Structural Shift

The weighted lottery, the $100,000 fee, the prevailing wage hike, the 38 per cent registration drop — these are not isolated policy actions. Together, they constitute a structural reorientation of the H-1B programme away from volume and toward a narrower, higher-paid cohort.

For Indian tech professionals early in their careers, the message is stark: the path that brought hundreds of thousands of engineers from Hyderabad and Pune and Bengaluru to Silicon Valley and Seattle over the last two decades is not the path that will be available to the next generation. The lottery is no longer random. And the odds are no longer equal."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The H-1B Lottery Isn't Random Anymore — Here's What the New Wage-Weighted System Actually Does",
    "subheadline": "Level IV earners now get four times the lottery chances of entry-level applicants. USCIS projects a 48 per cent drop in Level I selections. For early-career Indian workers, the arithmetic just got brutal.",
    "slug": make_slug("h1b-weighted-lottery-wage-level-indian-workers-fy2027"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals make up 72% of H-1B recipients, and the Indian applicant pool skews younger and earlier-career. The weighted system disproportionately reduces their selection odds while benefiting higher-paid applicants at large tech firms. IT services companies — the traditional pipeline for Indian engineers — face a structural disadvantage.",
    "tags": ["h1b", "weighted-lottery", "uscis", "wage-levels", "indian-tech", "immigration-reform"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "DHS Final Rule - Weighted H-1B Selection", "url": "https://www.federalregister.gov/"},
        {"name": "Dickinson Wright Immigration Blog", "url": "https://immigration.dickinson-wright.com/"},
        {"name": "American Hospital Association Letter to USCIS", "url": "https://www.aha.org/"},
        {"name": "USCIS H-1B Cap Data", "url": "https://www.uscis.gov/"},
        {"name": "Mondaq - US Immigration Updates", "url": "https://www.mondaq.com/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
    "body": article2_body
}

# ─── INSERT ───────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")
