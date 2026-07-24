#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-02 04:00 UTC run"""

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
# ARTICLE 1: Meta / Big Tech H-1B "Indentured Servanthood" Debate
# ─────────────────────────────────────────────

art1_body = """The accusation landed like a lobbying grenade on Capitol Hill this week: Meta, the company that built its empire on connecting people, is running an "indentured servanthood" program for its foreign workers. Steve Milloy, executive director of the Free Enterprise Project at the National Center for Public Policy Research, levelled the charge in a broadcast interview, arguing that the H-1B visa system has devolved from a mechanism for recruiting the "best and brightest" into a pipeline for cheap, captive labor.

The claim isn't new. But the messenger is. Milloy's outfit is a conservative shareholder activist group — the kind that typically champions deregulation and corporate freedom. When the political right starts borrowing the language of labor exploitation to attack Big Tech's visa practices, something in the immigration debate has shifted.

## The Numbers Behind the Noise

Meta sponsored approximately 3,200 H-1B workers in fiscal year 2025, according to USCIS data. Amazon led the pack with over 8,000, followed by Google, Microsoft, and Apple. Together, the top five U.S. technology companies accounted for roughly 25,000 H-1B petitions — and Indian nationals held the overwhelming majority of those visas, typically around 72-74 percent of all H-1B approvals.

The "indentured" label has a specific structural basis. An H-1B worker is tied to their sponsoring employer. Changing jobs requires a new petition, a new approval, and — under current processing timelines — months of uncertainty. If the worker has a pending green card application through their employer's PERM labor certification, switching jobs can mean restarting a process that already takes 503 days just for the initial labor certification approval. For an Indian national in the EB-2 queue, the total wait for a green card stretches beyond a decade.

This creates what immigration attorneys call "golden handcuffs." The worker is highly skilled, highly paid by global standards, but functionally immobile within the U.S. labor market. Leave your employer and you risk your immigration status. Stay, and you accept whatever compensation and conditions are offered.

## The Uncomfortable Alliance

What makes the current moment distinctive is the convergence of two historically opposed camps. From the left, labor unions and worker advocacy groups have long argued that the H-1B program suppresses domestic wages by importing cheaper foreign labor. The Economic Policy Institute has documented that over 60 percent of H-1B positions are certified at wages below the local median for the occupation.

From the right, the Trump administration's $100,000 H-1B fee — currently being challenged in federal court after a Boston judge questioned its legal authority — reflects a belief that the visa should be reserved for genuinely elite talent, not mid-level engineers. The new wage-weighted lottery system, effective for FY 2027 registrations, will multiply entries for higher-paid workers while reducing chances for entry-level positions.

Indian H-1B workers are caught between these two critiques: simultaneously accused of being too cheap (by labor advocates) and not expensive enough (by the administration).

## What This Means for Indian Professionals

For the estimated 500,000 Indian nationals currently on H-1B visas or in the green card queue, the "indentured servanthood" framing carries a bitter irony. Most chose to build careers in America precisely because they were recruited for specialized skills. Many hold advanced degrees from U.S. universities. A significant number earn well above six figures.

Yet the structural dependency is real. The 60-day grace period after a layoff — a reality that 110,000 tech workers faced in 2026 alone — means that losing a job isn't just a career setback. It's an immigration emergency that can upend a decade of investment in American life.

The growing political consensus that something is wrong with the H-1B system may eventually produce reform. But the proposed fixes — higher fees, wage floors, lottery weighting — all treat the symptom (employer dependency) without addressing the cause (a green card backlog that keeps workers in temporary status for a generation). Until that changes, the "indentured" label will keep finding traction, from both sides of the aisle."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Big Tech's 'Indentured Servanthood' Problem Has a New Voice — and It's Coming From the Right",
    "subheadline": "A conservative shareholder activist group accuses Meta of exploiting H-1B workers. For half a million Indians in the visa queue, the bipartisan critique is getting harder to ignore.",
    "slug": make_slug("big-tech-indentured-servanthood-h1b-meta-conservative"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers comprise 72-74% of all H-1B approvals and are the primary workforce affected by the 'indentured servanthood' dynamic — structurally tied to employers through visa dependency, golden handcuffs on green card applications, and the 60-day layoff clock that turns job loss into an immigration crisis.",
    "tags": ["h1b", "meta", "big-tech", "immigration-reform", "indian-workers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Audacy News", "url": "https://www.audacy.com/podcasts/6a31745ac53f4b5c45558e68c01ea651/episodes/metas_heavy_reliance_on_the_h1-8423429"},
        {"name": "Economic Policy Institute", "url": "https://www.epi.org/publication/h-1b-visas-and-prevailing-wage-levels/"},
        {"name": "USCIS H-1B Data Hub", "url": "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub"},
        {"name": "BizzBuzz News", "url": "https://www.bizzbuzz.news/economy/indian-tech-jobs-in-us-at-risk-h1b-approvals-fall-sharply-1373289"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2449455/pexels-photo-2449455.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art1_body,
    "is_editorial": False,
}


# ─────────────────────────────────────────────
# ARTICLE 2: EB-5 September 30 Grandfathering Deadline
# ─────────────────────────────────────────────

art2_body = """The clock on the wall reads September 30, 2026. That is the date after which EB-5 investors lose the strongest statutory protections available under current law — and for Indian nationals trapped in a green card backlog measured in decades, the deadline is beginning to concentrate minds.

