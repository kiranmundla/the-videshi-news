#!/usr/bin/env python3
"""Immigration writer — 2026-06-27 09:00 PT"""
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
# ARTICLE 1 — H-1B Returnees + India Job Market
# ─────────────────────────────────────────────

article1_body = """They called it the fallback plan. Lose your H-1B, go home, regroup, re-enter. For thousands of Indian tech professionals who built careers in Seattle, San Jose, and Austin, India was always supposed to be there — a booming tech economy with their name on it.

It isn't working out that way.

Active technology job openings in India fell to 93,000 in June, a 28-month low, according to specialist staffing firm Xpheno. That is a 14 per cent drop from May and a 17 per cent decline year-on-year. Senior-level openings — the kind returning Silicon Valley engineers would target — cratered by 67 per cent. Entry-level positions, where returning professionals might be willing to start over, fell 44 per cent.

Into this contracting market, 7,300 H-1B tech workers have arrived back in India in the first half of 2026 alone.

## The Mismatch Nobody Prepared For

The math is brutal. In the United States, a mid-career software engineer on H-1B earns between $140,000 and $200,000. In India's current market, comparable roles at IT services firms pay ₹25–40 lakh ($30,000–$48,000). Even at Global Capability Centres — the R&D outposts of American corporations in Bengaluru and Hyderabad — the top of the range rarely exceeds ₹60 lakh.

Employers in India are not just offering lower salaries; they are actively wary of returnees. Hiring managers worry that anyone who spent a decade in the Bay Area will leave again at the first opportunity. "There's a stigma," one Bengaluru-based recruiter told CareerNet. "Companies fear they're a flight risk — that they'll jump back to the US the moment the visa climate shifts."

The result is a double bind: too expensive for most Indian employers, too overqualified for the roles that are available, and too suspect in their intentions for the ones that fit.

## Why the Market Shrank

The job-market decline is not merely cyclical. It is structural. India's tech sector is undergoing the same AI-driven productivity revolution that is hollowing out American tech headcounts. Companies are replacing large delivery teams with leaner, AI-augmented units. Neelabh Shukla, Chief Business Officer at CareerNet, told India Today that "AI adoption in software development is now becoming mainstream and is starting to impact tech hiring globally. India, in particular, is seeing a sharper short-term effect given we are a high-volume tech hiring market."

Meanwhile, India's top IT services firms — TCS, Infosys, Wipro, HCL, Cognizant, and Tech Mahindra — saw their collective H-1B approvals fall 40 per cent to 11,041 in the year ending March 2026. TCS alone lost 3,242 approvals. The companies are not replacing those US-based roles with equivalent Indian ones; they are automating them away.

## The Push Factor from America

The return migration is not voluntary for most. US tech layoffs have claimed over 100,000 jobs, with roughly 25,000 of those estimated to involve H-1B holders. The 60-day grace period — the narrow window to find a new sponsor or leave — is unchanged at 60 days despite years of advocacy for an extension to 180 days.

Stricter visa regulations, the proposed $100,000 H-1B filing fee (currently in litigation), tighter processing norms, and a wage-weighted selection system have all made it harder to stay. For Indians specifically, the EB-2 green card category went "unavailable" in the July 2026 Visa Bulletin, slamming shut the most common path to permanent residency.

Staffing experts now predict that the number of Indian tech professionals returning from the US will outpace those leaving for the first time before the end of 2026.

## A Narrow Opening

Not all doors are closed. Global Capability Centres continue to absorb some returning talent — particularly professionals with over a decade of experience in niche domains like AI infrastructure, cloud architecture, or data engineering. Nvidia, which is expanding aggressively in India, has been hiring returning engineers. And a handful of Indian startups flush with late-stage funding are willing to pay for US-calibre experience.

But these are exceptions, not a trend. For the majority of returnees, India's tech economy is offering a lesson their American careers never taught them: the safety net has a salary cap, and it may not catch everyone."""

article1_sources = json.dumps([
    {"name": "Xpheno Active Jobs Outlook (via CareerNet)", "url": "https://careernet.in/news/indian-tech-jobs-hit-28-month-low-h1b-techies-returning-back-make-job-market-tougher/"},
    {"name": "ainvest.com", "url": "https://www.ainvest.com/news/tech-talent-faces-challenges-finding-jobs-india-1b-return-2606/"},
    {"name": "Mint", "url": "https://www.livemint.com/companies/it-u-h-1b-visas-green-card-immigration-tcs-infosys-cognizant-green-cards-hiring-11779598845829.html"},
    {"name": "LinkedIn / Xpheno Analysis", "url": "https://www.linkedin.com/pulse/indias-tech-hiring-hits-28-month-low-more-than-slowdown-hansraj-surti-tdclf"}
])

# ─────────────────────────────────────────────
# ARTICLE 2 — Birthright Citizenship + H-1B
# ─────────────────────────────────────────────

