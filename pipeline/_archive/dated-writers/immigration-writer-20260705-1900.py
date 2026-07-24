#!/usr/bin/env python3
"""Immigration writer — 2026-07-05 19:00 PT run. Two articles."""

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

# ── Article 1 ─────────────────────────────────────────────────────────
art1_body = """The Trump administration has spent the past eighteen months making the H-1B programme harder to enter. A weighted lottery that favours higher salaries. A proposed $100,000 registration fee now caught in a three-way circuit split. Tighter scrutiny of specialty-occupation claims. And yet the number that matters most to the roughly half a million Indians already inside the system is heading in the opposite direction.

Continuing-employment H-1B petitions — the extensions, renewals, and employer transfers that keep existing visa holders working — are on track to hit 291,542 approvals in fiscal year 2026, according to U.S. Citizenship and Immigration Services data compiled by analysts. That would be a record, and it reveals a paradox at the heart of the administration's immigration strategy: the harder it becomes to bring in new workers, the more desperately employers fight to keep the ones they have.

## The uncapped pipeline

The annual H-1B cap — 65,000 regular slots plus 20,000 for U.S. advanced-degree holders — generates the headlines every spring. But the renewal pipeline operates on different maths entirely. There is no numerical limit on extensions, transfers, or amendments for workers already in H-1B status. An employer can extend a worker's stay in three-year increments, switch them to a new position, or move them to a different company without ever touching the lottery.

This distinction has always existed, but it has never mattered more. With the weighted lottery selecting for higher-paid workers, the pool of newly approved H-1B holders is shifting. Companies that once relied on the lottery to bring in entry-level engineers or analysts are finding that pathway narrower. Their rational response: hold onto every existing H-1B worker they can, filing extension after extension rather than risk losing someone they cannot replace.

## What the record means for Indians

Indians hold an estimated 72 to 75 per cent of all H-1B visas, concentrated in technology, consulting, and engineering. For them, the record renewal number is simultaneously reassuring and alarming.

Reassuring, because it confirms that employers are investing legal fees and compliance effort to keep their Indian workers employed. The typical H-1B extension petition costs an employer $2,000 to $5,000 in legal and filing fees. At 291,542 approvals, that represents hundreds of millions of dollars in aggregate employer commitment — a tangible vote of confidence in a workforce that political rhetoric often frames as disposable.

Alarming, because the renewals are a holding pattern, not a resolution. Each extension keeps an H-1B worker employed for another three years, but it does nothing to advance their green card application. An Indian national in the EB-2 queue today faces a projected wait of 37 years, according to the Congressional Research Service. With EB-2 India declared unavailable for the remainder of fiscal year 2026, many of these renewed workers are extending their temporary status with no realistic path to permanence.

## The employer calculus

The record also reflects a structural shift in how U.S. employers view immigration risk. A decade ago, losing an H-1B worker to a visa denial was an inconvenience. Today, with the domestic STEM talent pipeline unable to keep pace with demand — particularly in artificial intelligence, cybersecurity, and semiconductor design — it is a competitive threat.

The numbers bear this out. A survey cited by Travel and Tour World found that nearly 65 per cent of U.S. companies reported losing foreign skilled workers due to H-1B uncertainty, green card backlogs, and processing delays. When replacing a departed H-1B worker means waiting a year for the next lottery, then competing in a wage-weighted selection, the economics of renewal become obvious.

## The quiet tightrope

Experts caution that the 291,542 figure refers to approved petitions, not unique individuals. A single worker can generate multiple petitions in a fiscal year — an extension, followed by an employer transfer, followed by an amendment. The actual number of individuals retained is lower, though USCIS does not publish that breakout.

What the data does show is that the H-1B programme, for all the political noise around it, is not shrinking. It is bifurcating. The front door — the lottery, the initial selection — is getting smaller and more expensive. The back corridor — extensions, transfers, the uncapped renewal machinery — is expanding to compensate. For the Indian professionals walking that corridor, the question is not whether they can keep working. It is whether working is enough when permanence remains decades away."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nearly 300,000 H-1B Renewals and Counting. The Number Trump's Crackdown Cannot Touch",
    "subheadline": "Continuing-employment approvals are on track to hit a record 291,542 in fiscal year 2026, revealing that employers are spending hundreds of millions to retain workers they can no longer easily replace.",
    "slug": make_slug("h1b-renewals-record-291542-continuing-employment-crackdown"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 72-75% of all H-1B visas. The record renewal number means employers are fighting to keep them — but each extension is a holding pattern, not a path to permanence, with EB-2 India declared unavailable and green card waits stretching to 37 years.",
    "tags": ["h1b", "uscis", "immigration", "visa-renewal", "green-card-backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "AInvest / USCIS Data", "url": "https://www.ainvest.com/news/1b-visa-renewals-hit-record-high-trump-stricter-rules-2607/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/labor-department-eyes-immigration-changes-in-broad-rule-plan"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/uk-aligns-with-canada-germany-australia-as-us-visa-crisis-fuels-global-talent-exodus/"},
        {"name": "USCIS H-1B Cap Announcement", "url": "https://www.uscis.gov/newsroom/alerts/uscis-reaches-fiscal-year-2026-h-1b-cap"},
        {"name": "Congressional Research Service (Green Card Backlog)", "url": "https://www.latestly.com/agency-news/employment-based-backlog-to-double-by-2030-indians-have-to-wait-for-decades-for-green-card-crs-6647283.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── Article 2 ─────────────────────────────────────────────────────────
art2_body = """For twenty-two years, the rules governing how an American employer proves it could not find a domestic worker before sponsoring a foreigner for a green card have remained essentially unchanged. The permanent labour certification process — known as PERM — was last overhauled in 2004, when LinkedIn was a year old, remote work was a novelty, and the iPhone did not exist. Now the Department of Labour wants to rewrite it.

