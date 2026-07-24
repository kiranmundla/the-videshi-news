#!/usr/bin/env python3
"""Immigration writer — 2026-07-06 01:00 PDT run.

Two articles:
1. Blind survey: reverse migration pay cliff for Indian tech workers
2. Global talent exodus: UK/Canada/Germany/Australia courting Indian talent
"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Load Supabase env ────────────────────────────────────────────────
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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1 — Reverse migration pay cliff
# ─────────────────────────────────────────────────────────────────────
article1_body = """The math looked simple: leave America's visa uncertainty behind, come home to India's booming Global Capability Centres, and keep building the same products for the same companies. Thousands of Indian tech workers have done exactly that over the past year. A new survey suggests the trade-off is far more punishing than the GCC brochure implies.

Blind, the anonymous professional network, surveyed 1,276 India-based tech professionals between 16 and 25 June 2026. More than half — 53 per cent — said they have personally witnessed reverse migration from the United States. At Amazon, the figure was 57 per cent; at Walmart, 58 per cent; at Uber, 55 per cent. These are the same firms scaling their India engineering centres most aggressively, and the correlation is not coincidental.

## The market that grows on paper

Here is the uncomfortable headline: 51 per cent of respondents said job opportunities in their role had actually shrunk over the past year, even as India's GCC footprint expanded to more than 1,700 centres employing roughly 510,000 engineers. Only 26 per cent said openings had grown.

The explanation, according to Blind's analysis, is structural. US Big Tech is filling new Indian seats with the same engineers it has shed in America — the same skill sets, the same institutional knowledge, at a fraction of the cost. Local talent, meanwhile, competes for whatever seats remain.

"Average pay has gone down in the last six months," one Google professional told Blind. "So you might be looking at a 1/5th pay of the US."

That ratio — roughly 80 per cent less for equivalent work — is the real price of the return ticket. For employers, the arithmetic is irresistible: retain experienced engineers, eliminate visa overhead, and cut payroll by four-fifths. For workers, it is a trade of salary for stability.

## AI is the dividing line

The pain is not evenly distributed, and the fault line runs through artificial intelligence. Among AI and machine learning engineers, 42 per cent reported fewer opportunities than a year ago — the lowest share of any discipline in the survey. Outside that track, the numbers are grimmer: 52 per cent of software engineers said opportunities had declined, alongside 54 per cent of product managers and 56 per cent of data and analytics professionals.

The pattern tracks with global hiring data. AI-adjacent roles remain scarce enough to command premiums — GCCs offered 21.1 per cent salary increases for AI/ML talent in 2026, according to Zinnov, more than double the 9.8 per cent average. Traditional software engineering, once the bedrock of India's outsourcing economy, is being squeezed from both ends: automation eroding routine tasks and returning workers flooding the applicant pool.

## Workers are not optimistic

Blind asked its respondents how the reverse migration wave would affect their own careers. The largest group — 40 per cent — chose neutrality, predicting no real impact. But negative sentiment (39 per cent) ran nearly double the positive (21 per cent). Almost a quarter said returning workers would directly take roles they might have qualified for; another 15 per cent feared the influx would raise the hiring bar across the board.

A separate Blind survey conducted in March found that 60 per cent of Indian professionals in the United States were *not* considering returning within the next two or three years. One-third said they would not accept any pay cut at all. The gap between what America pays and what India offers, even with visa uncertainty factored in, remains too wide for most to cross voluntarily.

## What this means for the diaspora

For Indian Americans watching from the other side of the Pacific, the Blind data clarifies a difficult calculation. The GCC boom is real — India is absorbing genuine engineering work, not just back-office support. But "going home" does not mean going home to equivalent compensation or equivalent career velocity.

The workers who can least afford to return — those mid-career, with mortgages and children in American schools, trapped in the EB-2 green card queue — are precisely the ones whose skills GCCs covet most. The ones who do return tend to be younger, with fewer ties and fewer sunk costs, or those who have already exhausted their visa options after successive H-1B lottery rejections.

