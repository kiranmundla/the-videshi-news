#!/usr/bin/env python3
"""Immigration writer — 2026-06-09 08:00 UTC run."""

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


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Domestic Visa Renewal Pilot for Indian Workers
# ─────────────────────────────────────────────────────────────

article1_body = """The State Department has quietly confirmed one of the most consequential changes for Indian H-1B workers in years: a domestic visa renewal programme that will allow tens of thousands of Indian nationals to get their visas stamped without leaving the United States.

Julie Stufft, the Deputy Assistant Secretary of State for Visa Services, laid out the plan in unusually direct terms. Starting in December, the State Department will process 20,000 visa renewals inside the country over a three-month pilot. The vast majority of those slots, she said, will go to Indian nationals.

"Because Indians are the largest skilled group of workers in the United States, we hope that India will benefit quite a bit from this programme," Stufft said. "It will prevent people from having to travel back to India or anywhere for a visa appointment to get their visa renewed."

## The Problem It Solves

Anyone who has ever renewed an H-1B visa stamp knows the drill. You book a flight to India — or, increasingly, a third country — schedule a consular appointment months in advance, hand over your passport, and wait. If you are lucky, you get it back in two weeks. If you are not, you are stranded abroad for months, watching your American job slip away.

The bottleneck is brutal. Indian consulates have been running wait times of six to twelve months for visa interview slots. The State Department's own expanded social-media vetting requirements — which mandate online-presence reviews for all H-1B applicants — have compressed the number of daily interviews each consulate can conduct. Posts in Hyderabad and Chennai began mass-rescheduling appointments late last year, pushing some slots out by four to six months.

For employers, the calculus is equally grim. An H-1B worker stuck abroad is a seat that cannot be filled, a project that stalls, a team that reorganises around absence. Export-control and payroll rules in most states make it illegal to simply let the employee work remotely from India while waiting.

## What Changes

The domestic renewal programme eliminates the trip entirely. Eligible H-1B holders will complete a DS-160 application online, mail in their passport, and receive a new visa foil by courier — all without leaving the country. A federal register notice laying out the full eligibility criteria and instructions is expected "very soon," according to Stufft.

The pilot builds on an earlier, smaller-scale programme the State Department tested in 2024, when it processed a limited batch of renewals for H-1B holders whose visas were originally issued in India or Canada. The December expansion is far more ambitious in scale: 20,000 renewals in three months, with plans to grow if the initial tranche goes smoothly.

## Why It Matters for Indian Americans

Three-quarters of all H-1B visas go to Indian nationals. For this population, the domestic renewal programme is not an incremental convenience — it is a structural fix for what has been one of the most anxiety-inducing aspects of working in America on a temporary visa.

The timing is significant. The programme arrives during a period of extraordinary uncertainty for Indian H-1B workers. A federal judge struck down the $100,000 visa fee this week, but the ruling faces appeal. Chip Roy's American White-Collar Worker Jobs Act threatens to slash visa durations from six years to two. The EB-2 India green card queue remains effectively frozen until October.

Against that backdrop, a programme that removes one major friction point — the need to leave the country to renew a document — is the kind of practical, low-drama improvement that actually changes daily life for hundreds of thousands of Indian professionals and their families.

Stufft framed the move as a win for the consulates too. "It will allow our missions in India to concentrate on new applicants," she said. Fewer renewals clogging the pipeline in Mumbai and Hyderabad means faster first-time appointments — a relief for students, tourists, and the next wave of workers entering the system.

The federal register notice, when it drops, will be one of the most closely read documents in the Indian American immigration community this year. The details — who qualifies, which visa classes are included beyond H-1B, how the mailing process works — will determine whether 20,000 slots is a meaningful dent or just a starting point."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "No More Flights Home — America Will Now Stamp Your H-1B Visa Without You Leaving the Country",
    "subheadline": "The State Department will process 20,000 domestic visa renewals starting in December, with the vast majority of slots going to Indian nationals.",
    "slug": make_slug("domestic-visa-renewal-h1b-india-20000-state-department"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Three-quarters of H-1B holders are Indian nationals. The domestic renewal programme eliminates the most dreaded ritual in their American working life — the trip home for visa stamping that can strand you abroad for months and jeopardise your job.",
    "tags": ["h1b", "visa-renewal", "state-department", "uscis", "indian-workers", "domestic-renewal"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/us-to-launch-new-plan-for-work-visas-in-december/"},
        {"name": "Fragomen (Immigration Law)", "url": "https://www.fragomen.com/insights/the-state-departments-domestic-visa-renewal-pilot.html"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-08/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "An open passport with visa stamps — a sight Indian H-1B workers may no longer need to collect abroad",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}


# ─────────────────────────────────────────────────────────────
# ARTICLE 2: AI Companies Ramp Up H-1B Filings
# ─────────────────────────────────────────────────────────────

article2_body = """While the rest of Silicon Valley slashes headcount and freezes hiring, the companies building the most powerful AI systems on earth are doing the opposite — they are pulling harder on the H-1B visa pipeline than ever before.

