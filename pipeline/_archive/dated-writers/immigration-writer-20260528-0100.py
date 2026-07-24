#!/usr/bin/env python3
"""Immigration writer — 2026-05-28 01:00 PDT batch"""

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


# ─────────────────────────────────────────────
# ARTICLE 1: AI Layoffs + 60-Day Grace Period
# ─────────────────────────────────────────────

art1_body = """The email arrives on a Tuesday morning. Your badge stops working by noon. And somewhere in the back of your mind, before the shock even registers, a clock starts ticking: sixty days.

That is the reality facing thousands of Indian tech workers in the United States right now, as artificial intelligence restructuring sweeps through Silicon Valley and beyond. Data from Layoffs.fyi shows over 110,000 tech positions have been eliminated across 144 companies in 2026 alone. For American workers, a layoff means updating LinkedIn and filing for unemployment. For the roughly 70 percent of H-1B visa holders who are Indian nationals — 283,772 out of 406,348 approved petitions in fiscal year 2025, according to USCIS data — it means something far more existential.

## The 60-Day Countdown

Under 8 CFR § 214.1(l)(2), H-1B workers who lose their jobs get a 60-day "grace period" to find a new employer willing to sponsor them, file a transfer petition, change to another visa status, or leave the country. Sixty days. That is roughly the time it takes most companies to schedule an initial phone screen.

The math is brutal. A laid-off engineer from Meta in Seattle must simultaneously find a new job, convince the new employer to file an H-1B transfer, pack up their family if it does not work out — all while their spouse on an H-4 visa cannot legally work (the H-4 EAD program is under separate siege), their children are mid-semester in American schools, and their apartment lease runs for another nine months.

Immigration attorneys report that some workers are attempting to switch to B-2 tourist visas to buy time, but approval rates for that route have declined sharply. USCIS has not issued any special guidance for the current wave of AI-related layoffs, and there is no indication one is coming.

## The Companies Driving the Cuts

Meta, Amazon, and Oracle have led the 2026 layoff cycle, each citing AI integration and workforce "optimization" as primary drivers. The bitter irony is not lost on the engineers being shown the door: many of them built the very AI systems now replacing their colleagues. The restructuring is not limited to junior roles. Senior engineers, technical leads, and even principal architects with a decade of U.S. tenure are receiving termination notices.

For Indian nationals, the concentration risk is especially acute. Indians dominate the H-1B program not because of some administrative quirk but because American tech companies recruited aggressively from IITs and NITs for two decades. The pipeline that made Hyderabad-to-Cupertino a well-worn path is now the same pipeline funneling people toward the exit.

## A Panel Recommendation Gathering Dust

The President's Advisory Commission on Asian Americans, Native Hawaiians, and Pacific Islanders has formally recommended extending the grace period from 60 days to 180 days. The reasoning is straightforward: in a market where even U.S. citizens take three to six months to land a comparable role, 60 days is a fiction. The recommendation has not been adopted by USCIS, and in the current political climate — where the administration has simultaneously raised H-1B filing fees to $100,000 and restricted adjustment of status — the prospect of any relief measure seems remote.

## What Families Are Actually Doing

On the ground, the response has been pragmatic and communal. Indian-American professional networks, including regional chapters of TiE and IANA, have begun organizing emergency job fairs specifically for displaced H-1B workers. WhatsApp groups with names like "H1B Layoff Support — Bay Area" now have thousands of members sharing leads, lawyer referrals, and tips on which companies still sponsor transfers quickly.

Some families are executing a calculated split: one spouse returns to India with the children to restart schooling, while the other stays to job-hunt on a dwindling grace period. Others are looking north to Canada, where an accelerated PR pathway for H-1B holders has turned what was once a backup plan into a primary strategy.

Indian consular officials in San Francisco, Houston, and New York have increased outreach to affected nationals, though the consulates' capacity to provide direct immigration assistance within the U.S. system is limited.

## The Structural Problem No One Will Fix

The 60-day grace period was codified in 2017 as part of the H-1B modernization rule. Before that, there was no formal grace period at all — workers were technically out of status the moment their employment ended. Sixty days was progress. But it was designed for a labor market where a skilled engineer could line up a new offer within a month. That market no longer exists, and the rule has not kept pace.

Until Washington acts — and there is no sign it will — the 60-day clock will keep running. The only question is how many Indian families it takes with it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "110,000 Tech Jobs Gone. 60 Days to Find Another One or Leave the Country.",
    "subheadline": "AI-driven layoffs are pushing thousands of Indian H-1B workers into a grace-period crisis that Washington designed for a labor market that no longer exists.",
    "slug": make_slug("ai-layoffs-h1b-60-day-grace-period-indian-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals hold 70% of all H-1B visas — 283,772 approved petitions in FY2025. The AI layoff wave is disproportionately hitting Indian tech workers who face a 60-day grace period to find new sponsorship or uproot families with children in American schools, spouses on H-4 visas, and years of green card backlog investment.",
    "tags": ["h1b", "layoffs", "ai", "grace-period", "uscis", "tech-workers", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Layoffs.fyi", "url": "https://layoffs.fyi/"},
        {"name": "USCIS H-1B Approval Data FY2025", "url": "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub"},
        {"name": "AIR News India", "url": "https://www.airnews.in/articles/bed304f0a3-ai-driven-layoffs-in-u-s-tech-sector-trigger-immigration-crisis-for-indian-h-1b-workers"},
        {"name": "Boundless Immigration", "url": "https://www.boundless.com/blog/grace-period-h1b-lay-offs"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/52608/pexels-photo-52608.jpeg",
    "image_caption": "For Indian H-1B workers, a layoff notice starts a 60-day countdown with no margin for error.",
    "body": art1_body
}


# ─────────────────────────────────────────────
# ARTICLE 2: Canada's PR Pathway for H-1B Holders
# ─────────────────────────────────────────────

art2_body = """When Ottawa announced its accelerated permanent residency pathway for U.S. H-1B visa holders, it did not bother with subtlety. The Canadian government earmarked CA$1.7 billion, set a target of 33,000 new permanent residents over 2026 and 2027, and made the pitch explicit: if America does not want your talent, Canada does.