article2_body = """Somewhere between the H-1B filing deadline and the green card backlog, a quieter crisis has been unfolding at 1 First Street NE, Washington. The Supreme Court is expected to rule as early as Monday on whether children born in America to parents on temporary work visas — including H-1B holders — are automatically United States citizens.

The answer has been yes for 128 years. It may be about to get complicated.

## What the Executive Order Does

President Trump signed Executive Order 14160 on his first day back in office in January 2025. It directed federal agencies to stop recognising US citizenship for children born in America if neither parent is a citizen or lawful permanent resident. The order explicitly targets parents on temporary status — H-1B workers, F-1 students, L-1 transferees, tourists, and anyone without a green card.

Under the order, an Indian software engineer on H-1B in Sunnyvale whose child is born at a local hospital would not be able to obtain a US passport or Social Security number for that child. The child would instead need to be placed on a dependent visa — H-4 status — and would be subject to removal if the parent's visa expired.

Bloomberg Law reported that the order could leave such children effectively stateless, since Indian citizenship law does not automatically extend to children born abroad to Indian citizens unless specific conditions are met.

## The Legal Landscape

Three federal district courts — in Washington, Maryland, and Massachusetts — immediately blocked the order with nationwide injunctions, calling it inconsistent with the Fourteenth Amendment's Citizenship Clause: "All persons born or naturalized in the United States, and subject to the jurisdiction thereof, are citizens of the United States."

The Supreme Court's 1898 decision in *United States v. Wong Kim Ark* interpreted that clause broadly, holding that a child born in the US to Chinese nationals with permanent domicile was a citizen. Legal scholars have long considered this settled law.

The Trump administration argues otherwise. Acting Solicitor General Harris contended that the phrase "subject to the jurisdiction thereof" excludes persons whose presence is temporary or unauthorised — a reading that, if accepted, would overturn more than a century of constitutional interpretation.

In an earlier phase of the litigation, the Supreme Court ruled 6-3 to limit the scope of the lower courts' nationwide injunctions, holding that individual plaintiffs must pursue class action procedures for broader relief. That procedural ruling, however, did not address the core constitutional question. That decision is still pending.

## The Scale of the Stakes

According to the Migration Policy Institute, roughly 2.5 million people were in the United States on temporary visas as of 2022. Indians account for the largest share of H-1B holders, and Indian families on work visas have among the highest birth rates of any immigrant group in the tech corridors of California, Texas, and the Northeast.

The executive order would not retroactively strip citizenship from children already born. But it would create a two-tier system going forward: children born to green card holders and citizens would be American; children born to visa holders in the same hospital, on the same day, would not.

Immigration attorneys say the anxiety is already real. "People are panicked," David Leopold, chair of the immigration practice at UB Greensfelder, told Bloomberg Law. "Employees are going to be desperate for information."

## What Monday Could Bring

The Supreme Court said it will issue additional rulings on Monday, June 29, without specifying which cases. The birthright citizenship challenge is among the last major decisions of the term.

Legal analysts widely expect the Court to strike down the executive order, based on the tenor of oral arguments in April and the weight of constitutional precedent. But the current Court has shown a willingness to revisit settled doctrine, and the 6-3 procedural ruling on injunctions signalled that the conservative majority is sympathetic to at least some of the administration's framing.

For the roughly 300,000 Indian families on H-1B, H-4, and L-1 visas with children born or expected in the United States, Monday is not an abstract constitutional exercise. It is a question with a name on the birth certificate."""

article2_sources = json.dumps([
    {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/25/supreme-court-birthright-citizenship-ruling-when/90692295007/"},
    {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-tax-report-state/h-1b-workers-kids-would-lose-citizenship-under-birthright-order"},
    {"name": "National Constitution Center", "url": "https://constitutioncenter.org/amp/blog/birthright-citizenship-cases-arrive-at-the-supreme-court"},
    {"name": "Mondaq / Ogletree", "url": "https://www.mondaq.com/unitedstates/work-visas/1649404/supreme-court-limits-nationwide-injunctions-but-does-not-decide-on-birthright-citizenship-challenge"}
])

# ─────────────────────────────────────────────
# BUILD ARTICLE LIST
# ─────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "They Left America. India Isn't Hiring Them Back",
        "subheadline": "India's tech job openings have cratered to a 28-month low just as 7,300 H-1B workers returned in six months. The fallback plan has a salary cap — and it may not catch everyone.",
        "slug": make_slug("h1b-returnees-india-tech-job-market-28-month-low-salary-mismatch"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals on H-1B who lose their jobs face a shrinking safety net at home — India's tech market is contracting and employers view returnees as overpriced flight risks.",
        "tags": ["h1b", "india", "tech-jobs", "return-migration", "layoffs"],
        "urgency": "medium",
        "sources": article1_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37088158/pexels-photo-37088158.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Bengaluru skyline at twilight — India's tech capital where returning H-1B workers are finding fewer opportunities",
        "image_attribution": "Pexels",
        "body": article1_body.strip(),
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Supreme Court Could Decide Monday Whether Your American-Born Child Is American",
        "subheadline": "Trump's birthright citizenship order would deny automatic US citizenship to children of H-1B holders. The ruling could come as early as June 29 — and 300,000 Indian families are watching.",
        "slug": make_slug("birthright-citizenship-supreme-court-h1b-families-monday-ruling"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian families on H-1B and L-1 visas with US-born children face the possibility that future births won't confer citizenship — a seismic shift for the diaspora's family-planning calculus.",
        "tags": ["birthright-citizenship", "supreme-court", "h1b", "fourteenth-amendment", "children"],
        "urgency": "high",
        "sources": article2_sources,
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
        "image_caption": "The United States Supreme Court building in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body.strip(),
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — \"{art['headline']}\"")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