Federal Department of Labor data from the second quarter of fiscal 2026 tells a striking story. Anthropic filed 59 certified H-1B labour condition applications, up from just 10 in the same period a year earlier — a nearly six-fold increase. OpenAI filed 63, more than tripling its Q2 2025 count of 20. Nvidia, already the dominant chipmaker in the AI stack, pushed its count to 765 from 641.

The numbers are small in absolute terms. But the trajectory is unmistakable, and it runs against the grain of everything else happening in tech immigration.

## The Great Divergence

The broader tech industry is retreating from H-1B sponsorship. Mass layoffs at Meta, Google, Amazon, and dozens of mid-tier firms have flooded the job market with experienced domestic talent, reducing the pressure to recruit abroad. The $100,000 visa fee — struck down by a federal judge this week, but still facing appeal — has added cost uncertainty to every new petition. USCIS processing times for premium cases have stretched. The political climate around work visas is the most hostile in a generation.

Against that backdrop, Anthropic, OpenAI, and Nvidia are accelerating. The reason is straightforward: the talent they need barely exists anywhere, and the fraction that does exists disproportionately holds non-American passports.

Building frontier AI models requires a particular kind of researcher — someone who can work at the intersection of large-scale distributed systems, advanced mathematics, and experimental machine-learning techniques. The global pool of people with that combination of skills is measured in the low thousands. Many trained at American universities, hold Indian or Chinese passports, and are precisely the workers the H-1B programme was designed to attract.

## The Indian Pipeline

Indian nationals make up the single largest share of H-1B recipients — roughly 72 per cent of all approvals in recent years. For AI companies, the dependence is even more concentrated. The graduate programmes at Stanford, MIT, Carnegie Mellon, and Berkeley that produce the researchers these firms recruit draw heavily from IIT, IIIT, and BITS graduates who arrive on F-1 student visas and transition to H-1B status after completing their degrees.

The salary data underscores the point. Nvidia's average H-1B compensation hit $202,000 in 2025. At OpenAI and Anthropic, senior research scientists command packages well north of $400,000. These are not the low-wage replacement workers that critics of the programme describe — they are among the highest-paid employees at companies that are themselves among the most valuable on earth.

## What It Means for the Visa Debate

The AI hiring surge complicates the political narrative around H-1B reform. Chip Roy's American White-Collar Worker Jobs Act, introduced last week, would replace the lottery with a wage-based selection system — a change that would actually benefit the workers these AI companies are recruiting, since they sit at the very top of the salary distribution.

But the same bill would slash visa durations to two years and eliminate the path to permanent residency, which could make it harder for companies to retain the researchers they hire. A two-year clock creates a revolving door: recruit, train, lose. For an Indian researcher who might otherwise spend a decade at a single lab, contributing to American AI dominance, the incentive shifts toward taking a position in London, Toronto, or Singapore instead.

Nvidia CEO Jensen Huang and OpenAI CEO Sam Altman have both publicly backed immigration reform that attracts top talent. "We want all the brightest minds to come to the United States," Huang told CNBC. Altman called for "streamlining the process and also delineating financial incentives."