The program builds on a 2023 pilot that offered open work permits to H-1B holders. That pilot had a cap of 10,000 spots. It filled in days. The message from the market was unmistakable: there is enormous latent demand among skilled workers in the U.S. — the overwhelming majority of them Indian — for a credible alternative to the American green card treadmill.

## What the New Pathway Offers

The accelerated PR pathway, outlined in Canada's 2025 Federal Budget and the 2026–2028 Immigration Levels Plan, targets professionals in technology, engineering, healthcare, and research. Unlike the 2023 pilot, which offered temporary work permits, this program leads directly to permanent residency — the Canadian equivalent of a green card, except without the decade-long wait.

Key features that matter to Indian professionals:

**No per-country caps.** This is the single most consequential difference. The U.S. green card system imposes a 7 percent per-country limit, which means Indians with identical qualifications to applicants from, say, Iceland, wait roughly 80 years longer. Canada's Express Entry system evaluates applicants purely on points — age, education, language proficiency, work experience — regardless of nationality.

**Family work rights.** Spouses of PR applicants can obtain open work permits, allowing them to work for any Canadian employer. Compare this to the U.S. H-4 visa, where dependent spouses have spent years in legal limbo over whether they can work at all.

**Processing speed.** Express Entry applications typically move from invitation to PR card in five to eight months. The accelerated pathway is designed to be faster still.

## Why Now

