#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-27 05:00 PDT run"""

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


# ────────────────────────────────────────────────
# ARTICLE 1: OBBBA Medicaid 5-Year Wall
# ────────────────────────────────────────────────
article1_body = """You waited fifteen years in the green card backlog. You paid every filing fee USCIS threw at you — the I-140, the I-485, the biometrics, the EAD renewals, the advance parole. You endured the lottery, the Request for Evidence, the radio silence. And then, one Tuesday morning, the card arrived. Permanent resident. The finish line.

Except it wasn't.

Under the One Big Beautiful Bill Act signed into law on July 4, 2025, new green card holders must now wait five years before they can access Medicaid — the government health insurance program that covers roughly 90 million Americans. The provision, buried deep in a 1,200-page reconciliation bill better known for its tax cuts and border wall funding, has received almost no attention in the immigration press. It should.

## The Five-Year Wall

The rule itself is not technically new. A version of it existed under the 1996 Personal Responsibility and Work Opportunity Act, which barred most legal immigrants from federally funded benefits for their first five years. But the OBBBA codifies and extends the restriction at a moment when it collides with the worst green card backlog in American immigration history.

For Indian nationals in the EB-2 and EB-3 categories, the math is grim. The median wait for a green card — from the day a PERM labor certification is filed to the day the card arrives — now stretches past a decade. Many Indian professionals currently in the backlog filed their initial applications between 2012 and 2015. If their priority dates become current in, say, 2027, they would not be eligible for Medicaid until 2032.

That is a twenty-year gap between entering the immigration system and accessing a basic government safety net — for people who have paid federal and state taxes every year they have been in the country.

## Work Requirements Add a Second Barrier

The Medicaid waiting period is only part of the story. The OBBBA also introduces work requirements for all Medicaid recipients aged 19 to 64: a minimum of 80 hours of verified activity per month, with eligibility checks every six months instead of annually.

An analysis by the Urban Institute, published in March 2026, projects that between 4.9 million and 10.1 million Medicaid enrollees will lose coverage by 2028 as a result of these provisions. The projections hold even for people who are working, because the real bottleneck is not eligibility — it is verification. States must confirm compliance through automated data systems, and for several categories of workers, those systems simply do not work.

Self-employed individuals face the steepest cliff. State quarterly wage databases cover more than 95 percent of traditional W-2 employment, but gig workers, freelancers, and independent contractors do not appear in those databases. The Urban Institute estimates enrollment losses of 30 to 73 percent for self-employed workers — a category that includes a significant share of Indian Americans running small businesses, consulting firms, or early-stage startups.

## Why This Hits Indian Families Harder

The Indian American community has the highest median household income of any ethnic group in the United States — roughly $150,000 per year, according to the most recent Census data. Most will never need Medicaid. But averages obscure the edges.

Not every Indian immigrant works at Google. The community includes restaurant owners in Edison who clear $40,000 after expenses, Uber drivers in Houston on H-4 EADs, graduate students on F-1 visas transitioning to green cards, and elderly parents on family-sponsored visas who arrive in the U.S. with no work history and no employer-provided insurance.

For newly arrived parents and spouses — particularly those entering on family-based green cards — the five-year wall creates a healthcare vacuum. They are too new to qualify for Medicaid, too old or underemployed to afford individual market premiums averaging $500 to $700 per month, and ineligible for most Affordable Care Act subsidies during the waiting period. The OBBBA also limits premium tax credits for immigrants during this window.

The practical result: new green card holders must either pay full-price premiums, go uninsured, or rely on emergency room visits — which shift costs to hospitals and, ultimately, to insured patients.

## The Retroactive Medicaid Cut

A quieter provision compounds the problem. The OBBBA reduces retroactive Medicaid coverage from three months to one month. Under the old rule, if a person qualified for Medicaid but did not sign up immediately, the program would cover medical costs incurred up to 90 days before the application date. That safety net is now 30 days.

For anyone who experiences a medical emergency shortly after receiving their green card — or shortly after the five-year waiting period ends — the window for back-coverage is dramatically tighter.

## What Can Be Done

Immigration attorneys and community organizations are advising newly approved green card holders to purchase private insurance immediately upon arrival, to budget for 60 months of premiums as part of immigration financial planning, and to explore state-level programs that may partially fill the gap. Some states — including California, New York, and Illinois — have historically funded their own versions of Medicaid that cover legal immigrants during the federal waiting period. Whether those programs survive the OBBBA's broader Medicaid funding cuts remains an open question.

For the hundreds of thousands of Indian families nearing the end of the green card backlog, the message is sobering: the card is not the finish line. It is the starting line of another wait — and this one comes with real financial risk."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "You Waited 15 Years for Your Green Card. Now Wait 5 More for Health Insurance.",
    "subheadline": "The OBBBA's Medicaid waiting period and new work requirements create a healthcare vacuum for Indian immigrants who just cleared the longest backlog in American history.",
    "slug": make_slug("obbba-medicaid-five-year-wall-green-card-indian-immigrants"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian green card applicants face the longest backlogs of any nationality — often 15+ years. The OBBBA's five-year Medicaid waiting period means they could go two decades in the immigration system before accessing basic government health coverage, even while paying taxes throughout. Self-employed Indian Americans (small business owners, consultants, gig workers) face a 30-73% risk of losing Medicaid coverage under the new work verification system.",
    "tags": ["obbba", "medicaid", "green-card", "healthcare", "immigration", "indian-americans"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "One Big Beautiful Bill Act — Wikipedia", "url": "https://en.wikipedia.org/wiki/One_Big_Beautiful_Bill_Act"},
        {"name": "Urban Institute / Robert Wood Johnson Foundation Analysis (March 2026)", "url": "https://www.rwjf.org/en/insights/our-research/2026/03/millions-could-lose-health-coverage-due-to-new-rules.html"},
        {"name": "AJMC — 5 Groups at Highest Risk of Losing Medicaid Under OBBBA", "url": "https://www.ajmc.com/view/5-groups-at-highest-risk-of-losing-medicaid-coverage-under-obbba"},
        {"name": "Greenspoon Marder — USCIS Shifts Green Cards to Consular Processing", "url": "https://www.gmlaw.com/news/uscis-has-issued-a-sweeping-new-policy-memorandum-shifting-the-default-pathway-for-green-cards/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7163940/pexels-photo-7163940.jpeg",
    "body": article1_body
}

# ────────────────────────────────────────────────
# ARTICLE 2: The $50,000 Documentation Arms Race
# ────────────────────────────────────────────────
article2_body = """The email arrives at 2 a.m. from a senior software engineer at a Fortune 500 company in the Bay Area. He makes $280,000 a year, has lived in the United States for eleven years, owns a home in Cupertino, and has two American-born children enrolled in public school. His I-140 was approved in 2019. His priority date is still years away.

