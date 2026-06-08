#!/usr/bin/env python3
"""
Videshi Immigration Writer — 2026-06-08
Two fresh articles on immigration topics for the Indian diaspora.
"""
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
    # ── ARTICLE 1 ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "'Why Did You Stay?' — The New Question That Could Derail Your Green Card Interview",
        "subheadline": "USCIS officers are now asking adjustment-of-status applicants to justify choosing to remain in the United States instead of going through consular processing abroad — and 'because it's easier' is the wrong answer.",
        "slug": make_slug("uscis-aos-interview-question-why-did-you-stay-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Hundreds of thousands of Indian H-1B holders in EB-2 and EB-3 queues have pending I-485 applications. The new interview questioning means they must now articulate — with documents and careful answers — why they deserve to adjust status inside the US rather than fly to Chennai or Mumbai for consular processing.",
        "tags": ["uscis", "green-card", "adjustment-of-status", "consular-processing", "h1b", "eb2", "eb3", "i-485", "pm-602"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/uscis-officers-question-why-12m-green-card-applicants-choose-adjustment-of-status-over-consular-processing/"},
            {"name": "Nolo Legal", "url": "https://www.nolo.com/legal-encyclopedia/what-to-expect-at-your-family-based-adjustment-of-status-interview.html"},
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/category/immigrant-family/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "image_caption": "An opened passport showing visa stamps, the kind of document USCIS officers are scrutinising more closely",
        "image_attribution": "Pexels",
        "body": """For decades, adjustment of status was the quiet default. You filed your I-485, showed up at a USCIS field office with your documents, answered some questions, and — assuming nothing was wrong — walked out a step closer to permanent residency. The alternative, consular processing, meant flying to a US embassy abroad and hoping a consular officer stamped your immigrant visa before your employer lost patience.

Most Indian professionals on H-1B visas chose to stay. They had jobs, mortgages, children in school. The law allowed it. Nobody asked why.

Now USCIS is asking.

## The Shift Nobody Saw Coming

On May 21, 2026, USCIS issued Policy Memorandum PM-602-0199, formally declaring that adjustment of status under Section 245 of the Immigration and Nationality Act is "an extraordinary act of administrative grace" — not a right. The language was clinical but the implication was blunt: USCIS officers now have explicit instructions to treat staying in the US for your green card as something that requires justification, not merely eligibility.

Reports from recent adjustment interviews confirm the shift is already operational. Officers are asking applicants — including those with clean records, valid H-1B status, and approved I-140 petitions — a deceptively simple question: "Why did you choose adjustment of status instead of consular processing?"

The question is not rhetorical. And the answer matters.

## What Officers Want to Hear

Immigration attorneys tracking the trend say officers are no longer satisfied with statutory eligibility alone. They want to know why approval *inside* the United States is warranted as a matter of discretion.

A persuasive answer, attorneys say, ties the choice to lawful status, work continuity, family stability, and full compliance with US immigration and tax rules. An H-1B worker might explain that they maintained valid status continuously, supported family members, paid taxes, and followed the legal process available to applicants physically present in the country.

What officers do not want to hear: "Because it's easier" or "Because I didn't want to travel." USCIS may interpret such answers as dismissing the discretionary question rather than engaging with it.

One template circulating among applicants and attorneys captures the expected tone: "I am lawfully present in the United States and eligible to apply for Adjustment of Status under the immigration law. I have maintained my status, complied with US immigration and tax requirements, and have ongoing employment and family ties here."

That is a starting point — not a script. Every case needs to be adapted to its own facts.

## Who Is Most Exposed

The people most affected are those who have been waiting the longest — which means, disproportionately, Indian nationals.

Roughly 627,000 Indian-born immigrants are stuck in the employment-based green card backlog, according to Brookings Institution estimates. Many have spent a decade or more in the US on H-1B visas, watching EB-2 and EB-3 priority dates crawl forward at geological speed. They have built careers, bought homes, raised children who speak English as a first language. They filed I-485 applications years ago and assumed the final interview would be routine.

It may no longer be.

Applicants with any complication — prior status gaps, a job change that created a brief period of unauthorised employment, a visa overstay during a transition, tax filing irregularities, or a prior visa denial — face the highest risk. But even clean cases may draw pointed questions. An officer can ask why AOS was chosen regardless of the applicant's record.

EB-5 investors physically present in the US, L-1 executives, and F-1 students who later changed to H-1B status are all within the interview risk pool.

## The Catch-22

The policy creates a particularly cruel bind for Indian workers in long backlogs. Consular processing requires leaving the United States for an immigrant visa interview at a US embassy — typically Chennai or Mumbai. But the same policy environment that now questions why you stayed also makes leaving risky: the PM-602 memo, combined with heightened consular scrutiny and the possibility of administrative processing delays abroad, means that an Indian worker who leaves for consular processing may not easily return.

Stay, and you must justify staying. Leave, and you may not come back.

## What to Prepare

Immigration attorneys are advising clients to treat the adjustment interview as an affirmative case for discretion, not a checkbox exercise. The documentation checklist now extends well beyond the standard I-485 filing:

Employment records — verification letters, pay stubs, W-2 forms, tax returns — showing continuous lawful employment. Family evidence — marriage certificates, children's birth certificates, joint leases or mortgages, school enrolment records. Community ties — volunteer work, professional licences, property ownership. Tax compliance — filed returns for every year in the US, with proof of payment.

Prior petition approvals do not settle the question. An approved I-140 does not guarantee I-485 approval, because the two decisions are legally separate.

## The Bigger Picture

The PM-602 memo does not end adjustment of status. It changes the atmosphere around it. What was once a routine administrative pathway is now framed as a privilege that must be earned — and explained.

For the hundreds of thousands of Indian professionals who chose to build their lives in America while waiting for a green card, the message is clear: the system that invited you to stay is now asking you to defend that choice. Have your answer ready."""
    },

    # ── ARTICLE 2 ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty-Nine Percent — The Talent Pipeline That Built Silicon Valley Is Collapsing",
        "subheadline": "A Brookings Institution analysis finds that F-1 student visas are projected to drop by nearly a third, only 85 companies have paid the $100,000 H-1B fee, and 1.2 million immigrants are trapped in green card backlogs — with Indians bearing the heaviest burden at every stage.",
        "slug": make_slug("brookings-talent-pipeline-collapse-f1-h1b-green-card-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students and workers dominate every stage of the US talent pipeline — 43% of F-1 visas, 72% of H-1B approvals, and 627,000 of the 1.2 million green card backlog. The Brookings analysis shows that every policy squeeze hits Indians hardest, from the F-1 application chill to the wage-weighted H-1B lottery to the EB-2/EB-3 queues that stretch decades.",
        "tags": ["brookings", "f1-visa", "h1b", "green-card-backlog", "talent-pipeline", "opt", "indian-students", "immigration-policy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "BBC / CEDI Rates", "url": "https://www.cedirates.com/india-wants-to-lure-its-best-minds-back-from-the-us/"},
            {"name": "US Chamber of Commerce v DHS", "url": "https://www.mccarter.com/insights/chamber-of-commerce-v-dhs/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7972741/pexels-photo-7972741.jpeg",
        "image_caption": "International students in graduation gowns — the first stage of a talent pipeline now under pressure at every junction",
        "image_attribution": "Pexels",
        "body": """The numbers arrive in a Brookings Institution research paper, 28 pages of charts and footnotes, the kind of document that gets circulated among policy staffers and then quietly ignored by the people making the decisions. But the headline figure is hard to ignore: a projected 29 percent decline in F-1 student visa issuances in 2025 alone.

That is not a dip. That is the front door of the American talent pipeline swinging shut.

## The Full Anatomy of a Collapse

The Brookings analysis, published in late May 2026, tracks what happens when you squeeze every stage of an immigration system simultaneously. Start with students, move to temporary workers, end with permanent residents. At each junction, the restrictions compound.

**Stage one: students.** The number of international students studying in the US reached an all-time high of 1.18 million in the 2024-2025 school year. Chinese and Indian students accounted for roughly 43 percent of all F-1 visas issued in 2024. But new issuances are projected to fall by 29 percent in 2025, driven by visa revocations, SEVIS terminations, and what Brookings calls a "demand chill" — prospective students simply deciding the US is no longer worth the risk.

The Trump administration terminated the SEVIS status of 1,800 international students without warning last spring, many from Muslim-majority countries. The State Department has publicly boasted about revoking 8,000 student visas. The message to families in Hyderabad and Chennai considering a $200,000 investment in an American master's degree is unambiguous.

**Stage two: post-graduation work.** After graduation, 72 percent of international students participate in Optional Practical Training — the programme that lets them work in the US for up to three years in STEM fields. Over 290,000 students were on OPT in the 2024-2025 school year. The Chip Roy bill introduced in June proposes eliminating OPT entirely. A separate DHS rule would end "Duration of Status" for F-1 visas, replacing it with a fixed four-year admission period and killing the Day-1 CPT pathway that thousands of Indian engineers use as a safety valve after losing the H-1B lottery.

**Stage three: H-1B.** The September 2025 presidential proclamation imposed a $100,000 fee on new H-1B petitions. Nine months later, only about 85 companies have paid it. The US Chamber of Commerce and a coalition of businesses have challenged the fee in court, but it remains in effect. Meanwhile, a December 2025 final rule replaced the random H-1B lottery with a wage-weighted system that prioritises higher-paid applicants — effectively disadvantaging early-career workers and anyone outside the top salary bands. The FY2027 H-1B cap was hit on March 31, 2026, just 25 days after applications opened.

**Stage four: green cards.** Brookings estimates the employment-based green card backlog at approximately 1.2 million people, including family members. Of those, roughly 627,000 were born in India. The base annual cap of 140,000 employment-based green cards has not changed since 1990 — and roughly half of those go to spouses and children, not workers. The 7 percent per-country ceiling means Indian applicants face wait times that stretch decades beyond what applicants from smaller countries experience.

Three-quarters of all employment-based green cards are issued through "adjustments of status" — meaning the recipients were already in the US on temporary visas. Squeeze the student and H-1B pipelines, and fewer people are in position to adjust. The downstream effect is mathematical.

## What India Stands to Lose — and Gain

The squeeze is already reshaping talent flows. A BBC report found that enquiries to relocation firms from Indian professionals exploring a return to India have nearly tripled since Trump's second term began. Executive search firms report a 30 percent increase in Ivy League Indian graduates looking at jobs back home. Global Capability Centres — the offshore R&D offices that companies like Microsoft, Amazon, and Goldman Sachs have expanded across Bangalore, Hyderabad, and Pune — are absorbing some of this talent.

But the reverse brain drain remains more aspiration than reality. India's startup ecosystem and GCC boom offer legitimate opportunities, but compensation gaps, infrastructure challenges, and the sheer difficulty of rebuilding a career after a decade abroad mean most Indian H-1B holders are not packing their bags. They are staying, waiting, and hoping the system that brought them to America still has room for them.

## The Economic Stakes

The Brookings researchers are blunt about what the US stands to lose. A 2022 study cited in the paper found that since 1990, 36 percent of total US innovation can be attributed to immigrants. International students contributed $42.9 billion to the US economy last academic year and supported more than 350,000 jobs, according to NAFSA. One study estimated that inflows of foreign STEM H-1B workers drove between 30 and 50 percent of aggregate nationwide productivity growth between 1990 and 2010.

The Social Security trust fund, expected to be exhausted by the early 2030s, runs a deficit that is 26 percent smaller under a high-immigration scenario compared to a low-immigration one. College-educated immigrants paid $8.8 trillion more in taxes than they received in benefits between 1994 and 2023.

None of this has stopped the policy machinery from grinding forward.

## The Compound Effect

What makes the Brookings analysis unusual is its refusal to treat each policy change in isolation. The F-1 decline feeds the OPT decline, which feeds the H-1B shortfall, which feeds the green card backlog. The system was designed as a pipeline; disrupt any segment and the flow downstream slows.

For Indian professionals — who dominate every stage of this pipeline — the compound effect is existential. Fewer students means fewer OPT workers. Fewer OPT workers means fewer H-1B applicants. Fewer H-1B holders means fewer people in the green card queue. And fewer people in the queue means fewer of the skilled workers that American companies, universities, and tax rolls depend on.

The pipeline was never perfect. It was slow, bureaucratic, and punishingly unfair to Indians in particular. But it worked. Whether it continues to is no longer a question of policy drift. It is a question of deliberate choice."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