Under the EB-5 Reform and Integrity Act of 2022, investors who file their I-526E petition on or before September 30 receive grandfathering protection: their petition will continue to be processed even if Congress fails to reauthorize the regional center program. They lock in the current $800,000 minimum investment for targeted employment areas. And they gain continued eligibility for concurrent filing, meaning they can apply for adjustment of status while their petition is pending.

After that date, the protections thin. The regional center program remains active through at least September 2027, and the investment amount is expected to stay at $800,000. But the statutory safety net — the guarantee that your petition survives a potential program lapse — disappears.

## Why Indians Are Paying Attention

The numbers make the case on their own. According to the National Visa Center's latest backlog data, there are 426,465 approved EB-2 petitions for Indian nationals waiting for a green card. Another 133,409 are in the EB-3 queue. Including dependents — spouses and children — the total reaches 862,363 individuals. The projected wait time for EB-2 India extends beyond 128 years at current allocation rates.

The EB-5 program offers a dramatically different timeline. For investors who file through a rural targeted employment area — one of the three set-aside categories created by the 2022 reform — current processing times run approximately 18 to 24 months. That is not a typo. An Indian professional who has been waiting since 2013 for an EB-2 green card could, through EB-5, hold a conditional green card before the end of 2028.

The math has not been lost on the community. Indian EB-5 applications surged over 300 percent between 2022 and 2025, according to regional center operators. Many applicants are current H-1B holders or their spouses — professionals already embedded in the American economy who are essentially paying $800,000 to escape a bureaucratic queue.

## The Trade-Offs Are Real

An EB-5 investment is not a guaranteed return. The $800,000 goes into a commercial enterprise — typically a real estate development, infrastructure project, or business venture administered by a USCIS-designated regional center. The investment must create at least 10 full-time jobs for U.S. workers. Capital is typically locked up for four to six years before the regional center returns it, and there is no guarantee of a return at all.

The 2022 reform act introduced significant investor protections: mandatory third-party fund administration, regular audits of regional centers, and strict compliance sanctions. But due diligence remains the investor's responsibility. Fraudulent regional centers have been prosecuted in the past, and USCIS has shut down non-compliant operators.

For a family already stretched by years of H-1B dependency — paying U.S. taxes, building careers, raising children who know no other country — the decision to write an $800,000 check is not purely financial. It is an emotional calculation about how much longer they are willing to wait for a system that was never designed to process 862,363 people through a per-country cap that allocates roughly 2,800 EB-2 visas per year to India.

## The Fiscal Year Pressure

The September 30 deadline falls at the end of the federal fiscal year, which also marks the expiration of current EB-5 set-aside allocations. Rural TEA set-asides — the category with the shortest processing times — have seen increasing competition, though they have not yet retrogressed for Indian nationals the way the main EB-5 category has for China.

Immigration attorneys are advising clients to file well before the deadline rather than waiting until September. USCIS processing of I-526E petitions involves document review, source-of-funds verification, and background checks. An incomplete filing submitted on September 29 offers no protection.

For the 862,363 Indians in the employment-based green card pipeline, the EB-5 was never supposed to be the answer. It was designed as an economic development tool, not an escape valve for a broken preference system. But when the system offers a 128-year wait on one hand and an $800,000 shortcut on the other, the market does what markets do. It prices in the dysfunction."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Four Months to File — The EB-5 Deadline That Could Save Indians a 128-Year Wait",
    "subheadline": "September 30 is the last day to lock in grandfathering protections under the EB-5 regional center program. For 862,363 Indians in the green card queue, the $800,000 question is getting urgent.",
    "slug": make_slug("eb5-september-deadline-indian-green-card-escape"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With 862,363 Indians (including dependents) trapped in the employment-based green card backlog — EB-2 projected at 128+ years — the EB-5 program offers an 18-24 month alternative at $800,000. Indian EB-5 applications have surged 300% since 2022. The September 30 grandfathering deadline is the strongest filing incentive yet.",
    "tags": ["eb5", "green-card", "indian-immigration", "investor-visa", "backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Golden Gate Global (EB-5 Update 2026-2027)", "url": "https://3gfund.com/eb-5-visa-update-2026-2027/"},
        {"name": "Shusterman Visa Bulletin Predictions", "url": "https://www.shusterman.com/visa-bulletin-predictions/"},
        {"name": "Fragomen LLP", "url": "https://www.fragomen.com/insights/despite-eb-5-retrogression-for-indian-nationals-eb-5-regional-center-program-provides-a-promising-pathway.html"},
        {"name": "BizzBuzz News", "url": "https://www.bizzbuzz.news/economy/as-visa-policies-tighten-eb-5-emerges-as-a-reliable-path-to-us-residency-1364505"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body,
    "is_editorial": False,
}


# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