For NRIs weighing the decision, the survey draws a sharp line: staying means visa uncertainty, but returning means a pay cliff that no amount of lower cost-of-living fully offsets. The companies, as Blind's headline puts it, are the real winners."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Same Job, One-Fifth the Pay. The Real Cost of Returning to India's GCC Boom",
    "subheadline": "A survey of 1,276 tech professionals finds that half say opportunities are shrinking even as capability centres multiply — and the salary gap with America remains punishing.",
    "slug": make_slug("gcc-reverse-migration-pay-cliff-blind-survey"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "NRIs weighing a return to India face a stark trade-off: visa stability in exchange for roughly 80 per cent less pay, with AI roles the only discipline partially insulated from the squeeze.",
    "tags": ["gcc", "reverse-migration", "h1b", "india-tech", "blind-survey", "salary"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Blind", "url": "https://www.teamblind.com/blog/workers-pushed-out-of-the-u-s-get-rehired-cheaper-in-india-u-s-big-tech-is-the-real-winner/"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/half-of-indian-tech-professionals-say-job-opportunities-have-shrunk-despite-gcc-expansion-103045.htm"},
        {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/"},
        {"name": "Blind (return intent survey)", "url": "https://www.teamblind.com/blog/going-home-isnt-worth-the-pay-cut-for-indians-in-the-u-s/"},
        {"name": "Zinnov GCC Report 2026", "url": "https://zinnov.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Software engineers working together in a modern tech office",
    "image_attribution": "Pexels",
    "body": article1_body,
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2 — Global talent exodus: UK / Canada / Germany / Australia
# ─────────────────────────────────────────────────────────────────────
article2_body = """For years, the question facing Indian tech workers in America was binary: stay and grind through the green card backlog, or go home. In 2026, a third option has arrived with force. Britain, Canada, Germany, and Australia are each rebuilding their immigration systems with a single, blunt objective — to catch the talent that America is shedding.

The scale of the American bleed is no longer anecdotal. A survey cited in a Travel and Tour World analysis found that roughly 65 per cent of US employers reported losing at least one foreign national employee in the past year due to visa-related challenges. Processing delays, Requests for Evidence, the H-1B lottery's inherent randomness, and EB-2 India's complete unavailability through September 2026 have turned legal immigration into an endurance test that many workers — and their employers — are choosing to abandon.

## The competitors and what they offer

Each rival destination has sharpened a distinct pitch.

**United Kingdom.** The Global Talent visa, expanded in 2024, requires no job offer and no employer sponsorship for workers endorsed in science, engineering, humanities, medicine, or digital technology. Processing takes roughly three weeks. The UK has also retained post-study work rights for international graduates — two years for bachelor's and master's holders, three years for doctoral graduates — at a time when America is proposing to replace Duration of Status with a rigid four-year cap.

**Canada.** Express Entry remains the benchmark points-based system: a score, a timeline, and a permanent residency outcome within months, not decades. Ottawa processed more than 110,000 Express Entry invitations in 2025 and introduced targeted draws for tech workers. The Global Talent Stream, designed for employer-referred high-skill workers, promises processing within two weeks.

**Germany.** The Opportunity Card (Chancenkarte), launched in June 2024, allows skilled workers to enter Germany for up to a year to seek employment — no job offer required. Paired with the EU Blue Card (minimum salary threshold of roughly €45,000 for shortage occupations), Germany offers a path to permanent residency in as few as 21 months. For Indian engineers accustomed to waiting 80 years in the EB-2 queue, the comparison is absurd.

**Australia.** The Global Talent visa (subclass 858) targets high-skill workers in priority sectors including technology, financial services, and healthcare. Endorsed applicants can receive permanent residency without a points test. Canberra has also lifted its permanent migration cap to 190,000 for 2024-25.

## The numbers behind America's problem

The concentration of foreign talent among top US employers underscores why the exodus matters. As of March 2026, Amazon led with 4,831 approved H-1B beneficiaries. Infosys held 3,195, Tata Consultancy Services 2,885, and Cognizant 2,657. Apple, Microsoft, Google, and Meta each employed between 1,600 and 2,400. These are not marginal hires — they are the engineering backbone of America's most valuable companies.

Indian IT services firms — Infosys, TCS, Cognizant, Capgemini — account for a disproportionate share of approved petitions, reflecting the dual-employer structure of the H-1B programme. Their workers, often among the most mobile, are precisely the ones Canada's Express Entry and Germany's Opportunity Card are designed to intercept.

The Department of Labor's proposed prevailing wage overhaul, published in March 2026, would raise the Level I floor from the 17th to the 34th percentile — an estimated $14,000 per year per worker. Employers already wary of the $100,000 H-1B fee litigation (now heading to the Supreme Court after a circuit split) may find it cheaper and faster to relocate roles to London, Toronto, or Berlin than to sponsor them in San Jose.

## Why this hits Indian Americans hardest

Indian nationals account for more than 70 per cent of all approved H-1B petitions annually. They represent the single largest group in the EB-2 and EB-3 green card backlogs, with estimated wait times exceeding a human lifetime. Every tightening of American rules — higher fees, stricter wage floors, lottery unpredictability, Duration of Status elimination — falls disproportionately on Indians because Indians are disproportionately in the system.

The competitor countries know this. Britain's Global Talent visa has seen a marked increase in Indian applicants. Canada's Express Entry draws have tilted toward tech occupations. Germany markets the Opportunity Card explicitly in Bangalore and Hyderabad. Australia's tech-focused Global Talent stream has become a viable exit ramp for engineers who have spent half a decade cycling through the H-1B lottery.

## The strategic picture

What is new in 2026 is not that other countries want skilled immigrants — they always have. What is new is the degree of coordination and the speed of policy change, all converging in a year when American immigration policy is at its most restrictive in a generation. The result is a buyers' market for Indian tech talent, and the buyer is no longer just one country.

For Indian Americans, the implication is both practical and existential. The green card queue may not clear in their working lifetimes. The H-1B renewal system, while recording a record 291,542 approvals this fiscal year, only underscores that the American model depends on perpetual temporary status rather than permanent belonging. The countries lining up to offer an alternative are betting that at some point, even the most stubborn optimist will do the arithmetic."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Britain, Canada, Germany, Australia. The Countries Lining Up to Take America's Indian Engineers",
    "subheadline": "With 65 per cent of US employers reporting foreign talent losses and EB-2 India shut for the year, rival nations are rewriting their immigration rules to intercept the workers America is pushing out.",
    "slug": make_slug("global-talent-exodus-uk-canada-germany-australia-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders facing decade-long green card waits now have structured alternatives in four major economies — each offering permanent residency in months, not lifetimes.",
    "tags": ["global-talent", "uk", "canada", "germany", "australia", "h1b", "brain-drain", "green-card-backlog"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/wue7d5l9mzrv/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/labor-department-eyes-immigration-changes-in-broad-rule-plan"},
        {"name": "WR Immigration", "url": "https://wolfsdorf.com/"},
        {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/news/2026/06/18/july-2026-visa-bulletin-uscis-continues-to-use-final-action-dates-for-eb-filings-causing-further-retrogression-for-india/"},
        {"name": "USCIS (FY2027 H-1B)", "url": "https://www.uscis.gov/newsroom/alerts/fy-2027-h-1b-initial-registration-selection-process-completed"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Flight information board displaying international departures at an airport terminal",
    "image_attribution": "Pexels",
    "body": article2_body,
}


# ── Insert articles ──────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