The timing is strategic. Washington has spent the past year making the H-1B program more expensive and more precarious. The $100,000 filing fee introduced in September 2025 was the most visible change, but the cumulative impact goes deeper: the $250 Visa Integrity Fee under the One Big Beautiful Bill, expanded social media vetting that has cut consular interview slots by 40 percent, and the May 21 USCIS memo that effectively reclassified adjustment of status as "extraordinary relief."

For an Indian engineer on an H-1B visa with a priority date in 2013, paying $100,000 to renew a temporary work permit while waiting for a green card that may never come, Canada's offer is not just attractive — it is rational. Reports suggest that 12 percent of current H-1B holders have already obtained Canadian work permits as insurance.

## The Pull Factors Beyond Immigration

Canada is not just selling a visa. It is selling stability. The federal government has committed to investing in credential recognition so that Indian degrees and professional certifications transfer more smoothly. Provincial nominee programs in British Columbia, Ontario, and Alberta are specifically targeting tech workers. And the STEM-focused category-based Express Entry draws that began in 2023 have created a dedicated channel for exactly the kind of professionals the U.S. is shedding.

Toronto and Vancouver have both seen significant growth in Indian tech worker populations over the past two years. Companies like Shopify, OpenText, and RBC have built dedicated onboarding programs for H-1B refugees — a term that has entered the Canadian HR lexicon without irony.

## What Indian H-1B Holders Should Know

The full program criteria have not been published by Immigration, Refugees and Citizenship Canada (IRCC), but the direction is clear. Professionals considering the pathway should:

Consolidate documentation of their H-1B status — Form I-797, I-94, visa copies. Build an Express Entry profile now, even before the accelerated pathway officially opens. Check their Comprehensive Ranking System (CRS) score. Explore provincial nominee programs in tech-heavy provinces as a parallel track.

The 2023 pilot showed that when this window opens, it closes fast.

## The Larger Realignment

What is happening is not merely a policy difference between two countries. It is a structural realignment of where the world's best-educated, most mobile workforce chooses to build its life. The United States spent decades building the most powerful talent pipeline in human history. Canada is now offering the same workers a shorter line, lower fees, and a permanent answer to the question that haunts every H-1B holder: will I ever actually belong here?

For the 283,000 Indians who received H-1B approvals last year, the question is no longer whether to have a Plan B. It is whether Plan B has quietly become Plan A."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Canada Is Spending $1.7 Billion to Poach America's Best Indian Engineers",
    "subheadline": "Ottawa's accelerated PR pathway targets 33,000 H-1B holders over two years — with no per-country caps, family work rights, and processing times measured in months, not decades.",
    "slug": make_slug("canada-accelerated-pr-pathway-h1b-indian-engineers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders face a unique trap: they dominate the program (70% of approvals) but face the longest green card waits (80+ years for EB-2 India). Canada's accelerated PR pathway — no per-country caps, 5-8 month processing, spouse work rights — directly targets this population. The 2023 pilot filled 10,000 spots in days, signaling massive Indian demand.",
    "tags": ["canada", "h1b", "permanent-residency", "express-entry", "green-card-backlog", "immigration", "indian-engineers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Liberty Immigration Canada", "url": "https://libertyimmigration.ca/canada-launches-accelerated-pr-pathway-for-h-1b-visa-holders/"},
        {"name": "CIC News", "url": "https://www.cicnews.com/2023/07/im-an-h-1b-visa-holder-can-i-pursue-a-canadian-open-work-permit-and-express-entry-at-the-same-time-0737641.html"},
        {"name": "VisaHQ", "url": "https://www.visahq.com/news/canada-to-launch-accelerated-pr-pathway-for-u-s-h-1b-visa-holders"},
        {"name": "Amir Ismail Immigration", "url": "https://amirismail.com/canada-h-1b-alternative/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16051603/pexels-photo-16051603.jpeg",
    "image_caption": "Canada's accelerated PR pathway is targeting tens of thousands of skilled workers stuck in the U.S. immigration system.",
    "body": art2_body
}


# ─────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone — {len(articles)} articles submitted at {now}")