For the tens of thousands of Indian engineers watching the visa debate from inside American labs and campuses, the AI companies' hiring data offers a counterpoint to the prevailing doom. The most consequential technology race of the century still runs through American offices, and the workers powering it still disproportionately carry Indian passports. Whether Washington's immigration policy catches up to that reality — or drives the talent elsewhere — remains the open question."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic, OpenAI and Nvidia Are Hiring More Foreign Workers Than Ever — While Everyone Else Pulls Back",
    "subheadline": "Federal data shows the three companies at the centre of the AI race have dramatically increased H-1B visa filings, even as the broader tech industry retreats from the programme.",
    "slug": make_slug("anthropic-openai-nvidia-h1b-filings-surge-ai-talent-war"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals hold 72 per cent of H-1B visas and dominate the graduate pipelines that feed AI research labs. The surge in filings by frontier AI companies is a direct lifeline for Indian engineers — and a high-stakes test of whether visa policy will keep them in America or push them to competing hubs abroad.",
    "tags": ["h1b", "ai", "anthropic", "openai", "nvidia", "tech-hiring", "indian-engineers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Business Insider (via EuropeSays)", "url": "https://europesays.com/2145063/h-1b-visa-filings-rise-for-anthropic-openai-nvidia-people/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/federal-judge-strikes-down-trumps-100k-h-1b-visa-fee-ruling-unconstitutional-tax"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-08/"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/u-s-tech-workforce-dependency-and-h-1b-visa-trends-identifying-high-growth-investment-opportunities/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "image_caption": "Nvidia CEO Jensen Huang, whose company filed 765 H-1B applications in Q2 2026",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ─────────────────────────────────────────────────────────────
# ARTICLE 3: NIW Denial Rates Now Outpace EB-1A
# ─────────────────────────────────────────────────────────────

article3_body = """For years, the EB-2 National Interest Waiver was the escape hatch. If you were an Indian engineer stuck in a green card queue that stretched decades into the future, the NIW offered something radical: a self-sponsored petition that bypassed the employer-dependent PERM labour certification entirely. No job offer required. No waiting for your company's lawyers to file. Just you, your credentials, and a case that your work benefits the United States.

The word spread through every Indian tech worker group chat in America. File an NIW. Dual-file with EB-1A. Hedge your bets. The strategy was so popular that it became standard advice from immigration attorneys. Between 2022 and 2024, NIW filings surged — particularly among Indian STEM professionals in AI, cybersecurity, and biotech.

Now the data shows the escape hatch is closing.

## The Numbers

USCIS adjudication data from the first quarter of fiscal 2025 reveals a striking reversal. The EB-2 NIW denial rate hit 37.2 per cent — the highest on record for the category. For comparison, the EB-1A "extraordinary ability" denial rate in the same quarter was 25.1 per cent.

That is a complete flip from recent history. In fiscal 2022, the NIW denial rate was just 4.3 per cent while EB-1A ran at 23.2 per cent. By Q4 of 2024, the lines crossed: NIW denials reached 29 per cent against EB-1A's 27.7 per cent. The gap has only widened since.

The backlog tells a similar story. Pending NIW cases have nearly doubled, with a 4.3-month inventory now stacked up. Approval rates have fallen 13 percentage points to 54 per cent. The petition volume has dipped slightly — a sign that some applicants are reading the room — but review times continue to lengthen.

## What Changed

Immigration attorneys point to several factors behind the crackdown.

First, USCIS adjudicators are applying the *Matter of Dhanasar* framework with increasing rigour. The three-pronged test — that the proposed endeavour has substantial merit and national importance, that the applicant is well-positioned to advance it, and that waiving the labour certification serves the national interest — was always meant to be demanding. But for several years after the 2016 decision, officers interpreted it relatively generously, especially for STEM applicants.

That generosity appears to have ended. Officers are now requiring more granular evidence that the applicant's specific work — not just their field — carries national significance. A software engineer working on cloud infrastructure cannot simply argue that cloud computing is important to America. They must demonstrate that their particular contribution advances a nationally significant endeavour in a way that other qualified workers could not.

Second, the sheer volume of applications may have triggered a recalibration. When tens of thousands of mid-career Indian tech workers began filing NIWs using nearly identical templates — citing similar publications, similar citation counts, similar "national importance" arguments — the signal-to-noise ratio degraded. USCIS responded by raising the bar.

Third, Requests for Evidence have become the default rather than the exception. When an officer issues an RFE, the case sits in limbo for two to three months before re-entering adjudication. The cascading effect inflates the backlog and delays approvals even for strong cases.

## The EB-1A Paradox

The counterintuitive result is that the supposedly harder category — EB-1A, which requires evidence of "extraordinary ability" such as major awards, extensive media coverage, and significant original contributions — now has a lower denial rate than the NIW. Part of this reflects self-selection: applicants who file EB-1A tend to have stronger profiles, having already cleared a psychological bar that deters marginal candidates. Part of it reflects the maturity of the EB-1A adjudication framework, which has decades of case law guiding officers on what qualifies.

For Indian applicants, the practical implication is clear. The dual-filing strategy — EB-1A plus NIW — remains sound, but treating the NIW as the "easier" option is no longer safe. Immigration attorneys are advising clients to invest in the EB-1A case as the primary track and treat the NIW as the backup, not the other way around.

## What to Do

If you are an Indian professional considering a self-sponsored green card petition, the landscape has shifted. Submit comprehensive documentation with the initial filing. Invest in detailed expert letters that connect your specific work to a nationally significant endeavour. Do not rely on generic templates. And build extra time into your planning — the days of quick NIW approvals are behind us.

The escape hatch is still open. It is just a lot harder to fit through."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Green Card Escape Hatch Is Closing — NIW Denials Now Outpace the 'Harder' EB-1A Category",
    "subheadline": "USCIS data shows the EB-2 National Interest Waiver denial rate has hit 37 per cent, overtaking EB-1A for the first time. Indian applicants who treated it as the easy route are recalibrating.",
    "slug": make_slug("niw-denial-rate-outpaces-eb1a-indian-green-card-escape"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The NIW became the go-to self-sponsored green card route for Indian tech workers stuck in decade-long EB-2/EB-3 queues. With denial rates now higher than EB-1A, the strategy that thousands of Indian engineers relied on needs rethinking.",
    "tags": ["niw", "eb-1a", "green-card", "uscis", "indian-workers", "immigration-policy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Manifest Law", "url": "https://manifestlaw.com/eb-2-niw-denials-now-outpace-eb-1a/"},
        {"name": "Boundless Immigration", "url": "https://www.boundless.com/research/uscis-q3-2025-data-eb-1a/"},
        {"name": "AILA (American Immigration Lawyers Association)", "url": "https://www.aila.org/library/think-immigration-beyond-the-h-1b-visa-eb-1a-and-eb-2-niw-green-cards"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8441786/pexels-photo-8441786.jpeg",
    "image_caption": "A professional reviews application documents — a scene familiar to thousands of Indian green card petitioners",
    "image_attribution": "Pexels",
    "body": article3_body.strip()
}


# ─────────────────────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