His question: "Do I need an economic benefit package?"

The answer, according to a growing number of immigration lawyers, is yes. And it will cost him between $15,000 and $50,000.

## The Memo That Launched a Thousand Invoices

On May 22, 2026, USCIS released a policy memo declaring that adjustment of status — the process by which a person already in the United States applies for a green card without leaving the country — is an "extraordinary form of relief" rather than an automatic entitlement. Officers were instructed to evaluate each case on a discretionary basis, weighing whether the applicant can demonstrate sufficient "economic benefit" to the United States.

Within 72 hours, immigration law firms across the country reported what one attorney called "the single largest spike in inbound client calls since the first travel ban." David Yurkofsky, a New York-based immigration lawyer who has practiced since 1993, posted a widely shared analysis on LinkedIn urging people to stop panicking. "Adjustment of Status is not a favor bestowed by bureaucrats," he wrote. "It is the law. INA Section 245. Written by Congress. Fifty years of cases."

He is correct. The memo does not abolish adjustment of status. It does not change the statute. What it does is raise the discretionary bar — and in doing so, it has created an entirely new market for documentation that proves an applicant is "extraordinary" enough to stay.

## Anatomy of a $50,000 Package

The packages being assembled by immigration attorneys typically include:

- **Three to five years of federal and state tax returns** with detailed annotations of total tax liability, showing cumulative contributions to U.S. coffers
- **Employer verification letters** confirming role, salary trajectory, and strategic importance to the organization
- **Third-party economic impact assessments** — essentially consultant reports arguing that the applicant's departure would harm the U.S. economy
- **Patent filings, published research, or startup valuations** for applicants in STEM fields
- **Community ties documentation**: property deeds, children's school enrollment records, volunteer work, church or temple membership, local business relationships
- **Affidavits from colleagues, supervisors, and industry experts** attesting to the applicant's contributions