The DOL's regulatory agenda, published on July 3 as part of the Trump administration's broader rulemaking blueprint, includes a proposal to modernise how the agency reviews PERM applications. The focus: updated standards for recruiting qualified American workers and new safeguards for U.S. workers affected by layoffs. The details remain sparse — this is a regulatory intent signal, not a draft rule — but the direction is unmistakable. The green card sponsorship process is about to get harder.

## Two fronts, one target

The PERM overhaul is not arriving in isolation. It lands alongside a separate proposed rule, published in March, that would significantly raise the prevailing wages employers must offer when sponsoring H-1B workers and green card applicants.

Under the current system, prevailing wage Level I — the entry-level tier — sits at roughly the 17th percentile of wages for a given occupation and geography. The proposed rule would move that floor to the 34th percentile. Level IV, the fully competent tier, would jump to the 88th percentile. The DOL estimates the average certified wage would rise by approximately $14,000 per year per worker.

The two actions target different parts of the same pipeline. PERM governs whether an employer can sponsor a green card at all. The prevailing wage rule governs how much it costs. Together, they would raise both the procedural and financial barriers to employment-based immigration.

## Why 2004 matters

The original PERM regulations were built for a world where job postings ran in Sunday newspapers, résumés arrived by post, and recruiting meant a phone call to a staffing agency. The DOL's own regulatory language acknowledges that "technology changes have altered key industry practices like recruiting" since then.

In practice, the 2004-era rules have created a compliance theatre that immigration attorneys know well. Employers must advertise positions in specific outlets, at specific times, using specific language — not because these methods are the most effective way to find American workers, but because the regulations mandate them. A software company in San Jose might post an ad in the *San Jose Mercury News* for a machine-learning engineer, knowing full well that no qualified domestic candidate reads print classifieds for tech jobs. But the law requires it, so they comply, file the paperwork, and wait.