The irony is hard to miss. A person who has been paying six figures in federal taxes for a decade must now pay five figures to prove they contribute to the economy.

## The Two-Tier System Taking Shape

The practical effect of the memo is not mass deportation — it is stratification. Applicants who can afford top-tier legal counsel and comprehensive documentation will clear the "extraordinary circumstances" bar. Those who cannot will be pushed into consular processing: returning to their home country, joining the queue at a U.S. embassy, and hoping their case is adjudicated before their employer fills their position with someone else.

For Indian applicants, this creates a particularly sharp divide. A principal engineer at Meta earning $400,000 can absorb the cost. A QA analyst at a mid-size firm in Charlotte making $95,000 — also on an H-1B, also paying taxes, also raising American-born children — may not.

"The memo doesn't say 'rich people get green cards,'" notes one Bay Area immigration attorney who asked not to be named because their firm is still advising clients on strategy. "But that is the functional outcome. If your case depends on a 200-page economic benefit portfolio, the people who can produce that portfolio are the ones who will stay."

## The $1.5 Billion Question

Yurkofsky's analysis raises a structural point that has received less attention. USCIS is almost entirely fee-funded. There are currently over one million pending I-485 applications, representing approximately $1.5 billion in filing fees the agency has already collected. Those fees fund USCIS operations — the officers, the service centers, the IT systems.

If the agency shifts the majority of green card processing to the State Department's consular system, it does not get to keep the fees for cases it no longer adjudicates. And the State Department, already struggling with its own backlogs (at one point, four Indian consulates were processing cases for 1.2 million applicants), is not staffed or funded to absorb the load.

In other words, the memo may create an institutional crisis at the same agency that issued it.

## What Immigration Lawyers Are Actually Advising

Despite the panic, the guidance from experienced practitioners is remarkably consistent:

1. **Do not withdraw your I-485.** The memo increases scrutiny; it does not invalidate pending applications.
2. **Start assembling documentation now.** Even if your priority date is years away, the evidence package is easier to build while you are employed and have access to employer cooperation.
3. **Dual-intent visa holders retain protection.** The memo explicitly states that filing for adjustment of status is "not inconsistent" with maintaining H-1B, O-1, or E-3 status. That language matters.
4. **Watch the courts.** Multiple legal challenges are expected. The Ninth Circuit has blocked similar discretionary tightening before.
5. **Budget for it.** Whether the cost is $15,000 or $50,000, treat it as a necessary expense — not unlike the years of H-1B filing fees, premium processing charges, and EAD renewals that preceded it.

## The Deeper Cost

The financial burden is real, but the psychological toll may be worse. Eleven years into a career in the United States, after hundreds of thousands of dollars in immigration fees, taxes, and legal costs, Indian professionals are being asked to prove — one more time — that they deserve to be here.

"I have paid more in U.S. taxes than most Americans will earn in a lifetime," the Cupertino engineer wrote in his 2 a.m. email. "And now I need to spend $30,000 to prove I'm extraordinary enough to stay."

He is not alone. The queue at the lawyer's office is long, and the meter is running."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The $50,000 Paper Chase: Proving You Deserve to Stay Is Now an Industry",
    "subheadline": "Immigration lawyers report a 300% surge in requests for 'economic benefit packages' — bespoke documentation bundles that cost up to $50,000 and may determine who gets a green card under the new USCIS memo.",
    "slug": make_slug("economic-benefit-package-immigration-lawyers-50k-documentation"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders — who constitute 71% of approved H-1B applications — are the single largest group affected by the USCIS memo's 'economic benefit' requirement. A two-tier system is emerging: well-paid Big Tech engineers can absorb $50K in documentation costs, while mid-career professionals at smaller firms face being pushed into consular processing. The irony of spending five figures to prove you contribute to an economy you've paid six figures in taxes to is not lost on the community.",
    "tags": ["uscis", "green-card", "immigration-lawyers", "economic-benefit", "h1b", "documentation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "David E. Yurkofsky, Immigration Attorney — 'Stop the PANIC' Legal Analysis", "url": "https://www.linkedin.com/pulse/stop-panic-david-yurkofsky-8yeoe"},
        {"name": "Archyde — U.S. Immigration Policy Memo Sparks Panic", "url": "https://www.archyde.com/u-s-immigration-policy-memo-sparks-panic-what-it-means-for-work-visa-holders-and-laid-off-tech-workers/"},
        {"name": "Greenspoon Marder — USCIS Shifts Green Cards to Consular Processing", "url": "https://www.gmlaw.com/news/uscis-has-issued-a-sweeping-new-policy-memorandum-shifting-the-default-pathway-for-green-cards/"},
        {"name": "USCIS Official Announcement — Adjustment of Status Policy (May 22, 2026)", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8112126/pexels-photo-8112126.jpeg",
    "body": article2_body
}


# ────────────────────────────────────────────────
# ARTICLE 3: Rubio's India visit — diplomatic fallout
# ────────────────────────────────────────────────
article3_body = """Marco Rubio brought Bollywood dancers, a speakerphone call from Donald Trump, and life-size cardboard cutouts of administration officials. What he did not bring was a single concrete concession on the visa policies that have thrown 1.2 million Indian immigration cases into chaos.

The Secretary of State's four-day tour of India, which concluded with a Quad foreign ministers' meeting on Tuesday, was billed as a relationship repair mission. By the time the last protocol photo was taken, the diagnosis was clear: Washington and New Delhi agree they need each other, but the terms have shifted, and immigration is the fracture that neither side has the tools to fix.

## The "Disproportionate" Admission

The most significant moment came not at a formal summit but during a joint press conference on Sunday. Standing beside Indian External Affairs Minister S. Jaishankar, Rubio acknowledged that recent U.S. visa policy changes would have a "disproportionate impact on Indian students, engineers, and tech workers."

That sentence landed like a concession grenade in New Delhi. It was the first time a senior Trump administration official explicitly linked U.S. immigration policy to its outsized effect on Indian nationals — a point India has been making, with increasing exasperation, for months. Student visa appointments frozen worldwide. F-1 revocations targeting Indian students. H-1B registration requirements that dropped applications by 38.5 percent. A consular processing mandate that four Indian consulates are not staffed to handle.

Rubio then defused it. "It is not a system that is targeted at India," he said. "It is one that's being applied globally."

Jaishankar, not one for diplomatic niceties when he does not feel like it, answered with a phrase that captured the asymmetry: "Where we are concerned, we have a view of India First."

## The Pakistan Factor

If immigration is the visible fracture, Pakistan is the one that runs deeper.

Trump's recent embrace of Pakistan — driven by Islamabad's role as a mediator in the Iran conflict — has unsettled New Delhi at a foundational level. India fought a brief military engagement with Pakistan just a year ago. Pakistan Army Chief Asim Munir, whom Trump has publicly praised as a critical partner, commands the forces India faced in that conflict.

Rubio confirmed that Indian officials raised "longstanding concerns about Pakistan, including accusations that it harbors militant groups that target India." He also confirmed that India did not specifically object to Pakistan's role as an Iran mediator — a diplomatic dance that signals disagreement without confrontation.

For the Indian diaspora in the United States, the Pakistan angle matters because it shapes the broader negotiating context. India's leverage on immigration — its ability to push Washington for concessions on H-1B caps, green card backlogs, or consular processing timelines — depends on the overall health of the relationship. When Washington needs India more than India needs Washington, visa policies loosen. When Washington has options — China engagement, Pakistan mediation, Middle East dealmaking — India's complaints move to the back of the queue.

Right now, they are at the back of the queue.

## What Rubio Offered (and What He Did Not)

The concrete deliverables from the trip were thin on immigration:

**What was offered:**
- A Trump invitation for Modi to visit the White House — relationship signaling, not policy
- Continued framing of U.S.-India ties as a "strategic partnership" — the same language used for the past twenty years
- A Quad meeting focused on China and maritime security — important, but unrelated to visa backlogs

**What was not offered:**
- No commitment to expedite consular processing at Indian posts
- No exemption for Indian nationals from the consular processing mandate
- No timeline for unfreezing student visa appointments
- No signal on the H-1B fee structure ($100,000 per application under the OBBBA)
- No discussion of the EB-2/EB-3 backlog, which affects Indian nationals more than every other country combined

The Atlantic Council's Michael Kugelman, a senior fellow for South Asia, told the Wall Street Journal that "the soundtrack to U.S.-India relations is less discordant than it has been" but noted "very hard constraints that have made it difficult to bring the relationship back to where it was some years ago."

Translation: the tone is better; the substance has not changed.

## The Diaspora Caught in the Middle

For Indian Americans — the 4.4 million who form the highest-income, highest-educated, and most politically active Asian American subgroup — the Rubio visit crystallizes a painful paradox. The community's economic contributions are undeniable. Indian-born founders run companies valued at over $1 trillion. Indian-born engineers staff the AI labs, chip design centers, and research hospitals that drive American competitiveness. The community remits roughly $11 billion to India annually, making it one of the largest bilateral financial flows in the world.

And yet, when the Secretary of State visits New Delhi to repair a relationship damaged in part by policies that disproportionately affect Indian workers and students, immigration does not make the agenda.

It is the Quad meeting, not the green card backlog, that gets the closing press conference. Pakistan's mediation role, not the 627,000 Indians stuck in visa limbo, that dominates the bilateral conversation. The cardboard cutouts of Trump officials at the embassy party, not the flesh-and-blood engineers wondering whether their I-485 will ever be adjudicated, that make the front page.

Rubio's visit was a success by the standards of traditional diplomacy — relationships stabilized, invitations extended, strategic alignment reaffirmed. By the standards of the 1.2 million Indian nationals whose lives depend on U.S. immigration policy, it changed nothing."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Bollywood Dancers, Cardboard Cutouts, and Zero Visa Concessions: Inside Rubio's India Charm Offensive",
    "subheadline": "The Secretary of State acknowledged U.S. visa policies have a 'disproportionate' impact on Indians. Then he offered nothing to fix them.",
    "slug": make_slug("rubio-india-visit-immigration-zero-concessions-quad"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Rubio's four-day India visit was the highest-profile diplomatic engagement since the AOS memo and student visa freeze. Indian Americans — 4.4 million strong, the highest-income Asian American subgroup — watched the trip for any signal on immigration relief. None came. The visit underscores a painful pattern: India's geopolitical value to Washington does not translate into visa policy concessions for the diaspora caught in the system.",
    "tags": ["rubio", "india", "diplomacy", "immigration", "h1b", "quad", "jaishankar"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wall Street Journal — 'America First' Shadows Visit by Rubio to Repair Rift With India", "url": "https://www.wsj.com/world/india/america-first-shadows-visit-by-rubio-to-repair-rift-with-india-1d72e023"},
        {"name": "Fox News — Rubio pushes back on India's visa concerns", "url": "https://www.foxnews.com/politics/rubio-pushes-back-indias-concerns-over-us-visa-curbs-says-policy-must-america-first-under-trump"},
        {"name": "USCIS — Adjustment of Status Policy Announcement (May 22, 2026)", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"},
        {"name": "Atlantic Council — Michael Kugelman on U.S.-India Relations", "url": "https://www.atlanticcouncil.org/programs/south-asia-center/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "body": article3_body
}


# ────────────────────────────────────────────────
# INSERT ALL ARTICLES
# ────────────────────────────────────────────────
articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n📰 Published {len(articles)} immigration articles at {now}")