The DOL's modernisation proposal signals an intent to replace this ritual with something more grounded in how hiring actually works. What that means in practice — whether it involves digital recruiting standards, job-board requirements, or algorithmic matching — remains to be seen. The comment period has not yet opened.

## The Indian squeeze

For Indian professionals, the timing is brutal. Consider the green card pipeline as a sequence of gates:

**Gate 1: PERM labour certification.** The employer proves no qualified American worker is available. Current processing time: 11 to 18 months. The proposed overhaul could extend this further if new recruiting requirements add steps.

**Gate 2: I-140 immigrant petition.** USCIS approves the employer's petition. Processing time: 6 to 12 months, or weeks with premium processing.

**Gate 3: Wait for a visa number.** This is where Indians hit the wall. The EB-2 category is unavailable for the rest of fiscal year 2026. The EB-3 final action date is stuck at January 2014. The Congressional Research Service projects the EB-2 backlog will take 37 years to clear under current law.

The PERM overhaul targets Gate 1. The prevailing wage increase raises the cost at every gate. And Gate 3 remains locked, regardless of what happens at the other two.

The practical effect: an Indian engineer whose employer begins the green card process today will navigate a modernised, costlier PERM regime to earn a spot in a queue that stretches to the 2060s. Smaller employers and non-profits — which are disproportionately likely to sponsor Indian workers in healthcare, research, and education — may find the new wage floors prohibitive and abandon sponsorship altogether.

## The private survey question

One detail in the prevailing wage proposal offers a sliver of relief. The DOL considered eliminating employers' ability to use private wage surveys as an alternative to the government's Occupational Employment and Wage Statistics data. It chose not to — for now. Private surveys often show lower prevailing wages for niche roles, and their preservation gives employers some flexibility to argue for more competitive benchmarks.

But the DOL also signalled that it intends to "monitor the use of private surveys to prevent abuse" and reserves the right to reject surveys that do not meet its standards. The message: this exemption is a reprieve, not a guarantee.

## What comes next

The PERM modernisation exists as a line item in a regulatory agenda — a statement of intent, not a draft rule. A proposed rule could appear within months or stall for years. The prevailing wage rule, by contrast, completed its comment period on May 26 and could be finalised by late 2026 or early 2027.

For the Indian professional community, the strategic calculation has not changed, but the stakes have risen. The green card path was already defined by decades of waiting. Now the entrance to that path is being redesigned — with higher tolls and new gatekeepers — even as the destination remains impossibly far away."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Labour Department Is Rewriting the Green Card Playbook. For the First Time in 22 Years",
    "subheadline": "A PERM overhaul — the first since 2004 — plus a proposed $14,000-per-worker wage hike would raise both the procedural and financial barriers to employer-sponsored green cards, hitting Indian applicants hardest.",
    "slug": make_slug("dol-perm-overhaul-prevailing-wage-hike-green-card-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals face a 37-year EB-2 green card wait. Now the very first step of that journey — the PERM labour certification — is being overhauled and made costlier, while smaller employers may abandon sponsorship entirely.",
    "tags": ["green-card", "perm", "dol", "prevailing-wage", "immigration", "eb2", "eb3"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/labor-department-eyes-immigration-changes-in-broad-rule-plan"},
        {"name": "Lexology", "url": "https://www.lexology.com/library/detail.aspx?g=dol-proposes-significant-increases-to-prevailing-wage-levels"},
        {"name": "Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1608122/dol-proposes-significant-increases-to-prevailing-wage-levels-for-h-1b-and-perm-programs-what-employers-need-to-know"},
        {"name": "South Asian Herald", "url": "https://southasianherald.com/us-visa-wall-gets-higher/"},
        {"name": "Congressional Research Service (via LatestLY)", "url": "https://www.latestly.com/agency-news/employment-based-backlog-to-double-by-2030-indians-have-to-wait-for-decades-for-green-card-crs-6647283.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_2.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_2.jpg",
    "image_caption": "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
